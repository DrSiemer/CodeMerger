import os
import json
import fnmatch
import hashlib
import tiktoken
import sys
import ctypes
import tempfile
import time
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
    NEW_FILE_ALERT_THRESHOLD_DEFAULT,
    FONT_LUMINANCE_THRESHOLD
)

# Reference holds the lock for the application lifetime
_instance_lock = None

# Global Tiktoken instance to prevent re-initialization during batch operations
_tiktoken_encoding = None

def is_dev_mode():
    """Centralized check for development environment."""
    return "--dev" in sys.argv or os.environ.get('CM_DEV_MODE') == '1'

def is_another_instance_running():
    # Identifies active instances via Named Mutex on Windows for environment isolation
    global _instance_lock

    try:
        kernel32 = ctypes.windll.kernel32

        suffix = "_DEV" if is_dev_mode() else ""
        mutex_name = f"Global\\CodeMerger_Instance_Mutex_C06CFB28{suffix}"

        _instance_lock = kernel32.CreateMutexW(None, False, mutex_name)

        if not _instance_lock:
            return False

        last_error = kernel32.GetLastError()
        if last_error == 183:
            return True

        return False
    except Exception:
        return False

def strip_markdown_wrapper(text):
    if not text:
        return ""

    clean_text = text.strip()
    if clean_text.startswith("```") and clean_text.endswith("```"):
        first_newline = clean_text.find('\n')
        if first_newline != -1:
            return clean_text[first_newline+1:-3].strip()

    return clean_text

def get_token_count_for_text(text):
    global _tiktoken_encoding
    try:
        if _tiktoken_encoding is None:
            # Uses cl100k_base encoding for compatibility with gpt-4
            _tiktoken_encoding = tiktoken.get_encoding("cl100k_base")

        return len(_tiktoken_encoding.encode(text, disallowed_special=()))
    except Exception:
        return -1

def get_file_hash(full_path):
    try:
        with open(full_path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except (IOError, OSError):
        return None

def _get_default_config_dict():
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
        'token_color_threshold': 4000,
        'enable_compact_mode_on_minimize': False,
        'enable_ultra_compact_mode': False,
        'add_all_warning_threshold': ADD_ALL_WARNING_THRESHOLD_DEFAULT,
        'new_file_alert_threshold': NEW_FILE_ALERT_THRESHOLD_DEFAULT,
        'show_feedback_on_paste': True,
        'info_mode_active': True,
        'user_lists': {
            'recent_projects': [],
            'filetypes': []
        }
    }

def _load_default_filetypes(target_dict):
    try:
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            target_dict.setdefault('user_lists', {})['filetypes'] = json.load(f)
    except Exception:
        pass

def _create_and_get_default_config():
    config = _get_default_config_dict()
    _load_default_filetypes(config)
    save_config(config)
    return config

def load_config():
    # Merges user values with the default template and applies migrations
    defaults = _get_default_config_dict()
    _load_default_filetypes(defaults)

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

    final_config = defaults.copy()

    for key in defaults:
        if key not in loaded_config:
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
    # Uses atomic replacement to prevent file corruption in multi-instance environments
    export_data = config.copy()

    user_lists_data = export_data.pop('user_lists', {'recent_projects': [], 'filetypes': []})

    if isinstance(user_lists_data.get('filetypes'), list):
        user_lists_data['filetypes'].sort(key=lambda item: item['ext'])

    export_data['user_lists'] = user_lists_data

    fd, temp_path = tempfile.mkstemp(dir=PERSISTENT_DATA_DIR, prefix='config_tmp_')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        max_retries = 5
        for attempt in range(max_retries):
            try:
                os.replace(temp_path, CONFIG_FILE_PATH)
                temp_path = None
                break
            except PermissionError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1)
    except IOError as e:
        print(f"Error saving configuration: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def update_and_get_new_filetypes():
    # Synchronizes local filetype settings with the bundled default template
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
    # Returns string-based paths and patterns for high-performance matching
    gitignore_data = []
    base_dir_norm = os.path.abspath(base_dir).replace('\\', '/')

    for root, dirs, files in os.walk(base_dir, topdown=True):
        root_norm = os.path.abspath(root).replace('\\', '/')

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
                        # Store root as string for faster prefix matching in is_ignored
                        gitignore_data.append((root_norm, patterns))
            except (IOError, OSError):
                pass

        if gitignore_data:
            dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), base_dir_norm, gitignore_data)]

    return gitignore_data

def is_ignored(path, base_dir, gitignore_data):
    # Follows standard Git rules: anchored vs match-anywhere, negated patterns, and dir-only
    if not gitignore_data:
        return False

    path_norm = path.replace('\\', '/')
    if '/.git/' in path_norm or path_norm.endswith('/.git'):
        return True

    is_ignored_flag = False
    is_dir = None

    for gitignore_dir_str, patterns in gitignore_data:
        if not path_norm.startswith(gitignore_dir_str):
            continue

        rel_path_str = path_norm[len(gitignore_dir_str):].lstrip('/')
        if not rel_path_str:
            continue

        parts = rel_path_str.split('/')

        for p_orig in patterns:
            p = p_orig.strip()
            if not p or p.startswith('#'):
                continue

            is_negated = p.startswith('!')
            if is_negated:
                p = p[1:]

            is_dir_only = p.endswith('/')
            p_clean = p.rstrip('/')

            is_anchored = '/' in p_clean or p_orig.startswith('/')
            p_final = p_clean.lstrip('/')

            match = False
            if not is_anchored:
                if any(fnmatch.fnmatch(part, p_final) for part in parts[:-1]):
                    match = True
                elif fnmatch.fnmatch(parts[-1], p_final):
                    if not is_dir_only:
                        match = True
                    else:
                        if is_dir is None: is_dir = os.path.isdir(path)
                        if is_dir: match = True
            else:
                if rel_path_str.startswith(p_final + '/'):
                    match = True
                elif fnmatch.fnmatch(rel_path_str, p_final):
                    if not is_dir_only:
                        match = True
                    else:
                        if is_dir is None: is_dir = os.path.isdir(path)
                        if is_dir: match = True

            if match:
                is_ignored_flag = not is_negated

    return is_ignored_flag

def load_app_version():
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

def calculate_font_color(hex_color):
    # Selects 'light' or 'dark' text based on background luminance
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Relative luminance formula (W3C standard)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return 'dark' if luminance > FONT_LUMINANCE_THRESHOLD else 'light'
    except (ValueError, IndexError):
        return 'light'