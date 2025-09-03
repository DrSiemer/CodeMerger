from tkinter import Toplevel, Frame, Label, Entry, StringVar
from .custom_widgets import RoundedButton
from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import position_window, save_window_geometry

class TitleEditDialog(Toplevel):
    def __init__(self, parent, title, prompt, initialvalue="", max_length=None):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.iconbitmap(ICON_PATH)
        self.result = None
        self.max_length = max_length

        self.configure(bg=c.DARK_BG)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        Label(main_frame, text=prompt, wraplength=350, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=(0, 10), anchor='w')

        self.entry_var = StringVar(value=initialvalue)
        self.entry = Entry(main_frame, textvariable=self.entry_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=("Segoe UI", 12))
        self.entry.pack(pady=5, fill='x', ipady=4)
        self.entry.focus_set()
        self.entry.select_range(0, 'end')

        if self.max_length:
            self.entry_var.trace_add("write", self._validate_length)

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.pack(pady=(15, 0), fill='x', anchor='e')
        right_buttons_frame = Frame(button_frame, bg=c.DARK_BG)
        right_buttons_frame.pack(side='right')

        ok_button = RoundedButton(right_buttons_frame, text="OK", command=self.on_ok, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=("Segoe UI", 12), width=90, height=30)
        ok_button.pack(side='right')

        cancel_button = RoundedButton(right_buttons_frame, text="Cancel", command=self.on_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=("Segoe UI", 12), width=90, height=30)
        cancel_button.pack(side='right', padx=(0, 10))


        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_cancel)

        # Set a fixed width and make non-resizable
        self.update_idletasks()
        required_height = self.winfo_reqheight()
        self.geometry(f"400x{required_height}")
        self.resizable(False, False)

        self._position_window()
        self.deiconify()
        self.wait_window(self)

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def _validate_length(self, *args):
        value = self.entry_var.get()
        if len(value) > self.max_length:
            self.entry_var.set(value[:self.max_length])

    def on_ok(self, event=None):
        self.result = self.entry_var.get()
        self._close_and_save_geometry()

    def on_cancel(self, event=None):
        self.result = None
        self._close_and_save_geometry()