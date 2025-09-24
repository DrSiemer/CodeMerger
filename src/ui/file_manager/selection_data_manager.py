import os
from tkinter import messagebox
from ...core.utils import get_file_hash, get_token_count_for_text

class SelectionDataManager:
    def __init__(self, base_dir, token_count_enabled, parent_for_errors):
        self.base_dir = base_dir
        self.token_count_enabled = token_count_enabled
        self.parent = parent_for_errors
        self.ordered_selection = []

    def _calculate_stats_for_file(self, path):
        """Reads a file and returns its stats, or None on error."""
        full_path = os.path.join(self.base_dir, path)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            mtime = os.path.getmtime(full_path)
            file_hash = get_file_hash(full_path)

            if self.token_count_enabled:
                tokens = get_token_count_for_text(content)
                lines = content.count('\n') + 1
            else:
                tokens, lines = 0, 0

            if file_hash is not None:
                return {'path': path, 'mtime': mtime, 'hash': file_hash, 'tokens': tokens, 'lines': lines}
        except OSError:
            messagebox.showerror("Error", f"Could not access file: {path}", parent=self.parent)
        return None

    def set_initial_selection(self, selection_list):
        self.ordered_selection = list(selection_list)

    def toggle_file(self, path):
        """Adds or removes a file from the selection model"""
        current_selection_paths = {f['path'] for f in self.ordered_selection}
        if path in current_selection_paths:
            self.ordered_selection = [f for f in self.ordered_selection if f['path'] != path]
        else:
            new_entry = self._calculate_stats_for_file(path)
            if new_entry:
                self.ordered_selection.append(new_entry)

    def add_files(self, paths_to_add):
        current_selection_paths = {f['path'] for f in self.ordered_selection}
        for path in paths_to_add:
            if path not in current_selection_paths:
                new_entry = self._calculate_stats_for_file(path)
                if new_entry:
                    self.ordered_selection.append(new_entry)

    def remove_all(self):
        self.ordered_selection.clear()

    def remove_by_indices(self, indices):
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]

    def reorder_move_to_top(self, indices):
        moved_items = [self.ordered_selection[i] for i in indices]
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]
        self.ordered_selection = moved_items + self.ordered_selection
        return range(len(moved_items))

    def reorder_move_up(self, indices):
        if not indices or indices[0] == 0:
            return None
        moved_items = [self.ordered_selection[i] for i in indices]
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]
        insert_index = indices[0] - 1
        for i, item in enumerate(moved_items):
            self.ordered_selection.insert(insert_index + i, item)
        return range(insert_index, insert_index + len(moved_items))

    def reorder_move_down(self, indices):
        if not indices or indices[-1] >= len(self.ordered_selection) - 1:
            return None
        moved_items = [self.ordered_selection[i] for i in indices]
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]
        insert_index = indices[0] + 1
        for i, item in enumerate(moved_items):
            self.ordered_selection.insert(insert_index + i, item)
        return range(insert_index, insert_index + len(moved_items))

    def reorder_move_to_bottom(self, indices):
        moved_items = [self.ordered_selection[i] for i in indices]
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]
        new_start_index = len(self.ordered_selection)
        self.ordered_selection.extend(moved_items)
        return range(new_start_index, len(self.ordered_selection))