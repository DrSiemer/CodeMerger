import os
from ..core.utils import parse_gitignore
from ..core.file_scanner import get_all_matching_files
from .. import constants as c

class FileMonitor:
    """
    Manages the periodic check for new and deleted files in the active project.
    """
    def __init__(self, app):
        self.app = app
        self._check_job = None
        self.newly_detected_files = []

    def start(self):
        """Starts or restarts the periodic check for new files based on current settings."""
        self.stop() # Ensure any existing job is cancelled before starting a new one

        self.newly_detected_files = []
        self._update_warning_ui()

        is_dir_active = self.app.project_manager.get_current_project() is not None
        if self.app.state.config.get('enable_new_file_check', True) and is_dir_active:
            interval_sec = self.app.state.config.get('new_file_check_interval', 5)
            self._schedule_next_check(interval_sec * 1000)

    def stop(self):
        """Stops the currently running file check job."""
        if self._check_job:
            self.app.after_cancel(self._check_job)
            self._check_job = None

    def _schedule_next_check(self, interval_ms):
        """Schedules the next execution of the file check."""
        self._check_job = self.app.after(interval_ms, self.perform_new_file_check)

    def perform_new_file_check(self):
        """Scans for new and deleted files and updates the state accordingly."""
        project_config = self.app.project_manager.get_current_project()
        if not project_config:
            self.stop()
            return

        all_project_files = get_all_matching_files(
            base_dir=project_config.base_dir,
            file_extensions=self.app.file_extensions,
            gitignore_patterns=parse_gitignore(project_config.base_dir)
        )

        current_set = set(all_project_files)
        known_set = set(project_config.known_files)

        # --- Check for and handle deleted files ---
        deleted_files = list(known_set - current_set)
        if deleted_files:
            project_config.known_files = [f for f in project_config.known_files if f not in deleted_files]
            project_config.save()

        # --- Check for new files ---
        new_files = list(current_set - known_set)
        if sorted(new_files) != sorted(self.newly_detected_files):
            self.newly_detected_files = new_files
            self._update_warning_ui()

        # Reschedule the next check
        interval_sec = self.app.state.config.get('new_file_check_interval', 5)
        self._schedule_next_check(interval_sec * 1000)

    def get_newly_detected_files_and_reset(self):
        """
        Returns the list of newly detected files and immediately clears the internal
        list and UI warning. This is called when opening the FileManager.
        """
        files_to_highlight = self.newly_detected_files[:]
        project_config = self.app.project_manager.get_current_project()
        if files_to_highlight and project_config:
            # Add the new files to the project's known list immediately
            project_config.known_files.extend(files_to_highlight)
            project_config.known_files = sorted(list(set(project_config.known_files)))
            project_config.save()

            # Reset the internal state and UI
            self.newly_detected_files = []
            self._update_warning_ui()

        return files_to_highlight

    def _update_warning_ui(self):
        """Shows or hides the new file warning icon and updates tooltips."""
        file_count = len(self.newly_detected_files)
        project_config = self.app.project_manager.get_current_project()
        project_name = project_config.project_name if project_config else ""

        if file_count > 0:
            file_str_verb = "file was" if file_count == 1 else "files were"
            tooltip_text = f"{file_count} new {file_str_verb} added to the project"
            self.app.new_files_tooltip.text = tooltip_text
            self.app.new_files_label.pack(side='right', padx=(10, 0))
            self.app.manage_files_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.app.new_files_label.pack_forget()
            self.app.manage_files_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

        if self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
            if file_count > 0:
                self.app.view_manager.compact_mode_window.show_warning(file_count, project_name)
            else:
                self.app.view_manager.compact_mode_window.hide_warning(project_name)