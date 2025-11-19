import tkinter as tk
from tkinter import Frame, Label, Entry, filedialog
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class WizardSettingsFrame(Frame):
    """
    Settings section for the New Project Wizard.
    """
    def __init__(self, parent, vars, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.default_parent_folder = vars['default_parent_folder']
        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="New Project Wizard", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True)

        Label(container, text="Default parent folder for new projects:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(anchor='w')

        folder_select_frame = Frame(container, bg=c.DARK_BG)
        folder_select_frame.pack(fill='x', pady=(5, 0))

        Entry(
            folder_select_frame, textvariable=self.default_parent_folder,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL
        ).pack(side='left', fill='x', expand=True, ipady=4)

        RoundedButton(
            folder_select_frame, text="Browse", command=self._browse_folder,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON, height=28, cursor='hand2'
        ).pack(side='left', padx=(5, 0))

    def _browse_folder(self):
        folder_selected = filedialog.askdirectory(parent=self)
        if folder_selected:
            self.default_parent_folder.set(folder_selected)