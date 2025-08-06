import os
import json
import tiktoken

def generate_output_string(base_dir, use_wrapper):
    """
    Core logic for merging files
    Reads the .allcode file, processes files, and returns the final string and a status message
    """
    config_path = os.path.join(base_dir, '.allcode')
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"No .allcode file found in {base_dir}")

    with open(config_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    final_ordered_list = data.get('selected_files', [])
    if not final_ordered_list:
        return None, "No files selected to copy"

    output_blocks = []
    skipped_files = []
    for path in final_ordered_list:
        full_path = os.path.join(base_dir, path)
        if not os.path.isfile(full_path):
            skipped_files.append(path)
            continue
        with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as code_file:
            content = code_file.read()
        output_blocks.append(f'--- {path} ---\n```\n{content}\n```')

    merged_code = '\n\n\n'.join(output_blocks)

    if use_wrapper:
        intro_text = data.get('intro_text', '').strip()
        outro_text = data.get('outro_text', '').strip()
        merged_code_with_header = f"Here's all the relevant code:\n\n{merged_code}"

        final_parts = []
        if intro_text:
            final_parts.append(intro_text)
        final_parts.append(merged_code_with_header)
        if outro_text:
            final_parts.append(outro_text)

        final_content = '\n\n\n'.join(final_parts)
        status_message = "Wrapped code copied to clipboard"
    else:
        final_content = f"Here's all the most recent code:\n\n{merged_code}"
        status_message = "Merged code copied to clipboard"

    if skipped_files:
        status_message += f". Skipped {len(skipped_files)} missing file(s)"

    return final_content, status_message

def recalculate_token_count(base_dir, selected_files):
    """
    Reads selected files, concatenates their content, and counts the tokens
    """
    if not selected_files:
        return 0

    all_content = []
    for rel_path in selected_files:
        full_path = os.path.join(base_dir, rel_path)
        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                all_content.append(f.read())
        except FileNotFoundError:
            # File might have been deleted, just skip it
            continue

    full_text = "\n".join(all_content)

    try:
        # cl100k_base is the encoding for gpt-4, gpt-3.5-turbo, and text-embedding-ada-002
        encoding = tiktoken.get_encoding("cl100k_base")
        # Using disallowed_special=() to count all tokens without errors
        total_tokens = len(encoding.encode(full_text, disallowed_special=()))
        return total_tokens
    except Exception:
        # If tiktoken fails for any reason, return -1 to indicate an error
        return -1