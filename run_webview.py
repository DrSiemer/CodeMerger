import sys
import os
import webview
import logging
import traceback
import time
import base64
from src.api import Api
from src.core.logger import setup_logging
from src.core.paths import get_bundle_dir, SPLASH_1_PATH, SPLASH_2_PATH, SPLASH_3_PATH
from src.core.file_monitor_thread import FileMonitorThread

# Import core backend logic
from src.app_state import AppState
from src.core.project_manager import ProjectManager
from src.core.utils import load_active_file_extensions, save_config

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
        self.splash_window = None
        self._is_shutting_down = False
        self._transitioning = False

        # Load persisted geometry from config
        geom = self.api.app_state.config.get('main_window_geom', {})

        self.main_last_x = geom.get('x')
        self.main_last_y = geom.get('y')
        self.main_last_w = geom.get('w', 1200)
        self.main_last_h = geom.get('h', 780)

        # Position Persistence and Monitor Tracking
        self.compact_mode_last_x = geom.get('compact_x')
        self.compact_mode_last_y = geom.get('compact_y')
        self.compact_last_monitor_handle = None

        # Configuration for production vs dev URL
        if dev_mode:
            self.base_url = "http://localhost:5173"
        else:
            bundle_dir = get_bundle_dir()
            self.base_url = os.path.join(bundle_dir, 'frontend', 'dist', 'index.html')

    def _update_main_bounds(self):
        """Safely captures the main window bounds, strictly ignoring minimized (-32000) states."""
        if not self.main_window:
            return

        x = self.main_window.x
        y = self.main_window.y
        w = self.main_window.width
        h = self.main_window.height

        if x is not None and x > -30000:
            self.main_last_x = x
        if y is not None and y > -30000:
            self.main_last_y = y
        if w is not None and w >= 800:
            self.main_last_w = w
        if h is not None and h >= 600:
            self.main_last_h = h

    def _get_main_window_monitor(self):
        """
        Identifies the monitor handle the main dashboard is currently on.
        Uses the center coordinates to avoid false triggers from maximized (-8) bounds.
        """
        main_x = self.main_last_x if self.main_last_x is not None else 0
        main_y = self.main_last_y if self.main_last_y is not None else 0
        main_w = self.main_last_w or 1200
        main_h = self.main_last_h or 780

        cx = int(main_x + (main_w // 2))
        cy = int(main_y + (main_h // 2))

        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                point = wintypes.POINT(cx, cy)
                MONITOR_DEFAULTTONEAREST = 2
                h_monitor = ctypes.windll.user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
                return h_monitor
            except Exception:
                pass

        # String fallback using the center coordinates
        return f"{int(cx // 1920)}_{int(cy // 1080)}"

    def _get_monitor_work_area(self, h_monitor):
        """Fetches the desktop bounds to prevent spawning windows out of bounds."""
        if sys.platform == "win32" and h_monitor:
            try:
                import ctypes
                from ctypes import wintypes
                class MONITORINFO(ctypes.Structure):
                    _fields_ = [
                        ("cbSize", wintypes.DWORD),
                        ("rcMonitor", wintypes.RECT),
                        ("rcWork", wintypes.RECT),
                        ("dwFlags", wintypes.DWORD),
                    ]
                mi = MONITORINFO()
                mi.cbSize = ctypes.sizeof(MONITORINFO)
                if ctypes.windll.user32.GetMonitorInfoW(h_monitor, ctypes.byref(mi)):
                    return (mi.rcWork.left, mi.rcWork.top, mi.rcWork.right, mi.rcWork.bottom)
            except Exception:
                pass

        try:
            if webview.screens:
                s = webview.screens[0]
                return (0, 0, s.width, s.height)
        except Exception:
            pass

        return (0, 0, 1920, 1080)

    def start(self):
        """Initializes primary windows and starts the PyWebView event loop."""
        def get_b64(path):
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
                except Exception: return ""
            return ""

        s1_b64 = get_b64(SPLASH_1_PATH)
        s2_b64 = get_b64(SPLASH_2_PATH)
        s3_b64 = get_b64(SPLASH_3_PATH)

        splash_html = f"""
        <body style="background:#1A1A1A; color:#FFFFFF; font-family:'Segoe UI', sans-serif; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; overflow:hidden; user-select:none;">
            <div style="text-align:center;">
                <div style="position:relative; width:64px; height:64px; margin: 0 auto 20px;">
                    <img src="{s1_b64}" class="logo logo-1">
                    <img src="{s2_b64}" class="logo logo-2">
                    <img src="{s3_b64}" class="logo logo-3">
                </div>
                <h1 style="font-weight:100; font-size:28px; letter-spacing:4px; margin:0; color:#eee;">CODEMERGER</h1>
                <div style="margin-top:15px; display:flex; align-items:center; justify-content:center;">
                    <div style="width:4px; height:4px; background:#0078D4; border-radius:50%; margin:0 3px; animation: pulse 1.5s infinite ease-in-out;"></div>
                    <p style="color:#0078D4; font-size:11px; margin:0; font-weight:bold; letter-spacing:1px; opacity:0.8; text-transform:uppercase;">Initializing Interface</p>
                </div>
            </div>
            <style>
                .logo {{ position: absolute; top: 0; left: 0; width: 64px; height: 64px; opacity: 0; }}
                .logo-1 {{ opacity: 1; }}
                .logo-2 {{ animation: fade-over 3s linear forwards 1.5s; }}
                .logo-3 {{ animation: fade-over 3s linear forwards 3.5s; }}
                @keyframes fade-over {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
                @keyframes pulse {{ 0%, 100% {{ opacity: 0.3; transform: scale(0.8); }} 50% {{ opacity: 1; transform: scale(1.2); }} }}
            </style>
        </body>
        """

        self.splash_window = webview.create_window(
            "CM-Splash", html=splash_html, width=400, height=280,
            frameless=True, on_top=True, background_color='#1A1A1A'
        )

        # Force window placement to loaded config if available
        main_kwargs = {
            "title": "CodeMerger",
            "url": self.base_url,
            "js_api": self.api,
            "width": self.main_last_w,
            "height": self.main_last_h,
            "min_size": (800, 600),
            "background_color": '#2E2E2E',
            "hidden": True
        }

        if self.main_last_x is not None and self.main_last_y is not None:
            main_kwargs["x"] = self.main_last_x
            main_kwargs["y"] = self.main_last_y

        self.main_window = webview.create_window(**main_kwargs)
        self.api.set_window_manager(self)

        self.main_window.events.minimized += self._on_main_minimized
        self.main_window.events.closing += self._on_main_closing

        try:
            self.main_window.events.moved += self._on_main_moved
            self.main_window.events.resized += self._on_main_resized
            self.main_window.events.restored += self._on_main_restored
            self.main_window.events.maximized += self._on_main_restored
            self.main_window.events.shown += self._on_main_restored
        except AttributeError: pass

        webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
        webview.start(debug=self.dev_mode)

    def _create_compact_window(self):
        if self.compact_window: return
        compact_url = f"{self.base_url}#/compact"
        if not self.dev_mode: compact_url = f"file://{self.base_url}#/compact"

        self.compact_window = webview.create_window(
            "CM-Compact", url=compact_url, js_api=self.api,
            width=100, height=120, min_size=(100, 120),
            frameless=True, on_top=True, hidden=True, background_color='#2E2E2E'
        )
        self.compact_window.events.closing += self._on_compact_closing

    def show_main_and_close_splash(self):
        if self.main_window:
            self.main_window.show()
            import threading
            threading.Timer(0.5, self._update_main_bounds).start()

        if self.splash_window:
            self.splash_window.destroy()
            self.splash_window = None

        if self.monitor:
            self.monitor.update_window(self.main_window)
            if not self.monitor.is_alive(): self.monitor.start()

        self._create_compact_window()

    def _on_main_moved(self, x, y):
        self._update_main_bounds()

    def _on_main_resized(self, width, height):
        self._update_main_bounds()

    def _on_main_restored(self):
        if self._transitioning: return
        self._transitioning = True
        try:
            if self.compact_window: self.compact_window.hide()
            if self.monitor: self.monitor.update_window(self.main_window)
        finally: self._transitioning = False

    def _on_main_minimized(self):
        if self._transitioning: return
        if self.api.app_state.config.get('enable_compact_mode_on_minimize', True):
            self._transitioning = True
            try:
                self.main_window.evaluate_js('window.dispatchEvent(new CustomEvent("cm-close-review"))')
                self.main_window.hide()
                self.show_compact()
            finally: self._transitioning = False

    def _on_main_closing(self):
        self._is_shutting_down = True

        # Save geometry to config before exiting
        try:
            self._update_main_bounds()
            if self.main_last_x is not None and self.main_last_y is not None:
                self.api.app_state.config['main_window_geom'] = {
                    'x': self.main_last_x,
                    'y': self.main_last_y,
                    'w': self.main_last_w,
                    'h': self.main_last_h,
                    'compact_x': self.compact_mode_last_x,
                    'compact_y': self.compact_mode_last_y
                }
                save_config(self.api.app_state.config)
        except Exception as e:
            log.error(f"Failed to save window geometry on exit: {e}")

        if self.compact_window:
            try: self.compact_window.destroy()
            except Exception: pass

    def _on_window_closed(self): pass

    def _on_compact_closing(self):
        if self._is_shutting_down: return
        self.restore_main()
        return False

    def show_compact(self):
        """Displays compact window centered on dashboard or at preserved drag location."""
        if self.compact_window:
            # Ensure we have the latest bounds before calculating centers
            self._update_main_bounds()

            current_main_monitor = self._get_main_window_monitor()

            # First time initialization
            if self.compact_last_monitor_handle is None:
                self.compact_last_monitor_handle = current_main_monitor

            # MONITOR CHANGE DETECTED
            if self.compact_last_monitor_handle != current_main_monitor:
                # Discard preserved position because we are on a new screen
                self.compact_mode_last_x = None
                self.compact_mode_last_y = None
                self.compact_last_monitor_handle = current_main_monitor

            widget_w, widget_h = 100, 120
            mon_x, mon_y, mon_right, mon_bottom = self._get_monitor_work_area(current_main_monitor)

            if self.compact_mode_last_x is not None and self.compact_mode_last_y is not None:
                target_x, target_y = self.compact_mode_last_x, self.compact_mode_last_y
            else:
                # NO ASSIGNED POSITION: Center of current dashboard area
                main_x = self.main_last_x if self.main_last_x is not None else mon_x
                main_y = self.main_last_y if self.main_last_y is not None else mon_y
                main_w = self.main_last_w or 1200
                main_h = self.main_last_h or 780

                target_x = main_x + (main_w // 2) - (widget_w // 2)
                target_y = main_y + (main_h // 2) - (widget_h // 2)

            # Defensive Clamping: Ensure window doesn't bleed off current monitor
            margin = 10
            target_x = max(mon_x + margin, min(target_x, mon_right - widget_w - margin))
            target_y = max(mon_y + margin, min(target_y, mon_bottom - widget_h - margin))

            # CRITICAL: Save the calculated position immediately so the frontend drag logic doesn't start at (0,0)
            self.compact_mode_last_x = target_x
            self.compact_mode_last_y = target_y

            self.compact_window.move(int(target_x), int(target_y))
            self.compact_window.show()
            self.compact_window.move(int(target_x), int(target_y))

            if self.monitor:
                self.monitor.update_window(self.compact_window)

    def restore_main(self):
        """Switch back to the full dashboard."""
        if self._transitioning: return
        self._transitioning = True
        try:
            if self.compact_window: self.compact_window.hide()
            if self.main_window:
                self.main_window.show()
                self.main_window.restore()
                if self.monitor:
                    self.monitor.update_window(self.main_window)
        finally: self._transitioning = False

    def exit_all(self):
        self._is_shutting_down = True
        if self.monitor: self.monitor.update_window(None)
        if self.main_window:
            try: self.main_window.destroy()
            except Exception: pass

def main():
    setup_logging()
    try:
        app_state = AppState()
        project_manager = ProjectManager(load_active_file_extensions)
        api = Api(app_state, project_manager)
        monitor = FileMonitorThread(None, app_state, project_manager)

        dev_mode = "--dev" in sys.argv
        manager = WindowManager(api, monitor, dev_mode=dev_mode)
        manager.start()
    except Exception:
        print("\n[FATAL ERROR] Application failed to start:")
        traceback.print_exc()
        input("\nPress Enter to exit...")
    finally:
        try: monitor.stop()
        except: pass

if __name__ == '__main__':
    main()