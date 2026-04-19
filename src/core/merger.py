import os
import json
from .. import constants as c
from .prompts import INSTR_FULL_FILE, INSTR_FAST_APPLY, EXAMPLE_FULL_FILE, EXAMPLE_FAST_APPLY
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

        formatting_instruction = f"""**CRITICAL INSTRUCTIONS FOR CODE GENERATION - READ CAREFULLY:**

1. **MANDATORY TAGGING & CLOSING POLICY:**
   Every section of your response (Answers, Intro, Changes, Delete, Verification) MUST be explicitly wrapped in tags.
   **CRITICAL:** Every opening tag MUST have an identical closing tag.
   Format: `<INTRO>[content]</INTRO>`

2. **INTRO, ANSWERS & CHANGES (PRE-CODE):**
   Immediately before the code blocks, provide these sections in this order:
   - **<INTRO>**: Use this to provide a technical implementation plan or architectural summary.
   - **<ANSWERS TO DIRECT USER QUESTIONS>**: If the user asked a specific question (usually ending with a '?'), answer it here. If there is no question mark in the prompt, there is no question. In that case, this block MUST remain empty (use a single dash `-`). Do NOT fill it with filler text like "None" or "No questions".
   - **<CHANGES>**: List of behavioral, algorithmic, or visual changes.

3. **{mode_instruction}**

4. **EVOLVED BASELINE AWARENESS (SESSION CONTEXT):**
   - You must acknowledge that the codebase evolves. If a file has been modified in previous turns of this conversation, that modified version is your only valid baseline for the ORIGINAL block.
   - NEVER reference the initial code blocks from the start of the chat if they have been superceded by your own subsequent changes.

5. **FUNCTIONAL PRESERVATION:**
   - Do not remove or break any existing functionality.
   - NO SILENT REFACTORING: Do not "improve," "clean up," or "simplify" any code that is not directly related to the requested change. Leave unrelated logic and comments untouched.

6. **STRICT CHANGE DETECTION & OUTPUT MINIMIZATION:**
   - ONLY output files that have actually been modified.
   - If a file's final code is **byte-for-byte identical** to the current state of the project, **DO NOT** include it in your output.
   - **UNCHANGED FILES (LAST RESORT ONLY):** If you feel a strict compulsion to acknowledge files you didn't modify, use the optional `<UNCHANGED>` block at the very end of your response. DO NOT output this block if you can simply stop yourself from outputting unchanged files. It is only here to prevent you from wasting tokens on unmodified code blocks.

7. **MANDATORY OUTPUT FORMAT (PARSER COMPATIBILITY):**
   - Every modified file MUST be wrapped exactly like this template, including the trailing marker:

{c.MARKER_PREFIX}{c.MARKER_FILE}`path/to/file.ext` ---
```[language_id]
{example_content}
```
{c.MARKER_PREFIX}{c.MARKER_EOF} ---

   - **CRITICAL:** The `{c.MARKER_PREFIX}{c.MARKER_EOF} ---` marker is a machine-parseable sentinel. It MUST be present after every file block.

8. **DELETE, VERIFICATION & UNCHANGED (POST-CODE):**
   Immediately following the final "--- End of file ---" marker, provide these sections:

   <DELETED FILES>
   STRICT FILE PATHS ONLY.
   FORMAT: DELETE FILE: path/to/obsolete_file.ext
   PROHIBITION: Do NOT describe code-level removals, logic deletions, or "cleanup."
   If no files were deleted from the filesystem, this section should ONLY contain a single dash (`-`). Do NOT write "None" or any other text.
   </DELETED FILES>

   <VERIFICATION>
   - Steps to test the changes.
   </VERIFICATION>

   <UNCHANGED>
   (OPTIONAL: You may list the names of unchanged files here to satisfy any compulsion to acknowledge them without outputting their code. Omit this block entirely if possible.)
   </UNCHANGED>

==========

You MUST format your EXACT output using this skeleton. Do not deviate from this structure:

<INTRO>
(Implementation plan)
</INTRO>

<ANSWERS TO DIRECT USER QUESTIONS>
(Answer any direct questions here, otherwise `-`)
</ANSWERS TO DIRECT USER QUESTIONS>

<CHANGES>
(List of changes)
</CHANGES>

{c.MARKER_PREFIX}{c.MARKER_FILE}`path/to/file.ext` ---
```language
(Full unabridged file code or surgical blocks as instructed)
```
{c.MARKER_PREFIX}{c.MARKER_EOF} ---

<DELETED FILES>
(Files to delete, or `-`)
</DELETED FILES>

<VERIFICATION>
(Testing steps)
</VERIFICATION>"""

        automation_warning = f"CRITICAL: I am using an automated parser. Please begin your response directly with the <INTRO> tag. You MUST use the exact XML tags and {c.MARKER_PREFIX}{c.MARKER_FILE} wrappers shown in the template. If you use `// ...` or `[rest of code]`, the parser will crash and your response will be useless. You must mirror every single line of the file (or the exact surgical blocks) without omitting lines within the block."

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