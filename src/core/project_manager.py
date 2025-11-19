import os
from .project_config import ProjectConfig
from .utils import parse_gitignore, get_file_hash, get_token_count_for_text, load_config
from .file_scanner import get_all_matching_files

class ProjectManager:
    """Handles loading, initializing, and managing the active project's configuration."""
    def __init__(self, get_active_file_extensions_func):
        self.project_config = None
        self.get_active_file_extensions = get_active_file_extensions_func

    def _populate_new_project_files(self, project_config):
        """
        Helper method to scan for files and populate the ProjectConfig for a new project.
        """
        all_project_files = get_all_matching_files(
            base_dir=project_config.base_dir,
            file_extensions=self.get_active_file_extensions(),
            gitignore_patterns=parse_gitignore(project_config.base_dir)
        )
        project_config.known_files = all_project_files

        # Auto-add files to selection for new projects
        selection = []
        total_tokens = 0
        app_config = load_config()
        token_count_enabled = app_config.get('token_count_enabled', True)

        for rel_path in all_project_files:
            full_path = os.path.join(project_config.base_dir, rel_path)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                mtime = os.path.getmtime(full_path)
                file_hash = get_file_hash(full_path)

                if token_count_enabled:
                    tokens = get_token_count_for_text(content)
                    lines = content.count('\n') + 1
                else:
                    tokens, lines = 0, 0

                if file_hash is not None:
                    selection.append({
                        'path': rel_path,
                        'mtime': mtime,
                        'hash': file_hash,
                        'tokens': tokens,
                        'lines': lines
                    })
                    total_tokens += tokens
            except OSError:
                pass

        project_config.selected_files = selection
        project_config.total_tokens = total_tokens

    def load_project(self, path):
        """
        Loads a project from a given path. If no .allcode file exists,
        it initializes a new one.
        Returns a tuple: (ProjectConfig object or None, status message string)
        """
        if not path or not os.path.isdir(path):
            self.project_config = None
            return None, "No project selected"

        is_new_project = not os.path.isfile(os.path.join(path, '.allcode'))
        self.project_config = ProjectConfig(path)
        files_were_cleaned = self.project_config.load()
        project_display_name = self.project_config.project_name

        if is_new_project:
            # Initialize a new project by scanning for all valid files
            self._populate_new_project_files(self.project_config)
            self.project_config.save()
            status_message = f"Initialized new project: {project_display_name}."
        elif files_were_cleaned:
            status_message = f"Activated project: {project_display_name} - Cleaned missing files."
        else:
            status_message = f"Activated project: {project_display_name}."

        return self.project_config, status_message

    def create_project_with_defaults(self, path, intro_text, outro_text):
        """
        Initializes a new project configuration at the specified path with default prompts.
        This is used by the wizard to ensure files are scanned and defaults are set
        before the project is fully loaded.
        """
        if not path or not os.path.isdir(path):
            return

        config = ProjectConfig(path)
        # Populate file list using the centralized logic
        self._populate_new_project_files(config)
        # Apply custom prompts
        config.intro_text = intro_text
        config.outro_text = outro_text
        config.save()

    def get_current_project(self):
        """Returns the currently active ProjectConfig object."""
        return self.project_config