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
        self._is_shutting_down = False

        # State lock to prevent race conditions during mode switches
        self._transitioning = False

        # Position Persistence and Monitor Tracking
        self.compact_mode_last_x = None
        self.compact_mode_last_y = None
        self.compact_last_monitor_handle = None

        self.main_last_x = None
        self.main_last_y = None
        self.main_last_w = 1200
        self.main_last_h = 780

        # Configuration for production vs dev URL
        if dev_mode:
            self.base_url = "http://localhost:5173"
        else:
            bundle_dir = get_bundle_dir()
            self.base_url = os.path.join(bundle_dir, 'frontend', 'dist', 'index.html')

    def _get_main_window_monitor(self):
        if not self.main_window:
            return None

        main_x, main_y = self.main_window.x, self.main_window.y
        if main_x <= -32000 or main_y <= -32000:
            if getattr(self, 'main_last_x', None) is not None:
                main_x, main_y = self.main_last_x, self.main_last_y
            else:
                main_x, main_y = 0, 0

        main_w = getattr(self, 'main_last_w', 1200)
        main_h = getattr(self, 'main_last_h', 780)

        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32

                # Approximate center of the window
                x = main_x + (main_w // 2)
                y = main_y + (main_h // 2)

                point = wintypes.POINT(x, y)
                MONITOR_DEFAULTTONEAREST = 2
                h_monitor = user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
                return h_monitor
            except Exception:
                pass

        # Fallback identifier based on rough coordinates
        return f"{main_x // 1920}_{main_y // 1080}"

    def _get_monitor_work_area(self, h_monitor):
        """Fetches the screen bounds to prevent spawning windows out of bounds."""
        if sys.platform == "win32" and h_monitor:
            try:
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32
                class MONITORINFO(ctypes.Structure):
                    _fields_ = [
                        ("cbSize", wintypes.DWORD),
                        ("rcMonitor", wintypes.RECT),
                        ("rcWork", wintypes.RECT),
                        ("dwFlags", wintypes.DWORD),
                    ]
                mi = MONITORINFO()
                mi.cbSize = ctypes.sizeof(MONITORINFO)
                if user32.GetMonitorInfoW(h_monitor, ctypes.byref(mi)):
                    return (mi.rcWork.left, mi.rcWork.top, mi.rcWork.right, mi.rcWork.bottom)
            except Exception:
                pass

        # Fallback to PyWebView screen info
        try:
            screens = webview.screens
            if screens:
                s = screens[0]
                return (0, 0, s.width, s.height)
        except Exception:
            pass

        return (0, 0, 1920, 1080)

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
            width=100,
            height=120,
            min_size=(100, 120),
            frameless=True,
            on_top=True,
            hidden=True, # Start hidden for instant show later
            background_color='#2E2E2E'
        )

        self.api.set_window_manager(self)
        self.monitor.update_window(self.main_window)

        # Dashboard Events
        self.main_window.events.minimized += self._on_main_minimized
        self.main_window.events.closing += self._on_main_closing
        self.main_window.events.closed += self._on_window_closed

        try:
            self.main_window.events.moved += self._on_main_moved
            self.main_window.events.resized += self._on_main_resized

            # Ensures compact window is hidden if OS forcefully restores main window
            self.main_window.events.restored += self._on_main_restored
            self.main_window.events.maximized += self._on_main_restored
            self.main_window.events.shown += self._on_main_restored
        except AttributeError:
            pass

        # Compact Events
        # Intercept the close event so it toggles visibility instead of killing the window
        self.compact_window.events.closing += self._on_compact_closing

        # Prevent DevTools from opening automatically when debug mode is enabled
        webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False

        # Start PyWebView loop (debug mode allows Ctrl+Shift+I in dev)
        webview.start(debug=self.dev_mode)

    def _on_main_moved(self, x, y):
        # Ignore off-screen coordinates (-32000) but keep valid (even negative) ones from maximized state
        if x > -32000 and y > -32000:
            self.main_last_x = x
            self.main_last_y = y

    def _on_main_resized(self, width, height):
        # Prevent 0x0 size overwrites when window is minimized by the OS
        if width > 0 and height > 0:
            self.main_last_w = width
            self.main_last_h = height

    def _on_main_restored(self):
        """Triggered when the OS restores the main window (e.g. via taskbar click)."""
        if self._transitioning:
            return

        self._transitioning = True
        try:
            if self.compact_window:
                self.compact_window.hide()
            self.monitor.update_window(self.main_window)
        finally:
            self._transitioning = False

    def _on_main_minimized(self):
        """Triggered when the user minimizes the main window."""
        if self._transitioning:
            return

        config = self.api.app_state.config
        if config.get('enable_compact_mode_on_minimize', True):
            self._transitioning = True
            try:
                self.main_window.hide()
                self.show_compact()
            finally:
                self._transitioning = False

    def _on_main_closing(self):
        """
        Triggered when the main dashboard is about to close.
        Destroying the compact window here prevents WebView2 shutdown race conditions
        that cause Error 1411.
        """
        self._is_shutting_down = True
        if self.compact_window:
            try:
                self.compact_window.destroy()
            except Exception:
                pass

    def _on_window_closed(self):
        """
        Triggered when the main dashboard is closed.
        Cleanup must be graceful to avoid Error 1411 (Chrome_WidgetWin unregister failure).
        """
        pass

    def _on_compact_closing(self):
        """Prevents the compact window from being destroyed; restores main instead."""
        if self._is_shutting_down:
            return # Allow destruction
        self.restore_main()
        return False # Prevent actual window destruction

    def show_compact(self):
        """Instantly displays the minimalist compact window."""
        if self.compact_window:
            current_monitor = self._get_main_window_monitor()

            if self.compact_last_monitor_handle is None:
                self.compact_last_monitor_handle = current_monitor

            # If the MAIN window changed monitors since last time, invalidate compact position
            monitor_changed = self.compact_last_monitor_handle != current_monitor
            if monitor_changed:
                self.compact_mode_last_x = None
                self.compact_mode_last_y = None
                self.compact_last_monitor_handle = current_monitor

            widget_w, widget_h = 100, 120

            if self.compact_mode_last_x is not None:
                target_x, target_y = self.compact_mode_last_x, self.compact_mode_last_y

                # Clamp the saved position to the bounds of the monitor it currently resides on
                if sys.platform == "win32":
                    try:
                        import ctypes
                        from ctypes import wintypes
                        user32 = ctypes.windll.user32
                        point = wintypes.POINT(int(target_x + widget_w//2), int(target_y + widget_h//2))
                        MONITOR_DEFAULTTONEAREST = 2
                        h_mon = user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
                        mon_x, mon_y, mon_right, mon_bottom = self._get_monitor_work_area(h_mon)
                        target_x = max(mon_x, min(target_x, mon_right - widget_w))
                        target_y = max(mon_y, min(target_y, mon_bottom - widget_h))
                    except Exception:
                        pass
            else:
                main_x = getattr(self, 'main_last_x', 0) or 0
                main_y = getattr(self, 'main_last_y', 0) or 0
                main_w = getattr(self, 'main_last_w', 1200)

                # Default placement: Top right of the main window area
                ideal_x = main_x + main_w - widget_w - 20
                ideal_y = main_y + 20
                margin = 10

                mon_x, mon_y, mon_right, mon_bottom = self._get_monitor_work_area(current_monitor)
                target_x = max(mon_x + margin, min(ideal_x, mon_right - widget_w - margin))
                target_y = max(mon_y + margin, min(ideal_y, mon_bottom - widget_h - margin))

            self.compact_last_monitor_handle = current_monitor

            self.compact_window.move(int(target_x), int(target_y))
            self.compact_window.show()
            self.monitor.update_window(self.compact_window)

    def restore_main(self):
        """Instantly switches back to the full dashboard."""
        if self._transitioning:
            return

        self._transitioning = True
        try:
            if self.compact_window:
                self.compact_window.hide()

            if self.main_window:
                self.main_window.show()
                self.main_window.restore()
                self.monitor.update_window(self.main_window)
        finally:
            self._transitioning = False

    def exit_all(self):
        """Closes all windows gracefully to allow process to exit naturally."""
        self._is_shutting_down = True
        self.monitor.update_window(None)
        if self.main_window:
            try:
                self.main_window.destroy()
            except Exception:
                pass

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