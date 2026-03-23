import os
import json
import re
import logging
from pathlib import Path
from tkinter import messagebox
from ... import constants as c
from ...core import prompts as p
from ...core.utils import load_config
from . import generator
from .segment_manager import SegmentManager
from . import starter_validator

log = logging.getLogger("CodeMerger")

class StarterProjectCreator:
    def __init__(self, dialog):
        self.dialog = dialog

    def create_project(self, llm_output, include_base_reference=False, project_pitch="a new project"):
        dialog = self.dialog
        is_valid, err_title, err_msg = starter_validator.validate_step(6, dialog.starter_state.project_data)
        if not is_valid:
            messagebox.showerror(err_title, err_msg, parent=dialog)
            return

        if not llm_output.strip():
            messagebox.showerror("Error", "LLM Result text area is empty.", parent=dialog)
            return

        raw_project_name = dialog.starter_state.project_data["name"].get()
        parent_folder = dialog.starter_state.project_data["parent_folder"].get()

        color_match = re.search(r"<COLOR>(.*?)</COLOR>", llm_output, re.DOTALL | re.IGNORECASE)
        recommended_color = color_match.group(1).strip() if color_match else None
        if recommended_color and not re.match(r'^#[0-9a-fA-F]{6}$', recommended_color):
            recommended_color = None

        success, project_path, msg = generator.prepare_project_directory(parent_folder, raw_project_name)
        if not success:
            if "already exists" in msg:
                if messagebox.askyesno("Warning", f"{msg} Overwrite?", parent=dialog):
                    success, project_path, msg = generator.prepare_project_directory(parent_folder, raw_project_name, overwrite=True)
                else: return
            if not success:
                messagebox.showerror("Error", msg, parent=dialog)
                return

        success, files_created, msg = generator.parse_and_write_files(project_path, llm_output)
        if not success:
            messagebox.showerror("Error", msg, parent=dialog)
            return

        try:
            concept_segs = dialog.starter_state.project_data.get("concept_segments")
            concept_content = SegmentManager.assemble_document(concept_segs, c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS) if concept_segs else dialog.starter_state.project_data.get("concept_md", "")
            if concept_content:
                (project_path / "concept.md").write_text(concept_content, encoding="utf-8")
                files_created.append("concept.md")

            todo_segs = dialog.starter_state.project_data.get("todo_segments")
            todo_content = SegmentManager.assemble_document(todo_segs, c.TODO_ORDER, c.TODO_PHASES) if todo_segs else dialog.starter_state.project_data.get("todo_md", "")
            if todo_content:
                (project_path / "todo.md").write_text(todo_content, encoding="utf-8")
                files_created.append("todo.md")
        except Exception as e:
            log.error(f"Failed to write mandatory documentation files: {e}")

        try:
            config_data = dialog.starter_state.get_dict()
            starter_json_path = project_path / "project-starter.json"
            with open(starter_json_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            files_created.append("project-starter.json")
        except Exception as e:
            log.error(f"Failed to write project-starter.json: {e}")

        if include_base_reference:
            base_path = dialog.starter_state.project_data["base_project_path"].get()
            base_files = dialog.starter_state.project_data["base_project_files"]
            if generator.write_base_reference_file(project_path, base_path, base_files):
                files_created.append("project_reference.md")

        conf = load_config()
        intro = f"We are working on {project_pitch}.\n\nContinue work on the plan laid out in `todo.md`. If a bug is reported, fix it first. ONLY output `todo.md` (in full, without omissions) when explicitly updating checkbox status."
        outro = conf.get('default_outro_prompt', p.DEFAULT_OUTRO_PROMPT)

        normalized_files = []
        merge_order_exclusion_list =['.gitignore', 'project-starter.json', '2do.txt']

        for f in files_created:
             norm = f.replace('\\', '/')
             if os.path.basename(norm) not in merge_order_exclusion_list:
                 normalized_files.append({'path': norm})

        dialog.app.project_manager.create_project_with_defaults(
            path=str(project_path),
            project_name=raw_project_name,
            intro_text=intro,
            outro_text=outro,
            initial_selected_files=normalized_files,
            project_color=recommended_color
        )

        dialog._display_success_screen(project_path.name, files_created, parent_folder, recommended_color)