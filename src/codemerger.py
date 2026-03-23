import json
import sys
import logging
from tkinter import Tk, messagebox
from .ui.app_window import App
from .core.utils import (
    load_active_file_extensions,
    load_app_version,
    update_and_get_new_filetypes,
    is_another_instance_running
)
from .core.logger import setup_logging
from .ui.new_filetypes_dialog import NewFiletypesDialog

def main():
    setup_logging()
    log = logging.getLogger("CodeMerger")

    try:
        newly_added_filetypes = update_and_get_new_filetypes()

        # Check for active instances to prevent configuration write collisions
        another_instance_active = is_another_instance_running()

        # Command-line Argument Parsing
        initial_project_path = None

        cmd_args = sys.argv[1:]

        if cmd_args:
            initial_project_path = cmd_args[0]
            log.info(f"Received initial project path from command line: {initial_project_path}")

        app_version = load_app_version()
        loaded_extensions = load_active_file_extensions()
        log.info(f"CodeMerger {app_version} starting up.")
        app = App(
            file_extensions=loaded_extensions,
            app_version=app_version,
            initial_project_path=initial_project_path,
            newly_added_filetypes=newly_added_filetypes,
            is_second_instance=another_instance_active
        )
        app.mainloop()
    except Exception as e:
        log.exception("An uncaught exception occurred during application startup.")
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