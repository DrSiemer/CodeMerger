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
    - If running as a bundled executable, this is a dedicated 'CodeMerger'
      folder within the user's AppData directory.
    - If running as a script, this is the project root.
    """
    if getattr(sys, 'frozen', False):  # Running as a bundled executable
        # Use the AppData folder for persistent configuration.
        app_data_path = os.getenv('APPDATA')
        if app_data_path:
            config_dir = os.path.join(app_data_path, 'CodeMerger')
            os.makedirs(config_dir, exist_ok=True)
            return config_dir
        # Fallback to the executable's directory if APPDATA is somehow not set
        return os.path.dirname(sys.executable)
    else: # Running as a script in a development environment
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

# Path to the pin button graphics
PIN_BUTTON_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'pinbutton.png')
PIN_BUTTON_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'pinbutton_active.png')