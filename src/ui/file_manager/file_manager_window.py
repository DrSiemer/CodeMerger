import os
from tkinter import Toplevel, messagebox

from ...core.utils import parse_gitignore
from .file_tree_builder import build_file_tree_data
from ...core.merger import recalculate_token_count
from .file_tree_handler import FileTreeHandler
from .selection_list_handler import SelectionListHandler
from .ui_setup import setup_file_manager_ui
from ... import constants as c
from ...core.paths import ICON_PATH
from ..window_utils import position_window, save_window_geometry

class FileManagerWindow(Toplevel):
    def __init__(self, parent, project_config, status_var, file_extensions, default_editor, newly_detected_files=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.project_config = project_config
        self.base_dir = self.project_config.base_dir
        self.status_var = status_var
        self.file_extensions = file_extensions
        self.default_editor = default_editor
        self.newly_detected_files = newly_detected_files or []

        self.title(f"Manage files for: {self.project_config.project_name}")
        self.iconbitmap(ICON_PATH)
        self.geometry("1000x700")
        self.minsize(600, 200)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

        self._recalculate_job = None
        self.current_total_tokens = self.project_config.total_tokens

        files_were_cleaned = self.project_config.load()
        if files_were_cleaned:
            self.status_var.set("Cleaned missing files from .allcode")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Escape>', lambda e: self.on_closing())

        self.gitignore_patterns = parse_gitignore(self.base_dir)

        # Build UI and then create handlers
        setup_file_manager_ui(self)
        self.create_handlers()

        # Populate with initial data
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.populate_tree()
        self.update_all_button_states()
        self._update_title(self.project_config.total_tokens)

        # Recalculate if files were cleaned OR if the token count is zero despite having files
        if files_were_cleaned or (self.current_total_tokens == 0 and self.project_config.selected_files):
            self.trigger_recalculation()

        self._position_window()
        self.deiconify()

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def create_handlers(self):
        """Instantiates and connects the UI handlers"""
        self.item_map = {}
        self.path_to_item_id = {}

        listbox_buttons = {
            'top': self.move_to_top_button,
            'up': self.move_up_button,
            'remove': self.remove_button,
            'down': self.move_down_button,
            'bottom': self.move_to_bottom_button
        }
        self.selection_handler = SelectionListHandler(self, self.merge_order_list, listbox_buttons, self.base_dir, self.default_editor, self.on_selection_list_changed)

        self.tree_handler = FileTreeHandler(
            parent=self,
            tree_widget=self.tree,
            action_button=self.tree_action_button,
            item_map=self.item_map,
            path_to_item_id=self.path_to_item_id,
            is_selected_callback=lambda path: path in self.selection_handler.ordered_selection,
            on_toggle_callback=self.on_file_toggled
        )
        self.tree_action_button.command = self.tree_handler.toggle_selection_for_selected
        self.move_to_top_button.command = self.selection_handler.move_to_top
        self.move_up_button.command = self.selection_handler.move_up
        self.move_down_button.command = self.selection_handler.move_down
        self.move_to_bottom_button.command = self.selection_handler.move_to_bottom
        self.remove_button.command = self.selection_handler.remove_selected

    def populate_tree(self):
        """Populates the treeview using data from the file_tree_builder"""
        tree_data = build_file_tree_data(self.base_dir, self.file_extensions, self.gitignore_patterns)

        def _insert_nodes(parent_id, nodes):
            for node in nodes:
                if node['type'] == 'dir':
                    is_open = node['path'] in self.project_config.expanded_dirs
                    dir_id = self.tree.insert(parent_id, 'end', text=node['name'], open=is_open)
                    self.item_map[dir_id] = {'path': node['path'], 'type': 'dir'}
                    self.path_to_item_id[node['path']] = dir_id
                    _insert_nodes(dir_id, node.get('children', []))
                elif node['type'] == 'file':
                    tags = ('file',)
                    if node['path'] in self.newly_detected_files:
                        tags += ('new_file_highlight',)
                    item_id = self.tree.insert(parent_id, 'end', text=f" {node['name']}", tags=tags)
                    self.item_map[item_id] = {'path': node['path'], 'type': 'file'}
                    self.path_to_item_id[node['path']] = item_id
                    self.tree_handler.update_checkbox_display(item_id)
        _insert_nodes('', tree_data)

    def on_selection_list_changed(self):
        """Callback from SelectionListHandler when its data changes"""
        self.tree_handler.update_all_checkboxes()
        self.update_all_button_states()
        self.trigger_recalculation()

    def on_file_toggled(self, path):
        """Callback from FileTreeHandler when a file is toggled"""
        self.selection_handler.toggle_file(path)
        self.tree_handler.update_checkbox_display(self.path_to_item_id.get(path))
        self.update_all_button_states()
        self.sync_highlights()
        # The selection_handler's toggle_file already triggers recalculation

    def handle_tree_select(self, event):
        """Coordinates actions when the tree selection changes"""
        if not self.tree.selection(): return # Event can fire on deselection
        self.merge_order_list.selection_clear(0, 'end')
        self.sync_highlights()
        self.update_all_button_states()

    def handle_list_select(self, event):
        """Coordinates actions when the listbox selection changes"""
        if not self.merge_order_list.curselection(): return # Event can fire on deselection
        self.tree.selection_set("")
        self.sync_highlights()
        self.update_all_button_states()

    def update_all_button_states(self):
        """Updates the state of all buttons based on current selections"""
        self.tree_handler.update_action_button_state()
        self.selection_handler.update_button_states()

    def sync_highlights(self):
        # Clear existing highlights from both lists
        for i in range(self.selection_handler.listbox.size()):
            self.selection_handler.listbox.itemconfig(i, {'bg': c.TEXT_INPUT_BG, 'fg': c.TEXT_COLOR})
        for item_id in self.tree.tag_has('subtle_highlight'):
            self.tree.item(item_id, tags=('file',))

        selected_path = None
        if self.tree.selection():
            item_id = self.tree.selection()[0]
            if self.item_map.get(item_id, {}).get('type') == 'file':
                selected_path = self.item_map[item_id]['path']
        elif self.merge_order_list.curselection():
            selected_index = self.merge_order_list.curselection()[0]
            if 0 <= selected_index < len(self.selection_handler.ordered_selection):
                selected_path = self.selection_handler.ordered_selection[selected_index]

        if not selected_path: return

        # Apply new highlight
        if self.tree.selection():
            try:
                list_index = self.selection_handler.ordered_selection.index(selected_path)
                self.selection_handler.listbox.itemconfig(list_index, {'bg': c.SUBTLE_HIGHLIGHT_COLOR, 'fg': c.TEXT_COLOR})
            except ValueError: pass
        elif self.merge_order_list.curselection():
            if selected_path in self.path_to_item_id:
                item_id = self.path_to_item_id[selected_path]
                self.tree.item(item_id, tags=('file', 'subtle_highlight'))
                self.tree.see(item_id)

    def trigger_recalculation(self):
        if self._recalculate_job: self.after_cancel(self._recalculate_job)
        self._recalculate_job = self.after(250, self.run_token_recalculation)

    def run_token_recalculation(self):
        self._recalculate_job = None
        total_tokens = recalculate_token_count(self.base_dir, self.selection_handler.ordered_selection)
        self._update_title(total_tokens)

    def _update_title(self, total_tokens):
        self.current_total_tokens = total_tokens
        num_files = len(self.selection_handler.ordered_selection)
        file_text = "files" if num_files != 1 else "file"
        if total_tokens >= 0:
            formatted_tokens = f"{total_tokens:,}".replace(',', '.')
            details_text = f"({num_files} {file_text} selected, {formatted_tokens} tokens)"
        else:
            details_text = f"({num_files} {file_text} selected, token count error)"
        self.merge_order_details_label.config(text=details_text)

    def select_all_files(self):
        all_paths = self.tree_handler.get_all_file_paths_in_tree_order()
        paths_to_add = [p for p in all_paths if p not in self.selection_handler.ordered_selection]
        if paths_to_add:
            self.selection_handler.add_files(paths_to_add)
            self.status_var.set(f"Added {len(paths_to_add)} file(s) to the merge list")
        else:
            self.status_var.set("No new files to add")

    def remove_all_files(self):
        if not self.selection_handler.ordered_selection:
            self.status_var.set("Merge list is already empty")
            return
        if messagebox.askyesno("Confirm Removal", "Are you sure you want to remove all files from the merge list?", parent=self):
            removed_count = len(self.selection_handler.ordered_selection)
            self.selection_handler.remove_all_files()
            self.status_var.set(f"Removed {removed_count} file(s) from the merge list")

    def _is_state_changed(self):
        """Compares current state to the last saved state"""
        # Compare list of selected files (order matters)
        if self.selection_handler.ordered_selection != self.project_config.selected_files:
            return True

        # Compare set of expanded directories
        current_expanded_dirs = set(self.tree_handler.get_expanded_dirs())
        if current_expanded_dirs != self.project_config.expanded_dirs:
            return True

        return False

    def on_closing(self):
        """Handles the window close event, checking for unsaved changes"""
        if self._is_state_changed():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before closing?",
                parent=self
            )
            if response is True:  # Yes, save
                self.save_and_close()
            elif response is False:  # No, discard
                self._close_and_save_geometry()
            # On Cancel (response is None), do nothing
        else:
            self._close_and_save_geometry()

    def save_and_close(self):
        self.project_config.selected_files = self.selection_handler.ordered_selection
        self.project_config.expanded_dirs = set(self.tree_handler.get_expanded_dirs())
        self.project_config.total_tokens = self.current_total_tokens
        self.project_config.known_files = list(set(self.project_config.known_files + self.selection_handler.ordered_selection))
        self.project_config.save()
        self.status_var.set("File selection and order saved to .allcode")
        self._close_and_save_geometry()