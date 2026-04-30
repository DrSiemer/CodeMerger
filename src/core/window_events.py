import os
import time
import threading
import logging

log = logging.getLogger("CodeMerger")

class WindowEventHandler:
    """Handles PyWebView native window lifecycle events."""
    def __init__(self, manager):
        self.manager = manager

    def on_main_moved(self, x, y):
        if self.manager.main_window and not self.manager._is_shutting_down:
            try:
                if getattr(self.manager, 'main_is_maximized', False):
                    return

                wx, wy = self.manager.main_window.x, self.manager.main_window.y
                if wx < -10000 or wy < -10000:
                    return

                self.manager.main_last_x, self.manager.main_last_y = wx, wy

                current_mon = self.manager._get_target_monitor_handle()
                if current_mon:
                    if self.manager._current_main_monitor is None:
                        self.manager._current_main_monitor = current_mon
                    elif self.manager._current_main_monitor != current_mon:
                        self.manager._current_main_monitor = current_mon
            except Exception: pass

    def on_main_resized(self, width, height):
        if self.manager.main_window and not self.manager._is_shutting_down:
            try:
                if getattr(self.manager, 'main_is_maximized', False):
                    return

                wx, wy = self.manager.main_window.x, self.manager.main_window.y
                if wx < -10000 or wy < -10000: return

                ww, wh = self.manager.main_window.width, self.manager.main_window.height
                if ww < 100 or wh < 100: return

                self.manager.main_last_w, self.manager.main_last_h = ww, wh
            except Exception: pass

    def on_main_restored(self):
        self.manager.main_is_maximized = False
        if self.manager._transitioning or self.manager._is_shutting_down: return
        self.manager._transitioning = True
        try:
            if self.manager.compact_window:
                try:
                    self.manager.compact_window.move(-10000, -10000)
                except Exception: pass
                self.manager.compact_window.hide()
            if self.manager.main_window:
                self.manager.broadcast_project_reload()
            if self.manager.monitor: self.manager.monitor.update_window(self.manager.main_window)
        finally: self.manager._transitioning = False

    def on_main_maximized(self):
        self.manager.main_is_maximized = True
        if self.manager._transitioning or self.manager._is_shutting_down: return
        self.manager._transitioning = True
        try:
            if self.manager.compact_window:
                try:
                    self.manager.compact_window.move(-10000, -10000)
                except Exception: pass
                self.manager.compact_window.hide()
            if self.manager.main_window:
                self.manager.broadcast_project_reload()
            if self.manager.monitor: self.manager.monitor.update_window(self.manager.main_window)
        finally: self.manager._transitioning = False

    def on_main_shown(self):
        if self.manager._transitioning or self.manager._is_shutting_down: return
        self.manager._transitioning = True
        try:
            if self.manager.compact_window:
                try:
                    self.manager.compact_window.move(-10000, -10000)
                except Exception: pass
                self.manager.compact_window.hide()
            if self.manager.main_window:
                self.manager.broadcast_project_reload()
            if self.manager.monitor: self.manager.monitor.update_window(self.manager.main_window)
        finally: self.manager._transitioning = False

    def on_main_minimized(self):
        if self.manager._transitioning or self.manager._is_shutting_down: return

        # Requirement: Project Starter should never minimize to Compact Mode
        if self.manager.is_starter_active:
            return

        should_compact = self.manager.api.app_state.config.get('enable_compact_mode_on_minimize', False)

        if self.manager._override_compact_behavior is not None:
            should_compact = self.manager._override_compact_behavior
            self.manager._override_compact_behavior = None

        if should_compact:
            self.manager._transitioning = True
            try:
                if self.manager.main_window:
                    try:
                        self.manager.main_window.evaluate_js('window.dispatchEvent(new CustomEvent("cm-close-review"))')
                    except Exception:
                        pass
                self.manager.show_compact()
            finally:
                self.manager._transitioning = False

    def on_main_closing(self):
        # Performs a final reconciled save of state and geometry on shutdown
        if self.manager._is_shutting_down: return
        self.manager._is_shutting_down = True
        self.manager._stop_failsafe.set()

        # Exit Watchdog ensures the process dies if the WebView engine hangs during teardown
        def _force_exit_watchdog():
            time.sleep(1.5)
            os._exit(0)
        threading.Thread(target=_force_exit_watchdog, daemon=True).start()

        try:
            # Sync final window geometry to internal config dict before reconciled save
            if self.manager.main_last_x is not None and self.manager.main_last_y is not None:
                self.manager.api.app_state.config['main_window_geom'] = {
                    'x': int(self.manager.main_last_x), 'y': int(self.manager.main_last_y),
                    'w': int(self.manager.main_last_w), 'h': int(self.manager.main_last_h),
                    'is_maximized': getattr(self.manager, 'main_is_maximized', False)
                }

            # Execute reconciled save to implement "Last Closed Wins" for Active Project
            self.manager.api.app_state._save()
        except Exception: pass

        for win in [self.manager.compact_window, self.manager.splash_window]:
            if win:
                try: win.destroy()
                except Exception: pass

    def on_compact_closing(self):
        if self.manager._is_shutting_down: return True
        self.manager.restore_main()
        return False