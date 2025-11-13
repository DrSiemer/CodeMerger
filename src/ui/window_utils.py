import sys
from .. import constants as c

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
            # Determine monitor from a point or window handle
            if isinstance(window, tuple): # It's a point (x, y)
                point = wintypes.POINT(window[0], window[1])
                h_monitor = user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
            else: # It's a window object
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

def _get_default_geometry_for_window(window_class_name):
    """Maps a window's class name to its default geometry string from constants."""
    if window_class_name == 'FileManagerWindow':
        return c.FILE_MANAGER_DEFAULT_GEOMETRY
    if window_class_name == 'SettingsWindow':
        return c.SETTINGS_WINDOW_DEFAULT_GEOMETRY
    if window_class_name == 'FiletypesManagerWindow':
        return c.FILETYPES_WINDOW_DEFAULT_GEOMETRY
    if window_class_name == 'InstructionsWindow':
        return c.INSTRUCTIONS_WINDOW_DEFAULT_GEOMETRY
    # Return None if no specific default is found for this window type
    return None

def position_window(window):
    """
    Calculates and applies the position for a window, ensuring it is always
    fully visible on the screen. It correctly centers on the parent window by
    default and respects saved positions.
    """
    parent = window.parent
    window_name = window.__class__.__name__
    saved_geometry = None
    if hasattr(parent, 'window_geometries'):
        saved_geometry = parent.window_geometries.get(window_name)

    win_w, win_h, x, y = 0, 0, 0, 0

    # --- Step 1: Determine authoritative dimensions and initial position ---
    if saved_geometry:
        try:
            parts = saved_geometry.replace('+', ' ').replace('x', ' ').split()
            if len(parts) == 4:
                win_w, win_h, x, y = map(int, parts)
            else: saved_geometry = None
        except (ValueError, IndexError):
            saved_geometry = None

    if not saved_geometry:
        # First, try to get a predefined default size from constants.
        default_geom_str = _get_default_geometry_for_window(window_name)
        if default_geom_str:
            try:
                size_part = default_geom_str.split('+')[0]
                w_str, h_str = size_part.split('x')
                win_w, win_h = int(w_str), int(h_str)
            except (ValueError, IndexError):
                win_w, win_h = 600, 400 # Fallback for malformed string
        else:
            # If no default string exists, trust the window's self-calculated size.
            window.update_idletasks()
            win_w = window.winfo_width()
            win_h = window.winfo_height()
            if win_w <= 1 or win_h <= 1: # Absolute fallback
                win_w, win_h = 600, 400

        # Now that we have a definitive width and height, calculate the centered position.
        parent.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2

    # --- Step 2: Constrain the position to be fully on-screen ---
    mon_left, mon_top, mon_right, mon_bottom = get_monitor_work_area((x, y))

    # Apply buffers to prevent spawning behind the taskbar or against the screen edges.
    mon_bottom -= 50
    mon_right -= 20
    mon_left += 10
    mon_top += 10

    if x + win_w > mon_right: x = mon_right - win_w
    if y + win_h > mon_bottom: y = mon_bottom - win_h
    if x < mon_left: x = mon_left
    if y < mon_top: y = mon_top

    # --- Step 3: Apply the final, fully calculated geometry ---
    window.geometry(f"{win_w}x{win_h}+{x}+{y}")

def save_window_geometry(window):
    """Saves the window's current geometry to the parent's registry."""
    if window.state() == 'normal' and hasattr(window.parent, 'window_geometries'):
        window.parent.window_geometries[window.__class__.__name__] = window.geometry()