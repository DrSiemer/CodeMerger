import tkinter as tk
from tkinter import messagebox
import pyperclip
from .... import constants as c
from ....core import prompts as p
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...widgets.markdown_renderer import MarkdownRenderer
from ...tooltip import ToolTip

class FullTextReviewer(tk.Frame):
    """
    A reusable component for reviewing and editing large blocks of Markdown.
    Includes a guiding questions panel, edit/render toggle, and prompt generation logic.
    """
    def __init__(self, parent, title, content, questions, on_text_change_callback, on_rewrite_callback, get_prompt_context_callback, starter_controller):
        super().__init__(parent, bg=c.DARK_BG)
        self.starter_controller = starter_controller
        self.questions = questions or["Review the content for accuracy and clarity."]
        self.on_text_change = on_text_change_callback
        self.on_rewrite = on_rewrite_callback
        self.get_prompt_context = get_prompt_context_callback

        self.current_question_index = 0
        self.is_raw_mode = False
        self.questions_visible = False

        self._build_ui(title, content)

    def _build_ui(self, title, content):
        self.grid_rowconfigure(1, weight=0) # Questions Panel
        self.grid_rowconfigure(2, weight=1) # Main View
        self.grid_columnconfigure(0, weight=1)

        # --- Header ---
        header_frame = tk.Frame(self, bg=c.DARK_BG)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(header_frame, text=title, font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        controls = tk.Frame(header_frame, bg=c.DARK_BG)
        controls.pack(side="right")

        self.q_btn = RoundedButton(controls, text="Questions", command=self._toggle_questions, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, cursor="hand2")
        self.q_btn.pack(side="left", padx=(0, 10))
        ToolTip(self.q_btn, "Toggle guiding questions to help refine this section.", delay=500)

        self.rewrite_btn = RoundedButton(controls, text="Rewrite", command=self.on_rewrite, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BOLD, height=24, cursor="hand2")
        self.rewrite_btn.pack(side="left", padx=(0, 10))
        ToolTip(self.rewrite_btn, "Instructional rewrite of the document with change notes.", delay=500)

        self.view_btn = RoundedButton(controls, text="Edit", command=self._toggle_view_mode, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="left")
        self.view_btn_tooltip = ToolTip(self.view_btn, "Switch to raw text editor", delay=500)

        # --- Questions Panel ---
        self.questions_container = tk.Frame(self, bg=c.DARK_BG)

        # --- Editor/Renderer ---
        self.view_frame = tk.Frame(self, bg=c.DARK_BG)
        self.view_frame.grid(row=2, column=0, sticky="nsew")
        self.view_frame.grid_rowconfigure(0, weight=1)
        self.view_frame.grid_columnconfigure(0, weight=1)

        self.editor = ScrollableText(
            self.view_frame, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size),
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.editor.insert("1.0", content)
        self.editor.text_widget.bind("<KeyRelease>", self._on_key_release)

        self.renderer = MarkdownRenderer(
            self.view_frame,
            base_font_size=self.starter_controller.font_size,
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.renderer.text_widget.bind("<Double-Button-1>", self._on_renderer_double_click)

        self._apply_view_mode()

    def register_info(self, info_mgr, editor_key="starter_view_toggle"):
        info_mgr.register(self.editor, editor_key)
        info_mgr.register(self.q_btn, "starter_seg_questions")
        info_mgr.register(self.rewrite_btn, "starter_seg_rewrite")
        info_mgr.register(self.view_btn, "starter_view_toggle")

    def refresh_fonts(self, size):
        self.editor.set_font_size(size)
        self.renderer.set_font_size(size)

    def set_content(self, text):
        self.editor.text_widget.config(state="normal")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)
        if not self.is_raw_mode:
            self.renderer.set_markdown(text)

    def get_content(self):
        return self.editor.get("1.0", "end-1c").strip()

    def _on_key_release(self, event=None):
        self.on_text_change(self.get_content())

    def _on_renderer_double_click(self, event):
        try:
            click_index = self.renderer.text_widget.index(f"@{event.x},{event.y}")
        except Exception:
            click_index = "1.0"
        self._toggle_view_mode()
        self.editor.update_idletasks()
        self.editor.text_widget.mark_set("insert", click_index)
        self.editor.text_widget.see(click_index)
        self.editor.text_widget.focus_set()

    def _toggle_view_mode(self):
        self.is_raw_mode = not self.is_raw_mode
        self._apply_view_mode()

    def _apply_view_mode(self):
        if self.is_raw_mode:
            self.renderer.grid_forget()
            self.editor.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Render", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.view_btn_tooltip.text = "Switch to stylized Markdown preview"
        else:
            self.renderer.set_markdown(self.editor.get("1.0", "end-1c"))
            self.editor.grid_forget()
            self.renderer.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Edit", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            self.view_btn_tooltip.text = "Switch to raw text editor"

        if self.view_btn_tooltip.tooltip_window:
             self.view_btn_tooltip.hide_tooltip()
             self.view_btn_tooltip.show_tooltip()

    def _toggle_questions(self):
        self.questions_visible = not self.questions_visible
        if self.questions_visible:
            self.questions_container.grid(row=1, column=0, sticky="ew", pady=(0, 10))
            self._create_question_prompter()
            self.q_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.questions_container.grid_remove()
            for widget in self.questions_container.winfo_children():
                widget.destroy()
            self.q_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _create_question_prompter(self):
        if self.questions_container.winfo_children():
            return

        panel = tk.Frame(self.questions_container, bg=c.STATUS_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        panel.pack(fill='x', expand=True)

        content_f = tk.Frame(panel, bg=c.STATUS_BG, padx=10, pady=10)
        content_f.pack(fill='x', expand=True)

        self.question_label = tk.Label(content_f, text="", wraplength=600, justify="left", anchor="w", font=c.FONT_NORMAL, bg=c.STATUS_BG, fg=c.TEXT_COLOR)
        self.question_label.pack(side='left', fill='x', expand=True)

        actions = tk.Frame(content_f, bg=c.STATUS_BG)
        actions.pack(side='left', padx=(10,0))

        nav = tk.Frame(actions, bg=c.STATUS_BG)
        nav.pack(anchor='e')
        self.prev_q = RoundedButton(nav, text="<", command=lambda: self._move_q(-1), width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.prev_q.pack(side="left")
        self.next_q = RoundedButton(nav, text=">", command=lambda: self._move_q(1), width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.next_q.pack(side="left", padx=2)

        copy_btn = RoundedButton(actions, text="Copy Context & Question", command=lambda: self._copy_q_prompt(copy_btn), width=160, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        copy_btn.pack(anchor='e', pady=(5, 0))
        ToolTip(copy_btn, "Copy the full text and this question, asking for feedback", delay=500)

        self._update_q_display()

    def _move_q(self, delta):
        self.current_question_index = max(0, min(self.current_question_index + delta, len(self.questions) - 1))
        self._update_q_display()

    def _update_q_display(self):
        if not hasattr(self, 'question_label'): return
        self.question_label.config(text=self.questions[self.current_question_index])
        self.prev_q.set_state("normal" if self.current_question_index > 0 else "disabled")
        self.next_q.set_state("normal" if self.current_question_index < len(self.questions) - 1 else "disabled")

    def _copy_q_prompt(self, btn):
        try:
            current_q = self.questions[self.current_question_index]
            context_label, context_content, focus_name, focus_content = self.get_prompt_context()

            prompt = p.STARTER_QUESTION_PROMPT_TEMPLATE.format(
                context_label=context_label,
                context_content=context_content,
                focus_name=focus_name,
                focus_content=focus_content,
                question=current_q,
                instruction_suffix="Please answer the question or provide critical feedback. Do NOT rewrite the text."
            )

            pyperclip.copy(prompt)
            btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: btn.config(text="Copy Context & Question", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if btn.winfo_exists() else None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy prompt: {e}", parent=self)