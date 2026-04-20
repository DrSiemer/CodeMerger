import os
import re
import logging
import webview
import json
from pathlib import Path
from src.core.project_config import ProjectConfig
from src.core.utils import parse_gitignore, load_config
from src.core.file_tree_builder import build_file_tree_data
from src import constants as c
from src.core import prompts as p
from src.core.paths import BOILERPLATE_DIR

log = logging.getLogger("CodeMerger")

class StarterApiScaffold:
    """API methods for scanning existing projects and scaffolding the new one."""

    def get_base_project_data(self, path):
        """Loads .codemerger data from a path without making it active. READ-ONLY."""
        if not path or not os.path.isdir(path):
            return None

        # Safety Check: Do not auto-migrate reference projects during a peek.
        # We demand the user updates the project by opening it normally first.
        codemerger_dir = os.path.join(path, '.codemerger')
        allcode_file = os.path.join(path, '.allcode')

        if not os.path.isdir(codemerger_dir) and os.path.isfile(allcode_file):
            return {
                "path": path,
                "status_msg": "ERROR: Legacy project format detected. Please open this project normally in CodeMerger to update it first."
            }

        config = ProjectConfig(path)
        try:
            # If neither the new folder nor the old file exists, it's just a folder
            if not os.path.isdir(codemerger_dir) and not os.path.isfile(allcode_file):
                return None

            config.load()
            return self._format_project_response(config, "")
        except Exception as e:
            log.error(f"Failed to load base project config: {e}")
            return None

    def get_base_file_tree(self, path, filter_text="", is_ext_filter=True, is_git_filter=True, selected_paths=None):
        """Returns the file tree for a base project path. Used in Step 2."""
        if not path or not os.path.isdir(path):
            return []

        from src.core.utils import load_active_file_extensions
        file_extensions = load_active_file_extensions()
        gitignore_patterns = parse_gitignore(path)

        sel_set = set()
        if selected_paths:
            sel_set = {f['path'] for f in selected_paths}

        raw_tree = build_file_tree_data(
            base_dir=path,
            file_extensions=file_extensions,
            gitignore_patterns=gitignore_patterns,
            filter_text=filter_text,
            is_extension_filter_active=is_ext_filter,
            selected_file_paths=sel_set,
            is_gitignore_filter_active=is_git_filter
        )
        return raw_tree

    def create_starter_project(self, llm_output, include_base_reference, project_pitch, _unused_data=None):
        """Initial check for directory existence before scaffolding project."""
        # Loads project data directly from the session file to bypass bridge limits and serialization issues
        project_data = self.get_starter_session()
        if not project_data or not isinstance(project_data, dict):
            return {"status": "ERROR", "message": "Failed to load project data from session. Please ensure your project has a name."}

        raw_project_name = project_data.get("name", "")
        parent_folder = project_data.get("parent_folder", "")

        if not raw_project_name or not parent_folder:
             return {"status": "ERROR", "message": "Project name and parent folder are required."}

        color_match = re.search(r"<COLOR>(.*?)</COLOR>", llm_output, re.DOTALL | re.IGNORECASE)
        recommended_color = color_match.group(1).strip() if color_match else None
        if recommended_color and not re.match(r'^#[0-9a-fA-F]{6}$', recommended_color):
            recommended_color = None

        def sanitize(name): return re.sub(r'[^a-zA-Z0-9_-]+', '-', name.lower()).strip('-')
        project_path = Path(parent_folder) / sanitize(raw_project_name)

        if project_path.exists():
            return {"status": "EXISTS", "path": str(project_path)}
        return self._do_create_starter_project(project_path, raw_project_name, parent_folder, llm_output, include_base_reference, project_pitch, project_data, recommended_color)

    def create_starter_project_overwrite(self, llm_output, include_base_reference, project_pitch, _unused_data=None):
        """Scaffolds project after user confirms directory overwrite."""
        import shutil
        project_data = self.get_starter_session()
        if not project_data or not isinstance(project_data, dict):
            return {"status": "ERROR", "message": "Failed to load project data from session."}

        raw_project_name = project_data.get("name", "")
        parent_folder = project_data.get("parent_folder", "")

        color_match = re.search(r"<COLOR>(.*?)</COLOR>", llm_output, re.DOTALL | re.IGNORECASE)
        recommended_color = color_match.group(1).strip() if color_match else None
        if recommended_color and not re.match(r'^#[0-9a-fA-F]{6}$', recommended_color):
            recommended_color = None

        def sanitize(name): return re.sub(r'[^a-zA-Z0-9_-]+', '-', name.lower()).strip('-')
        project_path = Path(parent_folder) / sanitize(raw_project_name)

        if project_path.exists():
            try: shutil.rmtree(project_path)
            except Exception as e: return {"status": "ERROR", "message": f"Failed to delete existing folder: {e}"}

        return self._do_create_starter_project(project_path, raw_project_name, parent_folder, llm_output, include_base_reference, project_pitch, project_data, recommended_color)

    def _do_create_starter_project(self, project_path, raw_project_name, parent_folder, llm_output, include_base_reference, project_pitch, project_data, recommended_color):
        try: project_path.mkdir(parents=True, exist_ok=True)
        except Exception as e: return {"status": "ERROR", "message": f"Failed to create directory: {e}"}

        EOF_MARKER = c.MARKER_PREFIX + c.MARKER_EOF + " ---"

        start_count = len(re.findall(r'^' + re.escape(c.MARKER_PREFIX) + re.escape(c.MARKER_FILE), llm_output, re.MULTILINE))
        end_count = len(re.findall(r'^' + re.escape(c.MARKER_PREFIX) + re.escape(c.MARKER_EOF), llm_output, re.MULTILINE))
        if start_count != end_count:
            return {"status": "ERROR", "message": f"Marker mismatch ({start_count} starts, {end_count} ends)."}

        file_pattern = re.compile(
            re.escape(c.MARKER_PREFIX) + r'File: `([^\n`]+)` ---\s*[\r\n]+```[^\n]*[\r\n]+(.*?)\n?```\s*[\r\n]+' + re.escape(EOF_MARKER),
            re.DOTALL
        )
        matches = file_pattern.finditer(llm_output)
        files_created = []
        found_any = False

        for match in matches:
            found_any = True
            file_path_str, content = match.groups()
            clean_rel_path = file_path_str.replace("boilerplate/", "").strip().replace('\\', '/')
            full_path = project_path / Path(clean_rel_path)

            try:
                if not os.path.normpath(str(full_path)).startswith(os.path.normpath(str(project_path))): continue
                full_path.parent.mkdir(parents=True, exist_ok=True)
                sanitized_content = "\n".join([line.rstrip() for line in content.splitlines()])
                full_path.write_text(sanitized_content, encoding="utf-8")
                files_created.append(str(clean_rel_path))
            except Exception as e: log.error(f"Failed to write file {clean_rel_path}: {e}")

        if not found_any:
            return {"status": "ERROR", "message": "No valid file blocks found."}

        # Dumps to string first to ensure serialization succeeds before truncating file
        try:
            target_json = project_path / "project-starter.json"
            json_str = json.dumps(project_data, indent=2)
            with open(str(target_json), "w", encoding="utf-8") as f:
                f.write(json_str)
            files_created.append("project-starter.json")
        except Exception as e:
            log.error(f"Failed to write project-starter.json: {e}")

        try:
            concept_segs = project_data.get("concept_segments")
            concept_content = self.assemble_starter_document(concept_segs, c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS) if concept_segs else project_data.get("concept_md", "")
            if concept_content:
                (project_path / "concept.md").write_text(concept_content, encoding="utf-8")
                files_created.append("concept.md")

            todo_segs = project_data.get("todo_segments")
            todo_content = self.assemble_starter_document(todo_segs, c.TODO_ORDER, c.TODO_PHASES) if todo_segs else project_data.get("todo_md", "")
            if todo_content:
                (project_path / "todo.md").write_text(todo_content, encoding="utf-8")
                files_created.append("todo.md")
        except Exception as e:
            log.error(f"Failed to write documentation files: {e}")

        if include_base_reference:
            ref_content = self._get_base_project_content(project_data)
            if ref_content:
                try:
                    (project_path / "project_reference.md").write_text(ref_content, encoding="utf-8")
                    files_created.append("project_reference.md")
                except Exception as e:
                    log.error(f"Failed to write project_reference.md: {e}")

        conf = load_config()
        intro = f"We are working on {project_pitch}.\n\nContinue work on the plan laid out in `todo.md`. If a bug is reported, fix it first. ONLY output `todo.md` (in full, without omissions) when explicitly updating checkbox status."
        outro = conf.get('default_outro_prompt', p.DEFAULT_OUTRO_PROMPT)

        normalized_files = []
        # Excludes temporary files and specific artifacts from the initial merge selection
        merge_order_exclusion_list = ['.gitignore', 'project-starter.json', '2do.txt', c.ALLCODE_TEMP_PREFIX]
        for f in files_created:
             norm = f.replace('\\', '/')
             filename = os.path.basename(norm)
             if filename not in merge_order_exclusion_list and \
                filename not in c.FILES_TO_IGNORE_FOR_VISUAL_COMPLETENESS and \
                not filename.startswith(c.ALLCODE_TEMP_PREFIX):
                 normalized_files.append({'path': norm})

        self.project_manager.create_project_with_defaults(
            path=str(project_path),
            project_name=raw_project_name,
            intro_text=intro,
            outro_text=outro,
            initial_selected_files=normalized_files,
            project_color=recommended_color
        )

        return {
            "status": "SUCCESS",
            "project_name": project_path.name,
            "files_created": files_created,
            "parent_folder": parent_folder,
            "project_color": recommended_color,
            "project_path": str(project_path)
        }