import tkinter as tk
from tkinter import Frame, Label, Entry, ttk
from ... import constants as c

class FileManagerSettingsFrame(Frame):
    def __init__(self, parent, vars, style_config, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.token_count_enabled = vars['token_count_enabled']
        self.add_all_warning_threshold = vars['add_all_warning_threshold']
        self.font_bold = style_config['font_bold']
        self.font_normal = style_config['font_normal']

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="File Manager", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15), padx=(25, 0))

        # Token Counting
        ttk.Checkbutton(container, text="Enable token counting", variable=self.token_count_enabled, style='Dark.TCheckbutton').pack(anchor='w')

        # 'Add All' Warning
        add_all_frame = Frame(container, bg=c.DARK_BG)
        add_all_frame.pack(fill='x', expand=True, pady=(5, 0))
        Label(add_all_frame, text="Warn when 'Add all' will add more than:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal).pack(side='left', padx=(0, 10))
        vcmd = (self.register(self._validate_integer), '%P')
        Entry(add_all_frame, textvariable=self.add_all_warning_threshold, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=self.font_normal, validate='key', validatecommand=vcmd).pack(side='left')
        Label(add_all_frame, text="files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal).pack(side='left', padx=(5, 0))

    def _validate_integer(self, value_if_allowed):
        if value_if_allowed == "": return True
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False