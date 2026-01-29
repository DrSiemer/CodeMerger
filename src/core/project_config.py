import os
import json
import random
import re
import colorsys
import hashlib
from ..constants import COMPACT_MODE_BG_COLOR, FONT_LUMINANCE_THRESHOLD
from .utils import get_token_count_for_text

def _get_file_hash(full_path):
    """Calculates the SHA1 hash of a file's content."""
    try:
        with open(full_path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except (IOError, OSError):
        return None

def _generate_random_color():
    """Generates a random, visually pleasing hex color string."""
    hue = random.random()
    saturation = random.uniform(0.5, 0.7)
    value = random.uniform(0.6, 0.8)
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    r_int, g_int, b_int = int(r * 255), int(g * 255), int(b * 255)
    return f"#{r_int:02x}{g_int:02x}{b_int:02x}"

def _calculate_font_color(hex_color):
    """Determines if light or dark text should be used for a given hex background color."""
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return 'dark' if luminance > FONT_LUMINANCE_THRESHOLD else 'light'
    except (ValueError, IndexError):
        return 'light'

class ProjectConfig:
    """
    Manages loading and saving the .allcode configuration for a project directory.
    Tracking for 'New Files' is now profile-specific via the 'unknown_files' list,
    while 'known_files' remains global to the project to avoid duplication.
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.allcode_path = os.path.join(self.base_dir, '.allcode')
        self.project_name = os.path.basename(self.base_dir)
        self.project_color = COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.known_files = [] # Global to project

        self.profiles = {}
        self.active_profile_name = "Default"
        self._last_mtime = 0

    @staticmethod
    def read_project_display_info(base_dir):
        allcode_path = os.path.join(base_dir, '.allcode')
        project_name = os.path.basename(base_dir)
        project_color = COMPACT_MODE_BG_COLOR

        if not os.path.isfile(allcode_path):
            return project_name, project_color

        try:
            with open(allcode_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if not content: return project_name, project_color
                data = json.loads(content)
                project_name = data.get('project_name', project_name)
                color_value = data.get('project_color')
                if color_value and isinstance(color_value, str) and re.match(r'^#[0-9a-fA-F]{6}$', color_value):
                        project_color = color_value
        except (json.JSONDecodeError, IOError):
            pass

        return project_name, project_color

    def get_active_profile(self):
        """Returns the dictionary for the currently active profile."""
        if self.active_profile_name not in self.profiles:
            self.profiles[self.active_profile_name] = self._create_empty_profile()
        return self.profiles[self.active_profile_name]

    def _create_empty_profile(self):
        """Returns a new, empty profile dictionary."""
        return {
            "selected_files": [],
            "total_tokens": 0,
            "intro_text": "",
            "outro_text": "",
            "expanded_dirs": [],
            "unknown_files": [] # Files that haven't been 'seen' by this profile yet
        }

    # Redirect properties to the active profile
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

    def load(self):
        data = {}
        config_was_updated = False
        files_were_cleaned_globally = False

        try:
            if os.path.isfile(self.allcode_path):
                # Capture mtime immediately before reading to track this version
                self._last_mtime = os.path.getmtime(self.allcode_path)
                with open(self.allcode_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    if content:
                        try:
                            data = json.loads(content)
                        except json.JSONDecodeError:
                            json_start_index = content.find('{')
                            if json_start_index != -1:
                                json_content = content[json_start_index:]
                                data = json.loads(json_content)
                                config_was_updated = True
        except (json.JSONDecodeError, IOError):
            pass

        self.project_name = data.get('project_name', os.path.basename(self.base_dir))
        color_value = data.get('project_color')
        font_color_value = data.get('project_font_color')

        if 'project_name' not in data: config_was_updated = True
        if not color_value or not isinstance(color_value, str) or not re.match(r'^#[0-9a-fA-F]{6}$', color_value):
            self.project_color = _generate_random_color()
            config_was_updated = True
        else:
            self.project_color = color_value

        if not font_color_value or font_color_value not in ['light', 'dark']:
            self.project_font_color = _calculate_font_color(self.project_color)
            config_was_updated = True
        else:
            self.project_font_color = font_color_value

        # Handle Profile Loading
        if 'profiles' in data and isinstance(data['profiles'], dict):
            self.profiles = data.get('profiles', {})
            self.active_profile_name = data.get('active_profile', 'Default')
            if not self.profiles:
                self.profiles['Default'] = self._create_empty_profile()
                self.active_profile_name = 'Default'
                config_was_updated = True
        else:
            # Migration from legacy flat format
            config_was_updated = True
            default_profile = self._create_empty_profile()
            default_profile['intro_text'] = data.get('intro_text', '')
            default_profile['outro_text'] = data.get('outro_text', '')
            default_profile['expanded_dirs'] = sorted(list(set(data.get('expanded_dirs', []))))
            default_profile['selected_files'] = data.get('selected_files', [])
            default_profile['total_tokens'] = data.get('total_tokens', 0)
            self.profiles = {'Default': default_profile}
            self.active_profile_name = 'Default'

        # Global Known Files Migration/Extraction
        all_found_known = set(data.get('known_files', []))
        for p_data in self.profiles.values():
            if 'known_files' in p_data:
                all_found_known.update(p_data.pop('known_files', []))
                config_was_updated = True
            # Ensure every profile has an 'unknown_files' list
            if 'unknown_files' not in p_data:
                p_data['unknown_files'] = []
                config_was_updated = True

        # Load known_files (project-level) WITHOUT strict existence check
        # We rely on FileMonitor to clean up deleted files later.
        # This prevents mass deletion of known files if the drive/folder is temporarily inaccessible during load.
        self.known_files = sorted(list(all_found_known))

        # Clean selected_files and unknown_files within each profile
        for profile_name, profile_data in self.profiles.items():
            # Standardize unknown_files list
            orig_unknown = set(profile_data.get('unknown_files', []))
            profile_data['unknown_files'] = sorted(list(orig_unknown))

            files_cleaned_in_profile, profile_updated = self._clean_profile_files(profile_data)
            if files_cleaned_in_profile:
                files_were_cleaned_globally = True
            if profile_updated:
                config_was_updated = True

        if config_was_updated or files_were_cleaned_globally:
            self.save()

        return files_were_cleaned_globally

    def _clean_profile_files(self, profile_data):
        profile_was_updated = False
        original_selection = profile_data.get('selected_files', [])
        is_new_format = original_selection and isinstance(original_selection[0], dict) and 'path' in original_selection[0]

        cleaned_selection = []
        if not is_new_format:
            if original_selection: profile_was_updated = True
            # Legacy migration MUST read files to calculate initial tokens/hash.
            # If files are missing during migration, they are skipped. This is acceptable for legacy upgrade.
            for f_path in original_selection:
                full_path = os.path.join(self.base_dir, f_path)
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
                        mtime = os.path.getmtime(full_path)
                        file_hash = _get_file_hash(full_path)
                        tokens = get_token_count_for_text(content)
                        lines = content.count('\n') + 1
                        cleaned_selection.append({'path': f_path, 'mtime': mtime, 'hash': file_hash, 'tokens': tokens, 'lines': lines})
                    except OSError: continue
        else:
            # Standard load: Do NOT check for file existence here.
            # Preserving entries allows the UI to handle "missing" files gracefully or
            # recover them if they reappear (network share glitches, git switching).
            for f_info in original_selection:
                if 'tokens' not in f_info or 'lines' not in f_info:
                    profile_was_updated = True
                cleaned_selection.append(f_info)

        profile_data['selected_files'] = cleaned_selection
        files_were_cleaned = len(cleaned_selection) < len(original_selection)

        if files_were_cleaned:
            profile_data['total_tokens'] = sum(f.get('tokens', 0) for f in cleaned_selection)
            profile_was_updated = True

        return files_were_cleaned, profile_was_updated

    def save(self):
        """Saves configuration with known_files at the root."""
        final_data = {
            "_info": "For information about this file, see: https://github.com/DrSiemer/CodeMerger/",
            "project_name": self.project_name,
            "project_color": self.project_color,
            "project_font_color": self.project_font_color,
            "active_profile": self.active_profile_name,
            "profiles": self.profiles,
            "known_files": sorted(list(set(self.known_files)))
        }
        with open(self.allcode_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)

        # Update timestamp to prevent detecting self-save as an external change
        if os.path.isfile(self.allcode_path):
            self._last_mtime = os.path.getmtime(self.allcode_path)

    def has_external_changes(self):
        """Checks if the .allcode file has been modified on disk since last load/save."""
        if not os.path.isfile(self.allcode_path):
            return False
        try:
            return os.path.getmtime(self.allcode_path) != self._last_mtime
        except OSError:
            return False

    def get_profile_names(self):
        return sorted(list(self.profiles.keys()))

    def create_new_profile(self, new_name, copy_files, copy_instructions):
        if new_name in self.profiles:
            return False

        if copy_files or copy_instructions:
            source_profile = self.get_active_profile()
            # Deep copy the file selection to prevent shared memory references
            new_profile = {
                "selected_files": [dict(f) for f in source_profile.get('selected_files', [])] if copy_files else [],
                "total_tokens": source_profile.get('total_tokens', 0) if copy_files else 0,
                "intro_text": source_profile.get('intro_text', '') if copy_instructions else '',
                "outro_text": source_profile.get('outro_text', '') if copy_instructions else '',
                "expanded_dirs": source_profile.get('expanded_dirs', [])[:] if copy_files else [],
                "unknown_files": source_profile.get('unknown_files', [])[:] if copy_files else []
            }
        else:
            new_profile = self._create_empty_profile()

        self.profiles[new_name] = new_profile
        return True

    def delete_profile(self, profile_name_to_delete):
        if profile_name_to_delete == "Default" or profile_name_to_delete not in self.profiles:
            return False
        del self.profiles[profile_name_to_delete]
        return True