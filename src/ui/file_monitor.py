import os
from ..core.utils import parse_gitignore
from ..core.file_scanner import get_all_matching_files
from .. import constants as c
from ..core.merger import recalculate_token_count

class FileMonitor:
    """
    Manages periodic checks for new and deleted files.
    Maintains independent 'unknown' state for each project profile.
    Also monitors the configuration file for external changes (e.g. git branch switch).
    """
    def __init__(self, app):
        self.app = app
        self._check_job = None
        self.newly_detected_files = [] # Files 'new' to the CURRENT active profile

    def start(self):
        self.stop()
        self._update_warning_ui()

        is_dir_active = self.app.project_manager.get_current_project() is not None
        if self.app.app_state.config.get('enable_new_file_check', True) and is_dir_active:
            interval_sec = self.app.app_state.config.get('new_file_check_interval', 5)
            self._schedule_next_check(interval_sec * 1000)

    def stop(self):
        if self._check_job:
            self.app.after_cancel(self._check_job)
            self._check_job = None

    def _schedule_next_check(self, interval_ms):
        self._check_job = self.app.after(interval_ms, self.perform_new_file_check)

    def perform_initial_scan(self):
        self.newly_detected_files = []
        self.perform_new_file_check(schedule_next=False)

    def perform_new_file_check(self, schedule_next=True):
        project_config = self.app.project_manager.get_current_project()
        if not project_config:
            self.stop()
            return

        # --- 0. Check for external config changes (e.g. git switch) ---
        if project_config.has_external_changes():
            try:
                # Capture current known files from memory before reload.
                # If we switch to a branch where .allcode is empty/fresh, we don't want to lose
                # our "seen" files history, otherwise everything shows up as NEW.
                current_memory_known = set(project_config.known_files)

                # Reload the config from disk to avoid overwriting it with stale state
                project_config.load()

                # Merge memory back into the loaded config
                if current_memory_known:
                    merged_known = set(project_config.known_files) | current_memory_known
                    project_config.known_files = sorted(list(merged_known))

                # Notify UI of the reload
                self.app.status_var.set("Reloaded project settings due to external change.")
                self.app.profile_actions.update_profile_selector_ui()
                self.app.button_manager.update_button_states()

                # Reset local detection state to avoid false positives against old config
                self.newly_detected_files = list(project_config.unknown_files)
                self._update_warning_ui()

            except Exception as e:
                # If load fails (e.g. file locked or corrupt), skip this scan cycle
                print(f"Error reloading config: {e}")
                if schedule_next:
                    interval_sec = self.app.app_state.config.get('new_file_check_interval', 5)
                    self._schedule_next_check(interval_sec * 1000)
                return

        base_dir = project_config.base_dir
        if not os.path.isdir(base_dir):
            self.stop()
            self.app.status_var.set(f"Project directory '{os.path.basename(base_dir)}' no longer exists.")
            self.app.ui_callbacks.on_directory_selected(None)
            return

        all_project_files = get_all_matching_files(
            base_dir=base_dir,
            file_extensions=self.app.file_extensions,
            gitignore_patterns=parse_gitignore(base_dir)
        )

        current_set = set(all_project_files)
        known_set = set(project_config.known_files)

        config_changed = False

        # --- 1. Handle Deleted Files ---
        # This logic handles actual deletions safely. Files are only removed from 'known_files'
        # if the filesystem scan confirms they are missing from 'current_set'.
        deleted_files = known_set - current_set
        if deleted_files:
            # Remove from global known list
            project_config.known_files = list(known_set - deleted_files)

            # Remove from all profiles' selections and unknown lists
            for p_name, p_data in project_config.profiles.items():
                orig_selection = len(p_data.get('selected_files', []))
                p_data['selected_files'] = [f for f in p_data.get('selected_files', []) if f['path'] not in deleted_files]
                p_data['unknown_files'] = [f for f in p_data.get('unknown_files', []) if f not in deleted_files]

                if len(p_data['selected_files']) != orig_selection:
                    p_data['total_tokens'] = 0 # Force recalc

            config_changed = True
            self.app.status_var.set(f"Cleaned {len(deleted_files)} missing file(s).")

        # --- 2. Handle Brand New Files (to the whole project) ---
        brand_new_files = current_set - set(project_config.known_files)
        if brand_new_files:
            # Update global list
            project_config.known_files.extend(list(brand_new_files))

            # Add to the 'unknown' list of EVERY profile
            for p_data in project_config.profiles.values():
                p_unknown = set(p_data.get('unknown_files', []))
                p_unknown.update(brand_new_files)
                p_data['unknown_files'] = sorted(list(p_unknown))

            config_changed = True

        if config_changed:
            project_config.save()

        # --- 3. Update UI based on active profile's unknown list ---
        # The 'newly_detected_files' is simply what the active profile hasn't seen.
        profile_unknown = project_config.unknown_files
        if sorted(profile_unknown) != sorted(self.newly_detected_files):
            self.newly_detected_files = profile_unknown
            self._update_warning_ui()

        if schedule_next:
            interval_sec = self.app.app_state.config.get('new_file_check_interval', 5)
            self._schedule_next_check(interval_sec * 1000)

    def get_newly_detected_files_and_reset(self):
        """Returns new files for active profile and clears its unknown list."""
        files_to_highlight = self.newly_detected_files[:]
        project_config = self.app.project_manager.get_current_project()

        if files_to_highlight and project_config:
            # Clear only the active profile's unknown list
            project_config.unknown_files = []
            project_config.save()

            self.newly_detected_files = []
            self._update_warning_ui()

        return files_to_highlight

    def _update_warning_ui(self):
        file_count = len(self.newly_detected_files)
        if file_count > 0:
            file_str_verb = "file was" if file_count == 1 else "files were"
            self.app.new_files_tooltip.text = f"{file_count} new {file_str_verb} found.\nClick to manage, Ctrl+Click to add all."
            if not self.app.new_files_label.winfo_ismapped():
                self.app.new_files_label.grid(row=0, column=0, sticky='e', padx=(10, 0))
            self.app.manage_files_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.app.new_files_label.grid_forget()
            self.app.manage_files_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

        if self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
            if file_count > 0:
                self.app.view_manager.compact_mode_window.show_warning(file_count, "")
            else:
                self.app.view_manager.compact_mode_window.hide_warning("")