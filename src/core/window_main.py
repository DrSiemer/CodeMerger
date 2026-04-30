import webview
import logging
from src import constants as c

log = logging.getLogger("CodeMerger")

def create_main_window(manager, m_left, m_top, m_w_phys, m_h_phys, scale):
    """Initializes the primary dashboard window and binds lifecycle events."""
    info_active = manager.api.app_state.config.get('info_mode_active', True)
    m_w_log = c.MAIN_WINDOW_WIDTH
    m_h_log = c.MAIN_WINDOW_HEIGHT_INFO_ON if info_active else c.MAIN_WINDOW_HEIGHT_INFO_OFF

    m_x_phys = int(m_left + (m_w_phys - (m_w_log * scale)) / 2)
    m_y_phys = int(m_top + (m_h_phys - (m_h_log * scale)) / 2)

    # Passing the base_url directly triggers PyWebView's internal HTTP server
    # which bypasses file:// CORS restrictions for Vue 3 ES modules
    # Width and height use logical units, x and y use physical position
    win = webview.create_window(
        "CodeMerger", url=manager.base_url, js_api=manager.api,
        width=m_w_log, height=m_h_log,
        min_size=(800, m_h_log),
        background_color='#2E2E2E',
        hidden=True, x=m_x_phys, y=m_y_phys
    )

    win.events.minimized += manager.event_handler.on_main_minimized
    win.events.closing += manager.event_handler.on_main_closing

    try:
        win.events.moved += manager.event_handler.on_main_moved
        win.events.resized += manager.event_handler.on_main_resized
        win.events.restored += manager.event_handler.on_main_restored
        win.events.maximized += manager.event_handler.on_main_maximized
        win.events.shown += manager.event_handler.on_main_shown
    except AttributeError:
        pass

    return win