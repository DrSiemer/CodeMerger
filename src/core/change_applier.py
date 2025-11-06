import os
import re

def _sanitize_content(path, content):
    """Cleans up whitespace and line endings"""
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]

    _, extension = os.path.splitext(path)
    if extension.lower() == '.md':
        # For markdown, only normalize line endings and trailing whitespace
        return '\n'.join(lines)

    # For all other code files, also collapse multiple consecutive empty lines
    collapsed_lines = []
    last_line_was_empty = False
    for line in lines:
        is_empty = not line
        if is_empty and last_line_was_empty:
            continue
        collapsed_lines.append(line)
        last_line_was_empty = is_empty
    return '\n'.join(collapsed_lines)

def execute_plan(updates, creations):
    """Writes the planned changes to the filesystem"""
    try:
        # Create new files
        for path, content in creations.items():
            dir_path = os.path.dirname(path)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            sanitized_content = _sanitize_content(path, content)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(sanitized_content)

        # Update existing files
        for path, content in updates.items():
            sanitized_content = _sanitize_content(path, content)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(sanitized_content)

    except IOError as e:
        return False, f"Error writing to file: {e}"

    total_files = len(updates) + len(creations)
    return True, f"Successfully applied changes to {total_files} file(s)."

def parse_and_plan_changes(base_dir, markdown_text):
    """
    Parses markdown using custom file wrappers, plans changes, and returns
    a dictionary describing the plan. This does NOT write any files.
    """
    markdown_text = re.sub(r'```(--- End of file ---)', r'```\n\n\1', markdown_text)

    file_blocks = re.findall(
        r'--- File: `([^\n`]+)` ---\s*\n```[^\n]*\n(.*?)\n```\s*\n--- End of file ---',
        markdown_text,
        re.DOTALL
    )

    if not file_blocks:
        return {'status': 'ERROR', 'message': "Error: No valid file blocks found. Make sure each file is wrapped with '--- File: `path` ---' and '--- End of file ---'."}

    files_to_update = {}
    files_to_create = {}

    for relative_path, content in file_blocks:
        # Normalize path separators
        relative_path = relative_path.strip().replace('\\', '/')
        full_path = os.path.normpath(os.path.join(base_dir, relative_path))

        # Security check: ensure the path is within the project directory
        if not full_path.startswith(os.path.normpath(base_dir)):
            return {'status': 'ERROR', 'message': f"Error: Path '{relative_path}' attempts to access a location outside the project directory."}

        if os.path.isfile(full_path):
            files_to_update[full_path] = content
        elif os.path.isdir(full_path):
            return {'status': 'ERROR', 'message': f"Error: The path '{relative_path}' points to a directory, not a file."}
        else:
            files_to_create[full_path] = content

    if not files_to_update and not files_to_create:
        # This case should be rare if file_blocks is not empty, but it's a good safeguard
        return {'status': 'ERROR', 'message': "Error: No valid files to update or create were found."}

    if files_to_create:
        return {
            'status': 'CONFIRM_CREATION',
            'updates': files_to_update,
            'creations': files_to_create
        }
    else:
        return {
            'status': 'SUCCESS',
            'updates': files_to_update,
            'creations': {}
        }