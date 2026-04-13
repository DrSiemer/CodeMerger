import threading

class BaseApi:
    """Provides base state and shared helper methods for the API mixins."""

    def __init__(self, app_state, project_manager):
        # Prefixing with an underscore prevents PyWebView from inspecting this attribute
        # during JS API generation, which avoids a premature DOM evaluation crash.
        self._window_manager = None
        self._color_picker_active = False

        # Stored plan for cross-window handoffs (Compact -> Main)
        self._last_parsed_plan = None

        # Cancellation event for long-running filesystem operations (Project Loading)
        self._load_cancel_event = threading.Event()

        self.app_state = app_state
        self.project_manager = project_manager

    def set_window_manager(self, mgr):
        """Links the Api to the central window orchestration logic."""
        self._window_manager = mgr

    def _format_project_response(self, project_config, status_msg):
        """Helper to format ProjectConfig into a dictionary suitable for JSON serialization."""
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