import os
import json
import time
from tkinter import Toplevel, Frame, Label, Button, Listbox, messagebox
from tkinter import ttk

from .utils import parse_gitignore, is_ignored
from .constants import SUBTLE_HIGHLIGHT_COLOR

# --- File Manager Window Class ---
class FileManagerWindow(Toplevel):
    def __init__(self, parent, base_dir, status_var, file_extensions):
        super().__init__(parent)

        self.base_dir = base_dir
        self.status_var = status_var
        self.file_extensions = file_extensions

        self.title(f"Manage files for: {os.path.basename(self.base_dir)}")
        self.geometry("850x700")
        self.transient(parent)
        self.grab_set()

        # Used to differentiate single and double clicks on the tree
        self.last_tree_click_time = 0

        self.allcode_path = os.path.join(self.base_dir, '.allcode')
        self.load_allcode_config()
        self.gitignore_patterns = parse_gitignore(self.base_dir)

        # --- UI Layout ---
        main_frame = Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left side for available files tree
        left_frame = Frame(main_frame, width=400)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        left_frame.pack_propagate(False)

        # Right side for selected files list
        right_frame = Frame(main_frame, width=400)
        right_frame.pack(side='left', fill='both', expand=True, padx=(5, 0))
        right_frame.pack_propagate(False)

        # --- Available Files Tree (Left) ---
        Label(left_frame, text="Available Files").pack(anchor='w')

        tree_frame = Frame(left_frame)
        tree_frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(tree_frame, show='tree')
        self.tree.pack(side='left', fill='both', expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        tree_scroll.pack(side='right', fill='y')
        self.tree.config(yscrollcommand=tree_scroll.set)

        self.tree.tag_configure('subtle_highlight', background=SUBTLE_HIGHLIGHT_COLOR)

        # --- Merge Order List (Right) ---
        Label(right_frame, text="Merge Order (Top to Bottom)").pack(anchor='w')

        list_frame = Frame(right_frame)
        list_frame.pack(fill='both', expand=True)

        self.merge_order_list = Listbox(list_frame, activestyle='none')
        self.merge_order_list.pack(side='left', fill='both', expand=True)

        list_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.merge_order_list.yview)
        list_scroll.pack(side='right', fill='y')
        self.merge_order_list.config(yscrollcommand=list_scroll.set)

        move_buttons_frame = Frame(right_frame)
        move_buttons_frame.pack(fill='x', pady=5)

        Button(move_buttons_frame, text="↑ Move Up", command=self.move_up).pack(side='left', expand=True)
        Button(move_buttons_frame, text="↓ Move Down", command=self.move_down).pack(side='left', expand=True)

        # --- Main Action Button ---
        Button(self, text="Save and Close", command=self.save_and_close).pack(pady=10)

        # --- Bindings ---
        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<Return>', self.toggle_selection_for_selected) # For accessibility
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.merge_order_list.bind('<<ListboxSelect>>', self.on_list_selection_change)
        self.merge_order_list.bind('<Double-1>', self.open_selected_file)

        # --- Initial Population ---
        self.item_map = {}
        self.path_to_item_id = {}
        self.populate_tree()
        self.update_listbox_from_data()

    def load_allcode_config(self):
        self.ordered_selection = []
        self.expanded_dirs = set()

        if not os.path.isfile(self.allcode_path):
            return

        with open(self.allcode_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                self.ordered_selection = data.get('selected_files', [])
                self.expanded_dirs = set(data.get('expanded_dirs', []))
            except json.JSONDecodeError:
                # Handle corrupted .allcode file
                self.ordered_selection = []
                self.expanded_dirs = set()

    def populate_tree(self):
        def _has_relevant_files(path):
            """Recursively checks if a directory contains any files matching the extension list."""
            for entry in os.scandir(path):
                if is_ignored(entry.path, self.base_dir, self.gitignore_patterns) or entry.name == 'allcode.txt':
                    continue
                if entry.is_dir():
                    if _has_relevant_files(entry.path):
                        return True
                elif entry.is_file() and os.path.splitext(entry.name)[1].lower() in self.file_extensions:
                    return True
            return False

        def _walk_dir(parent_id, path):
            """Walks a directory and adds its contents to the treeview."""
            try:
                # Sort entries to show folders first, then files, all alphabetically
                entries = sorted(os.scandir(path), key=lambda e: (e.is_file(), e.name.lower()))
            except OSError:
                return # Can't access directory

            for entry in entries:
                if is_ignored(entry.path, self.base_dir, self.gitignore_patterns) or entry.name == 'allcode.txt':
                    continue

                rel_path = os.path.relpath(entry.path, self.base_dir).replace('\\', '/')

                if entry.is_dir():
                    if _has_relevant_files(entry.path):
                        is_open = rel_path in self.expanded_dirs
                        dir_id = self.tree.insert(parent_id, 'end', text=entry.name, open=is_open)
                        self.item_map[dir_id] = {'path': rel_path, 'type': 'dir'}
                        self.path_to_item_id[rel_path] = dir_id
                        _walk_dir(dir_id, entry.path)
                elif entry.is_file() and os.path.splitext(entry.name)[1].lower() in self.file_extensions:
                    item_id = self.tree.insert(parent_id, 'end', text=f" {entry.name}", tags=('file',))
                    self.item_map[item_id] = {'path': rel_path, 'type': 'file'}
                    self.path_to_item_id[rel_path] = item_id
                    self.update_checkbox_display(item_id)

        _walk_dir('', self.base_dir)

    def on_tree_selection_change(self, event):
        """When a tree item is selected, deselect any listbox item and sync highlights."""
        if self.tree.selection():
            self.merge_order_list.selection_clear(0, 'end')
            self.sync_highlights()

    def on_list_selection_change(self, event):
        """When a listbox item is selected, deselect any tree item and sync highlights."""
        if self.merge_order_list.curselection():
            if self.tree.selection():
                self.tree.selection_set("")
            self.sync_highlights()

    def sync_highlights(self):
        """Highlights the corresponding item in the other list when one is selected."""
        self.clear_all_subtle_highlights()

        selected_path = None
        tree_selection = self.tree.selection()
        list_selection = self.merge_order_list.curselection()

        if tree_selection:
            item_id = tree_selection[0]
            if self.item_map.get(item_id, {}).get('type') == 'file':
                selected_path = self.item_map[item_id]['path']
        elif list_selection:
            selected_path = self.merge_order_list.get(list_selection[0])

        if not selected_path:
            return

        if tree_selection:
            # Highlight in listbox
            try:
                list_index = self.ordered_selection.index(selected_path)
                self.merge_order_list.itemconfig(list_index, {'bg': SUBTLE_HIGHLIGHT_COLOR})
            except ValueError:
                pass # Not in the selected list
        elif list_selection:
            # Highlight in treeview
            if selected_path in self.path_to_item_id:
                item_id = self.path_to_item_id[selected_path]
                self.tree.item(item_id, tags=('file', 'subtle_highlight'))
                self.tree.see(item_id) # Ensure the item is visible

    def clear_all_subtle_highlights(self):
        """Removes all custom background highlights from both lists."""
        for i in range(self.merge_order_list.size()):
            self.merge_order_list.itemconfig(i, {'bg': 'white'}) # Default listbox color

        for item_id in self.tree.tag_has('subtle_highlight'):
            self.tree.item(item_id, tags=('file',))

    def handle_tree_click(self, event):
        """Detects a double-click on the treeview to toggle file selection."""
        current_time = time.time()
        time_diff = current_time - self.last_tree_click_time
        self.last_tree_click_time = current_time

        # A simple time-based double-click detection
        if time_diff < 0.4:
            self.toggle_selection_for_selected()
            self.last_tree_click_time = 0 # Reset timer to prevent triple-clicks

    def update_checkbox_display(self, item_id):
        """Updates the text of a tree item to show a checked or unchecked box."""
        if self.item_map.get(item_id, {}).get('type') != 'file':
            return

        path = self.item_map[item_id]['path']
        is_checked = path in self.ordered_selection
        check_char = "☑" if is_checked else "☐"

        self.tree.item(item_id, text=f"{check_char} {os.path.basename(path)}")

    def toggle_selection_for_selected(self, event=None):
        """Adds or removes the selected file from the merge list."""
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        if self.item_map.get(item_id, {}).get('type') != 'file':
            return

        path = self.item_map[item_id]['path']
        if path in self.ordered_selection:
            self.ordered_selection.remove(path)
        else:
            self.ordered_selection.append(path)

        self.update_checkbox_display(item_id)
        self.update_listbox_from_data()
        self.sync_highlights()
        return "break" # Prevents further event processing

    def open_selected_file(self, event=None):
        """Opens the selected file in the system's default editor."""
        selection = self.merge_order_list.curselection()
        if not selection:
            return

        relative_path = self.merge_order_list.get(selection[0])
        full_path = os.path.join(self.base_dir, relative_path)

        if not os.path.isfile(full_path):
            messagebox.showwarning(
                "File Not Found",
                f"The file '{relative_path}' could not be found.",
                parent=self
            )
            return

        try:
            os.startfile(full_path)
        except AttributeError:
            # os.startfile is Windows-specific. Provide a fallback for other OS.
            messagebox.showinfo(
                "Unsupported Action",
                "Opening files is only supported on Windows.",
                parent=self
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}", parent=self)

    def update_listbox_from_data(self):
        """Refreshes the merge order listbox with the current selection."""
        # Preserve selection if possible
        selection = self.merge_order_list.curselection()

        self.merge_order_list.delete(0, 'end')

        for path in self.ordered_selection:
            self.merge_order_list.insert('end', path)

        if selection and selection[0] < self.merge_order_list.size():
            self.merge_order_list.select_set(selection[0])

    def move_up(self):
        """Moves the selected item up in the merge order list."""
        selection = self.merge_order_list.curselection()
        if not selection:
            return

        index = selection[0]
        if index > 0:
            # Rearrange in the data list
            path = self.ordered_selection.pop(index)
            self.ordered_selection.insert(index - 1, path)

            # Rearrange in the UI list
            self.merge_order_list.delete(index)
            self.merge_order_list.insert(index - 1, path)
            self.merge_order_list.select_set(index - 1)
            self.sync_highlights()

    def move_down(self):
        """Moves the selected item down in the merge order list."""
        selection = self.merge_order_list.curselection()
        if not selection:
            return

        index = selection[0]
        if index < len(self.ordered_selection) - 1:
            # Rearrange in the data list
            path = self.ordered_selection.pop(index)
            self.ordered_selection.insert(index + 1, path)

            # Rearrange in the UI list
            self.merge_order_list.delete(index)
            self.merge_order_list.insert(index + 1, path)
            self.merge_order_list.select_set(index + 1)
            self.sync_highlights()

    def save_and_close(self):
        """Saves the selection and order to .allcode and closes the window."""
        # Get a list of currently expanded directories to save their state
        expanded_dirs = sorted([
            info['path'] for item_id, info in self.item_map.items()
            if info.get('type') == 'dir' and self.tree.item(item_id, 'open')
        ])

        data_to_save = {
            "selected_files": self.ordered_selection,
            "expanded_dirs": expanded_dirs,
        }

        with open(self.allcode_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2)

        self.status_var.set("File selection and order saved to .allcode")
        self.destroy()