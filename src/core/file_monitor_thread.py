import threading
import time
import logging
import os
from .utils import parse_gitignore
from .file_scanner import get_all_matching_files

log = logging.getLogger("CodeMerger")

class FileMonitorThread(threading.Thread):
    """
    A background daemon thread that periodically scans the active project for new files.
    When changes are detected, it notifies the Vue frontend via PyWebView's evaluate_js.
    """
    def __init__(self, window, app_state, project_manager):
        super().__init__()
        self.daemon = True
        self.window = window
        self.app_state = app_state
        self.project_manager = project_manager
        self._stop_event = threading.Event()
        self._last_scan_count = 0

    def stop(self):
        self._stop_event.set()

    def run(self):
        log.info("File Monitor background thread started.")
        while not self._stop_event.is_set():
            config = self.app_state.config
            if config.get('enable_new_file_check', True):
                self._perform_check()

            # Wait for the interval defined in settings (default 5s)
            interval = config.get('new_file_check_interval', 5)
            # Sleep in short bursts to remain responsive to stop event
            for _ in range(interval * 2):
                if self._stop_event.is_set():
                    break
                time.sleep(0.5)

    def _perform_check(self):
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return

        base_dir = project_config.base_dir
        if not os.path.isdir(base_dir):
            return

        try:
            # Check for external config changes
            if project_config.has_external_changes():
                log.info("External changes detected in .allcode. Triggering UI reload.")
                project_config.load()
                self.window.evaluate_js('window.dispatchEvent(new CustomEvent("cm-project-reloaded"))')

            # Scan for new files
            from .utils import load_active_file_extensions
            file_extensions = load_active_file_extensions()
            gitignore_patterns = parse_gitignore(base_dir)

            all_files = get_all_matching_files(
                base_dir=base_dir,
                file_extensions=file_extensions,
                gitignore_patterns=gitignore_patterns
            )

            # Detect new files specifically for the active profile
            known_set = set(project_config.known_files)
            current_set = set(all_files)

            brand_new = current_set - known_set

            if brand_new:
                # Update known files to prevent repeat alerts
                project_config.known_files = sorted(list(known_set | brand_new))

                # Add to profile unknowns
                p_unknown = set(project_config.unknown_files)
                p_unknown.update(brand_new)
                project_config.unknown_files = sorted(list(p_unknown))

                project_config.save()

                # Notify Vue frontend
                count = len(project_config.unknown_files)
                log.info(f"Detected {len(brand_new)} new files. Total unknown: {count}")
                self.window.evaluate_js(f'window.dispatchEvent(new CustomEvent("cm-new-files", {{ detail: {{ count: {count} }} }}))')

        except Exception as e:
            log.error(f"Error during background file scan: {e}")