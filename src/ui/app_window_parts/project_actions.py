import os
import glob
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
        
        self._update_unreal_ui(connected=False)

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

        # Check for Unreal Project
        is_unreal_project = False
        # Safety check for app_state existence
        if hasattr(app, 'app_state') and app.app_state.unreal_integration_enabled:
            # Look for .uproject files in the root
            uproject_files = glob.glob(os.path.join(path, "*.uproject"))
            if uproject_files:
                is_unreal_project = True

        app.load_thread_result = (project_config, status_message, path, set_status, is_unreal_project)

    def _check_load_project_thread(self):
        app = self.app
        if not app.load_thread:
            return

        if app.load_thread.is_alive():
            app.after(100, self._check_load_project_thread)
        else:
            if app.load_thread_result:
                self._on_project_load_complete(*app.load_thread_result)
                app.load_thread_result = None
            app.load_thread = None

    def cancel_loading(self):
        app = self.app
        if app.load_thread and app.load_thread.is_alive():
            app.load_thread = None
            app.load_thread_result = None
            self._clear_project_ui()
            app.status_var.set("Loading cancelled")

    def _on_project_load_complete(self, project_config, status_message, path, set_status, is_unreal_project):
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

        if is_unreal_project:
            self.attempt_unreal_connection()
        else:
            if hasattr(app, 'unreal_client') and app.unreal_client:
                app.unreal_client.disconnect()
            self._update_unreal_ui(connected=False)

    def attempt_unreal_connection(self):
        app = self.app
        if not hasattr(app, 'unreal_client') or not app.unreal_client:
            return

        def connect_thread():
            success = app.unreal_client.connect(timeout=2.0)
            app.after(0, lambda: self._update_unreal_ui(success))
            
        app.status_var.set("Connecting to Unreal Engine...")
        if hasattr(app, 'unreal_status_label'):
            app.unreal_status_label.config(fg="#888800") # Yellow/Busy
            # FIX: Use grid instead of pack
            app.unreal_status_label.grid(row=0, column=1, padx=(0, 15), sticky='w')
        
        threading.Thread(target=connect_thread, daemon=True).start()

    def _update_unreal_ui(self, connected):
        app = self.app
        # Safety Check: Ensure UI elements exist
        if not hasattr(app, 'unreal_status_label') or not hasattr(app, 'unreal_toggle'):
            return

        if connected:
            app.unreal_status_label.config(fg=c.BTN_GREEN)
            app.unreal_status_tooltip.text = "Connected to Unreal Engine"
            # unreal_toggle is in the wrapper box which uses pack, so pack is correct here
            app.unreal_toggle.pack(pady=(0, 5), before=app.button_grid_frame) 
            app.status_var.set("Connected to Unreal Engine")
        else:
            app.unreal_status_label.config(fg="#555555")
            app.unreal_status_tooltip.text = "Unreal Engine Disconnected\n(Click to reconnect)"
            app.unreal_toggle.pack_forget()
            # Only clear status if it still says connecting
            if "Connecting" in app.status_var.get():
                app.status_var.set("Could not connect to Unreal Engine")