import os
from datetime import datetime
from .core.utils import load_config, save_config
from .constants import RECENT_PROJECTS_MAX
from .core.prompts import DEFAULT_COPY_MERGED_PROMPT
from .core.registry import get_setting

class AppState:
    """
    Manages the application's persistent state loaded from and saved to config.json
    """
    def __init__(self, is_second_instance=False):
        self.config = load_config()
        self.active_directory = self.config.get('active_directory', '')

        # Prevent secondary instances from automatically loading the last project
        if is_second_instance:
            self.active_directory = ''
            # Update local config dict so accidental saves don't immediately wipe the primary instance project
            self.config['active_directory'] = ''

        self.recent_projects = self.config.get('user_lists', {}).get('recent_projects', [])
        self.default_editor = self.config.get('default_editor', '')
        self.scan_for_secrets = self.config.get('scan_for_secrets', False)
        self.copy_merged_prompt = self.config.get('copy_merged_prompt', DEFAULT_COPY_MERGED_PROMPT)
        self.check_for_updates = get_setting('AutomaticUpdates', True)
        self.last_update_check = self.config.get('last_update_check', None)
        self.enable_compact_mode_on_minimize = self.config.get('enable_compact_mode_on_minimize', False)
        self.enable_ultra_compact_mode = self.config.get('enable_ultra_compact_mode', False)

        self.info_mode_active = self.config.get('info_mode_active', True)
        self.enable_fast_apply = self.config.get('enable_fast_apply', True)

        # Transient flag for cross-window signaling
        self.open_fm_on_restore = False

        # List of callbacks to synchronize info mode visibility across windows
        self._info_observers = []

        self._validate_active_dir()
        self._prune_recent_projects()

    def register_info_observer(self, callback):
        """Registers a callback function to be notified of info mode changes."""
        if callback not in self._info_observers:
            self._info_observers.append(callback)

    def toggle_info_mode(self):
        """Toggles the info mode state and notifies all registered observers."""
        self.info_mode_active = not self.info_mode_active
        self.config['info_mode_active'] = self.info_mode_active
        self._save()

        for observer in self._info_observers:
            try:
                observer(self.info_mode_active)
            except Exception:
                pass

    def _validate_active_dir(self):
        """Checks for existence of the active directory. Resets if not found"""
        if self.active_directory and not os.path.isdir(self.active_directory):
            self.active_directory = ''
            self.config['active_directory'] = ''
            self._save()

    def _prune_recent_projects(self):
        """Removes non-existent directories from the recent list"""
        initial_count = len(self.recent_projects)
        self.recent_projects = [d for d in self.recent_projects if os.path.isdir(d)]
        if len(self.recent_projects) != initial_count:
            self.config.setdefault('user_lists', {})['recent_projects'] = self.recent_projects
            self._save()

    def _save(self):
        """
        Saves the current state back to the config file with multi-instance reconciliation.
        Ensures that interactions in one window do not wipe history from another.
        """
        # Reload the latest state from disk to preserve history (Recent Projects) added by other windows
        disk_config = load_config()

        # Apply settings from our current memory state.
        # This ensures "Last Changed Wins" for active project and global preferences.
        disk_config['active_directory'] = self.active_directory
        disk_config['default_editor'] = self.default_editor
        disk_config['scan_for_secrets'] = self.scan_for_secrets
        disk_config['copy_merged_prompt'] = self.copy_merged_prompt
        disk_config['last_update_check'] = self.last_update_check
        disk_config['enable_compact_mode_on_minimize'] = self.enable_compact_mode_on_minimize
        disk_config['enable_ultra_compact_mode'] = self.enable_ultra_compact_mode
        disk_config['info_mode_active'] = self.info_mode_active
        disk_config['enable_fast_apply'] = self.enable_fast_apply

        # Preserve geometry if it was updated in our local config dict (e.g., during window move/resize)
        if 'main_window_geom' in self.config:
            disk_config['main_window_geom'] = self.config['main_window_geom']

        # Sync history lists
        disk_config.setdefault('user_lists', {})['recent_projects'] = self.recent_projects

        save_config(disk_config)
        # Update local memory dict to stay in sync with reconciled file
        self.config = disk_config

    def reload(self):
        """Reloads the configuration from disk, e.g., after settings change"""
        self.config = load_config()
        self.default_editor = self.config.get('default_editor', '')
        self.scan_for_secrets = self.config.get('scan_for_secrets', False)
        self.copy_merged_prompt = self.config.get('copy_merged_prompt', DEFAULT_COPY_MERGED_PROMPT)
        self.enable_compact_mode_on_minimize = self.config.get('enable_compact_mode_on_minimize', False)
        self.enable_ultra_compact_mode = self.config.get('enable_ultra_compact_mode', False)
        self.info_mode_active = self.config.get('info_mode_active', True)
        self.enable_fast_apply = self.config.get('enable_fast_apply', True)
        self.check_for_updates = get_setting('AutomaticUpdates', True)
        self.last_update_check = self.config.get('last_update_check', None)

    def update_last_check_date(self):
        """Updates the timestamp for the last update check to today"""
        now_iso = datetime.now().isoformat()
        self.last_update_check = now_iso
        self.config['last_update_check'] = now_iso
        self._save()

    def update_active_dir(self, new_dir):
        """Sets a new active directory and updates the recent list"""
        if not new_dir or not os.path.isdir(new_dir):
            return False

        self.active_directory = new_dir
        self.config['active_directory'] = new_dir

        if new_dir in self.recent_projects:
            self.recent_projects.remove(new_dir)
        self.recent_projects.insert(0, new_dir)
        self.recent_projects = self.recent_projects[:RECENT_PROJECTS_MAX]
        self.config.setdefault('user_lists', {})['recent_projects'] = self.recent_projects

        self._save()
        return True

    def remove_recent_project(self, path_to_remove):
        """
        Removes a directory from the recent list. If the removed path is also
        the active directory, the active directory is cleared.
        Returns True if the active directory was cleared, False otherwise.
        """
        cleared_active = False
        if path_to_remove in self.recent_projects:
            self.recent_projects.remove(path_to_remove)
            self.config.setdefault('user_lists', {})['recent_projects'] = self.recent_projects

            if path_to_remove == self.active_directory:
                self.active_directory = ''
                self.config['active_directory'] = ''
                cleared_active = True

            self._save()

        return cleared_active