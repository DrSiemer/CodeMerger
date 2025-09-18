import os
import tkinter as tk
from tkinter import Toplevel, messagebox

from ...core.utils import parse_gitignore, get_file_hash, get_token_count_for_text
from .file_tree_builder import build_file_tree_data
from .file_tree_handler import FileTreeHandler
from .selection_list_handler import SelectionListHandler
from .ui_setup import setup_file_manager_ui
from ... import constants as c
from ...core.paths import ICON_PATH
from ..window_utils import position_window, save_window_geometry
from ..assets import assets

class FileManagerWindow(Toplevel):
    def __init__(self, parent, project_config, status_var, file_extensions, default_editor, app_state, newly_detected_files=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.project_config = project_config
        self.base_dir = self.project_config.base_dir
        self.status_var = status_var
        self.file_extensions = file_extensions
        self.default_editor = default_editor
        self.app_state = app_state
        self.newly_detected_files = newly_detected_files or []
        self.full_paths_visible = False
        self.token_count_enabled = self.app_state.config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT)

        self.title(f"Manage files for: {self.project_config.project_name}")
        self.iconbitmap(ICON_PATH)
        self.geometry("1000x700")
        self.minsize(600, 200)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

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

        # Validate cache before populating UI
        self._validate_and_update_cache()

        # Populate with initial data
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.populate_tree()
        self.run_token_recalculation() # Update title from validated cache
        self.update_all_button_states()

        self._position_window()
        self.deiconify()

    def toggle_full_path_view(self):
        """Toggles full path visibility and resizes the columns."""
        self.full_paths_visible = not self.full_paths_visible

        # Tell the selection list handler to update its view
        self.selection_handler.toggle_full_path_view()

        # Update column weights and button image
        if self.full_paths_visible:
            # Give merge order list more space
            self.tree.master.grid_columnconfigure(0, weight=1)
            self.tree.master.grid_columnconfigure(2, weight=2)
            self.toggle_paths_button.config(image=assets.paths_icon_active)
        else:
            # Reset to equal space
            self.tree.master.grid_columnconfigure(0, weight=1)
            self.tree.master.grid_columnconfigure(2, weight=1)
            self.toggle_paths_button.config(image=assets.paths_icon)

    def _validate_and_update_cache(self):
        """
        Checks for file modifications by comparing mtime/hash or missing keys, then updates
        the token/line cache for any changed files. Also re-validates files with 0 tokens
        if token counting is enabled.
        """
        cache_was_updated = False
        for file_info in self.project_config.selected_files:
            path = file_info.get('path')
            if not path: continue

            full_path = os.path.join(self.base_dir, path)
            recalculate = False

            # --- Determine if a recalculation is needed ---
            # Reason 1: Essential data is missing from the cache.
            if 'tokens' not in file_info or 'lines' not in file_info:
                recalculate = True
            # Reason 2: Token counting is ON, but the cached value is 0. This is suspicious
            # unless the file is genuinely empty.
            elif self.token_count_enabled and file_info.get('tokens', -1) == 0:
                try:
                    if os.path.getsize(full_path) > 0:
                        recalculate = True
                except OSError:
                    continue # File might have been deleted, skip.
            else:
                try:
                    current_mtime = os.path.getmtime(full_path)
                    # Reason 3: Modification time has changed.
                    if current_mtime != file_info.get('mtime'):
                        recalculate = True
                    # Reason 4: mtime is the same, but hash has changed (covers fast saves).
                    else:
                        current_hash = get_file_hash(full_path)
                        if current_hash is not None and current_hash != file_info.get('hash'):
                            recalculate = True
                except OSError:
                    continue # Skip inaccessible files.

            # --- Perform recalculation if needed ---
            if recalculate:
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    file_info['mtime'] = os.path.getmtime(full_path)
                    file_info['hash'] = get_file_hash(full_path)

                    if self.token_count_enabled:
                        file_info['tokens'] = get_token_count_for_text(content)
                        file_info['lines'] = content.count('\n') + 1
                    else:
                        file_info['tokens'] = 0
                        file_info['lines'] = 0
                    cache_was_updated = True
                except (OSError, IOError):
                    # If file is unreadable now, mark stats as invalid
                    file_info['tokens'] = -1
                    file_info['lines'] = -1
                    cache_was_updated = True

        if cache_was_updated:
            self.project_config.save() # Save the updated cache to .allcode
            self.status_var.set("File cache updated for modified files.")

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
        self.selection_handler = SelectionListHandler(
            self, self.merge_order_list, listbox_buttons, self.base_dir, self.default_editor,
            self.on_selection_list_changed,
            token_count_enabled=self.token_count_enabled
        )

        self.tree_handler = FileTreeHandler(
            parent=self,
            tree_widget=self.tree,
            action_button=self.tree_action_button,
            item_map=self.item_map,
            path_to_item_id=self.path_to_item_id,
            is_selected_callback=lambda path: path in [f['path'] for f in self.selection_handler.ordered_selection],
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
        self.run_token_recalculation()

    def on_file_toggled(self, path):
        """Callback from FileTreeHandler when a file is toggled"""
        self.selection_handler.toggle_file(path)
        self.tree_handler.update_checkbox_display(self.path_to_item_id.get(path))
        self.update_all_button_states()
        self.sync_highlights()

    def handle_tree_select(self, event):
        """Coordinates actions when the tree selection changes"""
        if not self.tree.selection(): return
        self.merge_order_list.clear_selection()
        self.sync_highlights()
        self.update_all_button_states()

    def handle_merge_order_tree_select(self, event):
        """Coordinates actions when the listbox selection changes"""
        if not self.merge_order_list.curselection(): return
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.sync_highlights()
        self.update_all_button_states()

    def update_all_button_states(self):
        """Updates the state of all buttons based on current selections"""
        self.tree_handler.update_action_button_state()
        self.selection_handler.update_button_states()

    def sync_highlights(self):
        # Clear existing highlights from both lists
        for item_id in self.tree.tag_has('subtle_highlight'):
            self.tree.item(item_id, tags=('file',))
        self.merge_order_list.clear_highlights()

        selected_path = None
        source_widget = None

        if self.tree.selection():
            item_id = self.tree.selection()[0]
            if self.item_map.get(item_id, {}).get('type') == 'file':
                selected_path = self.item_map[item_id]['path']
                source_widget = self.tree
        elif self.merge_order_list.curselection():
            selected_index = self.merge_order_list.curselection()[0]
            selected_path = self.merge_order_list.get_item_data(selected_index)
            source_widget = self.merge_order_list

        if not selected_path: return

        # Apply new highlight to the *other* widget
        if source_widget == self.tree:
            try:
                paths_only = [f['path'] for f in self.selection_handler.ordered_selection]
                list_index = paths_only.index(selected_path)
                self.merge_order_list.highlight_item(list_index)
            except ValueError: pass # Item not in merge list
        elif source_widget == self.merge_order_list:
            if selected_path in self.path_to_item_id:
                item_id = self.path_to_item_id[selected_path]
                self.tree.item(item_id, tags=('file', 'subtle_highlight'))
                self.tree.see(item_id)

    def run_token_recalculation(self):
        # Calculate total by summing cached values
        if self.token_count_enabled:
            total_tokens = sum(f.get('tokens', 0) for f in self.selection_handler.ordered_selection)
            self._update_title(total_tokens)
        else:
            self._update_title(None)

    def _update_title(self, total_tokens):
        num_files = len(self.selection_handler.ordered_selection)
        file_text = "files" if num_files != 1 else "file"

        if total_tokens is not None:
            self.current_total_tokens = total_tokens
            if total_tokens >= 0:
                formatted_tokens = f"{total_tokens:,}".replace(',', '.')
                details_text = f"({num_files} {file_text} selected, {formatted_tokens} tokens)"
            else:
                details_text = f"({num_files} {file_text} selected, token count error)"
        else:
            self.current_total_tokens = 0
            details_text = f"({num_files} {file_text} selected)"

        self.merge_order_details_label.config(text=details_text)

    def select_all_files(self):
        all_paths = self.tree_handler.get_all_file_paths_in_tree_order()
        current_selection_paths = {f['path'] for f in self.selection_handler.ordered_selection}
        paths_to_add = [p for p in all_paths if p not in current_selection_paths]

        if not paths_to_add:
            self.status_var.set("No new files to add")
            return

        num_files_to_add = len(paths_to_add)
        warning_threshold = self.app_state.config.get('add_all_warning_threshold', c.ADD_ALL_WARNING_THRESHOLD_DEFAULT)

        if num_files_to_add > warning_threshold:
            proceed = messagebox.askyesno(
                "Confirm Adding Files",
                f"You are about to add {num_files_to_add} files to the merge list.\n\nAre you sure you want to continue?",
                parent=self
            )
            if not proceed:
                self.status_var.set("Operation cancelled by user.")
                return

        self.selection_handler.add_files(paths_to_add)
        self.status_var.set(f"Added {num_files_to_add} file(s) to the merge list")

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
        if self.selection_handler.ordered_selection != self.project_config.selected_files:
            return True

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
            if response is True:
                self.save_and_close()
            elif response is False:
                self._close_and_save_geometry()
        else:
            self._close_and_save_geometry()

    def save_and_close(self):
        self.project_config.selected_files = self.selection_handler.ordered_selection
        self.project_config.expanded_dirs = set(self.tree_handler.get_expanded_dirs())
        self.project_config.total_tokens = self.current_total_tokens
        current_selection_paths = {f['path'] for f in self.selection_handler.ordered_selection}
        self.project_config.known_files = list(set(self.project_config.known_files) | current_selection_paths)
        self.project_config.save()
        self.status_var.set("File selection and order saved to .allcode")
        self._close_and_save_geometry()