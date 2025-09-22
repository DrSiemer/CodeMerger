import os
from ...core.utils import is_ignored

def build_file_tree_data(base_dir, file_extensions, gitignore_patterns, filter_text=""):
    """
    Scans the file system respecting .gitignore and returns a data structure
    representing the relevant files and directories for the tree view.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    filter_text_lower = filter_text.lower()

    if not filter_text_lower:
        # Original, unfiltered logic for performance when not searching
        def _has_relevant_files(path):
            try:
                for entry in os.scandir(path):
                    if is_ignored(entry.path, base_dir, gitignore_patterns) or entry.name == '.allcode':
                        continue
                    if entry.is_dir():
                        if _has_relevant_files(entry.path): return True
                    elif entry.is_file():
                        file_name_lower = entry.name.lower()
                        file_ext = os.path.splitext(file_name_lower)[1]
                        if file_ext in extensions or file_name_lower in exact_filenames:
                            return True
            except OSError: return False
            return False

        def _build_nodes_unfiltered(current_path):
            nodes = []
            try: entries = sorted(os.scandir(current_path), key=lambda e: (e.is_file(), e.name.lower()))
            except OSError: return []

            for entry in entries:
                if is_ignored(entry.path, base_dir, gitignore_patterns) or entry.name == '.allcode': continue
                rel_path = os.path.relpath(entry.path, base_dir).replace('\\', '/')
                if entry.is_dir():
                    if _has_relevant_files(entry.path):
                        nodes.append({'name': entry.name, 'path': rel_path, 'type': 'dir', 'children': _build_nodes_unfiltered(entry.path)})
                elif entry.is_file():
                    file_name_lower = entry.name.lower()
                    file_ext = os.path.splitext(file_name_lower)[1]
                    if file_ext in extensions or file_name_lower in exact_filenames:
                        nodes.append({'name': entry.name, 'path': rel_path, 'type': 'file'})
            return nodes
        return _build_nodes_unfiltered(base_dir)

    # New filtered logic
    def _build_nodes_filtered(current_path):
        nodes = []
        try: entries = sorted(os.scandir(current_path), key=lambda e: (e.is_file(), e.name.lower()))
        except OSError: return [], False

        has_match_in_subtree = False
        for entry in entries:
            if is_ignored(entry.path, base_dir, gitignore_patterns) or entry.name == '.allcode': continue

            rel_path = os.path.relpath(entry.path, base_dir).replace('\\', '/')
            name_matches_filter = filter_text_lower in entry.name.lower()

            if entry.is_dir():
                child_nodes, child_has_match = _build_nodes_filtered(entry.path)
                if name_matches_filter or child_has_match:
                    has_match_in_subtree = True
                    nodes.append({'name': entry.name, 'path': rel_path, 'type': 'dir', 'children': child_nodes})
            elif entry.is_file():
                file_name_lower = entry.name.lower()
                file_ext = os.path.splitext(file_name_lower)[1]
                is_valid_type = file_ext in extensions or file_name_lower in exact_filenames
                if is_valid_type and name_matches_filter:
                    has_match_in_subtree = True
                    nodes.append({'name': entry.name, 'path': rel_path, 'type': 'file'})
        return nodes, has_match_in_subtree

    result_nodes, _ = _build_nodes_filtered(base_dir)
    return result_nodes