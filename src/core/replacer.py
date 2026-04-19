import re
import logging

log = logging.getLogger("CodeMerger")

def strip_indentation(text):
    """Removes common leading whitespace from a block of text."""
    lines = text.split('\n')
    non_empty = [line for line in lines if line.strip()]
    if not non_empty: return text
    min_indent = min(len(re.match(r'^([ \t]*)', line).group(1)) for line in non_empty)
    return '\n'.join(line[min_indent:] if line.strip() else line for line in lines)

def normalize_whitespace(text):
    """Collapses all whitespace into a single space for aggressive matching."""
    return re.sub(r'\s+', ' ', text).strip()

def _clean_block(text):
    """Normalizes line endings and removes surrounding empty lines."""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Strip surrounding newlines but keep internal ones
    return text.strip('\n')

def _is_line_match(line_a, line_b, fuzzy=False):
    """Compares two lines, ignoring trailing whitespace and optionally indentation."""
    if fuzzy:
        return line_a.strip() == line_b.strip()
    return line_a.rstrip() == line_b.rstrip()

def apply_fuzzy_patch(current_content, old_code_raw, new_code_raw):
    """Attempts to replace old_code with new_code using cascading strategies."""
    old_code = _clean_block(old_code_raw)
    new_code = _clean_block(new_code_raw)

    # Pre-normalization for check
    current_normalized = current_content.replace('\r\n', '\n').replace('\r', '\n')

    if not old_code.strip():
        raise ValueError("The 'ORIGINAL' block provided by the AI is empty.")

    # Strategy 0: Already Applied
    if new_code and new_code in current_normalized:
        return current_normalized, "Already Applied"

    # Strategy 1: Exact Match
    if old_code in current_normalized:
        if current_normalized.count(old_code) > 1:
            raise ValueError("Ambiguous match: ORIGINAL code appears multiple times. Needs more context.")
        return current_normalized.replace(old_code, new_code, 1), "Exact"

    # Strategy 2: Significant Line Match (Handles blank line differences)
    content_lines = current_normalized.split('\n')
    old_lines = old_code.split('\n')

    # Filter for lines that actually contain code
    significant_old_indices = [i for i, l in enumerate(old_lines) if l.strip()]
    if not significant_old_indices:
        raise ValueError("The 'ORIGINAL' block contains no code-bearing lines.")

    best_match_start = -1
    best_match_end = -1
    match_count = 0

    # Scan the file for the sequence of significant lines
    for i in range(len(content_lines)):
        if _is_line_match(content_lines[i], old_lines[significant_old_indices[0]]):
            curr_idx = i
            matched_all = True

            for sig_idx in significant_old_indices[1:]:
                found_next = False
                for search_idx in range(curr_idx + 1, len(content_lines)):
                    if content_lines[search_idx].strip():
                        if _is_line_match(content_lines[search_idx], old_lines[sig_idx]):
                            curr_idx = search_idx
                            found_next = True
                            break
                        else:
                            matched_all = False
                            break

                if not found_next:
                    matched_all = False
                    break

            if matched_all:
                match_count += 1
                best_match_start = i
                best_match_end = curr_idx

    if match_count == 1:
        prefix = content_lines[:best_match_start]
        suffix = content_lines[best_match_end + 1:]

        # If we are deleting code (new_code is empty),
        # we might need to collapse resulting double newlines
        if not new_code.strip():
            if prefix and suffix and not prefix[-1].strip() and not suffix[0].strip():
                prefix = prefix[:-1]

        result_lines = prefix + ([new_code] if new_code else []) + suffix
        return '\n'.join(result_lines), "Significant Line Match"
    elif match_count > 1:
        raise ValueError("Ambiguous match: Sequence of code found multiple times. Needs more context.")

    # Strategy 3: Indentation-Flexible Significant Match
    match_count = 0
    for i in range(len(content_lines)):
        if _is_line_match(content_lines[i], old_lines[significant_old_indices[0]], fuzzy=True):
            curr_idx = i
            matched_all = True
            for sig_idx in significant_old_indices[1:]:
                found_next = False
                for search_idx in range(curr_idx + 1, len(content_lines)):
                    if content_lines[search_idx].strip():
                        if _is_line_match(content_lines[search_idx], old_lines[sig_idx], fuzzy=True):
                            curr_idx = search_idx
                            found_next = True
                            break
                        else:
                            matched_all = False
                            break
                if not found_next:
                    matched_all = False
                    break
            if matched_all:
                match_count += 1
                best_match_start = i
                best_match_end = curr_idx

    if match_count == 1:
        prefix = content_lines[:best_match_start]
        suffix = content_lines[best_match_end + 1:]
        if not new_code.strip():
            if prefix and suffix and not prefix[-1].strip() and not suffix[0].strip():
                prefix = prefix[:-1]

        result_lines = prefix + ([new_code] if new_code else []) + suffix
        return '\n'.join(result_lines), "Indentation-Flexible Match"

    # Strategy 4: Diagnostic check
    if normalize_whitespace(old_code) in normalize_whitespace(current_normalized):
        raise ValueError("Code found, but the structure is too different to apply safely.")

    raise ValueError("Original code block not found in the local file. The AI might be hallucinating old code.")