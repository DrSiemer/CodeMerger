import tkinter as tk
from tkinter import Frame, Label, messagebox
from .... import constants as c
from ....core import prompts as p
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...widgets.markdown_renderer import MarkdownRenderer
from ...tooltip import ToolTip
from ..segment_manager import SegmentManager
from ...assets import assets

# Extracted Component Imports
from .reviewer_sidebar import ReviewerSidebar
from .reviewer_questions import ReviewerQuestions
from .reviewer_footer import ReviewerFooter
from .rewrite_dialog import RewriteUnsignedDialog
from .sync_dialog import SyncUnsignedDialog

class SegmentedReviewer(Frame):
    """
    Orchestrator widget that presents content in segments with a sidebar for navigation,
    sign-off capability, and a final merge trigger.
    """
    def __init__(self, parent, segment_keys, friendly_names_map, segments_data, signoffs_data, questions_map=None, on_change_callback=None, on_merge_callback=None):
        super().__init__(parent, bg=c.DARK_BG)
        self.parent = parent
        self.segment_keys = segment_keys
        self.friendly_names_map = friendly_names_map
        self.segments_data = segments_data
        self.signoffs_data = signoffs_data
        self.questions_map = questions_map or {}
        self.on_change_callback = on_change_callback
        self.on_merge_callback = on_merge_callback

        self.active_key = None
        self.is_loading_nav = False
        self.current_segment_original_text = ""
        self.questions_visible = False
        self.info_mgr = None

        self.signoff_vars = {}
        for key in self.segment_keys:
            val = self.signoffs_data.get(key, False)
            bv = tk.BooleanVar(value=val)
            bv.trace_add("write", lambda *a, k=key, v=bv: self._on_signoff_var_change(k, v))
            self.signoff_vars[key] = bv

        self._build_ui()

        start_key = self.segment_keys[0] if self.segment_keys else None
        if start_key:
            for key in self.segment_keys:
                if not self.signoff_vars[key].get():
                    start_key = key
                    break
            self._navigate(start_key)

    def _build_ui(self):
        # 1. Sidebar
        self.sidebar = ReviewerSidebar(
            self, self.segment_keys, self.friendly_names_map, self.signoff_vars,
            on_navigate_callback=self._navigate
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))

        # 2. Content Container
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

        # 3. Footer
        self.footer = ReviewerFooter(
            self.main_view_container,
            on_sign_off=self._sign_off,
            on_revert=self._revert_draft,
            on_sync=self._open_sync_dialog,
            on_merge=self._handle_final_merge
        )
        self.footer.pack(side="bottom", fill="x", pady=(10, 0))

        # 4. Questions Panel
        self.questions_panel = ReviewerQuestions(
            self.main_view_container, self.questions_map,
            get_context_callback=self._get_question_context
        )

        # 5. Display (Editor/Renderer)
        self.display_container = Frame(self.main_view_container, bg=c.DARK_BG)
        self.display_container.pack(side="top", fill="both", expand=True)
        self.display_container.grid_rowconfigure(0, weight=1)
        self.display_container.grid_columnconfigure(0, weight=1)

        self.editor = ScrollableText(
            self.display_container, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.parent.starter_controller.font_size),
            on_zoom=self.parent.starter_controller.adjust_font_size
        )
        self.editor.text_widget.bind("<KeyRelease>", self._on_text_change)

        self.renderer = MarkdownRenderer(
            self.display_container,
            base_font_size=self.parent.starter_controller.font_size,
            on_zoom=self.parent.starter_controller.adjust_font_size
        )
        self.renderer.text_widget.bind("<Double-Button-1>", self._on_renderer_double_click)

    def _navigate(self, key):
        if self.is_loading_nav: return
        self.is_loading_nav = True

        try:
            if self.active_key and self.active_key in self.segments_data:
                self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()

            self.active_key = None
            self.sidebar.set_active(key)
            self.sidebar.mark_updated(key, False)

            for w in self.header_controls.winfo_children(): w.destroy()

            self.questions_panel.pack_forget()
            self.editor.grid_forget()
            self.renderer.grid_forget()
            self.editor.text_widget.config(state="normal")
            self.editor.delete("1.0", "end")

            self._show_segment(key)
            self.active_key = key
        finally:
            self.is_loading_nav = False

    def _show_segment(self, key):
        name = self.friendly_names_map.get(key, key)
        self.title_label.config(text=name)
        self.current_segment_original_text = self.segments_data.get(key, "")
        self.editor.insert("1.0", self.current_segment_original_text)

        # Header Buttons
        self.q_btn = RoundedButton(self.header_controls, text="Questions", command=self._toggle_questions, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, cursor="hand2")
        self.q_btn.pack(side="left")
        ToolTip(self.q_btn, "Toggle guiding questions to help refine this section.", delay=500)

        self.rewrite_btn = RoundedButton(self.header_controls, text="Rewrite", command=self._open_rewrite_dialog, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BOLD, height=24, cursor="hand2")
        self.rewrite_btn.pack(side="left", padx=(10, 0))
        ToolTip(self.rewrite_btn, "Give an instruction to modify all unsigned segments at once.", delay=500)

        self.is_raw_mode = tk.BooleanVar(value=False)
        self.view_btn = RoundedButton(self.header_controls, text="Edit", command=self._toggle_view, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="left", padx=(10, 0))
        self.view_btn_tooltip = ToolTip(self.view_btn, "", delay=500)

        self.questions_panel.update_for_segment(key)
        self._toggle_view(force_render=True)
        self._update_footer_state(key)
        self._apply_questions_visibility()
        self._register_transient_info()

    def _on_signoff_var_change(self, key, var):
        self.signoffs_data[key] = var.get()
        if self.on_change_callback: self.on_change_callback()
        if key == self.active_key:
            self._update_footer_state()
        else:
            self._update_footer_buttons_only()

    def _update_footer_state(self, key=None):
        target_key = key or self.active_key
        if not target_key: return

        is_signed = self.signoff_vars[target_key].get()
        all_signed = all(self.signoff_vars[k].get() for k in self.segment_keys)

        if is_signed:
            self._toggle_view(force_render=True)
            self.view_btn.pack_forget()
            self.editor.text_widget.config(state="disabled", bg=c.DARK_BG)
        else:
            self.view_btn.pack(side="left", padx=(10, 0))
            self.editor.text_widget.config(state="normal", bg=c.TEXT_INPUT_BG)

        self._update_footer_buttons_only(target_key, is_signed, all_signed)

    def _update_footer_buttons_only(self, target_key=None, is_signed=None, all_signed=None):
        target_key = target_key or self.active_key
        if not target_key: return

        if is_signed is None:
            is_signed = self.signoff_vars[target_key].get()
        if all_signed is None:
            all_signed = all(self.signoff_vars[k].get() for k in self.segment_keys)

        current_text = self.segments_data.get(target_key, "").strip()
        has_changes = current_text != self.current_segment_original_text
        other_unsigned = any(not self.signoff_vars[k].get() for k in self.segment_keys if k != target_key)

        self.footer.update_state(
            is_signed=is_signed,
            all_signed=all_signed,
            has_changes=has_changes,
            has_other_unsigned=other_unsigned,
            current_text_exists=bool(current_text)
        )

    def _toggle_questions(self):
        self.questions_visible = not self.questions_visible
        self._apply_questions_visibility()

    def _apply_questions_visibility(self):
        if not hasattr(self, 'q_btn') or not self.q_btn.winfo_exists(): return
        if self.questions_visible:
            if not self.questions_panel.winfo_ismapped():
                self.questions_panel.pack(side="top", fill="x", before=self.display_container, pady=(0, 10))
            self.q_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.questions_panel.pack_forget()
            self.q_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _on_text_change(self, event=None):
        if self.is_loading_nav or self.active_key is None: return
        current_text = self.editor.get("1.0", "end-1c").strip()
        self.segments_data[self.active_key] = current_text
        if self.on_change_callback: self.on_change_callback()
        self._update_footer_state()

    def _get_question_context(self):
        """Callback for the questions panel to gather data for prompt creation."""
        context = ""
        for k in self.segment_keys:
            if k == self.active_key: continue
            txt = self.segments_data.get(k, "").strip()
            if txt: context += f"--- Context: {self.friendly_names_map.get(k, k)} ---\n{txt}\n\n"

        current_text = self.editor.get("1.0", "end-1c").strip()
        current_name = self.friendly_names_map.get(self.active_key, self.active_key)
        return context, current_name, current_text

    def _toggle_view(self, force_render=False):
        if force_render: self.is_raw_mode.set(False)
        else: self.is_raw_mode.set(not self.is_raw_mode.get())

        if self.is_raw_mode.get():
            self.renderer.grid_forget()
            self.editor.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Render", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.view_btn_tooltip.text = "Switch to stylized Markdown preview"
        else:
            self.editor.text_widget.tag_remove("sel", "1.0", "end")
            self.renderer.set_markdown(self.editor.get("1.0", "end-1c"))
            self.editor.grid_forget()
            self.renderer.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Edit", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            self.view_btn_tooltip.text = "Switch to raw text editor"

        if self.view_btn_tooltip.tooltip_window:
            self.view_btn_tooltip.hide_tooltip()
            self.view_btn_tooltip.show_tooltip()

    def _on_renderer_double_click(self, event):
        if self.signoff_vars[self.active_key].get(): return
        try: click_index = self.renderer.text_widget.index(f"@{event.x},{event.y}")
        except Exception: click_index = "1.0"
        self._toggle_view(force_render=False)
        self.editor.update_idletasks()
        self.editor.text_widget.mark_set("insert", click_index)
        self.editor.text_widget.see(click_index)
        self.editor.text_widget.focus_set()

    def _sign_off(self):
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        self.signoff_vars[self.active_key].set(True)
        self._update_footer_state()

        next_key = None
        current_idx = self.segment_keys.index(self.active_key)
        for i in range(current_idx + 1, len(self.segment_keys)):
            if not self.signoff_vars[self.segment_keys[i]].get():
                next_key = self.segment_keys[i]; break
        if not next_key:
            for i in range(0, current_idx):
                if not self.signoff_vars[self.segment_keys[i]].get():
                    next_key = self.segment_keys[i]; break
        if next_key: self._navigate(next_key)

    def _revert_draft(self):
        self.signoff_vars[self.active_key].set(False)
        self._update_footer_state()

    def _open_sync_dialog(self):
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        targets, references = [],[]
        for k in self.segment_keys:
            if k == self.active_key: continue
            if self.signoff_vars[k].get(): references.append(k)
            else: targets.append(k)
        if not targets: messagebox.showinfo("Nothing to Sync", "All other segments are signed off."); return

        target_context_str = "\n".join([f"--- Current Draft: {self.friendly_names_map.get(k, k)} ---\n{self.segments_data.get(k, '')}\n" for k in targets])
        ref_context_str = ""
        if references:
            ref_context_str = "\n### Locked Sections (Reference Only)\n" + "\n".join([f"--- Locked Section: {self.friendly_names_map.get(k, k)} ---\n{self.segments_data.get(k, '')}\n" for k in references])

        prompt = p.STARTER_SYNC_PROMPT_TEMPLATE.format(
            current_name=self.friendly_names_map.get(self.active_key, self.active_key),
            content=self.segments_data[self.active_key],
            ref_context=ref_context_str,
            target_context=target_context_str,
            target_instructions=SegmentManager.build_prompt_instructions(targets, self.friendly_names_map)
        )
        SyncUnsignedDialog(self, prompt, self._apply_sync_results)

    def _open_rewrite_dialog(self):
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        context_data = {
            'keys': self.segment_keys, 'names': self.friendly_names_map, 'data': self.segments_data,
            'signoffs': {k: self.signoff_vars[k].get() for k in self.segment_keys}
        }
        app_state = self.parent.starter_controller.app.app_state
        RewriteUnsignedDialog(self, app_state, context_data, self._apply_sync_results)

    def _apply_sync_results(self, llm_output):
        parsed = SegmentManager.parse_segments(llm_output)
        if not parsed: messagebox.showerror("Error", "Could not parse segments."); return
        mapped = SegmentManager.map_parsed_segments_to_keys(parsed, self.friendly_names_map)
        updated_count = 0
        for key, content in mapped.items():
            if key in self.segments_data and not self.signoff_vars[key].get():
                self.segments_data[key] = content
                if key == self.active_key:
                    self.editor.text_widget.config(state="normal")
                    self.editor.delete("1.0", "end")
                    self.editor.insert("1.0", content)
                    if not self.is_raw_mode.get(): self.renderer.set_markdown(content)
                else:
                    self.sidebar.mark_updated(key, True)
                updated_count += 1
        if updated_count > 0 and self.on_change_callback: self.on_change_callback()

    def _handle_final_merge(self):
        if not self.on_merge_callback: return
        if not messagebox.askyesno("Confirm Merge", "Merge all segments into a single document?\n\nThis cannot be undone.", parent=self):
            return
        full_text = SegmentManager.assemble_document(self.segments_data, self.segment_keys, self.friendly_names_map)
        self.on_merge_callback(full_text)

    def register_info(self, info_mgr):
        self.info_mgr = info_mgr
        self.sidebar.register_info(info_mgr)
        self.footer.register_info(info_mgr)
        self._register_transient_info()

    def _register_transient_info(self):
        if not self.info_mgr: return
        if hasattr(self, 'q_btn') and self.q_btn.winfo_exists(): self.info_mgr.register(self.q_btn, "starter_seg_questions")
        if hasattr(self, 'rewrite_btn') and self.rewrite_btn.winfo_exists(): self.info_mgr.register(self.rewrite_btn, "starter_seg_rewrite")
        if hasattr(self, 'view_btn') and self.view_btn.winfo_exists(): self.info_mgr.register(self.view_btn, "starter_view_toggle")
        self.info_mgr.register(self.footer.revert_btn, "starter_seg_unlock")
        self.info_mgr.register(self.footer.merge_btn, "starter_seg_merge")

    def refresh_fonts(self, size):
        self.editor.set_font_size(size)
        self.renderer.set_font_size(size)

    def get_assembled_content(self):
        full_text = SegmentManager.assemble_document(self.segments_data, self.segment_keys, self.friendly_names_map)
        return full_text, self.segments_data, self.signoffs_data