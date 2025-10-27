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

def apply_changes_from_markdown(base_dir, markdown_text):
    """
    Parses markdown text, extracts file paths and code blocks,
    and applies the changes to the corresponding files in the project.

    Returns:
        (bool, str): A tuple containing a boolean indicating success
                     and a message string.
    """
    markdown_text = preprocess_content(markdown_text)

    # Regex to find all code blocks with optional language tags
    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', markdown_text, re.DOTALL)

    # Split the text by code blocks to find the preceding file paths
    # The delimiter is the full code block pattern
    text_segments = re.split(r'```(?:\w+)?\n(?:.*?)\n```', markdown_text, flags=re.DOTALL)

    if not code_blocks:
        return False, "Error: No code blocks found in the input text."

    if len(text_segments) <= len(code_blocks):
         return False, "Error: Could not properly segment the input text. Make sure each code block is preceded by a file path."

    files_to_update = {}
    for i, code_block in enumerate(code_blocks):
        preceding_text = text_segments[i]
        relative_path = None
        content_to_write = code_block

        # A more robust regex that only matches valid path characters.
        # It requires at least one path separator.
        path_regex = r'[\w./\\-]*[/\\][\w./\\-]+'

        # Primary Strategy: Find all strings that look like paths in the preceding text.
        path_candidates = re.findall(path_regex, preceding_text)
        if path_candidates:
            # Use the last candidate found, as it's closest to the code block.
            # Strip common surrounding punctuation as a final safeguard.
            last_candidate = path_candidates[-1].strip('`\'":*,.()')
            if len(last_candidate) > 0:
                relative_path = last_candidate.replace('\\', '/')

        # Fallback Strategy: If no path was found externally, check the first line inside the code block.
        if not relative_path and code_block:
            lines = code_block.split('\n')
            if lines:
                first_line = lines[0] # [FIX] Correctly get the first line string, not the whole list.
                internal_path_candidates = re.findall(path_regex, first_line)
                if internal_path_candidates:
                    last_candidate = internal_path_candidates[-1].strip('`\'":*,#()')
                    if len(last_candidate) > 0:
                        relative_path = last_candidate.replace('\\', '/')
                        # If found inside, remove the path line from the content to be written.
                        content_to_write = '\n'.join(lines[1:])

        if not relative_path:
            return False, f"Error: Could not find a file path for code block {i + 1}."

        full_path = os.path.join(base_dir, relative_path)

        if not os.path.isfile(full_path):
            return False, f"Error: The file '{relative_path}' does not exist in the project."

        files_to_update[full_path] = content_to_write

    if not files_to_update:
        return False, "Error: No valid files to update were found."

    # If all checks pass, apply the changes
    try:
        for path, content in files_to_update.items():
            _, extension = os.path.splitext(path)

            # For non-markdown files, clean up extra whitespace
            if extension.lower() != '.md':
                # Sanitize each line: remove trailing whitespace, which also turns
                # lines with only spaces/tabs into truly empty lines.
                lines = [line.rstrip() for line in content.splitlines()]

                # Now, collapse multiple consecutive empty lines into a single one
                collapsed_lines = []
                last_line_was_empty = False
                for line in lines:
                    is_empty = not line
                    if is_empty and last_line_was_empty:
                        continue  # Skip this consecutive empty line

                    collapsed_lines.append(line)
                    last_line_was_empty = is_empty

                content = '\n'.join(collapsed_lines)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    except IOError as e:
        return False, f"Error writing to file: {e}"

    return True, f"Successfully applied changes to {len(files_to_update)} file(s)."