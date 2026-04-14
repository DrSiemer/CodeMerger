import os
from ..core.utils import is_ignored
from .. import constants as c

def get_all_matching_files(base_dir, file_extensions, gitignore_patterns=None, always_include_paths=None, cancel_event=None):
    """
    Scans the file system and returns a flat list of all matching file paths,
    respecting .gitignore. Integrated single-pass scan eliminates redundant traversal overhead.

    Args:
        base_dir (str): Project root directory.
        file_extensions (list): List of extensions to include.
        gitignore_patterns (list, optional): Pre-parsed patterns. If None, discovers automatically.
        always_include_paths (set, optional): Set of relative paths to explicitly check.
        cancel_event (threading.Event, optional): Event to signal scan interruption.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    matching_files = []
    base_dir_norm = os.path.abspath(base_dir).replace('\\', '/')

    def _scan_dir(current_path, current_rel_path, active_patterns):
        if cancel_event and cancel_event.is_set():
            return

        # Check for local gitignore to append to stack
        gitignore_path = os.path.join(current_path, '.gitignore')
        new_active_patterns = active_patterns
        if os.path.isfile(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8-sig') as f:
                    lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                    if lines:
                        new_active_patterns = active_patterns + [(current_path.replace('\\', '/'), lines)]
            except (IOError, OSError):
                pass

        try:
            for entry in os.scandir(current_path):
                if cancel_event and cancel_event.is_set():
                    return

                name_lower = entry.name.lower()
                if name_lower in c.SPECIAL_FILES_TO_IGNORE or name_lower.startswith(c.ALLCODE_TEMP_PREFIX):
                    continue

                if is_ignored(entry.path, base_dir_norm, new_active_patterns):
                    continue

                rel_path = f"{current_rel_path}/{entry.name}" if current_rel_path else entry.name

                if entry.is_dir():
                    _scan_dir(entry.path, rel_path, new_active_patterns)
                elif entry.is_file():
                    file_ext = os.path.splitext(name_lower)[1]
                    if file_ext in extensions or name_lower in exact_filenames:
                        matching_files.append(rel_path)
        except OSError:
            pass

    initial_patterns = gitignore_patterns if gitignore_patterns is not None else []
    _scan_dir(base_dir, "", initial_patterns)

    if cancel_event and cancel_event.is_set():
        return matching_files

    if always_include_paths:
        found_set = set(matching_files)
        for path in always_include_paths:
            normalized_path = path.replace('\\', '/')
            if normalized_path in found_set:
                continue

            full_path = os.path.join(base_dir, normalized_path)
            if os.path.isfile(full_path):
                matching_files.append(normalized_path)

    return matching_files