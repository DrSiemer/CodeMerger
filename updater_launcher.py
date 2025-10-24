import sys
import os
import time
import requests
import subprocess
import tempfile
import psutil

def write_log(message):
    """Appends a message to a log file in the temp directory for debugging."""
    log_path = os.path.join(tempfile.gettempdir(), "codemerger_updater_log.txt")
    with open(log_path, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def wait_for_process_to_close(pid):
    """Waits for a process with the given PID to terminate."""
    if pid is None:
        write_log("No PID provided to wait for.")
        return
    try:
        write_log(f"Waiting for main application (PID: {pid}) to close...")
        p = psutil.Process(pid)
        p.wait(timeout=10)
        write_log(f"Main application (PID: {pid}) has closed.")
    except psutil.NoSuchProcess:
        write_log(f"Main application (PID: {pid}) was already closed.")
        return
    except Exception as e:
        write_log(f"Error waiting for PID {pid} to close: {e}")

def download_file(url, dest_folder):
    """Downloads a file to a destination folder."""
    try:
        write_log(f"Starting download from: {url}")
        filename = url.split('/')[-1]
        dest_path = os.path.join(dest_folder, filename)
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        write_log(f"Download complete. Installer saved to: {dest_path}")
        return dest_path
    except Exception as e:
        write_log(f"Download failed: {e}")
        return None

def main():
    if len(sys.argv) != 3:
        write_log(f"Updater launched with incorrect arguments: {sys.argv}")
        return

    main_app_pid_str = sys.argv[1]
    download_url = sys.argv[2]

    try:
        main_app_pid = int(main_app_pid_str)
    except ValueError:
        write_log(f"Invalid PID passed to updater: {main_app_pid_str}")
        main_app_pid = None

    # Wait for the main app to fully terminate
    wait_for_process_to_close(main_app_pid)

    # Give the OS a moment to release file handles, just in case.
    time.sleep(1)

    # Proceed with download and installation
    temp_dir = tempfile.mkdtemp(prefix="codemerger-update-")
    installer_path = download_file(download_url, temp_dir)

    if installer_path and os.path.exists(installer_path):
        try:
            write_log(f"Launching installer: {installer_path}")
            # Use 'start' on Windows to launch detached.
            subprocess.Popen(f'start "" "{installer_path}" /SILENT', shell=True)
        except Exception as e:
            write_log(f"Failed to launch installer: {e}")
    else:
        write_log("Installer path not found after download attempt.")

if __name__ == "__main__":
    main()