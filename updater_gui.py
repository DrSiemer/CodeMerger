# updater_gui.py
import sys
import os
import time
import requests
import subprocess
import tempfile
import psutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import shutil

# --- Self-Contained Constants ---
DARK_BG = '#2E2E2E'
TEXT_COLOR = '#FFFFFF'
TEXT_INPUT_BG = '#3C3C3C'
TEXT_SUBTLE_COLOR = '#A0A0A0'
BTN_BLUE = '#0078D4'
FONT_NORMAL = ("Segoe UI", 11)
FONT_STATUS_BAR = ("Segoe UI", 9)
FONT_BUTTON = ("Segoe UI", 12)

class UpdateGUI(tk.Tk):
    def __init__(self, pid_to_wait_for, download_url):
        super().__init__()
        self.withdraw()  # Start hidden

        self.pid_to_wait_for = pid_to_wait_for
        self.download_url = download_url
        self.installer_path = None
        self.temp_dir = None
        self.cancelled = False

        self._setup_window()

        self.update_thread = threading.Thread(target=self._update_worker)
        self.update_thread.daemon = True
        self.update_thread.start()

    def _setup_window(self):
        self.title("Updating CodeMerger")
        self.resizable(False, False)
        self.configure(bg=DARK_BG, padx=20, pady=20)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.status_label = tk.Label(self, text="Waiting for CodeMerger to close...", bg=DARK_BG, fg=TEXT_COLOR, font=FONT_NORMAL)
        self.status_label.pack(pady=(0, 10), anchor='w')

        s = ttk.Style(self)
        s.theme_use('default')
        s.configure('Update.Horizontal.TProgressbar', background=BTN_BLUE, troughcolor=TEXT_INPUT_BG, bordercolor=TEXT_INPUT_BG, lightcolor=BTN_BLUE, darkcolor=BTN_BLUE)

        self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=400, mode='determinate', style='Update.Horizontal.TProgressbar')
        self.progress_bar.pack(pady=5, fill='x', expand=True)

        self.details_label = tk.Label(self, text="", bg=DARK_BG, fg=TEXT_SUBTLE_COLOR, font=FONT_STATUS_BAR)
        self.details_label.pack(pady=(5, 15), anchor='e')

        self.cancel_button = tk.Button(self, text="Cancel", command=self._on_cancel, bg='#555', fg='white', activebackground='#666', activeforeground='white', relief='flat', padx=15, pady=5, font=FONT_BUTTON)
        self.cancel_button.pack()

        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        x = (screen_w // 2) - (win_w // 2)
        y = (screen_h // 2) - (win_h // 2)
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.lift()
        self.focus_force()

    def _update_worker(self):
        try:
            if self.pid_to_wait_for:
                p = psutil.Process(self.pid_to_wait_for)
                p.wait(timeout=10)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            pass # Process is already gone or wait timed out, proceed.
        except Exception:
            pass # Ignore other potential errors, the goal is to proceed.

        time.sleep(0.5) # Brief pause for safety

        self.after(0, lambda: self.status_label.config(text=f"Downloading update..."))
        self.temp_dir = tempfile.mkdtemp(prefix="codemerger-update-")

        try:
            filename = self.download_url.split('/')[-1]
            self.installer_path = os.path.join(self.temp_dir, filename)

            with requests.get(self.download_url, stream=True, timeout=60) as r:
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
                            self.after(0, self._on_progress, progress, downloaded_size, total_size)

            if not self.cancelled:
                self.after(0, self._on_complete)

        except Exception as e:
            self._cleanup_temp_dir()
            self.after(0, self.show_error, f"Download failed: {e}")

    def _on_progress(self, progress, downloaded, total):
        self.progress_bar['value'] = progress
        self.details_label.config(text=f"{downloaded / 1_048_576:.2f} MB / {total / 1_048_576:.2f} MB")

    def _on_complete(self):
        self.status_label.config(text="Download complete. Launching installer...")
        self.progress_bar['value'] = 100
        self.cancel_button.config(state='disabled')
        self.after(1000, self._launch_and_exit)

    def _launch_and_exit(self):
        try:
            subprocess.Popen(f'start "" "{self.installer_path}" /SILENT', shell=True)
            self._cleanup_and_destroy()
        except Exception as e:
            self.show_error(f"Failed to launch installer: {e}")

    def show_error(self, message):
        messagebox.showerror("Update Failed", message)
        self._cleanup_and_destroy()

    def _cleanup_temp_dir(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _cleanup_and_destroy(self):
        self.destroy()
        sys.exit(0)

    def _on_cancel(self):
        self.cancelled = True
        self.status_label.config(text="Cancelling...")
        # The worker thread will see the flag and clean up. We just close the window.
        self._cleanup_and_destroy()

def main():
    if len(sys.argv) != 3:
        return
    try:
        pid = int(sys.argv[1])
        url = sys.argv[2]
        app = UpdateGUI(pid, url)
        app.mainloop()
    except Exception as e:
        log_dir = tempfile.gettempdir()
        with open(os.path.join(log_dir, "updater_gui_error.log"), "a") as f:
            f.write(f"An error occurred during updater startup: {e}\n")

if __name__ == '__main__':
    main()