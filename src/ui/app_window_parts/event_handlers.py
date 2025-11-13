import sys
import logging

log = logging.getLogger("CodeMerger")

class EventHandlers:
    def __init__(self, app):
        self.app = app

    def on_app_close(self):
        app = self.app
        log.info("Application closing.")
        app.file_monitor.stop()
        if app.view_manager.compact_mode_window and app.view_manager.compact_mode_window.winfo_exists():
            app.view_manager.compact_mode_window.destroy()
        app.destroy()

    def on_window_configure(self, event):
        app = self.app
        if app.view_manager.current_state == 'normal':
            app.view_manager.main_window_geom = (
                app.winfo_x(), app.winfo_y(),
                app.winfo_width(), app.winfo_height()
            )
            self.check_for_monitor_change()

    def check_for_monitor_change(self):
        app = self.app
        if sys.platform != "win32":
            return

        try:
            import ctypes
            user32 = ctypes.windll.user32
            MONITOR_DEFAULTTONEAREST = 2

            hwnd = app.winfo_id()
            new_monitor_handle = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

            if app.current_monitor_handle is None:
                app.current_monitor_handle = new_monitor_handle
                return

            if new_monitor_handle != app.current_monitor_handle:
                app.current_monitor_handle = new_monitor_handle
                app.window_geometries.clear()
                app.view_manager.invalidate_compact_mode_position()

        except Exception as e:
            log.warning(f"Failed to check for monitor change: {e}")

    def update_responsive_layout(self, event=None):
        app = self.app
        THRESHOLD = 600
        width = app.winfo_width()

        if width > THRESHOLD:
            app.main_content_frame.grid_configure(sticky='', padx=0)
        else:
            app.main_content_frame.grid_configure(sticky='w', padx=(20, 0))