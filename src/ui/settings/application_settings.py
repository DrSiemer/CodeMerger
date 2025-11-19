import tkinter as tk
from tkinter import Frame, Label, ttk, Entry, filedialog
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class ApplicationSettingsFrame(Frame):
    def __init__(self, parent, vars, updater, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.updater = updater
        self.enable_new_file_check = vars['enable_new_file_check']
        self.new_file_check_interval = vars['new_file_check_interval']
        self.scan_for_secrets = vars['scan_for_secrets']
        self.enable_compact_mode_on_minimize = vars['enable_compact_mode_on_minimize']
        self.check_for_updates = vars['check_for_updates']
        # We'll add a new variable for default parent folder, usually handled in SettingsWindow init
        # but we need to ensure it's passed down or handled here.
        # Assuming SettingsWindow passes a dictionary of vars, we need to make sure it exists there.
        self.default_parent_folder = vars.get('default_parent_folder')

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="Application settings", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15), padx=(25, 0))

        # File Check Section
        file_check_frame = Frame(container, bg=c.DARK_BG)
        file_check_frame.pack(fill='x', expand=True, pady=(0, 5))
        ttk.Checkbutton(file_check_frame, text="Periodically check for new project files", variable=self.enable_new_file_check, style='Dark.TCheckbutton', command=self._toggle_interval_selector).pack(anchor='w')

        interval_frame = Frame(file_check_frame, bg=c.DARK_BG)
        interval_frame.pack(fill='x', padx=(25, 0), pady=(5, 0))
        self.interval_label = Label(interval_frame, text="Check every:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.interval_label.pack(side='left', padx=(0, 10))
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.new_file_check_interval, values=['2', '5', '10', '30', '60'], state='readonly', width=5, style='Dark.TCombobox')
        self.interval_combo.pack(side='left')
        Label(interval_frame, text="seconds", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(side='left', padx=(5, 0))
        self._toggle_interval_selector()

        # Secret Scanning
        ttk.Checkbutton(container, text="Scan for secrets (on each copy)", variable=self.scan_for_secrets, style='Dark.TCheckbutton').pack(anchor='w')

        # Compact Mode
        ttk.Checkbutton(container, text="Activate compact mode when main window is minimized", variable=self.enable_compact_mode_on_minimize, style='Dark.TCheckbutton').pack(anchor='w')

        # Default Parent Folder for New Projects
        if self.default_parent_folder:
            new_proj_frame = Frame(container, bg=c.DARK_BG)
            new_proj_frame.pack(fill='x', expand=True, pady=(10, 5))
            Label(new_proj_frame, text="Default parent folder for new projects:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(anchor='w')

            folder_select_frame = Frame(new_proj_frame, bg=c.DARK_BG)
            folder_select_frame.pack(fill='x', pady=(5, 0))

            Entry(folder_select_frame, textvariable=self.default_parent_folder, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL).pack(side='left', fill='x', expand=True, ipady=4)
            RoundedButton(folder_select_frame, text="Browse", command=self._browse_folder, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, cursor='hand2').pack(side='left', padx=(5, 0))

        # Updates
        updates_frame = Frame(container, bg=c.DARK_BG)
        updates_frame.pack(fill='x', expand=True, pady=(10, 0))
        ttk.Checkbutton(updates_frame, text="Automatically check for updates daily", variable=self.check_for_updates, style='Dark.TCheckbutton').pack(side='left')
        RoundedButton(
            updates_frame, text="Check Now", command=self.updater.check_for_updates_manual,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=22, radius=4, cursor='hand2'
        ).pack(side='left', padx=(10, 0))

    def _toggle_interval_selector(self):
        new_state = 'normal' if self.enable_new_file_check.get() else 'disabled'
        self.interval_label.config(state=new_state)
        self.interval_combo.config(state='readonly' if self.enable_new_file_check.get() else 'disabled')

    def _browse_folder(self):
        folder_selected = filedialog.askdirectory(parent=self)
        if folder_selected:
            self.default_parent_folder.set(folder_selected)