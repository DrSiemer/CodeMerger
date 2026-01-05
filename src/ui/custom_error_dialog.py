import pyperclip
from tkinter import Toplevel, Frame, Message
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import position_window

class CustomErrorDialog(Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.parent = parent
        self.message = message
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.iconbitmap(ICON_PATH)

        self.configure(bg=c.DARK_BG)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        msg_widget = Message(main_frame, text=self.message, width=350, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        msg_widget.pack(pady=(0, 20))

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.pack(fill='x')

        ok_button = RoundedButton(button_frame, text="OK", command=self.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        ok_button.pack(side='right')

        copy_button = RoundedButton(button_frame, text="Copy Error", command=self._copy_to_clipboard, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, height=30, cursor='hand2')
        copy_button.pack(side='right', padx=(0, 10))

        self.bind("<Escape>", lambda e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()
        required_height = self.winfo_reqheight()
        dialog_width = 400
        self.geometry(f"{dialog_width}x{required_height}")
        self.resizable(False, False)

        # Ensure the window is fully on-screen and centered relative to parent
        position_window(self)

        self.deiconify()
        ok_button.focus_set()
        self.wait_window(self)

    def _copy_to_clipboard(self):
        pyperclip.copy(self.message)