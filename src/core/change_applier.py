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
    # Define markers using concatenation to prevent self-detection
    PREFIX = "--- "
    FILE_LABEL = "File: "
    EOF_LABEL = "End of file"
    EOF_MARKER = PREFIX + EOF_LABEL + " ---"

    def get_section(tag, text):
        match = re.search(rf'<{tag}>(.*?)</{tag}>', text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            content_lower = content.lower().strip('.')
            if content == "-" or content_lower in ["none", "n/a", "no files to delete", "no changes", "no conceptual questions were asked in the prompt", "no conceptual questions were asked", "no direct questions were asked", "no questions"]:
                return ""
            return content
        return ""

    # Verify marker symmetry via anchored line-start counts
    start_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(FILE_LABEL), markdown_text, re.MULTILINE))
    end_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(EOF_LABEL), markdown_text, re.MULTILINE))

    if start_count != end_count:
        return {
            'status': 'ERROR',
            'message': f"Format Error: Marker mismatch detected.\nFound {start_count} start markers but {end_count} end markers.",
            'hint': "Please ask the AI to correct its output format."
        }

    answers_text = get_section("ANSWERS TO DIRECT USER QUESTIONS", markdown_text)
    intro_text = get_section("INTRO", markdown_text)
    changes_text = get_section("CHANGES", markdown_text)
    delete_text = get_section("DELETED FILES", markdown_text)
    verification_text = get_section("VERIFICATION", markdown_text)

    # Flag to determine if the AI followed formatting for commentary at all
    has_any_tags = any([answers_text, intro_text, changes_text, delete_text, verification_text])

    # --- Orphan / Unformatted Text Detection ---
    # We define unformatted text as anything that is NOT inside a valid tag
    # and NOT inside a valid File block.
    orphan_detect = markdown_text

    # 1. Strip all valid tagged blocks
    orphan_detect = re.sub(r'<(ANSWERS TO DIRECT USER QUESTIONS|INTRO|CHANGES|DELETED FILES|VERIFICATION)>.*?</\1>', '', orphan_detect, flags=re.DOTALL | re.IGNORECASE)

    # 2. Strip all valid File blocks
    file_block_strip_pattern = re.escape(PREFIX) + r'File: `[^\n`]+` ---\s*[\r\n]+```[^\n]*[\r\n]+.*?\n```\s*[\r\n]+' + re.escape(EOF_MARKER)
    orphan_detect = re.sub(file_block_strip_pattern, '', orphan_detect, flags=re.DOTALL)

    # 3. Cleanup whitespace: Collapse multiple newlines (3+) left behind by stripped blocks into just two
    unformatted_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', orphan_detect).strip()

    # --- Pre-processing for common LLM formatting errors ---

    # Ensure there is a newline between the header and the code block
    markdown_text_processed = re.sub(r'(' + re.escape(PREFIX) + r'File: `.+?` ---\s*)\`\`\`', r'\1\n```', markdown_text)

    lines = markdown_text_processed.split('\n')
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
    markdown_text_processed = '\n'.join(processed_lines)

    # Ensure there is a newline between the closing backticks and the footer
    markdown_text_processed = re.sub(r'```(' + re.escape(EOF_MARKER) + r')', r'```\n\n\1', markdown_text_processed)

    # Robust regex using fragments
    file_block_regex = re.escape(PREFIX) + r'File: `([^\n`]+)` ---\s*[\r\n]+```[^\n]*[\r\n]+(.*?)\n```\s*[\r\n]+' + re.escape(EOF_MARKER)
    file_blocks = re.findall(file_block_regex, markdown_text_processed, re.DOTALL)

    if not file_blocks:
        # If NO file blocks are found, return the full original text as unformatted
        return {
            'status': 'UNFORMATTED',
            'message': "No valid file blocks were found.",
            'unformatted': markdown_text.strip(),
            'answers': answers_text,
            'intro': intro_text,
            'changes': changes_text,
            'delete': delete_text,
            'verification': verification_text,
            'has_any_tags': has_any_tags
        }

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

    result = {
        'updates': files_to_update,
        'creations': files_to_create,
        'answers': answers_text,
        'intro': intro_text,
        'changes': changes_text,
        'delete': delete_text,
        'verification': verification_text,
        'unformatted': unformatted_text,
        'has_any_tags': has_any_tags
    }

    if files_to_create:
        result['status'] = 'CONFIRM_CREATION'
    else:
        result['status'] = 'SUCCESS'

    return result