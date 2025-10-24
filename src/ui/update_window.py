import tkinter as tk
from tkinter import ttk, Toplevel, Frame, Label, messagebox
import threading
import requests
import os
import subprocess
import sys
import tempfile
import json
import shutil
from ..core.paths import ICON_PATH, UPDATE_CLEANUP_FILE_PATH
from .. import constants as c
from .widgets.rounded_button import RoundedButton


class UpdateManager:
    """Handles the update download and execution logic in a separate thread."""
    def __init__(self, parent_window, download_url, on_progress, on_complete, on_error):
        self.parent = parent_window
        self.download_url = download_url
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        self.cancelled = False
        self.temp_dir = ""
        self.installer_path = ""

    def start_download(self):
        """Starts the download process in a new thread."""
        thread = threading.Thread(target=self._download_worker)
        thread.daemon = True
        thread.start()

    def cancel(self):
        """Flags the download to be cancelled."""
        self.cancelled = True

    def _cleanup_temp_dir(self):
        """Safely removes the temporary directory if it exists."""
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _download_worker(self):
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="codemerger-update-")
            filename = self.download_url.split('/')[-1]
            self.installer_path = os.path.join(self.temp_dir, filename)

            with requests.get(self.download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded_size = 0

                with open(self.installer_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if self.cancelled:
                            self._cleanup_temp_dir()
                            return

                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            self.parent.after(0, self.on_progress, progress, downloaded_size, total_size)

            if not self.cancelled:
                self.parent.after(0, self.on_complete, self.installer_path, self.temp_dir)

        except requests.RequestException as e:
            self._cleanup_temp_dir()
            self.parent.after(0, self.on_error, f"Network error: {e}")
        except Exception as e:
            self._cleanup_temp_dir()
            self.parent.after(0, self.on_error, f"An unexpected error occurred: {e}")


class UpdateWindow(Toplevel):
    def __init__(self, parent, release_data):
        super().__init__(parent)
        self.parent = parent
        self.release_data = release_data
        self.update_manager = None

        self._setup_window()
        self._find_and_start_download()

    def _setup_window(self):
        self.title("Updating CodeMerger")
        self.iconbitmap(ICON_PATH)
        self.transient(self.parent)
        self.grab_set()
        self.focus_force()
        self.resizable(False, False)
        self.configure(bg=c.DARK_BG, padx=20, pady=20)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.status_label = Label(self, text="Preparing to download...", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.status_label.pack(pady=(0, 10), anchor='w')

        s = ttk.Style(self)
        s.theme_use('default')
        s.configure('Update.Horizontal.TProgressbar', background=c.BTN_BLUE, troughcolor=c.TEXT_INPUT_BG, bordercolor=c.TEXT_INPUT_BG, lightcolor=c.BTN_BLUE, darkcolor=c.BTN_BLUE)
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=400, mode='determinate', style='Update.Horizontal.TProgressbar')
        self.progress_bar.pack(pady=5, fill='x', expand=True)

        self.details_label = Label(self, text="", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_STATUS_BAR)
        self.details_label.pack(pady=(5, 15), anchor='e')

        self.cancel_button = RoundedButton(self, text="Cancel", command=self._on_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        self.cancel_button.pack()

        self.update_idletasks()
        parent_x, parent_y = self.parent.winfo_rootx(), self.parent.winfo_rooty()
        parent_w, parent_h = self.parent.winfo_width(), self.parent.winfo_height()
        win_w, win_h = self.winfo_width(), self.winfo_height()
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2
        self.geometry(f"+{x}+{y}")

    def _find_and_start_download(self):
        assets = self.release_data.get('assets', [])
        download_url = next((asset.get('browser_download_url') for asset in assets if asset.get('name', '').endswith('_Setup.exe')), None)

        if download_url:
            self.status_label.config(text=f"Downloading {self.release_data.get('tag_name', 'new version')}...")
            self.update_manager = UpdateManager(self, download_url, self.on_progress, self.on_complete, self.on_error)
            self.update_manager.start_download()
        else:
            self.on_error("Could not find the installer file in the latest release.")

    def on_progress(self, progress, downloaded_bytes, total_bytes):
        self.progress_bar['value'] = progress
        self.details_label.config(text=f"{downloaded_bytes/1024/1024:.2f} MB / {total_bytes/1024/1024:.2f} MB")

    def on_complete(self, installer_path, temp_dir_path):
        self.status_label.config(text="Download complete. Preparing to launch installer...")
        self.progress_bar['value'] = 100
        self.cancel_button.set_state('disabled')

        try:
            with open(UPDATE_CLEANUP_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump({'temp_dir_to_delete': temp_dir_path}, f)

            launcher_path = os.path.join(temp_dir_path, 'run_update.bat')
            installer_filename = os.path.basename(installer_path)

            script_content = f"""
@echo off
timeout /t 2 /nobreak > NUL
start "" "{installer_filename}" /SILENT
(goto) 2>nul & del "%~f0"
"""
            with open(launcher_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

        except IOError as e:
            self.on_error(f"Failed to create update script: {e}")
            return

        self.after(500, lambda: self._launch_and_exit(launcher_path, temp_dir_path))

    def _launch_and_exit(self, launcher_path, working_dir):
        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW

            subprocess.Popen([launcher_path], creationflags=creationflags, cwd=working_dir)

            self.parent.destroy()
            sys.exit(0)
        except Exception as e:
            self.on_error(f"Failed to launch update script: {e}")

    def on_error(self, message):
        self.grab_release()
        messagebox.showerror("Update Failed", message, parent=self.parent)
        self.destroy()

    def _on_cancel(self):
        if self.update_manager:
            self.update_manager.cancel()
        self.destroy()