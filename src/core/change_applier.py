import os
import re
from .replacer import apply_fuzzy_patch

def get_current_file_content(base_dir, rel_path):
    """Reads current file content from disk for backup/undo purposes."""
    full_path = os.path.join(base_dir, rel_path)
    if os.path.isfile(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except OSError:
            return None
    return None

def apply_single_file(base_dir, rel_path, content):
    """Writes a single file to disk, creating directories if needed."""
    try:
        path = os.path.join(base_dir, rel_path)
        dir_path = os.path.dirname(path)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        sanitized_content = _sanitize_content(path, content)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(sanitized_content)
        return True, ""
    except IOError as e:
        return False, str(e)

def delete_single_file(base_dir, rel_path):
    """Removes a single file from disk."""
    try:
        path = os.path.join(base_dir, rel_path)
        if os.path.isfile(path):
            os.remove(path)
        return True, ""
    except IOError as e:
        return False, str(e)

def _sanitize_content(path, content):
    """
    Normalizes content for writing and comparison.
    Aggressively stripping trailing whitespace ensures we don't get phantom diffs
    where invisible space differences from LLM outputs trigger false file changes.
    """
    if not content:
        return ""

    # Normalizes line endings to LF to adhere to PyWebView and JS standards
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]

    _, extension = os.path.splitext(path)
    # Markdown files often use double-spacing intentionally; we preserve them there
    if extension.lower() == '.md':
        return '\n'.join(lines).strip()

    collapsed_lines = []
    last_line_was_empty = False
    for line in lines:
        is_empty = not line
        if is_empty and last_line_was_empty:
            continue
        collapsed_lines.append(line)
        last_line_was_empty = is_empty

    return '\n'.join(collapsed_lines).strip()

def execute_plan(base_dir, updates, creations, deletions=None):
    """Writes the planned changes to the filesystem and deletes files marked for removal"""
    try:
        for rel_path, content in creations.items():
            apply_single_file(base_dir, rel_path, content)

        for rel_path, content in updates.items():
            apply_single_file(base_dir, rel_path, content)

        if deletions:
            for rel_path in deletions:
                delete_single_file(base_dir, rel_path)

    except IOError as e:
        return False, f"Error writing to file: {e}"

    total_added = len(updates) + len(creations)
    total_deleted = len(deletions) if deletions else 0
    msg = f"Successfully updated {total_added} file(s)"
    if total_deleted > 0:
        msg += f" and deleted {total_deleted} file(s)"

    return True, msg + "."

def process_surgical_blocks(current_content, llm_content):
    """Parses ORIGINAL/UPDATED blocks and applies them via the Fuzzy Engine."""
    patch_regex = re.compile(
        r'<<<<<<< ORIGINAL[ \t]*\n(.*?)\n=======[ \t]*\n?(.*?)\n?>>>>>>> UPDATED',
        re.DOTALL
    )

    # Normalize internal line endings for processing
    llm_content = llm_content.replace('\r\n', '\n').replace('\r', '\n')

    matches = list(patch_regex.finditer(llm_content))
    if not matches:
        return llm_content # Fallback to Full-File if no blocks found

    # Ensure the content we are patching is normalized to LF
    working_content = current_content.replace('\r\n', '\n').replace('\r', '\n')

    for match in matches:
        old_code, new_code = match.groups()
        # ValueError raised here will bubble up to parse_and_plan_changes
        working_content, _ = apply_fuzzy_patch(working_content, old_code, new_code)

    return working_content

def parse_and_plan_changes(base_dir, markdown_text):
    """
    Parses markdown using custom file wrappers, plans changes, and returns
    a dictionary describing the plan. This does NOT write any files.
    """
    # Normalize input line endings immediately to simplify regex matching
    markdown_text = markdown_text.replace('\r\n', '\n').replace('\r', '\n')

    # Define markers using concatenation to prevent self-detection
    PREFIX = "--- "
    FILE_LABEL = "File: "
    EOF_LABEL = "End of file"
    EOF_MARKER = PREFIX + EOF_LABEL + " ---"

    start_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(FILE_LABEL), markdown_text, re.MULTILINE))
    end_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(EOF_LABEL), markdown_text, re.MULTILINE))

    if start_count != end_count:
        return {
            'status': 'ERROR',
            'message': f"Format Error: Marker mismatch detected.\nFound {start_count} start markers but {end_count} end markers.",
            'hint': "Please ask the AI to correct its output format."
        }

    all_blocks = []

    tags = ["ANSWERS TO DIRECT USER QUESTIONS", "INTRO", "CHANGES", "DELETED FILES", "VERIFICATION", "UNCHANGED"]
    for tag in tags:
        # Accept truncated closing tag as well
        if tag == "ANSWERS TO DIRECT USER QUESTIONS":
            pattern = re.compile(rf'<{tag}>(.*?)</(?:ANSWERS TO DIRECT USER QUESTIONS|ANSWERS)>', re.DOTALL | re.IGNORECASE)
        else:
            pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.DOTALL | re.IGNORECASE)

        for match in pattern.finditer(markdown_text):
            content = match.group(1).strip()
            content_lower = content.lower().strip('.')

            # Filter out generic AI placeholder phrases
            filler_phrases = [
                "none", "n/a", "no files to delete", "no changes",
                "no conceptual questions were asked in the prompt",
                "no conceptual questions were asked",
                "no direct questions were asked", "no questions"
            ]

            if content == "-" or content_lower in filler_phrases:
                content = ""

            all_blocks.append({
                'type': 'tag',
                'tag': tag,
                'span': match.span(),
                'content': content
            })

    deletions_proposed = []
    delete_section_content = ""
    for b in all_blocks:
        if b['tag'] == "DELETED FILES":
            delete_section_content = b['content']
            break

    if delete_section_content:
        # Match lines like "DELETE FILE: path/to/file.ext"
        del_matches = re.findall(r'DELETE FILE:\s*(.+)', delete_section_content, re.IGNORECASE)
        deletions_proposed = [m.strip().replace('\\', '/') for m in del_matches if m.strip()]

    file_block_regex = re.compile(
        r'^' + re.escape(PREFIX) + r'File: [`\'](?P<path>[^`\n]+)[`\'] ---\s*\n+'
        r'```[^\n]*\n'
        r'(?P<content>.*?)'
        r'\n```\s*\n'
        r'^' + re.escape(EOF_MARKER),
        re.DOTALL | re.MULTILINE
    )

    files_to_update = {}
    files_to_create = {}
    skipped_files = []

    failed_paths = []
    for match in file_block_regex.finditer(markdown_text):
        rel_path = match.group('path').strip().replace('\\', '/')
        llm_raw_content = match.group('content')

        current_disk_content = get_current_file_content(base_dir, rel_path)

        try:
            if current_disk_content and "<<<<<<< ORIGINAL" in llm_raw_content:
                # If patching fails, process_surgical_blocks raises ValueError
                final_assembled_content = process_surgical_blocks(current_disk_content, llm_raw_content)
                sanitized_new = _sanitize_content(rel_path, final_assembled_content)
            else:
                sanitized_new = _sanitize_content(rel_path, llm_raw_content)
        except ValueError as e:
            failed_paths.append((rel_path, str(e)))
            continue

        all_blocks.append({
            'type': 'file',
            'path': rel_path,
            'span': match.span(),
            'content': sanitized_new
        })

        if os.path.isfile(os.path.join(base_dir, rel_path)):
            old_raw = current_disk_content
            if old_raw is not None:
                # Sanitize the local file EXACTLY the same way as the LLM input
                sanitized_old = _sanitize_content(rel_path, old_raw)

                if sanitized_old == sanitized_new:
                    skipped_files.append(rel_path)

            files_to_update[rel_path] = sanitized_new
        else:
            files_to_create[rel_path] = sanitized_new

    # Sort blocks by starting position to identify chronological order for UI tabs
    all_blocks.sort(key=lambda x: x['span'][0])

    ordered_segments = []
    last_end = 0

    for block in all_blocks:
        gap_text = markdown_text[last_end:block['span'][0]].strip()
        if gap_text:
            ordered_segments.append({
                'type': 'orphan',
                'content': gap_text
            })

        if block['type'] == 'tag':
            ordered_segments.append({
                'type': 'tag',
                'tag': block['tag'],
                'content': block['content']
            })
        else:
            ordered_segments.append({'type': 'file_placeholder'})

        last_end = block['span'][1]

    final_gap = markdown_text[last_end:].strip()
    if final_gap:
        ordered_segments.append({
            'type': 'orphan',
            'content': final_gap
        })

    # Path validation for security
    invalid_chars_pattern = r'[<>:"|?*]'
    base_dir_abs = os.path.abspath(base_dir)

    for rel_path in deletions_proposed:
        if re.search(invalid_chars_pattern, rel_path):
            return {'status': 'ERROR', 'message': f"Error: The deletion path '{rel_path}' contains invalid characters."}
        try:
            full_path = os.path.abspath(os.path.join(base_dir_abs, rel_path))
            if os.path.commonpath([base_dir_abs, full_path]) != base_dir_abs:
                return {'status': 'ERROR', 'message': f"Error: Deletion path '{rel_path}' attempts to access a location outside the project directory."}

            # NO-OP check for deletions: if file is already gone
            if not os.path.isfile(full_path):
                skipped_files.append(rel_path)
        except (ValueError, Exception):
            return {'status': 'ERROR', 'message': f"Error: Deletion path '{rel_path}' attempts to access a location outside the project directory."}

    def get_tag_content(tag_name):
        for s in ordered_segments:
            if s.get('tag') == tag_name:
                return s['content']
        return ""

    result = {
        'updates': files_to_update,
        'creations': files_to_create,
        'deletions_proposed': deletions_proposed,
        'skipped_files': skipped_files,
        'answers': get_tag_content("ANSWERS TO DIRECT USER QUESTIONS"),
        'intro': get_tag_content("INTRO"),
        'changes': get_tag_content("CHANGES"),
        'delete': get_tag_content("DELETED FILES"),
        'verification': get_tag_content("VERIFICATION"),
        'ordered_segments': ordered_segments,
        'has_any_tags': any(b['type'] == 'tag' for b in all_blocks)
    }

    if failed_paths:
        # Construct detailed error for the UI
        err_msg = "\n".join([f"- {p}: {e}" for p, e in failed_paths])
        return {
            'status': 'ERROR',
            'error_type': 'FAST_APPLY',
            'failed_paths': [p for p, e in failed_paths],
            'message': f"Fast-Apply Error in {len(failed_paths)} file(s):\n{err_msg}",
            'hint': "The AI is hallucinating old code. Click 'Copy Correction Prompt' to send the up-to-date source back to the AI."
        }

    if not all_blocks:
        result['status'] = 'UNFORMATTED'
        result['unformatted'] = markdown_text.strip()
    elif files_to_create or deletions_proposed:
        result['status'] = 'CONFIRM_CREATION'
    else:
        result['status'] = 'SUCCESS'

    return result