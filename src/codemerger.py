import json
import sys
import logging
from tkinter import Tk, messagebox
from .ui.app_window import App
from .core.utils import load_active_file_extensions, load_app_version
from .core.logger import setup_logging

def main():
    setup_logging()
    log = logging.getLogger("CodeMerger")

    try:
        # Check for command-line arguments
        initial_project_path = None
        if len(sys.argv) > 1:
            # The first argument (sys.argv[1]) is the path passed from the context menu
            initial_project_path = sys.argv[1]
            log.info(f"Received initial project path from command line: {initial_project_path}")

        # Load app version
        app_version = load_app_version()
        # Load active file extensions first
        loaded_extensions = load_active_file_extensions()
        log.info(f"CodeMerger {app_version} starting up.")
        # Create and run the main application
        app = App(
            file_extensions=loaded_extensions,
            app_version=app_version,
            initial_project_path=initial_project_path
        )
        app.mainloop()
    except Exception as e:
        log.exception("An uncaught exception occurred during application startup.")
        # Generic error for failures during startup
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"An unexpected error occurred on startup: {e}\n\n"
            f"If the problem persists, try deleting config.json.\n"
            f"A detailed log has been saved to %APPDATA%\\CodeMerger\\codemerger.log"
        )

if __name__ == '__main__':
    main()