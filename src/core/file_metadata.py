import os
from .utils import get_token_count_for_text, get_file_hash

def clean_and_update_metadata(config_instance, profile_data):
    """
    Verifies existence of selected files and recalculates metadata.
    Returns (files_were_cleaned, profile_was_updated).
    """
    profile_was_updated = False
    original_selection = profile_data.get('selected_files', [])
    is_new_format = original_selection and isinstance(original_selection[0], dict) and 'path' in original_selection[0]

    cleaned_selection = []
    if not is_new_format:
        if original_selection:
            profile_was_updated = True
        for f_path in original_selection:
            norm_path = f_path.replace('\\', '/')
            full_path = os.path.join(config_instance.base_dir, norm_path)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    mtime = os.path.getmtime(full_path)
                    file_hash = get_file_hash(full_path)
                    tokens = get_token_count_for_text(content)
                    lines = content.count('\n') + 1
                    cleaned_selection.append({
                        'path': norm_path, 'mtime': mtime, 'hash': file_hash,
                        'tokens': tokens, 'lines': lines
                    })
                except OSError:
                    continue
    else:
        for f_info in original_selection:
            rel_path = f_info['path'].replace('\\', '/')
            full_path = os.path.join(config_instance.base_dir, rel_path)
            if os.path.isfile(full_path):
                f_info['path'] = rel_path
                if any(k not in f_info for k in ['tokens', 'mtime', 'hash', 'lines']):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        f_info['tokens'] = get_token_count_for_text(content)
                        f_info['lines'] = content.count('\n') + 1
                        f_info['mtime'] = os.path.getmtime(full_path)
                        f_info['hash'] = get_file_hash(full_path)
                        profile_was_updated = True
                    except OSError:
                        pass
                cleaned_selection.append(f_info)

    profile_data['selected_files'] = cleaned_selection
    files_were_cleaned = len(cleaned_selection) < len(original_selection)

    if files_were_cleaned or profile_was_updated:
        profile_data['total_tokens'] = sum(f.get('tokens', 0) for f in cleaned_selection)

    return files_were_cleaned, profile_was_updated