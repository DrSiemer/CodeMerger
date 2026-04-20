import os
import threading
import logging
import time
from .project_config import ProjectConfig
from .utils import parse_gitignore, calculate_font_color
from .file_scanner import get_all_matching_files

log = logging.getLogger("CodeMerger")

class ProjectManager:
    """Handles loading, initializing, and managing the active project's configuration."""
    def __init__(self, get_active_file_extensions_func):
        self.project_config = None
        self.get_active_file_extensions = get_active_file_extensions_func
        # Lock to ensure thread-safe access to the project_config reference and management ops
        self._lock = threading.Lock()

        # Memory Cache: Stores a snapshot of the disk (file list + gitignores)
        self._disk_inventory = None
        self._inventory_timestamp = 0
        self._inventory_lock = threading.Lock()

        # Concurrency Lock: Prevents multiple threads from performing a disk walk at the same time
        self._scan_lock = threading.Lock()

    def get_inventory(self):
        """Returns the cached disk inventory and its age."""
        with self._inventory_lock:
            return self._disk_inventory, self._inventory_timestamp

    def set_inventory(self, inventory):
        """Updates the cached disk inventory and refreshes the age."""
        with self._inventory_lock:
            self._disk_inventory = inventory
            self._inventory_timestamp = time.time()

    def _populate_new_project_files(self, project_config, cancel_event=None):
        """
        Helper method to scan for files and populate the ProjectConfig for a new project.
        """
        all_project_files = get_all_matching_files(
            base_dir=project_config.base_dir,
            file_extensions=self.get_active_file_extensions(),
            gitignore_patterns=None,
            cancel_event=cancel_event
        )

        if cancel_event and cancel_event.is_set():
            return False

        project_config.known_files = all_project_files
        project_config.selected_files = []
        project_config.total_tokens = 0
        return True

    def load_project(self, path, cancel_event=None):
        """
        Loads a project from a given path. If no .allcode file exists,
        it initializes a new one. Passing None unloads the current project.
        Returns a tuple: (ProjectConfig object or None, status message string)
        """
        with self._lock:
            # Invalidate cache on project change
            self.set_inventory(None)
            self._inventory_timestamp = 0

            if path is None:
                self.project_config = None
                return None, "No project active."

            if not isinstance(path, str):
                log.error(f"ProjectManager received non-string path: {type(path)}")
                self.project_config = None
                return None, "Error: Invalid project path."

            if not os.path.isdir(path):
                self.project_config = None
                return None, f"Path is not a directory: {path}"

            codemerger_dir = os.path.join(path, '.codemerger')
            allcode_file = os.path.join(path, '.allcode')
            is_new_project = not os.path.isdir(codemerger_dir) and not os.path.isfile(allcode_file)

            self.project_config = ProjectConfig(path)

            try:
                files_were_cleaned = self.project_config.load()
            except RuntimeError as e:
                self.project_config = None
                return None, str(e)

            project_display_name = self.project_config.project_name

            if is_new_project:
                success = self._populate_new_project_files(self.project_config, cancel_event=cancel_event)

                if cancel_event and cancel_event.is_set():
                    self.project_config = None
                    return None, "Load cancelled."

                self.project_config.save()
                status_message = f"Initialized new project: {project_display_name}."
            elif files_were_cleaned:
                status_message = f"Activated project: {project_display_name} - Cleaned missing files."
            else:
                status_message = f"Activated project: {project_display_name}."

            return self.project_config, status_message

    def create_project_with_defaults(self, path, project_name, intro_text, outro_text, initial_selected_files=None, project_color=None):
        """
        Initializes a new project configuration at the specified path with default prompts.
        Optionally sets the initial selected files (merge list).
        """
        with self._lock:
            if not path or not os.path.isdir(path):
                return

            config = ProjectConfig(path)
            config.project_name = project_name

            if project_color:
                config.project_color = project_color
                config.project_font_color = calculate_font_color(project_color)

            self._populate_new_project_files(config)

            if initial_selected_files:
                processed_selection = []
                new_paths = set()

                for item in initial_selected_files:
                    if isinstance(item, str):
                        path_str = item
                        processed_selection.append({'path': path_str})
                        new_paths.add(path_str)
                    elif isinstance(item, dict) and 'path' in item:
                        processed_selection.append(item)
                        new_paths.add(item['path'])

                config.selected_files = processed_selection
                config.known_files = sorted(list(set(config.known_files) | new_paths))

            config.intro_text = intro_text
            config.outro_text = outro_text
            config.save()

    def get_current_project(self):
        """Returns the currently active ProjectConfig object."""
        with self._lock:
            return self.project_config