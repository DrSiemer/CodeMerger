import os
import json
import sys
import time
import subprocess
import pyperclip
import shutil
import tempfile
import logging
from tkinter import Tk, StringVar, messagebox, colorchooser, Toplevel, Frame
from PIL import Image, ImageTk

from ..app_state import AppState
from .view_manager import ViewManager
from .file_manager.file_manager_window import FileManagerWindow
from .filetypes_manager import FiletypesManagerWindow
from .settings.settings_window import SettingsWindow
from .wrapper_text_window import WrapperTextWindow
from .directory_dialog import DirectoryDialog
from ..core.utils import load_active_file_extensions
from ..core.paths import ICON_PATH, UPDATE_CLEANUP_FILE_PATH
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
from .paste_changes_dialog import PasteChangesDialog
from .new_profile_dialog import NewProfileDialog
from ..core import change_applier
from .compact_status import CompactStatusToast

log = logging.getLogger("CodeMerger")

class App(Tk):
    def __init__(self, file_extensions, app_version="", initial_project_path=None):
        super().__init__()
        self.withdraw()
        self._run_update_cleanup()
        assets.load_tk_images()
        self.assets = assets # [FIX] Assign assets to the instance

        self.file_extensions = file_extensions
        self.app_version = app_version
        self.app_bg_color = c.DARK_BG
        self.project_color = c.COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.window_geometries = {}
        self.title_click_job = None
        self.current_monitor_handle = None
        self.masked_logo_tk = None

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
        self.deiconify()
        self.lift()
        self.focus_force()

    def _run_update_cleanup(self):
        """
        Checks for and executes post-update cleanup instructions.
        This is designed to be safe by only deleting a specific directory
        located inside the system's temporary folder.
        """
        if not os.path.exists(UPDATE_CLEANUP_FILE_PATH):
            return

        log.info("Update cleanup file found. Proceeding with cleanup.")
        try:
            with open(UPDATE_CLEANUP_FILE_PATH, 'r', encoding='utf-8') as f:
                cleanup_data = json.load(f)

            dir_to_delete = cleanup_data.get('temp_dir_to_delete')
            if not dir_to_delete:
                log.warning("Cleanup file exists but contains no directory to delete.")
                return

            system_temp_dir = os.path.realpath(tempfile.gettempdir())
            path_to_delete = os.path.realpath(dir_to_delete)

            if not path_to_delete.startswith(system_temp_dir):
                log.error(f"SECURITY: Update cleanup aborted. Path '{path_to_delete}' is not in temp dir '{system_temp_dir}'.")
                return

            if os.path.isdir(path_to_delete):
                shutil.rmtree(path_to_delete, ignore_errors=True)
                log.info(f"Update Cleanup: Successfully removed temporary directory '{path_to_delete}'.")

        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Update Cleanup Error: Could not read or parse cleanup file. Error: {e}")
        finally:
            try:
                os.remove(UPDATE_CLEANUP_FILE_PATH)
            except OSError as e:
                log.error(f"Failed to remove cleanup file: {e}")

    def _on_window_configure(self, event):
        """
        Saves the main window's current geometry for the restore animation
        and checks if the window has moved to a new monitor.
        """
        if self.view_manager.current_state == 'normal':
            self.view_manager.main_window_geom = (
                self.winfo_x(), self.winfo_y(),
                self.winfo_width(), self.winfo_height()
            )
            self._check_for_monitor_change()

    def _check_for_monitor_change(self):
        """
        Detects if the main window has moved to a different monitor and clears
        saved window positions if so. (Windows-only)
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

                # Invalidate both child window AND compact mode positions
                self.window_geometries.clear()
                self.view_manager.invalidate_compact_mode_position()

                self.status_var.set("Moved to new monitor, window positions reset.")
        except Exception as e:
            log.warning(f"Failed to check for monitor change: {e}")
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
        log.info("Application closing.")
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

        self._update_profile_selector_ui()
        self.file_monitor.start()
        self.button_manager.update_button_states()

    def _update_profile_selector_ui(self):
        project_config = self.project_manager.get_current_project()
        profile_frame = self.profile_frame
        profile_frame.grid_rowconfigure(0, weight=1)

        # Forget all children of the profile frame to reset its layout
        for widget in profile_frame.winfo_children():
            widget.grid_forget()

        if not project_config:
            self.add_profile_button.set_state('disabled')
            return

        self.add_profile_button.set_state('normal')
        profile_names = project_config.get_profile_names()
        active_name = project_config.active_profile_name

        if len(profile_names) > 1:
            # NAVIGATOR layout (centered)
            # Configure profile_frame for centering
            profile_frame.grid_columnconfigure(0, weight=1)
            profile_frame.grid_columnconfigure(1, weight=0) # navigator
            profile_frame.grid_columnconfigure(2, weight=0) # + button
            profile_frame.grid_columnconfigure(3, weight=0, minsize=25) # width 20 + padx 5
            profile_frame.grid_columnconfigure(4, weight=1)

            # Grid the widgets inside profile_frame
            self.profile_navigator.grid(row=0, column=1, sticky='e')
            self.profile_navigator.set_profiles(profile_names, active_name)
            self.add_profile_button.grid(row=0, column=2, sticky='w', padx=(10, 0))

            if active_name != "Default":
                self.delete_profile_button.grid(row=0, column=3, sticky='w', padx=(5, 0))
        else:
            # COMPACT layout (left-aligned)
            # Configure profile_frame for left-alignment with an expanding column
            profile_frame.grid_columnconfigure(0, weight=0)
            profile_frame.grid_columnconfigure(1, weight=1) # Expanding pad
            # Reset other columns to clear any previous settings like minsize
            for i in range(2, 5):
                profile_frame.grid_columnconfigure(i, weight=0, minsize=0)

            # Grid the '+' button at the start of the profile_frame
            self.add_profile_button.grid(row=0, column=0, sticky='w', padx=(10, 0))

    def on_profile_switched(self, new_profile_name):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return

        if new_profile_name != project_config.active_profile_name:
            project_config.active_profile_name = new_profile_name
            project_config.save()
            self.status_var.set(f"Switched to profile: {new_profile_name}")
            self.button_manager.update_button_states()
        self._update_profile_selector_ui()
        self.focus_set()

    def open_new_profile_dialog(self, event=None):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return

        dialog = NewProfileDialog(
            parent=self,
            existing_profile_names=project_config.get_profile_names()
        )
        result = dialog.result

        if result:
            new_name = result['name']
            copy_files = result['copy_files']
            copy_wrappers = result['copy_wrappers']

            if project_config.create_new_profile(new_name, copy_files, copy_wrappers):
                project_config.active_profile_name = new_name # Switch to the new profile
                project_config.save()
                self._update_profile_selector_ui()
                self.button_manager.update_button_states()
                self.status_var.set(f"Created and switched to profile: {new_name}")
            else:
                self.status_var.set(f"Error: Profile '{new_name}' already exists.")

    def delete_current_profile(self, event=None):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return

        profile_to_delete = project_config.active_profile_name
        if profile_to_delete == "Default":
            self.status_var.set("Cannot delete the Default profile.")
            return

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the profile '{profile_to_delete}'?\nThis cannot be undone.",
            parent=self
        ):
            if project_config.delete_profile(profile_to_delete):
                # Switch back to default profile
                project_config.active_profile_name = "Default"
                project_config.save()
                self.status_var.set(f"Profile '{profile_to_delete}' deleted.")
                # Refresh UI
                self._update_profile_selector_ui()
                self.button_manager.update_button_states()
            else:
                self.status_var.set(f"Error: Could not delete profile '{profile_to_delete}'.")

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

    def open_paste_changes_dialog(self, initial_content=None):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return
        PasteChangesDialog(self, project_config.base_dir, self.status_var, initial_content=initial_content)

    def _show_compact_toast(self, message):
        """Displays a temporary status message below the compact mode window."""
        compact_window = self.view_manager.compact_mode_window
        if compact_window and compact_window.winfo_exists():
            CompactStatusToast(compact_window, message)
        else:
            # Fallback to the main status bar if not in compact mode
            self.status_var.set(message)

    def apply_changes_from_clipboard(self):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first", parent=self)
            return

        markdown_text = pyperclip.paste()
        if not markdown_text.strip():
            self._show_compact_toast("Clipboard is empty.")
            return

        plan = change_applier.parse_and_plan_changes(project_config.base_dir, markdown_text)

        status = plan.get('status')
        message = plan.get('message')

        if status == 'ERROR':
            messagebox.showerror("Parsing Error", message, parent=self)
            return

        # Direct confirmation for new files, skipping the full paste dialog
        if status == 'CONFIRM_CREATION':
            creations = plan.get('creations', {})
            creation_rel_paths = [os.path.relpath(p, project_config.base_dir).replace('\\', '/') for p in creations.keys()]

            confirm_message = (
                f"This operation will create {len(creations)} new file(s):\n\n"
                f" - " + "\n - ".join(creation_rel_paths) +
                "\n\nDo you want to proceed?"
            )
            if not messagebox.askyesno("Confirm New Files", confirm_message, parent=self):
                self._show_compact_toast("Operation cancelled.")
                return

        updates = plan.get('updates', {})
        creations = plan.get('creations', {})

        success, final_message = change_applier.execute_plan(updates, creations)

        if success:
            self._show_compact_toast(final_message)
        else:
            messagebox.showerror("File Write Error", final_message, parent=self)

    def on_paste_click(self, event):
        """Handles the press event for the main paste button to show a click."""
        self.paste_changes_button._draw(self.paste_changes_button.click_color)

    def on_paste_release(self, event):
        """Handles the release event to trigger the correct paste action."""
        self.paste_changes_button._draw(self.paste_changes_button.hover_color)
        is_ctrl = (event.state & 0x0004)
        if is_ctrl:
            self.apply_changes_from_clipboard()
        else:
            self.open_paste_changes_dialog()

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