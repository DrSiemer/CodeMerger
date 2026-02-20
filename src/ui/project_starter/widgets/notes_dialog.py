import tkinter as tk
from tkinter import Frame, Label
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...widgets.markdown_renderer import MarkdownRenderer
from ...window_utils import position_window
from ....core.paths import ICON_PATH

class NotesDisplayDialog(tk.Toplevel):
    """
    A modal dialog to display changes/explanations from the LLM.
    """
    def __init__(self, parent, notes_text):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.title("Change Summary & Explanation")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Use grid to ensure layout is respected in smaller window sizes
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        Label(main_frame, text="Review Changes", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Explicit height for the internal text widget ensures the window doesn't request
        # too much space, while grid layout ensures the button isn't pushed off screen.
        self.renderer = MarkdownRenderer(main_frame, base_font_size=11, height=8)
        self.renderer.grid(row=1, column=0, sticky="nsew")
        self.renderer.set_markdown(notes_text)

        btn_frame = Frame(main_frame, bg=c.DARK_BG)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))

        ok_button = RoundedButton(btn_frame, text="Got it", command=self.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
        ok_button.pack(side="right")

        # position_window uses NOTES_DIALOG_DEFAULT_GEOMETRY (600x350)
        position_window(self)

        self.deiconify()
        ok_button.focus_set()
        self.wait_window(self)