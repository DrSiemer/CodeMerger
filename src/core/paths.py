import sys
import os
from pathlib import Path

def get_bundle_dir():
    """
    Gets the base path for reading bundled resources.
    This is the temporary directory created by PyInstaller for the executable
    or the project root when running from source.
    """
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_persistent_data_dir():
    """
    Gets the directory for storing persistent data (e.g., config files).
    This is OS-aware for bundled executables.
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

# --- Define Application Paths ---
BUNDLE_DIR = get_bundle_dir()
PERSISTENT_DATA_DIR = get_persistent_data_dir()

# Path to the config file
CONFIG_FILE_PATH = os.path.join(PERSISTENT_DATA_DIR, 'config.json')

# Path to the bundled default filetypes template
DEFAULT_FILETYPES_CONFIG_PATH = os.path.join(BUNDLE_DIR, 'default_filetypes.json')

# Path to the application icon
ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'icon.ico')

# Path to the logo mask for the project color swatch
LOGO_MASK_PATH = os.path.join(BUNDLE_DIR, 'assets', 'logo_mask.png')

# Path to the new files warning icon
NEW_FILES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'newfiles.png')

# Path to the folder icon
FOLDER_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'folder.png')

# Path to the smaller folder icon used for revealing files
FOLDER_REVEAL_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'folder_small.png')

# Path to the trash icon
TRASH_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'trash.png')

# Path to the version file
VERSION_FILE_PATH = os.path.join(BUNDLE_DIR, 'version.txt')

# Path to the compact mode graphics
COMPACT_MODE_CLOSE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'compactmode_close.png')

# Path to the defaults icon
DEFAULTS_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'defaults.png')

# Path to the filetype filter toggle icon
EXTRA_FILES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'extra_files.png')
EXTRA_FILES_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'extra_files_active.png')

# Path to the paths toggle icon
PATHS_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'paths.png')
PATHS_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'paths_active.png')

# Path to the order request icon
ORDER_REQUEST_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'order_request.png')

# Windows Registry path
REGISTRY_KEY_PATH = r"Software\CodeMerger"

# Path for post-update cleanup instructions
UPDATE_CLEANUP_FILE_PATH = os.path.join(PERSISTENT_DATA_DIR, 'update_cleanup.json')