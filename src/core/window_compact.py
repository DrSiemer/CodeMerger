import webview
import logging
import sys
from src import constants as c

log = logging.getLogger("CodeMerger")

def _set_skip_taskbar(title):
    """
    Win32 implementation to strip the taskbar button from the compact widget.
    This ensures the app's taskbar presence remains anchored to the minimized Main Window.
    """
    if sys.platform == "win32":
        try:
            import ctypes
            # Using the window title to find the HWND
            hwnd = ctypes.windll.user32.FindWindowW(None, title)
            if hwnd:
                GWL_EXSTYLE = -20
                WS_EX_TOOLWINDOW = 0x00000080
                WS_EX_APPWINDOW = 0x00040000

                # Get current extended style
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

                # WS_EX_TOOLWINDOW hides from taskbar and Alt-Tab
                # WS_EX_APPWINDOW forces a taskbar button even for hidden/tool windows
                new_style = (style & ~WS_EX_APPWINDOW) | WS_EX_TOOLWINDOW

                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
        except Exception as e:
            log.debug(f"Failed to set skip taskbar style: {e}")

def create_compact_window(manager):
    """Initializes the frameless compact widget window"""
    if manager.compact_window: return
    compact_url = f"{manager.base_url}#/compact"

    manager.compact_window = webview.create_window(
        "CM-Compact", url=compact_url, js_api=manager.api,
        width=c.COMPACT_WINDOW_WIDTH_LOGICAL, height=c.COMPACT_WINDOW_HEIGHT_LOGICAL,
        min_size=(10, 10),
        frameless=True, on_top=True, hidden=True, background_color='#2E2E2E'
    )
    manager.compact_window.events.closing += manager._on_compact_closing

def show_compact_window(manager):
    """Calculates boundaries and places the compact window using Hybrid coordination logic"""
    if not manager.compact_window or manager._is_shutting_down: return

    if manager.compact_mode_last_x is not None and manager.compact_mode_last_y is not None:
        h_mon = manager._get_monitor_from_logical(manager.compact_mode_last_x, manager.compact_mode_last_y)
    else:
        h_mon = manager._get_target_monitor_handle()

    scale = manager._get_scale_factor(h_mon)
    m_l, m_t, m_r, m_b = manager._get_monitor_work_area_phys(h_mon)

    w_phys = int(c.COMPACT_WINDOW_WIDTH_LOGICAL * scale)
    h_phys = int(c.COMPACT_WINDOW_HEIGHT_LOGICAL * scale)

    if manager.compact_mode_last_x is not None and manager.compact_mode_last_y is not None:
        t_x_phys = int(manager.compact_mode_last_x * scale)
        t_y_phys = int(manager.compact_mode_last_y * scale)
    else:
        t_x_phys = manager.main_last_x + (manager.main_last_w / 2) - (w_phys / 2)
        t_y_phys = manager.main_last_y + (manager.main_last_h / 2) - (h_phys / 2)

    m = int(15 * scale)
    t_x_phys = max(m_l + m, min(t_x_phys, m_r - w_phys - m))
    t_y_phys = max(m_t + m, min(t_y_phys, m_b - h_phys - m))

    # Sync clamped physical coordinates back to logical state to prevent UI drag logic jumps
    manager.compact_mode_last_x = t_x_phys / scale
    manager.compact_mode_last_y = t_y_phys / scale

    exec_x_log = int(manager.compact_mode_last_x)
    exec_y_log = int(manager.compact_mode_last_y)

    # Ensure Vue has rendered the state in the background buffer
    manager._dispatch_project_reload(manager.compact_window)

    # Runtime resize consumes physical units while move consumes logical units
    # Due to a PyWebView High-DPI quirk on Windows, we must use physical pixels for resizing but logical pixels for moving
    manager.compact_window.resize(w_phys, h_phys)
    manager.compact_window.move(exec_x_log, exec_y_log)
    manager.compact_window.show()

    # Rule: Prevent taskbar icon jumping by ensuring the widget has no taskbar presence
    _set_skip_taskbar("CM-Compact")

    manager.compact_window.restore()

    if manager.monitor: manager.monitor.update_window(manager.compact_window)