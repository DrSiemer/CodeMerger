import os
import json
from tkinter import Tk, Toplevel, Frame, Label, Button, StringVar, messagebox, filedialog
from .utils import load_config, save_config, load_active_file_extensions
from .file_manager import FileManagerWindow
from .filetypes_manager import FiletypesManagerWindow
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
        # --- Load Configuration ---
        self.config = load_config()
        self.active_dir = StringVar(value=self.config.get('active_directory', 'No directory selected.'))
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
        button_frame.pack(fill='x', pady=10)
        Button(button_frame, text="Select Directory", command=self.open_change_directory_dialog).pack(side='left', expand=True, fill='x', padx=5)
        Button(button_frame, text="Manage Files", command=self.manage_files).pack(side='left', expand=True, fill='x', padx=5)
        Button(button_frame, text="Copy Merged", command=self.copy_merged_code).pack(side='left', expand=True, fill='x', padx=5)

        # --- 2. ADD THE CONFIG BUTTON ---
        # A new frame at the bottom to hold the less noticeable button
        config_frame = Frame(main_frame, bg=self.app_bg_color)
        config_frame.pack(fill='x', pady=(10,0), expand=True, side='bottom')
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

    # --- 3. ADD THE METHOD TO OPEN THE MANAGER ---
    def open_filetypes_manager(self):
        """Opens the filetype management window and sets a callback."""
        FiletypesManagerWindow(self, on_close_callback=self.reload_active_extensions)

    # --- 4. ADD THE CALLBACK METHOD ---
    def reload_active_extensions(self):
        """
        Reloads the list of active file extensions from the config file.
        This is called after the filetype manager is closed.
        """
        self.file_extensions = load_active_file_extensions()
        self.status_var.set("Filetype configuration updated.")

    def update_active_dir(self, new_dir):
        """Sets the new active directory and updates the configuration."""
        if not new_dir:
            return
        self.active_dir.set(new_dir)
        if new_dir in self.recent_dirs:
            self.recent_dirs.remove(new_dir)
        self.recent_dirs.insert(0, new_dir)
        self.recent_dirs = self.recent_dirs[:RECENT_DIRS_MAX]
        self.config['active_directory'] = new_dir
        self.config['recent_directories'] = self.recent_dirs
        save_config(self.config)
        self.status_var.set(f"Active directory changed to: {os.path.basename(new_dir)}")

    def open_change_directory_dialog(self):
        """Opens a dialog to select a new or recent directory."""
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
                    lines = (line.rstrip() for line in code_file)
                    cleaned_lines = [line for line in lines if line]
                    content = '\n'.join(cleaned_lines)
                output_blocks.append(f'--- {path} ---\n```\n{content}\n```')
            final_content = '\n\n\n'.join(output_blocks)
            self.clipboard_clear()
            self.clipboard_append(final_content)
            self.update()
            status_message = "Merged code copied to clipboard."
            if skipped_files:
                status_message += f" Skipped {len(skipped_files)} missing file(s)."
            self.status_var.set(status_message)
        except Exception as e:
            messagebox.showerror("Merging Error", f"An error occurred: {e}")
            self.status_var.set(f"Error during merging: {e}")

    def manage_files(self):
        """Opens the file manager window for the active directory."""
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid directory first.")
            return
        FileManagerWindow(self, base_dir, self.status_var, self.file_extensions)