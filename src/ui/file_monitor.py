import os
from ..core.utils import parse_gitignore
from ..core.file_scanner import get_all_matching_files
from .. import constants as c
from ..core.merger import recalculate_token_count

class FileMonitor:
    """
    Manages the periodic check for new and deleted files in the active project.
    """
    def __init__(self, app):
        self.app = app
        self._check_job = None
        self.newly_detected_files = []

    def start(self):
        """
        Starts or restarts the periodic check for new files based on current settings.
        Immediately performs a scan after starting.
        """
        self.stop() # Ensure any existing job is cancelled before starting a new one

        self.newly_detected_files = []
        self._update_warning_ui() # Clear any old warning state immediately

        is_dir_active = self.app.project_manager.get_current_project() is not None
        if self.app.app_state.config.get('enable_new_file_check', True) and is_dir_active:
            # Perform the first check immediately, then schedule subsequent checks
            self.app.after(100, self.perform_new_file_check)

    def stop(self):
        """Stops the currently running file check job."""
        if self._check_job:
            self.app.after_cancel(self._check_job)
            self._check_job = None

    def _schedule_next_check(self, interval_ms):
        """Schedules the next execution of the file check."""
        self._check_job = self.app.after(interval_ms, self.perform_new_file_check)

    def perform_new_file_check(self):
        """
        Scans for new and deleted files and updates the state accordingly.
        Also schedules the next check.
        """
        project_config = self.app.project_manager.get_current_project()
        if not project_config:
            self.stop()
            return

        base_dir = project_config.base_dir

        if not os.path.isdir(base_dir):
            self.stop()
            self.app.status_var.set(f"Project directory '{os.path.basename(base_dir)}' no longer exists. Monitoring stopped.")
            self.app.set_active_dir_display(None)
            return

        all_project_files = get_all_matching_files(
            base_dir=base_dir,
            file_extensions=self.app.file_extensions,
            gitignore_patterns=parse_gitignore(base_dir)
        )

        current_set = set(all_project_files)
        known_set = set(project_config.known_files)

        # --- Check for and handle deleted files ---
        deleted_files = known_set - current_set
        if deleted_files:
            project_config.known_files = list(known_set - deleted_files)
            # Also remove them from the selection list if they were there
            original_selection_count = len(project_config.selected_files)
            project_config.selected_files = [f for f in project_config.selected_files if f['path'] not in deleted_files]

            # If the selection changed, invalidate the token count
            if len(project_config.selected_files) != original_selection_count:
                project_config.total_tokens = 0

            project_config.save()
            self.app.status_var.set(f"Cleaned {len(deleted_files)} missing file(s) from '{project_config.project_name}'.")

        # --- Check for new files ---
        new_files = list(current_set - known_set)
        if sorted(new_files) != sorted(self.newly_detected_files):
            self.newly_detected_files = new_files
            self._update_warning_ui()

        # Reschedule the next check
        interval_sec = self.app.app_state.config.get('new_file_check_interval', 5)
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
            # This prevents them from being detected as "new" again.
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
            tooltip_text = f"{file_count} new {file_str_verb} found in the project"
            self.app.new_files_tooltip.text = tooltip_text
            if not self.app.new_files_label.winfo_ismapped():
                self.app.new_files_label.grid(row=0, column=0, sticky='e', padx=(10, 0))
            self.app.manage_files_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.app.new_files_label.grid_forget()
            self.app.manage_files_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

        if self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
            if file_count > 0:
                self.app.view_manager.compact_mode_window.show_warning(file_count, project_name)
            else:
                self.app.view_manager.compact_mode_window.hide_warning(project_name)