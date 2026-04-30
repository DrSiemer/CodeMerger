import logging
import pyperclip
import webview
import os
from src.core.utils import save_config, load_all_filetypes, save_filetypes
from src.core.registry import save_setting
from src.core import prompts as p

log = logging.getLogger("CodeMerger")

class ConfigApi:
    """API methods handling application settings and configurations."""

    def get_app_config(self):
        """Returns the global application configuration, integrating registry settings."""
        from src.core.utils import is_dev_mode
        config = self.app_state.config.copy()
        config['check_for_updates'] = self.app_state.check_for_updates
        config['is_dev'] = is_dev_mode()
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

            if self._window_manager:
                self._window_manager.on_config_changed(self.app_state.config)

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

    def copy_useful_prompt(self, prompt_type):
        """Copies a specialized prompt to the clipboard."""
        try:
            if prompt_type == 'cleanup':
                pyperclip.copy(p.COMMENT_CLEANUP_PROMPT)
                return "Copied comment cleanup prompt."
            elif prompt_type == 'dead_weight':
                pyperclip.copy(p.DEAD_WEIGHT_PROMPT)
                return "Copied dead weight prompt."
            elif prompt_type == 'dry_up':
                pyperclip.copy(p.DRY_UP_PROMPT)
                return "Copied DRY up code prompt."
            elif prompt_type == 'magic_numbers':
                pyperclip.copy(p.MAGIC_NUMBER_PROMPT)
                return "Copied magic number hunter prompt."
            elif prompt_type == 'brutal_review':
                pyperclip.copy(p.BRUTAL_REVIEW_PROMPT)
                return "Copied brutal review prompt."
            elif prompt_type == 'eli5':
                pyperclip.copy(p.ELI5_PROMPT)
                return "Copied ELI5 breakdown prompt."
            return "Unknown prompt type."
        except Exception as e:
            log.error(f"Failed to copy prompt: {e}")
            return "Failed to copy prompt."

    def select_editor_executable(self):
        """Opens a native file dialog to select the code editor executable."""
        if not self._window_manager or not self._window_manager.main_window:
            return None

        # Windows typically uses .exe; other platforms are more varied
        file_types = ("Executable files (*.exe)", "All files (*.*)") if os.name == 'nt' else ("All files (*.*)",)

        result = self._window_manager.main_window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=file_types
        )

        if result and len(result) > 0:
            return result[0]
        return None