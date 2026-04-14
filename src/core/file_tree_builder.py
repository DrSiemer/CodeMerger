import os
from .utils import is_ignored
from .. import constants as c

def build_file_tree_data(base_dir, file_extensions, gitignore_patterns, filter_text="", is_extension_filter_active=True, selected_file_paths=None, is_gitignore_filter_active=True, unknown_files=None):
    """
    Scans the file system respecting .gitignore and returns a tree data structure.
    Optimized for large projects by building the tree and injecting metadata in a single pass.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    filter_text_lower = filter_text.lower()

    if selected_file_paths is None:
        selected_file_paths = set()
    if unknown_files is None:
        unknown_files = set()

    def is_visible(rel_path, file_name):
        """Determines if a file should be visible based on filters."""
        # Files in the Merge Order are ALWAYS visible regardless of filters
        if rel_path in selected_file_paths:
            return True

        if filter_text_lower and filter_text_lower not in file_name.lower():
            return False

        if is_extension_filter_active:
            file_name_lower = file_name.lower()
            file_ext = os.path.splitext(file_name_lower)[1]
            if not (file_ext in extensions or file_name_lower in exact_filenames):
                return False

        return True

    def should_be_ignored(path, rel_path):
        """Determines if a directory should be skipped."""
        if not is_gitignore_filter_active:
            return False

        # Files in the selection bypass gitignore visibility
        if rel_path in selected_file_paths:
            return False

        # Check if any selected file is deeper than this path to ensure path remains reachable
        prefix = rel_path + "/"
        if any(p.startswith(prefix) for p in selected_file_paths):
            return False

        return is_ignored(path, base_dir, gitignore_patterns)

    def _build_nodes(current_path):
        nodes = []
        try:
            # Scandir is significantly faster than listdir for large directories
            entries = sorted(os.scandir(current_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except OSError:
            return []

        for entry in entries:
            name_low = entry.name.lower()
            # Prune ignored system/temp folders and files early
            if name_low in c.SPECIAL_FILES_TO_IGNORE or name_low.startswith(c.ALLCODE_TEMP_PREFIX):
                continue

            rel_path = os.path.relpath(entry.path, base_dir).replace('\\', '/')

            if entry.is_dir():
                if should_be_ignored(entry.path, rel_path):
                    continue

                children = _build_nodes(entry.path)

                # Keep directory if it has visible children OR if it matches the text filter itself
                matches_filter = filter_text_lower and filter_text_lower in entry.name.lower()

                if children or matches_filter:
                    nodes.append({
                        'name': entry.name,
                        'path': rel_path,
                        'type': 'dir',
                        'children': children
                    })
            else:
                if is_visible(rel_path, entry.name):
                    # Fold metadata logic into the scan to avoid second recursive pass
                    is_filtered = False
                    filter_reason = ''

                    if rel_path in selected_file_paths:
                        file_git_ignored = is_ignored(entry.path, base_dir, gitignore_patterns)

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

    return _build_nodes(base_dir)