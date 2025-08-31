import json
import sys
from tkinter import Tk, messagebox
from .ui.app_window import App
from .core.utils import load_active_file_extensions, load_app_version

def main():
    try:
        # Check for command-line arguments
        initial_project_path = None
        if len(sys.argv) > 1:
            # The first argument (sys.argv[1]) is the path passed from the context menu
            initial_project_path = sys.argv[1]

        # Load app version
        app_version = load_app_version()
        # Load active file extensions first
        loaded_extensions = load_active_file_extensions()
        # Create and run the main application
        app = App(
            file_extensions=loaded_extensions,
            app_version=app_version,
            initial_project_path=initial_project_path
        )
        app.mainloop()
    except Exception as e:
        # Generic error for failures during startup
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"An unexpected error occurred on startup: {e}\n\n"
            f"If the problem persists, try deleting config.json."
        )

if __name__ == '__main__':
    main()