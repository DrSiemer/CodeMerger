import tkinter as tk
from tkinter import Toplevel, Frame, StringVar, BooleanVar
from ...core.utils import load_config, save_config
from ...core.registry import get_setting, save_setting
from ...core.paths import ICON_PATH
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_frame import ScrollableFrame
from ..style_manager import apply_dark_theme
from .application_settings import ApplicationSettingsFrame
from .file_manager_settings import FileManagerSettingsFrame
from .prompts_settings import PromptsSettingsFrame
from .editor_settings import EditorSettingsFrame
from .wizard_settings import WizardSettingsFrame
from .unreal_settings import UnrealSettingsFrame
from ... import constants as c
from ..window_utils import position_window, save_window_geometry

class SettingsWindow(Toplevel):
    def __init__(self, parent, updater, on_close_callback=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.updater = updater
        self.on_close_callback = on_close_callback

        self.config = load_config()
        self._init_vars()
        self._init_styles()
        self._init_window()
        self._create_widgets()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Escape>', lambda e: self.on_closing())

        self._position_window()
        self.deiconify()

    def _init_vars(self):
        self.vars = {
            'editor_path': StringVar(value=self.config.get('default_editor', '')),
            'scan_for_secrets': BooleanVar(value=self.config.get('scan_for_secrets', False)),
            'check_for_updates': BooleanVar(value=get_setting('AutomaticUpdates', True)),
            'enable_new_file_check': BooleanVar(value=self.config.get('enable_new_file_check', True)),
            'new_file_check_interval': StringVar(value=str(self.config.get('new_file_check_interval', 5))),
            'token_count_enabled': BooleanVar(value=self.config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT)),
            'enable_compact_mode_on_minimize': BooleanVar(value=self.config.get('enable_compact_mode_on_minimize', True)),
            'add_all_warning_threshold': StringVar(value=str(self.config.get('add_all_warning_threshold', c.ADD_ALL_WARNING_THRESHOLD_DEFAULT))),
            'default_parent_folder': StringVar(value=self.config.get('default_parent_folder', '')),
            'unreal_integration_enabled': BooleanVar(value=self.config.get('unreal_integration_enabled', False)),
            'unreal_port': StringVar(value=str(self.config.get('unreal_port', 6766)))
        }

    def _init_styles(self):
        apply_dark_theme(self)

    def _init_window(self):
        self.title("Settings")
        self.iconbitmap(ICON_PATH)
        self.geometry(c.SETTINGS_WINDOW_DEFAULT_GEOMETRY)
        self.minsize(c.SETTINGS_WINDOW_MIN_WIDTH, c.SETTINGS_WINDOW_MIN_HEIGHT)
        self.transient(self.parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _create_widgets(self):
        # --- Main container frame ---
        main_frame = Frame(self, bg=c.DARK_BG)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # --- Use the reusable ScrollableFrame ---
        self.scroll_frame = ScrollableFrame(main_frame, bg=c.DARK_BG)
        self.scroll_frame.grid(row=0, column=0, sticky='nsew')
        content_frame = self.scroll_frame.scrollable_frame
        content_frame.config(padx=20, pady=20)

        # --- Instantiate and pack setting sections ---
        app_settings = ApplicationSettingsFrame(content_frame, self.vars, self.updater)
        app_settings.pack(fill='x', expand=True)

        fm_settings = FileManagerSettingsFrame(content_frame, self.vars)
        fm_settings.pack(fill='x', expand=True)

        self.prompts_frame = PromptsSettingsFrame(content_frame, self.config, on_toggle=None)
        self.prompts_frame.pack(fill='x', expand=True)

        unreal_settings = UnrealSettingsFrame(content_frame, self.vars)
        unreal_settings.pack(fill='x', expand=True)

        editor_settings = EditorSettingsFrame(content_frame, self.vars)
        editor_settings.pack(fill='x', expand=True)

        wizard_settings = WizardSettingsFrame(content_frame, self.vars)
        wizard_settings.pack(fill='x', expand=True)

        # --- Action Buttons (Outside scroll area) ---
        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        save_button = RoundedButton(button_frame, text="Save and Close", command=self.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        save_button.grid(row=0, column=1, sticky='e')

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def on_closing(self):
        self._close_and_save_geometry()

    def save_and_close(self):
        config = self.config
        prompt_values = self.prompts_frame.get_values()

        config['default_editor'] = self.vars['editor_path'].get()
        config['scan_for_secrets'] = self.vars['scan_for_secrets'].get()
        config['enable_new_file_check'] = self.vars['enable_new_file_check'].get()
        config['token_count_enabled'] = self.vars['token_count_enabled'].get()
        config['enable_compact_mode_on_minimize'] = self.vars['enable_compact_mode_on_minimize'].get()
        config['default_parent_folder'] = self.vars['default_parent_folder'].get()
        config['unreal_integration_enabled'] = self.vars['unreal_integration_enabled'].get()
        config.update(prompt_values)

        try:
            config['new_file_check_interval'] = int(self.vars['new_file_check_interval'].get())
        except ValueError:
            config['new_file_check_interval'] = 5

        try:
            add_all_val = self.vars['add_all_warning_threshold'].get()
            config['add_all_warning_threshold'] = int(add_all_val) if add_all_val else c.ADD_ALL_WARNING_THRESHOLD_DEFAULT
        except ValueError:
            config['add_all_warning_threshold'] = c.ADD_ALL_WARNING_THRESHOLD_DEFAULT

        try:
            config['unreal_port'] = int(self.vars['unreal_port'].get())
        except ValueError:
            config['unreal_port'] = 6766

        save_config(config)
        save_setting('AutomaticUpdates', self.vars['check_for_updates'].get())

        if self.on_close_callback:
            self.on_close_callback()
        self._close_and_save_geometry()