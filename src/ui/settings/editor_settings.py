import os
import tkinter as tk
from tkinter import Frame, Label, Entry, filedialog
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class EditorSettingsFrame(Frame):
    def __init__(self, parent, vars, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.editor_path = vars['editor_path']

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="Default Editor", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True)

        Entry(container, textvariable=self.editor_path, state='readonly', readonlybackground=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL).pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=4)
        RoundedButton(container, text="Browse...", command=self._browse_for_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2').pack(side='left', padx=(0, 5))
        RoundedButton(container, text="Clear", command=self._clear_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2').pack(side='left')

    def _browse_for_editor(self):
        file_types = [("Executable files", "*.exe"), ("All files", "*.*")] if os.name == 'nt' else []
        filepath = filedialog.askopenfilename(title="Select Editor Application", filetypes=file_types, parent=self)
        if filepath:
            self.editor_path.set(filepath)

    def _clear_editor(self):
        self.editor_path.set('')