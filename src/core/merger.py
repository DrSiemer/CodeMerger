import os
import json
from .. import constants as c
from .prompts import DEFAULT_COPY_MERGED_PROMPT
from .utils import get_token_count_for_text

def get_language_from_path(path):
    """Maps file extensions to Markdown code block identifiers"""
    _, ext = os.path.splitext(path)
    return c.LANGUAGE_MAP.get(ext.lower(), '')

def generate_output_string(base_dir, project_config, use_wrapper, copy_merged_prompt):
    """
    Concatenates selected files into a single machine-parseable string
    Returns the final string and a status message
    """
    if not project_config.selected_files:
        return None, "No files selected to copy"

    final_ordered_list = [f['path'] for f in project_config.selected_files]

    output_blocks = []
    skipped_files = []

    # Use fragments to build markers to avoid triggering regex when CodeMerger bundles itself
    PREFIX = "--- "
    FILE_LABEL = "File: "
    EOF_LABEL = "End of file"

    for path in final_ordered_list:
        full_path = os.path.join(base_dir, path)
        if not os.path.isfile(full_path):
            skipped_files.append(path)
            continue
        with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as code_file:
            content = code_file.read()

        language = get_language_from_path(path)

        # Build block using concatenation
        block_header = f"{PREFIX}{FILE_LABEL}`{path}` ---"
        block_footer = f"{PREFIX}{EOF_LABEL} ---"

        output_blocks.append(f"{block_header}\n\n```{language}\n{content}\n```\n\n{block_footer}")

    merged_code = '\n\n'.join(output_blocks)

    if use_wrapper:
        project_title = project_config.project_name

        # Defensive coercion ensures fields corrupted by trailing commas are handled correctly
        intro_text = project_config.intro_text
        if isinstance(intro_text, (list, tuple)):
            intro_text = "\n".join(intro_text)

        outro_text = project_config.outro_text
        if isinstance(outro_text, (list, tuple)):
            outro_text = "\n".join(outro_text)

        formatting_instruction = """**CRITICAL INSTRUCTIONS FOR CODE GENERATION - READ CAREFULLY:**

1. **MANDATORY TAGGING & CLOSING POLICY:**
   Every section of your response (Answers, Intro, Changes, Delete, Verification) MUST be explicitly wrapped in tags.
   **CRITICAL:** Every opening tag MUST have an identical closing tag.

   Format: `<INTRO>[content]</INTRO>`

2. **INTRO, CHANGES & ANSWERS (PRE-CODE):**
   Immediately before the code blocks, provide these sections in this order:
   - **<INTRO>**: Use this to provide a technical implementation plan or architectural summary.
   - **<CHANGES>**: List of behavioral, algorithmic, or visual changes.
   - **<ANSWERS TO DIRECT USER QUESTIONS>**: If the user asked a specific question (usually ending with a '?'), answer it here. If there is no question mark in the prompt, there is no question. In that case, this block MUST remain empty (use a single dash `-`). Do NOT fill it with filler text like "None" or "No questions".

3. **NO CODE TRUNCATION (STRICT REQUIREMENT):**
   - You MUST provide the **FULL, COMPLETE content** for EVERY file you modify.
   - **DO NOT** use comments like `// ... rest of code`, `/* unchanged */`, or `[previous logic here]`.
   - ZERO OMISSION POLICY: Every single line, comment, and whitespace character not explicitly targeted for change MUST be mirrored exactly from the source. I am using a diff-tool to verify; any missing existing code is a failure. Byte-for-byte mirroring of unchanged lines is MANDATORY.

4. **FUNCTIONAL PRESERVATION:**
   - Do not remove or break any existing functionality.
   - NO SILENT REFACTORING: Do not "improve," "clean up," or "simplify" any code that is not directly related to the requested change. Leave unrelated logic and comments untouched.

5. **STRICT CHANGE DETECTION & OUTPUT MINIMIZATION:**
   - ONLY output files that have actually been modified.
   - If a file's final code is **byte-for-byte identical** to the original input provided in this prompt, **DO NOT** include it in your output.
   - You may list names of unchanged files at the end of your response, but do not wrap them in code blocks.

6. **MANDATORY OUTPUT FORMAT (PARSER COMPATIBILITY):**
   - Every modified file MUST be wrapped exactly like this template, including the trailing marker:

--- File: `path/to/file.ext` ---

```[language_id]
[full code here]
```
--- End of file ---

   - **CRITICAL:** The `--- End of file ---` marker is a machine-parseable sentinel. It MUST be present after every file block.

7. **DELETE & VERIFICATION (POST-CODE):**
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

==========

You MUST format your EXACT output using this skeleton. Do not deviate from this structure:

<INTRO>
(Implementation plan)
</INTRO>

<CHANGES>
(List of changes)
</CHANGES>

<ANSWERS TO DIRECT USER QUESTIONS>
(Answer any direct questions here, otherwise `-`)
</ANSWERS TO DIRECT USER QUESTIONS>

--- File: `path/to/file.ext` ---
```language
(Full unabridged file code)
```
--- End of file ---

<DELETED FILES>
(Files to delete, or `-`)
</DELETED FILES>

<VERIFICATION>
(Testing steps)
</VERIFICATION>
"""

        automation_warning = "CRITICAL: I am using an automated parser. You MUST use the exact XML tags and --- File: --- wrappers shown in the template. If you use `// ...` or `[rest of code]`, the parser will crash and your response will be useless. You must mirror every single line of the file, even unchanged ones."

        if outro_text:
            final_outro = f"{formatting_instruction}\n\n{outro_text}\n\n{automation_warning}"
        else:
            final_outro = f"{formatting_instruction}\n\n{automation_warning}"

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
    """Summarizes total tokens for the current selection set"""
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
            continue

    full_text = "\n".join(all_content)
    return get_token_count_for_text(full_text)