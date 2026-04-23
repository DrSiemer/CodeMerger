import os
from .. import constants as c
from .prompts import (
    INSTR_FULL_FILE, INSTR_FAST_APPLY, EXAMPLE_FULL_FILE, EXAMPLE_FAST_APPLY,
    FORMATTING_INSTRUCTION_TEMPLATE, AUTOMATION_WARNING_TEMPLATE
)
from .utils import get_token_count_for_text

def get_language_from_path(path):
    """Maps file extensions to Markdown code block identifiers"""
    _, ext = os.path.splitext(path)
    return c.LANGUAGE_MAP.get(ext.lower(), '')

def generate_output_string(base_dir, project_config, use_wrapper, copy_merged_prompt, enable_fast_apply=False):
    """
    Concatenates selected files into a single machine-parseable string
    Returns the final string and a status message
    """
    if not project_config.selected_files:
        return None, "No files selected to copy"

    final_ordered_list = [f['path'] for f in project_config.selected_files]

    output_blocks = []
    skipped_files = []

    for path in final_ordered_list:
        full_path = os.path.join(base_dir, path)
        if not os.path.isfile(full_path):
            skipped_files.append(path)
            continue
        with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as code_file:
            content = code_file.read()

        language = get_language_from_path(path)

        # Build block using central markers
        block_header = f"{c.MARKER_PREFIX}{c.MARKER_FILE}`{path}` ---"
        block_footer = f"{c.MARKER_PREFIX}{c.MARKER_EOF} ---"

        output_blocks.append(f"{block_header}\n```{language}\n{content}\n```\n{block_footer}")

    merged_code = '\n\n'.join(output_blocks)

    if use_wrapper:
        project_title = project_config.project_name

        intro_text = project_config.intro_text
        if isinstance(intro_text, (list, tuple)):
            intro_text = "\n".join(intro_text)

        outro_text = project_config.outro_text
        if isinstance(outro_text, (list, tuple)):
            outro_text = "\n".join(outro_text)

        # Build dynamic mode-based instructions
        mode_instruction = INSTR_FAST_APPLY if enable_fast_apply else INSTR_FULL_FILE
        example_content = EXAMPLE_FAST_APPLY if enable_fast_apply else EXAMPLE_FULL_FILE

        formatting_instruction = FORMATTING_INSTRUCTION_TEMPLATE.format(
            mode_instruction=mode_instruction,
            example_content=example_content,
            marker_prefix=c.MARKER_PREFIX,
            marker_file=c.MARKER_FILE,
            marker_eof=c.MARKER_EOF
        )

        automation_warning = AUTOMATION_WARNING_TEMPLATE.format(
            marker_prefix=c.MARKER_PREFIX,
            marker_file=c.MARKER_FILE
        )

        final_parts = [f"# {project_title}"]

        if intro_text:
            final_parts.append(intro_text)

        final_parts.append(formatting_instruction)
        final_parts.append("## Project Files")
        final_parts.append(merged_code)

        footer_parts = []
        if outro_text:
            footer_parts.append(outro_text)
        footer_parts.append(automation_warning)

        final_parts.append('\n\n'.join(footer_parts))

        final_content = '\n\n'.join(final_parts) + '\n'
        status_message = "Wrapped code copied as Markdown"
    else:
        if copy_merged_prompt:
            final_content = copy_merged_prompt + "\n\n" + merged_code
        else:
            final_content = merged_code
        status_message = "Merged code copied as Markdown"

    if skipped_files:
        status_message += f". Skipped {len(skipped_files)} missing file(s)"

    return final_content, status_message

def generate_subset_output(base_dir, paths):
    """
    Bundles a specific list of file paths into standard CodeMerger Markdown blocks.
    Used by the Visualizer to copy code for specific nodes/subtrees.
    """
    output_blocks = []
    for path in paths:
        full_path = os.path.join(base_dir, path)
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as code_file:
                content = code_file.read()
        except OSError:
            continue

        language = get_language_from_path(path)

        block_header = f"{c.MARKER_PREFIX}{c.MARKER_FILE}`{path}` ---"
        block_footer = f"{c.MARKER_PREFIX}{c.MARKER_EOF} ---"

        output_blocks.append(f"{block_header}\n```{language}\n{content}\n```\n{block_footer}")

    return '\n\n'.join(output_blocks)

def recalculate_token_count(base_dir, selected_files_info):
    """
    Summarizes total tokens for the current selection set.
    Optimized to handle massive projects by processing files individually
    to reduce memory overhead and re-using the global tokenizer instance.
    """
    if not selected_files_info:
        return 0

    total = 0
    for file_info in selected_files_info:
        rel_path = file_info['path']
        full_path = os.path.join(base_dir, rel_path)
        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
                # Individual token counts are faster and more memory efficient than joining strings
                count = get_token_count_for_text(content)
                if count > 0:
                    total += count
        except FileNotFoundError:
            continue

    return total