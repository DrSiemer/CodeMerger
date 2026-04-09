import os
import logging
import base64
from src.core.paths import BUNDLE_DIR

log = logging.getLogger("CodeMerger")

class WindowApi:
    """API methods for managing PyWebView windows and assets."""

    def ensure_window_size(self, width, height):
        """
        Requests the main window to expand to the specified logical dimensions.
        Multiplies requested size by the backend scale factor to ensure it matches
        physical pixel expectations on high-DPI monitors.
        """
        if not self._window_manager or not self._window_manager.main_window:
            return

        win = self._window_manager.main_window
        scale = self._window_manager._get_scale_factor()

        # win.width and win.height report physical pixels on Windows
        current_phys_w = win.width
        current_phys_h = win.height

        # Convert logical pixels from frontend to physical pixels for backend comparison
        target_phys_w = int(width * scale)
        target_phys_h = int(height * scale)

        # Only grow, never shrink
        new_phys_w = max(current_phys_w, target_phys_w)
        new_phys_h = max(current_phys_h, target_phys_h)

        if new_phys_w != current_phys_w or new_phys_h != current_phys_h:
            log.info(f"[UI-Resize] Scaling growth: {current_phys_w}x{current_phys_h} -> {new_phys_w}x{new_phys_h} (Scale: {scale})")
            win.resize(new_phys_w, new_phys_h)
        else:
            log.debug(f"[UI-Resize] Logical {width}x{height} is already met by physical {current_phys_w}x{current_phys_h}")

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
        """
        path = os.path.abspath(os.path.join(BUNDLE_DIR, 'assets', filename))

        if not os.path.exists(path):
            log.error(f"[API] Asset NOT found on disk: {path}")
            return ""

        try:
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                ext = os.path.splitext(filename)[1].lower().strip('.')
                mime = f"image/{ext}" if ext != 'ico' else "image/x-icon"
                return f"data:{mime};base64,{encoded_string}"
        except Exception as e:
            log.error(f"[API] Failed to encode image {filename}: {e}")
            return ""

    def get_compact_window_pos(self):
        """
        Returns the true physical coordinates of the Compact window to initialize drag logic.
        Eliminates the (0,0) jump bug by asking the OS directly if possible.
        """
        if self._window_manager:
            # Source of truth 1: Actual window properties
            if self._window_manager.compact_window:
                x = self._window_manager.compact_window.x
                y = self._window_manager.compact_window.y
                if x is not None and y is not None and x > -30000:
                    return {'x': x, 'y': y}

            # Source of truth 2: Saved persistent state
            x = self._window_manager.compact_mode_last_x
            y = self._window_manager.compact_mode_last_y
            if x is not None and y is not None:
                return {'x': x, 'y': y}

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
        """
        Moves the Compact window and captures coordinates for persistence.
        """
        if self._window_manager and self._window_manager.compact_window:
            new_x, new_y = int(x), int(y)
            self._window_manager.compact_window.move(new_x, new_y)

            # Persist coordinates in the manager state so they survive maximizes/restores
            self._window_manager.compact_mode_last_x = new_x
            self._window_manager.compact_mode_last_y = new_y

    def close_app(self):
        """Immediately terminates the application."""
        if self._window_manager:
            self._window_manager.exit_all()