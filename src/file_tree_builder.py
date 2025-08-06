import os
from .utils import is_ignored

def build_file_tree_data(base_dir, file_extensions, gitignore_patterns):
    """
    Scans the file system respecting .gitignore and returns a data structure
    representing the relevant files and directories for the tree view
    """
    def _has_relevant_files(path):
        """Recursively checks if a directory contains any files matching the extension list"""
        for entry in os.scandir(path):
            if is_ignored(entry.path, base_dir, gitignore_patterns) or entry.name == 'allcode.txt':
                continue
            if entry.is_dir():
                if _has_relevant_files(entry.path):
                    return True
            elif entry.is_file() and os.path.splitext(entry.name)[1].lower() in file_extensions:
                return True
        return False

    def _build_nodes(current_path):
        """Walks a directory and builds a list of nodes for its contents"""
        nodes = []
        try:
            # Sort entries to show folders first, then files, all alphabetically
            entries = sorted(os.scandir(current_path), key=lambda e: (e.is_file(), e.name.lower()))
        except OSError:
            return []

        for entry in entries:
            if is_ignored(entry.path, base_dir, gitignore_patterns) or entry.name == 'allcode.txt':
                continue

            rel_path = os.path.relpath(entry.path, base_dir).replace('\\', '/')

            if entry.is_dir():
                if _has_relevant_files(entry.path):
                    node = {
                        'name': entry.name,
                        'path': rel_path,
                        'type': 'dir',
                        'children': _build_nodes(entry.path)
                    }
                    nodes.append(node)
            elif entry.is_file() and os.path.splitext(entry.name)[1].lower() in file_extensions:
                node = {
                    'name': entry.name,
                    'path': rel_path,
                    'type': 'file'
                }
                nodes.append(node)
        return nodes

    return _build_nodes(base_dir)