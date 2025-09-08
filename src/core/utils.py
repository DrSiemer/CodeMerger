import os
import json
import fnmatch
from pathlib import Path
from ..constants import (
    CONFIG_FILE, DEFAULT_FILETYPES_CONFIG, VERSION_FILE,
    DEFAULT_COPY_MERGED_PROMPT, DEFAULT_INTRO_PROMPT, DEFAULT_OUTRO_PROMPT
)

def _create_and_get_default_config():
    """
    Creates a new config object from the default template, saves it to disk,
    and returns it. This is the definitive first-run function
    """
    config = {
        'active_directory': '',
        'recent_projects': [],
        'filetypes': [],
        'default_editor': '',
        'scan_for_secrets': False,
        'last_update_check': None,
        'enable_new_file_check': True,
        'new_file_check_interval': 5,
        'copy_merged_prompt': DEFAULT_COPY_MERGED_PROMPT,
        'default_intro_prompt': DEFAULT_INTRO_PROMPT,
        'default_outro_prompt': DEFAULT_OUTRO_PROMPT
    }
    try:
        # Load the list of filetypes from the bundled template
        with open(DEFAULT_FILETYPES_CONFIG, 'r', encoding='utf-8-sig') as f:
            config['filetypes'] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback in case the template is missing or corrupt
        pass

    # Save the newly created config to disk before returning
    save_config(config)
    return config

def load_config():
    """
    Loads the main application configuration from config.json.
    If the file is missing or corrupt, it's created from the default template
    """
    try:
        # If config file doesn't exist, this will raise FileNotFoundError
        with open(CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
            # If file is empty, this will raise JSONDecodeError
            config = json.load(f)
            # If file is valid but missing keys, handle that too
            if 'filetypes' not in config:
                raise ValueError("Config is missing 'filetypes' key.")
            if 'default_editor' not in config:
                config['default_editor'] = '' # Add missing key for backward compatibility
            if 'recent_directories' in config: # Backward compatibility
                config['recent_projects'] = config.pop('recent_directories')
            if 'scan_for_secrets' not in config:
                config['scan_for_secrets'] = False # Add missing key for backward compatibility
            if 'last_update_check' not in config:
                config['last_update_check'] = None
            if 'check_for_updates' in config:
                del config['check_for_updates'] # Clean up old key if present
            if 'enable_new_file_check' not in config:
                config['enable_new_file_check'] = True
            if 'new_file_check_interval' not in config:
                config['new_file_check_interval'] = 5
            if 'copy_merged_prompt' not in config:
                config['copy_merged_prompt'] = DEFAULT_COPY_MERGED_PROMPT
            if 'default_intro_prompt' not in config:
                config['default_intro_prompt'] = DEFAULT_INTRO_PROMPT
            if 'default_outro_prompt' not in config:
                config['default_outro_prompt'] = DEFAULT_OUTRO_PROMPT
            return config
    except (FileNotFoundError, json.JSONDecodeError, ValueError, IOError):
        # Any failure in reading the config results in creating a new one
        return _create_and_get_default_config()

def save_config(config):
    """Saves the complete application configuration object to config.json"""
    # Ensure filetypes are sorted alphabetically for consistency
    if 'filetypes' in config and isinstance(config.get('filetypes'), list):
        config['filetypes'].sort(key=lambda item: item['ext'])

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def load_all_filetypes():
    """Helper function to load just the filetypes list from the main config"""
    config = load_config()
    return config.get('filetypes', [])

def save_filetypes(filetypes_list):
    """
    Loads the current config, updates the filetypes list, and saves it back
    """
    config = load_config()
    config['filetypes'] = filetypes_list
    save_config(config)

def load_active_file_extensions():
    """Loads active filetypes from the config and returns them as a set"""
    all_types = load_all_filetypes()
    return {item['ext'] for item in all_types if item.get('active', False)}

def parse_gitignore(base_dir):
    """
    Parses all .gitignore files from the base directory downwards.
    Returns a list of tuples, where each tuple contains the Path object for the
    .gitignore's directory and a list of its patterns.
    """
    gitignore_data = []
    for root, dirs, files in os.walk(base_dir, topdown=True):
        if '.git' in dirs:
            dirs.remove('.git')

        if '.gitignore' in files:
            gitignore_path = os.path.join(root, '.gitignore')
            try:
                with open(gitignore_path, 'r', encoding='utf-8-sig') as f:
                    patterns = [
                        line.strip() for line in f
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    if patterns:
                        gitignore_data.append((Path(root), patterns))
            except (IOError, OSError):
                pass
    return gitignore_data

def is_ignored(path, base_dir, gitignore_data):
    """
    Checks if a given path should be ignored based on all found .gitignore files,
    respecting the location and rules of each file.
    """
    target_path = Path(path)
    if '.git' in target_path.parts:
        return True

    is_ignored_flag = False
    for gitignore_dir, patterns in gitignore_data:
        try:
            relative_path_str = target_path.relative_to(gitignore_dir).as_posix()
        except ValueError:
            continue # Path is not under this .gitignore's control

        for p in patterns:
            is_negated = p.startswith('!')
            if is_negated:
                p = p[1:]

            is_dir_only = p.endswith('/')
            if is_dir_only:
                p = p.rstrip('/')

            current_match = False
            # Patterns without slashes match any path component.
            if '/' not in p:
                if any(fnmatch.fnmatch(part, p) for part in Path(relative_path_str).parts):
                    current_match = True
            # Patterns with slashes are matched against the full relative path.
            else:
                if fnmatch.fnmatch(relative_path_str, p):
                    current_match = True

            if current_match:
                # For directory-only patterns, ensure we're matching a directory
                # or a file within that directory.
                if is_dir_only and not (relative_path_str == p or relative_path_str.startswith(p + '/')):
                    current_match = False

            if current_match:
                if is_negated:
                    is_ignored_flag = False
                else:
                    is_ignored_flag = True

    return is_ignored_flag


def load_app_version():
    """
    Reads the version from version.txt and returns it as a formatted string.
    Returns a default string if the file is not found or is malformed
    """
    try:
        version_data = {}
        with open(VERSION_FILE, 'r', encoding='utf-8-sig') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    version_data[key.strip().lower()] = value.strip()

        major = version_data.get('major', '?')
        minor = version_data.get('minor', '?')
        revision = version_data.get('revision', '?')

        return f"v{major}.{minor}.{revision}"

    except (FileNotFoundError, IndexError):
        # Handle case where file doesn't exist or line split fails
        return "v?.?.?"