import os
import json
from pathlib import Path

from .constants import CONFIG_FILE, FILETYPES_CONFIG

# --- Helper Functions ---

def load_file_extensions():
    """Loads the set of target file extensions from the config file."""
    with open(FILETYPES_CONFIG, 'r') as f:
        return set(json.load(f))

def load_config():
    """Loads the main application configuration from config.json."""
    if not os.path.exists(CONFIG_FILE):
        return {'active_directory': '', 'recent_directories': []}

    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Return a default config if the file is corrupted or unreadable
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
                # Handle directory-only patterns
                if not target_path.is_dir():
                    continue
                if relative_path.match(p.rstrip('/')) or relative_path.match('*/' + p.rstrip('/')):
                    return True
            elif p.startswith('/'):
                # Handle patterns anchored to the root
                if relative_path.match(p.lstrip('/')):
                    return True
            else:
                # Handle general patterns
                if relative_path.match(p) or relative_path.match('*/' + p):
                    return True

    except ValueError:
        # This can happen if the path is not inside the base_dir, which means we shouldn't ignore it
        return False

    return False