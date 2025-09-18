import tkinter as tk
from tkinter import Frame, Label, Text, BooleanVar
from .rounded_button import RoundedButton
from ... import constants as c

class CollapsibleTextSection(Frame):
    """
    A collapsible frame containing a title, a reset button, and a multi-line text widget.
    """
    def __init__(self, parent, title, initial_text, default_text, on_toggle_callback=None, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.on_toggle_callback = on_toggle_callback
        self.font_bold = ("Segoe UI", 12, 'bold')
        self.font_normal = ("Segoe UI", 12)
        self.font_small_button = ("Segoe UI", 9)

        # --- Header ---
        header_frame = Frame(self, bg=c.DARK_BG)
        header_frame.pack(fill='x', expand=True)

        self.icon_label = Label(header_frame, text="▶", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR, cursor="hand2")
        self.icon_label.pack(side='left', padx=(0, 5))

        title_label = Label(header_frame, text=title, font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR, cursor="hand2")
        title_label.pack(side='left')

        reset_button = RoundedButton(
            header_frame, text="Reset", command=self.reset_text,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=self.font_small_button, height=22, radius=4,
            cursor='hand2'
        )
        reset_button.pack(side='right', padx=(5, 0))

        # --- Body (initially hidden) ---
        self.body_frame = Frame(self, bg=c.DARK_BG)
        text_frame = Frame(self.body_frame, bd=1, relief='sunken')
        text_frame.pack(fill='x', expand=True, padx=(22, 0))
        self.text_widget = Text(
            text_frame, wrap='word', undo=True, height=4,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            relief='flat', bd=0, highlightthickness=0, font=self.font_normal
        )
        self.text_widget.pack(fill='x', expand=True, ipady=4, ipadx=4)

        # --- State and Bindings ---
        self.is_expanded = BooleanVar(value=False)
        self.default_text = default_text
        self.text_widget.insert('1.0', initial_text)

        self.icon_label.bind("<Button-1>", self.toggle_section)
        title_label.bind("<Button-1>", self.toggle_section)

    def toggle_section(self, event=None):
        """Expands or collapses the text area."""
        self.is_expanded.set(not self.is_expanded.get())
        if self.is_expanded.get():
            self.body_frame.pack(fill='x', expand=True, pady=(2, 0))
            self.icon_label.config(text="▼")
        else:
            self.body_frame.pack_forget()
            self.icon_label.config(text="▶")

        if self.on_toggle_callback:
            # Use 'after' to allow the UI to update before the callback fires
            self.after(5, self.on_toggle_callback)

    def reset_text(self):
        """Resets the text widget to its default value."""
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('1.0', self.default_text)

    def get_text(self):
        """Returns the current content of the text widget."""
        return self.text_widget.get('1.0', 'end-1c')