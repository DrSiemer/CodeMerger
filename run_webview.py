import sys
import os
import webview
import logging
import time
from src.api import Api
from src.core.logger import setup_logging
from src.core.paths import get_bundle_dir
from src.core.file_monitor_thread import FileMonitorThread

# Import core backend logic
from src.app_state import AppState
from src.core.project_manager import ProjectManager
from src.core.utils import load_active_file_extensions

log = logging.getLogger("CodeMerger")

class WindowManager:
    """
    Coordinates the visibility and lifecycle of the main application window
    and the minimalist compact widget using a persistent window strategy.
    """
    def __init__(self, api, monitor, dev_mode=False):
        self.api = api
        self.monitor = monitor
        self.dev_mode = dev_mode
        self.main_window = None
        self.compact_window = None

        # State lock to prevent race conditions during mode switches
        self._transitioning = False

        # Configuration for production vs dev URL
        if dev_mode:
            self.base_url = "http://localhost:5173"
        else:
            bundle_dir = get_bundle_dir()
            self.base_url = os.path.join(bundle_dir, 'frontend', 'dist', 'index.html')

    def start(self):
        """Initializes both windows immediately for fast switching."""

        # 1. Create Main Window
        self.main_window = webview.create_window(
            "CodeMerger",
            url=self.base_url,
            js_api=self.api,
            width=1200,
            height=780,
            min_size=(800, 600),
            background_color='#2E2E2E'
        )

        # 2. Create Compact Window (Hidden by default)
        compact_url = f"{self.base_url}#/compact"
        if not self.dev_mode:
            compact_url = f"file://{self.base_url}#/compact"

        self.compact_window = webview.create_window(
            "CM-Compact",
            url=compact_url,
            js_api=self.api,
            width=155,
            height=160,
            frameless=True,
            on_top=True,
            hidden=True, # Start hidden for instant show later
            background_color='#2E2E2E'
        )

        self.api.set_window_manager(self)
        self.monitor.update_window(self.main_window)

        # Dashboard Events
        self.main_window.events.minimized += self._on_main_minimized
        self.main_window.events.closed += self._on_window_closed

        # Compact Events
        # Intercept the close event so it toggles visibility instead of killing the window
        self.compact_window.events.closing += self._on_compact_closing

        # Start PyWebView loop (Debug disabled by default)
        webview.start(debug=False)

    def _on_main_minimized(self):
        """Triggered when the user minimizes the main window."""
        if self._transitioning:
            return

        config = self.api.app_state.config
        if config.get('enable_compact_mode_on_minimize', True):
            self._transitioning = True

            # Sequence matters: hide main before showing compact to prevent dual-visibility
            self.main_window.hide()
            time.sleep(0.05) # Allow Z-order buffer
            self.show_compact()

            self._transitioning = False

    def _on_window_closed(self):
        """Forcefully exits the entire process to kill background threads and Chromium."""
        self.exit_all()

    def _on_compact_closing(self):
        """Prevents the compact window from being destroyed; restores main instead."""
        self.restore_main()
        return False # Prevent actual window destruction

    def show_compact(self):
        """Instantly displays the minimalist compact window."""
        if self.compact_window:
            self.compact_window.show()
            self.monitor.update_window(self.compact_window)

    def restore_main(self):
        """Instantly switches back to the full dashboard."""
        if self._transitioning:
            return

        self._transitioning = True

        if self.compact_window:
            self.compact_window.hide()

        if self.main_window:
            # Brief sleep to allow OS to release the Z-order before main shows
            time.sleep(0.05)
            self.main_window.show()
            self.main_window.restore()
            self.monitor.update_window(self.main_window)

        self._transitioning = False

    def exit_all(self):
        """Closes all windows and exits the process forcefully."""
        self.monitor.update_window(None)
        # Force destruction of all child processes and threads
        os._exit(0)

def main():
    setup_logging()

    # Initialize Core Application Logic
    app_state = AppState()
    project_manager = ProjectManager(load_active_file_extensions)

    # Initialize API
    api = Api(app_state, project_manager)

    # Initialize background file monitor
    monitor = FileMonitorThread(None, app_state, project_manager)
    monitor.start()

    # Launch via Manager
    dev_mode = "--dev" in sys.argv
    manager = WindowManager(api, monitor, dev_mode=dev_mode)

    try:
        manager.start()
    finally:
        log.info("Window context lost. Terminating background services.")
        monitor.stop()

if __name__ == '__main__':
    main()