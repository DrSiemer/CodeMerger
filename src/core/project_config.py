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
    """
    Generates a random, visually pleasing hex color string.
    The color is generated in the HSV space with controlled saturation and
    value to avoid overly bright or dark colors, then converted to RGB and hex.
    """
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
        # Using the luminance formula to determine brightness
        # A threshold of 150 is used for better visual comfort, favoring light text.
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return 'dark' if luminance > FONT_LUMINANCE_THRESHOLD else 'light'
    except (ValueError, IndexError):
        return 'light' # Default to light text on error

class ProjectConfig:
    """
    Manages loading and saving the .allcode configuration for a project directory
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.allcode_path = os.path.join(self.base_dir, '.allcode')
        self.project_name = os.path.basename(self.base_dir)
        self.project_color = COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.known_files = []

        self.profiles = {}
        self.active_profile_name = "Default"

    @staticmethod
    def read_project_display_info(base_dir):
        """
        Performs a lightweight read of .allcode just for display purposes,
        avoiding the expensive file system validation of a full load().
        Returns a tuple of (project_name, project_color).
        """
        allcode_path = os.path.join(base_dir, '.allcode')
        project_name = os.path.basename(base_dir) # Default
        project_color = COMPACT_MODE_BG_COLOR # Default

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
            # On error, just return the defaults.
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
            "expanded_dirs": []
        }

    # These properties are for backward compatibility and convenience.
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
        # Return as a set for consistency with old implementation
        return set(self.get_active_profile().get('expanded_dirs', []))

    @expanded_dirs.setter
    def expanded_dirs(self, value):
        # Store as a sorted list for stable JSON output
        self.get_active_profile()['expanded_dirs'] = sorted(list(value))

    def load(self):
        """
        Loads the .allcode config, handles migration from old format, and
        cleans out any references to files that no longer exist.
        Returns True if the file list was modified during the cleaning process.
        """
        data = {}
        config_was_updated = False
        files_were_cleaned_globally = False

        try:
            if os.path.isfile(self.allcode_path):
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
            pass # Treat corrupt/unreadable files as empty

        # --- Load project-level settings ---
        self.project_name = data.get('project_name', os.path.basename(self.base_dir))
        original_known_files = data.get('known_files', [])
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

        # --- Handle Profile Migration and Loading ---
        if 'profiles' in data and isinstance(data['profiles'], dict):
            # New format, load profiles directly
            self.profiles = data.get('profiles', {})
            self.active_profile_name = data.get('active_profile', 'Default')
            if not self.profiles: # Handle empty profiles dict
                self.profiles['Default'] = self._create_empty_profile()
                self.active_profile_name = 'Default'
                config_was_updated = True
            if self.active_profile_name not in self.profiles:
                self.active_profile_name = list(self.profiles.keys())[0]
                config_was_updated = True
        else:
            # Old format, migrate to new structure
            config_was_updated = True
            default_profile = self._create_empty_profile()
            default_profile['intro_text'] = data.get('intro_text', '')
            default_profile['outro_text'] = data.get('outro_text', '')
            default_profile['expanded_dirs'] = sorted(list(set(data.get('expanded_dirs', []))))
            default_profile['selected_files'] = data.get('selected_files', [])
            default_profile['total_tokens'] = data.get('total_tokens', 0)
            self.profiles = {'Default': default_profile}
            self.active_profile_name = 'Default'

        # --- Clean known_files (project-level) ---
        cleaned_known_files = [f for f in original_known_files if os.path.isfile(os.path.join(self.base_dir, f))]
        self.known_files = cleaned_known_files
        if len(cleaned_known_files) < len(original_known_files):
            config_was_updated = True

        # --- Clean selected_files within each profile ---
        for profile_name, profile_data in self.profiles.items():
            files_cleaned_in_profile, profile_updated = self._clean_profile_files(profile_data)
            if files_cleaned_in_profile:
                files_were_cleaned_globally = True
            if profile_updated:
                config_was_updated = True

        if config_was_updated or files_were_cleaned_globally:
            self.save()

        return files_were_cleaned_globally

    def _clean_profile_files(self, profile_data):
        """Cleans file lists for a single profile. Returns (bool_cleaned, bool_updated)."""
        profile_was_updated = False
        original_selection = profile_data.get('selected_files', [])
        is_new_format = original_selection and isinstance(original_selection[0], dict) and 'path' in original_selection[0]

        cleaned_selection = []
        if not is_new_format:
            if original_selection: profile_was_updated = True
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
            for f_info in original_selection:
                if os.path.isfile(os.path.join(self.base_dir, f_info['path'])):
                    if 'tokens' not in f_info or 'lines' not in f_info:
                        profile_was_updated = True
                    cleaned_selection.append(f_info)

        profile_data['selected_files'] = cleaned_selection
        files_were_cleaned = len(cleaned_selection) < len(original_selection)

        if files_were_cleaned:
            profile_data['total_tokens'] = sum(f.get('tokens', 0) for f in cleaned_selection)
            profile_was_updated = True

        # Ensure expanded_dirs is a list for JSON
        if isinstance(profile_data.get('expanded_dirs'), set):
            profile_data['expanded_dirs'] = sorted(list(profile_data['expanded_dirs']))
            profile_was_updated = True

        return files_were_cleaned, profile_was_updated

    def save(self):
        """Saves the configuration to the .allcode file"""
        # Build the dictionary in the desired order to control the JSON output
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

    def get_profile_names(self):
        return sorted(list(self.profiles.keys()))

    def create_new_profile(self, new_name, copy_files, copy_instructions):
        if new_name in self.profiles:
            return False # Profile already exists

        if copy_files or copy_instructions:
            source_profile = self.get_active_profile()
            new_profile = {
                "selected_files": source_profile.get('selected_files', []) if copy_files else [],
                "total_tokens": source_profile.get('total_tokens', 0) if copy_files else 0,
                "intro_text": source_profile.get('intro_text', '') if copy_instructions else '',
                "outro_text": source_profile.get('outro_text', '') if copy_instructions else '',
                "expanded_dirs": source_profile.get('expanded_dirs', []) if copy_files else []
            }
        else:
            new_profile = self._create_empty_profile()

        self.profiles[new_name] = new_profile
        return True

    def delete_profile(self, profile_name_to_delete):
        """Deletes a profile if it exists and is not the default profile."""
        if profile_name_to_delete == "Default" or profile_name_to_delete not in self.profiles:
            return False
        del self.profiles[profile_name_to_delete]
        return True