import os
import json
from .. import constants as c
from .utils import get_token_count_for_text

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
        output_blocks.append(f"--- File: `{path}` ---\n\n```{language}\n{content}\n```\n\n--- End of file ---")

    merged_code = '\n\n'.join(output_blocks)

    if use_wrapper:
        project_title = project_config.project_name
        intro_text = project_config.intro_text
        outro_text = project_config.outro_text

        # Always prepended to the wrapped outro text
        formatting_instruction = """**CRITICAL INSTRUCTIONS FOR CODE GENERATION - READ CAREFULLY:**

1. **NO CODE TRUNCATION (STRICT REQUIREMENT):**
   - You MUST provide the **FULL, COMPLETE content** for EVERY file you modify.
   - **DO NOT** use comments like `// ... rest of code`, `/* unchanged */`, or `[previous logic here]`.
   - Any missing lines will result in the permanent deletion of that code from my project. Truncation is a failure to follow instructions and causes data loss.

2. **STRICT CHANGE DETECTION & OUTPUT MINIMIZATION:**
   - ONLY output files that have actually been modified.
   - If a file's final code is **byte-for-byte identical** to the original input provided in this prompt, **DO NOT** include it in your output.
   - You may list names of unchanged files at the end of your response, but do not wrap them in code blocks.

3. **MANDATORY OUTPUT FORMAT (PARSER COMPATIBILITY):**
   - Every modified file MUST be wrapped exactly like this template:
   --- File: `path/to/file.ext` ---
   ```[language_id]
   [full code here]
   ```
   --- End of file ---

4. **VERIFICATION SUMMARY (POST-CODE):**
   - Immediately following the final "--- End of file ---" marker, include a section titled:
   ### Summary & Verification
   - **Logic Changes:** Bulleted list of behavioral/algorithmic changes.
   - **UI Changes:** Bulleted list of visual/layout modifications.
   - **Verification Steps:** A clear list of actions I must take to test these specific changes.

5. **FILE OPERATIONS:**
   - If your modifications make certain existing files obsolete, explicitly state: "DELETE FILE: `path/to/obsolete_file.ext`" in the Summary section."""

        if outro_text:
            final_outro = f"{formatting_instruction}\n\n{outro_text}"
        else:
            final_outro = formatting_instruction

        final_parts = [f"# {project_title}"]
        if intro_text:
            final_parts.append(intro_text)
        final_parts.append(merged_code)
        final_parts.append(final_outro)

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
    return get_token_count_for_text(full_text)