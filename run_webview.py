import sys
import os
import ctypes

# --- DPI AWARENESS BOOTSTRAP ---
# Must be called before any UI elements or windows are initialized to ensure
# Windows calculates coordinates and scaling correctly on High DPI displays.
if sys.platform == "win32":
    try:
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 (-4)
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

import webview
import logging
import traceback
import time
import base64
import threading
from src.api import Api
from src.core.logger import setup_logging
from src.core.paths import get_bundle_dir, SPLASH_1_PATH, SPLASH_2_PATH, SPLASH_3_PATH
from src.core.file_monitor_thread import FileMonitorThread
from src.core.updater import Updater
from src.core.utils import load_app_version
from src import constants as c

# Import core backend logic
from src.app_state import AppState
from src.core.project_manager import ProjectManager
from src.core.utils import load_active_file_extensions, save_config, update_and_get_new_filetypes
from src.core.window_manager import WindowManager

log = logging.getLogger("CodeMerger")

def main():
    setup_logging()
    monitor = None
    try:
        newly_added_filetypes = update_and_get_new_filetypes()
        app_state = AppState()
        project_manager = ProjectManager(load_active_file_extensions)
        api = Api(app_state, project_manager, newly_added_filetypes)
        monitor = FileMonitorThread(None, app_state, project_manager)
        manager = WindowManager(api, monitor, dev_mode=("--dev" in sys.argv))
        manager.start()
    except Exception as e:
        log.error(f"Fatal error during startup:\n{traceback.format_exc()}")
    finally:
        try:
            if monitor: monitor.stop()
        except Exception: pass
    os._exit(0)

if __name__ == '__main__':
    main()