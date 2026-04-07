import os
import logging
import base64
from src.core.paths import BUNDLE_DIR

log = logging.getLogger("CodeMerger")

class WindowApi:
    """API methods for managing PyWebView windows and assets."""

    def ensure_window_size(self, width, height):
        """
        Requests the main window to expand to the specified dimensions if it is
        currently smaller. This prevents large modals from being clipped.
        """
        if not self._window_manager or not self._window_manager.main_window:
            return

        win = self._window_manager.main_window
        current_w = win.width
        current_h = win.height

        target_w = max(current_w, width)
        target_h = max(current_h, height)

        if target_w != current_w or target_h != current_h:
            log.info(f"Expanding window to {target_w}x{target_h} to accommodate content.")
            win.resize(target_w, target_h)

    def signal_ui_ready(self):
        """
        Called by the frontend (Vue) once the app is mounted and rendered.
        Triggers the transition from Splash to Main Window.
        """
        if self._window_manager:
            self._window_manager.show_main_and_close_splash()

    def get_image_base64(self, filename):
        """
        Reads an image from the assets directory and returns a Base64 data URL.
        Allows the frontend to use local project assets.
        """
        path = os.path.abspath(os.path.join(BUNDLE_DIR, 'assets', filename))

        if not os.path.exists(path):
            log.error(f"[API] Asset NOT found on disk: {path}")
            return ""

        try:
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                # Determine mime type based on extension
                ext = os.path.splitext(filename)[1].lower().strip('.')
                mime = f"image/{ext}" if ext != 'ico' else "image/x-icon"

                result = f"data:{mime};base64,{encoded_string}"
                return result
        except Exception as e:
            log.error(f"[API] Failed to encode image {filename}: {e}")
            return ""

    def get_compact_window_pos(self):
        """Explicitly returns the screen coordinates of the Compact window."""
        if self._window_manager and self._window_manager.compact_window:
            win = self._window_manager.compact_window
            return {'x': win.x, 'y': win.y}
        return {'x': 0, 'y': 0}

    def restore_main_window(self):
        """Triggers the WindowManager to close the compact view and restore the main window."""
        if self._window_manager:
            self._window_manager.restore_main()
            return True
        return False

    def minimize_window(self):
        """Programmatically minimizes the active window."""
        if self._window_manager and self._window_manager.main_window:
            self._window_manager.main_window.minimize()

    def move_compact_window(self, x, y):
        """Explicitly moves the Compact window to target coordinates."""
        if self._window_manager and self._window_manager.compact_window:
            self._window_manager.compact_window.move(int(x), int(y))
            self._window_manager.compact_mode_last_x = int(x)
            self._window_manager.compact_mode_last_y = int(y)

    def close_app(self):
        """Immediately terminates the application."""
        if self._window_manager:
            self._window_manager.exit_all()