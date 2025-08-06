import os
from .utils import load_config, save_config
from .constants import RECENT_DIRS_MAX

class AppState:
    """
    Manages the application's persistent state loaded from and saved to config.json
    """
    def __init__(self):
        self.config = load_config()
        self.active_directory = self.config.get('active_directory', '')
        self.recent_dirs = self.config.get('recent_directories', [])
        self.default_editor = self.config.get('default_editor', '')

        self._validate_active_dir()
        self._prune_recent_dirs()

    def _validate_active_dir(self):
        """Checks for existence of the active directory. Resets if not found"""
        if self.active_directory and not os.path.isdir(self.active_directory):
            self.active_directory = ''
            self.config['active_directory'] = ''
            self._save()

    def _prune_recent_dirs(self):
        """Removes non-existent directories from the recent list"""
        initial_count = len(self.recent_dirs)
        self.recent_dirs = [d for d in self.recent_dirs if os.path.isdir(d)]
        if len(self.recent_dirs) != initial_count:
            self.config['recent_directories'] = self.recent_dirs
            self._save()

    def _save(self):
        """Saves the current state back to the config file"""
        save_config(self.config)

    def reload(self):
        """Reloads the configuration from disk, e.g., after settings change"""
        self.config = load_config()
        self.default_editor = self.config.get('default_editor', '')

    def update_active_dir(self, new_dir):
        """Sets a new active directory and updates the recent list"""
        if not new_dir or not os.path.isdir(new_dir):
            return False

        self.active_directory = new_dir
        self.config['active_directory'] = new_dir

        if new_dir in self.recent_dirs:
            self.recent_dirs.remove(new_dir)
        self.recent_dirs.insert(0, new_dir)
        self.recent_dirs = self.recent_dirs[:RECENT_DIRS_MAX]
        self.config['recent_directories'] = self.recent_dirs

        self._save()
        return True

    def remove_recent_directory(self, path_to_remove):
        """Removes a directory from the recent list"""
        if path_to_remove in self.recent_dirs:
            self.recent_dirs.remove(path_to_remove)
            self.config['recent_directories'] = self.recent_dirs
            self._save()