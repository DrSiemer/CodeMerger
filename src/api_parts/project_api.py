import os
import sys
import subprocess
import webview
import logging
from src.core.project_config import ProjectConfig

log = logging.getLogger("CodeMerger")

class ProjectApi:
    """API methods for project selection, loading, and directory actions."""

    def get_current_project(self):
        """Loads and returns the currently active project from AppState."""
        path = self.app_state.active_directory
        if path and os.path.isdir(path):
            project_config, status_msg = self.project_manager.load_project(path)
            return self._format_project_response(project_config, status_msg)
        return None

    def get_recent_projects(self):
        """Returns a formatted list of recently opened projects for the Project Selector Modal."""
        recent = []
        for path in self.app_state.recent_projects:
            if os.path.isdir(path):
                name, color = ProjectConfig.read_project_display_info(path)
                recent.append({"path": path, "name": name, "color": color})
        return recent

    def remove_recent_project(self, path):
        """Removes a project from the recents list and returns the updated list."""
        self.app_state.remove_recent_project(path)
        return self.get_recent_projects()

    def load_project(self, path):
        """Activates and loads a specific project path."""
        if path and os.path.isdir(path):
            if self.app_state.update_active_dir(path):
                project_config, status_msg = self.project_manager.load_project(path)
                return self._format_project_response(project_config, status_msg)
        return None

    def rename_project(self, new_name):
        """Updates the name of the currently active project."""
        project_config = self.project_manager.get_current_project()
        if not project_config or not new_name.strip():
            return None

        project_config.project_name = new_name.strip()
        project_config.save()
        return self._format_project_response(project_config, f"Project renamed to '{new_name.strip()}'")

    def select_project(self):
        """
        Opens the native OS directory selection dialog.
        """
        if not self._window_manager or not self._window_manager.main_window:
            return None

        result = self._window_manager.main_window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            selected_path = result[0]
            if self.app_state.update_active_dir(selected_path):
                project_config, status_msg = self.project_manager.load_project(selected_path)
                return self._format_project_response(project_config, status_msg)
        return None

    def select_color(self):
        """Opens a native color picker and updates the project color."""
        if self._color_picker_active:
            return None

        from tkinter import colorchooser, Tk
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return None

        self._color_picker_active = True
        try:
            # Create a temporary hidden Tk root to host the dialog
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            result = colorchooser.askcolor(
                title="Choose project color",
                initialcolor=project_config.project_color,
                parent=root
            )

            root.destroy()

            if result and result[1]:
                new_hex = result[1]
                project_config.project_color = new_hex
                from src.core.project_config import _calculate_font_color
                project_config.project_font_color = _calculate_font_color(new_hex)
                project_config.save()
                return self._format_project_response(project_config, "Project color updated.")
        finally:
            self._color_picker_active = False

        return None

    def select_directory(self):
        """Opens native OS directory selection dialog specifically for general directory selection."""
        if not self._window_manager or not self._window_manager.main_window:
            return None
        result = self._window_manager.main_window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            return result[0]
        return None

    def open_path(self, path):
        """Opens a specific directory path in the OS file explorer."""
        if not path or not os.path.isdir(path):
            return False
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            return True
        except Exception as e:
            log.error(f"Failed to open path {path}: {e}")
            return False

    def open_project_folder(self, is_ctrl=False, is_alt=False):
        """
        Handles folder icon interactions:
        - Default: Opens the project root in File Explorer/Finder.
        - Ctrl: Copies the full path to the clipboard.
        - Alt: Opens a clean command prompt in the project directory (Windows only).
        """
        project_path = self.app_state.active_directory
        if not project_path or not os.path.isdir(project_path):
            return "No active project folder to open."

        if is_alt:
            try:
                if sys.platform == "win32":
                    # Environment Scrubbing logic to ensure a clean shell
                    new_env = os.environ.copy()
                    venv_root = new_env.pop('VIRTUAL_ENV', None)
                    new_env.pop('PYTHONHOME', None)
                    new_env.pop('PYTHONPATH', None)
                    new_env.pop('PROMPT', None)

                    purge_targets = []
                    if venv_root: purge_targets.append(venv_root.lower())
                    bundle_dir = getattr(sys, '_MEIPASS', None)
                    if bundle_dir: bundle_dir_lower = bundle_dir.lower()
                    else: bundle_dir_lower = ""
                    exec_dir = os.path.dirname(sys.executable).lower()

                    path_entries = new_env.get('PATH', '').split(os.pathsep)
                    cleaned_entries = []
                    for e in path_entries:
                        low = e.lower()
                        if (venv_root and low.startswith(venv_root.lower())) or \
                           (bundle_dir_lower and low.startswith(bundle_dir_lower)) or \
                           (low.startswith(exec_dir)):
                            continue
                        cleaned_entries.append(e)

                    new_env['PATH'] = os.pathsep.join(cleaned_entries)

                    subprocess.Popen('cmd.exe', cwd=project_path, creationflags=subprocess.CREATE_NEW_CONSOLE, env=new_env)
                    return "Opened clean console in project folder."
                else:
                    return "Terminal feature only available on Windows."
            except Exception as e:
                log.error(f"Failed to open console: {e}")
                return f"Error opening console: {e}"

        if is_ctrl:
            import pyperclip
            pyperclip.copy(project_path.replace('/', '\\'))
            return "Project path copied to clipboard."

        # Default: Open in native file manager
        try:
            if sys.platform == "win32":
                os.startfile(project_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", project_path])
            else:
                subprocess.Popen(["xdg-open", project_path])
            return "Opened project folder."
        except Exception as e:
            log.error(f"Failed to open folder: {e}")
            return f"Error opening folder: {e}"