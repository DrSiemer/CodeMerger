import os
import re

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
        with open(path, 'w', encoding='utf-8') as f:
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
    """Cleans up whitespace and line endings"""
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]

    _, extension = os.path.splitext(path)
    if extension.lower() == '.md':
        return '\n'.join(lines)

    collapsed_lines = []
    last_line_was_empty = False
    for line in lines:
        is_empty = not line
        if is_empty and last_line_was_empty:
            continue
        collapsed_lines.append(line)
        last_line_was_empty = is_empty
    return '\n'.join(collapsed_lines)

def execute_plan(base_dir, updates, creations, deletions=None):
    """Writes the planned changes to the filesystem and deletes files marked for removal"""
    try:
        # Create new files
        for rel_path, content in creations.items():
            apply_single_file(base_dir, rel_path, content)

        # Update existing files
        for rel_path, content in updates.items():
            apply_single_file(base_dir, rel_path, content)

        # Handle Deletions
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

def parse_and_plan_changes(base_dir, markdown_text):
    """
    Parses markdown using custom file wrappers, plans changes, and returns
    a dictionary describing the plan. This does NOT write any files.
    """
    # Define markers using concatenation to prevent self-detection
    PREFIX = "--- "
    FILE_LABEL = "File: "
    EOF_LABEL = "End of file"
    EOF_MARKER = PREFIX + EOF_LABEL + " ---"

    # Verify marker symmetry via anchored line-start counts
    start_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(FILE_LABEL), markdown_text, re.MULTILINE))
    end_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(EOF_LABEL), markdown_text, re.MULTILINE))

    if start_count != end_count:
        return {
            'status': 'ERROR',
            'message': f"Format Error: Marker mismatch detected.\nFound {start_count} start markers but {end_count} end markers.",
            'hint': "Please ask the AI to correct its output format."
        }

    # Identify all blocks chronologically
    all_blocks = []

    # Identify tagged sections
    tags = ["ANSWERS TO DIRECT USER QUESTIONS", "INTRO", "CHANGES", "DELETED FILES", "VERIFICATION"]
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

    # Extract proposed deletions from the tag content
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

    # Identify file blocks
    file_block_regex = re.compile(
        r'^' + re.escape(PREFIX) + r'File: [`\'](?P<path>[^`\n]+)[`\'] ---\s+'   # Header
        r'```[^\n]*\s+'                                                          # Opening Backticks
        r'(?P<content>(?:(?!\n' + re.escape(EOF_MARKER) + r').)*?)'              # Content (Negative Lookahead)
        r'\s+```\s+'                                                             # Closing Backticks
        r'^' + re.escape(EOF_MARKER),                                            # Footer
        re.DOTALL | re.MULTILINE
    )

    for match in file_block_regex.finditer(markdown_text):
        all_blocks.append({
            'type': 'file',
            'path': match.group('path').strip().replace('\\', '/'),
            'span': match.span(),
            'content': match.group('content').strip() # Content is cleaned of wrapper whitespace
        })

    # Sort blocks by starting position to identify chronological order
    all_blocks.sort(key=lambda x: x['span'][0])

    # Map orphans (unformatted gaps between valid blocks)
    ordered_segments = []
    last_end = 0

    for block in all_blocks:
        # Check for gap before this block
        gap_text = markdown_text[last_end:block['span'][0]].strip()
        if gap_text:
            ordered_segments.append({
                'type': 'orphan',
                'content': gap_text
            })

        # Add metadata for the block itself
        if block['type'] == 'tag':
            ordered_segments.append({
                'type': 'tag',
                'tag': block['tag'],
                'content': block['content']
            })
        else:
            ordered_segments.append({'type': 'file_placeholder'})

        last_end = block['span'][1]

    # Check for trailing orphan commentary
    final_gap = markdown_text[last_end:].strip()
    if final_gap:
        ordered_segments.append({
            'type': 'orphan',
            'content': final_gap
        })

    # Validation and planning for file changes
    files_to_update = {}
    files_to_create = {}
    invalid_chars_pattern = r'[<>:"|?*]'
    base_dir_abs = os.path.abspath(base_dir)

    # Validate Proposed Deletions (Critical Security Step)
    for rel_path in deletions_proposed:
        if re.search(invalid_chars_pattern, rel_path):
            return {
                'status': 'ERROR',
                'message': f"Error: The deletion path '{rel_path}' contains invalid characters."
            }

        try:
            full_path = os.path.abspath(os.path.join(base_dir_abs, rel_path))
            if os.path.commonpath([base_dir_abs, full_path]) != base_dir_abs:
                return {
                    'status': 'ERROR',
                    'message': f"Error: Deletion path '{rel_path}' attempts to access a location outside the project directory."
                }
        except (ValueError, Exception):
            return {
                'status': 'ERROR',
                'message': f"Error: Deletion path '{rel_path}' attempts to access a location outside the project directory."
            }

    # Validate and Plan File Blocks (Updates/Creations)
    file_blocks = [b for b in all_blocks if b['type'] == 'file']
    for b in file_blocks:
        rel_path = b['path']
        content = b['content']

        if re.search(invalid_chars_pattern, rel_path):
            return {
                'status': 'ERROR',
                'message': f"Error: The file path '{rel_path}' contains invalid characters."
            }

        try:
            full_path = os.path.abspath(os.path.join(base_dir_abs, rel_path))
            if os.path.commonpath([base_dir_abs, full_path]) != base_dir_abs:
                return {
                    'status': 'ERROR',
                    'message': f"Error: Path '{rel_path}' attempts to access a location outside the project directory."
                }
        except (ValueError, Exception):
            return {
                'status': 'ERROR',
                'message': f"Error: Path '{rel_path}' attempts to access a location outside the project directory."
            }

        if os.path.isfile(full_path):
            files_to_update[rel_path] = content
        elif os.path.isdir(full_path):
            return {
                'status': 'ERROR',
                'message': f"Error: The path '{rel_path}' points to a directory, not a file."
            }
        else:
            files_to_create[rel_path] = content

    # Helper to extract flat tag content for compatibility
    def get_tag_content(tag_name):
        for s in ordered_segments:
            if s.get('tag') == tag_name:
                return s['content']
        return ""

    result = {
        'updates': files_to_update,
        'creations': files_to_create,
        'deletions_proposed': deletions_proposed,
        'answers': get_tag_content("ANSWERS TO DIRECT USER QUESTIONS"),
        'intro': get_tag_content("INTRO"),
        'changes': get_tag_content("CHANGES"),
        'delete': get_tag_content("DELETED FILES"),
        'verification': get_tag_content("VERIFICATION"),
        'ordered_segments': ordered_segments,
        'has_any_tags': any(b['type'] == 'tag' for b in all_blocks)
    }

    if not all_blocks:
        result['status'] = 'UNFORMATTED'
        result['unformatted'] = markdown_text.strip()
    elif files_to_create or deletions_proposed:
        result['status'] = 'CONFIRM_CREATION'
    else:
        result['status'] = 'SUCCESS'

    return result