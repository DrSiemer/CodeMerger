import sys
import os
from pathlib import Path

def get_bundle_dir():
    """
    Gets the base path for reading bundled resources
    Returns the temporary directory created by PyInstaller or the project root
    """
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_persistent_data_dir():
    """
    Gets the directory for storing persistent data
    Uses OS-appropriate paths for user configuration
    """
    if getattr(sys, 'frozen', False):
        if sys.platform == "win32":
            app_data_path = os.getenv('APPDATA')
            if app_data_path:
                config_dir = os.path.join(app_data_path, 'CodeMerger')
            else:
                config_dir = os.path.dirname(sys.executable)
        elif sys.platform == "darwin":
            config_dir = os.path.join(str(Path.home()), 'Library', 'Application Support', 'CodeMerger')
        else:
            config_dir = os.path.join(str(Path.home()), '.config', 'CodeMerger')

        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Application Paths
BUNDLE_DIR = get_bundle_dir()
PERSISTENT_DATA_DIR = get_persistent_data_dir()

CONFIG_FILE_PATH = os.path.join(PERSISTENT_DATA_DIR, 'config.json')

DEFAULT_FILETYPES_CONFIG_PATH = os.path.join(BUNDLE_DIR, 'default_filetypes.json')

# Project Starter Template Paths
BOILERPLATE_DIR = os.path.join(BUNDLE_DIR, 'assets', 'boilerplate')
REFERENCE_DIR = os.path.join(BUNDLE_DIR, 'assets', 'reference')

ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'icon.ico')

LOGO_MASK_PATH = os.path.join(BUNDLE_DIR, 'assets', 'logo_mask.png')
LOGO_MASK_SMALL_PATH = os.path.join(BUNDLE_DIR, 'assets', 'logo_mask_small.png')

NEW_FILES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'newfiles.png')
NEW_FILES_MANY_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'newfiles_many.png')

FOLDER_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'folder.png')
FOLDER_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'folder_active.png')

FOLDER_REVEAL_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'folder_small.png')

TRASH_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'trash.png')

EDIT_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'edit.png')

VERSION_FILE_PATH = os.path.join(BUNDLE_DIR, 'version.txt')

COMPACT_MODE_CLOSE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'compactmode_close.png')

DEFAULTS_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'defaults.png')

EXTRA_FILES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'extra_files.png')
EXTRA_FILES_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'extra_files_active.png')

GIT_FILES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'git_files.png')
GIT_FILES_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'git_files_active.png')

PATHS_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'paths.png')
PATHS_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'paths_active.png')

ORDER_REQUEST_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'order_request.png')

SETTINGS_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'settings.png')
FILETYPES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'filetypes.png')
SETTINGS_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'settings_active.png')
FILETYPES_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'filetypes_active.png')

# Project Starter Icons
PROJECT_STARTER_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'project_starter.png')
PROJECT_STARTER_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'project_starter_active.png')
LOCKED_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'locked.png')
UNLOCKED_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'unlocked.png')

# Info Mode Icons
INFO_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'info.png')
INFO_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'info_active.png')

REGISTRY_KEY_PATH = r"Software\CodeMerger"

UPDATE_CLEANUP_FILE_PATH = os.path.join(PERSISTENT_DATA_DIR, 'update_cleanup.json')