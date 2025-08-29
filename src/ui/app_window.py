import os
import json
import pyperclip
from tkinter import Tk, Frame, Label, Button, StringVar, messagebox, colorchooser, simpledialog
from PIL import Image, ImageTk

from ..app_state import AppState
from .view_manager import ViewManager
from .file_manager.file_manager_window import FileManagerWindow
from .filetypes_manager import FiletypesManagerWindow
from .settings_window import SettingsWindow
from .wrapper_text_window import WrapperTextWindow
from ..core.merger import generate_output_string
from .directory_dialog import DirectoryDialog
from ..core.utils import load_active_file_extensions
from ..core.paths import ICON_PATH, EDIT_ICON_PATH
from ..core.project_config import ProjectConfig
from ..constants import COMPACT_MODE_BG_COLOR
from ..core.secret_scanner import scan_for_secrets

class App(Tk):
    def __init__(self, file_extensions, app_version=""):
        super().__init__()
        self.file_extensions = file_extensions
        self.app_bg_color = '#FFFFFF'
        self.project_config = None
        self.project_color = COMPACT_MODE_BG_COLOR
        self.edit_icon = None
        self._hide_edit_icon_job = None
        self.title_label = None

        self.state = AppState()
        self.view_manager = ViewManager(self)

        # Window Setup
        self.title(f"CodeMerger [ {app_version} ]")
        self.iconbitmap(ICON_PATH)
        self.geometry("500x250")
        self.configure(bg=self.app_bg_color)

        self.load_images()

        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.bind("<Map>", self.view_manager.on_main_window_restored)

        self.active_dir = StringVar()
        self.project_title_var = StringVar()
        self.active_dir.trace_add('write', self.update_button_states)

        self.build_ui()

        self.set_active_dir_display(self.state.active_directory)

    def load_images(self):
        try:
            edit_img_src = Image.open(EDIT_ICON_PATH)
            self.edit_icon = ImageTk.PhotoImage(edit_img_src)
        except Exception:
            self.edit_icon = None

    def build_ui(self):
        """Creates and packs all the UI widgets"""
        main_frame = Frame(self, padx=15, pady=15, bg=self.app_bg_color)
        main_frame.pack(fill='both', expand=True)

        top_frame = Frame(main_frame, bg=self.app_bg_color)
        top_frame.pack(side='top', fill='x')

        title_line_frame = Frame(top_frame, bg=self.app_bg_color)
        title_line_frame.pack(fill='x', pady=(2, 10))

        self.color_swatch = Frame(title_line_frame, width=28, height=28, relief='sunken', borderwidth=1, cursor="hand2")
        self.color_swatch.pack(side='left', padx=(0, 10))
        self.color_swatch.pack_propagate(False) # Prevent shrinking
        self.color_swatch.bind("<Button-1>", self.open_color_chooser)

        self.title_label = Label(title_line_frame, textvariable=self.project_title_var, font=('Helvetica', 18, 'bold'), bg=self.app_bg_color, anchor='w', cursor="hand2", wraplength=450, justify='left')
        self.title_label.pack(side='left', anchor='w')
        self.title_label.bind("<Button-1>", self.edit_project_title)

        self.edit_icon_label = Label(title_line_frame, image=self.edit_icon, bg=self.app_bg_color, cursor="hand2")
        if self.edit_icon:
            self.edit_icon_label.bind("<Button-1>", self.edit_project_title)

        # Bind hover events
        self.title_label.bind("<Enter>", self.on_title_area_enter)
        self.title_label.bind("<Leave>", self.on_title_area_leave)
        self.edit_icon_label.bind("<Enter>", self.on_title_area_enter)
        self.edit_icon_label.bind("<Leave>", self.on_title_area_leave)

        top_button_frame = Frame(top_frame, bg=self.app_bg_color)
        top_button_frame.pack(fill='x', pady=5)

        self.wrapper_text_button = Button(top_button_frame, text="Wrapper Text", command=self.open_wrapper_text_window)
        self.wrapper_text_button.pack(side='right', padx=(3, 0))
        self.manage_files_button = Button(top_button_frame, text="Manage Files", command=self.manage_files)
        self.manage_files_button.pack(side='right', expand=True, fill='x')
        Button(top_button_frame, text="Select project", command=self.open_change_directory_dialog).pack(side='right', expand=True, fill='x', padx=(0, 3))

        config_frame = Frame(main_frame, bg=self.app_bg_color)
        config_frame.pack(side='bottom', fill='x', pady=(5, 0))
        Button(config_frame, text="Settings", command=self.open_settings_window, relief='flat', fg='gray').pack(side='left')
        Button(config_frame, text="Manage Filetypes", command=self.open_filetypes_manager, relief='flat', fg='gray').pack(side='left', padx=10)
        self.compact_mode_button = Button(config_frame, text="Compact Mode", command=self.view_manager.toggle_compact_mode)
        self.compact_mode_button.pack(side='right')

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

    def on_title_area_enter(self, event=None):
        if self._hide_edit_icon_job:
            self.after_cancel(self._hide_edit_icon_job)
            self._hide_edit_icon_job = None

        if self.project_config and self.edit_icon:
            self.update_idletasks()
            x = self.title_label.winfo_x() + self.title_label.winfo_width() + 5
            icon_height = self.edit_icon.height()
            y = self.title_label.winfo_y() + (self.title_label.winfo_height() // 2) - (icon_height // 2) - 10
            self.edit_icon_label.place(x=x, y=y)

    def on_title_area_leave(self, event=None):
        self._hide_edit_icon_job = self.after(50, self.edit_icon_label.place_forget)

    def edit_project_title(self, event=None):
        if not self.project_config:
            return

        current_name = self.project_config.project_name
        new_name = simpledialog.askstring(
            "Edit Project Title",
            "Enter the new title for the project:",
            initialvalue=current_name,
            parent=self
        )

        if new_name and new_name.strip() and new_name.strip() != current_name:
            new_name = new_name.strip()
            self.project_title_var.set(new_name)
            self.project_config.project_name = new_name
            self.project_config.save()
            self.status_var.set(f"Project title changed to '{new_name}'")

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
        """Sets the display string for the active directory and loads its config"""
        if path and os.path.isdir(path):
            self.active_dir.set(path)
            self.project_config = ProjectConfig(path)
            self.project_config.load()
            self.project_title_var.set(self.project_config.project_name)
            self.project_color = self.project_config.project_color
        else:
            self.active_dir.set("No project selected")
            self.project_title_var.set("Select a project folder using the button below")
            self.project_config = None
            self.project_color = COMPACT_MODE_BG_COLOR
        self.update_button_states() # Explicitly call update after changing dir

    def update_button_states(self, *args):
        """Updates button states based on the active directory and .allcode file"""
        is_dir_active = os.path.isdir(self.active_dir.get())
        dir_dependent_state = 'normal' if is_dir_active else 'disabled'
        copy_buttons_state = 'disabled'
        has_wrapper_text = False

        self.manage_files_button.config(state=dir_dependent_state)
        self.wrapper_text_button.config(state=dir_dependent_state)
        self.compact_mode_button.config(state=dir_dependent_state)
        self.color_swatch.config(bg=self.project_color if is_dir_active else "#f0f0f0")

        if not is_dir_active:
            self.edit_icon_label.place_forget()

        if is_dir_active and self.project_config:
            if self.project_config.selected_files:
                copy_buttons_state = 'normal'
            intro = self.project_config.intro_text.strip()
            outro = self.project_config.outro_text.strip()
            if intro or outro:
                has_wrapper_text = True

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
            self.status_var.set(f"Active project changed to: {os.path.basename(new_dir)}")

    def on_recent_removed(self, path_to_remove):
        self.state.remove_recent_project(path_to_remove)
        self.status_var.set(f"Removed '{os.path.basename(path_to_remove)}' from recent projects")

    def open_color_chooser(self, event=None):
        if not self.project_config: return
        # Ask for color, returns (rgb_tuple, hex_string)
        color_code = colorchooser.askcolor(title="Choose project color", initialcolor=self.project_color)
        if color_code and color_code[1]: # Check if a color was chosen
            self.project_color = color_code[1]
            self.project_config.project_color = self.project_color
            self.project_config.save()
            self.update_button_states()

    def open_settings_window(self):
        SettingsWindow(self, on_close_callback=self.on_settings_closed)

    def open_wrapper_text_window(self):
        if not self.project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return
        wt_window = WrapperTextWindow(self, self.project_config, self.status_var, on_close_callback=self.update_button_states)
        self.wait_window(wt_window)

    def open_filetypes_manager(self):
        FiletypesManagerWindow(self, on_close_callback=self.reload_active_extensions)

    def reload_active_extensions(self):
        self.file_extensions = load_active_file_extensions()
        self.status_var.set("Filetype configuration updated")

    def open_change_directory_dialog(self):
        self.state._prune_recent_projects()
        DirectoryDialog(
            parent=self,
            app_bg_color=self.app_bg_color,
            recent_projects=self.state.recent_projects,
            on_select_callback=self.on_directory_selected,
            on_remove_callback=self.on_recent_removed
        )

    def _perform_copy(self, use_wrapper: bool):
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid project folder first", parent=self)
            self.status_var.set("Error: Invalid project folder")
            return

        try:
            files_to_copy = self.project_config.selected_files
            if not files_to_copy:
                self.status_var.set("No files selected to copy.")
                return

            # --- Scan for secrets BEFORE merging (if enabled) ---
            if self.state.scan_for_secrets:
                report = scan_for_secrets(base_dir, files_to_copy)
                if report:
                    warning_message = (
                        "Warning: Potential secrets were detected in your selection.\n\n"
                        f"{report}\n\n"
                        "Do you still want to copy this content to your clipboard?"
                    )
                    proceed = messagebox.askyesno("Secrets Detected", warning_message, parent=self)
                    if not proceed:
                        self.status_var.set("Copy cancelled due to potential secrets.")
                        return

            # --- If scan passes or user agrees, proceed to copy ---
            final_content, status_message = generate_output_string(base_dir, use_wrapper)
            if final_content is not None:
                pyperclip.copy(final_content)
                self.status_var.set(status_message)
            else:
                self.status_var.set(status_message or "Error: Could not generate content.")

        except FileNotFoundError:
            messagebox.showerror("Error", f"No .allcode file found in {base_dir}", parent=self)
            self.status_var.set("Error: .allcode file not found")
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Error", f"Could not read .allcode file. Is it empty or corrupt?\n\nDetails: {e}", parent=self)
            self.status_var.set("Error: Could not read .allcode file")
        except Exception as e:
            messagebox.showerror("Merging Error", f"An error occurred: {e}", parent=self)
            self.status_var.set(f"Error during merging: {e}")

    def copy_merged_code(self):
        self._perform_copy(use_wrapper=False)

    def copy_wrapped_code(self):
        self._perform_copy(use_wrapper=True)

    def manage_files(self):
        if not self.project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return
        fm_window = FileManagerWindow(self, self.project_config, self.status_var, self.file_extensions, self.state.default_editor)
        self.wait_window(fm_window)
        self.update_button_states()