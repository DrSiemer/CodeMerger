import tkinter as tk
import os
import pyperclip
from tkinter import Frame, Label, ttk, BooleanVar, messagebox
from PIL import Image, ImageDraw, ImageTk
from .. import constants as c
from .widgets.rounded_button import RoundedButton
from .widgets.markdown_renderer import MarkdownRenderer
from .widgets.scrollable_frame import ScrollableFrame
from .window_utils import position_window, save_window_geometry
from .style_manager import apply_dark_theme
from ..core.paths import ICON_PATH
from ..core.utils import save_config
from ..core import change_applier
from .tooltip import ToolTip
from .info_manager import attach_info_mode
from .assets import assets

class FeedbackDialog(tk.Toplevel):
    def __init__(self, parent, plan, on_apply=None, on_refuse=None, force_verification=False):
        super().__init__(parent)
        self.parent = parent
        self.plan = plan
        self.on_apply_executor = on_apply
        self.on_refuse = on_refuse

        # Identify the root App instance immediately for global action handling
        self.app = parent
        while self.app and not hasattr(self.app, 'action_handlers'):
            self.app = getattr(self.app, 'parent', getattr(self.app, 'master', None))

        # Track project base directory
        project = self.app.project_manager.get_current_project()
        self.base_dir = project.base_dir if project else ""

        # Establish Persistent State References
        if 'file_states' not in self.plan:
            self.plan['file_states'] = {}
            self.plan['undo_buffer'] = {}
            self.file_states = self.plan['file_states']
            self.undo_buffer = self.plan['undo_buffer']
            self._initialize_file_states()
        else:
            self.file_states = self.plan['file_states']
            self.undo_buffer = self.plan['undo_buffer']

        self.app_state = getattr(parent, 'app_state', getattr(parent.master, 'app_state', None))
        self.withdraw()
        self.title("AI Response Review")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)

        # Ensure grid is used on the Toplevel so the main frame and info panel never overlap
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Modality & Layering Logic
        is_parent_topmost = False
        try: is_parent_topmost = self.parent.attributes("-topmost")
        except Exception: pass
        if is_parent_topmost: self.attributes("-topmost", True)
        else: self.transient(parent)

        apply_dark_theme(self)

        # Generate vertical accent bars for all tabs
        self._gray_accent = self._create_vertical_accent(c.TEXT_SUBTLE_COLOR)  # Intro / Placeholder
        self._cyan_accent = self._create_vertical_accent("#00BCD4")           # Answers
        self._blue_accent = self._create_vertical_accent(c.BTN_BLUE)          # Changes
        self._red_accent = self._create_vertical_accent(c.WARN)               # Delete
        self._green_accent = self._create_vertical_accent(c.BTN_GREEN)        # Verification
        self._yellow_accent = self._create_vertical_accent(c.ATTENTION)       # Unformatted

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Main Layout Rows: 0=Header, 1=UnformattedAlert, 2=Notebook, 3=BottomActions
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        header_row = Frame(main_frame, bg=c.DARK_BG)
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_row.columnconfigure(0, weight=1)

        title_text = "Review Proposed Update" if on_apply else "Review Last Update"
        Label(header_row, text=title_text, font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w")

        self.new_files_btn = None
        self._check_for_new_files(header_row)

        ordered_segments = plan.get('ordered_segments', [])
        orphan_segments = [s for s in ordered_segments if s['type'] == 'orphan']
        has_unformatted = len(orphan_segments) > 0
        has_any_tags = plan.get('has_any_tags', False)

        self.alert_frame = Frame(main_frame, bg=c.DARK_BG)

        # UI CHANGE: Show the correction button if ANY unformatted segments exist.
        if has_unformatted:
            self.alert_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
            alert_msg = "This response contains commentary not wrapped in tags" if has_any_tags else "This response was not properly wrapped in XML tags"
            Label(self.alert_frame, text=alert_msg, fg=c.WARN, bg=c.DARK_BG, font=c.FONT_NORMAL).pack(side='left')

            self.admonish_btn = RoundedButton(self.alert_frame, text="Copy Correction Prompt", command=self._copy_admonishment, bg=c.ATTENTION, fg="#FFFFFF", font=c.FONT_SMALL_BUTTON, width=200, height=26, cursor="hand2")
            self.admonish_btn.pack(side='right')

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        self.renderers = []
        self.tab_widgets_for_info = []
        self.tab_indices = {}

        # Forced "Changes" tab order handling
        changes_tab_added = False
        current_idx = 0

        for seg in ordered_segments:
            stype = seg['type']
            content = seg.get('content', "").strip()
            if not content and stype != 'file_placeholder': continue

            if stype == 'tag':
                tag_name = seg['tag']
                if tag_name == "DELETED FILES": continue

                # Injection: Add Changes tab before Verification if it hasn't been added yet
                if tag_name == "VERIFICATION" and not changes_tab_added:
                    has_data = plan.get('updates') or plan.get('creations') or plan.get('deletions_proposed')
                    if has_data:
                        self._add_tab("Changes", "", icon=self._blue_accent, info_key="review_tab_changes")
                        changes_tab_added = True
                        current_idx += 1

                title = tag_name.replace("ANSWERS TO DIRECT USER QUESTIONS", "Answers").title()
                icon = self._gray_accent
                info_key = "review_tab_placeholder"
                if "INTRO" in tag_name: info_key = "review_tab_intro"
                elif "CHANGES" in tag_name:
                    icon = self._blue_accent; info_key = "review_tab_changes"
                    changes_tab_added = True
                elif "ANSWERS" in tag_name: icon = self._cyan_accent; info_key = "review_tab_answers"
                elif "VERIFICATION" in tag_name: icon = self._green_accent; info_key = "review_tab_verification"

                self._add_tab(title, content, icon=icon, info_key=info_key)
                if "VERIFICATION" in tag_name: self.tab_indices['verification'] = current_idx
                current_idx += 1
            elif stype == 'orphan':
                title = "Unformatted output"
                self._add_unformatted_tab(title, content)
                current_idx += 1

        if not changes_tab_added:
            has_data = plan.get('updates') or plan.get('creations') or plan.get('deletions_proposed')
            if has_data:
                self._add_tab("Changes", "", icon=self._blue_accent, info_key="review_tab_changes")

        if current_idx == 0:
            self._add_tab("Response Summary", "The AI response contained only code blocks.", icon=self._gray_accent, info_key="review_tab_placeholder")

        if force_verification and 'verification' in self.tab_indices:
            self.notebook.select(self.tab_indices['verification'])

        self.bottom_frame = Frame(main_frame, bg=c.DARK_BG)
        self.bottom_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))

        show_val = self.app_state.config.get('show_feedback_on_paste', True) if self.app_state else True
        self.show_var = BooleanVar(value=show_val)
        self.auto_show_chk = ttk.Checkbutton(self.bottom_frame, text="Show automatically", variable=self.show_var, style='Dark.TCheckbutton', command=self._save_setting)
        self.auto_show_chk.pack(side="left")

        if self.on_apply_executor:
            # Main action buttons
            self.apply_btn = RoundedButton(self.bottom_frame, text="Apply All Remaining", command=self._handle_apply_all, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BOLD, width=200, height=30, cursor="hand2")
            self.cancel_btn = RoundedButton(self.bottom_frame, text="Close", command=self.destroy, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")

            # Initial pack
            self.apply_btn.pack(side="right")
            self.cancel_btn.pack(side="right", padx=(0, 10))
        else:
            self.ok_button = RoundedButton(self.bottom_frame, text="OK", command=self.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
            self.ok_button.pack(side="right")

        self.bind("<Escape>", lambda e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        initial_w, initial_h = 900, 750
        if self.app_state and self.app_state.info_mode_active: initial_h += c.INFO_PANEL_HEIGHT
        self.geometry(f"{initial_w}x{initial_h}")
        self.minsize(600, 500)
        position_window(self)

        if self.app_state:
            self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")
            self.info_mgr = attach_info_mode(self, self.app_state, manager_type='grid', grid_row=1, toggle_btn=self.info_toggle_btn)
            self.info_mgr.register(self.notebook, "review_tabs")
            self.info_mgr.register(self.auto_show_chk, "review_auto_show")
            if hasattr(self, 'apply_btn'): self.info_mgr.register(self.apply_btn, "review_apply")
            self.info_mgr.register(self.info_toggle_btn, "info_toggle")

        self._update_mass_apply_visibility()
        self.deiconify()

    def _initialize_file_states(self):
        for path in self.plan.get('updates', {}): self.file_states[path] = "pending"
        for path in self.plan.get('creations', {}): self.file_states[path] = "pending"
        for path in self.plan.get('deletions_proposed', []): self.file_states[path] = "pending"

    def _add_tab(self, title, markdown_text, icon=None, info_key=None):
        if title == "Changes":
            self._add_interactive_changes_tab(title, markdown_text, icon)
            return
        frame = Frame(self.notebook, bg=c.DARK_BG)
        if icon: self.notebook.add(frame, text=title, image=icon, compound="left")
        else: self.notebook.add(frame, text=title)
        renderer = MarkdownRenderer(frame, base_font_size=11, on_zoom=self._adjust_font_size)
        renderer.pack(fill="both", expand=True)
        renderer.set_markdown(markdown_text.strip())
        self.renderers.append(renderer)
        if info_key: self.tab_widgets_for_info.append((renderer, info_key))

    def _add_interactive_changes_tab(self, title, desc, icon):
        frame = Frame(self.notebook, bg=c.DARK_BG)
        self.notebook.add(frame, text=title, image=icon, compound="left")
        header = Frame(frame, bg=c.DARK_BG, padx=15, pady=10)
        header.pack(fill='x')
        Label(header, text="Proposed Actions", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')

        if desc.strip():
            self.toggle_desc_btn = RoundedButton(header, text="Show AI Commentary", command=self._toggle_commentary, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
            self.toggle_desc_btn.pack(side='right')
            self.commentary_renderer = MarkdownRenderer(frame, base_font_size=10, height=8)
            self.commentary_renderer.set_markdown(desc.strip())

        self.file_list_scroll = ScrollableFrame(frame, bg=c.DARK_BG)
        self.file_list_scroll.pack(fill='both', expand=True, padx=15, pady=(0, 10))
        self._refresh_file_list_ui()

    def _toggle_commentary(self):
        if not hasattr(self, 'commentary_renderer'): return
        if self.commentary_renderer.winfo_ismapped():
            self.commentary_renderer.pack_forget()
            self.toggle_desc_btn.config(text="Show AI Commentary", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        else:
            self.commentary_renderer.pack(fill='x', before=self.file_list_scroll, padx=15, pady=(0, 10))
            self.toggle_desc_btn.config(text="Hide AI Commentary", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)

    def _refresh_file_list_ui(self):
        container = self.file_list_scroll.scrollable_frame
        for w in container.winfo_children(): w.destroy()

        updates = self.plan.get('updates', {})
        creations = self.plan.get('creations', {})
        deletions = self.plan.get('deletions_proposed', [])

        if updates:
            self._create_group_header(container, "Modify Content", c.BTN_BLUE)
            for p in sorted(updates.keys()): self._create_file_row(container, p, "modify")
        if creations:
            self._create_group_header(container, "Create New File", c.BTN_GREEN)
            for p in sorted(creations.keys()): self._create_file_row(container, p, "create")
        if deletions:
            self._create_group_header(container, "Delete Obsolete File", c.WARN)
            for p in sorted(deletions): self._create_file_row(container, p, "delete")

        self._update_mass_apply_visibility()

    def _create_group_header(self, parent, text, color):
        f = Frame(parent, bg=c.DARK_BG)
        f.pack(fill='x', pady=(15, 5))
        Label(f, text=text.upper(), font=(c.FONT_FAMILY_PRIMARY, 9, 'bold'), bg=c.DARK_BG, fg=color).pack(side='left')
        Frame(f, bg=color, height=1).pack(side='left', fill='x', expand=True, padx=(10, 0))

    def _create_file_row(self, parent, path, action_type):
        row = Frame(parent, bg=c.DARK_BG)
        row.pack(fill='x', pady=2)
        state = self.file_states.get(path, "pending")

        is_handled = state in ["applied", "deleted", "rejected"]
        font = (c.FONT_FAMILY_PRIMARY, 11, 'overstrike') if is_handled else c.FONT_NORMAL
        fg = c.TEXT_SUBTLE_COLOR if is_handled else c.TEXT_COLOR

        Label(row, text=path, font=font, fg=fg, bg=c.DARK_BG, anchor='w').pack(side='left', fill='x', expand=True)
        btn_frame = Frame(row, bg=c.DARK_BG)
        btn_frame.pack(side='right')

        if is_handled:
            is_new_creation = path in self.plan.get('creations', {})
            show_undo = False
            if state == "rejected": show_undo = True
            elif is_new_creation: show_undo = True
            elif path in self.undo_buffer and self.undo_buffer[path] is not None: show_undo = True

            if show_undo:
                RoundedButton(btn_frame, text="Undo", command=lambda: self._undo_file_action(path, action_type), bg="#666666", fg="#FFFFFF", font=c.FONT_SMALL_BUTTON, width=60, height=24, radius=4, cursor="hand2").pack()
        else:
            if action_type == "delete":
                RoundedButton(btn_frame, text="Accept Delete", command=lambda: self._apply_file_action(path, "delete"), bg=c.WARN, fg="#FFFFFF", font=c.FONT_SMALL_BUTTON, width=100, height=24, radius=4, cursor="hand2").pack(side='left', padx=2)
                RoundedButton(btn_frame, text="Keep", command=lambda: self._discard_file_item(path), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=60, height=24, radius=4, cursor="hand2").pack(side='left')
            else:
                RoundedButton(btn_frame, text="Accept", command=lambda: self._apply_file_action(path, action_type), bg=c.BTN_GREEN, fg="#FFFFFF", font=c.FONT_SMALL_BUTTON, width=70, height=24, radius=4, cursor="hand2").pack(side='left', padx=2)
                RoundedButton(btn_frame, text="Discard", command=lambda: self._discard_file_item(path), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=70, height=24, radius=4, cursor="hand2").pack(side='left')

    def _apply_file_action(self, path, action_type):
        original = None
        if action_type == "delete":
            full_path = os.path.join(self.base_dir, path)
            if not os.path.isfile(full_path):
                messagebox.showinfo("File Already Missing", f"The file '{path}' is already missing from disk. Marking as handled.", parent=self)
                self.file_states[path] = "deleted"
                self.undo_buffer[path] = None
                self._refresh_file_list_ui()
                return

        if action_type != "create":
            original = change_applier.get_current_file_content(self.base_dir, path)
            if original is None:
                messagebox.showwarning("Access Error", f"Cannot backup '{path}'. Action cancelled.", parent=self)
                return

        self.undo_buffer[path] = original

        success = False
        if action_type == "delete":
            success, err = change_applier.delete_single_file(self.base_dir, path)
            if success: self.file_states[path] = "deleted"
        else:
            content = self.plan['updates'].get(path) or self.plan['creations'].get(path)
            success, err = change_applier.apply_single_file(self.base_dir, path, content)
            if success: self.file_states[path] = "applied"

        if success:
            self.app.button_manager.update_button_states()
            self._refresh_file_list_ui()
            self.app.file_monitor.perform_new_file_check(schedule_next=False)
        else:
            messagebox.showerror("IO Error", f"Failed to process {path}: {err}", parent=self)

    def _undo_file_action(self, path, action_type):
        is_new_creation = path in self.plan.get('creations', {})
        original_content = self.undo_buffer.get(path)
        success = False

        if self.file_states.get(path) == "rejected":
            success = True
        elif is_new_creation:
            success, err = change_applier.delete_single_file(self.base_dir, path)
        elif original_content is not None:
            success, err = change_applier.apply_single_file(self.base_dir, path, original_content)

        if success:
            self.file_states[path] = "pending"
            self.app.button_manager.update_button_states()
            self._refresh_file_list_ui()
            self.app.file_monitor.perform_new_file_check(schedule_next=False)
        else:
            messagebox.showerror("Undo Error", f"Could not restore {path}", parent=self)

    def _discard_file_item(self, path):
        self.file_states[path] = "rejected"
        self.app.button_manager.update_button_states()
        self._refresh_file_list_ui()

    def _update_mass_apply_visibility(self):
        """Hides the mass apply button if no files are in pending state. Forces order [Close] [Apply]."""
        if not hasattr(self, 'apply_btn'): return

        has_pending = any(s == "pending" for s in self.file_states.values())
        if has_pending:
            if not self.apply_btn.winfo_ismapped():
                # Correct button order: Cancel on left, Apply on far right
                self.cancel_btn.pack_forget()
                self.apply_btn.pack(side="right")
                self.cancel_btn.pack(side="right", padx=(0, 10))
        else:
            self.apply_btn.pack_forget()

    def _handle_apply_all(self):
        pending_updates = {p: c for p, c in self.plan.get('updates', {}).items() if self.file_states.get(p) == "pending"}
        pending_creations = {p: c for p, c in self.plan.get('creations', {}).items() if self.file_states.get(p) == "pending"}
        pending_deletions = [p for p in self.plan.get('deletions_proposed', []) if self.file_states.get(p) == "pending"]

        if not (pending_updates or pending_creations or pending_deletions):
            return

        for path in list(pending_updates.keys()) + pending_deletions:
            if path not in self.undo_buffer:
                 self.undo_buffer[path] = change_applier.get_current_file_content(self.base_dir, path)

        if self.on_apply_executor(pending_updates, pending_creations, pending_deletions) is not False:
            for p in pending_updates: self.file_states[p] = "applied"
            for p in pending_creations: self.file_states[p] = "applied"
            for p in pending_deletions: self.file_states[p] = "deleted"

            if 'verification' in self.tab_indices:
                self._update_mass_apply_visibility()
                self.cancel_btn.config(text="Close")
                self.notebook.select(self.tab_indices['verification'])
            else:
                self.destroy()

    def _check_for_new_files(self, container):
        if not self.app: return
        new_count = len(self.app.file_monitor.newly_detected_files)
        if new_count > 0:
            self.new_files_btn = Label(container, image=assets.new_files_icon, bg=c.DARK_BG, cursor="hand2")
            self.new_files_btn.grid(row=0, column=1, sticky="e")
            self.new_files_btn.bind("<ButtonRelease-1>", lambda e: (self.app.action_handlers.add_new_files_to_merge_order(), self.new_files_btn.grid_forget()))
            ToolTip(self.new_files_btn, f"{new_count} new files found.")

    def _create_vertical_accent(self, hex_color):
        size = (14, 22)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 1, 3, 20], radius=1, fill=hex_color)
        return ImageTk.PhotoImage(img)

    def _add_unformatted_tab(self, title, raw_text):
        frame = Frame(self.notebook, bg=c.DARK_BG)
        self.notebook.add(frame, text=title, image=self._yellow_accent, compound="left")
        renderer = MarkdownRenderer(frame, base_font_size=11, on_zoom=self._adjust_font_size)
        renderer.pack(fill="both", expand=True)
        renderer.set_markdown(raw_text.strip())
        self.renderers.append(renderer)
        self.tab_widgets_for_info.append((renderer, "review_tab_unformatted"))

    def _copy_admonishment(self):
        msg = "Please follow the output format as described in your instructions."
        pyperclip.copy(msg)
        self.admonish_btn.config(text="Copied!", bg=c.BTN_GREEN)
        self.after(2000, lambda: self.admonish_btn.config(text="Copy Correction Prompt", bg=c.ATTENTION) if self.admonish_btn.winfo_exists() else None)

    def _adjust_font_size(self, delta):
        if not self.renderers: return
        new_size = max(8, min(self.renderers[0].base_font_size + delta, 40))
        for r in self.renderers: r.set_font_size(new_size)

    def _save_setting(self):
        if not self.app_state: return
        self.app_state.config['show_feedback_on_paste'] = self.show_var.get()
        save_config(self.app_state.config)
        self.app.button_manager.refresh_paste_tooltips()

    def destroy(self):
        if hasattr(self.app, 'active_feedback_dialog') and self.app.active_feedback_dialog is self:
            self.app.active_feedback_dialog = None
        save_window_geometry(self)
        super().destroy()