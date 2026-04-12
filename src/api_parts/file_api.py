import os
import json
import pyperclip
import logging
import subprocess
import sys
from src.core.utils import parse_gitignore, get_token_count_for_text, is_ignored, get_file_hash
from src.core.file_tree_builder import build_file_tree_data
from src.core.merger import generate_output_string

log = logging.getLogger("CodeMerger")

class FileApi:
    """API methods concerning the file tree, file parsing, and the merge list."""

    def get_file_tree(self, filter_text="", is_ext_filter=True, is_git_filter=True):
        """Returns the project file tree data structure, enhanced with metadata."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return []

        base_dir = project_config.base_dir
        from src.core.utils import load_active_file_extensions
        file_extensions = load_active_file_extensions()
        gitignore_patterns = parse_gitignore(base_dir)
        selected_paths = {f['path'] for f in project_config.selected_files}
        unknown_files = set(project_config.unknown_files)

        raw_tree = build_file_tree_data(
            base_dir=base_dir,
            file_extensions=file_extensions,
            gitignore_patterns=gitignore_patterns,
            filter_text=filter_text,
            is_extension_filter_active=is_ext_filter,
            selected_file_paths=selected_paths,
            is_gitignore_filter_active=is_git_filter
        )

        # Inject is_new and is_filtered flags recursively
        def inject_metadata(nodes):
            for node in nodes:
                rel_path = node['path']
                node['is_new'] = rel_path in unknown_files

                # Check if file is in selection but normally filtered
                if rel_path in selected_paths:
                    is_git_ignored = is_ignored(os.path.join(base_dir, rel_path), base_dir, gitignore_patterns)

                    file_name_lower = node['name'].lower()
                    file_ext = os.path.splitext(file_name_lower)[1]
                    extensions_set = {ext for ext in file_extensions if ext.startswith('.')}
                    exact_filenames_set = {ext for ext in file_extensions if not ext.startswith('.')}
                    is_valid_ext = file_ext in extensions_set or file_name_lower in exact_filenames_set

                    node['is_filtered'] = is_git_ignored or (not is_valid_ext)
                else:
                    node['is_filtered'] = False

                if 'children' in node:
                    inject_metadata(node['children'])

        inject_metadata(raw_tree)
        return raw_tree

    def get_token_count(self, file_path):
        """Calculates token count for a specific file relative to project root."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return 0

        full_path = os.path.join(project_config.base_dir, file_path)
        if not os.path.isfile(full_path):
            return 0

        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return get_token_count_for_text(content)
        except Exception:
            return 0

    def get_token_count_for_path(self, base_dir, rel_path):
        """Used by Step 2 File Manager to calculate tokens for base project files."""
        full_path = os.path.join(base_dir, rel_path)
        if not os.path.isfile(full_path):
            return 0
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return get_token_count_for_text(content)
        except Exception:
            return 0

    def clear_unknown_files(self):
        """
        Resets the unknown files list for the current project profile.
        Used to dismiss alert icons when the user opens the file manager.
        """
        project_config = self.project_manager.get_current_project()
        if project_config:
            project_config.unknown_files = []
            project_config.save()
            # Notify UI
            if self._window_manager and self._window_manager.main_window:
                self._window_manager.main_window.evaluate_js('window.dispatchEvent(new CustomEvent("cm-new-files", { detail: { count: 0 } }))')
            return True
        return False

    def add_all_new_files(self):
        """
        Instantly adds all currently detected unknown files to the merge list.
        Clears the unknown files tracker upon completion.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return None

        new_files = list(project_config.unknown_files)
        if not new_files:
            return self._format_project_response(project_config, "No new files to add.")

        base_dir = project_config.base_dir
        current_selection_paths = {f['path'] for f in project_config.selected_files}
        files_to_add = [path for path in new_files if path not in current_selection_paths]

        added_count = 0
        for path in files_to_add:
            full_path = os.path.join(base_dir, path)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                mtime = os.path.getmtime(full_path)
                file_hash = get_file_hash(full_path)
                tokens = get_token_count_for_text(content)
                lines = content.count('\n') + 1

                project_config.selected_files.append({
                    'path': path, 'mtime': mtime, 'hash': file_hash,
                    'tokens': tokens, 'lines': lines
                })
                added_count += 1
            except Exception as e:
                log.error(f"Failed to process new file {path}: {e}")

        # Recalculate total tokens
        project_config.total_tokens = sum(f.get('tokens', 0) for f in project_config.selected_files)

        # Clear unknown files for the active profile
        project_config.unknown_files = []

        # Ensure these files are marked as known globally
        current_paths = {f['path'] for f in project_config.selected_files}
        project_config.known_files = sorted(list(set(project_config.known_files) | current_paths))

        project_config.save()

        # Manually trigger the event to clear the counter in UI immediately
        if self._window_manager and self._window_manager.main_window:
            self._window_manager.main_window.evaluate_js('window.dispatchEvent(new CustomEvent("cm-new-files", { detail: { count: 0 } }))')

        return self._format_project_response(project_config, f"Added {added_count} new file(s) to merge list.")

    def update_project_files(self, selected_files, total_tokens, expanded_dirs=None):
        """Updates the project configuration with a new selection, order, and expansion state."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return False

        project_config.selected_files = selected_files
        project_config.total_tokens = total_tokens

        if expanded_dirs is not None:
            project_config.expanded_dirs = set(expanded_dirs)

        # Clear unknown files for the active profile once user has interacted with the manager
        project_config.unknown_files = []

        current_paths = {f['path'] for f in selected_files}
        project_config.known_files = sorted(list(set(project_config.known_files) | current_paths))

        project_config.save()
        return True

    def generate_order_request(self, selected_files):
        """Generates a prompt asking for the optimal file order and copies it to clipboard."""
        project_config = self.project_manager.get_current_project()
        if not project_config or not selected_files:
            return "Failed to generate request: No files selected."

        # Temporarily apply provided selection to logic
        orig_selection = project_config.selected_files
        project_config.selected_files = selected_files

        try:
            merged_code, _ = generate_output_string(
                base_dir=project_config.base_dir,
                project_config=project_config,
                use_wrapper=False,
                copy_merged_prompt=""
            )

            if not merged_code:
                return "Failed to generate request: Could not merge file content."

            paths = [f['path'] for f in selected_files]
            prepend_text = "Please provide me with the optimal order in which to present these files to a language model. Only return the file list in the exact same format I will use here:\n\n"
            json_payload = json.dumps(paths, indent=2)
            content_intro = "Here's the content of the files, to help you determine the best order:"

            final_string = f"{prepend_text}{json_payload}\n\n{content_intro}\n\n{merged_code}"

            pyperclip.copy(final_string)
            return "Order request with file content copied to clipboard."
        except Exception as e:
            log.error(f"Error generating order request: {e}")
            return f"Error: {str(e)}"
        finally:
            # Restore original selection
            project_config.selected_files = orig_selection

    def open_file(self, rel_path):
        """Opens a specific project file in the OS default or configured editor."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return False

        full_path = os.path.join(project_config.base_dir, rel_path)
        if not os.path.isfile(full_path):
            return False

        # Check for configured editor
        app_config = self.app_state.config
        editor = app_config.get('default_editor', '')

        try:
            if editor and os.path.isfile(editor):
                subprocess.Popen([editor, full_path])
            else:
                if sys.platform == "win32":
                    os.startfile(full_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", full_path])
                else:
                    subprocess.Popen(["xdg-open", full_path])
            return True
        except Exception as e:
            log.error(f"Failed to open file {rel_path}: {e}")
            return False