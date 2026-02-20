import os
from ..core.utils import is_ignored
from .. import constants as c

def get_all_matching_files(base_dir, file_extensions, gitignore_patterns, always_include_paths=None):
    """
    Scans the file system and returns a flat list of all matching file paths,
    respecting .gitignore.

    Args:
        base_dir (str): Project root directory.
        file_extensions (list): List of extensions to include.
        gitignore_patterns (list): Parsed gitignore patterns.
        always_include_paths (set, optional): Set of relative paths to explicitly
                                              check and include if they exist,
                                              ignoring filters.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    matching_files = []

    def _scan_dir(current_path):
        try:
            for entry in os.scandir(current_path):
                if entry.name.lower() in c.SPECIAL_FILES_TO_IGNORE:
                    continue

                if is_ignored(entry.path, base_dir, gitignore_patterns):
                    continue

                if entry.is_dir():
                    _scan_dir(entry.path)
                elif entry.is_file():
                    file_name_lower = entry.name.lower()
                    file_ext = os.path.splitext(file_name_lower)[1]
                    if file_ext in extensions or file_name_lower in exact_filenames:
                        rel_path = os.path.relpath(entry.path, base_dir).replace('\\', '/')
                        matching_files.append(rel_path)
        except OSError:
            pass # Ignore permission errors etc

    _scan_dir(base_dir)

    # Post-scan: Explicitly check and include specific paths (e.g., selected files)
    # that might have been filtered out by gitignore or extension filters.
    if always_include_paths:
        # Convert list to set for O(1) lookups if it's not already
        found_set = set(matching_files)

        for path in always_include_paths:
            if path in found_set:
                continue

            full_path = os.path.join(base_dir, path)
            if os.path.isfile(full_path):
                # Normalizing path separators just in case
                normalized_path = path.replace('\\', '/')
                matching_files.append(normalized_path)

    return matching_files