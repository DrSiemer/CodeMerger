import webview
import os
import logging
import pyperclip
import base64
import json
from src.core.secret_scanner import scan_for_secrets
from src.core.merger import generate_output_string
from src.core.project_config import ProjectConfig
from src.core.utils import save_config, load_all_filetypes, save_filetypes, parse_gitignore, get_token_count_for_text, is_ignored
from src.core.registry import save_setting
from src.core.paths import BUNDLE_DIR
from src.ui.file_manager.file_tree_builder import build_file_tree_data

log = logging.getLogger("CodeMerger")

class Api:
    """
    The Python API bridge exposed to the Vue 3 frontend via PyWebView.
    Methods defined here can be called directly from JavaScript using `window.pywebview.api.method_name()`.
    """
    def __init__(self, app_state, project_manager):
        # Prefixing with an underscore prevents PyWebView from inspecting this attribute
        # during JS API generation, which avoids a premature DOM evaluation crash.
        self._window = None
        self.app_state = app_state
        self.project_manager = project_manager

    def set_window(self, window):
        """Sets the active PyWebView window reference."""
        self._window = window

    def ensure_window_size(self, width, height):
        """
        Requests the main window to expand to the specified dimensions if it is
        currently smaller. This prevents large modals from being clipped.
        """
        if not self._window:
            return

        current_w = self._window.width
        current_h = self._window.height

        target_w = max(current_w, width)
        target_h = max(current_h, height)

        if target_w != current_w or target_h != current_h:
            log.info(f"Expanding window to {target_w}x{target_h} to accommodate content.")
            self._window.resize(target_w, target_h)

    def get_image_base64(self, filename):
        """
        Reads an image from the assets directory and returns a Base64 data URL.
        Allows the frontend to use local project assets.
        """
        path = os.path.join(BUNDLE_DIR, 'assets', filename)
        if not os.path.exists(path):
            return ""

        try:
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                # Determine mime type based on extension
                ext = os.path.splitext(filename)[1].lower().strip('.')
                mime = f"image/{ext}" if ext != 'ico' else "image/x-icon"
                return f"data:{mime};base64,{encoded_string}"
        except Exception as e:
            log.error(f"Failed to encode image {filename}: {e}")
            return ""

    def get_app_config(self):
        """Returns the global application configuration, integrating registry settings."""
        config = self.app_state.config.copy()
        config['check_for_updates'] = self.app_state.check_for_updates
        return config

    def save_app_config(self, new_config):
        """Saves the application configuration and updates internal state."""
        try:
            if 'check_for_updates' in new_config:
                save_setting('AutomaticUpdates', new_config['check_for_updates'])
                self.app_state.check_for_updates = new_config['check_for_updates']
                del new_config['check_for_updates']

            self.app_state.config.update(new_config)
            save_config(self.app_state.config)
            self.app_state.reload()
            return True
        except Exception as e:
            log.error(f"Error saving config: {e}")
            return False

    def get_filetypes(self):
        """Returns the array of indexed filetypes."""
        return load_all_filetypes()

    def save_filetypes(self, filetypes):
        """Saves the filetypes array to configuration."""
        try:
            save_filetypes(filetypes)
            return True
        except Exception as e:
            log.error(f"Error saving filetypes: {e}")
            return False

    def _format_project_response(self, project_config, status_msg):
        """Helper to format ProjectConfig into a dictionary suitable for JSON serialization."""
        if not project_config:
            return None
        return {
            "path": project_config.base_dir,
            "project_name": project_config.project_name,
            "project_color": project_config.project_color,
            "project_font_color": project_config.project_font_color,
            "total_tokens": project_config.total_tokens,
            "selected_files": project_config.selected_files,
            "unknown_files": project_config.unknown_files,
            "expanded_dirs": list(project_config.expanded_dirs),
            "has_instructions": bool(project_config.intro_text or project_config.outro_text),
            "status_msg": status_msg
        }

    def get_current_project(self):
        """Loads and returns the currently active project from AppState."""
        path = self.app_state.active_directory
        if path and os.path.isdir(path):
            project_config, status_msg = self.project_manager.load_project(path)
            return self._format_project_response(project_config, status_msg)
        return None

    def get_recent_projects(self):
        """Returns a formatted list of recently opened projects for the Project Selector Modal."""
        recent = []
        for path in self.app_state.recent_projects:
            if os.path.isdir(path):
                name, color = ProjectConfig.read_project_display_info(path)
                recent.append({"path": path, "name": name, "color": color})
        return recent

    def remove_recent_project(self, path):
        """Removes a project from the recents list and returns the updated list."""
        self.app_state.remove_recent_project(path)
        return self.get_recent_projects()

    def load_project(self, path):
        """Activates and loads a specific project path."""
        if path and os.path.isdir(path):
            if self.app_state.update_active_dir(path):
                project_config, status_msg = self.project_manager.load_project(path)
                return self._format_project_response(project_config, status_msg)
        return None

    def rename_project(self, new_name):
        """Updates the name of the currently active project."""
        project_config = self.project_manager.get_current_project()
        if not project_config or not new_name.strip():
            return None

        project_config.project_name = new_name.strip()
        project_config.save()
        return self._format_project_response(project_config, f"Project renamed to '{new_name.strip()}'")

    def select_project(self):
        """
        Opens the native OS directory selection dialog.
        """
        if not self._window:
            return None

        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            selected_path = result[0]
            if self.app_state.update_active_dir(selected_path):
                project_config, status_msg = self.project_manager.load_project(selected_path)
                return self._format_project_response(project_config, status_msg)
        return None

    def copy_code(self, use_wrapper):
        """
        Merges the selected files and copies the result to the clipboard.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config or not project_config.selected_files:
            return "No files selected to copy."

        base_dir = self.app_state.active_directory
        files_to_copy = [f['path'] for f in project_config.selected_files]

        if self.app_state.scan_for_secrets:
            report = scan_for_secrets(base_dir, files_to_copy)
            if report:
                warning_message = f"Warning: Potential secrets were detected in your selection.\n\n{report}\n\nDo you still want to copy this content to your clipboard?"
                proceed = self._window.create_confirmation_dialog("Secrets Detected", warning_message)
                if not proceed:
                    return "Copy cancelled due to potential secrets."

        final_content, status_message = generate_output_string(
            base_dir,
            project_config,
            use_wrapper,
            self.app_state.copy_merged_prompt
        )

        if final_content is not None:
            pyperclip.copy(final_content)
            return status_message

        return status_message or "Error: Could not generate content."

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

        # Temporarily apply provided selection to merger logic
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

    def test(self):
        """A simple test method to verify the Vue -> Python bridge is working."""
        log.info("API test method called from Vue frontend.")
        return "Hello from Python API! The bridge is working perfectly."