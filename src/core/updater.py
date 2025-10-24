import json
import webbrowser
import os
import sys
import subprocess
from datetime import datetime
from urllib import request, error
from tkinter import messagebox
from .. import constants as c
from ..core.paths import BUNDLE_DIR

class Updater:
    """
    Handles checking for application updates from a GitHub repository.
    """
    def __init__(self, parent, app_state, current_version):
        self.parent = parent
        self.state = app_state
        self.current_version = current_version
        self.repo_url = c.GITHUB_API_URL

    def _should_check_for_updates(self):
        """
        Determines if an update check should be performed based on user settings
        and the last check date. An update check is performed if it's a new day.
        """
        if not self.state.check_for_updates:
            return False

        last_check_str = self.state.last_update_check
        if not last_check_str:
            return True

        try:
            last_check_date = datetime.fromisoformat(last_check_str).date()
            current_date = datetime.now().date()
            should_check = current_date > last_check_date
            return should_check
        except (ValueError, TypeError) as e:
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

                    latest_version = latest_version_tag.lstrip('v').strip()
                    current_version_normalized = self.current_version.lstrip('v').strip()

                    if self._is_newer(latest_version, current_version_normalized):
                        self._notify_user(data)
                    else:
                        print("  You are on the latest version.")
        except Exception as e:
            print(f"  Updater Error: An exception was caught during the network check: {e}")
            pass
        finally:
            print("  Updating last check date to now.")
            self.state.update_last_check_date()

    def check_for_updates_manual(self):
        """
        Performs a user-initiated update check and provides direct feedback.
        """
        try:
            with request.urlopen(self.repo_url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    latest_version_tag = data.get('tag_name', 'v0.0.0')

                    latest_version = latest_version_tag.lstrip('v').strip()
                    current_version_normalized = self.current_version.lstrip('v').strip()

                    if self._is_newer(latest_version, current_version_normalized):
                        self._notify_user(data)
                    else:
                        messagebox.showinfo(
                            "Up to Date",
                            f"You are running the latest version of CodeMerger ({self.current_version}).",
                            parent=self.parent
                        )
                else:
                    messagebox.showerror(
                        "Update Check Failed",
                        f"Could not check for updates. Server returned status {response.status}.",
                        parent=self.parent
                    )
        except error.URLError as e:
            messagebox.showerror(
                "Update Check Failed",
                f"Could not check for updates. Please check your internet connection.\n\nDetails: {e.reason}",
                parent=self.parent
            )
        except Exception as e:
            messagebox.showerror(
                "Update Check Failed",
                f"An unexpected error occurred while checking for updates.\n\nDetails: {e}",
                parent=self.parent
            )

    def _is_newer(self, latest_str, current_str):
        """
        Compares two version strings (e.g., '1.2.3') and returns True if
        the latest is newer than the current.
        """
        try:
            latest_parts = tuple(map(int, latest_str.split('.')))
            current_parts = tuple(map(int, current_str.split('.')))
            is_newer = latest_parts > current_parts
            print(f"  Version comparison result: {latest_parts} > {current_parts} is {is_newer}")
            return is_newer
        except (ValueError, IndexError) as e:
            print(f"    Updater Version Parse Error: Could not compare '{latest_str}' and '{current_str}'. Details: {e}")
            return False

    def _notify_user(self, release_data):
        """
        Displays a dialog to the user about the available update.
        """
        latest_version = release_data.get('tag_name', 'N/A')
        release_notes = release_data.get('body', 'No release notes available.')

        message = (
            f"A new version of CodeMerger is available!\n\n"
            f"  Your version: {self.current_version}\n"
            f"  Latest version: {latest_version}\n\n"
            f"Release Notes:\n{release_notes}\n\n"
            f"CodeMerger will now close and the update will be downloaded and installed.\n\n"
            "Do you want to proceed?"
        )

        if messagebox.askyesno("Update Available", message, parent=self.parent):
            self.start_update_process(release_data)
        else:
            print("  Update declined :'(")

    def start_update_process(self, release_data):
        """
        Launches the external GUI updater executable and exits the main application.
        """
        assets = release_data.get('assets', [])
        download_url = next((asset.get('browser_download_url') for asset in assets if asset.get('name', '').endswith('_Setup.exe')), None)

        if not download_url:
            messagebox.showerror("Update Error", "Could not find a downloadable installer in the release.", parent=self.parent)
            return

        updater_exe_path = os.path.join(BUNDLE_DIR, "updater_gui.exe")

        if not os.path.exists(updater_exe_path):
             # Fallback for running from a built distribution folder directly
             if getattr(sys, 'frozen', False):
                 base_path = os.path.dirname(sys.executable)
                 updater_exe_path = os.path.join(base_path, "updater_gui.exe")

        if not os.path.exists(updater_exe_path):
            messagebox.showerror("Update Error", f"The updater application is missing and could not be found.\n\nPlease reinstall CodeMerger.", parent=self.parent)
            return

        try:
            pid = os.getpid()

            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.DETACHED_PROCESS

            subprocess.Popen(
                [updater_exe_path, str(pid), download_url],
                creationflags=creationflags,
                close_fds=True
            )

            # Exit the main application
            self.parent.destroy()
            sys.exit(0)

        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to launch the updater process: {e}", parent=self.parent)