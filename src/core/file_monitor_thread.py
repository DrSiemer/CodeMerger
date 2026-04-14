import threading
import time
import logging
import os
import sys
from .utils import parse_gitignore
from .file_scanner import get_project_inventory

log = logging.getLogger("CodeMerger")

class FileMonitorThread(threading.Thread):
    """
    Background daemon thread that periodically scans the active project for new files.
    Features:
    - Adaptive Throttling: Automatically scales wait time to ensure scan work < 25% duty cycle.
    - Result Caching: Maintains a raw inventory of file paths and gitignore patterns.
    - Forced Interrupt: Can be triggered manually by the API to refresh cache.
    """
    def __init__(self, window, app_state, project_manager):
        super().__init__()
        self.name = "FileMonitor"
        self.daemon = True
        self.window = window
        self.app_state = app_state
        self.project_manager = project_manager
        self._stop_event = threading.Event()
        self._force_check_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        self._force_check_event.set()

    def update_window(self, window):
        """Updates the window reference used for JS evaluation"""
        self.window = window

    def force_check(self):
        """Interrupts the current sleep to perform an immediate background scan."""
        self._force_check_event.set()

    def _set_low_priority(self):
        """Sets the current thread to background processing mode on Windows."""
        if sys.platform == "win32":
            try:
                import ctypes
                # THREAD_MODE_BACKGROUND_BEGIN = 0x00010000
                ctypes.windll.kernel32.SetThreadPriority(ctypes.windll.kernel32.GetCurrentThread(), 0x00010000)
            except Exception:
                pass

    def run(self):
        log.info("File Monitor background thread started.")
        self._set_low_priority()

        while not self._stop_event.is_set():
            config = self.app_state.config

            start_time = time.perf_counter()

            if config.get('enable_new_file_check', True):
                self._perform_check()

            end_time = time.perf_counter()
            duration = end_time - start_time

            user_interval = config.get('new_file_check_interval', 5)
            adaptive_interval = max(user_interval, int(duration * 4))

            if duration > 1.0:
                log.debug(f"Large scan detected ({duration:.2f}s). Throttling next background check to {adaptive_interval}s.")

            self._force_check_event.clear()
            for _ in range(adaptive_interval * 2):
                if self._stop_event.is_set() or self._force_check_event.is_set():
                    break
                time.sleep(0.5)

    def _safe_eval(self, js_code):
        """Executes JavaScript in the current window context."""
        if not self.window:
            return
        try:
            self.window.evaluate_js(js_code)
        except Exception:
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

            # Update Project Inventory Cache (Discover ALL files and gitignores)
            with self.project_manager._scan_lock:
                inventory = get_project_inventory(base_dir, cancel_event=self._stop_event)
                if self._stop_event.is_set(): return
                inventory['files'].sort(key=str.lower)
                self.project_manager.set_inventory(inventory)

            # Match inventory against project profile requirements for "New File" alerts
            from .utils import load_active_file_extensions, is_ignored
            file_extensions = load_active_file_extensions()
            extensions = {ext for ext in file_extensions if ext.startswith('.')}
            exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}

            base_dir_norm = os.path.abspath(base_dir).replace('\\', '/')
            all_files = inventory['files']
            gitignores = inventory['gitignores']

            # Filter inventory down to what is allowed by active settings to identify "true" new files
            profile_all_files = []
            for rel_path in all_files:
                abs_path = os.path.join(base_dir, rel_path)
                # Note: For background alerts, we DO respect gitignore rules
                if is_ignored(abs_path, base_dir_norm, gitignores):
                    continue

                name_low = os.path.basename(rel_path).lower()
                ext = os.path.splitext(name_low)[1]
                if ext in extensions or name_low in exact_filenames:
                    profile_all_files.append(rel_path)

            known_set = set(project_config.known_files)
            current_set = set(profile_all_files)

            config_changed = False

            # Detect and prune physically deleted files
            missing_from_scan = known_set - current_set
            truly_deleted = set()
            if missing_from_scan:
                for rel_path in missing_from_scan:
                    if not os.path.exists(os.path.join(base_dir, rel_path)):
                        truly_deleted.add(rel_path)

            if truly_deleted:
                log.info(f"Detected {len(truly_deleted)} physically deleted files.")
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
                project_config.update_known_files(brand_new)
                config_changed = True
                count = len(project_config.unknown_files)
                self._safe_eval(f'window.dispatchEvent(new CustomEvent("cm-new-files", {{ detail: {{ count: {count} }} }}))')

            if config_changed:
                project_config.save()

        except Exception as e:
            log.error(f"Error during background file scan: {e}")