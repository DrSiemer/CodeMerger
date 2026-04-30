import json
import os
import sys
import subprocess
import logging
import tkinter as tk
from datetime import datetime
from urllib import request, error
from tkinter import messagebox
from .. import constants as c
from ..core.paths import BUNDLE_DIR

log = logging.getLogger("CodeMerger")

class Updater:
    """
    Handles checking for application updates from a GitHub repository.
    Strictly Windows-only implementation.
    """
    def __init__(self, parent, app_state, current_version):
        self.parent = parent
        self.state = app_state
        self.current_version = current_version
        self.repo_url = c.GITHUB_API_URL

    def _get_dialog_parent(self):
        # Forces a hidden Tk root to the top so messageboxes appear over the PyWebView window
        if self.parent and hasattr(self.parent, 'winfo_exists') and self.parent.winfo_exists():
            return self.parent

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.lift()
        return root

    def _should_check_for_updates(self):
        """Determines if an update check is required today"""
        if not self.state.check_for_updates:
            log.info("Update check skipped: disabled by user setting.")
            return False

        last_check_str = self.state.last_update_check
        if not last_check_str:
            log.info("Performing first-time update check.")
            return True

        try:
            last_check_date = datetime.fromisoformat(last_check_str).date()
            current_date = datetime.now().date()
            should_check = current_date > last_check_date
            if should_check:
                log.info("Performing daily update check.")
            return should_check
        except (ValueError, TypeError) as e:
            log.warning(f"Could not parse last update check date '{last_check_str}'. Performing check. Error: {e}")
            return True

    def check_for_updates(self):
        """Performs update check and notifies user of new releases"""
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
                        log.info(f"Application is up to date (current: {self.current_version}).")
                else:
                    log.warning(f"Update check failed: Server returned status {response.status}.")
        except Exception as e:
            log.error(f"Update check failed with a network error: {e}", exc_info=False)
            pass
        finally:
            log.info("Updating last check date to now.")
            self.state.update_last_check_date()

    def check_for_updates_manual(self):
        """Performs a user-initiated update check and provides direct feedback"""
        log.info("Performing manual update check.")
        dialog_root = self._get_dialog_parent()
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
                            parent=dialog_root
                        )
                else:
                    messagebox.showerror(
                        "Update Check Failed",
                        f"Could not check for updates. Server returned status {response.status}.",
                        parent=dialog_root
                    )
        except error.URLError as e:
            log.error(f"Manual update check failed: {e.reason}")
            messagebox.showerror(
                "Update Check Failed",
                f"Could not check for updates. Please check your internet connection.\n\nDetails: {e.reason}",
                parent=dialog_root
            )
        except Exception as e:
            log.exception("An unexpected error occurred during manual update check.")
            messagebox.showerror(
                "Update Check Failed",
                f"An unexpected error occurred while checking for updates.\n\nDetails: {e}",
                parent=dialog_root
            )
        finally:
            if dialog_root != self.parent:
                dialog_root.destroy()

    def _is_newer(self, latest_str, current_str):
        """Compares version tuples to identify newer releases"""
        try:
            latest_parts = tuple(map(int, latest_str.split('.')))
            current_parts = tuple(map(int, current_str.split('.')))
            is_newer = latest_parts > current_parts
            log.info(f"Version comparison: latest={latest_parts} > current={current_parts} is {is_newer}")
            return is_newer
        except (ValueError, IndexError) as e:
            log.error(f"Could not parse version strings for comparison: latest='{latest_str}', current='{current_str}'. Error: {e}")
            return False

    def _notify_user(self, release_data):
        """Prompts the user to install available updates"""
        latest_version = release_data.get('tag_name', 'N/A')
        release_notes = release_data.get('body', 'No release notes available.')
        log.info(f"New version available: {latest_version}. Prompting user to update.")

        message = (
            f"A new version of CodeMerger is available!\n\n"
            f"  Your version: {self.current_version}\n"
            f"  Latest version: {latest_version}\n\n"
            f"Release Notes:\n{release_notes}\n\n"
            f"CodeMerger will now close and the update will be downloaded and installed.\n\n"
            "Do you want to proceed?"
        )

        dialog_root = self._get_dialog_parent()
        if messagebox.askyesno("Update Available", message, parent=dialog_root):
            self.start_update_process(release_data)
        else:
            log.info("User declined the update.")

    def start_update_process(self, release_data):
        """Launches external GUI updater and terminates main application immediately"""
        assets = release_data.get('assets', [])
        download_url = next((asset.get('browser_download_url') for asset in assets if asset.get('name', '').endswith('_Setup.exe')), None)

        if not download_url:
            log.error("Could not find a downloadable setup file in the latest release assets.")
            dialog_root = self._get_dialog_parent()
            messagebox.showerror("Update Error", "Could not find a downloadable installer in the release.", parent=dialog_root)
            return

        updater_exe_path = ""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            updater_exe_path = os.path.join(base_path, "updater_gui.exe")
        else:
            root_path = os.path.join(BUNDLE_DIR, "updater_gui.exe")
            build_path = os.path.join(BUNDLE_DIR, "dist", "CodeMerger", "updater_gui.exe")

            if os.path.exists(root_path):
                updater_exe_path = root_path
            elif os.path.exists(build_path):
                updater_exe_path = build_path
            else:
                updater_exe_path = root_path

        if not os.path.exists(updater_exe_path):
            log.critical(f"Updater executable 'updater_gui.exe' not found at expected path: {updater_exe_path}")
            dialog_root = self._get_dialog_parent()
            messagebox.showerror("Update Error", f"The updater application is missing and could not be found.\n\nChecked path: {updater_exe_path}\n\nPlease reinstall CodeMerger.", parent=dialog_root)
            return

        try:
            pid = os.getpid()
            log.info(f"Starting update process. Current PID: {pid}. Updater: {updater_exe_path}. URL: {download_url}")

            subprocess.Popen(
                [updater_exe_path, str(pid), download_url],
                creationflags=subprocess.DETACHED_PROCESS,
                close_fds=True
            )

            log.info("Updater launched. Force-terminating main application for update cycle.")

            # Bypasses COM teardown hangs that often block the external updater from accessing the PID
            os._exit(0)

        except Exception as e:
            log.exception("Failed to launch the updater process.")
            dialog_root = self._get_dialog_parent()
            messagebox.showerror("Update Error", f"Failed to launch the updater process: {e}", parent=dialog_root)