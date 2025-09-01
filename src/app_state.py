import os
from datetime import datetime
from .core.utils import load_config, save_config
from .constants import RECENT_PROJECTS_MAX
from .core.registry import get_setting

class AppState:
    """
    Manages the application's persistent state loaded from and saved to config.json
    """
    def __init__(self):
        self.config = load_config()
        self.active_directory = self.config.get('active_directory', '')
        self.recent_projects = self.config.get('recent_projects', [])
        self.default_editor = self.config.get('default_editor', '')
        self.scan_for_secrets = self.config.get('scan_for_secrets', False)
        self.check_for_updates = get_setting('AutomaticUpdates', True)
        self.last_update_check = self.config.get('last_update_check', None)

        self._validate_active_dir()
        self._prune_recent_projects()

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
            self.config['recent_projects'] = self.recent_projects
            self._save()

    def _save(self):
        """Saves the current state back to the config file"""
        save_config(self.config)

    def reload(self):
        """Reloads the configuration from disk, e.g., after settings change"""
        self.config = load_config()
        self.default_editor = self.config.get('default_editor', '')
        self.scan_for_secrets = self.config.get('scan_for_secrets', False)
        # Reload from registry as well
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
        self.config['recent_projects'] = self.recent_projects

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
            self.config['recent_projects'] = self.recent_projects

            if path_to_remove == self.active_directory:
                self.active_directory = ''
                self.config['active_directory'] = ''
                cleared_active = True

            self._save()

        return cleared_active