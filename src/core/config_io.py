import os
import json
import random
import re
import colorsys
import tempfile
import time
import sys
from ..constants import COMPACT_MODE_BG_COLOR, CODEMERGER_TEMP_PREFIX
from .utils import calculate_font_color

def generate_random_color():
    """Generates a random visually pleasing hex color string"""
    hue = random.random()
    saturation = random.uniform(0.5, 0.7)
    value = random.uniform(0.6, 0.8)
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    r_int, g_int, b_int = int(r * 255), int(g * 255), int(b * 255)
    return f"#{r_int:02x}{g_int:02x}{b_int:02x}"

def ensure_dir_hidden(dir_path):
    """Sets the hidden attribute on a directory (Windows only)"""
    if sys.platform == "win32" and os.path.exists(dir_path):
        try:
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            attrs = ctypes.windll.kernel32.GetFileAttributesW(dir_path)
            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                ctypes.windll.kernel32.SetFileAttributesW(dir_path, attrs | FILE_ATTRIBUTE_HIDDEN)
        except Exception: pass

def write_hi_text(hi_file_path):
    """Creates a helpful hi.txt file in the .codemerger root."""
    content = """Hi there! This folder contains the configuration and session data for CodeMerger.

CodeMerger helps you bundle your project code for language models while maintaining full custody of your context.

Folder Structure:
- config.json: Project metadata (name, color, and active profile pointer).
- profiles/: Individual directories for your project profiles.
- profiles/[Name]/selection.json: The list and order of files included in your context.
- profiles/[Name]/instructions.json: Your custom Intro and Outro prompts.
- profiles/[Name]/files.json: Profile-specific file states and token counts.

These files are designed to be part of your repository.

Official Repository: https://github.com/DrSiemer/CodeMerger/
"""
    try:
        with open(hi_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception: pass

def atomic_write(target_path, data):
    """Writes JSON data to a file using an atomic replace pattern with hidden-attribute awareness."""
    fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(target_path), prefix=CODEMERGER_TEMP_PREFIX)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        max_retries = 5
        is_windows = sys.platform == "win32"
        was_hidden = False

        for attempt in range(max_retries):
            try:
                if is_windows and os.path.exists(target_path):
                    import ctypes
                    FILE_ATTRIBUTE_HIDDEN = 0x02
                    attrs = ctypes.windll.kernel32.GetFileAttributesW(target_path)
                    if attrs != -1 and (attrs & FILE_ATTRIBUTE_HIDDEN):
                        was_hidden = True
                        ctypes.windll.kernel32.SetFileAttributesW(target_path, attrs & ~FILE_ATTRIBUTE_HIDDEN)

                os.replace(temp_path, target_path)
                temp_path = None

                if is_windows and was_hidden:
                    attrs = ctypes.windll.kernel32.GetFileAttributesW(target_path)
                    if attrs != -1:
                        ctypes.windll.kernel32.SetFileAttributesW(target_path, attrs | FILE_ATTRIBUTE_HIDDEN)
                break
            except PermissionError:
                if attempt == max_retries - 1: raise
                time.sleep(0.1)
    finally:
        if temp_path and os.path.exists(temp_path):
            try: os.remove(temp_path)
            except Exception: pass

def read_project_display_info(base_dir):
    """Quickly extracts project metadata for UI display without loading the full config object."""
    config_file = os.path.join(base_dir, '.codemerger', 'config.json')
    legacy_path = os.path.join(base_dir, '.allcode')
    project_name = os.path.basename(base_dir)
    project_color = COMPACT_MODE_BG_COLOR

    target_file = config_file if os.path.isfile(config_file) else legacy_path
    if not os.path.isfile(target_file):
        return project_name, project_color

    try:
        with open(target_file, 'r', encoding='utf-8-sig') as f:
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