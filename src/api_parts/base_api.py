import threading

class BaseApi:
    """Provides base state and shared helper methods for the API mixins"""

    def __init__(self, app_state, project_manager, newly_added_filetypes=None):
        # Prefixing with an underscore prevents PyWebView from inspecting this attribute
        # during JS API generation, which avoids a premature DOM evaluation crash
        self._window_manager = None
        self._color_picker_active = False

        self._newly_added_filetypes = newly_added_filetypes or []
        self._last_parsed_plan = None
        self._load_cancel_event = threading.Event()
        self._dialog_lock = threading.Lock()

        self.app_state = app_state
        self.project_manager = project_manager

        # Transient state for restoring project after Starter session
        self._previous_project_path = None

    def set_window_manager(self, mgr):
        """Links the Api to the central window orchestration logic"""
        self._window_manager = mgr

    def _broadcast_reload(self):
        """Triggers a global synchronization of project state across all windows"""
        if self._window_manager:
            self._window_manager.broadcast_project_reload()

    def _format_project_response(self, project_config, status_msg):
        """Formats ProjectConfig into a dictionary suitable for JSON serialization"""
        if not project_config:
            return None
        return {
            "path": project_config.base_dir,
            "project_name": project_config.project_name,
            "project_color": project_config.project_color,
            "project_font_color": project_config.project_font_color,
            "active_profile": project_config.active_profile_name,
            "profiles": project_config.get_profile_names(),
            "new_file_count": len(project_config.unknown_files),
            "total_tokens": project_config.total_tokens,
            "selected_files": project_config.selected_files,
            "unknown_files": project_config.unknown_files,
            "expanded_dirs": list(project_config.expanded_dirs),
            "has_instructions": bool(project_config.intro_text or project_config.outro_text),
            "intro_text": project_config.intro_text,
            "outro_text": project_config.outro_text,
            "status_msg": status_msg
        }

    def _show_managed_confirmation(self, title, message):
        """
        Displays a native confirmation dialog centered on the monitor
        Uses a topmost hidden parent to ensure it appears in front of the Compact Mode window
        """
        import tkinter as tk
        from tkinter import messagebox
        from src.core.window_geometry import WindowGeometry

        if not self._dialog_lock.acquire(blocking=False):
            return False

        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            mgr = self._window_manager
            if mgr:
                is_compact = mgr.compact_window and not mgr.compact_window.hidden
                if is_compact and mgr.compact_mode_last_x is not None:
                    h_mon = mgr._get_monitor_from_logical(mgr.compact_mode_last_x, mgr.compact_mode_last_y)
                else:
                    h_mon = mgr._get_target_monitor_handle()

                m_l, m_t, m_r, m_b = mgr._get_monitor_work_area_phys(h_mon)
                scale = mgr._get_scale_factor(h_mon)

                center_x = (m_l + (m_r - m_l) / 2) / scale
                center_y = (m_t + (m_b - m_t) / 2) / scale

                root.geometry(f"+{int(center_x)}+{int(center_y)}")

            result = messagebox.askyesno(title, message, parent=root)
            root.destroy()
            return result
        finally:
            self._dialog_lock.release()