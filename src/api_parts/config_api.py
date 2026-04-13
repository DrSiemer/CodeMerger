import logging
import pyperclip
from src.core.utils import save_config, load_all_filetypes, save_filetypes
from src.core.registry import save_setting
from src.core import prompts as p

log = logging.getLogger("CodeMerger")

class ConfigApi:
    """API methods handling application settings and configurations."""

    def get_app_config(self):
        """Returns the global application configuration, integrating registry settings."""
        config = self.app_state.config.copy()
        config['check_for_updates'] = self.app_state.check_for_updates
        return config

    def save_app_config(self, new_config):
        """Saves the application configuration and updates internal state."""
        try:
            if 'check_for_updates' in new_config:
                save_setting('AutomaticUpdates', new_config['check_for_updates'])
                self.app_state.check_for_updates = new_config['check_for_updates']
                del new_config['check_for_updates']

            self.app_state.config.update(new_config)
            save_config(self.app_state.config)
            self.app_state.reload()
            return True
        except Exception as e:
            log.error(f"Error saving config: {e}")
            return False

    def get_newly_added_filetypes(self):
        """Returns the list of filetypes added during the version migration on boot."""
        return self._newly_added_filetypes

    def check_for_updates_manual(self):
        """Triggers a manual update check via the central Updater logic."""
        if self._window_manager and hasattr(self._window_manager, 'updater'):
            self._window_manager.updater.check_for_updates_manual()
            return True
        return False

    def get_filetypes(self):
        """Returns the array of indexed filetypes."""
        return load_all_filetypes()

    def save_filetypes(self, filetypes):
        """Saves the filetypes array to configuration."""
        try:
            save_filetypes(filetypes)
            return True
        except Exception as e:
            log.error(f"Error saving filetypes: {e}")
            return False

    def save_project_instructions(self, intro, outro):
        """Updates the intro and outro instructions for the currently active project."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return None

        project_config.intro_text = intro
        project_config.outro_text = outro
        project_config.save()

        return self._format_project_response(project_config, "Instructions saved successfully.")

    def copy_comment_cleanup_prompt(self):
        """Copies the standard comment cleanup instruction to the clipboard."""
        try:
            pyperclip.copy(p.COMMENT_CLEANUP_PROMPT)
            return "Copied comment cleanup prompt."
        except Exception as e:
            log.error(f"Failed to copy cleanup prompt: {e}")
            return "Failed to copy prompt."