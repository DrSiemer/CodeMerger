import os
import json
import pyperclip
from tkinter import Tk, Frame, Label, Button, StringVar, messagebox

from .app_state import AppState
from .view_manager import ViewManager
from .file_manager import FileManagerWindow
from .filetypes_manager import FiletypesManagerWindow
from .settings_window import SettingsWindow
from .wrapper_text_window import WrapperTextWindow
from .merger import generate_output_string
from .directory_dialog import DirectoryDialog
from .utils import load_active_file_extensions
from .paths import ICON_PATH

class App(Tk):
    def __init__(self, file_extensions, app_version=""):
        super().__init__()
        self.file_extensions = file_extensions
        self.app_bg_color = '#FFFFFF'

        self.state = AppState()
        self.view_manager = ViewManager(self)

        # Window Setup
        self.title(f"CodeMerger [ {app_version} ]")
        self.iconbitmap(ICON_PATH)
        self.geometry("500x250")
        self.configure(bg=self.app_bg_color)

        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.bind("<Map>", self.view_manager.on_main_window_restored)

        self.active_dir = StringVar()
        self.active_dir.trace_add('write', self.update_button_states)

        self.build_ui()

        self.set_active_dir_display(self.state.active_directory)

    def build_ui(self):
        """Creates and packs all the UI widgets"""
        main_frame = Frame(self, padx=15, pady=15, bg=self.app_bg_color)
        main_frame.pack(fill='both', expand=True)

        top_frame = Frame(main_frame, bg=self.app_bg_color)
        top_frame.pack(side='top', fill='x')
        Label(top_frame, text="Active Directory:", font=('Helvetica', 10, 'bold'), bg=self.app_bg_color).pack(anchor='w')
        Label(top_frame, textvariable=self.active_dir, fg="blue", wraplength=450, justify='left', bg=self.app_bg_color).pack(anchor='w', fill='x', pady=(0, 10))
        top_button_frame = Frame(top_frame, bg=self.app_bg_color)
        top_button_frame.pack(fill='x', pady=5)
        self.wrapper_text_button = Button(top_button_frame, text="Wrapper Text", command=self.open_wrapper_text_window)
        self.wrapper_text_button.pack(side='right', padx=(3, 0))
        self.manage_files_button = Button(top_button_frame, text="Manage Files", command=self.manage_files)
        self.manage_files_button.pack(side='right', expand=True, fill='x')
        Button(top_button_frame, text="Select Directory", command=self.open_change_directory_dialog).pack(side='right', expand=True, fill='x', padx=(0, 3))

        config_frame = Frame(main_frame, bg=self.app_bg_color)
        config_frame.pack(side='bottom', fill='x', pady=(5, 0))
        Button(config_frame, text="Settings", command=self.open_settings_window, relief='flat', fg='gray').pack(side='left')
        Button(config_frame, text="Manage Filetypes", command=self.open_filetypes_manager, relief='flat', fg='gray').pack(side='left', padx=10)
        Button(config_frame, text="Compact Mode", command=self.view_manager.toggle_compact_mode, relief='flat', fg='gray').pack(side='right')

        copy_button_frame = Frame(main_frame, bg=self.app_bg_color)
        copy_button_frame.pack(fill='both', expand=True, pady=10)
        copy_button_frame.grid_rowconfigure(0, weight=1)
        copy_button_frame.grid_columnconfigure(0, weight=1)
        button_row = Frame(copy_button_frame, bg=self.app_bg_color)
        button_row.grid(row=0, column=0, sticky='ew')
        self.copy_wrapped_button = Button(button_row, text="Copy Wrapped", command=self.copy_wrapped_code, font=('Helvetica', 14, 'bold'), pady=5)
        self.copy_wrapped_button.pack(side='left', padx=(0, 5))
        self.copy_merged_button = Button(button_row, text="Copy Merged", command=self.copy_merged_code, font=('Helvetica', 14, 'bold'), pady=5)
        self.copy_merged_button.pack(side='left', expand=True, fill='x', padx=(5, 0))

        self.status_var = StringVar(value="Ready")
        Label(self, textvariable=self.status_var, bd=1, relief='sunken', anchor='w').pack(side='bottom', fill='x')

    def on_app_close(self):
        """Safely destroys child windows before closing the main app"""
        if self.view_manager.compact_mode_window and self.view_manager.compact_mode_window.winfo_exists():
            self.view_manager.compact_mode_window.destroy()
        self.destroy()

    def show_and_raise(self):
        """De-minimizes, raises, and focuses the main window"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def set_active_dir_display(self, path):
        """Sets the display string for the active directory's StringVar"""
        if path and os.path.isdir(path):
            self.active_dir.set(path)
        else:
            self.active_dir.set("No directory selected")

    def update_button_states(self, *args):
        """Updates button states based on the active directory and .allcode file"""
        is_dir_active = os.path.isdir(self.active_dir.get())
        dir_dependent_state = 'normal' if is_dir_active else 'disabled'
        copy_buttons_state = 'disabled'
        has_wrapper_text = False

        self.manage_files_button.config(state=dir_dependent_state)
        self.wrapper_text_button.config(state=dir_dependent_state)

        if is_dir_active:
            allcode_path = os.path.join(self.active_dir.get(), '.allcode')
            if os.path.isfile(allcode_path):
                try:
                    if os.path.getsize(allcode_path) > 0:
                        with open(allcode_path, 'r', encoding='utf-8-sig') as f:
                            data = json.load(f)
                            if data.get('selected_files'):
                                copy_buttons_state = 'normal'
                            intro = data.get('intro_text', '').strip()
                            outro = data.get('outro_text', '').strip()
                            if intro or outro:
                                has_wrapper_text = True
                except (json.JSONDecodeError, IOError):
                    pass

        self.copy_merged_button.config(state=copy_buttons_state)
        self.copy_wrapped_button.config(state=copy_buttons_state)

        self.copy_wrapped_button.pack_forget()
        self.copy_merged_button.pack_forget()
        if has_wrapper_text:
            self.copy_wrapped_button.pack(side='left', padx=(0, 5))
            self.copy_merged_button.pack(side='left', expand=True, fill='x', padx=(5, 0))
        else:
            self.copy_merged_button.pack(expand=True, fill='x')

    def on_settings_closed(self):
        self.state.reload()
        self.status_var.set("Settings updated")

    def on_directory_selected(self, new_dir):
        if self.state.update_active_dir(new_dir):
            self.set_active_dir_display(new_dir)
            self.status_var.set(f"Active directory changed to: {os.path.basename(new_dir)}")

    def on_recent_removed(self, path_to_remove):
        self.state.remove_recent_directory(path_to_remove)
        self.status_var.set(f"Removed '{os.path.basename(path_to_remove)}' from recent directories")

    def open_settings_window(self):
        SettingsWindow(self, on_close_callback=self.on_settings_closed)

    def open_wrapper_text_window(self):
        if not os.path.isdir(self.active_dir.get()):
            messagebox.showerror("Error", "Please select a valid directory first")
            return
        wt_window = WrapperTextWindow(self, self.active_dir.get(), self.status_var, on_close_callback=self.update_button_states)
        self.wait_window(wt_window)

    def open_filetypes_manager(self):
        FiletypesManagerWindow(self, on_close_callback=self.reload_active_extensions)

    def reload_active_extensions(self):
        self.file_extensions = load_active_file_extensions()
        self.status_var.set("Filetype configuration updated")

    def open_change_directory_dialog(self):
        self.state._prune_recent_dirs()
        DirectoryDialog(
            parent=self,
            app_bg_color=self.app_bg_color,
            recent_dirs=self.state.recent_dirs,
            on_select_callback=self.on_directory_selected,
            on_remove_callback=self.on_recent_removed
        )

    def _perform_copy(self, use_wrapper: bool):
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid directory first")
            self.status_var.set("Error: Invalid directory")
            return

        try:
            final_content, status_message = generate_output_string(base_dir, use_wrapper)
            if final_content is not None:
                pyperclip.copy(final_content)
            self.status_var.set(status_message)
        except FileNotFoundError:
            messagebox.showerror("Error", f"No .allcode file found in {base_dir}")
            self.status_var.set("Error: .allcode file not found")
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Error", f"Could not read .allcode file. Is it empty or corrupt?\n\nDetails: {e}")
            self.status_var.set("Error: Could not read .allcode file")
        except Exception as e:
            messagebox.showerror("Merging Error", f"An error occurred: {e}")
            self.status_var.set(f"Error during merging: {e}")

    def copy_merged_code(self):
        self._perform_copy(use_wrapper=False)

    def copy_wrapped_code(self):
        self._perform_copy(use_wrapper=True)

    def manage_files(self):
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid directory first")
            return
        fm_window = FileManagerWindow(self, base_dir, self.status_var, self.file_extensions, self.state.default_editor)
        self.wait_window(fm_window)
        self.update_button_states()