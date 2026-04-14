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

SPLASH_1_PATH = os.path.join(BUNDLE_DIR, 'assets', 'splash_1.png')
SPLASH_2_PATH = os.path.join(BUNDLE_DIR, 'assets', 'splash_2.png')
SPLASH_3_PATH = os.path.join(BUNDLE_DIR, 'assets', 'splash_3.png')

VERSION_FILE_PATH = os.path.join(BUNDLE_DIR, 'version.txt')

REGISTRY_KEY_PATH = r"Software\CodeMerger"