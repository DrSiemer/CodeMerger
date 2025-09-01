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
    if getattr(sys, 'frozen', False):  # Running as a bundled executable
        if sys.platform == "win32":
            # Use the AppData folder for persistent configuration on Windows.
            app_data_path = os.getenv('APPDATA')
            if app_data_path:
                config_dir = os.path.join(app_data_path, 'CodeMerger')
            else: # Fallback
                config_dir = os.path.dirname(sys.executable)
        elif sys.platform == "darwin":
            # Use Application Support directory on macOS.
            config_dir = os.path.join(str(Path.home()), 'Library', 'Application Support', 'CodeMerger')
        else: # Linux and other Unix-like systems
            config_dir = os.path.join(str(Path.home()), '.config', 'CodeMerger')

        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    else: # Running as a script in a development environment
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

# Path to the edit icon
EDIT_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'edit.png')

# Path to the trash icon
TRASH_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'trash.png')

# Path to the version file
VERSION_FILE_PATH = os.path.join(BUNDLE_DIR, 'version.txt')

# Path to the compact mode graphics
COMPACT_MODE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'compactmode.png')
COMPACT_MODE_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'compactmode_clicked.png')
COMPACT_MODE_CLOSE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'compactmode_close.png')