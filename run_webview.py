import sys
import os
import webview
import logging
from src.api import Api
from src.core.logger import setup_logging
from src.core.paths import get_bundle_dir
from src.core.file_monitor_thread import FileMonitorThread

# Import core backend logic
from src.app_state import AppState
from src.core.project_manager import ProjectManager
from src.core.utils import load_active_file_extensions

log = logging.getLogger("CodeMerger")

def main():
    # Initialize logging
    setup_logging()

    # Initialize Core Application Logic
    app_state = AppState()
    project_manager = ProjectManager(load_active_file_extensions)

    # Initialize the Python API bridge
    api = Api(app_state, project_manager)

    # Detect if we should run in dev mode (connect to Vite local server)
    dev_mode = "--dev" in sys.argv

    if dev_mode:
        url = "http://localhost:5173"
        print("Running in DEV mode. Make sure 'npm run dev' is running in the frontend folder.")
    else:
        # In production, point to the built Vue assets
        bundle_dir = get_bundle_dir()
        url = os.path.join(bundle_dir, 'frontend', 'dist', 'index.html')

        if not os.path.exists(url):
            print(f"Error: Production build not found at {url}")
            print("Please run 'npm run build' in the frontend directory first.")
            sys.exit(1)

    # Create the main PyWebView window
    # Resized to 1200x780 to comfortably accommodate Modals and complex layouts
    window = webview.create_window(
        "CodeMerger",
        url=url,
        js_api=api,
        width=1200,
        height=780,
        min_size=(800, 600),
        background_color='#2E2E2E' # Matches DARK_BG
    )

    # Link the window reference to the API for native dialogs
    api.set_window(window)

    # Initialize background file monitor
    monitor = FileMonitorThread(window, app_state, project_manager)
    monitor.start()

    # Start the application loop. This call blocks until the window is closed.
    webview.start(debug=dev_mode)

    # After the UI loop returns, perform cleanup.
    # Note: Logic moved here from on_closed event to avoid Win32 race conditions (Error 1411).
    log.info("Window closed. Terminating application.")
    monitor.stop()

if __name__ == '__main__':
    main()