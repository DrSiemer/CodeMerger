import os
import webview
import logging
import time
import threading
from src.core.paths import get_bundle_dir
from src.core.updater import Updater
from src.core.utils import load_app_version, save_config

from src.core.window_geometry import WindowGeometry
from src.core.window_splash import create_splash_window
from src.core.window_main import create_main_window
from src.core.window_compact import create_compact_window, show_compact_window

log = logging.getLogger("CodeMerger")

class WindowManager:
    """
    Coordinates the visibility and lifecycle of application windows
    Uses a persistent window strategy for the minimalist compact widget

    UNIT COORDINATION STRATEGY (PyWebView 5.3+ / Windows DPI Awareness V2):
    - CONSTRUCTOR (create_window): Position (x,y) = PHYSICAL | Size (w,h) = LOGICAL
    - RUNTIME (move, resize): move = LOGICAL | resize = PHYSICAL
    - PROPERTIES (win.x, win.width): All = PHYSICAL
    - EVENTS (moved, resized): All = LOGICAL
    """
    def __init__(self, api, monitor, dev_mode=False, debug_mode=False):
        self.api = api
        self.monitor = monitor
        self.dev_mode = dev_mode
        self.debug_mode = debug_mode
        self.main_window = None
        self.compact_window = None
        self.splash_window = None
        self._is_shutting_down = False
        self._transitioning = False
        self._handshake_received = False
        self._handshake_lock = threading.Lock()
        self._stop_failsafe = threading.Event()
        self._current_main_monitor = None

        # Latch to override minimize behavior for a single event
        self._override_compact_behavior = None

        self.start_time = time.time()
        self.MIN_SPLASH_DURATION = 0.4

        # Stored in PHYSICAL units
        geom = self.api.app_state.config.get('main_window_geom', {})

        self.main_last_x = geom.get('x')
        self.main_last_y = geom.get('y')
        self.main_last_w = geom.get('w', 1200)
        self.main_last_h = geom.get('h', 750)

        # Compact Mode Position is strictly transient and resets every session
        self.compact_mode_last_x = None
        self.compact_mode_last_y = None

        if dev_mode:
            self.base_url = "http://localhost:5173"
        else:
            bundle_dir = get_bundle_dir()
            index_path = os.path.join(bundle_dir, 'frontend', 'dist', 'index.html')
            self.base_url = os.path.abspath(os.path.normpath(index_path))

        app_version = load_app_version()
        self.updater = Updater(self, self.api.app_state, app_version)

    def _get_scale_factor(self, h_monitor=None):
        return WindowGeometry.get_scale_factor(h_monitor, self.main_window, self.main_last_x, self.main_last_y)

    def _get_target_monitor_handle(self):
        return WindowGeometry.get_target_monitor_handle(self.main_window, self.main_last_x, self.main_last_y)

    def _get_monitor_from_logical(self, x_log, y_log):
        return WindowGeometry.get_monitor_from_logical(x_log, y_log, self.main_window, self.main_last_x, self.main_last_y)

    def _get_monitor_work_area_phys(self, h_monitor):
        return WindowGeometry.get_monitor_work_area_phys(h_monitor)

    def start(self):
        """Initializes windows and starts the PyWebView UI loop"""
        h_mon = self._get_target_monitor_handle()
        m_left, m_top, m_right, m_bottom = self._get_monitor_work_area_phys(h_mon)
        scale = self._get_scale_factor(h_mon)
        m_w_phys, m_h_phys = m_right - m_left, m_bottom - m_top

        self.splash_window = create_splash_window(m_left, m_top, m_w_phys, m_h_phys, scale)
        self.main_window = create_main_window(self, m_left, m_top, m_w_phys, m_h_phys, scale)

        self.api.set_window_manager(self)
        self._current_main_monitor = h_mon

        def show_splash_warm():
            time.sleep(0.25)
            if self.splash_window and not self._handshake_received:
                self.splash_window.show()

        threading.Thread(target=show_splash_warm, daemon=True).start()

        def failsafe():
            # Check for engine responsiveness to start UI regardless of handshake signals
            for _ in range(20):
                if self._stop_failsafe.wait(1.0):
                    return

                if self._is_shutting_down or self._handshake_received:
                    return

                if self.main_window:
                    try:
                        if self.main_window.evaluate_js('window.pywebview && window.pywebview.api ? true : false'):
                            self.show_main_and_close_splash(source="Proactive Check")
                            return
                    except Exception:
                        pass

            if not self._handshake_received:
                self.show_main_and_close_splash(source="Failsafe Timeout")

        threading.Thread(target=failsafe, daemon=True).start()

        webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
        webview.start(gui='edgechromium', debug=self.debug_mode)

    def show_main_and_close_splash(self, source="Failsafe"):
        """Transitions visibility from splash screen to main dashboard"""
        with self._handshake_lock:
            if self._handshake_received or self._is_shutting_down:
                return
            self._handshake_received = True

        if source == "Handshake":
            log.info("Frontend handshake received. Transitioning from splash.")
        elif source == "Proactive Check":
            log.info("Proactive check detected active engine. Transitioning from splash.")
        else:
            log.warning(f"Frontend handshake alert ({source}). Triggering show.")
            if self.main_window:
                try:
                    self.main_window.load_url(self.base_url)
                except Exception as e:
                    log.error(f"Failsafe URL reload failed: {e}")

        self._stop_failsafe.set()

        elapsed = time.time() - self.start_time
        if elapsed < self.MIN_SPLASH_DURATION:
            time.sleep(self.MIN_SPLASH_DURATION - elapsed)

        if self.main_window and self.main_window.hidden:
            self.main_window.show()

        if self.splash_window:
            self.splash_window.hide()

            def cleanup_splash():
                time.sleep(5.0)
                if self.splash_window:
                    try: self.splash_window.destroy()
                    except Exception: pass
                    self.splash_window = None

            threading.Thread(target=cleanup_splash, daemon=True).start()

        if self.monitor:
            self.monitor.update_window(self.main_window)
            if not self.monitor.is_alive():
                self.monitor.start()

        create_compact_window(self)

        if self.updater:
            threading.Thread(target=self.updater.check_for_updates, daemon=True).start()

    def _on_main_moved(self, x, y):
        if self.main_window and not self._is_shutting_down:
            try:
                wx, wy = self.main_window.x, self.main_window.y
                if wx < -10000 or wy < -10000:
                    return

                self.main_last_x, self.main_last_y = wx, wy

                current_mon = self._get_target_monitor_handle()
                if current_mon:
                    if self._current_main_monitor is None:
                        self._current_main_monitor = current_mon
                    elif self._current_main_monitor != current_mon:
                        log.info("Main window moved to a different monitor. Resetting compact mode position.")
                        self._current_main_monitor = current_mon
                        self.compact_mode_last_x = None
                        self.compact_mode_last_y = None
            except Exception: pass

    def _on_main_resized(self, width, height):
        if self.main_window and not self._is_shutting_down:
            try:
                wx, wy = self.main_window.x, self.main_window.y
                if wx < -10000 or wy < -10000: return

                ww, wh = self.main_window.width, self.main_window.height
                if ww < 100 or wh < 100: return

                self.main_last_w, self.main_last_h = ww, wh
            except Exception: pass

    def _on_main_restored(self):
        if self._transitioning or self._is_shutting_down: return
        self._transitioning = True
        try:
            if self.compact_window: self.compact_window.hide()
            if self.monitor: self.monitor.update_window(self.main_window)
        finally: self._transitioning = False

    def _on_main_minimized(self):
        if self._transitioning or self._is_shutting_down: return

        should_compact = self.api.app_state.config.get('enable_compact_mode_on_minimize', True)

        if self._override_compact_behavior is not None:
            should_compact = self._override_compact_behavior
            self._override_compact_behavior = None

        if should_compact:
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
                # Save only main window geometry since Compact coordinates are transient
                self.api.app_state.config['main_window_geom'] = {
                    'x': int(self.main_last_x), 'y': int(self.main_last_y),
                    'w': int(self.main_last_w), 'h': int(self.main_last_h)
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
        show_compact_window(self)

    def restore_main(self):
        if self._transitioning or self._is_shutting_down: return
        self._transitioning = True
        try:
            if self.compact_window: self.compact_window.hide()
            if self.main_window:
                self.main_window.show()
                self.main_window.restore()
                if self.monitor: self.monitor.update_window(self.main_window)
        finally: self._transitioning = False

    def minimize_main(self, toggle_compact=False):
        """Triggers main window minimization with optional logic override"""
        if not self.main_window: return

        if toggle_compact:
            current_setting = self.api.app_state.config.get('enable_compact_mode_on_minimize', True)
            self._override_compact_behavior = not current_setting

        self.main_window.minimize()

    def exit_all(self):
        self._is_shutting_down = True
        if self.main_window:
            try: self.main_window.destroy()
            except Exception: pass