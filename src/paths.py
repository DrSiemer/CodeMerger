import sys
import os

def get_bundle_dir():
    """
    Gets the base path for reading bundled resources.
    This is the temporary directory created by PyInstaller for the executable
    or the project root when running from source.
    """
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_persistent_data_dir():
    """
    Gets the directory for storing persistent data (e.g., config files).
    - If running as a bundled executable, this is the directory of the executable.
    - If running as a script, this is the project root.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# --- Define Application Paths ---
BUNDLE_DIR = get_bundle_dir()
PERSISTENT_DATA_DIR = get_persistent_data_dir()

# Path to the config file
CONFIG_FILE_PATH = os.path.join(PERSISTENT_DATA_DIR, 'config.json')

# Path to the bundled default filetypes template
DEFAULT_FILETYPES_CONFIG_PATH = os.path.join(BUNDLE_DIR, 'default_filetypes.json')

# Path to the application icon
ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'icon.ico')

# Path to the version file
VERSION_FILE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'version.txt')