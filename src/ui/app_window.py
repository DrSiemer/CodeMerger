import os
import json
import sys
import time
import subprocess
import pyperclip
from tkinter import Tk, StringVar, messagebox, colorchooser
from PIL import Image, ImageTk

from ..app_state import AppState
from .view_manager import ViewManager
from .file_manager.file_manager_window import FileManagerWindow
from .filetypes_manager import FiletypesManagerWindow
from .settings.settings_window import SettingsWindow
from .wrapper_text_window import WrapperTextWindow
from .directory_dialog import DirectoryDialog
from ..core.utils import load_active_file_extensions
from ..core.paths import ICON_PATH
from .. import constants as c
from ..core.updater import Updater
from .ui_builder import setup_ui
from .file_monitor import FileMonitor
from .title_edit_dialog import TitleEditDialog
from ..core.project_manager import ProjectManager
from ..core.clipboard import copy_project_to_clipboard
from .assets import assets
from .button_state_manager import ButtonStateManager
from ..core.project_config import _calculate_font_color
from .status_bar_manager import StatusBarManager

class App(Tk):
    def __init__(self, file_extensions, app_version="", initial_project_path=None):
        super().__init__()
        self.withdraw()
        assets.load_tk_images()

        self.file_extensions = file_extensions
        self.app_version = app_version
        self.app_bg_color = c.DARK_BG
        self.project_color = c.COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.window_geometries = {}
        self.title_click_job = None
        self.current_monitor_handle = None
        self.last_x = 0
        self.last_y = 0

        self.app_state = AppState()
        self.view_manager = ViewManager(self)
        self.updater = Updater(self, self.app_state, self.app_version)
        self.project_manager = ProjectManager(lambda: self.file_extensions)
        self.file_monitor = FileMonitor(self)
        self.button_manager = ButtonStateManager(self)

        # Window Setup
        self.title(f"CodeMerger [ {app_version} ]")
        self.iconbitmap(ICON_PATH)
        self.geometry(c.DEFAULT_WINDOW_GEOMETRY)
        self.minsize(c.MIN_WINDOW_WIDTH, c.MIN_WINDOW_HEIGHT)
        self.configure(bg=self.app_bg_color)

        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.bind("<Map>", self.view_manager.on_main_window_restored)
        self.bind("<Unmap>", self.view_manager.on_main_window_minimized)
        self.bind("<Configure>", self._on_window_configure)

        # Initialize StringVar members before UI build
        self.active_dir = StringVar()
        self.project_title_var = StringVar()
        self.status_var = StringVar(value="")
        self.active_dir.trace_add('write', self.button_manager.update_button_states)

        setup_ui(self)

        # Initialize the status bar manager now that the widget exists
        self.status_bar_manager = StatusBarManager(self, self.status_bar, self.status_var)

        # --- Project Loading Logic ---
        if initial_project_path and os.path.isdir(initial_project_path):
            self.app_state.update_active_dir(initial_project_path)
            self.set_active_dir_display(initial_project_path)
        else:
            self.set_active_dir_display(self.app_state.active_directory)

        # Perform update check
        self.after(1500, self.updater.check_for_updates)
        self.deiconify() # Show window now that it's fully configured

    def _on_window_configure(self, event):
        """
        Saves the main window's geometry and detects movement.
        """
        # We only save the geometry when the main window is in its normal state.
        if self.view_manager.current_state == 'normal':
            x, y = self.winfo_x(), self.winfo_y()
            if x != self.last_x or y != self.last_y:
                self.view_manager.main_window_last_move_time = time.time()
                self.last_x = x
                self.last_y = y

            self.view_manager.main_window_geom = (
                x, y,
                self.winfo_width(), self.winfo_height()
            )
            self._check_for_monitor_change()

    def _check_for_monitor_change(self):
        """
        Detects if the main window has moved to a different monitor and clears
        saved child window positions if so. (Windows-only)
        """
        if sys.platform != "win32":
            return

        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            MONITOR_DEFAULTTONEAREST = 2

            hwnd = self.winfo_id()
            new_monitor_handle = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

            if self.current_monitor_handle is None:
                self.current_monitor_handle = new_monitor_handle
                return

            if new_monitor_handle != self.current_monitor_handle:
                self.current_monitor_handle = new_monitor_handle
                if self.window_geometries:
                    self.window_geometries.clear()
                    self.status_var.set("Moved to new monitor, popup window positions cleared.")
        except Exception:
            # Fail silently if any of the Windows API calls fail
            pass

    def handle_title_click(self, event=None):
        """
        Handles a single click on the project title. Schedules project selection
        to open after a short delay, allowing for a double-click to override it.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config:
            # If no project is active, open the dialog immediately.
            self.open_change_directory_dialog()
            return

        # Always cancel any previous job to reset the timer
        if self.title_click_job:
            self.after_cancel(self.title_click_job)
            self.title_click_job = None

        # Schedule the project selector to open after a delay
        self.title_click_job = self.after(250, self.open_change_directory_dialog)

    def edit_project_title(self, event=None):
        # Cancel the pending single-click action first
        if self.title_click_job:
            self.after_cancel(self.title_click_job)
            self.title_click_job = None

        project_config = self.project_manager.get_current_project()
        if not project_config:
            return

        current_name = project_config.project_name
        dialog = TitleEditDialog(
            parent=self,
            title="Edit Project Title",
            prompt="Enter the new title for the project:",
            initialvalue=current_name,
            max_length=c.PROJECT_TITLE_MAX_LENGTH
        )
        new_name = dialog.result

        if new_name is not None and new_name.strip() and new_name.strip() != current_name:
            new_name = new_name.strip()
            self.project_title_var.set(new_name)
            project_config.project_name = new_name
            project_config.save()
            self.status_var.set(f"Project title changed to '{new_name}'")

    def on_app_close(self):
        """Safely destroys child windows before closing the main app"""
        self.file_monitor.stop()
        if self.view_manager.compact_mode_window and self.view_manager.compact_mode_window.winfo_exists():
            self.view_manager.compact_mode_window.destroy()
        self.destroy()

    def show_and_raise(self):
        """De-minimizes, raises, and focuses the main window"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def set_active_dir_display(self, path, set_status=True):
        """Sets the display string for the active directory and loads its config"""
        project_config, status_message = self.project_manager.load_project(path)
        if set_status:
            self.status_var.set(status_message)

        if project_config:
            self.active_dir.set(path)
            self.project_title_var.set(project_config.project_name)
            self.project_color = project_config.project_color
            self.project_font_color = project_config.project_font_color
            self.title_label.config(font=c.FONT_LARGE_BOLD, fg=c.TEXT_COLOR)
        else:
            self.active_dir.set("No project selected")
            self.project_title_var.set("(no active project)")
            self.project_color = c.COMPACT_MODE_BG_COLOR
            self.project_font_color = 'light'
            self.title_label.config(font=c.FONT_LARGE_BOLD, fg=c.TEXT_SUBTLE_COLOR)

        self.file_monitor.start()
        self.button_manager.update_button_states()

    def on_settings_closed(self):
        self.app_state.reload()
        self.file_monitor.start()
        self.status_var.set("Settings updated")

    def on_directory_selected(self, new_dir):
        if self.app_state.update_active_dir(new_dir):
            self.set_active_dir_display(new_dir)

    def on_recent_removed(self, path_to_remove):
        cleared_active = self.app_state.remove_recent_project(path_to_remove)
        self.status_var.set(f"Removed '{os.path.basename(path_to_remove)}' from recent projects")
        if cleared_active:
            self.set_active_dir_display(None)

    def open_color_chooser(self, event=None):
        project_config = self.project_manager.get_current_project()
        if not project_config: return
        # result is a tuple: ((r,g,b), '#rrggbb') or (None, None)
        result = colorchooser.askcolor(title="Choose project color", initialcolor=self.project_color)
        if result and result[1]:
            new_hex_color = result[1]
            self.project_color = new_hex_color
            project_config.project_color = new_hex_color

            # Calculate and save the new font color
            new_font_color = _calculate_font_color(new_hex_color)
            self.project_font_color = new_font_color
            project_config.project_font_color = new_font_color

            project_config.save()
            self.button_manager.update_button_states()

    def open_project_folder(self, event=None):
        project_path = self.active_dir.get()
        is_ctrl_pressed = event and (event.state & 0x0004)

        if is_ctrl_pressed:
            if project_path and os.path.isdir(project_path):
                pyperclip.copy(project_path.replace('/', '\\'))
                self.status_var.set("Copied project path to clipboard")
            else:
                self.status_var.set("No active project path to copy")
            return

        # Normal click
        if project_path and os.path.isdir(project_path):
            try:
                if sys.platform == "win32":
                    os.startfile(project_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", project_path])
                else:
                    subprocess.Popen(["xdg-open", project_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}", parent=self)
        else:
            self.status_var.set("No active project folder to open.")

    def open_settings_window(self):
        SettingsWindow(self, self.updater, on_close_callback=self.on_settings_closed)

    def open_wrapper_text_window(self):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return
        wt_window = WrapperTextWindow(self, project_config, self.status_var, on_close_callback=self.button_manager.update_button_states)
        self.wait_window(wt_window)

    def open_filetypes_manager(self):
        FiletypesManagerWindow(self, on_close_callback=self.reload_active_extensions)

    def reload_active_extensions(self):
        self.file_extensions = load_active_file_extensions()
        self.status_var.set("Filetype configuration updated")
        self.file_monitor.start()

    def open_change_directory_dialog(self):
        self.app_state._prune_recent_projects()
        DirectoryDialog(
            parent=self,
            app_bg_color=self.app_bg_color,
            recent_projects=self.app_state.recent_projects,
            on_select_callback=self.on_directory_selected,
            on_remove_callback=self.on_recent_removed
        )

    def _perform_copy(self, use_wrapper: bool):
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid project folder first", parent=self)
            self.status_var.set("Error: Invalid project folder")
            return

        project_config = self.project_manager.get_current_project()
        if not project_config:
            self.status_var.set("Error: No active project.")
            return

        status_message = copy_project_to_clipboard(
            parent=self,
            base_dir=base_dir,
            project_config=project_config,
            use_wrapper=use_wrapper,
            copy_merged_prompt=self.app_state.copy_merged_prompt,
            scan_secrets_enabled=self.app_state.scan_for_secrets
        )
        self.status_var.set(status_message)

    def copy_merged_code(self):
        self._perform_copy(use_wrapper=False)

    def copy_wrapped_code(self):
        self._perform_copy(use_wrapper=True)

    def manage_files(self):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return

        files_to_highlight = self.file_monitor.get_newly_detected_files_and_reset()

        fm_window = FileManagerWindow(
            self,
            project_config,
            self.status_var,
            self.file_extensions,
            self.app_state.default_editor,
            app_state=self.app_state,
            newly_detected_files=files_to_highlight
        )
        self.wait_window(fm_window)
        self.set_active_dir_display(self.active_dir.get(), set_status=False)