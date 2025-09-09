import os
import json
import tiktoken
from .. import constants as c

def get_language_from_path(path):
    """Gets a markdown language identifier from a file path based on its extension"""
    _, ext = os.path.splitext(path)
    return c.LANGUAGE_MAP.get(ext.lower(), '') # Return empty string for unknown extensions

def generate_output_string(base_dir, project_config, use_wrapper, copy_merged_prompt):
    """
    Core logic for merging files
    Reads the .allcode file, processes files, and returns the final string and a status message
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
        # Format each file as a standard Markdown section with a fenced code block
        output_blocks.append(f"## `{path}`\n\n```{language}\n{content}\n```")

    merged_code = '\n\n'.join(output_blocks)

    if use_wrapper:
        project_title = project_config.project_name
        intro_text = project_config.intro_text
        outro_text = project_config.outro_text

        final_parts = [f"# {project_title}"]
        if intro_text:
            final_parts.append(intro_text)
        final_parts.append(merged_code)
        if outro_text:
            final_parts.append(outro_text)

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

def recalculate_token_count(base_dir, selected_files_info):
    """
    Reads selected files, concatenates their content, and counts the tokens
    """
    if not selected_files_info:
        return 0

    all_content = []
    for file_info in selected_files_info:
        rel_path = file_info['path']
        full_path = os.path.join(base_dir, rel_path)
        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                all_content.append(f.read())
        except FileNotFoundError:
            # File might have been deleted, just skip it
            continue

    full_text = "\n".join(all_content)

    try:
        # cl100k_base is the encoding for gpt-4, gpt-3.5-turbo, and text-embedding-ada-002
        encoding = tiktoken.get_encoding("cl100k_base")
        # Using disallowed_special=() to count all tokens without errors
        total_tokens = len(encoding.encode(full_text, disallowed_special=()))
        return total_tokens
    except Exception:
        # If tiktoken fails for any reason, return -1 to indicate an error
        return -1