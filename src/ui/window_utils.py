def position_window(window):
    """
    Calculates the centered position for a window relative to its parent,
    then constrains that position to ensure the window is fully visible.
    """
    window.update_idletasks()  # Ensure window dimensions are calculated

    # Try to get geometry from the saved state first
    window_name = window.__class__.__name__
    if window_name in window.parent.window_geometries:
        window.geometry(window.parent.window_geometries[window_name])
        return

    # If no saved geometry, calculate the centered position
    parent = window.parent
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    win_w = window.winfo_width()
    win_h = window.winfo_height()

    x = parent_x + (parent_w - win_w) // 2
    y = parent_y + (parent_h - win_h) // 2

    # Get screen dimensions and ensure the window is on-screen
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    if x + win_w > screen_w:
        x = screen_w - win_w
    if y + win_h > screen_h:
        y = screen_h - win_h
    if x < 0:
        x = 0
    if y < 0:
        y = 0

    window.geometry(f'+{x}+{y}')

def save_window_geometry(window):
    """Saves the window's current geometry to the parent's registry."""
    window.parent.window_geometries[window.__class__.__name__] = window.geometry()