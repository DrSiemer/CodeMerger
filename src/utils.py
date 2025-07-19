import os
import json
from pathlib import Path
from .constants import CONFIG_FILE, FILETYPES_CONFIG, DEFAULT_FILETYPES_CONFIG

def _create_user_filetypes_from_default():
    """
    Reads the bundled default filetypes config and writes it to the
    user's persistent data directory. This is called on first run or
    if the user's config is deleted or corrupted.
    Returns the loaded data.
    """
    try:
        with open(DEFAULT_FILETYPES_CONFIG, 'r') as f:
            default_data = json.load(f)

        # Save this default data as the new user config
        save_filetypes(default_data)
        return default_data
    except (FileNotFoundError, json.JSONDecodeError):
        # If the bundled default is missing or broken, return an empty list
        # to prevent a crash.
        return []


def load_all_filetypes():
    """
    Loads the full list of filetype objects from the user's config file.
    If the user's file doesn't exist, it's created from the bundled default.
    """
    if not os.path.exists(FILETYPES_CONFIG):
        return _create_user_filetypes_from_default()

    try:
        with open(FILETYPES_CONFIG, 'r') as f:
            data = json.load(f)
            # Basic validation
            if isinstance(data, list) and all("ext" in i and "active" in i for i in data):
                return data
            else:
                # The file is malformed, so restore from default
                return _create_user_filetypes_from_default()
    except (json.JSONDecodeError, IOError):
        # The file is corrupted or unreadable, restore from default
        return _create_user_filetypes_from_default()


def save_filetypes(filetypes_list):
    """Saves the list of filetype objects, sorted alphabetically."""
    sorted_list = sorted(filetypes_list, key=lambda item: item['ext'])
    with open(FILETYPES_CONFIG, 'w') as f:
        json.dump(sorted_list, f, indent=2)

def load_active_file_extensions():
    """Loads filetypes and returns a set of currently active extensions."""
    all_types = load_all_filetypes()
    return {item['ext'] for item in all_types if item.get('active', False)}

def load_config():
    """Loads the main application configuration from config.json."""
    if not os.path.exists(CONFIG_FILE):
        return {'active_directory': '', 'recent_directories': []}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {'active_directory': '', 'recent_directories': []}

def save_config(config):
    """Saves the application configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def parse_gitignore(base_dir):
    """Parses a .gitignore file and returns a list of patterns."""
    gitignore_path = os.path.join(base_dir, '.gitignore')
    patterns = []
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            patterns = [
                line.strip() for line in f
                if line.strip() and not line.strip().startswith('#')
            ]
    return patterns

def is_ignored(path, base_dir, gitignore_patterns):
    """Checks if a given path should be ignored based on .gitignore patterns."""
    try:
        base_path = Path(base_dir)
        target_path = Path(path)
        relative_path = target_path.relative_to(base_path)
        for p in gitignore_patterns:
            if p.endswith('/'):
                if not target_path.is_dir():
                    continue
                if relative_path.match(p.rstrip('/')) or relative_path.match('*/' + p.rstrip('/')):
                    return True
            elif p.startswith('/'):
                if relative_path.match(p.lstrip('/')):
                    return True
            else:
                if relative_path.match(p) or relative_path.match('*/' + p):
                    return True
    except ValueError:
        return False
    return False