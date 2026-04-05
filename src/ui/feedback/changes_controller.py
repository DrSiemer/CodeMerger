import os
import subprocess
import sys
import tkinter as tk
from tkinter import Frame, Label, Button, messagebox
from ... import constants as c
from ...core import change_applier
from ..widgets.rounded_button import RoundedButton
from ..widgets.markdown_renderer import MarkdownRenderer
from ..widgets.scrollable_frame import ScrollableFrame
from ..widgets.diff_viewer import DiffViewer
from ..tooltip import ToolTip

class FeedbackChangesController:
    """
    Manages the interactive file list in the 'Changes' tab.
    Handles row building, diff viewing, and state tracking for individual files.
    """
    def __init__(self, window):
        self.window = window
        self._diff_viewers = {}
        self._initialize_file_states()

    def register_info(self, info_mgr):
        """Binds info documentation to the changes list controls."""
        if hasattr(self.window, 'toggle_commentary_btn'):
            info_mgr.register(self.window.toggle_commentary_btn, "review_commentary")

    def _initialize_file_states(self):
        """Determines initial state (pending/skipped) for all files in the plan."""
        window = self.window
        if window.file_states: return # Already initialized for this plan

        updates = window.plan.get('updates', {})
        for path, content in updates.items():
            old_text = change_applier.get_current_file_content(window.base_dir, path)
            if old_text is not None:
                sanitized_new = change_applier._sanitize_content(os.path.join(window.base_dir, path), content)
                if old_text == sanitized_new:
                    window.file_states[path] = "skipped"
                    continue
            window.file_states[path] = "pending"

        for path in window.plan.get('creations', {}):
            window.file_states[path] = "pending"

        for path in window.plan.get('deletions_proposed', []):
            if not os.path.isfile(os.path.join(window.base_dir, path)):
                window.file_states[path] = "skipped"
                continue
            window.file_states[path] = "pending"

    def add_interactive_changes_tab(self):
        """Constructs the Change management tab."""
        window = self.window
        frame = Frame(window.notebook, bg=c.DARK_BG)
        window.notebook.add(frame, text="Changes", image=window._blue_accent, compound="left")

        header = Frame(frame, bg=c.DARK_BG, padx=20, pady=10)
        header.pack(fill='x')
        Label(header, text="Proposed Actions", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')

        desc = window.plan.get('changes', "").strip()
        if desc:
            window.toggle_commentary_btn = RoundedButton(header, text="Show AI Commentary", command=self.toggle_commentary, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
            window.toggle_commentary_btn.pack(side='right')
            window.commentary_renderer = MarkdownRenderer(frame, base_font_size=10, auto_height=True)
            window.commentary_renderer.set_markdown(desc)

        window.file_list_scroll = ScrollableFrame(frame, bg=c.DARK_BG)
        window.file_list_scroll.pack(fill='both', expand=True, pady=(0, 10))
        self.refresh_file_list_ui()

    def toggle_commentary(self):
        window = self.window
        if not hasattr(window, 'commentary_renderer'): return
        if window.commentary_renderer.winfo_ismapped():
            window.commentary_renderer.pack_forget()
            window.toggle_commentary_btn.config(text="Show AI Commentary", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        else:
            window.commentary_renderer.pack(fill='x', before=window.file_list_scroll, padx=20, pady=(0, 10))
            window.toggle_commentary_btn.config(text="Hide AI Commentary", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)

    def refresh_file_list_ui(self):
        """Wipes and rebuilds the interactive file rows."""
        window = self.window
        container = window.file_list_scroll.scrollable_frame
        for w in container.winfo_children(): w.destroy()
        self._diff_viewers.clear()

        updates = window.plan.get('updates', {})
        creations = window.plan.get('creations', {})
        deletions = window.plan.get('deletions_proposed', [])

        if updates:
            self._create_group_header(container, "Modify Content", c.BTN_BLUE)
            for p in sorted(updates.keys()): self._create_file_row(container, p, "modify")
        if creations:
            self._create_group_header(container, "Create New File", c.BTN_GREEN)
            for p in sorted(creations.keys()): self._create_file_row(container, p, "create")
        if deletions:
            self._create_group_header(container, "Delete Obsolete File", c.WARN)
            for p in sorted(deletions): self._create_file_row(container, p, "delete")

        self.update_mass_apply_visibility()

    def _create_group_header(self, container, text, color):
        f = Frame(container, bg=c.DARK_BG, padx=20)
        f.pack(fill='x', pady=(15, 5))
        Label(f, text=text.upper(), font=(c.FONT_FAMILY_PRIMARY, 9, 'bold'), bg=c.DARK_BG, fg=color).pack(side='left')
        Frame(f, bg=color, height=1).pack(side='left', fill='x', expand=True, padx=(10, 0))

    def _create_file_row(self, parent, path, action_type):
        """Renders an individual file row with action buttons."""
        window = self.window
        row_container = Frame(parent, bg=c.DARK_BG)
        row_container.pack(fill='x', pady=2, padx=(20, 20))

        row_header = Frame(row_container, bg=c.DARK_BG)
        row_header.pack(fill='x')

        state = window.file_states.get(path, "pending")
        is_handled = state in ["applied", "deleted", "rejected"]
        is_skipped = state == "skipped"

        font_config = c.FONT_NORMAL
        if is_handled:
            font = (font_config[0], font_config[1], 'overstrike')
            fg = c.TEXT_SUBTLE_COLOR
        elif is_skipped:
            font = font_config
            fg = c.TEXT_SUBTLE_COLOR
        else:
            font = font_config
            fg = c.TEXT_COLOR

        lbl_name = Label(row_header, text=path, font=font, fg=fg, bg=c.DARK_BG, anchor='w', cursor='hand2')
        lbl_name.pack(side='left', fill='x', expand=True)

        lbl_name.bind("<Button-1>", lambda e, p=path: self.open_file_in_editor(p))
        lbl_name.bind("<Enter>", lambda e, l=lbl_name, f=font_config: self._on_link_hover(l, f, True))
        lbl_name.bind("<Leave>", lambda e, l=lbl_name, f=font: self._on_link_hover(l, f, False))

        btn_frame = Frame(row_header, bg=c.DARK_BG)
        btn_frame.pack(side='right')

        diff_container = Frame(row_container, bg=c.DARK_BG)

        btn_opts = {'font': c.FONT_SMALL_BUTTON, 'relief': 'flat', 'borderwidth': 0, 'height': 1, 'cursor': 'hand2', 'padx': 10}

        if is_skipped:
            msg = "Already deleted" if action_type == "delete" else "No changes"
            Label(btn_frame, text=msg, font=c.FONT_SMALL_BUTTON, fg=c.TEXT_SUBTLE_COLOR, bg=c.DARK_BG, padx=10).pack()
        elif is_handled:
            is_new_creation = path in window.plan.get('creations', {})
            show_undo = False
            if state == "rejected": show_undo = True
            elif is_new_creation: show_undo = True
            elif path in window.undo_buffer and window.undo_buffer[path] is not None: show_undo = True

            if show_undo:
                u_btn = Button(btn_frame, text="Undo", command=lambda: self.undo_file_action(path, action_type), bg="#666666", fg="#FFFFFF", **btn_opts)
                u_btn.pack()
                if window.info_mgr: window.info_mgr.register(u_btn, "review_file_action")
        else:
            btn_text = "View" if action_type in ["create", "delete"] else "Diff"
            d_btn = Button(btn_frame, text=btn_text, command=lambda: self.toggle_diff(path, diff_container, action_type), bg=c.BTN_BLUE, fg="#FFFFFF", **btn_opts)
            d_btn.pack(side='left', padx=(0, 2))

            tooltip_msg = "View file content" if action_type in ["create", "delete"] else "Inspect text changes"
            ToolTip(d_btn, tooltip_msg)
            if window.info_mgr: window.info_mgr.register(d_btn, "review_diff")

            if action_type == "delete":
                a_btn = Button(btn_frame, text="Accept Delete", command=lambda: self.apply_file_action(path, "delete"), bg=c.WARN, fg="#FFFFFF", **btn_opts)
                a_btn.pack(side='left', padx=(0, 2))
                k_btn = Button(btn_frame, text="Keep", command=lambda: self.discard_file_item(path), bg=c.STATUS_BG, fg=c.TEXT_COLOR, **btn_opts)
                k_btn.pack(side='left')
                if window.info_mgr:
                    window.info_mgr.register(a_btn, "review_file_action")
                    window.info_mgr.register(k_btn, "review_file_action")
            else:
                a_btn = Button(btn_frame, text="Accept", command=lambda: self.apply_file_action(path, action_type), bg=c.BTN_GREEN, fg="#FFFFFF", **btn_opts)
                a_btn.pack(side='left', padx=(0, 2))
                r_btn = Button(btn_frame, text="Discard", command=lambda: self.discard_file_item(path), bg=c.STATUS_BG, fg=c.TEXT_COLOR, **btn_opts)
                r_btn.pack(side='left')
                if window.info_mgr:
                    window.info_mgr.register(a_btn, "review_file_action")
                    window.info_mgr.register(r_btn, "review_file_action")

    def _on_link_hover(self, label, base_font, is_enter):
        if is_enter:
            st = base_font[2] + ' underline' if len(base_font) > 2 else 'underline'
            label.config(font=(base_font[0], base_font[1], st), fg=c.BTN_BLUE_TEXT)
        else:
            state = self.window.file_states.get(label.cget('text'))
            dim = state in ["applied", "deleted", "rejected", "skipped"]
            label.config(font=base_font, fg=c.TEXT_SUBTLE_COLOR if dim else c.TEXT_COLOR)

    def open_file_in_editor(self, rel_path):
        window = self.window
        full_path = os.path.join(window.base_dir, rel_path)
        if not os.path.isfile(full_path): return
        editor = window.app_state.config.get('default_editor', '')
        try:
            if editor and os.path.isfile(editor): subprocess.Popen([editor, full_path])
            else:
                if sys.platform == "win32": os.startfile(full_path)
                elif sys.platform == "darwin": subprocess.call(['open', full_path])
                else: subprocess.call(['xdg-open', full_path])
        except Exception as e: messagebox.showerror("Error", f"Could not open file: {e}", parent=window)

    def toggle_diff(self, path, container, action_type):
        if container.winfo_ismapped():
            container.pack_forget()
            return
        if path not in self._diff_viewers:
            old, new = "", ""
            if action_type == "create":
                new = self.window.plan['creations'].get(path, "")
            elif action_type == "delete":
                # For deletions, show current content as a plain view (like a new file)
                new = change_applier.get_current_file_content(self.window.base_dir, path) or ""
            else:
                old = change_applier.get_current_file_content(self.window.base_dir, path) or ""
                new = self.window.plan['updates'].get(path, "")

            v = DiffViewer(container, old, new)
            v.pack(fill='x', pady=(5, 10))
            self._diff_viewers[path] = v
        container.pack(fill='x')
        self.window.file_list_scroll._on_frame_configure()

    def apply_file_action(self, path, action_type):
        window = self.window
        original = None
        if action_type == "delete":
            if not os.path.isfile(os.path.join(window.base_dir, path)):
                window.file_states[path] = "deleted"; window.undo_buffer[path] = None
                self.refresh_file_list_ui(); return
        if action_type != "create":
            original = change_applier.get_current_file_content(window.base_dir, path)
            if original is None: return
        window.undo_buffer[path] = original
        success = False
        if action_type == "delete":
            success, _ = change_applier.delete_single_file(window.base_dir, path)
            if success: window.file_states[path] = "deleted"
        else:
            content = window.plan['updates'].get(path) or window.plan['creations'].get(path)
            success, _ = change_applier.apply_single_file(window.base_dir, path, content)
            if success:
                window.file_states[path] = "applied"
                # Automatic Addition to Merge List on individual Accept
                if hasattr(window.app, 'action_handlers'):
                    window.app.action_handlers.ensure_file_is_merged(path)

        if success:
            window.app.button_manager.update_button_states()
            self.refresh_file_list_ui()
            window.app.file_monitor.perform_new_file_check(schedule_next=False)

    def undo_file_action(self, path, action_type):
        window = self.window
        is_new = path in window.plan.get('creations', {})
        original = window.undo_buffer.get(path)
        success = False
        if window.file_states.get(path) == "rejected": success = True
        elif is_new: success, _ = change_applier.delete_single_file(window.base_dir, path)
        elif original is not None: success, _ = change_applier.apply_single_file(window.base_dir, path, original)
        if success:
            window.file_states[path] = "pending"
            window.app.button_manager.update_button_states()
            self.refresh_file_list_ui()
            window.app.file_monitor.perform_new_file_check(schedule_next=False)

    def discard_file_item(self, path):
        self.window.file_states[path] = "rejected"
        self.window.app.button_manager.update_button_states()
        self.refresh_file_list_ui()

    def update_mass_apply_visibility(self):
        window = self.window
        if not hasattr(window, 'apply_btn'): return
        has_pending = any(s == "pending" for s in window.file_states.values())
        if has_pending:
            manual = any(s in ["applied", "deleted", "rejected"] for s in window.file_states.values())
            window.apply_btn.config(text="Apply All Remaining" if manual else "Apply All")
            if not window.apply_btn.winfo_ismapped():
                window.cancel_btn.pack_forget()
                window.apply_btn.pack(side="right")
                window.cancel_btn.pack(side="right", padx=(0, 10))
        else: window.apply_btn.pack_forget()