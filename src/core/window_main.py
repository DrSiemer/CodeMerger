import webview
import logging

log = logging.getLogger("CodeMerger")

def create_main_window(manager, m_left, m_top, m_w_phys, m_h_phys, scale):
    """Initializes the primary dashboard window and binds lifecycle events."""
    info_active = manager.api.app_state.config.get('info_mode_active', True)
    m_w_log, m_h_log = 800, 550 if info_active else 500

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

    win.events.minimized += manager._on_main_minimized
    win.events.closing += manager._on_main_closing

    try:
        win.events.moved += manager._on_main_moved
        win.events.resized += manager._on_main_resized
        win.events.restored += manager._on_main_restored
        win.events.maximized += manager._on_main_restored
        win.events.shown += manager._on_main_restored
    except AttributeError:
        pass

    return win