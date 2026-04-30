import threading
import time
import logging
import os
import sys
from .utils import parse_gitignore
from .file_scanner import get_project_inventory, enrich_inventory
from .. import constants as c

log = logging.getLogger("CodeMerger")

class FileMonitorThread(threading.Thread):
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
        self.window = window

    def force_check(self):
        self._force_check_event.set()

    def _set_low_priority(self):
        if sys.platform == "win32":
            try:
                import ctypes
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
            # Scans faster than FAST_SCAN_THRESHOLD_SECONDS ignore adaptive multipliers
            adaptive_interval = max(user_interval, int(duration * 4)) if duration > c.FAST_SCAN_THRESHOLD_SECONDS else user_interval

            self._force_check_event.clear()
            for _ in range(int(adaptive_interval * 2)):
                if self._stop_event.is_set() or self._force_check_event.is_set():
                    break
                time.sleep(0.5)

    def _safe_eval(self, js_code):
        if not self.window: return
        try:
            self.window.evaluate_js(js_code)
        except Exception as e:
            log.error(f"JS Eval Error: {e}")

    def _perform_check(self):
        project_config = self.project_manager.get_current_project()
        if not project_config: return

        base_dir = project_config.base_dir
        if not os.path.isdir(base_dir): return

        try:
            if project_config.has_external_changes():
                log.info("External change detected in project configuration. Reloading.")
                if project_config.load():
                    self._safe_eval('window.dispatchEvent(new CustomEvent("cm-project-reloaded"))')

            with self.project_manager._scan_lock:
                raw_inventory = get_project_inventory(base_dir, cancel_event=self._stop_event)
                if self._stop_event.is_set(): return
                inventory = enrich_inventory(base_dir, raw_inventory)
                self.project_manager.set_inventory(inventory)

            from .utils import load_active_file_extensions
            file_extensions = load_active_file_extensions()
            extensions = {ext for ext in file_extensions if ext.startswith('.')}
            exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}

            all_files = inventory['files']
            profile_all_files = []
            for item in all_files:
                if item['i']: continue
                if item['e'] in extensions or item['n'] in exact_filenames:
                    profile_all_files.append(item['p'])

            known_set = set(project_config.known_files)
            current_set = set(profile_all_files)
            config_changed = False

            missing = known_set - current_set
            truly_deleted = {p for p in missing if not os.path.exists(os.path.join(base_dir, p))}
            if truly_deleted:
                log.info(f"Monitor: Truly deleted {len(truly_deleted)} files.")
                project_config.known_files = sorted(list(known_set - truly_deleted))
                for p_data in project_config.profiles.values():
                    p_data['selected_files'] = [f for f in p_data.get('selected_files', []) if f['path'] not in truly_deleted]
                    p_data['unknown_files'] = [f for f in p_data.get('unknown_files', []) if f not in truly_deleted]
                config_changed = True

            brand_new = current_set - set(project_config.known_files)
            if brand_new:
                log.info(f"Monitor: NEW files detected: {list(brand_new)}")
                project_config.update_known_files(brand_new)
                config_changed = True

            if config_changed:
                log.info("Monitor: Saving changes to config...")
                project_config.save()
                log.info("Monitor: Save complete. Notifying frontend.")

                count = len(project_config.unknown_files)
                self._safe_eval(f'window.dispatchEvent(new CustomEvent("cm-new-files", {{ detail: {{ count: {count} }} }}))')
                if truly_deleted:
                    self._safe_eval('window.dispatchEvent(new CustomEvent("cm-project-reloaded"))')

        except Exception as e:
            log.error(f"Error in FileMonitorThread: {e}")