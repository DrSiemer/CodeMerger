import os
import sys
import subprocess
from tkinter import messagebox, Toplevel, Label
from ... import constants as c
from ...core.utils import get_file_hash

class SelectionListHandler:
    """
    Manages the 'Merge Order' listbox and its associated buttons,
    handling the data model (ordered_selection) and user actions.
    """
    def __init__(self, parent, list_widget, buttons, base_dir, default_editor, on_change_callback, line_count_enabled, line_count_threshold):
        self.parent = parent
        self.listbox = list_widget
        self.move_to_top_button = buttons['top']
        self.move_up_button = buttons['up']
        self.remove_button = buttons['remove']
        self.move_down_button = buttons['down']
        self.move_to_bottom_button = buttons['bottom']
        self.base_dir = base_dir
        self.default_editor = default_editor
        self.on_change = on_change_callback
        self.line_count_enabled = line_count_enabled
        self.line_count_threshold = line_count_threshold
        self.ordered_selection = []
        self.listbox.bind_event('<<ListSelectionChanged>>', self.on_list_selection_change)
        self.listbox.bind_event('<Double-1>', self.open_selected_file)

    def set_initial_selection(self, selection_list):
        self.ordered_selection = list(selection_list)
        self.update_listbox_from_data()

    def update_listbox_from_data(self):
        """
        Refreshes the merge order list, handling line counts, coloring,
        and font styles based on user settings.
        """
        display_items = []
        color_map = {}
        # --- Prepare data for display ---
        if self.line_count_enabled:
            file_details = []
            for file_info in self.ordered_selection:
                path = file_info['path']
                line_count = 0
                try:
                    with open(os.path.join(self.base_dir, path), 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = len(f.readlines())
                except (IOError, OSError):
                    line_count = -1
                file_details.append({'path': path, 'line_count': line_count})
            # Determine color tags for top 3 longest files
            ranked_files = sorted(
                [f for f in file_details if f['line_count'] >= self.line_count_threshold],
                key=lambda x: x['line_count'],
                reverse=True
            )
            if len(ranked_files) > 0: color_map[ranked_files[0]['path']] = c.WARN
            if len(ranked_files) > 1: color_map[ranked_files[1]['path']] = c.ATTENTION
            if len(ranked_files) > 2: color_map[ranked_files[2]['path']] = c.NOTE
        for file_info in self.ordered_selection:
            path = file_info['path']
            basename = os.path.basename(path)
            right_col_text = ""
            right_col_color = c.TEXT_SUBTLE_COLOR
            if self.line_count_enabled:
                data = next((item for item in file_details if item["path"] == path), None)
                if data:
                    line_count = data['line_count']
                    if line_count > self.line_count_threshold:
                        right_col_text = str(line_count)
                        if path in color_map:
                            right_col_color = color_map[path]
                    elif line_count == -1:
                        right_col_text = "?"
            display_items.append({
                'left': basename,
                'right': right_col_text,
                'right_fg': right_col_color,
                'data': path # Store original path for identification
            })
        self.listbox.set_items(display_items)

    def on_list_selection_change(self, event=None):
        """Callback for when the listbox selection changes"""
        self.parent.handle_merge_order_tree_select(event)

    def update_button_states(self):
        """Enables or disables the action buttons based on selection"""
        new_state = 'normal' if self.listbox.curselection() else 'disabled'
        self.move_to_top_button.config(state=new_state)
        self.move_up_button.config(state=new_state)
        self.remove_button.config(state=new_state)
        self.move_down_button.config(state=new_state)
        self.move_to_bottom_button.config(state=new_state)

    def toggle_file(self, path):
        """Adds or removes a file from the selection model"""
        current_selection_paths = {f['path'] for f in self.ordered_selection}
        if path in current_selection_paths:
            self.ordered_selection = [f for f in self.ordered_selection if f['path'] != path]
        else:
            full_path = os.path.join(self.base_dir, path)
            try:
                mtime = os.path.getmtime(full_path)
                file_hash = get_file_hash(full_path)
                if file_hash is not None:
                    new_entry = {'path': path, 'mtime': mtime, 'hash': file_hash}
                    self.ordered_selection.append(new_entry)
            except OSError:
                messagebox.showerror("Error", f"Could not access file: {path}", parent=self.parent)
                return
        self.update_listbox_from_data()
        self.on_change()

    def add_files(self, paths_to_add):
        current_selection_paths = {f['path'] for f in self.ordered_selection}
        for path in paths_to_add:
            if path not in current_selection_paths:
                full_path = os.path.join(self.base_dir, path)
                try:
                    mtime = os.path.getmtime(full_path)
                    file_hash = get_file_hash(full_path)
                    if file_hash is not None:
                        new_entry = {'path': path, 'mtime': mtime, 'hash': file_hash}
                        self.ordered_selection.append(new_entry)
                except OSError:
                    continue
        self.update_listbox_from_data()
        self.on_change()

    def remove_all_files(self):
        self.ordered_selection.clear()
        self.update_listbox_from_data()
        self.on_change()

    def move_to_top(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices: return
        moved_items = [self.ordered_selection[i] for i in selection_indices]
        for index in sorted(selection_indices, reverse=True):
            del self.ordered_selection[index]
        self.ordered_selection = moved_items + self.ordered_selection
        new_selection_indices = range(len(moved_items))
        self.update_listbox_from_data()
        self.listbox.selection_set(new_selection_indices[0], new_selection_indices[-1])
        self.listbox.see(new_selection_indices[0])
        self.on_change()

    def move_up(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices or selection_indices[0] == 0:
            return
        new_selection = []
        for i in sorted(selection_indices):
            target_index = i - 1
            # Swap the item with the one above it
            self.ordered_selection[i], self.ordered_selection[target_index] = self.ordered_selection[target_index], self.ordered_selection[i]
            new_selection.append(target_index)
        self.update_listbox_from_data()
        self.listbox.selection_set(new_selection[0], new_selection[-1])
        self.listbox.see(new_selection[0])
        self.on_change()

    def move_down(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices or selection_indices[-1] >= len(self.ordered_selection) - 1:
            return
        new_selection = []
        # Iterate backwards to prevent index issues when moving multiple items
        for i in sorted(selection_indices, reverse=True):
            target_index = i + 1
            self.ordered_selection[i], self.ordered_selection[target_index] = self.ordered_selection[target_index], self.ordered_selection[i]
            new_selection.insert(0, target_index) # Insert at beginning to keep order
        self.update_listbox_from_data()
        self.listbox.selection_set(new_selection[0], new_selection[-1])
        self.listbox.see(new_selection[-1])
        self.on_change()

    def move_to_bottom(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices: return
        moved_items = [self.ordered_selection[i] for i in selection_indices]
        for index in sorted(selection_indices, reverse=True):
            del self.ordered_selection[index]
        new_start_index = len(self.ordered_selection)
        self.ordered_selection.extend(moved_items)
        self.update_listbox_from_data()
        self.listbox.selection_set(new_start_index, len(self.ordered_selection) - 1)
        self.listbox.see(len(self.ordered_selection) - 1)
        self.on_change()

    def remove_selected(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices: return
        # Remove from data model by iterating backwards
        for index in sorted(selection_indices, reverse=True):
            del self.ordered_selection[index]
        self.update_listbox_from_data()
        self.on_change()

    def open_selected_file(self, event=None):
        selection_indices = self.listbox.curselection()
        if not selection_indices: return "break"
        # Get the data (full path) associated with the first selected item
        relative_path = self.listbox.get_item_data(selection_indices[0])
        if not relative_path: return "break"
        full_path = os.path.join(self.base_dir, relative_path)
        if not os.path.isfile(full_path):
            messagebox.showwarning("File Not Found", f"The file '{relative_path}' could not be found", parent=self.parent)
            return "break"
        try:
            if self.default_editor and os.path.isfile(self.default_editor):
                subprocess.Popen([self.default_editor, full_path])
            else:
                if sys.platform == "win32": os.startfile(full_path)
                elif sys.platform == "darwin": subprocess.call(['open', full_path])
                else: subprocess.call(['xdg-open', full_path])
        except (AttributeError, FileNotFoundError):
            messagebox.showinfo("Unsupported Action", "Could not open file with the system default\nPlease configure a default editor in Settings", parent=self.parent)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}", parent=self.parent)
        return "break"