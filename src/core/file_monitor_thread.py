import threading
import time
import logging
import os
from .utils import parse_gitignore
from .file_scanner import get_all_matching_files

log = logging.getLogger("CodeMerger")

class FileMonitorThread(threading.Thread):
    """
    Background daemon thread that periodically scans the active project for new files
    Notifies the Vue frontend via PyWebView's evaluate_js when changes are found
    """
    def __init__(self, window, app_state, project_manager):
        super().__init__()
        self.daemon = True
        self.window = window
        self.app_state = app_state
        self.project_manager = project_manager
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def update_window(self, window):
        """Updates the window reference used for JS evaluation"""
        self.window = window

    def run(self):
        log.info("File Monitor background thread started.")
        while not self._stop_event.is_set():
            config = self.app_state.config
            if config.get('enable_new_file_check', True):
                self._perform_check()

            interval = config.get('new_file_check_interval', 5)

            # Sleep in short bursts to remain responsive to stop event
            for _ in range(interval * 2):
                if self._stop_event.is_set():
                    break
                time.sleep(0.5)

    def _safe_eval(self, js_code):
        """
        Executes JavaScript in the current window context
        Prevents crashes when a window is closed while a scan finishes
        """
        if not self.window:
            return

        try:
            self.window.evaluate_js(js_code)
        except Exception:
            # Silently ignore errors caused by calling evaluate_js on a disposed/closed window
            pass

    def _perform_check(self):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return

        base_dir = project_config.base_dir
        if not os.path.isdir(base_dir):
            return

        try:
            if project_config.has_external_changes():
                log.info("Modified .allcode detected. Synchronizing internal state...")
                if project_config.load():
                    log.info("Project configuration updated externally. Triggering UI refresh.")
                    self._safe_eval('window.dispatchEvent(new CustomEvent("cm-project-reloaded"))')

            from .utils import load_active_file_extensions
            file_extensions = load_active_file_extensions()
            gitignore_patterns = parse_gitignore(base_dir)

            all_files = get_all_matching_files(
                base_dir=base_dir,
                file_extensions=file_extensions,
                gitignore_patterns=gitignore_patterns
            )

            known_set = set(project_config.known_files)
            current_set = set(all_files)

            config_changed = False

            # Detect and Prune physically deleted files
            missing_from_scan = known_set - current_set
            truly_deleted = set()
            if missing_from_scan:
                for rel_path in missing_from_scan:
                    if not os.path.exists(os.path.join(base_dir, rel_path)):
                        truly_deleted.add(rel_path)

            if truly_deleted:
                log.info(f"Detected {len(truly_deleted)} physically deleted files. Pruning configuration.")
                for rel_path in sorted(list(truly_deleted)):
                    log.info(f"  [REMOVED] {rel_path}")

                project_config.known_files = sorted(list(known_set - truly_deleted))
                for p_data in project_config.profiles.values():
                    orig_len = len(p_data.get('selected_files', []))
                    p_data['selected_files'] = [f for f in p_data.get('selected_files', []) if f['path'] not in truly_deleted]
                    p_data['unknown_files'] = [f for f in p_data.get('unknown_files', []) if f not in truly_deleted]
                    if len(p_data['selected_files']) != orig_len:
                        p_data['total_tokens'] = sum(f.get('tokens', 0) for f in p_data['selected_files'])
                config_changed = True

                self._safe_eval('window.dispatchEvent(new CustomEvent("cm-project-reloaded"))')

            brand_new = current_set - set(project_config.known_files)
            if brand_new:
                log.info(f"Detected {len(brand_new)} brand new files.")
                for rel_path in sorted(list(brand_new)):
                    log.info(f"  [NEW]     {rel_path}")

                project_config.update_known_files(brand_new)
                config_changed = True

                count = len(project_config.unknown_files)
                self._safe_eval(f'window.dispatchEvent(new CustomEvent("cm-new-files", {{ detail: {{ count: {count} }} }}))')

            if config_changed:
                project_config.save()

        except Exception as e:
            log.error(f"Error during background file scan: {e}")