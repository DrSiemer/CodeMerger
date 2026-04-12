import os
import logging
import tkinter as tk
from src.core import prompts as p
from src import constants as c
from src.core.paths import BOILERPLATE_DIR, REFERENCE_DIR
from src.core.merger import get_language_from_path

log = logging.getLogger("CodeMerger")

class StarterApiPrompts:
    """API methods handling construction of prompts for the Project Starter."""

    def _get_base_project_content(self, project_data):
        # Defensive check to prevent 'NoneType' object has no attribute 'get'
        if project_data is None:
            project_data = {}

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

                # Use the imported function from merger core
                language = get_language_from_path(rel_path)
                content_blocks.append(f"--- File: `{rel_path}` ---\n```{language}\n{content}\n```\n")
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
        if project_data is None: project_data = {}

        user_goal = project_data.get("goal", "")
        friendly_map = {k: v.get("label", k) for k, v in questions_map.items()} if questions_map else c.CONCEPT_SEGMENTS
        segment_instructions = self._build_prompt_instructions(c.CONCEPT_ORDER, friendly_map)

        concept_template = self.get_concept_template()

        parts = [
            p.STARTER_CONCEPT_PROMPT_INTRO,
            "\n### User Goal\n```\n" + user_goal.strip() + "\n```",
            "\n### Reference Template (Standard Concept Structure)\n```markdown\n" + concept_template + "\n```" if concept_template else "",
            self._get_base_project_content(project_data),
            "\n### Format Instructions",
            segment_instructions,
            p.STARTER_CONCEPT_PROMPT_CORE_INSTR
        ]
        return "\n".join(parts)

    def generate_stack_prompt(self, project_data):
        """Constructs and returns the Tech Stack recommendation prompt."""
        if project_data is None: project_data = {}

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
        if project_data is None: project_data = {}

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
        if project_data is None: project_data = {}

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
                        # This teaches the LLM the correct response format by example.
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

    def get_starter_rewrite_prompt(self, instruction, targets, references, names, data, is_merged_mode=False):
        """Generates a prompt for instructional rewriting of starter segments."""
        if data is None: data = {}

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
        if segments_data is None: segments_data = {}

        target_context_str = "\n".join([f"--- Current Draft: {friendly_names_map.get(k, k)} ---\n{segments_data.get(k, '')}\n" for k in targets])
        ref_context_str = ""
        if references:
            ref_context_str = "\n### Locked Sections (Reference Only)\n" + "\n".join([f"--- Locked Section: {friendly_names_map.get(k, k)} ---\n{segments_data.get(k, '')}\n" for k in references])

        return p.STARTER_SYNC_PROMPT_TEMPLATE.format(
            current_name=friendly_names_map.get(active_key, active_key),
            content=segments_data.get(active_key, ""),
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