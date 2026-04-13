import sys

class WindowGeometry:
    """Provides stateless utility functions for Windows High-DPI physical math."""

    @staticmethod
    def get_target_monitor_handle(main_window, main_last_x, main_last_y):
        """Identifies the monitor handle using Physical probing for accuracy."""
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                wx, wy = 0, 0
                if main_window:
                    try:
                        wx, wy = main_window.x, main_window.y
                    except Exception:
                        pass

                # Prevent probing minimize coordinates (-32000)
                if main_window and wx > -10000 and wy > -10000:
                    px, py = int(wx + 20), int(wy + 20)
                elif main_last_x is not None and main_last_y is not None:
                    px, py = int(main_last_x + 20), int(main_last_y + 20)
                else:
                    px = int(ctypes.windll.user32.GetSystemMetrics(0) / 2)
                    py = int(ctypes.windll.user32.GetSystemMetrics(1) / 2)

                point = wintypes.POINT(px, py)
                return ctypes.windll.user32.MonitorFromPoint(point, 2)
            except Exception: pass
        return None

    @staticmethod
    def get_scale_factor(h_monitor=None, main_window=None, main_last_x=None, main_last_y=None):
        """Retrieves the DPI scaling multiplier (e.g. 1.5) for the active monitor."""
        if sys.platform == "win32":
            try:
                import ctypes
                if h_monitor is None:
                    h_monitor = WindowGeometry.get_target_monitor_handle(main_window, main_last_x, main_last_y)

                if h_monitor:
                    scale_percent = ctypes.c_uint()
                    ctypes.windll.shcore.GetScaleFactorForMonitor(h_monitor, ctypes.byref(scale_percent))
                    return scale_percent.value / 100.0
            except Exception: pass
        return 1.0

    @staticmethod
    def get_monitor_from_logical(x_log, y_log, main_window=None, main_last_x=None, main_last_y=None):
        """Identifies the monitor handle containing a specific logical coordinate."""
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                monitors = []
                def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
                    monitors.append(hMonitor)
                    return 1

                MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
                ctypes.windll.user32.EnumDisplayMonitors(0, None, MonitorEnumProc(callback), 0)

                for h_mon in monitors:
                    scale = WindowGeometry.get_scale_factor(h_mon, main_window, main_last_x, main_last_y)
                    m_l, m_t, m_r, m_b = WindowGeometry.get_monitor_work_area_phys(h_mon)

                    if (m_l / scale) <= x_log <= (m_r / scale) and (m_t / scale) <= y_log <= (m_b / scale):
                        return h_mon

                # Fallback physical guess
                point = wintypes.POINT(int(x_log), int(y_log))
                return ctypes.windll.user32.MonitorFromPoint(point, 2)
            except Exception: pass
        return WindowGeometry.get_target_monitor_handle(main_window, main_last_x, main_last_y)

    @staticmethod
    def get_monitor_work_area_phys(h_monitor):
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