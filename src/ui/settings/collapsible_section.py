import tkinter as tk
from tkinter import Frame, Label, Text, BooleanVar, ttk
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

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
        text_frame = Frame(self.body_frame, bd=1, relief='sunken')
        text_frame.pack(fill='x', expand=True, padx=(22, 0))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.text_widget = Text(
            text_frame, wrap='word', undo=True, height=4,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            relief='flat', bd=0, highlightthickness=0, font=c.FONT_NORMAL
        )
        self.scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        self.text_widget.grid(row=0, column=0, sticky='nsew')

        # --- State and Bindings ---
        self.is_expanded = BooleanVar(value=False)
        self.default_text = default_text
        self.text_widget.insert('1.0', initial_text)

        self.icon_label.bind("<Button-1>", self.toggle_section)
        title_label.bind("<Button-1>", self.toggle_section)

        # Bind to events that change content or layout, ensuring the check always runs
        self.text_widget.bind("<KeyRelease>", self._schedule_check)
        self.text_widget.bind("<Configure>", self._schedule_check)
        self.bind("<Configure>", self._schedule_check)

    def _schedule_check(self, event=None):
        """
        Schedules a check using after_idle to ensure it runs after Tkinter
        has finished all pending geometry calculations.
        """
        self.after_idle(self._manage_scrollbar)

    def _manage_scrollbar(self):
        top_fraction, bottom_fraction = self.text_widget.yview()

        is_needed = bottom_fraction < 1.0
        is_visible = self.scrollbar.winfo_ismapped()

        if is_needed and not is_visible:
            self.scrollbar.grid(row=0, column=1, sticky='ns')
        elif not is_needed and is_visible:
            self.scrollbar.grid_forget()

    def toggle_section(self, event=None):
        """Expands or collapses the text area."""
        self.is_expanded.set(not self.is_expanded.get())
        if self.is_expanded.get():
            self.body_frame.pack(fill='x', expand=True, pady=(2, 0))
            self.icon_label.config(text="▼")
        else:
            self.body_frame.pack_forget()
            self.icon_label.config(text="▶")

        self._schedule_check()

        if self.on_toggle_callback:
            self.after(5, self.on_toggle_callback)

    def reset_text(self):
        """Resets the text widget to its default value."""
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('1.0', self.default_text)
        self._schedule_check()

    def get_text(self):
        """Returns the current content of the text widget."""
        return self.text_widget.get('1.0', 'end-1c')