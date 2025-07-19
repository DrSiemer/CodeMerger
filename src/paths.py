import sys
import os

def get_bundle_dir():
    """
    Gets the base path for reading bundled resources.
    This is the temporary directory created by PyInstaller for the executable
    or the project root when running from source.
    """
    # PyInstaller creates a temp folder and stores its path in _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    # In normal execution, we are in the 'src' folder, so we go up one level
    # to the project root.
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_persistent_data_dir():
    """
    Gets the directory for storing persistent data (e.g., config files).
    - If running as a bundled executable, this is the directory of the executable.
    - If running as a script, this is the project root (same as get_bundle_dir).
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as a bundled exe (sys.executable is the path to the exe)
        return os.path.dirname(sys.executable)
    else:
        # Running as a script
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# --- Define Application Paths ---

# The absolute path to bundled resources (assets, filetypes.json)
BUNDLE_DIR = get_bundle_dir()

# The absolute path for persistent, writable files (config.json)
PERSISTENT_DATA_DIR = get_persistent_data_dir()

# Path to the config file for recent directories
# THIS IS THE KEY CHANGE: Use the persistent directory
CONFIG_FILE_PATH = os.path.join(PERSISTENT_DATA_DIR, 'config.json')

# Path to the filetypes config (this is a bundled resource)
FILETYPES_CONFIG_PATH = os.path.join(BUNDLE_DIR, 'filetypes.json')

# Path to the application icon (this is a bundled resource)
ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'icon.ico')