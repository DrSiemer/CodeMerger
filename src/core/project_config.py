import os
import json
import random
import re
import colorsys
import hashlib
from ..constants import COMPACT_MODE_BG_COLOR
from .merger import recalculate_token_count

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
        return 'dark' if luminance > 150 else 'light'
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
        self.selected_files = []
        self.known_files = []
        self.expanded_dirs = set()
        self.total_tokens = 0
        self.intro_text = ''
        self.outro_text = ''
        self.project_color = COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'

    def load(self):
        """
        Loads the .allcode config, and crucially, cleans out any references
        to files that no longer exist on the filesystem. Returns True if
        the file list was modified during the cleaning process
        """
        data = {}
        config_was_updated = False
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

        self.project_name = data.get('project_name', os.path.basename(self.base_dir))
        self.intro_text = data.get('intro_text', '')
        self.outro_text = data.get('outro_text', '')
        self.expanded_dirs = set(data.get('expanded_dirs', []))
        original_selection = data.get('selected_files', [])
        original_known_files = data.get('known_files', [])

        if 'project_name' not in data:
            config_was_updated = True

        color_value = data.get('project_color')
        # Validate color value; if missing, invalid, or not a hex string, generate a new one
        if not color_value or not isinstance(color_value, str) or not re.match(r'^#[0-9a-fA-F]{6}$', color_value):
            self.project_color = _generate_random_color()
            config_was_updated = True
        else:
            self.project_color = color_value

        # --- Calculate font color if it's not set ---
        font_color_value = data.get('project_font_color')
        if not font_color_value or font_color_value not in ['light', 'dark']:
            self.project_font_color = _calculate_font_color(self.project_color)
            config_was_updated = True
        else:
            self.project_font_color = font_color_value

        # --- Process selected_files, handling both old and new formats ---
        cleaned_selection = []
        # Check if the list is not empty and the first item is a dictionary with 'path'
        is_new_format = original_selection and isinstance(original_selection[0], dict) and 'path' in original_selection[0]

        if not is_new_format:
            # Old format (list of strings): convert to the new format
            if original_selection: config_was_updated = True
            for f_path in original_selection:
                full_path = os.path.join(self.base_dir, f_path)
                if os.path.isfile(full_path):
                    try:
                        mtime = os.path.getmtime(full_path)
                        file_hash = _get_file_hash(full_path)
                        cleaned_selection.append({'path': f_path, 'mtime': mtime, 'hash': file_hash})
                    except OSError:
                        continue # Skip files that can't be accessed
        else:
            # New format (list of dicts): filter out non-existent files
            cleaned_selection = [
                f_info for f_info in original_selection
                if os.path.isfile(os.path.join(self.base_dir, f_info['path']))
            ]
        self.selected_files = cleaned_selection
        files_were_cleaned = len(cleaned_selection) < len(original_selection)

        cleaned_known_files = [
            f for f in original_known_files
            if os.path.isfile(os.path.join(self.base_dir, f))
        ]
        self.known_files = cleaned_known_files
        known_files_were_cleaned = len(cleaned_known_files) < len(original_known_files)

        if files_were_cleaned:
            if len(self.selected_files) > 100:
                self.total_tokens = 0
            else:
                self.total_tokens = recalculate_token_count(self.base_dir, self.selected_files)
            config_was_updated = True
        else:
            # The file list is intact, so the cached token count is trustworthy
            self.total_tokens = data.get('total_tokens', 0)

        if known_files_were_cleaned:
            config_was_updated = True

        if config_was_updated:
            self.save()

        return files_were_cleaned

    def save(self):
        """Saves the configuration to the .allcode file"""
        # Build the dictionary in the desired order to control the JSON output
        final_data = {
            "_info": "For information about this file, see: https://github.com/DrSiemer/CodeMerger/",
            "project_name": self.project_name,
            "project_color": self.project_color,
            "project_font_color": self.project_font_color,
            "expanded_dirs": sorted(list(self.expanded_dirs)),
            "selected_files": self.selected_files,
            "total_tokens": self.total_tokens,
            "intro_text": self.intro_text,
            "outro_text": self.outro_text,
            "known_files": sorted(list(set(self.known_files)))
        }
        with open(self.allcode_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)