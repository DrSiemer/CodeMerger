import tkinter as tk
from tkinter import Frame, Label, Entry, filedialog
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class StarterSettingsFrame(Frame):
    """
    Settings section for the Project Starter.
    """
    def __init__(self, parent, vars, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.default_parent_folder = vars['default_parent_folder']
        self._create_widgets()

    def _create_widgets(self):
        self.title_label = Label(self, text="Project Starter", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR)
        self.title_label.pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True)

        self.folder_label = Label(container, text="Default parent folder for new projects:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.folder_label.pack(anchor='w')

        folder_select_frame = Frame(container, bg=c.DARK_BG)
        folder_select_frame.pack(fill='x', pady=(5, 0))

        self.folder_entry = Entry(
            folder_select_frame, textvariable=self.default_parent_folder,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL
        )
        self.folder_entry.pack(side='left', fill='x', expand=True, ipady=4)

        self.browse_btn = RoundedButton(
            folder_select_frame, text="Browse", command=self._browse_folder,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON, height=28, cursor='hand2'
        )
        self.browse_btn.pack(side='left', padx=(5, 0))

    def register_info(self, info_mgr):
        """Registers granular components with Info Mode."""
        info_mgr.register(self.title_label, "set_starter")
        info_mgr.register(self.folder_label, "set_starter_folder")
        info_mgr.register(self.folder_entry, "set_starter_folder")
        info_mgr.register(self.browse_btn, "set_starter_folder")

    def _browse_folder(self):
        folder_selected = filedialog.askdirectory(parent=self)
        if folder_selected:
            self.default_parent_folder.set(folder_selected)