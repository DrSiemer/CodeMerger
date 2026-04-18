import os
from ..core.utils import is_ignored
from .. import constants as c

def enrich_inventory(base_dir, raw_inventory):
    """
    Enriches a raw disk walk inventory with metadata (ignore status, extension).
    This moves expensive string/IO operations out of the UI build loop.
    """
    base_dir_norm = os.path.abspath(base_dir).replace('\\', '/')
    gitignores = raw_inventory['gitignores']

    enriched_files = []
    for rel_path in raw_inventory['files']:
        abs_path = os.path.join(base_dir, rel_path)

        # Store metadata to make UI filtering O(1) per file
        enriched_files.append({
            'p': rel_path,                           # Path
            'n': os.path.basename(rel_path).lower(), # Name (normalized)
            'i': is_ignored(abs_path, base_dir_norm, gitignores), # Is Ignored
            'e': os.path.splitext(rel_path.lower())[1] # Extension
        })

    # Sort enriched files by path (case-insensitive) for stable Trie construction
    enriched_files.sort(key=lambda x: x['p'].lower())

    return {
        'files': enriched_files,
        'gitignores': gitignores
    }

def get_project_inventory(base_dir, cancel_event=None):
    """
    Performs a raw disk walk and returns a complete inventory of the project.
    Returns a dict: { 'files': [rel_paths], 'gitignores': [(abs_root, [patterns])] }
    This inventory is used as the raw source for tree building.
    """
    file_list = []
    gitignore_data = []

    add_file = file_list.append
    add_ignore = gitignore_data.append

    def _walk(current_path, current_rel_path):
        if cancel_event and cancel_event.is_set():
            return

        # Discover local gitignore
        gitignore_path = os.path.join(current_path, '.gitignore')
        if os.path.isfile(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8-sig') as f:
                    patterns = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                    if patterns:
                        add_ignore((current_path.replace('\\', '/'), patterns))
            except (IOError, OSError):
                pass

        try:
            for entry in os.scandir(current_path):
                name_lower = entry.name.lower()
                # Skip hard-coded performance anchors
                if name_lower in c.SPECIAL_FILES_TO_IGNORE or name_lower.startswith(c.ALLCODE_TEMP_PREFIX):
                    continue

                if name_lower == '.git':
                    continue

                rel_path = f"{current_rel_path}/{entry.name}" if current_rel_path else entry.name

                if entry.is_dir():
                    _walk(entry.path, rel_path)
                else:
                    # We store ALL files in the inventory.
                    # Gitignore and Extension filtering happens during Trie building in the API.
                    add_file(rel_path)
        except OSError:
            pass

    _walk(base_dir, "")

    return {
        'files': file_list,
        'gitignores': gitignore_data
    }

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