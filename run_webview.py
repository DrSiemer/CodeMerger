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
from src.core.utils import load_active_file_extensions, save_config

log = logging.getLogger("CodeMerger")

class WindowManager:
    """
    Coordinates the visibility and lifecycle of the main application window
    and the minimalist compact widget using a persistent window strategy.

    UNIT COORDINATION STRATEGY (PyWebView 5.3+ / Windows DPI Awareness V2):
    - CONSTRUCTOR (create_window): Position (x,y) = PHYSICAL | Size (w,h) = LOGICAL
    - RUNTIME (move, resize): move = LOGICAL | resize = PHYSICAL
    - PROPERTIES (win.x, win.width): All = PHYSICAL
    - EVENTS (moved, resized): All = LOGICAL

    Internal state (main_last_x, etc.) is stored in PHYSICAL pixels.
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
        self._handshake_received = False
        self._stop_failsafe = threading.Event()

        # Timing for minimum splash visibility
        self.start_time = time.time()
        self.MIN_SPLASH_DURATION = 0.8

        # Load persisted geometry (Stored in PHYSICAL units)
        geom = self.api.app_state.config.get('main_window_geom', {})

        self.main_last_x = geom.get('x')
        self.main_last_y = geom.get('y')
        self.main_last_w = geom.get('w', 1200)
        self.main_last_h = geom.get('h', 750)

        # Compact Mode Position (Logical)
        self.compact_mode_last_x = geom.get('compact_x')
        self.compact_mode_last_y = geom.get('compact_y')

        if dev_mode:
            self.base_url = "http://localhost:5173"
        else:
            bundle_dir = get_bundle_dir()
            self.base_url = os.path.abspath(os.path.join(bundle_dir, 'frontend', 'dist', 'index.html'))

        app_version = load_app_version()
        self.updater = Updater(None, self.api.app_state, app_version)

    def _get_scale_factor(self, h_monitor=None):
        """Retrieves the DPI scaling multiplier (e.g. 1.5) for the active monitor."""
        if sys.platform == "win32":
            try:
                if h_monitor is None:
                    h_monitor = self._get_target_monitor_handle()

                if h_monitor:
                    scale_percent = ctypes.c_uint()
                    ctypes.windll.shcore.GetScaleFactorForMonitor(h_monitor, ctypes.byref(scale_percent))
                    return scale_percent.value / 100.0
            except Exception: pass
        return 1.0

    def _get_target_monitor_handle(self):
        """Identifies the monitor handle using Physical probing for accuracy."""
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                if self.main_window:
                    px, py = int(self.main_window.x + 20), int(self.main_window.y + 20)
                else:
                    px = int(ctypes.windll.user32.GetSystemMetrics(0) / 2)
                    py = int(ctypes.windll.user32.GetSystemMetrics(1) / 2)

                point = wintypes.POINT(px, py)
                return ctypes.windll.user32.MonitorFromPoint(point, 2)
            except Exception: pass
        return None

    def _get_monitor_work_area_phys(self, h_monitor):
        """Fetches raw physical desktop bounds for a specific monitor handle."""
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
            except Exception: pass
        return (0, 0, 1920, 1080)

    def start(self):
        """Initializes primary windows using physical centering."""
        def get_b64(path):
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
                except Exception: return ""
            return ""

        splash_html = f"""
        <body style="background:#1A1A1A; color:#FFFFFF; font-family:'Segoe UI', sans-serif; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; overflow:hidden; user-select:none;">
            <div style="text-align:center;">
                <div style="position:relative; width:64px; height:64px; margin: 0 auto 20px;">
                    <img src="{get_b64(SPLASH_1_PATH)}" class="logo logo-1">
                    <img src="{get_b64(SPLASH_2_PATH)}" class="logo logo-2">
                    <img src="{get_b64(SPLASH_3_PATH)}" class="logo logo-3">
                </div>
                <h1 style="font-weight:100; font-size:28px; letter-spacing:4px; margin:0; color:#eee;">CODEMERGER</h1>
                <div style="margin-top:15px; display:flex; align-items:center; justify-content:center;">
                    <div style="width:4px; height:4px; background:#0078D4; border-radius:50%; margin:0 3px; animation: pulse 0.8s infinite ease-in-out;"></div>
                    <p style="color:#0078D4; font-size:11px; margin:0; font-weight:bold; letter-spacing:1px; opacity:0.8; text-transform:uppercase;">Initializing Interface</p>
                </div>
            </div>
            <style>
                .logo {{ position: absolute; top: 0; left: 0; width: 64px; height: 64px; opacity: 0; }}
                .logo-1 {{ opacity: 1; }}
                .logo-2 {{ animation: fade-over 0.6s linear forwards 0.3s; }}
                .logo-3 {{ animation: fade-over 0.6s linear forwards 0.6s; }}
                @keyframes fade-over {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
                @keyframes pulse {{ 0%, 100% {{ opacity: 0.3; transform: scale(0.8); }} 50% {{ opacity: 1; transform: scale(1.2); }} }}
            </style>
        </body>
        """

        h_mon = self._get_target_monitor_handle()
        m_left, m_top, m_right, m_bottom = self._get_monitor_work_area_phys(h_mon)
        scale = self._get_scale_factor(h_mon)
        m_w_phys, m_h_phys = m_right - m_left, m_bottom - m_top

        # Step 1: Splash (Centered Physically)
        s_w_log, s_h_log = 400, 280
        s_x_phys = int(m_left + (m_w_phys - (s_w_log * scale)) / 2)
        s_y_phys = int(m_top + (m_h_phys - (s_h_log * scale)) / 2)

        self.splash_window = webview.create_window(
            "CM-Splash", html=splash_html, width=s_w_log, height=s_h_log,
            x=s_x_phys, y=s_y_phys,
            frameless=True, on_top=True, background_color='#1A1A1A',
            hidden=True
        )

        # Step 2: Main Window (Always center physically on boot)
        info_active = self.api.app_state.config.get('info_mode_active', True)
        m_w_log, m_h_log = 800, 550 if info_active else 500

        m_x_phys = int(m_left + (m_w_phys - (m_w_log * scale)) / 2)
        m_y_phys = int(m_top + (m_h_phys - (m_h_log * scale)) / 2)

        # Passing self.base_url directly triggers PyWebView's internal HTTP server
        # which bypasses file:// CORS restrictions for Vue 3 ES modules.
        self.main_window = webview.create_window(
            "CodeMerger", url=self.base_url, js_api=self.api,
            width=m_w_log, height=m_h_log, # Logical Size
            min_size=(800, m_h_log),
            background_color='#2E2E2E',
            hidden=True, x=m_x_phys, y=m_y_phys # Physical Position
        )
        self.api.set_window_manager(self)

        # Warm-up delay for Splash
        def show_splash_warm():
            time.sleep(0.25)
            if self.splash_window and not self._handshake_received:
                self.splash_window.show()

        threading.Thread(target=show_splash_warm, daemon=True).start()

        self.main_window.events.minimized += self._on_main_minimized
        self.main_window.events.closing += self._on_main_closing

        try:
            self.main_window.events.moved += self._on_main_moved
            self.main_window.events.resized += self._on_main_resized
            self.main_window.events.restored += self._on_main_restored
            self.main_window.events.maximized += self._on_main_restored
            self.main_window.events.shown += self._on_main_restored
        except AttributeError: pass

        def failsafe():
            if self._stop_failsafe.wait(7): return
            if not self._handshake_received:
                self.show_main_and_close_splash()

        threading.Thread(target=failsafe, daemon=True).start()

        webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
        webview.start(gui='edgechromium', debug=self.dev_mode)

    def _create_compact_window(self):
        if self.compact_window: return
        compact_url = f"{self.base_url}#/compact"

        self.compact_window = webview.create_window(
            "CM-Compact", url=compact_url, js_api=self.api,
            width=c.COMPACT_WINDOW_WIDTH_LOGICAL, height=c.COMPACT_WINDOW_HEIGHT_LOGICAL,
            min_size=(10, 10),
            frameless=True, on_top=True, hidden=True, background_color='#2E2E2E'
        )
        self.compact_window.events.closing += self._on_compact_closing

    def show_main_and_close_splash(self):
        """Transition from splash to main interface."""
        if self._handshake_received or self._is_shutting_down: return
        self._handshake_received = True
        self._stop_failsafe.set()

        elapsed = time.time() - self.start_time
        if elapsed < self.MIN_SPLASH_DURATION:
            time.sleep(self.MIN_SPLASH_DURATION - elapsed)

        if self.main_window and self.main_window.hidden:
            self.main_window.show()

        if self.splash_window:
            try: self.splash_window.destroy()
            except Exception: pass
            self.splash_window = None

        if self.monitor:
            self.monitor.update_window(self.main_window)
            if not self.monitor.is_alive(): self.monitor.start()

        self._create_compact_window()

    def _on_main_moved(self, x, y):
        if self.main_window and not self._is_shutting_down:
            self.main_last_x, self.main_last_y = self.main_window.x, self.main_window.y

    def _on_main_resized(self, width, height):
        if self.main_window and not self._is_shutting_down:
            self.main_last_w, self.main_last_h = self.main_window.width, self.main_window.height

    def _on_main_restored(self):
        if self._transitioning or self._is_shutting_down: return
        self._transitioning = True
        try:
            if self.compact_window: self.compact_window.hide()
            if self.monitor: self.monitor.update_window(self.main_window)
        finally: self._transitioning = False

    def _on_main_minimized(self):
        if self._transitioning or self._is_shutting_down: return
        if self.api.app_state.config.get('enable_compact_mode_on_minimize', True):
            self._transitioning = True
            try:
                self.main_window.evaluate_js('window.dispatchEvent(new CustomEvent("cm-close-review"))')
                self.main_window.hide()
                self.show_compact()
            finally: self._transitioning = False

    def _on_main_closing(self):
        if self._is_shutting_down: return
        self._is_shutting_down = True
        self._stop_failsafe.set()

        try:
            if self.main_last_x is not None and self.main_last_y is not None:
                self.api.app_state.config['main_window_geom'] = {
                    'x': int(self.main_last_x), 'y': int(self.main_last_y),
                    'w': int(self.main_last_w), 'h': int(self.main_last_h),
                    'compact_x': int(self.compact_mode_last_x) if self.compact_mode_last_x else None,
                    'compact_y': int(self.compact_mode_last_y) if self.compact_mode_last_y else None
                }
                save_config(self.api.app_state.config)
        except Exception: pass

        for win in [self.compact_window, self.splash_window]:
            if win:
                try: win.destroy()
                except Exception: pass

    def _on_compact_closing(self):
        if self._is_shutting_down: return
        self.restore_main()
        return False

    def show_compact(self):
        """Displays compact window using Hybrid coordination logic."""
        if not self.compact_window or self._is_shutting_down: return

        h_mon = self._get_target_monitor_handle()
        scale = self._get_scale_factor(h_mon)
        m_l, m_t, m_r, m_b = self._get_monitor_work_area_phys(h_mon)

        w_phys, h_phys = int(c.COMPACT_WINDOW_WIDTH_LOGICAL * scale), int(c.COMPACT_WINDOW_HEIGHT_LOGICAL * scale)

        if self.compact_mode_last_x is not None and self.compact_mode_last_y is not None:
            t_x_phys, t_y_phys = int(self.compact_mode_last_x * scale), int(self.compact_mode_last_y * scale)
        else:
            t_x_phys = self.main_last_x + (self.main_last_w / 2) - (w_phys / 2)
            t_y_phys = self.main_last_y + (self.main_last_h / 2) - (h_phys / 2)

        m = int(15 * scale)
        t_x_phys = max(m_l + m, min(t_x_phys, m_r - w_phys - m))
        t_y_phys = max(m_t + m, min(t_y_phys, m_b - h_phys - m))

        # Runtime resize requires Physical units | move requires Logical units
        self.compact_window.resize(w_phys, h_phys)
        self.compact_window.move(int(t_x_phys / scale), int(t_y_phys / scale))
        self.compact_window.show()
        self.compact_window.restore()

        if self.monitor: self.monitor.update_window(self.compact_window)

    def restore_main(self):
        """Switch back to the full dashboard."""
        if self._transitioning or self._is_shutting_down: return
        self._transitioning = True
        try:
            if self.compact_window: self.compact_window.hide()
            if self.main_window:
                self.main_window.show()
                self.main_window.restore()
                if self.monitor: self.monitor.update_window(self.main_window)
        finally: self._transitioning = False

    def exit_all(self):
        self._is_shutting_down = True
        if self.main_window:
            try: self.main_window.destroy()
            except Exception: pass

def main():
    setup_logging()
    monitor = None
    try:
        app_state = AppState()
        project_manager = ProjectManager(load_active_file_extensions)
        api = Api(app_state, project_manager)
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