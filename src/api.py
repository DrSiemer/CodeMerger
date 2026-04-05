import webview
import os
import logging
import pyperclip
from src.core.secret_scanner import scan_for_secrets
from src.core.merger import generate_output_string
from src.core.project_config import ProjectConfig

log = logging.getLogger("CodeMerger")

class Api:
    """
    The Python API bridge exposed to the Vue 3 frontend via PyWebView.
    Methods defined here can be called directly from JavaScript using `window.pywebview.api.method_name()`.
    """
    def __init__(self, app_state, project_manager):
        # Prefixing with an underscore prevents PyWebView from inspecting this attribute
        # during JS API generation, which avoids a premature DOM evaluation crash.
        self._window = None
        self.app_state = app_state
        self.project_manager = project_manager

    def set_window(self, window):
        """Sets the active PyWebView window reference."""
        self._window = window

    def get_app_config(self):
        """Returns the global application configuration."""
        return self.app_state.config

    def _format_project_response(self, project_config, status_msg):
        """Helper to format ProjectConfig into a dictionary suitable for JSON serialization."""
        if not project_config:
            return None
        return {
            "path": project_config.base_dir,
            "project_name": project_config.project_name,
            "project_color": project_config.project_color,
            "project_font_color": project_config.project_font_color,
            "total_tokens": project_config.total_tokens,
            "has_instructions": bool(project_config.intro_text or project_config.outro_text),
            "status_msg": status_msg
        }

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

    def select_project(self):
        """
        Opens the native OS directory selection dialog.
        Initializes the selected directory as a CodeMerger project and updates the active state.
        Returns the project data dictionary, or None if cancelled.
        """
        if not self._window:
            log.warning("select_project called but window reference is missing.")
            return None

        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            selected_path = result[0]
            log.info(f"Directory selected via native dialog: {selected_path}")

            # Update internal state and load/initialize the project
            if self.app_state.update_active_dir(selected_path):
                project_config, status_msg = self.project_manager.load_project(selected_path)
                return self._format_project_response(project_config, status_msg)

        log.info("Directory selection cancelled.")
        return None

    def copy_code(self, use_wrapper):
        """
        Merges the selected files and copies the result to the clipboard.
        Evaluates secret scanning and prompts the user via PyWebView dialogs if necessary.
        Replaces the Tkinter-dependent `copy_project_to_clipboard` logic.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config or not project_config.selected_files:
            return "No files selected to copy."

        base_dir = self.app_state.active_directory
        files_to_copy = [f['path'] for f in project_config.selected_files]

        if self.app_state.scan_for_secrets:
            report = scan_for_secrets(base_dir, files_to_copy)
            if report:
                warning_message = f"Warning: Potential secrets were detected in your selection.\n\n{report}\n\nDo you still want to copy this content to your clipboard?"
                # create_confirmation_dialog returns True for OK, False for Cancel
                proceed = self._window.create_confirmation_dialog("Secrets Detected", warning_message)
                if not proceed:
                    return "Copy cancelled due to potential secrets."

        final_content, status_message = generate_output_string(
            base_dir,
            project_config,
            use_wrapper,
            self.app_state.copy_merged_prompt
        )

        if final_content is not None:
            pyperclip.copy(final_content)
            return status_message

        return status_message or "Error: Could not generate content."

    def test(self):
        """A simple test method to verify the Vue -> Python bridge is working."""
        log.info("API test method called from Vue frontend.")
        return "Hello from Python API! The bridge is working perfectly."