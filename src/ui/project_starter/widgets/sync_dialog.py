import tkinter as tk
from tkinter import Frame, Label, messagebox, Toplevel
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...window_utils import position_window
from ...tooltip import ToolTip

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
        ToolTip(copy_btn, "Copy the synchronization prompt to clipboard", delay=500)

        # Step 2: Paste Response
        Label(main_frame, text="2. Paste Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=4, column=0, sticky="w", pady=(15, 5))

        self.response_text = ScrollableText(main_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.response_text.grid(row=5, column=0, sticky="nsew", pady=(0, 15))

        # Actions
        btn_frame = Frame(main_frame, bg=c.DARK_BG)
        btn_frame.grid(row=6, column=0, sticky="e")

        btn_cancel = RoundedButton(btn_frame, text="Cancel", command=self.destroy, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor="hand2")
        btn_cancel.pack(side="left", padx=(0, 10))

        btn_apply = RoundedButton(btn_frame, text="Apply Changes", command=self._on_apply, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=120, height=30, cursor="hand2")
        btn_apply.pack(side="left")
        ToolTip(btn_apply, "Apply the synced content to your unlocked segments", delay=500)

    def _copy_prompt(self, btn):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.prompt)
            btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: btn.config(text="Copy", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))
        except tk.TclError:
            messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.", parent=self)

    def _on_apply(self):
        content = self.response_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Input Required", "Please paste the LLM response first.", parent=self)
            return

        self.on_apply_callback(content)
        self.destroy()