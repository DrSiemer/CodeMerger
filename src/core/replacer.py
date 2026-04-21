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

def levenshtein(a, b):
    """Calculates the Levenshtein distance between two strings."""
    if a == b: return 0
    if len(a) == 0: return len(b)
    if len(b) == 0: return len(a)
    if len(a) > len(b):
        a, b = b, a
    prev = list(range(len(a) + 1))
    for j in range(1, len(b) + 1):
        curr = [j]
        for i in range(1, len(a) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr.append(min(prev[i] + 1, curr[i - 1] + 1, prev[i - 1] + cost))
        prev = curr
    return prev[-1]

def normalize_whitespace(text):
    """Collapses all whitespace into a single space for aggressive matching."""
    return re.sub(r'\s+', ' ', text).strip()

def _clean_block(text):
    """Normalizes line endings and removes surrounding empty lines."""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.rstrip('\n').lstrip('\n')

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

    # Strategy 0.5: Replace All Shortcut: if the model provides the replace-all marker, we replace the entire file content
    if old_code.strip() == "--==[ REPLACE ALL ]==--":
        return new_code, "Replace All"

    if not old_code.strip():
        if not current_normalized.strip():
            return new_code, "Creation"
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

    # Filter for lines that actually contain code.
    # This allows us to jump over variable amounts of whitespace/blank lines between code blocks.
    significant_old_indices = [i for i, l in enumerate(old_lines) if l.strip()]
    if not significant_old_indices:
        raise ValueError("The 'ORIGINAL' block contains no code-bearing lines.")

    best_match_start = -1
    best_match_end = -1
    match_count = 0

    # Scan the file for the sequence of significant lines
    for i in range(len(content_lines)):
        # Check if the first non-empty line of the block matches the current line
        if _is_line_match(content_lines[i], old_lines[significant_old_indices[0]]):
            curr_idx = i
            matched_all = True

            for sig_idx in significant_old_indices[1:]:
                found_next = False
                # Search forward for the next significant line
                for search_idx in range(curr_idx + 1, len(content_lines)):
                    if content_lines[search_idx].strip():
                        if _is_line_match(content_lines[search_idx], old_lines[sig_idx]):
                            curr_idx = search_idx
                            found_next = True
                            break
                        else:
                            # We found code, but it's the wrong code. Match failed.
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

    # Strategy 4: Block-Anchor Match (Levenshtein)
    # Anchors on the first and last non-empty lines. Scans all candidate blocks
    # whose boundaries match. Scores middle lines via Levenshtein distance.
    if len(significant_old_indices) >= 3:
        first_search = old_lines[significant_old_indices[0]].strip()
        last_search = old_lines[significant_old_indices[-1]].strip()
        search_block_size = len(significant_old_indices)

        candidates = []
        for i in range(len(content_lines)):
            if content_lines[i].strip() == first_search:
                for j in range(i + 2, len(content_lines)):
                    if content_lines[j].strip() == last_search:
                        candidates.append((i, j))
                        break

        if candidates:
            def score_similarity(start_line, end_line):
                cand_lines = [l for l in content_lines[start_line:end_line+1] if l.strip()]
                if len(cand_lines) < 3: return 0.0

                actual_block_size = len(cand_lines)
                lines_to_check = min(search_block_size - 2, actual_block_size - 2)
                if lines_to_check <= 0: return 1.0

                similarity = 0.0
                for j in range(1, min(search_block_size - 1, actual_block_size - 1)):
                    orig_line = cand_lines[j].strip()
                    search_line = old_lines[significant_old_indices[j]].strip()
                    max_len = max(len(orig_line), len(search_line))
                    if max_len == 0: continue
                    dist = levenshtein(orig_line, search_line)
                    similarity += (1.0 - dist / max_len) / lines_to_check
                return similarity

            best_match = None
            max_sim = -1.0

            if len(candidates) == 1:
                start_line, end_line = candidates[0]
                if score_similarity(start_line, end_line) >= 0.0:
                    best_match = (start_line, end_line)
            else:
                for c_start, c_end in candidates:
                    sim = score_similarity(c_start, c_end)
                    if sim > max_sim:
                        max_sim = sim
                        best_match = (c_start, c_end)

                if max_sim < 0.3:
                    best_match = None

            if best_match:
                prefix = content_lines[:best_match[0]]
                suffix = content_lines[best_match[1] + 1:]
                if not new_code.strip():
                    if prefix and suffix and not prefix[-1].strip() and not suffix[0].strip():
                        prefix = prefix[:-1]

                result_lines = prefix + ([new_code] if new_code else []) + suffix
                return '\n'.join(result_lines), "Block-Anchor Match"

    # Helper for robust normalized block matching
    def apply_normalized_match(normalizer_fn, strategy_name):
        normalized_old = normalizer_fn(old_code)
        if not normalized_old:
            return None

        matches = []
        for i in range(len(content_lines)):
            # Skip lines that become empty after normalization to avoid overlapping false matches
            if not normalizer_fn(content_lines[i]):
                continue

            accumulated = []
            for j in range(i, min(i + len(old_lines) * 3, len(content_lines))):
                accumulated.append(content_lines[j])
                norm_accum = normalizer_fn('\n'.join(accumulated))

                if norm_accum == normalized_old:
                    matches.append((i, j))
                    break
                elif len(norm_accum) > len(normalized_old) + 50:
                    break

        if len(matches) == 1:
            best_match_start, best_match_end = matches[0]
            prefix = content_lines[:best_match_start]
            suffix = content_lines[best_match_end + 1:]
            if not new_code.strip():
                if prefix and suffix and not prefix[-1].strip() and not suffix[0].strip():
                    prefix = prefix[:-1]
            result_lines = prefix + ([new_code] if new_code else []) + suffix
            return '\n'.join(result_lines), strategy_name
        elif len(matches) > 1:
            raise ValueError(f"Ambiguous match: {strategy_name} block appears {len(matches)} times.")

        return None

    # Strategy 5: Whitespace-Normalized Match
    res = apply_normalized_match(normalize_whitespace, "Whitespace-Normalized Match")
    if res: return res

    # Strategy 6: All-Whitespace-Stripped Match (Aggressive Fallback)
    def strip_all_whitespace(text):
        return re.sub(r'\s+', '', text)

    res = apply_normalized_match(strip_all_whitespace, "All-Whitespace-Stripped Match")
    if res: return res

    # Strategy 7: Diagnostic check
    if normalize_whitespace(old_code) in normalize_whitespace(current_normalized):
        raise ValueError("Code found, but the structure is too different to apply safely.")

    raise ValueError("Original code block not found in the local file. The AI might be hallucinating old code.")