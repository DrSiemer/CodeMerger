from tkinter import Toplevel, Frame, Label, Text
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import position_window

class MultilineInputDialog(Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.iconbitmap(ICON_PATH)
        self.result = None

        self.configure(bg=c.DARK_BG)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        Label(main_frame, text=prompt, wraplength=450, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=(0, 10), sticky='w')

        text_frame = Frame(main_frame, bg=c.TEXT_INPUT_BG, bd=1, relief='sunken')
        text_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        self.text_widget = Text(text_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, undo=True, wrap='word')
        self.text_widget.pack(fill='both', expand=True, padx=5, pady=5)

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=2, column=0, pady=(15, 0), sticky='e')

        ok_button = RoundedButton(button_frame, text="OK", command=self.on_ok, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        ok_button.pack(side='right')

        cancel_button = RoundedButton(button_frame, text="Cancel", command=self.on_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        cancel_button.pack(side='right', padx=(0, 10))

        self.bind("<Control-Return>", self.on_ok)
        self.bind("<Escape>", self.on_cancel)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.geometry("500x400")
        self.minsize(400, 300)
        position_window(self)
        self.deiconify()
        self.text_widget.focus_set()
        self.wait_window(self)

    def on_ok(self, event=None):
        self.result = self.text_widget.get('1.0', 'end-1c')
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()