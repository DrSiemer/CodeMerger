import os
import time

class FileTreeHandler:
    """
    Manages the file tree view in the FileManagerWindow, including population,
    event handling, and visual state
    """
    def __init__(self, parent, tree_widget, action_button, item_map, path_to_item_id, is_selected_callback, on_toggle_callback):
        self.parent = parent
        self.tree = tree_widget
        self.action_button = action_button
        self.item_map = item_map
        self.path_to_item_id = path_to_item_id
        self.is_selected = is_selected_callback
        self.on_toggle = on_toggle_callback

        self.last_tree_click_time = 0
        self.last_clicked_item_id = None

        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<Return>', self.toggle_selection_for_selected) # For accessibility
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.tree.bind("<Button-1>", self.handle_tree_deselection_click, add='+')

    def get_expanded_dirs(self):
        """Returns a list of currently expanded directories"""
        return [
            info['path'] for item_id, info in self.item_map.items()
            if info.get('type') == 'dir' and self.tree.item(item_id, 'open')
        ]

    def update_checkbox_display(self, item_id):
        """Updates the text of a tree item to show a checked or unchecked box"""
        item_info = self.item_map.get(item_id, {})
        if item_info.get('type') != 'file':
            return

        path = item_info['path']
        is_checked = self.is_selected(path)
        check_char = "☑" if is_checked else "☐"
        self.tree.item(item_id, text=f"{check_char} {os.path.basename(path)}")

    def update_all_checkboxes(self):
        """Iterates through all file items and updates their checkbox state"""
        for item_id, info in self.item_map.items():
            if info.get('type') == 'file':
                self.update_checkbox_display(item_id)

    def handle_tree_deselection_click(self, event):
        """Deselects a tree item if a click occurs in an empty area"""
        if not self.tree.identify_row(event.y) and self.tree.selection():
            self.tree.selection_set("")

    def on_tree_selection_change(self, event=None):
        """Callback for when the tree selection changes"""
        self.parent.handle_tree_select(event)

    def update_action_button_state(self):
        """Updates the state and text of the button under the treeview"""
        selection = self.tree.selection()
        if not selection:
            self.action_button.config(state='disabled', text="Add to Merge List")
            return

        item_id = selection[0]
        item_info = self.item_map.get(item_id, {})
        if item_info.get('type') != 'file':
            self.action_button.config(state='disabled', text="Add to Merge List")
            return

        self.action_button.config(state='normal')
        if self.is_selected(item_info['path']):
            self.action_button.config(text="Remove from Merge List")
        else:
            self.action_button.config(text="Add to Merge List")

    def handle_tree_click(self, event):
        """Detects a double-click on the same treeview item"""
        item_id = self.tree.identify_row(event.y)
        current_time = time.time()
        time_diff = current_time - self.last_tree_click_time

        if time_diff < 0.4 and item_id and item_id == self.last_clicked_item_id:
            self.toggle_selection_for_selected()
            self.last_tree_click_time = 0
            self.last_clicked_item_id = None
        else:
            self.last_tree_click_time = current_time
            self.last_clicked_item_id = item_id

    def toggle_selection_for_selected(self, event=None):
        """Adds or removes the selected file from the merge list via the callback"""
        selection = self.tree.selection()
        if not selection: return "break"

        item_id = selection[0]
        item_info = self.item_map.get(item_id, {})
        if item_info.get('type') != 'file': return "break"

        self.on_toggle(item_info['path'])
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