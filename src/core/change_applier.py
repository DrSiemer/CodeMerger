import os
import re

def preprocess_content(content):
    """
    Preprocesses the markdown content to handle specific formatting issues.
    - Adds a linebreak before closing triple backticks if they are at the end of a line of code.
    """
    lines = content.split('\n')
    processed_lines = []
    for line in lines:
        # Add a newline before closing backticks if they are not on their own line
        if line.strip().endswith('```') and len(line.strip()) > 3:
            processed_lines.append(line.replace('```', ''))
            processed_lines.append('```')
        else:
            processed_lines.append(line)
    return '\n'.join(processed_lines)

def _sanitize_content(path, content):
    """Cleans up whitespace in non-markdown code files."""
    _, extension = os.path.splitext(path)
    if extension.lower() == '.md':
        return content  # Don't sanitize markdown

    # Sanitize each line: remove trailing whitespace
    lines = [line.rstrip() for line in content.splitlines()]

    # Collapse multiple consecutive empty lines into a single one
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
    """Writes the planned changes to the filesystem."""
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
    Parses markdown, plans changes, and returns a dictionary describing the plan.
    This does NOT write any files.
    """
    markdown_text = preprocess_content(markdown_text)

    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', markdown_text, re.DOTALL)
    text_segments = re.split(r'```(?:\w+)?\n(?:.*?)\n```', markdown_text, flags=re.DOTALL)

    if not code_blocks:
        return {'status': 'ERROR', 'message': "Error: No code blocks found in the input text."}

    if len(text_segments) <= len(code_blocks):
        return {'status': 'ERROR', 'message': "Error: Could not properly segment the input text. Make sure each code block is preceded by a file path."}

    files_to_update = {}
    files_to_create = {}

    for i, code_block in enumerate(code_blocks):
        preceding_text = text_segments[i]
        relative_path = None
        content_to_write = code_block
        path_found_outside_block = False

        # Step 1: Prioritize finding a path in a markdown header (e.g., ## `path`)
        header_lines = [line.strip() for line in preceding_text.strip().split('\n') if line.strip().startswith('##')]
        if header_lines:
            last_header = header_lines[-1]
            first_space_index = last_header.find(' ')
            if first_space_index != -1:
                path_from_header = last_header[first_space_index + 1:].strip().strip('`\'"')
                if path_from_header:
                    relative_path = path_from_header.replace('\\', '/')
                    path_found_outside_block = True

        lines = code_block.split('\n')
        should_strip_first_line = False

        # Step 2: Only if no path was found outside, inspect the first line of the code block.
        if not path_found_outside_block and lines:
            first_line_text = lines[0]
            stripped_first_line = first_line_text.strip()

            path_candidate = None
            match = re.search(r'([\w.-]+(?:/|\\)[\w./\\-]*[\w-]+|[\w-]+\.[\w-]+)', stripped_first_line)
            if match:
                path_candidate = match.group(0).strip('`\'":*,#() ').replace('\\', '/')

            if path_candidate:
                is_markdown = path_candidate.lower().endswith('.md')

                # Apply special rule for markdown files starting with '#'
                if is_markdown and stripped_first_line.startswith('#'):
                    if len(lines) > 1:
                        if lines[1].strip().startswith('# '):
                            should_strip_first_line = True
                            relative_path = path_candidate
                else:
                    # For non-markdown files, or markdown not starting with '#', strip if a path was found.
                    should_strip_first_line = True
                    relative_path = path_candidate

        if should_strip_first_line:
            content_to_write = '\n'.join(lines[1:])

        if not relative_path:
            return {'status': 'ERROR', 'message': f"Error: Could not determine a file path for code block {i + 1}."}

        full_path = os.path.normpath(os.path.join(base_dir, relative_path))

        if not full_path.startswith(os.path.normpath(base_dir)):
            return {'status': 'ERROR', 'message': f"Error: Path '{relative_path}' attempts to access a location outside the project directory."}

        if os.path.isfile(full_path):
            files_to_update[full_path] = content_to_write
        elif os.path.isdir(full_path):
            return {'status': 'ERROR', 'message': f"Error: The path '{relative_path}' points to a directory, not a file."}
        else:
            files_to_create[full_path] = content_to_write

    if not files_to_update and not files_to_create:
        return {'status': 'ERROR', 'message': "Error: No valid files to update or create were found."}

    if files_to_create:
        return {
            'status': 'CONFIRM_CREATION',
            'updates': files_to_update,
            'creations': creations
        }
    else:
        return {
            'status': 'SUCCESS',
            'updates': files_to_update,
            'creations': {}
        }