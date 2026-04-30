import logging
from src.api_parts.starter_api_session import StarterApiSession
from src.api_parts.starter_api_prompts import StarterApiPrompts
from src.api_parts.starter_api_parsing import StarterApiParsing
from src.api_parts.starter_api_scaffold import StarterApiScaffold

log = logging.getLogger("CodeMerger")

class StarterApi(
    StarterApiSession,
    StarterApiPrompts,
    StarterApiParsing,
    StarterApiScaffold
):
    """API methods concerning the comprehensive Project Starter feature pipeline."""

    def on_starter_open(self):
        """Initializes starter session: deactivates current project and disables compact mode."""
        self._previous_project_path = self.app_state.active_directory
        if self._previous_project_path:
            # Requirements: Project Starter should deactivate the current model
            self.load_project(None)

        if self._window_manager:
            self._window_manager.is_starter_active = True
        return True

    def on_starter_close(self, project_created=False):
        """Finalizes starter session: restores previous project if needed and re-enables compact mode."""
        if self._window_manager:
            self._window_manager.is_starter_active = False

        # Ensure the shared AI response memory is cleared to prevent scaffolding leaks
        self.clear_parsed_plan()

        # Requirements: reactivate the project on close unless activating a created project
        if not project_created and self._previous_project_path:
            self.load_project(self._previous_project_path)

        self._previous_project_path = None
        return True

    def test(self):
        """A simple test method to verify the Vue -> Python bridge is working."""
        log.info("API test method called from Vue frontend.")
        return "Hello from Python API! The bridge is working perfectly."