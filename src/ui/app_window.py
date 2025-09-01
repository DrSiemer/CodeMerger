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
from ..core.paths import ICON_PATH, EDIT_ICON_PATH, TRASH_ICON_PATH
from ..core.project_config import ProjectConfig
from .. import constants as c # Import constants
from ..core.secret_scanner import scan_for_secrets
from ..core.updater import Updater
from .custom_widgets import RoundedButton

class App(Tk):
    def __init__(self, file_extensions, app_version="", initial_project_path=None):
        super().__init__()
        self.file_extensions = file_extensions
        self.app_version = app_version
        self.app_bg_color = c.DARK_BG
        self.project_config = None
        self.project_color = c.COMPACT_MODE_BG_COLOR
        self.edit_icon = None
        self.trash_icon_image = None
        self._hide_edit_icon_job = None
        self.title_label = None

        self.state = AppState()
        self.view_manager = ViewManager(self)
        self.updater = Updater(self, self.state, self.app_version)

        # Window Setup
        self.title(f"CodeMerger [ {app_version} ]")
        self.iconbitmap(ICON_PATH)
        self.geometry("800x400")
        self.minsize(800, 400)
        self.configure(bg=self.app_bg_color)

        self.load_images()

        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.bind("<Map>", self.view_manager.on_main_window_restored)

        self.active_dir = StringVar()
        self.project_title_var = StringVar()
        self.active_dir.trace_add('write', self.update_button_states)

        self.build_ui()

        # --- Project Loading Logic ---
        if initial_project_path and os.path.isdir(initial_project_path):
            self.state.update_active_dir(initial_project_path)
            self.set_active_dir_display(initial_project_path)
        else:
            self.set_active_dir_display(self.state.active_directory)

        # Perform update check
        self.after(1500, self.updater.check_for_updates)

    def load_images(self):
        try:
            edit_img_src = Image.open(EDIT_ICON_PATH)
            self.edit_icon = ImageTk.PhotoImage(edit_img_src)
            # Load the trash icon as a Pillow Image object for the custom button
            self.trash_icon_image = Image.open(TRASH_ICON_PATH).resize((18, 18), Image.Resampling.LANCZOS)
        except Exception:
            self.edit_icon = None
            self.trash_icon_image = None

    def build_ui(self):
        """Creates and places all the UI widgets based on the new dark theme design"""
        # --- Style Definitions ---
        font_family = "Segoe UI"
        font_normal = (font_family, 12)
        font_large_bold = (font_family, 24, 'bold')
        font_button = (font_family, 16)

        # --- Window Grid Configuration ---
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # --- Top Bar (Row 0) ---
        top_bar = Frame(self, bg=c.TOP_BAR_BG, padx=20, pady=15)
        top_bar.grid(row=0, column=0, sticky='ew')

        self.color_swatch = Frame(top_bar, width=48, height=48, cursor="hand2")
        self.color_swatch.pack(side='left', padx=(0, 15))
        self.color_swatch.pack_propagate(False)
        self.color_swatch.bind("<Button-1>", self.open_color_chooser)
        self.color_swatch.config(bg=c.TOP_BAR_BG)

        self.title_label = Label(top_bar, textvariable=self.project_title_var, font=font_large_bold, bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, anchor='w', cursor="hand2")
        self.title_label.pack(side='left')
        self.title_label.bind("<Button-1>", self.edit_project_title)
        self.title_label.bind("<Enter>", self.on_title_area_enter)
        self.title_label.bind("<Leave>", self.on_title_area_leave)

        self.edit_icon_label = Label(top_bar, image=self.edit_icon, bg=c.TOP_BAR_BG, cursor="hand2")
        if self.edit_icon:
            self.edit_icon_label.bind("<Button-1>", self.edit_project_title)
            self.edit_icon_label.bind("<Enter>", self.on_title_area_enter)
            self.edit_icon_label.bind("<Leave>", self.on_title_area_leave)

        # --- Top-Level Buttons (Row 1) ---
        top_buttons_container = Frame(self, bg=c.DARK_BG, padx=20)
        top_buttons_container.grid(row=1, column=0, sticky='ew', pady=(15, 0))
        top_buttons_container.columnconfigure(1, weight=1)

        left_buttons = Frame(top_buttons_container, bg=c.DARK_BG)
        left_buttons.grid(row=0, column=0, sticky='w')

        RoundedButton(left_buttons, text="Select Project", font=font_button, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=self.open_change_directory_dialog).pack(side='left')
        self.manage_files_button = RoundedButton(left_buttons, text="Manage Files", font=font_button, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=self.manage_files)
        self.manage_files_button.pack(side='left', padx=(10, 0))

        right_buttons = Frame(top_buttons_container, bg=c.DARK_BG)
        right_buttons.grid(row=0, column=2, sticky='e')
        self.compact_mode_button = RoundedButton(right_buttons, text="Compact Mode", font=font_button, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=self.view_manager.toggle_compact_mode)
        self.compact_mode_button.pack()

        # --- Center "Wrapper & Output" Box (Row 2) ---
        center_frame = Frame(self, bg=c.DARK_BG)
        center_frame.grid(row=2, column=0, sticky='nsew', pady=0)

        wrapper_box = Frame(center_frame, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        wrapper_box.place(relx=0.5, rely=0.55, anchor='center')

        Label(wrapper_box, text="Wrapper & Output", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal, pady=2).pack(pady=(10, 5))

        button_grid_frame = Frame(wrapper_box, bg=c.DARK_BG)
        button_grid_frame.pack(pady=(5, 18), padx=30)
        button_grid_frame.columnconfigure(0, weight=1)
        button_grid_frame.columnconfigure(1, weight=1)

        copy_button_height = 60
        self.copy_wrapped_button = RoundedButton(button_grid_frame, height=copy_button_height, text="Copy Wrapped", font=font_button, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, width=180, command=self.copy_wrapped_code)

        define_wrapper_width = self.copy_wrapped_button.width
        self.wrapper_text_button = RoundedButton(button_grid_frame, text="Define Wrapper Text", height=30, width=define_wrapper_width, font=font_button, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=self.open_wrapper_text_window)

        self.copy_merged_button = RoundedButton(button_grid_frame, height=copy_button_height, text="Copy Merged", font=font_button, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=self.copy_merged_code)

        self.wrapper_text_button.grid(row=0, column=0, sticky='ew', pady=(0, 5))

        # --- Bottom Bar (Row 3) ---
        bottom_bar = Frame(self, bg=c.DARK_BG)
        bottom_bar.grid(row=3, column=0, sticky='ew', pady=(20, 15))
        bottom_buttons_container = Frame(bottom_bar, bg=c.DARK_BG)
        bottom_buttons_container.pack(side='left', padx=20)

        RoundedButton(bottom_buttons_container, text="Manage Filetypes", font=font_button, fg=c.TEXT_COLOR, command=self.open_filetypes_manager, hollow=True).pack(side='left')
        RoundedButton(bottom_buttons_container, text="Settings", font=font_button, fg=c.TEXT_COLOR, command=self.open_settings_window, hollow=True).pack(side='left', padx=(10, 0))

        # --- Status Bar (Row 4) ---
        self.status_var = StringVar(value="Ready")
        status_bar = Label(
            self,
            textvariable=self.status_var,
            relief='flat',
            anchor='w',
            bg=c.STATUS_BG,
            fg=c.STATUS_FG,
            font=(font_family, 9),
            padx=20,
            pady=4
        )
        status_bar.grid(row=4, column=0, sticky='ew')

    def on_title_area_enter(self, event=None):
        if self._hide_edit_icon_job:
            self.after_cancel(self._hide_edit_icon_job)
            self._hide_edit_icon_job = None

        if self.project_config and self.edit_icon:
            self.edit_icon_label.place(
                in_=self.title_label.master,
                x=self.title_label.winfo_x() + self.title_label.winfo_width() + 5,
                y=self.title_label.winfo_y() + (self.title_label.winfo_height() // 2) - (self.edit_icon.height() // 2)
            )

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
        font_family = "Segoe UI"
        font_large_bold = (font_family, 24, 'bold')
        if path and os.path.isdir(path):
            self.active_dir.set(path)
            self.project_config = ProjectConfig(path)
            files_were_cleaned = self.project_config.load()
            if files_were_cleaned:
                self.status_var.set(f"Active project: {os.path.basename(path)} - Cleaned missing files.")
            else:
                self.status_var.set(f"Active project: {os.path.basename(path)} - Wrapper text loaded.")
            self.project_title_var.set(self.project_config.project_name)
            self.project_color = self.project_config.project_color
            self.title_label.config(font=font_large_bold)
        else:
            self.active_dir.set("No project selected")
            self.project_title_var.set("CodeMerger")
            self.project_config = None
            self.project_color = c.COMPACT_MODE_BG_COLOR
            self.title_label.config(font=font_large_bold)
            self.status_var.set("No active project.")
        self.update_button_states()

    def update_button_states(self, *args):
        """Updates button states based on the active directory and .allcode file"""
        is_dir_active = os.path.isdir(self.active_dir.get())
        dir_dependent_state = 'normal' if is_dir_active else 'disabled'
        copy_buttons_state = 'disabled'
        has_wrapper_text = False

        self.manage_files_button.set_state(dir_dependent_state)
        self.wrapper_text_button.set_state(dir_dependent_state)
        self.compact_mode_button.set_state(dir_dependent_state)

        if is_dir_active:
            self.color_swatch.config(bg=self.project_color)
            if not self.color_swatch.winfo_ismapped():
                 self.color_swatch.pack(side='left', padx=(0, 15), before=self.title_label)
        else:
             if self.color_swatch.winfo_ismapped():
                self.color_swatch.pack_forget()

        if not is_dir_active:
            self.edit_icon_label.place_forget()

        if is_dir_active and self.project_config:
            if self.project_config.selected_files:
                copy_buttons_state = 'normal'
            intro = self.project_config.intro_text.strip()
            outro = self.project_config.outro_text.strip()
            if intro or outro:
                has_wrapper_text = True

        self.copy_merged_button.set_state(copy_buttons_state)
        self.copy_wrapped_button.set_state(copy_buttons_state)

        self.copy_wrapped_button.grid_remove()
        self.copy_merged_button.grid_remove()
        self.wrapper_text_button.grid_remove()

        if has_wrapper_text:
            self.wrapper_text_button.grid(row=0, column=0, sticky='ew', pady=(0, 5))
            self.copy_wrapped_button.grid(row=1, column=0, sticky='ew', padx=(0, 5))
            self.copy_merged_button.grid(row=1, column=1, sticky='ew', padx=(5, 0))
        else:
            self.wrapper_text_button.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5))
            self.copy_merged_button.grid(row=1, column=0, columnspan=2, sticky='ew')

    def on_settings_closed(self):
        self.state.reload()
        self.status_var.set("Settings updated")

    def on_directory_selected(self, new_dir):
        if self.state.update_active_dir(new_dir):
            self.set_active_dir_display(new_dir)

    def on_recent_removed(self, path_to_remove):
        cleared_active = self.state.remove_recent_project(path_to_remove)
        self.status_var.set(f"Removed '{os.path.basename(path_to_remove)}' from recent projects")
        if cleared_active:
            self.set_active_dir_display(None)

    def open_color_chooser(self, event=None):
        if not self.project_config: return
        color_code = colorchooser.askcolor(title="Choose project color", initialcolor=self.project_color)
        if color_code and color_code[1]:
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
            on_remove_callback=self.on_recent_removed,
            trash_icon_image=self.trash_icon_image
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
        self.set_active_dir_display(self.active_dir.get())