import sys
import os
import signal

# Flag environment early to ensure isolated configuration paths
if "--dev" in sys.argv:
    os.environ['CM_DEV_MODE'] = '1'

import ctypes
from ctypes import wintypes
import mimetypes

# DPI AWARENESS BOOTSTRAP
# Must be called before UI initialization to ensure correct coordinate scaling on High DPI displays
if sys.platform == "win32":
    try:
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

from src.app_state import AppState
from src.core.project_manager import ProjectManager
from src.core.utils import (
    load_active_file_extensions, save_config, update_and_get_new_filetypes,
    is_another_instance_running
)
from src.core.window_manager import WindowManager

log = logging.getLogger("CodeMerger")

def main():
    # Forceful exit handlers for terminal signals
    signal.signal(signal.SIGINT, lambda s, f: os._exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: os._exit(0))

    dev_mode = os.environ.get('CM_DEV_MODE') == '1'
    debug_mode = "--debug" in sys.argv or "--inspect" in sys.argv or dev_mode
    show_console = "--console" in sys.argv

    # Detect if this instance is secondary. Dev and Prod instances are isolated via unique Mutex names.
    is_second_instance = is_another_instance_running()

    if show_console and sys.platform == "win32":
        try:
            ctypes.windll.kernel32.AllocConsole()

            # Enable ANSI support for formatted logs in the spawned console
            kernel32 = ctypes.windll.kernel32
            h_out = kernel32.GetStdHandle(-11)
            if h_out != -1:
                mode = wintypes.DWORD()
                if kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
                    kernel32.SetConsoleMode(h_out, mode.value | 0x0004)

            sys.stdout = open('CONOUT$', 'w', encoding='utf-8')
            sys.stderr = open('CONOUT$', 'w', encoding='utf-8')
        except Exception:
            pass

    # MIME Type Registration
    # Force-register correct MIME types to bypass ES module failures caused by incorrect registry settings
    # This bypasses a common Windows registry bug where .js files are served as text/plain, which breaks Vite ES modules in Chromium
    mimetypes.init()
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('application/javascript', '.mjs')
    mimetypes.add_type('text/css', '.css')
    mimetypes.add_type('image/svg+xml', '.svg')
    mimetypes.add_type('image/x-icon', '.ico')

    setup_logging()

    # WebView Engine Global Settings
    webview.settings['ALLOW_FILE_URLS'] = True
    os.environ['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = '--allow-file-access-from-files'

    monitor = None
    try:
        log.info("--- CodeMerger Startup ---")
        bundle_dir = get_bundle_dir()
        log.info(f"Bundle Directory: {bundle_dir}")

        newly_added_filetypes = update_and_get_new_filetypes()
        app_state = AppState(is_second_instance=is_second_instance)
        project_manager = ProjectManager(load_active_file_extensions)
        api = Api(app_state, project_manager, newly_added_filetypes)
        monitor = FileMonitorThread(None, app_state, project_manager)

        manager = WindowManager(api, monitor, dev_mode=dev_mode, debug_mode=debug_mode)
        log.info(f"Base URL Resolved: {manager.base_url}")

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