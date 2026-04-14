import webview
import logging
from src import constants as c

log = logging.getLogger("CodeMerger")

def create_compact_window(manager):
    """Initializes the frameless compact widget window."""
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
    """Calculates boundaries and places the compact window using Hybrid coordination logic."""
    if not manager.compact_window or manager._is_shutting_down: return

    # 1. Identify Target Monitor
    if manager.compact_mode_last_x is not None and manager.compact_mode_last_y is not None:
        h_mon = manager._get_monitor_from_logical(manager.compact_mode_last_x, manager.compact_mode_last_y)
    else:
        h_mon = manager._get_target_monitor_handle()

    # 2. Get Physical Geometry for this Monitor
    scale = manager._get_scale_factor(h_mon)
    m_l, m_t, m_r, m_b = manager._get_monitor_work_area_phys(h_mon)

    w_phys = int(c.COMPACT_WINDOW_WIDTH_LOGICAL * scale)
    h_phys = int(c.COMPACT_WINDOW_HEIGHT_LOGICAL * scale)

    log.info("[DPI Debug] Compact Placement Logic Triggered:")
    log.info(f"  - Monitor Work Area (Phys): L={m_l}, T={m_t}, R={m_r}, B={m_b}")
    log.info(f"  - Scale Factor: {scale}")
    log.info(f"  - Compact Phys Size: {w_phys}x{h_phys}")

    # 3. Calculate Target Physical Position
    if manager.compact_mode_last_x is not None and manager.compact_mode_last_y is not None:
        log.info(f"  - Mode: Restoring Transient Session Position (Logical {manager.compact_mode_last_x}, {manager.compact_mode_last_y})")
        t_x_phys = int(manager.compact_mode_last_x * scale)
        t_y_phys = int(manager.compact_mode_last_y * scale)
    else:
        log.info("  - Mode: Fallback Center over Main Window")
        log.info(f"  - Main Window Phys: X={manager.main_last_x}, Y={manager.main_last_y}, W={manager.main_last_w}, H={manager.main_last_h}")
        t_x_phys = manager.main_last_x + (manager.main_last_w / 2) - (w_phys / 2)
        t_y_phys = manager.main_last_y + (manager.main_last_h / 2) - (h_phys / 2)

    log.info(f"  - Calculated Physical Target: X={t_x_phys}, Y={t_y_phys}")

    # 4. Clamp to Monitor Work Area
    m = int(15 * scale)
    t_x_phys = max(m_l + m, min(t_x_phys, m_r - w_phys - m))
    t_y_phys = max(m_t + m, min(t_y_phys, m_b - h_phys - m))

    log.info(f"  - Clamped Physical Position: X={t_x_phys}, Y={t_y_phys}")

    # 5. Sync clamped physical coordinates back to logical state to prevent UI drag logic jumps
    manager.compact_mode_last_x = t_x_phys / scale
    manager.compact_mode_last_y = t_y_phys / scale

    exec_x_log = int(manager.compact_mode_last_x)
    exec_y_log = int(manager.compact_mode_last_y)

    log.info(f"  - Final Execution (Logical Units): X={exec_x_log}, Y={exec_y_log}")

    # Runtime resize requires Physical units | move requires Logical units
    manager.compact_window.resize(w_phys, h_phys)
    manager.compact_window.move(exec_x_log, exec_y_log)
    manager.compact_window.show()
    manager.compact_window.restore()

    if manager.monitor: manager.monitor.update_window(manager.compact_window)