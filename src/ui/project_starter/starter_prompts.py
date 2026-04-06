import os
import tkinter as tk
from ... import constants as c
from ...core import prompts as p
from ...core.paths import REFERENCE_DIR
from .segment_manager import SegmentManager

def get_base_project_content(project_data):
    """
    Collects code from the base project's merge list for inclusion in LLM prompts.
    """
    base_path = project_data.get("base_project_path", tk.StringVar()).get()
    base_files = project_data.get("base_project_files",[])
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

def get_concept_prompt(project_data, questions_map):
    """Constructs the prompt for Step 3: Concept."""
    user_goal = project_data.get("goal", "")
    friendly_map = {k: v["label"] for k, v in questions_map.items()}
    segment_instructions = SegmentManager.build_prompt_instructions(c.CONCEPT_ORDER, friendly_map)

    parts = [
        p.STARTER_CONCEPT_PROMPT_INTRO,
        "\n### User Goal\n```\n" + user_goal.strip() + "\n```",
        get_base_project_content(project_data),
        "\n### Format Instructions",
        segment_instructions,
        p.STARTER_CONCEPT_PROMPT_CORE_INSTR
    ]
    return "\n".join(parts)

def get_stack_prompt(project_data):
    """Constructs the prompt for Step 4: Stack."""
    concept = project_data.get("concept_md", "")
    experience = project_data.get("stack_experience", "")
    parts = [
        p.STARTER_STACK_PROMPT_INTRO,
        "\n### Developer Experience\n```\n" + (experience if experience.strip() else "No specific experience listed. Recommend standard industry defaults.") + "\n```",
        "\n### Project Concept\n```markdown\n" + concept + "\n```",
        p.STARTER_STACK_PROMPT_INSTR
    ]
    return "\n".join(parts)

def get_todo_prompt(project_data, questions_map):
    """Constructs the prompt for Step 5: TODO."""
    concept_md = project_data.get("concept_md")
    if not concept_md and project_data.get("concept_segments"):
        concept_md = SegmentManager.assemble_document(project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS)

    stack = project_data["stack"].get()
    example_code = get_base_project_content(project_data)

    template_path = os.path.join(REFERENCE_DIR, "todo.md")
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            todo_template = f.read()
    except Exception:
        todo_template = "(Template not found)"

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