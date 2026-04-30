import os
import logging
import threading
from .config_io import read_project_display_info
from .profile_logic import (
    sanitize_profile_name, create_empty_profile_dict,
    create_new_profile, delete_profile, update_known_files_logic
)
from ..constants import COMPACT_MODE_BG_COLOR

log = logging.getLogger("CodeMerger")

class ProjectConfig:
    """
    State orchestrator for project-specific settings stored in .codemerger.
    Delegates procedural persistence and metadata logic to modular components.
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.config_dir = os.path.join(self.base_dir, '.codemerger')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.hi_file = os.path.join(self.config_dir, 'hi.txt')
        self.profiles_dir = os.path.join(self.config_dir, 'profiles')
        self.legacy_allcode_path = os.path.join(self.base_dir, '.allcode')

        self.project_name = os.path.basename(self.base_dir)
        self.project_color = COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.known_files = []

        self.profiles = {}
        self.active_profile_name = "default"
        self._last_mtimes = {}
        self._last_content_hash = None

        self.is_dirty = False
        self._load_successful = False
        self._lock = threading.RLock()

    @staticmethod
    def read_project_display_info(base_dir):
        return read_project_display_info(base_dir)

    def get_active_profile(self):
        if self.active_profile_name not in self.profiles:
            self.profiles[self.active_profile_name] = create_empty_profile_dict()
        return self.profiles[self.active_profile_name]

    # --- Profile Data Proxies ---

    @property
    def visualizer_map(self):
        return self.get_active_profile().get('visualizer_map')

    @visualizer_map.setter
    def visualizer_map(self, value):
        self.get_active_profile()['visualizer_map'] = value

    @property
    def selected_files(self):
        return self.get_active_profile().get('selected_files', [])

    @selected_files.setter
    def selected_files(self, value):
        self.get_active_profile()['selected_files'] = value

    @property
    def total_tokens(self):
        return self.get_active_profile().get('total_tokens', 0)

    @total_tokens.setter
    def total_tokens(self, value):
        self.get_active_profile()['total_tokens'] = value

    @property
    def intro_text(self):
        return self.get_active_profile().get('intro_text', '')

    @intro_text.setter
    def intro_text(self, value):
        self.get_active_profile()['intro_text'] = value

    @property
    def outro_text(self):
        return self.get_active_profile().get('outro_text', '')

    @outro_text.setter
    def outro_text(self, value):
        self.get_active_profile()['outro_text'] = value

    @property
    def expanded_dirs(self):
        return set(self.get_active_profile().get('expanded_dirs', []))

    @expanded_dirs.setter
    def expanded_dirs(self, value):
        self.get_active_profile()['expanded_dirs'] = sorted(list(value))

    @property
    def unknown_files(self):
        return self.get_active_profile().get('unknown_files', [])

    @unknown_files.setter
    def unknown_files(self, value):
        self.get_active_profile()['unknown_files'] = sorted(list(set(value)))

    # --- Delegated Logic ---

    def load(self):
        with self._lock:
            if self.is_dirty: return False
            from .config_persistence import load_project_config
            return load_project_config(self)

    def save(self):
        with self._lock:
            from .config_persistence import save_project_config
            save_project_config(self)

    def has_external_changes(self):
        from .config_persistence import has_external_config_changes
        return has_external_config_changes(self)

    def get_profile_names(self):
        return sorted(list(self.profiles.keys()))

    def create_new_profile(self, name, copy_files, copy_instructions):
        with self._lock:
            return create_new_profile(self, name, copy_files, copy_instructions)

    def delete_profile(self, profile_name_to_delete):
        with self._lock:
            return delete_profile(self, profile_name_to_delete)

    def update_known_files(self, paths, originating_profile_name=None):
        return update_known_files_logic(self, paths, originating_profile_name)