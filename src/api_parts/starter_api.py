import os
import json
import re
import logging
import webview
from pathlib import Path
from src.core.paths import PERSISTENT_DATA_DIR, REFERENCE_DIR, BOILERPLATE_DIR
from src.core.project_config import ProjectConfig
from src.core.utils import parse_gitignore
from src.ui.file_manager.file_tree_builder import build_file_tree_data
from src.core import prompts as p
from src import constants as c

log = logging.getLogger("CodeMerger")

class StarterApi:
    """API methods concerning the comprehensive Project Starter feature pipeline."""

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

        if filepath and len(filepath) > 0:
            try:
                with open(filepath[0], "w", encoding="utf-8") as f:
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

        if filepath and len(filepath) > 0:
            try:
                with open(filepath[0], "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Failed to load config: {e}")
                return None
        return None

    def get_concept_questions(self):
        """Loads guiding questions for the Concept step."""
        try:
            with open(os.path.join(REFERENCE_DIR, "concept_questions.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_todo_questions(self):
        """Loads guiding questions for the TODO step."""
        try:
            with open(os.path.join(REFERENCE_DIR, "todo_questions.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_todo_template(self):
        """Returns the raw content of the reference TODO template."""
        try:
            with open(os.path.join(REFERENCE_DIR, "todo.md"), "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def get_base_project_data(self, path):
        """Loads .allcode from a path without making it active. READ-ONLY."""
        if not path or not os.path.isdir(path):
            return None

        config = ProjectConfig(path)
        try:
            # We use load() which handles reconciliation but we won't save() back.
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

        # Determine selection set
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

    def _get_base_project_content(self, project_data):
        base_path = project_data.get("base_project_path", "")
        base_files = project_data.get("base_project_files", [])
        if not base_path or not base_files:
            return ""

        content_blocks = ["\n### Example Project Code (For Reference Only)\n"]
        for file_info in base_files:
            rel_path = file_info['path']
            full_path = os.path.join(base_path, rel_path)
            try:
                with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    content = f.read()
                content_blocks.append(f"--- File: `{rel_path}` ---\n```\n{content}\n```\n")
            except Exception:
                pass
        return "\n".join(content_blocks)

    def _build_prompt_instructions(self, segment_keys, friendly_names_map):
        instructions = [
            "You MUST structure your response using specific section separators.",
            "Do not add any text outside these sections.",
            "For each section, output the delimiter followed immediately by the content and close it.",
            "\nREQUIRED FORMAT:"
        ]
        for key in segment_keys:
            name = friendly_names_map.get(key, key)
            delimiter = c.DELIMITER_TEMPLATE.format(name=name)
            instructions.append(f"{delimiter}\n... content for {name} ...\n</SECTION>")
        return "\n".join(instructions)

    def generate_concept_prompt(self, project_data, questions_map):
        """Constructs and returns the Concept generation prompt."""
        user_goal = project_data.get("goal", "")
        friendly_map = {k: v.get("label", k) for k, v in questions_map.items()} if questions_map else c.CONCEPT_SEGMENTS
        segment_instructions = self._build_prompt_instructions(c.CONCEPT_ORDER, friendly_map)

        parts = [
            p.STARTER_CONCEPT_PROMPT_INTRO,
            "\n### User Goal\n```\n" + user_goal.strip() + "\n```",
            self._get_base_project_content(project_data),
            "\n### Format Instructions",
            segment_instructions,
            p.STARTER_CONCEPT_PROMPT_CORE_INSTR
        ]
        return "\n".join(parts)

    def generate_stack_prompt(self, project_data):
        """Constructs and returns the Tech Stack recommendation prompt."""
        concept = project_data.get("concept_md", "")
        experience = project_data.get("stack_experience", "")
        parts = [
            p.STARTER_STACK_PROMPT_INTRO,
            "\n### Developer Experience\n```\n" + (experience.strip() if experience.strip() else "No specific experience listed. Recommend standard industry defaults.") + "\n```",
            "\n### Project Concept\n```markdown\n" + concept + "\n```",
            p.STARTER_STACK_PROMPT_INSTR
        ]
        return "\n".join(parts)

    def generate_todo_prompt(self, project_data, questions_map):
        """Constructs and returns the TODO plan generation prompt."""
        concept_md = project_data.get("concept_md")
        if not concept_md and project_data.get("concept_segments"):
            concept_md = self.assemble_starter_document(project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS)

        stack = project_data.get("stack", "")
        example_code = self._get_base_project_content(project_data)
        todo_template = self.get_todo_template() or "(Template not found)"
        valid_headers = [v for k, v in c.TODO_PHASES.items()]
        headers_str = ", ".join([f'"{h}"' for h in valid_headers])

        parts = [
            p.STARTER_TODO_PROMPT_INTRO,
            "\n### Tech Stack\n" + stack,
            "\n### Project Concept\n```markdown\n" + (concept_md or "No concept provided.") + "\n```",
            example_code,
            "\n### Reference Template (Standard TODO List)\n```markdown\n" + todo_template + "\n```",
            p.STARTER_TODO_PROMPT_INSTR.format(headers_str=headers_str)
        ]
        return "\n".join(parts)

    def generate_master_prompt(self, project_data):
        """Constructs and returns the final Project Boilerplate generation prompt."""
        name = project_data.get("name", "")
        stack = project_data.get("stack", "")

        concept = self.assemble_starter_document(project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS) if project_data.get("concept_segments") else project_data.get("concept_md", "")
        todo = self.assemble_starter_document(project_data["todo_segments"], c.TODO_ORDER, c.TODO_PHASES) if project_data.get("todo_segments") else project_data.get("todo_md", "")

        prompt_content = ""
        try:
            files = sorted([
                f for f in os.listdir(BOILERPLATE_DIR)
                if os.path.isfile(os.path.join(BOILERPLATE_DIR, f))
                and f not in {'.DS_Store', 'Thumbs.db', '_start.txt'}
            ])
            for filename in files:
                path = os.path.join(BOILERPLATE_DIR, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        # Include the '--- End of file ---' marker for consistency
                        prompt_content += f"--- File: `boilerplate/{filename}` ---\n```\n{f.read()}\n```\n--- End of file ---\n\n"
                except Exception:
                    pass
        except Exception:
            prompt_content = "Error loading boilerplate files."

        example_code = self._get_base_project_content(project_data)

        parts = [
            p.STARTER_GENERATE_MASTER_INTRO.format(name=name, stack=stack),
            "\n### Provided Files\n" + prompt_content,
            "\n### Project Concept\n```markdown\n" + concept + "\n```",
            "\n### TODO Plan\n```markdown\n" + todo + "\n```",
            example_code,
            p.STARTER_GENERATE_MASTER_INSTR
        ]
        return "\n".join(parts)

    def parse_starter_segments(self, text):
        """Parses segmented XML-style output from LLM for the Project Starter."""
        pattern = re.compile(r'<SECTION name="([^"]+)">\s*(.*?)(?=</SECTION>|<SECTION name=|$)', re.DOTALL | re.IGNORECASE)
        matches = pattern.findall(text)
        segments = {}
        if not matches: return {}
        for name, content in matches: segments[name.strip()] = content.strip()
        return segments

    def map_parsed_segments_to_keys(self, parsed_data, friendly_names_map):
        """Maps friendly display names from LLM output to internal data keys."""
        def normalize(s): return re.sub(r'[^a-z0-9]', '', s.lower())
        norm_label_to_key = {normalize(v): k for k, v in friendly_names_map.items()}
        norm_key_to_key = {normalize(k): k for k in friendly_names_map.keys()}
        keyed_data = {}
        for name, content in parsed_data.items():
            norm_name = normalize(name)
            key = norm_label_to_key.get(norm_name)
            if not key: key = norm_key_to_key.get(norm_name)
            if key: keyed_data[key] = content
            else: keyed_data[name] = content
        return keyed_data

    def assemble_starter_document(self, segments_dict, order_keys, friendly_names_map):
        """Combines multiple segments into a single Markdown document."""
        doc_parts = []
        for key in order_keys:
            if key in segments_dict and segments_dict[key].strip():
                friendly_name = friendly_names_map.get(key, key)
                content = segments_dict[key].strip()
                doc_parts.append(f"## {friendly_name}\n\n{content}")
        return "\n\n".join(doc_parts)

    def get_starter_rewrite_prompt(self, instruction, targets, references, names, data, is_merged_mode=False):
        """Generates a prompt for instructional rewriting of starter segments."""
        if is_merged_mode:
            target_blocks = [f"{data.get('full_content', '')}"]
            reference_blocks = []
            target_instructions = "Return the complete updated Markdown document."
        else:
            target_blocks = []
            for t in targets:
                name = names.get(t, t)
                content = data.get(t, "")
                target_blocks.append(f"--- Draft: {name} ---\n{content}\n")

            reference_blocks = []
            for r in references:
                name = names.get(r, r)
                content = data.get(r, "")
                reference_blocks.append(f"--- Locked Section: {name} ---\n{content}\n")

            friendly_map = {k: names.get(k, k) for k in targets}
            target_instructions = self._build_prompt_instructions(targets, friendly_map)

        references_str = ""
        consistency_instr = "Ensure the rewritten content is internally consistent."
        if reference_blocks:
            references_str = "\n\n### Locked Sections (Reference Only - DO NOT CHANGE)\n" + "".join(reference_blocks)
            consistency_instr = "Ensure consistency with 'Locked Sections' (Reference Only), but do not modify them."

        return p.STARTER_REWRITE_PROMPT_TEMPLATE.format(
            instruction=instruction,
            references=references_str,
            targets=''.join(target_blocks),
            consistency_instr=consistency_instr,
            target_instructions=target_instructions
        )

    def get_starter_sync_prompt(self, active_key, friendly_names_map, segments_data, targets, references):
        """Generates a prompt for propagating manual changes to other segments."""
        target_context_str = "\n".join([f"--- Current Draft: {friendly_names_map.get(k, k)} ---\n{segments_data.get(k, '')}\n" for k in targets])
        ref_context_str = ""
        if references:
            ref_context_str = "\n### Locked Sections (Reference Only)\n" + "\n".join([f"--- Locked Section: {friendly_names_map.get(k, k)} ---\n{segments_data.get(k, '')}\n" for k in references])

        return p.STARTER_SYNC_PROMPT_TEMPLATE.format(
            current_name=friendly_names_map.get(active_key, active_key),
            content=segments_data[active_key],
            ref_context=ref_context_str,
            target_context=target_context_str,
            target_instructions=self._build_prompt_instructions(targets, friendly_names_map)
        )

    def get_starter_question_prompt(self, context_str, current_name, current_text, question):
        """Generates a prompt based on guiding questions."""
        return p.STARTER_QUESTION_PROMPT_TEMPLATE.format(
            context_label="Context",
            context_content=context_str,
            focus_name=current_name,
            focus_content=current_text,
            question=question,
            instruction_suffix=f"Focus ONLY on the segment '{current_name}'. Please answer the question or provide critical feedback regarding this segment. Do NOT rewrite the text."
        )

    def create_starter_project(self, llm_output, include_base_reference, project_pitch, project_data):
        """Initial check for directory existence before scaffolding project."""
        raw_project_name = project_data.get("name", "")
        parent_folder = project_data.get("parent_folder", "")

        color_match = re.search(r"<COLOR>(.*?)</COLOR>", llm_output, re.DOTALL | re.IGNORECASE)
        recommended_color = color_match.group(1).strip() if color_match else None
        if recommended_color and not re.match(r'^#[0-9a-fA-F]{6}$', recommended_color):
            recommended_color = None

        def sanitize_project_name(name): return re.sub(r'[^a-zA-Z0-9_-]+', '-', name.lower()).strip('-')
        sanitized_name = sanitize_project_name(raw_project_name)
        base_dir = Path(parent_folder)
        project_path = base_dir / sanitized_name

        if project_path.exists():
            return {"status": "EXISTS", "path": str(project_path)}
        return self._do_create_starter_project(project_path, raw_project_name, parent_folder, llm_output, include_base_reference, project_pitch, project_data, recommended_color)

    def create_starter_project_overwrite(self, llm_output, include_base_reference, project_pitch, project_data):
        """Scaffolds project after user confirms directory overwrite."""
        import shutil
        raw_project_name = project_data.get("name", "")
        parent_folder = project_data.get("parent_folder", "")

        color_match = re.search(r"<COLOR>(.*?)</COLOR>", llm_output, re.DOTALL | re.IGNORECASE)
        recommended_color = color_match.group(1).strip() if color_match else None
        if recommended_color and not re.match(r'^#[0-9a-fA-F]{6}$', recommended_color):
            recommended_color = None

        def sanitize_project_name(name): return re.sub(r'[^a-zA-Z0-9_-]+', '-', name.lower()).strip('-')
        sanitized_name = sanitize_project_name(raw_project_name)
        base_dir = Path(parent_folder)
        project_path = base_dir / sanitized_name

        if project_path.exists():
            try: shutil.rmtree(project_path)
            except Exception as e: return {"status": "ERROR", "message": f"Failed to delete existing folder: {e}"}

        return self._do_create_starter_project(project_path, raw_project_name, parent_folder, llm_output, include_base_reference, project_pitch, project_data, recommended_color)

    def _do_create_starter_project(self, project_path, raw_project_name, parent_folder, llm_output, include_base_reference, project_pitch, project_data, recommended_color):
        from src.core.utils import load_config
        try: project_path.mkdir(parents=True, exist_ok=True)
        except Exception as e: return {"status": "ERROR", "message": f"Failed to create directory: {e}"}

        PREFIX = "--- "
        FILE_LABEL = "File: "
        EOF_LABEL = "End of file"
        EOF_MARKER = PREFIX + EOF_LABEL + " ---"

        start_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(FILE_LABEL), llm_output, re.MULTILINE))
        end_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(EOF_LABEL), llm_output, re.MULTILINE))
        if start_count != end_count:
            return {"status": "ERROR", "message": f"Marker mismatch ({start_count} starts, {end_count} ends). Please ask the AI to provide the full output again."}

        file_pattern = re.compile(
            re.escape(PREFIX) + r'File: `([^\n`]+)` ---\s*[\r\n]+```[^\n]*[\r\n]+(.*?)\n?```\s*[\r\n]+' + re.escape(EOF_MARKER),
            re.DOTALL
        )
        matches = file_pattern.finditer(llm_output)
        files_created = []
        found_any = False

        for match in matches:
            found_any = True
            file_path_str, content = match.groups()
            clean_rel_path = file_path_str.replace("boilerplate/", "").strip().replace('\\', '/')
            relative_path = Path(clean_rel_path)
            full_path = project_path / relative_path

            try:
                if not os.path.normpath(str(full_path)).startswith(os.path.normpath(str(project_path))): continue
                full_path.parent.mkdir(parents=True, exist_ok=True)
                sanitized_content = "\n".join([line.rstrip() for line in content.splitlines()])
                full_path.write_text(sanitized_content, encoding="utf-8")
                files_created.append(str(relative_path))
            except Exception as e: log.error(f"Failed to write file {relative_path}: {e}")

        if not found_any:
            return {"status": "ERROR", "message": "No valid file blocks found in the output. Make sure each file is wrapped with '--- File: `path` ---' and '--- End of file ---', and ensure the code is wrapped in standard triple backticks."}

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
        except Exception: pass

        try:
            with open(project_path / "project-starter.json", "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=2)
            files_created.append("project-starter.json")
        except Exception: pass

        if include_base_reference:
            base_path = project_data.get("base_project_path", "")
            base_files = project_data.get("base_project_files", [])
            ref_content = self._get_base_project_content(project_data)
            if ref_content:
                (project_path / "project_reference.md").write_text(ref_content, encoding="utf-8")
                files_created.append("project_reference.md")

        conf = load_config()
        intro = f"We are working on {project_pitch}.\n\nContinue work on the plan laid out in `todo.md`. If a bug is reported, fix it first. ONLY output `todo.md` (in full, without omissions) when explicitly updating checkbox status."
        outro = conf.get('default_outro_prompt', p.DEFAULT_OUTRO_PROMPT)

        normalized_files = []
        merge_order_exclusion_list = ['.gitignore', 'project-starter.json', '2do.txt']
        for f in files_created:
             norm = f.replace('\\', '/')
             if os.path.basename(norm) not in merge_order_exclusion_list:
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

    def test(self):
        """A simple test method to verify the Vue -> Python bridge is working."""
        log.info("API test method called from Vue frontend.")
        return "Hello from Python API! The bridge is working perfectly."