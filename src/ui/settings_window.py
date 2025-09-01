import os
from tkinter import Toplevel, Frame, Label, Entry, filedialog, StringVar, BooleanVar, ttk, Text
from ..core.utils import load_config, save_config
from ..core.registry import get_setting, save_setting
from ..core.paths import ICON_PATH
from .custom_widgets import RoundedButton
from .. import constants as c

class SettingsWindow(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_close_callback = on_close_callback

        config = load_config()
        self.editor_path = StringVar(value=config.get('default_editor', ''))
        self.scan_for_secrets = BooleanVar(value=config.get('scan_for_secrets', False))
        self.check_for_updates = BooleanVar(value=get_setting('AutomaticUpdates', True))
        self.enable_new_file_check = BooleanVar(value=config.get('enable_new_file_check', True))
        self.new_file_check_interval = StringVar(value=str(config.get('new_file_check_interval', 5)))

        # --- Style Definitions ---
        font_family = "Segoe UI"
        font_normal = (font_family, 12)
        font_bold = (font_family, 12, 'bold')
        font_button = (font_family, 16)

        # --- Window Setup ---
        self.title("Settings")
        self.iconbitmap(ICON_PATH)
        self.geometry("600x600")
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

        # --- UI Layout ---
        main_frame = Frame(self, padx=20, pady=20, bg=c.DARK_BG)
        main_frame.pack(fill='both', expand=True)

        # --- Helper for section headers ---
        def create_section_header(parent, text):
            Label(parent, text=text, font=font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))

        # --- Style for ttk Widgets ---
        self.option_add('*TCombobox*Listbox.background', c.TEXT_INPUT_BG)
        self.option_add('*TCombobox*Listbox.foreground', c.TEXT_COLOR)
        self.option_add('*TCombobox*Listbox.selectBackground', c.BTN_BLUE)
        self.option_add('*TCombobox*Listbox.selectForeground', c.BTN_BLUE_TEXT)

        s = ttk.Style()
        s.theme_use('default')
        s.configure('Dark.TCheckbutton', background=c.DARK_BG, foreground=c.TEXT_COLOR, font=font_normal)
        s.map('Dark.TCheckbutton',
              background=[('active', c.DARK_BG)],
              indicatorcolor=[('selected', c.BTN_BLUE), ('!selected', c.TEXT_INPUT_BG)],
              indicatorrelief=[('pressed', 'sunken'), ('!pressed', 'flat')])

        s.configure('Dark.TCombobox',
                    fieldbackground=c.TEXT_INPUT_BG,
                    background=c.TEXT_INPUT_BG,
                    arrowcolor=c.TEXT_COLOR,
                    foreground=c.TEXT_COLOR,
                    selectbackground=c.TEXT_INPUT_BG,
                    selectforeground=c.TEXT_COLOR)
        s.map('Dark.TCombobox',
              foreground=[('readonly', c.TEXT_COLOR)],
              fieldbackground=[('readonly', c.TEXT_INPUT_BG)])


        # --- 1. Check for updates ---
        create_section_header(main_frame, "Application Updates")
        updates_frame = Frame(main_frame, bg=c.DARK_BG)
        updates_frame.pack(fill='x', expand=False)
        self.update_checkbox = ttk.Checkbutton(updates_frame, text="Automatically check for updates daily", variable=self.check_for_updates, style='Dark.TCheckbutton')
        self.update_checkbox.pack(anchor='w')


        # --- 2. File monitoring ---
        create_section_header(main_frame, "File System Monitoring")
        file_system_frame = Frame(main_frame, bg=c.DARK_BG)
        file_system_frame.pack(fill='x', expand=False)
        self.new_file_check_checkbox = ttk.Checkbutton(file_system_frame, text="Periodically check for new project files", variable=self.enable_new_file_check, style='Dark.TCheckbutton', command=self.toggle_interval_selector)
        self.new_file_check_checkbox.pack(anchor='w')

        interval_frame = Frame(file_system_frame, bg=c.DARK_BG)
        interval_frame.pack(fill='x', padx=(25, 0), pady=(5, 0))
        self.interval_label = Label(interval_frame, text="Check every:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal)
        self.interval_label.pack(side='left', padx=(0, 10))
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.new_file_check_interval, values=['2', '5', '10', '30', '60'], state='readonly', width=5, style='Dark.TCombobox')
        self.interval_combo.pack(side='left')
        Label(interval_frame, text="seconds", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal).pack(side='left', padx=(5, 0))
        self.toggle_interval_selector()


        # --- 3. Scan for secrets ---
        create_section_header(main_frame, "Secret Scanning")
        secrets_frame = Frame(main_frame, bg=c.DARK_BG)
        secrets_frame.pack(fill='x', expand=False)
        self.scan_checkbox = ttk.Checkbutton(secrets_frame, text="Scan for secrets on copy (slower)", variable=self.scan_for_secrets, style='Dark.TCheckbutton')
        self.scan_checkbox.pack(anchor='w')


        # --- 4. "Copy Merged" Prompt ---
        create_section_header(main_frame, '"Copy Merged" Prompt')
        prompt_frame = Frame(main_frame, bg=c.DARK_BG)
        prompt_frame.pack(fill='x', expand=False)
        prompt_text_frame = Frame(prompt_frame, bd=1, relief='sunken')
        prompt_text_frame.pack(fill='x', expand=True)
        self.copy_merged_prompt_text = Text(prompt_text_frame, wrap='word', undo=True, height=4, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', bd=0, highlightthickness=0, font=font_normal)
        self.copy_merged_prompt_text.pack(fill='x', expand=True, ipady=4, ipadx=4)
        self.copy_merged_prompt_text.insert('1.0', config.get('copy_merged_prompt', ''))


        # --- 5. Editor config ---
        create_section_header(main_frame, "Default Editor")
        editor_frame = Frame(main_frame, bg=c.DARK_BG)
        editor_frame.pack(fill='x', expand=False)
        self.editor_entry = Entry(editor_frame, textvariable=self.editor_path, state='readonly',
                                  readonlybackground=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, relief='flat', font=font_normal)
        self.editor_entry.pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=4)
        self.browse_button = RoundedButton(editor_frame, text="Browse...", command=self.browse_for_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button)
        self.browse_button.pack(side='left', padx=(0, 5))
        self.clear_button = RoundedButton(editor_frame, text="Clear", command=self.clear_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button)
        self.clear_button.pack(side='left')


        # --- Action Buttons ---
        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.pack(side='bottom', fill='x', pady=(20, 0))

        self.save_button = RoundedButton(button_frame, text="Save and Close", command=self.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=font_button)
        self.save_button.pack(side='right')

        # --- Bindings ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Escape>', lambda e: self.on_closing())

    def toggle_interval_selector(self):
        """Enables or disables the interval dropdown based on the checkbox state."""
        new_state = 'normal' if self.enable_new_file_check.get() else 'disabled'
        self.interval_label.config(state=new_state)
        self.interval_combo.config(state='readonly' if self.enable_new_file_check.get() else 'disabled')

    def browse_for_editor(self):
        # Provide file types for typical executables on Windows
        file_types = [("Executable files", "*.exe"), ("All files", "*.*")] if os.name == 'nt' else []
        filepath = filedialog.askopenfilename(
            title="Select Editor Application",
            filetypes=file_types,
            parent=self
        )
        if filepath:
            self.editor_path.set(filepath)

    def clear_editor(self):
        self.editor_path.set('')

    def on_closing(self):
        self.destroy()

    def save_and_close(self):
        """Saves the configuration and then closes the window."""
        config = load_config()
        config['default_editor'] = self.editor_path.get()
        config['scan_for_secrets'] = self.scan_for_secrets.get()
        config['copy_merged_prompt'] = self.copy_merged_prompt_text.get('1.0', 'end-1c')
        config['enable_new_file_check'] = self.enable_new_file_check.get()
        try:
            config['new_file_check_interval'] = int(self.new_file_check_interval.get())
        except ValueError:
            config['new_file_check_interval'] = 5 # Fallback to default
        save_config(config)
        save_setting('AutomaticUpdates', self.check_for_updates.get())

        if self.on_close_callback:
            self.on_close_callback()

        self.destroy()