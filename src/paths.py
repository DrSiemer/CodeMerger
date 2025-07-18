import sys
import os

def get_base_path():
    """
    Gets the base path for the application, which is the directory
    containing the executable or the main script. This works for both
    normal execution and a PyInstaller bundled app.
    """
    # PyInstaller creates a temp folder and stores its path in _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS

    # In normal execution, we are in the 'src' folder, so we go up one level
    # to the project root.
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# --- Define Application Paths ---

# The absolute path to the project root or the executable's directory
BASE_PATH = get_base_path()

# Path to the config file for recent directories
CONFIG_FILE_PATH = os.path.join(BASE_PATH, 'config.json')

# Path to the filetypes config
FILETYPES_CONFIG_PATH = os.path.join(BASE_PATH, 'filetypes.json')

# Path to the application icon
ICON_PATH = os.path.join(BASE_PATH, 'assets', 'icon.ico')