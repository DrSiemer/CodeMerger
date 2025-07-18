import json
from tkinter import Tk, messagebox

from .app_window import App
from .utils import load_file_extensions
from .constants import FILETYPES_CONFIG

def main():
    try:
        # Load file extensions first, as they are required by the app
        loaded_extensions = load_file_extensions()

        # Create and run the main application
        app = App(file_extensions=loaded_extensions)
        app.mainloop()

    except FileNotFoundError:
        # Create a dummy root to show the error message if the main window can't be created
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            "Configuration Error",
            f"The required configuration file '{FILETYPES_CONFIG}' was not found."
        )
    except json.JSONDecodeError:
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            "Configuration Error",
            f"The file '{FILETYPES_CONFIG}' is not a valid JSON file."
        )

if __name__ == '__main__':
    main()