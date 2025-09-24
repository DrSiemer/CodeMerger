import sys

# Platform-specific logic for getting monitor info
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    # Define necessary structures and constants from the Windows API
    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork", wintypes.RECT),
            ("dwFlags", wintypes.DWORD),
        ]

    MONITOR_DEFAULTTONEAREST = 2

    # Load the user32 library
    user32 = ctypes.windll.user32

def get_monitor_work_area(window):
    """
    Gets the work area of the monitor that the given window is on.
    Returns a tuple (left, top, right, bottom).
    Provides a fallback for non-Windows platforms.
    """
    if sys.platform == "win32":
        try:
            hwnd = window.winfo_id()
            h_monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
            monitor_info = MONITORINFO()
            monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
            if user32.GetMonitorInfoW(h_monitor, ctypes.byref(monitor_info)):
                work_area = monitor_info.rcWork
                return (work_area.left, work_area.top, work_area.right, work_area.bottom)
        except Exception:
            # Fallback on API failure
            pass

    # Fallback for non-Windows or if API calls fail
    return (0, 0, window.winfo_screenwidth(), window.winfo_screenheight())

def position_window(window):
    """
    Calculates the position for a window, preferring a saved position. If no
    saved position is available, it centers the window on its parent. Finally,
    it constrains the position to ensure the window is fully visible on the
    target monitor.
    """
    window.update_idletasks()  # Ensure window dimensions are up-to-date

    parent = window.parent
    win_w = window.winfo_width()
    win_h = window.winfo_height()

    x, y = 0, 0
    use_saved_geometry = False

    # --- Step 1: Try to use saved geometry ---
    window_name = window.__class__.__name__
    saved_geometry = parent.window_geometries.get(window_name)

    if saved_geometry:
        try:
            parts = saved_geometry.replace('+', ' ').replace('x', ' ').split()
            saved_x, saved_y = int(parts[2]), int(parts[3])
            x, y = saved_x, saved_y
            use_saved_geometry = True
        except (ValueError, IndexError):
            use_saved_geometry = False # Fallback to centering if parsing fails

    if not use_saved_geometry:
        # Fallback: Center on parent if no valid saved geometry
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2

    # --- Step 2: Constrain the calculated position to be fully on-screen ---
    if sys.platform == "win32":
        try:
            h_monitor = None
            # If centering, the reference monitor MUST be the parent's.
            if not use_saved_geometry:
                parent_hwnd = parent.winfo_id()
                h_monitor = user32.MonitorFromWindow(parent_hwnd, MONITOR_DEFAULTTONEAREST)
            # If using a saved position, the reference monitor is where that point is.
            else:
                target_point = wintypes.POINT(x, y)
                h_monitor = user32.MonitorFromPoint(target_point, MONITOR_DEFAULTTONEAREST)

            monitor_info = MONITORINFO()
            monitor_info.cbSize = ctypes.sizeof(MONITORINFO)

            if user32.GetMonitorInfoW(h_monitor, ctypes.byref(monitor_info)):
                # Use the work area of the correct monitor for bounds checking
                monitor_work_area = monitor_info.rcWork
                screen_x_min, screen_y_min = monitor_work_area.left, monitor_work_area.top
                screen_x_max, screen_y_max = monitor_work_area.right, monitor_work_area.bottom

                # Constrain the window to the monitor's work area
                if x + win_w > screen_x_max: x = screen_x_max - win_w
                if y + win_h > screen_y_max: y = screen_y_max - win_h
                if x < screen_x_min: x = screen_x_min
                if y < screen_y_min: y = screen_y_min

                window.geometry(f'+{x}+{y}')
                return # Exit after successful positioning
        except Exception:
            # Fallback if API calls fail
            pass

    # --- Fallback for non-Windows or if API calls fail ---
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    if x + win_w > screen_w: x = screen_w - win_w
    if y + win_h > screen_h: y = screen_h - win_h
    if x < 0: x = 0
    if y < 0: y = 0

    window.geometry(f'+{x}+{y}')

def save_window_geometry(window):
    """Saves the window's current geometry to the parent's registry."""
    window.parent.window_geometries[window.__class__.__name__] = window.geometry()