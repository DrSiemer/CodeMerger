import tkinter as tk
from tkinter import Frame, Label, messagebox
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...widgets.markdown_renderer import MarkdownRenderer
from ...tooltip import ToolTip
from ..segment_manager import SegmentManager

# Extracted Component Imports
from .sidebar_item import SidebarItem
from .rewrite_dialog import RewriteUnsignedDialog
from .sync_dialog import SyncUnsignedDialog

class SegmentedReviewer(Frame):
    """
    A widget that presents content in segments with a sidebar for navigation,
    sign-off capability, and a final merge trigger.
    """
    def __init__(self, parent, segment_keys, friendly_names_map, segments_data, signoffs_data, questions_map=None, on_change_callback=None, on_merge_callback=None):
        super().__init__(parent, bg=c.DARK_BG)
        self.segment_keys = segment_keys
        self.friendly_names_map = friendly_names_map
        self.segments_data = segments_data
        self.signoffs_data = signoffs_data
        self.questions_map = questions_map or {}
        self.on_change_callback = on_change_callback
        self.on_merge_callback = on_merge_callback

        self.active_key = None
        self.sidebar_items = {}
        self.current_question_index = 0
        self.is_loading_nav = False # Prevents overwrite race conditions
        self.current_segment_original_text = "" # Tracks content state for sync button logic
        self.questions_visible = False # Track visibility state across segments

        self.signoff_vars = {}
        for key in self.segment_keys:
            val = self.signoffs_data.get(key, False)
            bv = tk.BooleanVar(value=val)
            bv.trace_add("write", lambda *a, k=key, v=bv: self._on_signoff_var_change(k, v))
            self.signoff_vars[key] = bv

        self._build_ui()

        # Determine start key: find first unsigned, or default to first
        start_key = self.segment_keys[0] if self.segment_keys else None
        if start_key:
            for key in self.segment_keys:
                if not self.signoff_vars[key].get():
                    start_key = key
                    break

        if start_key:
            self._navigate(start_key)

    def refresh_fonts(self, size):
        if hasattr(self, 'editor') and self.editor.winfo_exists():
            self.editor.set_font_size(size)
        if hasattr(self, 'renderer') and self.renderer.winfo_exists():
            self.renderer.set_font_size(size)

    def _on_signoff_var_change(self, key, var):
        self.signoffs_data[key] = var.get()
        if self.on_change_callback:
            self.on_change_callback()

        # When external signoff changes (e.g. from sidebar), update footer buttons immediately
        if key == self.active_key:
            self._update_footer_state()

    def _build_ui(self):
        # Sidebar
        self.sidebar_frame = Frame(self, bg=c.DARK_BG, width=220)
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar_frame.pack_propagate(False)

        for key in self.segment_keys:
            name = self.friendly_names_map.get(key, key)
            item = SidebarItem(
                self.sidebar_frame, name, False,
                status_var=self.signoff_vars[key],
                command=lambda k=key: self._navigate(k)
            )
            item.pack(fill="x")
            ToolTip(item, f"Navigate to {name}", delay=500)
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

        # Footer
        self.footer = Frame(self.main_view_container, bg=c.DARK_BG)
        self.footer.pack(side="bottom", fill="x", pady=(10, 0))

        self.footer_buttons_frame = Frame(self.footer, bg=c.DARK_BG)
        self.footer_buttons_frame.pack(fill='x', expand=True)

        # Footer Buttons
        self.signoff_btn = RoundedButton(self.footer_buttons_frame, text="Sign Off & Next", command=self._sign_off, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, width=160, cursor="hand2")
        ToolTip(self.signoff_btn, "Lock this section and move to the next incomplete part", delay=500)

        self.revert_btn = RoundedButton(self.footer_buttons_frame, text="Unlock to Edit", command=self._revert_draft, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2")
        ToolTip(self.revert_btn, "Release the sign-off to make further changes to this section", delay=500)

        self.sync_btn = RoundedButton(self.footer_buttons_frame, text="Sync Unsigned", command=self._open_sync_dialog, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_SMALL_BUTTON, width=130, cursor="hand2")
        ToolTip(self.sync_btn, "Propagates your changes to other unlocked sections to maintain consistency.\n(Only affects sections that are not signed off)", delay=500)

        # Merge Button (Initially hidden, appears when all sections are signed)
        self.merge_btn = RoundedButton(self.footer_buttons_frame, text="Merge Segments", command=self._handle_final_merge, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, width=160, cursor="hand2")
        ToolTip(self.merge_btn, "Finalize all segments and merge them into a single document", delay=500)

        self.questions_panel = Frame(self.main_view_container, bg=c.STATUS_BG, padx=10, pady=10)

        self.display_container = Frame(self.main_view_container, bg=c.DARK_BG)
        self.display_container.pack(side="top", fill="both", expand=True)
        self.display_container.grid_rowconfigure(0, weight=1)
        self.display_container.grid_columnconfigure(0, weight=1)

        self.editor = ScrollableText(
            self.display_container, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.master.wizard_controller.font_size),
            on_zoom=self.master.wizard_controller.adjust_font_size
        )
        self.editor.text_widget.bind("<KeyRelease>", self._on_text_change)

        self.renderer = MarkdownRenderer(
            self.display_container,
            base_font_size=self.master.wizard_controller.font_size,
            on_zoom=self.master.wizard_controller.adjust_font_size
        )
        self.renderer.text_widget.bind("<Double-Button-1>", self._on_renderer_double_click)

    def _on_renderer_double_click(self, event):
        if self.revert_btn.winfo_ismapped(): return
        try: click_index = self.renderer.text_widget.index(f"@{event.x},{event.y}")
        except Exception: click_index = "1.0"
        self._toggle_view(force_render=False)
        self.editor.update_idletasks()
        self.editor.text_widget.mark_set("insert", click_index)
        self.editor.text_widget.see(click_index)
        self.editor.text_widget.focus_set()

    def _navigate(self, key):
        if self.is_loading_nav: return
        self.is_loading_nav = True

        try:
            if self.active_key and self.active_key in self.segments_data:
                self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()

            self.active_key = None
            self.current_question_index = 0
            for k, item in self.sidebar_items.items(): item.set_selected(k == key)
            for w in self.header_controls.winfo_children(): w.destroy()

            self.questions_panel.pack_forget()
            self.editor.grid_forget()
            self.renderer.grid_forget()
            self.editor.text_widget.config(state="normal")
            self.editor.delete("1.0", "end")

            if key in self.sidebar_items:
                self.sidebar_items[key].set_updated(False)

            self._show_segment(key)
            self.active_key = key
        finally:
            self.is_loading_nav = False

    def _show_segment(self, key):
        name = self.friendly_names_map.get(key, key)
        self.title_label.config(text=name)

        # Capture original content for sync logic
        self.current_segment_original_text = self.segments_data.get(key, "")
        self.editor.insert("1.0", self.current_segment_original_text)

        self.q_btn = RoundedButton(self.header_controls, text="Questions", command=self._toggle_questions, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, cursor="hand2")
        self.q_btn.pack(side="left")
        ToolTip(self.q_btn, "Toggle guiding questions to help refine this section.", delay=500)

        # Rewrite button: Bigger font, simple "Rewrite" text, blue color
        self.rewrite_btn = RoundedButton(
            self.header_controls,
            text="Rewrite",
            command=self._open_rewrite_dialog,
            bg=c.BTN_BLUE,
            fg=c.BTN_BLUE_TEXT,
            font=c.FONT_BOLD,
            height=24,
            cursor="hand2"
        )
        self.rewrite_btn.pack(side="left", padx=(10, 0))
        ToolTip(self.rewrite_btn, "Give an instruction to modify all unsigned segments at once.", delay=500)

        self.is_raw_mode = tk.BooleanVar(value=False)
        self.view_btn = RoundedButton(self.header_controls, text="Edit", command=self._toggle_view, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="left", padx=(10, 0))

        self.view_btn_tooltip = ToolTip(self.view_btn, "", delay=500)

        self._update_questions_panel(key)
        self._toggle_view(force_render=True)
        self._update_footer_state(key)
        self._apply_questions_visibility()

    def _toggle_view(self, force_render=False):
        if force_render: self.is_raw_mode.set(False)
        else: self.is_raw_mode.set(not self.is_raw_mode.get())

        if self.is_raw_mode.get():
            self.renderer.grid_forget()
            self.editor.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Render", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            if hasattr(self, 'view_btn_tooltip'):
                self.view_btn_tooltip.text = "Switch to stylized Markdown preview"
                if self.view_btn_tooltip.tooltip_window:
                    self.view_btn_tooltip.hide_tooltip()
                    self.view_btn_tooltip.show_tooltip()
        else:
            self.editor.text_widget.tag_remove("sel", "1.0", "end")
            self.renderer.set_markdown(self.editor.get("1.0", "end-1c"))
            self.editor.grid_forget()
            self.renderer.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Edit", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            if hasattr(self, 'view_btn_tooltip'):
                self.view_btn_tooltip.text = "Switch to raw text editor"
                if self.view_btn_tooltip.tooltip_window:
                    self.view_btn_tooltip.hide_tooltip()
                    self.view_btn_tooltip.show_tooltip()

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

        btn_row = Frame(self.questions_panel, bg=c.STATUS_BG)
        btn_row.pack(anchor="w")

        copy_btn = RoundedButton(btn_row, text="Copy Context & Question", command=lambda: self._copy_q_context(q_list[self.current_question_index], copy_btn), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=26, cursor="hand2")
        copy_btn.pack(side="left")
        ToolTip(copy_btn, "Copy a prompt containing the current segment text and this question", delay=500)

    def _refresh_q_text(self, lbl, q_list, pb, nb):
        idx = self.current_question_index
        lbl.config(text=q_list[idx])
        pb.set_state("normal" if idx > 0 else "disabled")
        nb.set_state("normal" if idx < len(q_list)-1 else "disabled")

    def _toggle_questions(self):
        self.questions_visible = not self.questions_visible
        self._apply_questions_visibility()

    def _apply_questions_visibility(self):
        # Ensure q_btn exists
        if not hasattr(self, 'q_btn') or not self.q_btn.winfo_exists():
            self.questions_panel.pack_forget()
            return

        if self.questions_visible:
            if not self.questions_panel.winfo_ismapped():
                self.questions_panel.pack(side="top", fill="x", before=self.display_container, pady=(0, 10))
            self.q_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.questions_panel.pack_forget()
            self.q_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _copy_q_context(self, question, btn):
        context = ""
        for k in self.segment_keys:
            if k == self.active_key: continue
            txt = self.segments_data.get(k, "").strip()
            if txt: context += f"--- Context: {self.friendly_names_map.get(k, k)} ---\n{txt}\n\n"

        current_txt = self.editor.get("1.0", "end-1c").strip()
        current_name = self.friendly_names_map.get(self.active_key, self.active_key)

        prompt = f"### Context\n{context}\n### Focus: {current_name}\n{current_txt}\n\n### Question\n{question}\n\n" \
                 f"Instruction: Focus ONLY on the segment '{current_name}'. " \
                 f"Please answer the question or provide critical feedback regarding this segment. Do NOT rewrite the text."

        try:
            self.clipboard_clear()
            self.clipboard_append(prompt)
            btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: btn.config(text="Copy Context & Question", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))
        except tk.TclError: messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.", parent=self)

    def _on_text_change(self, event=None):
        if self.is_loading_nav or self.active_key is None: return
        current_text = self.editor.get("1.0", "end-1c").strip()
        self.segments_data[self.active_key] = current_text
        if self.on_change_callback: self.on_change_callback()
        self._update_sync_button_visibility(current_text)

    def _update_footer_state(self, key=None):
        target_key = key or self.active_key
        if not target_key: return

        is_signed = self.signoff_vars[target_key].get()
        all_signed = all(self.signoff_vars[k].get() for k in self.segment_keys)

        # Enforcement: If current segment is signed, force Render and hide Edit toggle
        if is_signed:
            self._toggle_view(force_render=True)
            if hasattr(self, 'view_btn'): self.view_btn.pack_forget()
        else:
            if hasattr(self, 'view_btn'): self.view_btn.pack(side="left", padx=(10, 0))

        if all_signed:
            # If all are signed, show Merge Button in the main slot
            self.signoff_btn.pack_forget()
            self.sync_btn.pack_forget()
            self.merge_btn.pack(side="right")

            # Allow reversion even if all are signed
            self.revert_btn.pack(side="left", padx=(0, 10))
            self.editor.text_widget.config(state="disabled", bg=c.DARK_BG)
            return

        # Not all signed: Hide Merge button
        self.merge_btn.pack_forget()

        if is_signed:
            self.signoff_btn.pack_forget()
            self.sync_btn.pack_forget()
            self.revert_btn.pack(side="left", padx=(0, 10))
            self.editor.text_widget.config(state="disabled", bg=c.DARK_BG)
        else:
            self.revert_btn.pack_forget()
            self.signoff_btn.pack(side="right")
            self._update_sync_button_visibility(self.segments_data.get(target_key, "").strip())
            self.editor.text_widget.config(state="normal", bg=c.TEXT_INPUT_BG)

    def _update_sync_button_visibility(self, current_text):
        target_key = self.active_key
        if not target_key: return

        is_signed = self.signoff_vars[target_key].get()
        if is_signed:
            self.sync_btn.pack_forget()
            return

        other_unsigned = any(not self.signoff_vars[k].get() for k in self.segment_keys if k != target_key)
        has_changes = current_text != self.current_segment_original_text

        if other_unsigned and has_changes and current_text:
            if not self.sync_btn.winfo_ismapped():
                self.sync_btn.pack(side="left")
        else:
            self.sync_btn.pack_forget()

    def _sign_off(self):
        # Save current state before proceeding
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        self.signoff_vars[self.active_key].set(True)
        # Footer update handles hiding SignOff and showing Merge/Revert logic
        self._update_footer_state()

        # Check for next unsigned segment to navigate to
        next_key = None
        current_idx = self.segment_keys.index(self.active_key)

        # 1. Search forward
        for i in range(current_idx + 1, len(self.segment_keys)):
            if not self.signoff_vars[self.segment_keys[i]].get():
                next_key = self.segment_keys[i]
                break

        # 2. Search from beginning if not found
        if not next_key:
            for i in range(0, current_idx):
                if not self.signoff_vars[self.segment_keys[i]].get():
                    next_key = self.segment_keys[i]
                    break

        if next_key:
            self._navigate(next_key)

    def _handle_final_merge(self):
        if not self.on_merge_callback:
            return

        # Confirm with user first
        if not messagebox.askyesno("Confirm Merge", "Merge all segments into a single document?\n\nThis cannot be undone.", parent=self):
            return

        # Assemble full text
        full_text = SegmentManager.assemble_document(self.segments_data, self.segment_keys, self.friendly_names_map)

        # Pass full text to parent handler to switch views
        self.on_merge_callback(full_text)

    def _revert_draft(self):
        self.signoff_vars[self.active_key].set(False)
        self._update_footer_state()

    def _open_sync_dialog(self):
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        targets, references = [], []
        for k in self.segment_keys:
            if k == self.active_key: continue
            if self.signoff_vars[k].get(): references.append(k)
            else: targets.append(k)
        if not targets: messagebox.showinfo("Nothing to Sync", "All other segments are signed off."); return

        target_context_str = "\n".join([f"--- Current Draft: {self.friendly_names_map.get(k, k)} ---\n{self.segments_data.get(k, '')}\n" for k in targets])
        ref_context_str = ""
        if references:
            ref_context_str = "\n### Locked Sections (Reference Only)\n" + "\n".join([f"--- Locked Section: {self.friendly_names_map.get(k, k)} ---\n{self.segments_data.get(k, '')}\n" for k in references])

        current_name = self.friendly_names_map.get(self.active_key, self.active_key)
        prompt = f"You are a Consistency Engine. The user has modified section **{current_name}**.\nUpdate *unsigned* drafts to match these changes, respecting *locked* sections.\n\n### New Source of Truth: {current_name}\n```\n{self.segments_data[self.active_key]}\n```\n{ref_context_str}\n### Drafts to Update\n{target_context_str}\n\n### Instructions\n1. {SegmentManager.build_prompt_instructions(targets, self.friendly_names_map)}"
        SyncUnsignedDialog(self, prompt, self._apply_sync_results)

    def _open_rewrite_dialog(self):
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        context_data = {
            'keys': self.segment_keys, 'names': self.friendly_names_map, 'data': self.segments_data,
            'signoffs': {k: self.signoff_vars[k].get() for k in self.segment_keys}
        }
        RewriteUnsignedDialog(self, context_data, self._apply_sync_results)

    def _apply_sync_results(self, llm_output):
        parsed = SegmentManager.parse_segments(llm_output)
        if not parsed: messagebox.showerror("Error", "Could not parse segments."); return
        mapped = SegmentManager.map_parsed_segments_to_keys(parsed, self.friendly_names_map)
        updated_count = 0
        for key, content in mapped.items():
            if key in self.segments_data and not self.signoff_vars[key].get():
                self.segments_data[key] = content

                # If the updated key is the one we are looking at, refresh the UI immediately
                if key == self.active_key:
                    self.editor.text_widget.config(state="normal")
                    self.editor.delete("1.0", "end")
                    self.editor.insert("1.0", content)

                    # Update the Markdown renderer if we are currently in Rendered mode
                    if not self.is_raw_mode.get():
                        self.renderer.set_markdown(content)

                elif key in self.sidebar_items:
                    self.sidebar_items[key].set_updated(True)

                updated_count += 1

        if updated_count > 0 and self.on_change_callback:
            self.on_change_callback()

        if updated_count == 0:
            messagebox.showinfo("Info", "No matching segments found.")

    def get_assembled_content(self):
        full_text = SegmentManager.assemble_document(self.segments_data, self.segment_keys, self.friendly_names_map)
        return full_text, self.segments_data, self.signoffs_data