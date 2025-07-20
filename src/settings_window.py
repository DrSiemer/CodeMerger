import os
from tkinter import Toplevel, Frame, Label, Button, Entry, filedialog, StringVar
from .utils import load_config, save_config
from .paths import ICON_PATH

class SettingsWindow(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_close_callback = on_close_callback

        config = load_config()
        self.editor_path = StringVar(value=config.get('default_editor', ''))

        # --- Window Setup ---
        self.title("Settings")
        self.iconbitmap(ICON_PATH)
        self.geometry("600x200")
        self.transient(parent)
        self.grab_set()

        # --- UI Layout ---
        main_frame = Frame(self, padx=15, pady=15)
        main_frame.pack(fill='both', expand=True)

        # --- Default Editor Setting ---
        editor_frame = Frame(main_frame)
        editor_frame.pack(fill='x', expand=True, pady=(0, 10))

        Label(editor_frame, text="Default Editor:", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(0, 5))

        editor_entry_frame = Frame(editor_frame)
        editor_entry_frame.pack(fill='x', expand=True)

        self.editor_entry = Entry(editor_entry_frame, textvariable=self.editor_path, state='readonly', readonlybackground='white')
        self.editor_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        self.browse_button = Button(editor_entry_frame, text="Browse...", command=self.browse_for_editor)
        self.browse_button.pack(side='left', padx=(0, 5))

        self.clear_button = Button(editor_entry_frame, text="Clear", command=self.clear_editor)
        self.clear_button.pack(side='left')

        # --- Action Buttons ---
        button_frame = Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=(20, 0))

        # Placeholder for future settings
        Label(button_frame, text="").pack(expand=True, fill='x')

        self.save_button = Button(button_frame, text="Save and Close", command=self.save_and_close)
        self.save_button.pack(side='right')

        # --- Bindings ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        save_config(config)

        if self.on_close_callback:
            self.on_close_callback()

        self.destroy()