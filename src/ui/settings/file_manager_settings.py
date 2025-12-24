import tkinter as tk
from tkinter import Frame, Label, Entry, ttk
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class FileManagerSettingsFrame(Frame):
    def __init__(self, parent, vars, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.token_count_enabled = vars['token_count_enabled']
        self.token_limit = vars['token_limit']
        self.add_all_warning_threshold = vars['add_all_warning_threshold']

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="File Manager", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15), padx=(25, 0))

        # Token Counting
        ttk.Checkbutton(container, text="Enable token counting", variable=self.token_count_enabled, style='Dark.TCheckbutton').pack(anchor='w')

        # Token Limit Section
        limit_frame = Frame(container, bg=c.DARK_BG)
        limit_frame.pack(fill='x', expand=True, pady=(5, 0))
        Label(limit_frame, text="Max token limit (empty for none):", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(side='left', padx=(0, 10))
        vcmd = (self.register(self._validate_integer), '%P')
        Entry(limit_frame, textvariable=self.token_limit, width=8, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd).pack(side='left')
        RoundedButton(limit_frame, text="Clear", command=lambda: self.token_limit.set(""), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=22, radius=4, cursor='hand2').pack(side='left', padx=(10, 0))

        # 'Add All' Warning
        add_all_frame = Frame(container, bg=c.DARK_BG)
        add_all_frame.pack(fill='x', expand=True, pady=(5, 0))
        Label(add_all_frame, text="Warn when 'Add all' will add more than:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(side='left', padx=(0, 10))
        Entry(add_all_frame, textvariable=self.add_all_warning_threshold, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd).pack(side='left')
        Label(add_all_frame, text="files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(side='left', padx=(5, 0))

    def _validate_integer(self, value_if_allowed):
        if value_if_allowed == "": return True
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False