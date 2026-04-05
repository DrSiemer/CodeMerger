import sys
import os
import webview
from src.api import Api
from src.core.logger import setup_logging
from src.core.paths import get_bundle_dir

def main():
    # Initialize logging
    setup_logging()

    # Initialize the Python API bridge
    api = Api()

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
    window = webview.create_window(
        "CodeMerger",
        url=url,
        js_api=api,
        width=1100,
        height=800,
        min_size=(800, 600),
        background_color='#2E2E2E' # Matches DARK_BG
    )

    # Link the window reference to the API for native dialogs
    api.set_window(window)

    # Start the application loop
    webview.start(debug=dev_mode)

if __name__ == '__main__':
    main()