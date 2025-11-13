import os
from ...core.utils import load_active_file_extensions

class UICallbacks:
    def __init__(self, app):
        self.app = app

    def on_settings_closed(self):
        app = self.app
        app.app_state.reload()
        app.file_monitor.start()
        app.status_var.set("Settings updated")

    def on_directory_selected(self, new_dir):
        app = self.app
        if app.app_state.update_active_dir(new_dir):
            app.project_actions.set_active_dir_display(new_dir)

    def on_recent_removed(self, path_to_remove):
        app = self.app
        cleared_active = app.app_state.remove_recent_project(path_to_remove)
        app.status_var.set(f"Removed '{os.path.basename(path_to_remove)}' from recent projects")
        if cleared_active:
            app.project_actions.set_active_dir_display(None)

    def reload_active_extensions(self):
        app = self.app
        app.file_extensions = load_active_file_extensions()
        app.status_var.set("Filetype configuration updated")
        app.file_monitor.start()