import os
from ..core.utils import is_ignored
from .. import constants as c

def get_all_matching_files(base_dir, file_extensions, gitignore_patterns):
    """
    Scans the file system and returns a flat list of all matching file paths,
    respecting .gitignore. Optimized for speed, returning just a list of strings
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
    return matching_files