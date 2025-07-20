import os
import json
import pyperclip
from tkinter import Tk, Toplevel, Frame, Label, Button, StringVar, messagebox, filedialog
from .utils import load_config, save_config, load_active_file_extensions
from .file_manager import FileManagerWindow
from .filetypes_manager import FiletypesManagerWindow
from .settings_window import SettingsWindow
from .constants import RECENT_DIRS_MAX
from .paths import ICON_PATH

class App(Tk):
    def __init__(self, file_extensions):
        super().__init__()
        self.file_extensions = file_extensions
        self.app_bg_color = '#FFFFFF'

        # --- Window Setup ---
        self.title("CodeMerger")
        self.iconbitmap(ICON_PATH)
        self.geometry("500x200")
        self.configure(bg=self.app_bg_color)

        # --- Load Configuration & Validate Active Directory ---
        self.config = load_config()
        self.default_editor = self.config.get('default_editor', '')
        active_dir_path = self.config.get('active_directory', '')

        # Check for existence of the active directory on boot. Reset if not found.
        if active_dir_path and not os.path.isdir(active_dir_path):
            self.config['active_directory'] = ''
            save_config(self.config)
            active_dir_path = ''

        self.active_dir = StringVar()
        self.active_dir.trace_add('write', self.update_button_states)
        self.set_active_dir_display(active_dir_path) # Set initial display value

        self.recent_dirs = self.config.get('recent_directories', [])

        # --- UI Layout ---
        main_frame = Frame(self, padx=15, pady=15, bg=self.app_bg_color)
        main_frame.pack(fill='both', expand=True)

        # Active directory display
        dir_label = Label(main_frame, text="Active Directory:", font=('Helvetica', 10, 'bold'), bg=self.app_bg_color)
        dir_label.pack(anchor='w')
        active_dir_display = Label(
            main_frame, textvariable=self.active_dir, fg="blue",
            wraplength=450, justify='left', bg=self.app_bg_color
        )
        active_dir_display.pack(anchor='w', fill='x', pady=(0, 10))

        # Main action buttons
        button_frame = Frame(main_frame, bg=self.app_bg_color)
        button_frame.pack(fill='x', pady=5)
        Button(button_frame, text="Select Directory", command=self.open_change_directory_dialog).pack(side='left', expand=True, fill='x', padx=5)

        self.manage_files_button = Button(button_frame, text="Manage Files", command=self.manage_files)
        self.manage_files_button.pack(side='left', expand=True, fill='x', padx=5)

        self.copy_merged_button = Button(button_frame, text="Copy Merged", command=self.copy_merged_code)
        self.copy_merged_button.pack(side='left', expand=True, fill='x', padx=5)

        # A new frame at the bottom to hold the less noticeable button
        config_frame = Frame(main_frame, bg=self.app_bg_color)
        config_frame.pack(fill='x', side='bottom', pady=(5, 0))
        settings_button = Button(
            config_frame,
            text="Settings",
            command=self.open_settings_window,
            relief='flat',
            fg='gray'
        )
        settings_button.pack(side='left')
        config_button = Button(
            config_frame,
            text="Manage Filetypes",
            command=self.open_filetypes_manager,
            relief='flat',
            fg='gray'
        )
        config_button.pack(side='right')

        # Status bar
        self.status_var = StringVar(value="Ready")
        status_bar = Label(self, textvariable=self.status_var, bd=1, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')

        # Set initial button states based on initial active_dir value
        self.update_button_states()

    def set_active_dir_display(self, path):
        """Sets the display string for the active directory's StringVar."""
        if path and os.path.isdir(path):
            self.active_dir.set(path)
        else:
            self.active_dir.set("No directory selected.")

    def update_button_states(self, *args):
        """
        Updates button states based on whether the active_dir StringVar holds a valid path.
        """
        is_dir_active = os.path.isdir(self.active_dir.get())
        new_state = 'normal' if is_dir_active else 'disabled'

        # Check if buttons exist before configuring them
        if hasattr(self, 'manage_files_button'):
            self.manage_files_button.config(state=new_state)
        if hasattr(self, 'copy_merged_button'):
            self.copy_merged_button.config(state=new_state)

    def on_settings_closed(self):
        """Callback for when the settings window is saved and closed."""
        self.config = load_config()
        self.default_editor = self.config.get('default_editor', '')
        self.status_var.set("Settings updated.")

    def open_settings_window(self):
        """Opens the main settings management window."""
        SettingsWindow(self, on_close_callback=self.on_settings_closed)

    def open_filetypes_manager(self):
        FiletypesManagerWindow(self, on_close_callback=self.reload_active_extensions)

    def reload_active_extensions(self):
        self.file_extensions = load_active_file_extensions()
        self.status_var.set("Filetype configuration updated.")

    def update_active_dir(self, new_dir):
        # A blank new_dir can be passed from the browse dialog if cancelled.
        if not new_dir or not os.path.isdir(new_dir):
            return

        # Update config first
        self.config['active_directory'] = new_dir
        if new_dir in self.recent_dirs:
            self.recent_dirs.remove(new_dir)
        self.recent_dirs.insert(0, new_dir)
        self.recent_dirs = self.recent_dirs[:RECENT_DIRS_MAX]
        self.config['recent_directories'] = self.recent_dirs
        save_config(self.config)

        # Then update UI. The trace on active_dir will handle button states.
        self.set_active_dir_display(new_dir)
        self.status_var.set(f"Active directory changed to: {os.path.basename(new_dir)}")

    def open_change_directory_dialog(self):
        # First, validate recent directories and update the config if any are removed.
        initial_count = len(self.recent_dirs)
        self.recent_dirs = [d for d in self.recent_dirs if os.path.isdir(d)]
        if len(self.recent_dirs) != initial_count:
            self.config['recent_directories'] = self.recent_dirs
            save_config(self.config)

        dialog = Toplevel(self)
        dialog.title("Select Directory")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=self.app_bg_color)
        screen_width = self.winfo_screenwidth()
        dialog_width = max(400, min(int(screen_width * 0.5), 800))
        dialog.geometry(f"{dialog_width}x250")
        Label(dialog, text="Select a recent directory or browse for a new one.", padx=10, pady=10, bg=self.app_bg_color).pack()

        def select_and_close(path):
            self.update_active_dir(path)
            dialog.destroy()

        for path in self.recent_dirs:
            btn = Button(dialog, text=path, command=lambda p=path: select_and_close(p))
            btn.pack(fill='x', padx=10, pady=2)

        browse_btn = Button(dialog, text="Browse for Directory...", command=lambda: select_and_close(filedialog.askdirectory(title="Select Project Directory")))
        browse_btn.pack(pady=10)

    def copy_merged_code(self):
        """Merges selected files and copies the result to the clipboard."""
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid directory first.")
            self.status_var.set("Error: Invalid directory.")
            return
        config_path = os.path.join(base_dir, '.allcode')
        if not os.path.isfile(config_path):
            messagebox.showerror("Error", f"No .allcode file found in {base_dir}")
            self.status_var.set("Error: .allcode file not found.")
            return
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            final_ordered_list = data.get('selected_files', [])
            if not final_ordered_list:
                self.status_var.set("No files selected to copy.")
                return
            output_blocks = []
            skipped_files = []
            for path in final_ordered_list:
                full_path = os.path.join(base_dir, path)
                if not os.path.isfile(full_path):
                    skipped_files.append(path)
                    continue
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as code_file:
                    content = code_file.read()
                output_blocks.append(f'--- {path} ---\n```\n{content}\n```')

            final_content = '\n\n\n'.join(output_blocks)
            pyperclip.copy(final_content)

            status_message = "Merged code copied to clipboard."
            if skipped_files:
                status_message += f" Skipped {len(skipped_files)} missing file(s)."
            self.status_var.set(status_message)
        except Exception as e:
            messagebox.showerror("Merging Error", f"An error occurred: {e}")
            self.status_var.set(f"Error during merging: {e}")

    def manage_files(self):
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid directory first.")
            return
        FileManagerWindow(self, base_dir, self.status_var, self.file_extensions, self.default_editor)