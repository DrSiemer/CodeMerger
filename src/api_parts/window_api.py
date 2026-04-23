import os
import logging
import base64
import threading
from src.core.paths import BUNDLE_DIR

log = logging.getLogger("CodeMerger")

class WindowApi:
    """API methods for managing PyWebView windows and assets"""

    def restore_main_window_and_trigger_fm(self):
        """Transitions from compact widget to main dashboard and triggers file manager."""
        if self._window_manager:
            self._window_manager.restore_main(trigger_fm=True)
            return True
        return False

    def trigger_file_manager_in_main(self):
        """Forces the main window to open the File Manager."""
        if self._window_manager:
            self._window_manager.trigger_file_manager_in_main()

    def ensure_window_size(self, width, height):
        """
        Requests the main window to expand to specified dimensions
        Logic performed in Physical space; Move requires Logical units while Resize requires Physical units
        """
        if not self._window_manager or not self._window_manager.main_window:
            return

        mgr = self._window_manager
        win = mgr.main_window

        try:
            curr_w_phys = win.width
            curr_h_phys = win.height
            curr_x_phys = win.x
            curr_y_phys = win.y
        except Exception:
            return

        if curr_w_phys is None or curr_h_phys is None or curr_x_phys is None or curr_y_phys is None:
            return

        if curr_x_phys < -10000 or curr_y_phys < -10000:
            return

        h_mon = mgr._get_target_monitor_handle()
        m_l_phys, m_t_phys, m_r_phys, m_b_phys = mgr._get_monitor_work_area_phys(h_mon)
        scale = mgr._get_scale_factor(h_mon)

        m_w_phys, m_h_phys = m_r_phys - m_l_phys, m_b_phys - m_t_phys

        target_w_phys = int(width * scale)
        target_h_phys = int(height * scale)

        # Safety Clamp against monitor resolution (10px logical margin)
        margin_phys = int(10 * scale)
        max_allowed_w = m_w_phys - (margin_phys * 2)
        max_allowed_h = m_h_phys - (margin_phys * 2)

        if target_w_phys > max_allowed_w:
            target_w_phys = max_allowed_w
        if target_h_phys > max_allowed_h:
            target_h_phys = max_allowed_h

        applied_w_phys = max(curr_w_phys, target_w_phys)
        applied_h_phys = max(curr_h_phys, target_h_phys)

        if applied_w_phys <= curr_w_phys and applied_h_phys <= curr_h_phys:
            return

        # Purposeful choice: grow the window outwards from its current center
        center_x_phys = curr_x_phys + (curr_w_phys // 2)
        center_y_phys = curr_y_phys + (curr_h_phys // 2)

        new_x_phys = center_x_phys - (applied_w_phys // 2)
        new_y_phys = center_y_phys - (applied_h_phys // 2)

        # Overlapping-edge enforcement system
        # 1. Right/Bottom checks (may push window Left/Up to stay in bounds)
        if new_x_phys + applied_w_phys > m_r_phys - margin_phys:
            new_x_phys = (m_r_phys - margin_phys) - applied_w_phys
        if new_y_phys + applied_h_phys > m_b_phys - margin_phys:
            new_y_phys = (m_b_phys - margin_phys) - applied_h_phys

        # 2. Left/Top checks (may push window Right/Down - ABSOLUTE PRIORITY)
        # This second pass ensures that even if stage 1 pushed the window up, the title bar
        # is never sacrificed. If the window is too big for the screen, the bottom overflows.
        if new_x_phys < m_l_phys + margin_phys:
            new_x_phys = m_l_phys + margin_phys
        if new_y_phys < m_t_phys + margin_phys:
            new_y_phys = m_t_phys + margin_phys

        # HYBRID DOMAIN EXECUTION
        exec_w_phys = int(applied_w_phys)
        exec_h_phys = int(applied_h_phys)
        exec_x_log = int(new_x_phys / scale)
        exec_y_log = int(new_y_phys / scale)

        win.move(exec_x_log, exec_y_log)

        def apply_resize_sequenced():
            if win:
                try:
                    win.resize(exec_w_phys, exec_h_phys)
                except Exception:
                    pass

        threading.Timer(0.02, apply_resize_sequenced).start()

        mgr.main_last_w, mgr.main_last_h = applied_w_phys, applied_h_phys
        mgr.main_last_x, mgr.main_last_y = new_x_phys, new_y_phys

    def signal_ui_ready(self):
        if self._window_manager:
            self._window_manager.show_main_and_close_splash(source="Handshake")

    def get_image_base64(self, filename):
        """Reads image from assets and returns as Base64 data URL"""
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
        """Returns logical coordinates for initializing JS drag logic"""
        mgr = self._window_manager
        if not mgr:
            return {'x': 0, 'y': 0}

        # Primary: use the logical tracking variables if they have been initialized
        if mgr.compact_mode_last_x is not None and mgr.compact_mode_last_y is not None:
            return {'x': mgr.compact_mode_last_x, 'y': mgr.compact_mode_last_y}

        # Fallback: Query live physical coordinates and convert to logical
        if mgr.compact_window:
            try:
                xp, yp = mgr.compact_window.x, mgr.compact_window.y
                if xp > -10000:
                    scale = mgr._get_scale_factor()
                    return {'x': xp / scale, 'y': yp / scale}
            except Exception:
                pass

        return {'x': 0, 'y': 0}

    def restore_main_window(self):
        """Transitions from compact widget to main dashboard"""
        if self._window_manager:
            self._window_manager.restore_main()
            return True
        return False

    def minimize_window(self, toggle=False):
        """Programmatically minimizes the window with optional logic override"""
        if self._window_manager:
            self._window_manager.minimize_main(toggle_compact=toggle)

    def move_compact_window(self, x, y):
        """Updates compact window position using Logical coordinates"""
        if self._window_manager and self._window_manager.compact_window:
            self._window_manager.compact_window.move(int(x), int(y))
            self._window_manager.compact_mode_last_x = x
            self._window_manager.compact_mode_last_y = y

    def close_app(self):
        """Terminates the application"""
        if self._window_manager:
            self._window_manager.exit_all()