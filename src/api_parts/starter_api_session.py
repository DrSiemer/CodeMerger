import os
import json
import logging
import webview
from src.core.paths import PERSISTENT_DATA_DIR, REFERENCE_DIR

log = logging.getLogger("CodeMerger")

class StarterApiSession:
    """API methods concerning the persistence and static asset loading for Project Starter."""

    def get_starter_session(self):
        """Retrieves persistent state for the Project Starter process."""
        target = os.path.join(PERSISTENT_DATA_DIR, "project_starter_session.json")
        if not os.path.exists(target): return {}
        try:
            with open(target, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {}

    def save_starter_session(self, data):
        """Saves current Project Starter state to disk."""
        target = os.path.join(PERSISTENT_DATA_DIR, "project_starter_session.json")
        try:
            with open(target, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
            return True
        except Exception: return False

    def clear_starter_session(self):
        """Deletes the Project Starter session file."""
        target = os.path.join(PERSISTENT_DATA_DIR, "project_starter_session.json")
        if os.path.exists(target):
            try: os.remove(target)
            except OSError: pass
        return True

    def export_starter_config(self, data):
        """Opens a save file dialog and exports the config JSON."""
        if not self._window_manager or not self._window_manager.main_window:
            return False

        project_name = data.get("name", "").strip()
        initial_file = f"{project_name}.json" if project_name else "project-config.json"

        filepath = self._window_manager.main_window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=initial_file
        )

        if filepath:
            actual_path = filepath[0] if isinstance(filepath, (list, tuple)) else filepath
            if not actual_path: return False
            if not actual_path.lower().endswith('.json'):
                actual_path += '.json'

            try:
                with open(actual_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                return True
            except Exception as e:
                log.error(f"Failed to export config: {e}")
                return False
        return False

    def load_starter_config(self):
        """Opens an open file dialog and reads the config JSON."""
        if not self._window_manager or not self._window_manager.main_window:
            return None

        filepath = self._window_manager.main_window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=("JSON files (*.json)", "All files (*.*)")
        )

        if filepath:
            actual_path = filepath[0] if isinstance(filepath, (list, tuple)) else filepath
            if not actual_path: return None

            try:
                with open(actual_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Failed to load config: {e}")
                return None
        return None

    def get_concept_questions(self):
        """Loads guiding questions for the Concept step."""
        path = os.path.join(REFERENCE_DIR, "concept_questions.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_todo_questions(self):
        """Loads guiding questions for the TODO step."""
        path = os.path.join(REFERENCE_DIR, "todo_questions.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_concept_template(self):
        """Returns the raw content of the reference concept template."""
        path = os.path.join(REFERENCE_DIR, "concept.md")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def get_todo_template(self):
        """Returns the raw content of the reference TODO template."""
        path = os.path.join(REFERENCE_DIR, "todo.md")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""