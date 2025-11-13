import tkinter as tk
from tkinter import Toplevel, Frame, Label
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_frame import ScrollableFrame
from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import position_window

class NewFiletypesDialog(Toplevel):
    def __init__(self, parent, new_filetypes_data):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.transient(parent)
        self.title("New Filetypes Added")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        Label(
            main_frame,
            text="The following new default filetypes have been added to your configuration:",
            wraplength=400, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR,
            font=c.FONT_NORMAL
        ).pack(anchor='w', pady=(0, 10))

        ok_button = RoundedButton(
            main_frame, text="OK", command=self.destroy,
            bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL,
            width=90, height=30, cursor='hand2'
        )
        ok_button.pack(side='bottom', anchor='e', pady=(15, 0))

        # --- Scrollable List of New Filetypes ---
        scroll_container = ScrollableFrame(main_frame, bg=c.DARK_BG)
        scroll_container.pack(fill='both', expand=True, pady=5)
        content_frame = scroll_container.scrollable_frame

        for ft in sorted(new_filetypes_data, key=lambda x: x['ext']):
            row = Frame(content_frame, bg=c.DARK_BG)
            row.pack(fill='x', expand=True, pady=3, padx=5)

            ext_label = Label(row, text=ft['ext'], font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR, width=12, anchor='w')
            ext_label.pack(side='left')

            desc_label = Label(row, text=ft.get('description', ''), font=c.FONT_NORMAL, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, wraplength=280, justify='left', anchor='w')
            desc_label.pack(side='left', fill='x', expand=True)

        self.bind("<Return>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()

        # Re-calculate height based on the new layout
        num_items = len(new_filetypes_data)
        item_height_estimate = 35
        # Calculate the fixed height of elements outside the list
        base_height = ok_button.winfo_reqheight() + 130
        # Calculate the variable height of the list, with a maximum
        list_height = min(num_items * item_height_estimate, 350)
        dialog_height = base_height + list_height

        dialog_width = 450
        self.geometry(f"{dialog_width}x{dialog_height}")
        self.resizable(True, True)

        position_window(self)

        self.deiconify()
        ok_button.focus_set()