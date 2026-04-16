import os
from .utils import is_ignored
from .. import constants as c

def build_file_tree_data(base_dir, file_extensions, gitignore_patterns=None, filter_text="", is_extension_filter_active=True, selected_file_paths=None, is_gitignore_filter_active=True, unknown_files=None, inventory=None):
    """
    Scans the file system respecting .gitignore and returns a tree data structure.
    Optimized for massive projects by supporting an in-memory 'inventory' cache.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    filter_text_lower = filter_text.lower()
    base_dir_norm = os.path.abspath(base_dir).replace('\\', '/')

    if selected_file_paths is None:
        selected_file_paths = set()
    if unknown_files is None:
        unknown_files = set()

    # --- MODE A: BUILD FROM ENRICHED MEMORY INVENTORY (INSTANT) ---
    if inventory:
        all_items = inventory['files'] # Enriched list of {p, n, i, e}
        gitignores = inventory['gitignores']

        # First Pass: Identify visible files
        visible_items = []
        for item in all_items:
            rel_path = item['p']

            # Rule: Text Filter is the absolute primary. If it exists, everything must match it.
            if filter_text_lower and filter_text_lower not in rel_path.lower():
                continue

            is_selected = rel_path in selected_file_paths

            # Rule: If not selected, it must pass secondary settings filters
            if not is_selected:
                # Extension Filter
                if is_extension_filter_active:
                    ext = item['e']
                    name_low = item['n']
                    if not (ext in extensions or name_low in exact_filenames):
                        continue

                # Gitignore Filter
                if is_gitignore_filter_active:
                    # USE PRE-CALCULATED FLAG from background enrichment
                    if item['i']:
                        continue

            visible_items.append(item)

        # Second Pass: Construct Trie structure
        root_nodes = []
        path_to_node = {}

        # Inventory 'files' is pre-sorted in FileMonitorThread (alphabetical)
        for item in visible_items:
            rel_path = item['p']
            parts = rel_path.split('/')
            current_level_nodes = root_nodes
            parent_path = ""

            for i, part in enumerate(parts):
                is_last = (i == len(parts) - 1)
                part_path = f"{parent_path}/{part}" if parent_path else part

                if part_path not in path_to_node:
                    node_type = 'file' if is_last else 'dir'

                    is_filtered = False
                    filter_reason = ''

                    # Logic for "Purple" Metadata (Selected but hidden by settings)
                    if node_type == 'file' and rel_path in selected_file_paths:
                        file_git_ignored = item['i']
                        file_ext = item['e']
                        name_low = item['n']
                        is_valid_ext = file_ext in extensions or name_low in exact_filenames

                        if file_git_ignored:
                            is_filtered = True
                            filter_reason = 'Normally hidden by .gitignore'
                        elif not is_valid_ext:
                            is_filtered = True
                            filter_reason = 'Normally hidden by filetype settings'

                    new_node = {
                        'name': part,
                        'path': part_path,
                        'type': node_type
                    }
                    if node_type == 'dir':
                        new_node['children'] = []
                    else:
                        new_node['is_new'] = part_path in unknown_files
                        new_node['is_filtered'] = is_filtered
                        new_node['filter_reason'] = filter_reason

                    path_to_node[part_path] = new_node
                    current_level_nodes.append(new_node)

                if not is_last:
                    current_level_nodes = path_to_node[part_path]['children']
                    parent_path = part_path

        # Final Pass: Restore "Folders First" sorting
        def sort_tree(nodes):
            # Sort by type (dirs before files) and then name (alphabetical)
            nodes.sort(key=lambda n: (n['type'] != 'dir', n['name'].lower()))
            for n in nodes:
                if 'children' in n:
                    sort_tree(n['children'])

        sort_tree(root_nodes)
        return root_nodes

    # --- MODE B: BUILD FROM DISK (FALLBACK) ---
    def load_local_gitignore(path):
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
        local_patterns = load_local_gitignore(current_path)
        new_active_patterns = active_patterns
        if local_patterns:
            new_active_patterns = active_patterns + [(current_path.replace('\\', '/'), local_patterns)]

        try:
            entries = sorted(os.scandir(current_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except OSError:
            return []

        for entry in entries:
            name_low = entry.name.lower()
            if name_low in c.SPECIAL_FILES_TO_IGNORE or name_low.startswith(c.ALLCODE_TEMP_PREFIX):
                continue

            rel_path = f"{current_rel_path}/{entry.name}" if current_rel_path else entry.name
            entry_path_norm = entry.path.replace('\\', '/')

            # Standard visibility logic for Disk Mode
            if entry.is_dir():
                # Text Filter (applies to path)
                matches_filter = not filter_text_lower or filter_text_lower in rel_path.lower()

                if is_gitignore_filter_active and rel_path not in selected_file_paths:
                    prefix = rel_path + "/"
                    is_reachable = any(p.startswith(prefix) for p in selected_file_paths)
                    if not is_reachable and is_ignored(entry_path_norm, base_dir_norm, new_active_patterns):
                        continue

                children = _build_nodes(entry.path, rel_path, new_active_patterns)
                if children or matches_filter:
                    nodes.append({'name': entry.name, 'path': rel_path, 'type': 'dir', 'children': children})
            else:
                visible = False
                # Primary filter: Search
                if not filter_text_lower or filter_text_lower in rel_path.lower():
                    if rel_path in selected_file_paths:
                        visible = True
                    else:
                        file_ext = os.path.splitext(name_low)[1]
                        matches_ext = not is_extension_filter_active or (file_ext in extensions or name_low in exact_filenames)
                        if matches_ext:
                            if not is_gitignore_filter_active or not is_ignored(entry_path_norm, base_dir_norm, new_active_patterns):
                                visible = True

                if visible:
                    is_filtered = False
                    filter_reason = ''
                    if rel_path in selected_file_paths:
                        file_git_ignored = is_ignored(entry_path_norm, base_dir_norm, new_active_patterns)
                        file_ext = os.path.splitext(name_low)[1]
                        is_valid_ext = file_ext in extensions or name_low in exact_filenames
                        if file_git_ignored: is_filtered, filter_reason = True, 'Normally hidden by .gitignore'
                        elif not is_valid_ext: is_filtered, filter_reason = True, 'Normally hidden by filetype settings'

                    nodes.append({
                        'name': entry.name, 'path': rel_path, 'type': 'file',
                        'is_new': rel_path in unknown_files, 'is_filtered': is_filtered, 'filter_reason': filter_reason
                    })
        return nodes

    initial_patterns = gitignore_patterns if gitignore_patterns is not None else []
    return _build_nodes(base_dir, "", initial_patterns)