import tkinter as tk
import pyperclip
from tkinter import Frame, Label, Text, messagebox, Toplevel
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...widgets.markdown_renderer import MarkdownRenderer
from ...window_utils import position_window
from ...tooltip import ToolTip
from ..segment_manager import SegmentManager

class SyncUnsignedDialog(Toplevel):
    """
    A dialog to handle the prompt generation and response parsing for propagating changes.
    """
    def __init__(self, parent, prompt, on_apply_callback):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.prompt = prompt
        self.on_apply_callback = on_apply_callback
        self.result = None

        self.title("Sync Unsigned Segments")
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

        self.geometry("600x600")
        self.minsize(500, 500)
        position_window(self)
        self.deiconify()

    def _build_ui(self):
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        Label(main_frame, text="Propagate Changes", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 10))
        Label(main_frame, text="Update other unsigned segments to match your recent changes.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Step 1: Copy Prompt
        step1_frame = Frame(main_frame, bg=c.DARK_BG)
        step1_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        Label(step1_frame, text="1. Copy Prompt", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")
        copy_btn = RoundedButton(step1_frame, text="Copy", command=lambda: self._copy_prompt(copy_btn), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        copy_btn.pack(side="right")

        # Step 2: Paste Response
        Label(main_frame, text="2. Paste Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=4, column=0, sticky="w", pady=(15, 5))

        self.response_text = ScrollableText(main_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.response_text.grid(row=5, column=0, sticky="nsew", pady=(0, 15))

        # Actions
        btn_frame = Frame(main_frame, bg=c.DARK_BG)
        btn_frame.grid(row=6, column=0, sticky="e")

        RoundedButton(btn_frame, text="Cancel", command=self.destroy, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor="hand2").pack(side="left", padx=(0, 10))
        RoundedButton(btn_frame, text="Apply Changes", command=self._on_apply, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=120, height=30, cursor="hand2").pack(side="left")

    def _copy_prompt(self, btn):
        pyperclip.copy(self.prompt)
        btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: btn.config(text="Copy", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

    def _on_apply(self):
        content = self.response_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Input Required", "Please paste the LLM response first.", parent=self)
            return

        self.on_apply_callback(content)
        self.destroy()

class SidebarItem(Frame):
    def __init__(self, parent, text, is_overview, status_var=None, command=None):
        super().__init__(parent, bg=c.DARK_BG, cursor="hand2")
        self.command = command
        self.is_selected = False
        self.is_disabled = False
        self.is_updated = False # Indicates content was changed via sync but not viewed
        self.status_var = status_var
        self.is_overview = is_overview

        # Alignment: Overview (Full Text) is the parent. Segments are children.
        if not is_overview:
            # Bullet indicator for segments (Uses Unicode Black Circle)
            self.indicator = Label(self, text="●", font=("Arial", 12), bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR)
            self.indicator.pack(side="left", padx=(15, 5))
            text_padx = (0, 10)
        else:
            # No indicator for Full Text, align to far left
            self.indicator = Label(self, bg=c.DARK_BG)
            text_padx = (10, 10)

        label_text = text
        font = c.FONT_BOLD if is_overview else c.FONT_NORMAL

        self.label = Label(self, text=label_text, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font, anchor="w")
        self.label.pack(side="left", fill="x", expand=True, pady=8, padx=text_padx)

        self._bind_events()

        if self.status_var:
            self.status_var.trace_add("write", self._update_status_icon)
            self._update_status_icon()

    def _bind_events(self):
        self.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)
        if hasattr(self, 'indicator') and self.indicator.winfo_ismapped():
            self.indicator.bind("<Button-1>", self._on_click)

    def _unbind_events(self):
        self.unbind("<Button-1>")
        self.label.unbind("<Button-1>")
        if hasattr(self, 'indicator'): self.indicator.unbind("<Button-1>")

    def _on_click(self, event=None):
        if not self.is_disabled and self.command:
            self.command()

    def set_selected(self, selected):
        if self.is_disabled: return
        self.is_selected = selected
        bg = c.TEXT_INPUT_BG if selected else c.DARK_BG
        self.config(bg=bg)
        self.label.config(bg=bg)
        self.indicator.config(bg=bg)

    def set_disabled(self, disabled):
        self.is_disabled = disabled
        if disabled:
            fg = c.BTN_GRAY_TEXT
            cursor = "arrow"
            self._unbind_events()
        else:
            fg = c.TEXT_COLOR
            cursor = "hand2"
            self._bind_events()

        self.config(cursor=cursor)
        self.label.config(fg=fg, cursor=cursor)
        self.indicator.config(fg=fg, cursor=cursor)

    def set_updated(self, updated):
        """Marks the item as having pending changes from a sync operation."""
        # Don't show updated status if the item is signed off or disabled
        if self.is_disabled or (self.status_var and self.status_var.get()):
            return
        self.is_updated = updated
        self._update_status_icon()

    def _update_status_icon(self, *args):
        if not self.status_var or self.is_overview: return

        if self.status_var.get():
            # Signed Off: Green Check
            self.indicator.config(text="✓", fg=c.BTN_GREEN)
        elif self.is_updated:
            # Updated / Attention Needed: Orange Dot
            self.indicator.config(text="●", fg=c.ATTENTION)
        else:
            # Default: Gray Dot
            self.indicator.config(text="●", fg=c.TEXT_SUBTLE_COLOR)

class SegmentedReviewer(Frame):
    """
    A widget that presents content in segments with a sidebar for navigation,
    sign-off capability, and a full overview mode.
    Corrects the overwrite race condition by using navigation locking.
    """
    def __init__(self, parent, segment_keys, friendly_names_map, segments_data, signoffs_data, questions_map=None, on_change_callback=None):
        super().__init__(parent, bg=c.DARK_BG)
        self.segment_keys = segment_keys
        self.friendly_names_map = friendly_names_map
        self.segments_data = segments_data
        self.signoffs_data = signoffs_data
        self.questions_map = questions_map or {}
        self.on_change_callback = on_change_callback

        self.active_key = None
        self.sidebar_items = {}
        self.current_question_index = 0
        self.is_loading_nav = False # Prevents overwrite race conditions

        self.signoff_vars = {}
        for key in self.segment_keys:
            val = self.signoffs_data.get(key, False)
            bv = tk.BooleanVar(value=val)
            bv.trace_add("write", lambda *a, k=key, v=bv: self._on_signoff_var_change(k, v))
            self.signoff_vars[key] = bv

        self._build_ui()

        # Determine start key
        start_key = "overview"
        if self.segment_keys:
            start_key = self.segment_keys[0]
            for key in self.segment_keys:
                if not self.signoff_vars[key].get():
                    start_key = key
                    break

            if all(self.signoff_vars[k].get() for k in self.segment_keys):
                self._update_overview_availability()
                start_key = "overview"

        self._navigate(start_key)

    def _on_signoff_var_change(self, key, var):
        self.signoffs_data[key] = var.get()
        self._update_overview_availability()
        if self.on_change_callback:
            self.on_change_callback()

    def _update_overview_availability(self):
        if not self.segment_keys: return
        all_signed = all(self.signoff_vars[k].get() for k in self.segment_keys)
        ov_item = self.sidebar_items.get("overview")
        if ov_item:
            ov_item.set_disabled(not all_signed)

    def _build_ui(self):
        # Sidebar
        self.sidebar_frame = Frame(self, bg=c.DARK_BG, width=220)
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar_frame.pack_propagate(False)

        ov_item = SidebarItem(self.sidebar_frame, "Full Text", True, command=lambda: self._navigate("overview"))
        ov_item.pack(fill="x")
        self.sidebar_items["overview"] = ov_item

        Frame(self.sidebar_frame, bg=c.WRAPPER_BORDER, height=1).pack(fill="x", pady=5)

        for key in self.segment_keys:
            name = self.friendly_names_map.get(key, key)
            item = SidebarItem(
                self.sidebar_frame, name, False,
                status_var=self.signoff_vars[key],
                command=lambda k=key: self._navigate(k)
            )
            item.pack(fill="x")
            self.sidebar_items[key] = item

        # Content Area
        self.content_area = Frame(self, bg=c.DARK_BG)
        self.content_area.pack(side="left", fill="both", expand=True)

        self.header_frame = Frame(self.content_area, bg=c.DARK_BG)
        self.header_frame.pack(side="top", fill="x", pady=(0, 10))
        self.title_label = Label(self.header_frame, text="", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR)
        self.title_label.pack(side="left")

        self.header_controls = Frame(self.header_frame, bg=c.DARK_BG)
        self.header_controls.pack(side="right")

        self.main_view_container = Frame(self.content_area, bg=c.DARK_BG)
        self.main_view_container.pack(fill="both", expand=True)

        # Footer (Packed first to ensure visibility)
        self.footer = Frame(self.main_view_container, bg=c.DARK_BG)
        self.footer.pack(side="bottom", fill="x", pady=(10, 0))

        # Footer buttons container
        self.footer_buttons_frame = Frame(self.footer, bg=c.DARK_BG)
        self.footer_buttons_frame.pack(fill='x', expand=True)

        # Right-aligned buttons
        self.signoff_btn = RoundedButton(self.footer_buttons_frame, text="Sign Off & Next", command=self._sign_off, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, width=160, cursor="hand2")
        self.signoff_btn.pack(side="right")

        # Left-aligned buttons
        self.revert_btn = RoundedButton(self.footer_buttons_frame, text="Unlock to Edit", command=self._revert_draft, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2")

        self.sync_btn = RoundedButton(self.footer_buttons_frame, text="Sync Unsigned", command=self._open_sync_dialog, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_SMALL_BUTTON, width=130, cursor="hand2")
        ToolTip(self.sync_btn, "Propagates your changes to other unlocked sections to maintain consistency.\n(Only affects sections that are not signed off)", delay=500)

        # Questions Panel
        self.questions_panel = Frame(self.main_view_container, bg=c.STATUS_BG, padx=10, pady=10)

        # Display Area
        self.display_container = Frame(self.main_view_container, bg=c.DARK_BG)
        self.display_container.pack(side="top", fill="both", expand=True)
        self.display_container.grid_rowconfigure(0, weight=1)
        self.display_container.grid_columnconfigure(0, weight=1)

        # Standard Edit Font (11)
        self.editor = ScrollableText(self.display_container, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_DEFAULT)
        self.editor.text_widget.bind("<KeyRelease>", self._on_text_change)

        # Larger Render Font (14)
        self.renderer = MarkdownRenderer(self.display_container, base_font_size=14)
        # Bind double-click to enable edit mode from markdown view
        self.renderer.text_widget.bind("<Double-Button-1>", self._on_renderer_double_click)

    def _on_renderer_double_click(self, event):
        """
        Handles double-click on the markdown renderer.
        Switches to edit mode and attempts to place cursor at the clicked line.
        """
        # If edit mode is locked (e.g. signed off), do nothing
        if self.revert_btn.winfo_ismapped():
            return

        # 1. Capture the index from the rendered widget
        try:
            click_index = self.renderer.text_widget.index(f"@{event.x},{event.y}")
        except Exception:
            click_index = "1.0"

        # 2. Switch to Edit Mode
        self._toggle_view(force_render=False) # is_raw_mode -> True

        # 3. Apply position to Editor
        # Note: Line mapping is approximate because renderer hides markdown syntax
        self.editor.update_idletasks()
        self.editor.text_widget.mark_set("insert", click_index)
        self.editor.text_widget.see(click_index)
        self.editor.text_widget.focus_set()

    def _navigate(self, key):
        if self.is_loading_nav: return
        self.is_loading_nav = True

        try:
            # 1. Save current into dictionary BEFORE changing the key pointer
            if self.active_key and self.active_key != "overview" and self.active_key in self.segments_data:
                self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()

            # 2. Nullify active key to prevent any events from writing to data during transition
            self.active_key = None

            # 3. Reset UI state
            self.current_question_index = 0
            for k, item in self.sidebar_items.items(): item.set_selected(k == key)
            for w in self.header_controls.winfo_children(): w.destroy()

            self.questions_panel.pack_forget()
            self.editor.grid_forget()
            self.renderer.grid_forget()

            # Ensure editor is enabled so delete works.
            # (If coming from a signed-off segment, the editor was disabled)
            self.editor.text_widget.config(state="normal")

            # Clear editor buffer
            self.editor.delete("1.0", "end")

            # Reset updated status if visiting that segment
            if key in self.sidebar_items:
                self.sidebar_items[key].set_updated(False)

            if key == "overview":
                self._show_overview()
            else:
                self._show_segment(key)

            # 4. Finally update the segment pointer
            self.active_key = key
        finally:
            self.is_loading_nav = False

    def _show_segment(self, key):
        name = self.friendly_names_map.get(key, key)
        self.title_label.config(text=name)

        # Load content
        content = self.segments_data.get(key, "")
        self.editor.insert("1.0", content)

        # Build Header Controls
        self.q_btn = RoundedButton(self.header_controls, text="Questions", command=self._toggle_questions, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, cursor="hand2")
        self.q_btn.pack(side="left")

        self.is_raw_mode = tk.BooleanVar(value=False)
        self.view_btn = RoundedButton(self.header_controls, text="Edit", command=self._toggle_view, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="left", padx=(10, 0))

        self._update_questions_panel(key)
        self._toggle_view(force_render=True)
        self._update_footer_state(key)

    def _toggle_view(self, force_render=False):
        if force_render: self.is_raw_mode.set(False)
        else: self.is_raw_mode.set(not self.is_raw_mode.get())

        if self.is_raw_mode.get():
            self.renderer.grid_forget()
            self.editor.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Render", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            # Clear text selection before rendering to avoid stuck selections
            self.editor.text_widget.tag_remove("sel", "1.0", "end")

            content = self.editor.get("1.0", "end-1c")
            self.renderer.set_markdown(content)
            self.editor.grid_forget()
            self.renderer.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Edit", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _update_questions_panel(self, key):
        for w in self.questions_panel.winfo_children(): w.destroy()
        q_list = self.questions_map.get(key, {}).get("questions", [])
        if not q_list:
            Label(self.questions_panel, text="No specific questions for this segment.", bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack()
            return

        header = Frame(self.questions_panel, bg=c.STATUS_BG); header.pack(fill="x")
        Label(header, text="Review Question:", font=c.FONT_BOLD, bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack(side="left")

        nav = Frame(header, bg=c.STATUS_BG); nav.pack(side="right")
        def move(delta):
            self.current_question_index = max(0, min(self.current_question_index + delta, len(q_list)-1))
            self._refresh_q_text(lbl, q_list, pb, nb)

        pb = RoundedButton(nav, text="<", command=lambda: move(-1), width=24, height=24, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2")
        pb.pack(side="left")
        nb = RoundedButton(nav, text=">", command=lambda: move(1), width=24, height=24, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2")
        nb.pack(side="left", padx=5)

        lbl = Label(self.questions_panel, text="", justify="left", anchor="w", bg=c.STATUS_BG, fg=c.TEXT_COLOR, wraplength=550, font=c.FONT_NORMAL)
        lbl.pack(fill="x", pady=(5, 10))
        self._refresh_q_text(lbl, q_list, pb, nb)

        copy_btn = RoundedButton(self.questions_panel, text="Copy Context & Question", command=lambda: self._copy_q_context(q_list[self.current_question_index], copy_btn), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=26, cursor="hand2")
        copy_btn.pack(anchor="w")

    def _refresh_q_text(self, lbl, q_list, pb, nb):
        idx = self.current_question_index
        lbl.config(text=q_list[idx])
        pb.set_state("normal" if idx > 0 else "disabled")
        nb.set_state("normal" if idx < len(q_list)-1 else "disabled")

    def _toggle_questions(self):
        if self.questions_panel.winfo_ismapped():
            self.questions_panel.pack_forget()
            self.q_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        else:
            self.questions_panel.pack(side="top", fill="x", before=self.display_container, pady=(0, 10))
            self.q_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)

    def _copy_q_context(self, question, btn):
        context = ""
        for k in self.segment_keys:
            if k == self.active_key: continue
            txt = self.segments_data.get(k, "").strip()
            if txt: context += f"--- Context: {self.friendly_names_map.get(k, k)} ---\n{txt}\n\n"

        current_txt = self.editor.get("1.0", "end-1c").strip()
        current_name = self.friendly_names_map.get(self.active_key, self.active_key)

        prompt = f"### Context\n{context}\n### Focus: {current_name}\n{current_txt}\n### Question\n{question}\n\nInstruction: Focus ONLY on the segment '{current_name}'."
        pyperclip.copy(prompt)
        btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: btn.config(text="Copy Context & Question", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

    def _show_overview(self):
        self.title_label.config(text="Full Text Overview")
        self.signoff_btn.pack_forget()
        self.revert_btn.pack_forget()
        self.sync_btn.pack_forget()

        self.is_raw_mode = tk.BooleanVar(value=False)
        self.view_btn = RoundedButton(self.header_controls, text="Edit", command=self._toggle_view, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="right")

        full_text = SegmentManager.assemble_document(self.segments_data, self.segment_keys, self.friendly_names_map)
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", full_text)
        self._toggle_view(force_render=True)

    def _on_text_change(self, event=None):
        if self.is_loading_nav or self.active_key is None: return
        if self.active_key != "overview":
            self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
            if self.on_change_callback: self.on_change_callback()

    def _update_footer_state(self, key=None):
        target_key = key or self.active_key
        if target_key == "overview" or not target_key: return

        is_signed = self.signoff_vars[target_key].get()
        if is_signed:
            self.signoff_btn.pack_forget()
            self.sync_btn.pack_forget()
            self.revert_btn.pack(side="left", padx=(0, 10))
            self.editor.text_widget.config(state="disabled", bg=c.DARK_BG)
        else:
            self.revert_btn.pack_forget()
            self.signoff_btn.pack(side="right")

            # Logic for Sync Button visibility
            # Can only sync if:
            # 1. Current segment has content
            # 2. There are OTHER segments that are NOT signed off
            other_unsigned = any(
                not self.signoff_vars[k].get()
                for k in self.segment_keys
                if k != target_key
            )
            has_content = bool(self.segments_data.get(target_key, "").strip())

            if other_unsigned and has_content:
                self.sync_btn.pack(side="left")
            else:
                self.sync_btn.pack_forget()

            self.editor.text_widget.config(state="normal", bg=c.TEXT_INPUT_BG)

    def _sign_off(self):
        # Manual save before move
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        self.signoff_vars[self.active_key].set(True)
        self._update_footer_state()
        self._update_overview_availability()

        current_idx = self.segment_keys.index(self.active_key)
        for i in range(current_idx + 1, len(self.segment_keys)):
            next_key = self.segment_keys[i]
            if not self.signoff_vars[next_key].get():
                self._navigate(next_key)
                return

        if all(self.signoff_vars[k].get() for k in self.segment_keys):
            self._navigate("overview")

    def _revert_draft(self):
        self.signoff_vars[self.active_key].set(False)
        self._update_footer_state()
        self._update_overview_availability()

    def _open_sync_dialog(self):
        # Save current content first
        current_content = self.editor.get("1.0", "end-1c").strip()
        self.segments_data[self.active_key] = current_content

        # Identify segments
        targets = []
        references = []

        for k in self.segment_keys:
            if k == self.active_key:
                continue

            if self.signoff_vars[k].get():
                references.append(k)
            else:
                targets.append(k)

        if not targets:
            messagebox.showinfo("Nothing to Sync", "All other segments are signed off.")
            return

        # Build Prompt
        friendly_map = {k: self.friendly_names_map.get(k, k) for k in targets}
        target_instructions = SegmentManager.build_prompt_instructions(targets, friendly_map)

        # Build Context Blocks
        target_context_blocks = []
        for t_key in targets:
            t_name = friendly_map[t_key]
            t_content = self.segments_data.get(t_key, "")
            target_context_blocks.append(f"--- Current Draft: {t_name} ---\n{t_content}\n")
        target_context_str = "\n".join(target_context_blocks)

        reference_context_str = ""
        if references:
            ref_blocks = []
            for r_key in references:
                r_name = self.friendly_names_map.get(r_key, r_key)
                r_content = self.segments_data.get(r_key, "")
                ref_blocks.append(f"--- Locked Section: {r_name} ---\n{r_content}\n")
            reference_context_str = "\n### Locked Sections (Reference Only - DO NOT CHANGE)\n" + "\n".join(ref_blocks)

        current_name = self.friendly_names_map.get(self.active_key, self.active_key)

        prompt = f"""You are a Consistency Engine. The user has modified the section **{current_name}**.
Your task is to rewrite the *unsigned* draft sections to be consistent with these changes, while respecting the *locked* sections.

### New Content: {current_name} (Source of Truth)
```
{current_content}
```
{reference_context_str}
### Drafts to Update (Rewrite these)
{target_context_str}

### Instructions
1. Review the "Drafts to Update".
2. Rewrite them to align with the logic/facts in "{current_name}" and the "Locked Sections" (if any).
3. Preserve existing details in the drafts unless they conflict.
4. {target_instructions}
5. Do NOT output content for the Locked Sections. Only output the Drafts.
"""
        SyncUnsignedDialog(self, prompt, self._apply_sync_results)

    def _apply_sync_results(self, llm_output):
        parsed = SegmentManager.parse_segments(llm_output)
        if not parsed:
            messagebox.showerror("Error", "Could not parse segments from response.")
            return

        mapped = SegmentManager.map_parsed_segments_to_keys(parsed, self.friendly_names_map)

        updated_count = 0
        for key, content in mapped.items():
            # Only update if the key is actually in our segments and is unsigned
            if key in self.segments_data and key != self.active_key and not self.signoff_vars[key].get():
                self.segments_data[key] = content
                if key in self.sidebar_items:
                    self.sidebar_items[key].set_updated(True)
                updated_count += 1

        if updated_count == 0:
            messagebox.showinfo("Info", "No matching segments found to update.")

    def get_assembled_content(self):
        full_text = SegmentManager.assemble_document(self.segments_data, self.segment_keys, self.friendly_names_map)
        return full_text, self.segments_data, self.signoffs_data