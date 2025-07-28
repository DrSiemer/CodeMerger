import json
from tkinter import Tk, messagebox
from .app_window import App
from .utils import load_active_file_extensions, load_app_version

def main():
    try:
        # Load app version
        app_version = load_app_version()
        # Load active file extensions first
        loaded_extensions = load_active_file_extensions()
        # Create and run the main application
        app = App(file_extensions=loaded_extensions, app_version=app_version)
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