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
        # Only capture geometry and monitor changes when in NORMAL state.
        # This prevents movement/resizing events triggered by the state-machine
        # animations from polluting the saved restoration target.
        if app.view_manager.current_state == 'normal':
            if app.state() != 'iconic':
                app.view_manager.main_window_geom = (
                    app.winfo_x(), app.winfo_y(),
                    app.winfo_width(), app.winfo_height()
                )
                self.check_for_monitor_change()

    def check_for_monitor_change(self):
        """
        Detects if the window has crossed onto a different physical screen.
        If a monitor change is detected, saved geometries (including compact position)
        are invalidated to ensure the UI remains fully visible and contextually placed.
        """
        app = self.app

        # Do not perform check if the window is minimized
        if app.state() == 'iconic':
            return

        if sys.platform != "win32":
            return

        try:
            import ctypes
            user32 = ctypes.windll.user32
            MONITOR_DEFAULTTONEAREST = 2

            hwnd = app.winfo_id()
            new_monitor_handle = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

            # Initial boot synchronization
            if app.current_monitor_handle is None:
                app.current_monitor_handle = new_monitor_handle
                # Sync ViewManager handle so first minimize doesn't trigger monitor_changed
                app.view_manager.compact_last_monitor_handle = new_monitor_handle
                return

            if new_monitor_handle != app.current_monitor_handle:
                log.info(f"Monitor switch detected. Handle: {app.current_monitor_handle} -> {new_monitor_handle}")
                app.current_monitor_handle = new_monitor_handle

                # Clear standard window geometries (File Manager, etc)
                app.window_geometries.clear()

                # Strictly invalidate the compact mode coordinates when crossing screens.
                # This enforces recalculation on the new screen's workspace.
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