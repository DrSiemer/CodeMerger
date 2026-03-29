import tkinter as tk
from tkinter import Frame, Label, messagebox
from .... import constants as c
from ....core import prompts as p
from ...widgets.rounded_button import RoundedButton
from ...tooltip import ToolTip

class ReviewerQuestions(Frame):
    """
    Encapsulates the guiding questions panel and prompt generation logic.
    """
    def __init__(self, parent, questions_map, get_context_callback, **kwargs):
        super().__init__(parent, bg=c.STATUS_BG, padx=10, pady=10, **kwargs)
        self.questions_map = questions_map
        self.get_context_callback = get_context_callback

        self.current_key = None
        self.current_q_list = []
        self.current_index = 0

    def update_for_segment(self, key):
        """Rebuilds the panel content for the specified segment."""
        self.current_key = key
        for w in self.winfo_children():
            w.destroy()

        self.current_q_list = self.questions_map.get(key, {}).get("questions", [])
        self.current_index = 0

        if not self.current_q_list:
            Label(self, text="No specific questions for this segment.", bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack()
            return

        header = Frame(self, bg=c.STATUS_BG)
        header.pack(fill="x")
        Label(header, text="Review Question:", font=c.FONT_BOLD, bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack(side="left")

        nav = Frame(header, bg=c.STATUS_BG)
        nav.pack(side="right")

        self.prev_btn = RoundedButton(nav, text="<", command=lambda: self._move(-1), width=24, height=24, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2")
        self.prev_btn.pack(side="left")

        self.next_btn = RoundedButton(nav, text=">", command=lambda: self._move(1), width=24, height=24, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2")
        self.next_btn.pack(side="left", padx=5)

        self.lbl_text = Label(self, text="", justify="left", anchor="w", bg=c.STATUS_BG, fg=c.TEXT_COLOR, wraplength=550, font=c.FONT_NORMAL)
        self.lbl_text.pack(fill="x", pady=(5, 10))

        btn_row = Frame(self, bg=c.STATUS_BG)
        btn_row.pack(anchor="w")

        self.copy_btn = RoundedButton(btn_row, text="Copy Context & Question", command=self._copy_q_context, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=26, cursor="hand2")
        self.copy_btn.pack(side="left")
        ToolTip(self.copy_btn, "Copy a prompt containing the current segment text and this question", delay=500)

        self._refresh_display()

    def _move(self, delta):
        self.current_index = max(0, min(self.current_index + delta, len(self.current_q_list) - 1))
        self._refresh_display()

    def _refresh_display(self):
        idx = self.current_index
        self.lbl_text.config(text=self.current_q_list[idx])
        self.prev_btn.set_state("normal" if idx > 0 else "disabled")
        self.next_btn.set_state("normal" if idx < len(self.current_q_list) - 1 else "disabled")

    def _copy_q_context(self):
        question = self.current_q_list[self.current_index]
        context_data = self.get_context_callback() # Expected to return (context_str, current_name, current_text)

        context_str, current_name, current_text = context_data

        prompt = p.STARTER_QUESTION_PROMPT_TEMPLATE.format(
            context_label="Context",
            context_content=context_str,
            focus_name=current_name,
            focus_content=current_text,
            question=question,
            instruction_suffix=f"Focus ONLY on the segment '{current_name}'. Please answer the question or provide critical feedback regarding this segment. Do NOT rewrite the text."
        )

        try:
            self.clipboard_clear()
            self.clipboard_append(prompt)
            self.copy_btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: self.copy_btn.config(text="Copy Context & Question", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if self.copy_btn.winfo_exists() else None)
        except tk.TclError:
            messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.", parent=self)