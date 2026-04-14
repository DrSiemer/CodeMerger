import os
from .utils import is_ignored
from .. import constants as c

def build_file_tree_data(base_dir, file_extensions, gitignore_patterns=None, filter_text="", is_extension_filter_active=True, selected_file_paths=None, is_gitignore_filter_active=True, unknown_files=None):
    """
    Scans the file system respecting .gitignore and returns a tree data structure.
    Optimized for massive projects by integrating .gitignore detection and Accumulated Pattern matching
    into a single-pass recursion stack to achieve O(N) complexity.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    filter_text_lower = filter_text.lower()
    base_dir_norm = os.path.abspath(base_dir).replace('\\', '/')

    if selected_file_paths is None:
        selected_file_paths = set()
    if unknown_files is None:
        unknown_files = set()

    def load_local_gitignore(path):
        """Checks for and parses a .gitignore in the current directory."""
        gitignore_path = os.path.join(path, '.gitignore')
        if os.path.isfile(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8-sig') as f:
                    return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            except (IOError, OSError):
                pass
        return None

    def _build_nodes(current_path, current_rel_path, active_patterns):
        nodes = []

        # 1. Discover and append local patterns for this subtree
        local_patterns = load_local_gitignore(current_path)
        new_active_patterns = active_patterns
        if local_patterns:
            # We clone the stack only when a new .gitignore is found to save memory
            new_active_patterns = active_patterns + [(current_path.replace('\\', '/'), local_patterns)]

        try:
            entries = sorted(os.scandir(current_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except OSError:
            return []

        for entry in entries:
            name_low = entry.name.lower()
            if name_low in c.SPECIAL_FILES_TO_IGNORE or name_low.startswith(c.ALLCODE_TEMP_PREFIX):
                continue

            # Optimized relative path generation via string concatenation
            rel_path = f"{current_rel_path}/{entry.name}" if current_rel_path else entry.name
            entry_path_norm = entry.path.replace('\\', '/')

            if entry.is_dir():
                # Directory Ignoring Check
                if is_gitignore_filter_active and rel_path not in selected_file_paths:
                    # Check if any selected file is deeper than this path to ensure path remains reachable
                    prefix = rel_path + "/"
                    is_reachable = any(p.startswith(prefix) for p in selected_file_paths)

                    if not is_reachable and is_ignored(entry_path_norm, base_dir_norm, new_active_patterns):
                        continue

                children = _build_nodes(entry.path, rel_path, new_active_patterns)
                matches_filter = filter_text_lower and filter_text_lower in entry.name.lower()

                if children or matches_filter:
                    nodes.append({
                        'name': entry.name,
                        'path': rel_path,
                        'type': 'dir',
                        'children': children
                    })
            else:
                # File Visibility Check
                visible = False
                if rel_path in selected_file_paths:
                    visible = True
                else:
                    matches_text = not filter_text_lower or filter_text_lower in name_low
                    matches_ext = not is_extension_filter_active or (os.path.splitext(name_low)[1] in extensions or name_low in exact_filenames)

                    if matches_text and matches_ext:
                        if not is_gitignore_filter_active or not is_ignored(entry_path_norm, base_dir_norm, new_active_patterns):
                            visible = True

                if visible:
                    is_filtered = False
                    filter_reason = ''

                    if rel_path in selected_file_paths:
                        file_git_ignored = is_ignored(entry_path_norm, base_dir_norm, new_active_patterns)
                        file_ext = os.path.splitext(name_low)[1]
                        is_valid_ext = file_ext in extensions or name_low in exact_filenames

                        if file_git_ignored:
                            is_filtered = True
                            filter_reason = 'Normally hidden by .gitignore'
                        elif not is_valid_ext:
                            is_filtered = True
                            filter_reason = 'Normally hidden by filetype settings'

                    nodes.append({
                        'name': entry.name,
                        'path': rel_path,
                        'type': 'file',
                        'is_new': rel_path in unknown_files,
                        'is_filtered': is_filtered,
                        'filter_reason': filter_reason
                    })
        return nodes

    # Start recursion with an empty patterns stack (or provided initial patterns)
    initial_patterns = gitignore_patterns if gitignore_patterns is not None else []
    return _build_nodes(base_dir, "", initial_patterns)