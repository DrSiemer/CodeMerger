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
        self.new_file_alert_threshold = vars['new_file_alert_threshold']

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="File Manager", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15), padx=(25, 0))

        # Token Counting
        self.tokens_chk = ttk.Checkbutton(container, text="Enable token counting", variable=self.token_count_enabled, style='Dark.TCheckbutton')
        self.tokens_chk.pack(anchor='w')

        # Token Limit Section
        limit_frame = Frame(container, bg=c.DARK_BG)
        limit_frame.pack(fill='x', expand=True, pady=(5, 0))
        self.limit_label = Label(limit_frame, text="Max token limit (empty for none):", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.limit_label.pack(side='left', padx=(0, 10))

        vcmd = (self.register(self._validate_integer), '%P')
        self.limit_entry = Entry(limit_frame, textvariable=self.token_limit, width=8, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd)
        self.limit_entry.pack(side='left')

        self.limit_clear_btn = RoundedButton(limit_frame, text="Clear", command=lambda: self.token_limit.set(""), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=22, radius=4, cursor='hand2')
        self.limit_clear_btn.pack(side='left', padx=(10, 0))

        # 'Add All' Warning
        add_all_frame = Frame(container, bg=c.DARK_BG)
        add_all_frame.pack(fill='x', expand=True, pady=(5, 0))
        self.threshold_label = Label(add_all_frame, text="Warn when 'Add all' will add more than:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.threshold_label.pack(side='left', padx=(0, 10))

        self.threshold_entry = Entry(add_all_frame, textvariable=self.add_all_warning_threshold, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd)
        self.threshold_entry.pack(side='left')

        self.files_label = Label(add_all_frame, text="files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.files_label.pack(side='left', padx=(5, 0))

        # Apply Changes Creation Warning Threshold
        alert_frame = Frame(container, bg=c.DARK_BG)
        alert_frame.pack(fill='x', expand=True, pady=(5, 0))
        self.alert_threshold_label = Label(alert_frame, text="New file alert threshold:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.alert_threshold_label.pack(side='left', padx=(0, 10))

        self.alert_threshold_entry = Entry(alert_frame, textvariable=self.new_file_alert_threshold, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd)
        self.alert_threshold_entry.pack(side='left')

        self.files_label_alert = Label(alert_frame, text="files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.files_label_alert.pack(side='left', padx=(5, 0))

    def register_info(self, info_mgr):
        """Registers granular components with Info Mode."""
        info_mgr.register(self.tokens_chk, "set_fm_tokens")
        info_mgr.register(self.limit_label, "set_fm_limit")
        info_mgr.register(self.limit_entry, "set_fm_limit")
        info_mgr.register(self.limit_clear_btn, "set_fm_limit")
        info_mgr.register(self.threshold_label, "set_fm_threshold")
        info_mgr.register(self.threshold_entry, "set_fm_threshold")
        info_mgr.register(self.files_label, "set_fm_threshold")
        info_mgr.register(self.alert_threshold_label, "set_fm_alert_threshold")
        info_mgr.register(self.alert_threshold_entry, "set_fm_alert_threshold")
        info_mgr.register(self.files_label_alert, "set_fm_alert_threshold")

    def _validate_integer(self, value_if_allowed):
        if value_if_allowed == "": return True
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False