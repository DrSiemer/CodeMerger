import os
from ...core.utils import is_ignored
from ... import constants as c

def build_file_tree_data(base_dir, file_extensions, gitignore_patterns, filter_text="", is_extension_filter_active=True, selected_file_paths=None, is_gitignore_filter_active=True):
    """
    Scans the file system respecting .gitignore and returns a data structure
    representing the relevant files and directories for the tree view.
    Ensures that files in 'selected_file_paths' always bypass filters to remain visible.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    filter_text_lower = filter_text.lower()

    if selected_file_paths is None:
        selected_file_paths = set()

    def is_path_or_child_selected(rel_path):
        """Checks if this path or any path deeper than it is in the Merge Order."""
        if rel_path in selected_file_paths:
            return True
        prefix = rel_path + "/"
        return any(p.startswith(prefix) for p in selected_file_paths)

    def should_be_ignored(path, rel_path):
        """Determines if a directory should be entered or ignored by gitignore."""
        if not is_gitignore_filter_active:
            return False
        # If the directory itself, or any file within it, is selected, we MUST NOT ignore it.
        if is_path_or_child_selected(rel_path):
            return False
        return is_ignored(path, base_dir, gitignore_patterns)

    def is_file_visible(rel_path, file_name):
        """Helper to determine if a file should be visible based on the filter state."""
        # Files in the Merge Order are ALWAYS visible regardless of filters.
        if rel_path in selected_file_paths:
            return True

        if is_extension_filter_active:
            file_name_lower = file_name.lower()
            file_ext = os.path.splitext(file_name_lower)[1]
            if not (file_ext in extensions or file_name_lower in exact_filenames):
                return False

        return True

    if not filter_text_lower:
        # Original, unfiltered logic for performance when not searching
        def _has_relevant_files(path, rel_path):
            try:
                for entry in os.scandir(path):
                    e_rel = os.path.relpath(entry.path, base_dir).replace('\\', '/')
                    if should_be_ignored(entry.path, e_rel) or entry.name.lower() in c.SPECIAL_FILES_TO_IGNORE:
                        continue
                    if entry.is_dir():
                        if _has_relevant_files(entry.path, e_rel): return True
                    elif entry.is_file():
                        if is_file_visible(e_rel, entry.name):
                            return True
            except OSError: return False
            return False

        def _build_nodes_unfiltered(current_path):
            nodes = []
            try: entries = sorted(os.scandir(current_path), key=lambda e: (e.is_file(), e.name.lower()))
            except OSError: return []

            for entry in entries:
                e_rel = os.path.relpath(entry.path, base_dir).replace('\\', '/')
                if should_be_ignored(entry.path, e_rel) or entry.name.lower() in c.SPECIAL_FILES_TO_IGNORE: continue

                if entry.is_dir():
                    if _has_relevant_files(entry.path, e_rel):
                        nodes.append({'name': entry.name, 'path': e_rel, 'type': 'dir', 'children': _build_nodes_unfiltered(entry.path)})
                elif entry.is_file():
                    if is_file_visible(e_rel, entry.name):
                        nodes.append({'name': entry.name, 'path': e_rel, 'type': 'file'})
            return nodes
        return _build_nodes_unfiltered(base_dir)

    # New filtered logic
    def _build_nodes_filtered(current_path):
        nodes = []
        try: entries = sorted(os.scandir(current_path), key=lambda e: (e.is_file(), e.name.lower()))
        except OSError: return [], False

        has_match_in_subtree = False
        for entry in entries:
            e_rel = os.path.relpath(entry.path, base_dir).replace('\\', '/')
            if should_be_ignored(entry.path, e_rel) or entry.name.lower() in c.SPECIAL_FILES_TO_IGNORE: continue

            name_matches_filter = filter_text_lower in entry.name.lower()

            if entry.is_dir():
                child_nodes, child_has_match = _build_nodes_filtered(entry.path)
                if name_matches_filter or child_has_match:
                    has_match_in_subtree = True
                    nodes.append({'name': entry.name, 'path': e_rel, 'type': 'dir', 'children': child_nodes})
            elif entry.is_file():
                if is_file_visible(e_rel, entry.name) and name_matches_filter:
                    has_match_in_subtree = True
                    nodes.append({'name': entry.name, 'path': e_rel, 'type': 'file'})
        return nodes, has_match_in_subtree

    result_nodes, _ = _build_nodes_filtered(base_dir)
    return result_nodes