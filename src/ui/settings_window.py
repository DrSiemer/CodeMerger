import os
import tkinter as tk
from tkinter import Toplevel, Frame, Label, Entry, filedialog, StringVar, BooleanVar, ttk
from ..core.utils import load_config, save_config
from ..core.registry import get_setting, save_setting
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_frame import ScrollableFrame
from .widgets.collapsible_section import CollapsibleTextSection
from .style_manager import apply_dark_theme
from .. import constants as c
from .window_utils import position_window, save_window_geometry

class SettingsWindow(Toplevel):
    def __init__(self, parent, updater, on_close_callback=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.updater = updater
        self.on_close_callback = on_close_callback

        config = load_config()
        self.editor_path = StringVar(value=config.get('default_editor', ''))
        self.scan_for_secrets = BooleanVar(value=config.get('scan_for_secrets', False))
        self.check_for_updates = BooleanVar(value=get_setting('AutomaticUpdates', True))
        self.enable_new_file_check = BooleanVar(value=config.get('enable_new_file_check', True))
        self.new_file_check_interval = StringVar(value=str(config.get('new_file_check_interval', 5)))
        self.token_count_enabled = BooleanVar(value=config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT))
        self.token_count_threshold = StringVar(value=str(config.get('token_count_threshold', c.TOKEN_COUNT_THRESHOLD_DEFAULT)))
        self.enable_compact_mode_on_minimize = BooleanVar(value=config.get('enable_compact_mode_on_minimize', True))

        self.font_family = "Segoe UI"
        self.font_normal = (self.font_family, 12)
        self.font_bold = (self.font_family, 12, 'bold')
        self.font_button = (self.font_family, 16)

        self.title("Settings")
        self.iconbitmap(ICON_PATH)
        self.geometry("600x550")
        self.minsize(500, 300)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        apply_dark_theme(self)

        main_frame = Frame(self, bg=c.DARK_BG)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        scroll_frame = ScrollableFrame(main_frame, bg=c.DARK_BG)
        scroll_frame.grid(row=0, column=0, sticky='nsew')
        content_frame = scroll_frame.scrollable_frame
        content_frame.config(padx=20, pady=20)

        # --- All content goes into the content_frame ---
        Label(content_frame, text="Application Updates", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        updates_frame = Frame(content_frame, bg=c.DARK_BG)
        updates_frame.pack(fill='x', expand=True, pady=(0, 15))

        check_now_button = RoundedButton(
            updates_frame, text="Check Now", command=self.run_manual_update_check,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=(self.font_family, 9), height=22, radius=4
        )
        check_now_button.pack(side='right', padx=(10, 0))
        ttk.Checkbutton(updates_frame, text="Automatically check for updates daily", variable=self.check_for_updates, style='Dark.TCheckbutton').pack(side='left')

        Label(content_frame, text="Window Behavior", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        window_behavior_frame = Frame(content_frame, bg=c.DARK_BG)
        window_behavior_frame.pack(fill='x', expand=True, pady=(0, 15))
        ttk.Checkbutton(window_behavior_frame, text="Activate compact mode when main window is minimized", variable=self.enable_compact_mode_on_minimize, style='Dark.TCheckbutton').pack(anchor='w')

        Label(content_frame, text="File System Monitoring", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        file_system_frame = Frame(content_frame, bg=c.DARK_BG)
        file_system_frame.pack(fill='x', expand=True, pady=(0, 15))
        ttk.Checkbutton(file_system_frame, text="Periodically check for new project files", variable=self.enable_new_file_check, style='Dark.TCheckbutton', command=self.toggle_interval_selector).pack(anchor='w')
        interval_frame = Frame(file_system_frame, bg=c.DARK_BG)
        interval_frame.pack(fill='x', padx=(25, 0), pady=(5, 0))
        self.interval_label = Label(interval_frame, text="Check every:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal)
        self.interval_label.pack(side='left', padx=(0, 10))
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.new_file_check_interval, values=['2', '5', '10', '30', '60'], state='readonly', width=5, style='Dark.TCombobox')
        self.interval_combo.pack(side='left')
        Label(interval_frame, text="seconds", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal).pack(side='left', padx=(5, 0))
        self.toggle_interval_selector()

        Label(content_frame, text="Secret Scanning", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        secrets_frame = Frame(content_frame, bg=c.DARK_BG)
        secrets_frame.pack(fill='x', expand=True, pady=(0, 15))
        ttk.Checkbutton(secrets_frame, text="Scan for secrets on copy (slower)", variable=self.scan_for_secrets, style='Dark.TCheckbutton').pack(anchor='w')

        Label(content_frame, text="Token Counting", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        token_count_frame = Frame(content_frame, bg=c.DARK_BG)
        token_count_frame.pack(fill='x', expand=True, pady=(0, 15))
        ttk.Checkbutton(token_count_frame, text="Count tokens for selected files", variable=self.token_count_enabled, style='Dark.TCheckbutton', command=self.toggle_threshold_selector).pack(anchor='w')
        threshold_frame = Frame(token_count_frame, bg=c.DARK_BG)
        threshold_frame.pack(fill='x', padx=(25, 0), pady=(5, 0))
        self.threshold_label = Label(threshold_frame, text="Only show count for files with more than:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal)
        self.threshold_label.pack(side='left', padx=(0, 10))
        vcmd = (self.register(self.validate_integer), '%P')
        self.threshold_entry = Entry(threshold_frame, textvariable=self.token_count_threshold, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=self.font_normal, validate='key', validatecommand=vcmd)
        self.threshold_entry.pack(side='left')
        self.tokens_label = Label(threshold_frame, text="tokens", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal)
        self.tokens_label.pack(side='left', padx=(5, 0))
        self.toggle_threshold_selector()

        self.copy_merged_prompt_section = CollapsibleTextSection(content_frame, '"Copy Merged" Prompt', config.get('copy_merged_prompt', ''), c.DEFAULT_COPY_MERGED_PROMPT, on_toggle_callback=scroll_frame._on_frame_configure)
        self.copy_merged_prompt_section.pack(fill='x', expand=True, pady=(15,0))
        self.default_intro_section = CollapsibleTextSection(content_frame, 'Default Intro Prompt', config.get('default_intro_prompt', ''), c.DEFAULT_INTRO_PROMPT, on_toggle_callback=scroll_frame._on_frame_configure)
        self.default_intro_section.pack(fill='x', expand=True, pady=(15,0))
        self.default_outro_section = CollapsibleTextSection(content_frame, 'Default Outro Prompt', config.get('default_outro_prompt', ''), c.DEFAULT_OUTRO_PROMPT, on_toggle_callback=scroll_frame._on_frame_configure)
        self.default_outro_section.pack(fill='x', expand=True, pady=(15,0))

        Label(content_frame, text="Default Editor", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        editor_frame = Frame(content_frame, bg=c.DARK_BG)
        editor_frame.pack(fill='x', expand=True)
        self.editor_entry = Entry(editor_frame, textvariable=self.editor_path, state='readonly', readonlybackground=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, relief='flat', font=self.font_normal)
        self.editor_entry.pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=4)
        RoundedButton(editor_frame, text="Browse...", command=self.browse_for_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=self.font_button).pack(side='left', padx=(0, 5))
        RoundedButton(editor_frame, text="Clear", command=self.clear_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=self.font_button).pack(side='left')

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        RoundedButton(button_frame, text="Save and Close", command=self.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=self.font_button).grid(row=0, column=1, sticky='e')

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Escape>', lambda e: self.on_closing())

        self._position_window()
        self.deiconify()

    def validate_integer(self, value_if_allowed):
        if value_if_allowed == "" or value_if_allowed.isdigit():
            return True
        return False

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def run_manual_update_check(self):
        self.updater.check_for_updates_manual()

    def toggle_interval_selector(self):
        new_state = 'normal' if self.enable_new_file_check.get() else 'disabled'
        self.interval_label.config(state=new_state)
        self.interval_combo.config(state='readonly' if self.enable_new_file_check.get() else 'disabled')

    def toggle_threshold_selector(self):
        new_state = 'normal' if self.token_count_enabled.get() else 'disabled'
        self.threshold_label.config(state=new_state)
        self.threshold_entry.config(state=new_state)
        self.tokens_label.config(state=new_state)

    def browse_for_editor(self):
        file_types = [("Executable files", "*.exe"), ("All files", "*.*")] if os.name == 'nt' else []
        filepath = filedialog.askopenfilename(title="Select Editor Application", filetypes=file_types, parent=self)
        if filepath:
            self.editor_path.set(filepath)

    def clear_editor(self):
        self.editor_path.set('')

    def on_closing(self):
        self._close_and_save_geometry()

    def save_and_close(self):
        config = load_config()
        config['default_editor'] = self.editor_path.get()
        config['scan_for_secrets'] = self.scan_for_secrets.get()
        config['copy_merged_prompt'] = self.copy_merged_prompt_section.get_text()
        config['default_intro_prompt'] = self.default_intro_section.get_text()
        config['default_outro_prompt'] = self.default_outro_section.get_text()
        config['enable_new_file_check'] = self.enable_new_file_check.get()
        config['token_count_enabled'] = self.token_count_enabled.get()
        config['enable_compact_mode_on_minimize'] = self.enable_compact_mode_on_minimize.get()

        try:
            config['new_file_check_interval'] = int(self.new_file_check_interval.get())
        except ValueError:
            config['new_file_check_interval'] = 5

        try:
            threshold_val = self.token_count_threshold.get()
            config['token_count_threshold'] = int(threshold_val) if threshold_val else 0
        except ValueError:
            config['token_count_threshold'] = c.TOKEN_COUNT_THRESHOLD_DEFAULT

        save_config(config)
        save_setting('AutomaticUpdates', self.check_for_updates.get())
        if self.on_close_callback:
            self.on_close_callback()
        self._close_and_save_geometry()