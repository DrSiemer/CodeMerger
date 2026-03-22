import os
import json
import fnmatch
import hashlib
import tiktoken
import sys
from pathlib import Path
from ..core.paths import (
    CONFIG_FILE_PATH, DEFAULT_FILETYPES_CONFIG_PATH, VERSION_FILE_PATH, PERSISTENT_DATA_DIR
)
from ..core.prompts import (
    DEFAULT_COPY_MERGED_PROMPT, DEFAULT_INTRO_PROMPT, DEFAULT_OUTRO_PROMPT
)
from ..constants import (
    TOKEN_COUNT_ENABLED_DEFAULT,
    ADD_ALL_WARNING_THRESHOLD_DEFAULT
)

# Global reference to hold the lock/mutex for the lifetime of the application
_instance_lock = None

def is_another_instance_running():
    """
    Checks if another instance of CodeMerger is currently running.
    Uses a Named Mutex on Windows and a file lock on POSIX systems.
    This is significantly faster than iterating through process lists.
    Returns False if the CM_DEV_MODE environment variable is set.
    """
    global _instance_lock

    # Skip check if launched via go.bat (dev mode)
    if os.environ.get('CM_DEV_MODE') == '1':
        return False

    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32

            # Unique name for the mutex
            mutex_name = "Global\\CodeMerger_Instance_Mutex_C06CFB28"

            # CreateMutexW returns a handle. If it fails, it returns 0.
            # (security_attributes, initial_owner, name)
            _instance_lock = kernel32.CreateMutexW(None, False, mutex_name)

            if not _instance_lock:
                return False

            # Check if the mutex already existed (ERROR_ALREADY_EXISTS = 183)
            last_error = kernel32.GetLastError()
            if last_error == 183:
                return True

            return False
        except Exception:
            # Fallback if ctypes fails
            return False
    else:
        # POSIX implementation using fcntl file locking
        try:
            import fcntl

            lock_file_path = os.path.join(PERSISTENT_DATA_DIR, 'app.lock')

            # Ensure directory exists
            if not os.path.exists(PERSISTENT_DATA_DIR):
                os.makedirs(PERSISTENT_DATA_DIR, exist_ok=True)

            # Create/Open the lock file
            _instance_lock = open(lock_file_path, 'w')

            try:
                # Try to acquire an exclusive lock without blocking (LOCK_NB)
                fcntl.lockf(_instance_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return False
            except (IOError, BlockingIOError):
                # If we get an error, the file is already locked by another instance
                return True
        except Exception:
            return False

def strip_markdown_wrapper(text):
    """
    Removes outer markdown code block wrappers (triple backticks) from a string.
    Example: converts "```markdown\n# Title\n```" to "# Title".
    """
    if not text:
        return ""

    clean_text = text.strip()
    if clean_text.startswith("```") and clean_text.endswith("```"):
        # Find the end of the opening ``` line (e.g., ```markdown or just ```)
        first_newline = clean_text.find('\n')
        if first_newline != -1:
            # Return content between the first newline and the last 3 characters
            return clean_text[first_newline+1:-3].strip()

    return clean_text

def get_token_count_for_text(text):
    """Calculates the token count for a given string."""
    try:
        # cl100k_base is the encoding for gpt-4, gpt-3.5-turbo, and text-embedding-ada-002
        encoding = tiktoken.get_encoding("cl100k_base")
        # Using disallowed_special=() to count all tokens without errors
        return len(encoding.encode(text, disallowed_special=()))
    except Exception:
        # If tiktoken fails for any reason, return -1 to indicate an error
        return -1

def get_file_hash(full_path):
    """Calculates the SHA1 hash of a file's content."""
    try:
        with open(full_path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except (IOError, OSError):
        return None

def _get_default_config_dict():
    """Returns a fresh dictionary with all default application settings."""
    return {
        'active_directory': '',
        'default_editor': '',
        'user_experience': '',
        'scan_for_secrets': False,
        'last_update_check': None,
        'enable_new_file_check': True,
        'new_file_check_interval': 5,
        'copy_merged_prompt': DEFAULT_COPY_MERGED_PROMPT,
        'default_intro_prompt': DEFAULT_INTRO_PROMPT,
        'default_outro_prompt': DEFAULT_OUTRO_PROMPT,
        'token_count_enabled': TOKEN_COUNT_ENABLED_DEFAULT,
        'token_limit': 0,
        'enable_compact_mode_on_minimize': True,
        'add_all_warning_threshold': ADD_ALL_WARNING_THRESHOLD_DEFAULT,
        'show_feedback_on_paste': True,
        'info_mode_active': True,
        'user_lists': {
            'recent_projects': [],
            'filetypes': []
        }
    }

def _create_and_get_default_config():
    """
    Creates a new config object from the default template, saves it to disk,
    and returns it. This is the definitive first-run function.
    """
    config = _get_default_config_dict()
    try:
        # Load the list of filetypes from the bundled template
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            config['user_lists']['filetypes'] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    save_config(config)
    return config

def load_config():
    """
    Loads the main application configuration using a non-destructive reconciliation strategy.
    If the file exists, it merges user values with the default template to ensure all keys exist.
    If migrations are needed, they are applied and the result is saved back to disk.
    """
    defaults = _get_default_config_dict()

    # Pre-populate default filetypes in the template
    try:
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            defaults['user_lists']['filetypes'] = json.load(f)
    except Exception:
        pass

    if not os.path.exists(CONFIG_FILE_PATH):
        return _create_and_get_default_config()

    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            loaded_config = json.load(f)
    except (json.JSONDecodeError, IOError):
        return _create_and_get_default_config()

    migration_occurred = False

    # --- 1. Key Migrations (Legacy Formats) ---
    # Handle the transition from flat keys to nested 'user_lists'
    if 'recent_projects' in loaded_config or 'filetypes' in loaded_config or 'recent_directories' in loaded_config:
        migration_occurred = True
        user_lists = loaded_config.setdefault('user_lists', {})
        if 'recent_projects' in loaded_config:
            user_lists['recent_projects'] = loaded_config.pop('recent_projects', [])
        elif 'recent_directories' in loaded_config:
            user_lists['recent_projects'] = loaded_config.pop('recent_directories', [])
        if 'filetypes' in loaded_config:
            user_lists['filetypes'] = loaded_config.pop('filetypes', [])

    # Handle singular renames
    if 'line_count_enabled' in loaded_config:
        loaded_config['token_count_enabled'] = loaded_config.pop('line_count_enabled')
        migration_occurred = True

    # Cleanup unused legacy keys
    for old_key in ['default_parent_folder', 'check_for_updates', 'line_count_threshold', 'token_count_threshold']:
        if old_key in loaded_config:
            loaded_config.pop(old_key)
            migration_occurred = True

    # --- 2. Deep Reconciliation ---
    # Merge the loaded config into the defaults. This ensures all keys exist
    # (including newly added features) without wiping old settings.
    final_config = defaults.copy()

    # Check for missing top-level keys before update to determine if we should save
    for key in defaults:
        if key not in loaded_config:
            # We don't mark migration_occurred for 'info_mode_active' if it's the only thing,
            # to avoid forced saves on every single boot for existing users unless necessary.
            if key != 'info_mode_active':
                migration_occurred = True

    final_config.update(loaded_config)

    # Handle nested user_lists merge specifically to avoid overwriting the whole group
    if 'user_lists' in loaded_config:
        final_config['user_lists'] = defaults['user_lists'].copy()
        final_config['user_lists'].update(loaded_config['user_lists'])

    if migration_occurred:
        save_config(final_config)

    return final_config

def save_config(config):
    """
    Saves the application configuration to config.json.
    Operates on a copy to avoid mutating the configuration object in memory.
    """
    # Create a local copy to avoid side effects (like the 'pop' bug)
    export_data = config.copy()

    user_lists_data = export_data.pop('user_lists', {'recent_projects': [], 'filetypes': []})

    # Ensure filetypes are sorted alphabetically for consistency
    if isinstance(user_lists_data.get('filetypes'), list):
        user_lists_data['filetypes'].sort(key=lambda item: item['ext'])

    export_data['user_lists'] = user_lists_data

    try:
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    except IOError as e:
        print(f"Error saving configuration: {e}")

def update_and_get_new_filetypes():
    """
    Checks for new default filetypes and updates the format of existing ones.
    Returns a list of newly added filetype dictionaries.
    """
    config = load_config()
    user_lists = config.setdefault('user_lists', {})
    local_filetypes = user_lists.get('filetypes', [])

    try:
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            default_filetypes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    local_map = {ft['ext']: ft for ft in local_filetypes}
    default_map = {ft['ext']: ft for ft in default_filetypes}

    newly_added = []
    config_changed = False

    # 1. Update existing local filetypes to the new format
    for ext, local_ft in local_map.items():
        if 'description' not in local_ft or 'default' not in local_ft:
            config_changed = True
            default_ft = default_map.get(ext)
            if default_ft: # This is a default filetype
                local_ft['description'] = default_ft.get('description', '')
                local_ft['default'] = True
            else: # This is a custom user-added filetype
                local_ft.setdefault('description', '')
                local_ft['default'] = False

    # 2. Add new default filetypes that are not in the local list
    for ext, default_ft in default_map.items():
        if ext not in local_map:
            config_changed = True
            local_filetypes.append(default_ft.copy())
            newly_added.append(default_ft.copy())

    if config_changed:
        user_lists['filetypes'] = local_filetypes
        save_config(config)

    return newly_added

def load_all_filetypes():
    """Helper function to load just the filetypes list from the main config"""
    config = load_config()
    return config.get('user_lists', {}).get('filetypes', [])

def save_filetypes(filetypes_list):
    """
    Loads the current config, updates the filetypes list, and saves it back
    """
    config = load_config()
    config.setdefault('user_lists', {})['filetypes'] = filetypes_list
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

        # Prune ignored directories to stop os.walk from entering them.
        # This prevents scanning massive folders like node_modules.
        if gitignore_data:
            dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), base_dir, gitignore_data)]

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
            relative_path = target_path.relative_to(gitignore_dir)
        except ValueError:
            continue

        relative_path_str = relative_path.as_posix()

        for p_orig in patterns:
            p = p_orig.strip()
            if not p: continue

            is_negated = p.startswith('!')
            if is_negated:
                p = p[1:]

            # The matching strategy depends on whether the pattern contains a slash.
            # This check must happen before stripping a trailing slash.
            contains_slash = '/' in p

            is_dir_only = p.endswith('/')
            if is_dir_only:
                p = p.rstrip('/')

            match = False
            if not contains_slash:
                # If no slash, match against any component of the path.
                if any(fnmatch.fnmatch(part, p) for part in relative_path.parts):
                    match = True
            else:
                # If there is a slash, it's a path match relative to the .gitignore location.
                # A leading slash in the original pattern also makes it a path match.
                p_to_match = p.lstrip('/')
                if fnmatch.fnmatch(relative_path_str, p_to_match) or \
                   relative_path_str.startswith(p_to_match + '/'):
                    match = True

            # Post-match checks for directory-only patterns
            if match and is_dir_only:
                # If the pattern was directory-only, it cannot match a file of the same name.
                if relative_path_str == p and not target_path.is_dir():
                    match = False

            # Update the final ignore status based on the match.
            # Later rules in the same file override earlier ones.
            if match:
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
        with open(VERSION_FILE_PATH, 'r', encoding='utf-8-sig') as f:
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