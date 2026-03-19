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

def execute_plan(base_dir, updates, creations):
    """Writes the planned changes to the filesystem"""
    try:
        # Create new files
        for rel_path, content in creations.items():
            path = os.path.join(base_dir, rel_path)
            dir_path = os.path.dirname(path)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            sanitized_content = _sanitize_content(path, content)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(sanitized_content)

        # Update existing files
        for rel_path, content in updates.items():
            path = os.path.join(base_dir, rel_path)
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
    answers_match = re.search(r'<<ANSWERS>>(.*?)<<ANSWERS>>', markdown_text, re.DOTALL)
    answers_text = answers_match.group(1).strip() if answers_match else ""

    intro_match = re.search(r'<<INTRO>>(.*?)<<INTRO>>', markdown_text, re.DOTALL)
    intro_text = intro_match.group(1).strip() if intro_match else ""

    changes_match = re.search(r'<<CHANGES>>(.*?)<<CHANGES>>', markdown_text, re.DOTALL)
    changes_text = changes_match.group(1).strip() if changes_match else ""

    delete_match = re.search(r'<<DELETE>>(.*?)<<DELETE>>', markdown_text, re.DOTALL)
    delete_text = delete_match.group(1).strip() if delete_match else ""

    verification_match = re.search(r'<<VERIFICATION>>(.*?)<<VERIFICATION>>', markdown_text, re.DOTALL)
    verification_text = verification_match.group(1).strip() if verification_match else ""

    # --- Pre-processing for common LLM formatting errors ---

    # Ensure there is a newline between the header and the code block
    markdown_text = re.sub(r'(--- File: `.+?` ---\s*)\`\`\`', r'\1\n```', markdown_text)

    lines = markdown_text.split('\n')
    processed_lines = []
    for line in lines:
        stripped_line = line.strip()
        # Find ``` that is not at the start of the line and has content before it.
        if stripped_line.endswith('```') and stripped_line != '```':
            pos = line.rfind('```')
            processed_lines.append(line[:pos])
            processed_lines.append(line[pos:])
        else:
            processed_lines.append(line)
    markdown_text = '\n'.join(processed_lines)

    # Ensure there is a newline between the closing backticks and the footer
    markdown_text = re.sub(r'```(--- End of file ---)', r'```\n\n\1', markdown_text)

    # Robust regex: handles \r\n, varying whitespace, and avoids being tripped up by content
    # We look for the File header, the opening backticks, the content, the closing backticks, and the footer.
    file_blocks = re.findall(
        r'--- File: `([^\n`]+)` ---\s*[\r\n]+```[^\n]*[\r\n]+(.*?)\n```\s*[\r\n]+--- End of file ---',
        markdown_text,
        re.DOTALL
    )

    if not file_blocks:
        return {'status': 'ERROR', 'message': "No valid file blocks were found. Make sure each file is wrapped with '--- File: `path` ---' and '--- End of file ---'."}

    files_to_update = {}
    files_to_create = {}

    invalid_chars_pattern = r'[<>:"|?*]'

    for relative_path, content in file_blocks:
        # Normalize path separators
        relative_path = relative_path.strip().replace('\\', '/')
        full_path = os.path.normpath(os.path.join(base_dir, relative_path))

        # Validation for illegal characters in the path
        if re.search(invalid_chars_pattern, relative_path):
            return {'status': 'ERROR', 'message': f"Error: The file path '{relative_path}' contains invalid characters."}

        # Validation for path component length
        path_components = relative_path.split('/')
        for component in path_components:
            if len(component) > 260:
                return {'status': 'ERROR', 'message': f"Error: A filename or directory in the path '{relative_path}' exceeds the 260-character limit."}

        # Security check: ensure the path is within the project directory
        if not full_path.startswith(os.path.normpath(base_dir)):
            return {'status': 'ERROR', 'message': f"Error: Path '{relative_path}' attempts to access a location outside the project directory."}

        if os.path.isfile(full_path):
            files_to_update[relative_path] = content
        elif os.path.isdir(full_path):
            return {'status': 'ERROR', 'message': f"Error: The path '{relative_path}' points to a directory, not a file."}
        else:
            files_to_create[relative_path] = content

    if not files_to_update and not files_to_create:
        return {'status': 'ERROR', 'message': "Error: No valid files to update or create were found."}

    if files_to_create:
        return {
            'status': 'CONFIRM_CREATION',
            'updates': files_to_update,
            'creations': files_to_create,
            'answers': answers_text,
            'intro': intro_text,
            'changes': changes_text,
            'delete': delete_text,
            'verification': verification_text
        }
    else:
        return {
            'status': 'SUCCESS',
            'updates': files_to_update,
            'creations': {},
            'answers': answers_text,
            'intro': intro_text,
            'changes': changes_text,
            'delete': delete_text,
            'verification': verification_text
        }