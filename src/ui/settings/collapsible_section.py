import tkinter as tk
from tkinter import Frame, Label, BooleanVar
from ..widgets.rounded_button import RoundedButton
from ... import constants as c
from ..widgets.scrollable_text import ScrollableText

class CollapsibleTextSection(Frame):
    """
    A collapsible frame containing a title, a reset button, and a multi-line text widget.
    """
    def __init__(self, parent, title, initial_text, default_text, on_toggle_callback=None, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.on_toggle_callback = on_toggle_callback

        # --- Header ---
        header_frame = Frame(self, bg=c.DARK_BG)
        header_frame.pack(fill='x', expand=True)

        self.icon_label = Label(header_frame, text="▶", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR, cursor="hand2")
        self.icon_label.pack(side='left', padx=(0, 5))

        title_label = Label(header_frame, text=title, font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR, cursor="hand2")
        title_label.pack(side='left')

        reset_button = RoundedButton(
            header_frame, text="Reset", command=self.reset_text,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON, height=22, radius=4,
            cursor='hand2'
        )
        reset_button.pack(side='right', padx=(5, 0))

        # --- Body (initially hidden) ---
        self.body_frame = Frame(self, bg=c.DARK_BG)

        self.text_widget = ScrollableText(
            self.body_frame,
            height=4,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=c.FONT_NORMAL
        )
        self.text_widget.pack(fill='x', expand=True, padx=(22, 0))

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
            self.after(5, self.on_toggle_callback)

    def reset_text(self):
        """Resets the text widget to its default value."""
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('1.0', self.default_text)

    def get_text(self):
        """Returns the current content of the text widget."""
        return self.text_widget.get('1.0', 'end-1c')