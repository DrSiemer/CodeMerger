import webview
import os
import logging

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
            "status_msg": status_msg
        }

    def get_current_project(self):
        """Loads and returns the currently active project from AppState."""
        path = self.app_state.active_directory
        if path and os.path.isdir(path):
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