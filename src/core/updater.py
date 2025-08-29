import json
import webbrowser
from datetime import datetime, timedelta
from urllib import request, error
from tkinter import messagebox

class Updater:
    """
    Handles checking for application updates from a GitHub repository.
    """
    def __init__(self, parent, app_state, current_version):
        self.parent = parent
        self.state = app_state
        self.current_version = current_version
        self.repo_url = "https://api.github.com/repos/DrSiemer/codemerger/releases/latest"

    def _should_check_for_updates(self):
        """
        Determines if an update check should be performed based on user settings
        and the last check date.
        """
        if not self.state.check_for_updates:
            return False

        last_check_str = self.state.last_update_check
        if not last_check_str:
            return True # Never checked before

        try:
            last_check_date = datetime.fromisoformat(last_check_str)
            return datetime.now() - last_check_date > timedelta(days=1)
        except (ValueError, TypeError):
            # If the date is malformed, it's safer to check
            return True

    def check_for_updates(self):
        """
        Performs the update check if conditions are met and handles the result.
        This is designed to fail silently on network errors.
        """
        if not self._should_check_for_updates():
            return

        try:
            with request.urlopen(self.repo_url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    latest_version_tag = data.get('tag_name', 'v0.0.0')

                    # Normalize versions by removing the 'v' prefix for comparison
                    latest_version = latest_version_tag.lstrip('v')
                    current_version_normalized = self.current_version.lstrip('v')

                    if self._is_newer(latest_version, current_version_normalized):
                        self._notify_user(data)
        except (error.URLError, Exception):
            # Silently fail on network errors or JSON parsing issues
            pass
        finally:
            # Always update the last check date, even if the check fails
            self.state.update_last_check_date()

    def _is_newer(self, latest_str, current_str):
        """
        Compares two version strings (e.g., '1.2.3') and returns True if
        the latest is newer than the current.
        """
        try:
            # This handles versions like '1.2.3' correctly
            latest_parts = tuple(map(int, latest_str.split('.')))
            current_parts = tuple(map(int, current_str.split('.')))
            return latest_parts > current_parts
        except (ValueError, IndexError):
            # If version strings are malformed, assume no update
            return False

    def _notify_user(self, release_data):
        """
        Displays a dialog to the user about the available update.
        """
        latest_version = release_data.get('tag_name', 'N/A')
        release_notes = release_data.get('body', 'No release notes available.')
        release_url = release_data.get('html_url', '')

        message = (
            f"A new version of CodeMerger is available!\n\n"
            f"  Your version: {self.current_version}\n"
            f"  Latest version: {latest_version}\n\n"
            f"Release Notes:\n{release_notes}\n\n"
            f"Would you like to go to the download page?"
        )

        if messagebox.askyesno("Update Available", message, parent=self.parent):
            if release_url:
                webbrowser.open_new_tab(release_url)