import os
import threading
import logging

from ... import constants as c

log = logging.getLogger("CodeMerger")

class ProjectActions:
    def __init__(self, app):
        self.app = app

    def _start_loading_animation(self):
        app = self.app
        app.helpers.stop_loading_animation()
        app.title_label.config(font=c.FONT_LOADING_TITLE, fg=c.TEXT_SUBTLE_COLOR)
        app.helpers.animate_loading(0)

    def _clear_project_ui(self):
        app = self.app
        app.helpers.stop_loading_animation()
        project_config, status_message = app.project_manager.load_project(None)
        app.status_var.set(status_message)

        app.active_dir.set("No project selected")
        app.project_title_var.set("(no active project)")
        app.project_color = c.COMPACT_MODE_BG_COLOR
        app.project_font_color = 'light'
        app.title_label.config(font=c.FONT_LARGE_BOLD, fg=c.TEXT_SUBTLE_COLOR)

        app.profile_actions.update_profile_selector_ui()
        app.file_monitor.start()
        app.button_manager.update_button_states()

    def set_active_dir_display(self, path, set_status=True):
        app = self.app
        if not path or not os.path.isdir(path):
            self._clear_project_ui()
            return

        app.active_dir.set("Loading...")
        self._start_loading_animation()

        app.button_manager.update_button_states()
        app.profile_actions.update_profile_selector_ui()

        self._load_project_async(path, set_status)

    def _load_project_async(self, path, set_status=True):
        app = self.app
        app.load_thread = threading.Thread(
            target=self._load_project_worker,
            args=(path, set_status),
            daemon=True
        )
        app.load_thread.start()
        app.after(100, self._check_load_project_thread)

    def _load_project_worker(self, path, set_status):
        app = self.app
        project_config, status_message = app.project_manager.load_project(path)

        if project_config:
            app.file_monitor.perform_initial_scan()

        app.load_thread_result = (project_config, status_message, path, set_status)

    def _check_load_project_thread(self):
        app = self.app
        if app.load_thread and app.load_thread.is_alive():
            app.after(100, self._check_load_project_thread)
        else:
            if app.load_thread_result:
                self._on_project_load_complete(*app.load_thread_result)
                app.load_thread_result = None
            app.load_thread = None

    def _on_project_load_complete(self, project_config, status_message, path, set_status):
        app = self.app
        app.helpers.stop_loading_animation()
        if set_status:
            app.status_var.set(status_message)

        if project_config:
            app.active_dir.set(path)
            app.project_title_var.set(project_config.project_name)
            app.project_color = project_config.project_color
            app.project_font_color = project_config.project_font_color
            app.title_label.config(font=c.FONT_LARGE_BOLD, fg=c.TEXT_COLOR)
        else:
            app.active_dir.set("No project selected")
            app.project_title_var.set("(no active project)")
            app.project_color = c.COMPACT_MODE_BG_COLOR
            app.project_font_color = 'light'
            app.title_label.config(font=c.FONT_LARGE_BOLD, fg=c.TEXT_SUBTLE_COLOR)

        app.profile_actions.update_profile_selector_ui()
        app.file_monitor.start()
        app.button_manager.update_button_states()