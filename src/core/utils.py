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
    ADD_ALL_WARNING_THRESHOLD_DEFAULT,
    NEW_FILE_ALERT_THRESHOLD_DEFAULT
)

# Reference holds the lock for the application lifetime
_instance_lock = None

def is_another_instance_running():
    """
    Identifies active instances via Named Mutex on Windows or file lock on POSIX
    Returns False if CM_DEV_MODE environment variable is active
    """
    global _instance_lock

    if os.environ.get('CM_DEV_MODE') == '1':
        return False

    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32

            mutex_name = "Global\\CodeMerger_Instance_Mutex_C06CFB28"

            _instance_lock = kernel32.CreateMutexW(None, False, mutex_name)

            if not _instance_lock:
                return False

            last_error = kernel32.GetLastError()
            if last_error == 183:
                return True

            return False
        except Exception:
            return False
    else:
        try:
            import fcntl

            lock_file_path = os.path.join(PERSISTENT_DATA_DIR, 'app.lock')

            if not os.path.exists(PERSISTENT_DATA_DIR):
                os.makedirs(PERSISTENT_DATA_DIR, exist_ok=True)

            _instance_lock = open(lock_file_path, 'w')

            try:
                fcntl.lockf(_instance_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return False
            except (IOError, BlockingIOError):
                return True
        except Exception:
            return False

def strip_markdown_wrapper(text):
    """
    Removes triple backtick wrappers from a string
    """
    if not text:
        return ""

    clean_text = text.strip()
    if clean_text.startswith("```") and clean_text.endswith("```"):
        first_newline = clean_text.find('\n')
        if first_newline != -1:
            return clean_text[first_newline+1:-3].strip()

    return clean_text

def get_token_count_for_text(text):
    """Calculates the token count for a string"""
    try:
        # Uses cl100k_base encoding for compatibility with gpt-4
        encoding = tiktoken.get_encoding("cl100k_base")
        # Counts all tokens including special sequences
        return len(encoding.encode(text, disallowed_special=()))
    except Exception:
        return -1

def get_file_hash(full_path):
    """Calculates the SHA1 hash of file content"""
    try:
        with open(full_path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except (IOError, OSError):
        return None

def _get_default_config_dict():
    """Returns a dictionary with default application settings"""
    return {
        'active_directory': '',
        'default_editor': '',
        'user_experience': '',
        'default_parent_folder': '',
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
        'new_file_alert_threshold': NEW_FILE_ALERT_THRESHOLD_DEFAULT,
        'show_feedback_on_paste': True,
        'info_mode_active': True,
        'user_lists': {
            'recent_projects': [],
            'filetypes': []
        }
    }

def _create_and_get_default_config():
    """
    Initializes configuration from the default template and saves to disk
    """
    config = _get_default_config_dict()
    try:
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            config['user_lists']['filetypes'] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    save_config(config)
    return config

def load_config():
    """
    Loads configuration using a non-destructive reconciliation strategy
    Merges user values with the default template and applies necessary migrations
    """
    defaults = _get_default_config_dict()

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

    # Key Migrations (Legacy Formats)
    if 'recent_projects' in loaded_config or 'filetypes' in loaded_config or 'recent_directories' in loaded_config:
        migration_occurred = True
        user_lists = loaded_config.setdefault('user_lists', {})
        if 'recent_projects' in loaded_config:
            user_lists['recent_projects'] = loaded_config.pop('recent_projects', [])
        elif 'recent_directories' in loaded_config:
            user_lists['recent_projects'] = loaded_config.pop('recent_directories', [])
        if 'filetypes' in loaded_config:
            user_lists['filetypes'] = loaded_config.pop('filetypes', [])

    if 'line_count_enabled' in loaded_config:
        loaded_config['token_count_enabled'] = loaded_config.pop('line_count_enabled')
        migration_occurred = True

    for old_key in ['default_parent_folder', 'check_for_updates', 'line_count_threshold', 'token_count_threshold']:
        if old_key in loaded_config and old_key != 'default_parent_folder':
            loaded_config.pop(old_key)
            migration_occurred = True

    # Deep Reconciliation
    # Ensures all current keys exist without wiping user settings
    final_config = defaults.copy()

    for key in defaults:
        if key not in loaded_config:
            # Prevents forced saves on boot unless essential configuration is missing
            if key != 'info_mode_active':
                migration_occurred = True

    final_config.update(loaded_config)

    if 'user_lists' in loaded_config:
        final_config['user_lists'] = defaults['user_lists'].copy()
        final_config['user_lists'].update(loaded_config['user_lists'])

    if migration_occurred:
        save_config(final_config)

    return final_config

def save_config(config):
    """
    Saves application configuration to disk
    Operates on a copy to avoid mutating the in-memory object
    """
    export_data = config.copy()

    user_lists_data = export_data.pop('user_lists', {'recent_projects': [], 'filetypes': []})

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
    Synchronizes local filetype settings with the bundled default template
    Returns a list of newly added filetype dictionaries
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

    for ext, local_ft in local_map.items():
        if 'description' not in local_ft or 'default' not in local_ft:
            config_changed = True
            default_ft = default_map.get(ext)
            if default_ft:
                local_ft['description'] = default_ft.get('description', '')
                local_ft['default'] = True
            else:
                local_ft.setdefault('description', '')
                local_ft['default'] = False

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
    config = load_config()
    return config.get('user_lists', {}).get('filetypes', [])

def save_filetypes(filetypes_list):
    config = load_config()
    config.setdefault('user_lists', {})['filetypes'] = filetypes_list
    save_config(config)

def load_active_file_extensions():
    all_types = load_all_filetypes()
    return {item['ext'] for item in all_types if item.get('active', False)}

def parse_gitignore(base_dir):
    """
    Parses all .gitignore files starting from the project root
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

        # Prunes ignored directories in-place to prevent os.walk from entering them
        # Modifying the dirs list in-place prevents os.walk from entering ignored directories, drastically improving full-project scan times
        if gitignore_data:
            dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), base_dir, gitignore_data)]

    return gitignore_data

def is_ignored(path, base_dir, gitignore_data):
    """
    Determines if a path should be ignored based on parsed .gitignore rules
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

            # Matching strategy depends on whether the pattern contains a slash
            contains_slash = '/' in p

            is_dir_only = p.endswith('/')
            if is_dir_only:
                p = p.rstrip('/')

            match = False
            if not contains_slash:
                if any(fnmatch.fnmatch(part, p) for part in relative_path.parts):
                    match = True
            else:
                p_to_match = p.lstrip('/')
                if fnmatch.fnmatch(relative_path_str, p_to_match) or \
                   relative_path_str.startswith(p_to_match + '/'):
                    match = True

            if match and is_dir_only:
                if relative_path_str == p and not target_path.is_dir():
                    match = False

            if match:
                if is_negated:
                    is_ignored_flag = False
                else:
                    is_ignored_flag = True
    return is_ignored_flag

def load_app_version():
    """
    Returns the version string from version.txt
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
        return "v?.?.?"