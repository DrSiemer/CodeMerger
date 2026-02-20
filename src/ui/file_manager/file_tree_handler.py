import os
import time
from ... import constants as c
from ...core.utils import is_ignored

class FileTreeHandler:
    """
    Manages the file tree view in the FileManagerWindow, including population,
    event handling, and visual state.
    """
    def __init__(self, parent, tree_widget, action_button, item_map, path_to_item_id, is_selected_callback, on_toggle_callback):
        self.parent = parent
        self.tree = tree_widget
        self.action_button = action_button
        self.item_map = item_map
        self.path_to_item_id = path_to_item_id
        self.is_selected = is_selected_callback
        self.on_toggle = on_toggle_callback

        # Bind events
        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<Double-1>', self.handle_double_click)
        self.tree.bind('<Return>', self.toggle_selection_for_selected) # For accessibility
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.tree.bind("<Button-1>", self.handle_tree_deselection_click, add='+')

    def get_expanded_dirs(self):
        """Returns a list of currently expanded directories"""
        return [
            info['path'] for item_id, info in self.item_map.items()
            if info.get('type') == 'dir' and self.tree.item(item_id, 'open')
        ]

    def update_item_visuals(self, item_id, current_selection_paths=None):
        """
        Updates the text (checkbox) and visual style of a tree item.
        Applies 'filtered_file_highlight' if a file is normally hidden by filters.
        Applies 'selected_grey' tag if:
        1. A file is selected OR is in the ignore list (e.g. __init__.py).
        2. A folder has all its 'relevant' files selected (ignoring files in the list).
        """
        item_info = self.item_map.get(item_id, {})
        item_type = item_info.get('type')
        if not item_type: return

        if current_selection_paths is None:
            # Create the set for O(1) lookup
            current_selection_paths = {f['path'] for f in self.parent.selection_handler.ordered_selection}

        tags = list(self.tree.item(item_id, 'tags'))

        # Clear existing visual tags to start fresh
        for t in ['selected_grey', 'filtered_file_highlight']:
            if t in tags: tags.remove(t)

        if item_type == 'file':
            path = item_info['path']
            filename = os.path.basename(path)
            is_checked = path in current_selection_paths

            check_char = "☑" if is_checked else "☐"
            self.tree.item(item_id, text=f"{check_char} {filename}")

            # --- Check Normal Filter Status ---
            hidden_reasons = []

            # 1. Check Gitignore
            if is_ignored(os.path.join(self.parent.base_dir, path), self.parent.base_dir, self.parent.gitignore_patterns):
                hidden_reasons.append("the .gitignore filter")

            # 2. Check Extension Filter
            file_name_lower = filename.lower()
            file_ext = os.path.splitext(file_name_lower)[1]
            extensions = {ext for ext in self.parent.file_extensions if ext.startswith('.')}
            exact_filenames = {ext for ext in self.parent.file_extensions if not ext.startswith('.')}

            if not (file_ext in extensions or file_name_lower in exact_filenames):
                hidden_reasons.append("the filetype filter")

            if hidden_reasons:
                tags.append('filtered_file_highlight')
                reason_str = " and ".join(hidden_reasons)
                item_info['hidden_reason'] = f"This file would normally be hidden by {reason_str}."
            else:
                item_info.pop('hidden_reason', None)
                # Apply grey out only if it's NOT a filtered highlight
                if is_checked or filename in c.FILES_TO_IGNORE_FOR_VISUAL_COMPLETENESS:
                    tags.append('selected_grey')

        elif item_type == 'dir':
            files_in_subtree = self._get_all_files_in_subtree(item_id)

            if not files_in_subtree:
                # Folder contains no files (empty or only dirs).
                # Consider it "complete" (grey) so it doesn't draw attention.
                tags.append('selected_grey')
            else:
                # Filter down to only files that actually matter for "completeness"
                relevant_files = [
                    p for p in files_in_subtree
                    if os.path.basename(p) not in c.FILES_TO_IGNORE_FOR_VISUAL_COMPLETENESS
                ]

                if not relevant_files:
                    # Folder contains ONLY ignored files (e.g. only __init__.py).
                    # It is visually complete.
                    tags.append('selected_grey')
                else:
                    # Folder is grey only if ALL relevant files are selected.
                    if all(p in current_selection_paths for p in relevant_files):
                        tags.append('selected_grey')

        self.tree.item(item_id, tags=tags)

    def update_all_visuals(self):
        """Iterates through all items in the tree and updates their visual state."""
        # Calculate selection set once for performance
        current_selection_paths = {f['path'] for f in self.parent.selection_handler.ordered_selection}
        for item_id in self.item_map:
            self.update_item_visuals(item_id, current_selection_paths)

    def handle_tree_deselection_click(self, event):
        """Deselects a tree item if a click occurs in an empty area"""
        if not self.tree.identify_row(event.y) and self.tree.selection():
            self.tree.selection_set("")

    def on_tree_selection_change(self, event=None):
        """Callback for when the tree selection changes"""
        self.parent.handle_tree_select(event)

    def update_action_button_state(self):
        """Updates the state and text of the button under the treeview based on multi-selection."""
        selection = self.tree.selection()
        if not selection:
            self.action_button.config(state='disabled', text="Add to Merge List")
            return

        selected_files = [
            self.item_map.get(item_id) for item_id in selection
            if self.item_map.get(item_id, {}).get('type') == 'file'
        ]

        if not selected_files:
            self.action_button.config(state='disabled', text="Add to Merge List")
            return

        self.action_button.config(state='normal')

        paths = [f['path'] for f in selected_files]
        selection_states = [self.is_selected(path) for path in paths]

        if all(selection_states):
            self.action_button.config(text="Remove from Merge List")
        elif not any(selection_states):
            self.action_button.config(text="Add to Merge List")
        else:
            self.action_button.config(text="Toggle Selection")

    def handle_tree_click(self, event):
        """Standard click handler to manage focus and manual click tracking."""
        # Selection is handled natively by the widget. We just ensure it has focus.
        self.tree.focus_set()

    def handle_double_click(self, event):
        """
        Handles native double-click event. Toggles files or folders
        and blocks the default tree expansion/collapse behavior.
        """
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self._toggle_item(item_id)
        return "break"

    def _get_all_files_in_subtree(self, parent_id):
        """Recursively collects all file paths under a given directory node in the tree."""
        files = []
        for child_id in self.tree.get_children(parent_id):
            child_info = self.item_map.get(child_id, {})
            if child_info.get('type') == 'file':
                files.append(child_info['path'])
            elif child_info.get('type') == 'dir':
                files.extend(self._get_all_files_in_subtree(child_id))
        return files

    def toggle_selection_for_selected(self, event=None):
        """Adds or removes the selected file(s) from the merge list via the callback"""
        selection = self.tree.selection()
        if not selection:
            return "break"

        for item_id in selection:
            self._toggle_item(item_id)

        return "break"

    def get_all_file_paths_in_tree_order(self):
        """Returns a flat list of all file paths in the order they appear in the tree"""
        all_tree_files = []
        def _traverse(parent_id):
            for item_id in self.tree.get_children(parent_id):
                item_info = self.item_map.get(item_id, {})
                if item_info.get('type') == 'file':
                    all_tree_files.append(item_info['path'])
                elif item_info.get('type') == 'dir':
                    _traverse(item_id)
        _traverse('')
        return all_tree_files

    def _toggle_item(self, item_id):
        """Toggles a single file or an entire folder's contents."""
        if not item_id:
            return
        item_info = self.item_map.get(item_id, {})
        item_type = item_info.get('type')

        if item_type == 'file':
            self.on_toggle(item_info['path'])
        elif item_type == 'dir':
            files_in_subtree = self._get_all_files_in_subtree(item_id)
            if not files_in_subtree:
                return

            current_selection_paths = {f['path'] for f in self.parent.selection_handler.ordered_selection}
            subtree_paths_set = set(files_in_subtree)

            # If all files in the folder are already selected, remove them. Otherwise, add them.
            if subtree_paths_set.issubset(current_selection_paths):
                self.parent.selection_handler.remove_files(files_in_subtree)
            else:
                # Only add files that are not already in the selection
                paths_to_add = [p for p in files_in_subtree if p not in current_selection_paths]
                self.parent.selection_handler.add_files(paths_to_add)