import json
import logging

log = logging.getLogger("CodeMerger")

class WindowBroadcaster:
    """Manages the transmission of data to the Javascript API across all windows."""
    def __init__(self, manager):
        self.manager = manager

    def _dispatch_project_reload(self, win):
        """Broadcasts current project state to a window, bypassing async round-trips"""
        if not win or not self.manager.api: return
        if not self.manager._handshake_received: return
        project_config = self.manager.api.project_manager.get_current_project()
        data = self.manager.api._format_project_response(project_config, "") if project_config else None
        data_json = json.dumps(data)
        try:
            win.evaluate_js(f'window.dispatchEvent(new CustomEvent("cm-project-reloaded", {{ detail: {data_json} }}))')
        except Exception as e:
            log.debug(f"Failed to evaluate JS on window: {e}")

    def broadcast_project_reload(self):
        """Pushes current state to all windows to ensure hidden windows stay synchronized"""
        if not self.manager.api: return
        if not self.manager._handshake_received: return
        project_config = self.manager.api.project_manager.get_current_project()
        data = self.manager.api._format_project_response(project_config, "") if project_config else None
        data_json = json.dumps(data)
        js = f'window.dispatchEvent(new CustomEvent("cm-project-reloaded", {{ detail: {data_json} }}))'

        for win in [self.manager.main_window, self.manager.compact_window]:
            if win:
                try: win.evaluate_js(js)
                except Exception as e: log.debug(f"Failed to evaluate JS on window: {e}")

    def broadcast_config_update(self, config_data):
        """Pushes global config updates to all frontend contexts."""
        if not self.manager._handshake_received: return
        js = f'window.dispatchEvent(new CustomEvent("cm-config-updated", {{ detail: {json.dumps(config_data)} }}))'
        for win in [self.manager.main_window, self.manager.compact_window]:
            if win:
                try: win.evaluate_js(js)
                except Exception: pass

    def trigger_file_manager_in_main(self):
        """Forces the main window to open the File Manager."""
        if self.manager.main_window:
            log.info("WindowManager: Triggering remote openFileManager JS call.")
            try:
                self.manager.main_window.evaluate_js("if (window.openFileManager) window.openFileManager();")
            except Exception as e:
                log.debug(f"Failed to evaluate JS on main window: {e}")