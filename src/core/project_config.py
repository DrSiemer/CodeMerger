import os
import json
import random
import colorsys
from ..constants import COMPACT_MODE_BG_COLOR

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
                        data = json.loads(content)
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
        if 'project_color' not in data:
            self.project_color = _generate_random_color()
            config_was_updated = True
        else:
            self.project_color = data.get('project_color', COMPACT_MODE_BG_COLOR)

        # Filter out files that no longer exist on disk from both lists
        cleaned_selection = [
            f for f in original_selection
            if os.path.isfile(os.path.join(self.base_dir, f))
        ]
        self.selected_files = cleaned_selection

        cleaned_known_files = [
            f for f in original_known_files
            if os.path.isfile(os.path.join(self.base_dir, f))
        ]
        self.known_files = cleaned_known_files

        files_were_cleaned = len(cleaned_selection) < len(original_selection)
        known_files_were_cleaned = len(cleaned_known_files) < len(original_known_files)


        if files_were_cleaned:
            self.total_tokens = 0 # Invalidate token count if files are missing
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
            "project_name": self.project_name,
            "project_color": self.project_color,
            "expanded_dirs": sorted(list(self.expanded_dirs)),
            "selected_files": self.selected_files,
            "total_tokens": self.total_tokens,
            "intro_text": self.intro_text,
            "outro_text": self.outro_text,
            "known_files": sorted(list(set(self.known_files)))
        }
        with open(self.allcode_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)