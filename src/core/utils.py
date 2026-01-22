import os
import json
import fnmatch
import hashlib
import tiktoken
import psutil
import sys
from pathlib import Path
from ..core.paths import (
    CONFIG_FILE_PATH, DEFAULT_FILETYPES_CONFIG_PATH, VERSION_FILE_PATH
)
from ..constants import (
    DEFAULT_COPY_MERGED_PROMPT, DEFAULT_INTRO_PROMPT, DEFAULT_OUTRO_PROMPT,
    TOKEN_COUNT_ENABLED_DEFAULT,
    ADD_ALL_WARNING_THRESHOLD_DEFAULT
)

def is_another_instance_running():
    """
    Checks if another instance of CodeMerger is currently running.
    Checks for the executable name if frozen, or the module name if running from source.
    Returns False if the CM_DEV_MODE environment variable is set.
    """
    # Skip check if launched via go.bat (dev mode)
    if os.environ.get('CM_DEV_MODE') == '1':
        return False

    current_pid = os.getpid()
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Skip the current process
                if proc.info['pid'] == current_pid:
                    continue

                # Check for frozen executable (Windows)
                if getattr(sys, 'frozen', False):
                    if proc.info['name'] and proc.info['name'].lower() == "codemerger.exe":
                        return True
                # Check for running from source
                else:
                    cmdline = proc.info.get('cmdline')
                    if cmdline and any("src.codemerger" in arg for arg in cmdline):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception:
        # Fallback to False if psutil fails for any reason
        return False
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

def _create_and_get_default_config():
    """
    Creates a new config object from the default template, saves it to disk,
    and returns it. This is the definitive first-run function
    """
    config = {
        'active_directory': '',
        'default_editor': '',
        'default_parent_folder': '',
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
        'user_lists': {
            'recent_projects': [],
            'filetypes': []
        }
    }
    try:
        # Load the list of filetypes from the bundled template
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            config['user_lists']['filetypes'] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback in case the template is missing or corrupt
        pass

    # Save the newly created config to disk before returning
    save_config(config)
    return config

def load_config():
    """
    Loads the main application configuration from config.json.
    If the file is missing or corrupt, it's created from the default template.
    It also handles automatic migration from older config formats.
    """
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
            migration_occurred = False

            # --- Backward Compatibility: Migrate old flat list format to new nested format ---
            if 'recent_projects' in config or 'filetypes' in config or 'recent_directories' in config:
                migration_occurred = True
                user_lists_group = config.setdefault('user_lists', {})

                # Handle 'recent_projects' or the even older 'recent_directories'
                if 'recent_projects' in config:
                    user_lists_group['recent_projects'] = config.pop('recent_projects', [])
                elif 'recent_directories' in config:
                    user_lists_group['recent_projects'] = config.pop('recent_directories', [])

                if 'filetypes' in config:
                    user_lists_group['filetypes'] = config.pop('filetypes', [])

            # --- Standard key validation and addition for backward compatibility ---
            if 'user_lists' not in config or 'filetypes' not in config.get('user_lists', {}):
                raise ValueError("Config is missing 'filetypes' key.")
            if 'default_editor' not in config:
                config['default_editor'] = ''
            if 'default_parent_folder' not in config:
                config['default_parent_folder'] = ''
            if 'user_experience' not in config:
                config['user_experience'] = ''
            if 'scan_for_secrets' not in config:
                config['scan_for_secrets'] = False
            if 'last_update_check' not in config:
                config['last_update_check'] = None
            if 'check_for_updates' in config:
                del config['check_for_updates']
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
            if 'line_count_enabled' in config:
                config['token_count_enabled'] = config.pop('line_count_enabled')
            if 'token_count_enabled' not in config:
                config['token_count_enabled'] = TOKEN_COUNT_ENABLED_DEFAULT
            if 'token_limit' not in config:
                config['token_limit'] = 0
            if 'line_count_threshold' in config:
                config.pop('line_count_threshold')
            if 'token_count_threshold' in config:
                config.pop('token_count_threshold')
            if 'enable_compact_mode_on_minimize' not in config:
                config['enable_compact_mode_on_minimize'] = True
            if 'add_all_warning_threshold' not in config:
                config['add_all_warning_threshold'] = ADD_ALL_WARNING_THRESHOLD_DEFAULT

            # If a migration was performed, save the newly structured config immediately.
            if migration_occurred:
                save_config(config)

            return config
    except (FileNotFoundError, json.JSONDecodeError, ValueError, IOError):
        # Any failure results in creating a new, correctly structured config
        return _create_and_get_default_config()

def save_config(config):
    """Saves the complete application configuration object to config.json"""
    # Force 'user_lists' to be the last key for consistent ordering.
    user_lists_data = config.pop('user_lists', {'recent_projects': [], 'filetypes': []})

    # Ensure filetypes within the group are sorted alphabetically for consistency
    if isinstance(user_lists_data.get('filetypes'), list):
        user_lists_data['filetypes'].sort(key=lambda item: item['ext'])

    config['user_lists'] = user_lists_data

    with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

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