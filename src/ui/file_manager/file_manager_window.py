import tkinter as tk
from tkinter import Toplevel, StringVar
from ...core.utils import parse_gitignore
from .file_tree_builder import build_file_tree_data
from .file_tree_handler import FileTreeHandler
from .selection_list_controller import SelectionListController
from .ui_setup import setup_file_manager_ui
from .ui_controller import FileManagerUIController
from .data_controller import FileManagerDataController
from .state_controller import FileManagerStateController
from .order_request_handler import OrderRequestHandler
from ... import constants as c
from ...core.paths import ICON_PATH
from ..window_utils import position_window, save_window_geometry
from ..custom_error_dialog import CustomErrorDialog

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
        self.is_extension_filter_active = True
        self.is_gitignore_filter_active = True
        self.hovered_file_path = None
        self.current_total_tokens = self.project_config.total_tokens
        self.sash_pos_normal = None
        self.window_geometries = {}

        self.title(f"Manage files for: {self.project_config.project_name}")
        self.iconbitmap(ICON_PATH)
        self.geometry(c.FILE_MANAGER_DEFAULT_GEOMETRY)
        self.minsize(c.FILE_MANAGER_MIN_WIDTH, c.FILE_MANAGER_MIN_HEIGHT)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

        if self.project_config.load():
            self.status_var.set("Cleaned missing files from .allcode")

        self.gitignore_patterns = parse_gitignore(self.base_dir)
        self.ui_controller = FileManagerUIController(self)
        self.data_controller = FileManagerDataController(self)
        self.state_controller = FileManagerStateController(self)
        self.order_request_handler = OrderRequestHandler(self)

        setup_file_manager_ui(self)
        self.create_handlers()

        self.filter_text = StringVar()
        self.filter_entry.config(textvariable=self.filter_text)
        self.filter_text.trace_add('write', self.ui_controller.apply_filter)
        self.clear_filter_button.bind("<Button-1>", self.ui_controller.clear_filter)

        self.protocol("WM_DELETE_WINDOW", self.state_controller.on_closing)
        self.bind('<Escape>', lambda e: self.state_controller.on_closing())
        self.tree.bind("<Motion>", self.ui_controller.on_tree_motion)
        self.tree.bind("<Leave>", self.ui_controller.on_tree_leave)

        self.data_controller.validate_and_update_cache()
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.populate_tree()
        self.data_controller.run_token_recalculation()
        self.update_all_button_states()

        self._position_window()
        self.deiconify()

        if self.newly_detected_files:
            self.ui_controller.expand_and_scroll_to_new_files()

    def show_error_dialog(self, title, message):
        # Instantiate the dialog with this window as the parent to keep focus.
        CustomErrorDialog(self, title, message)

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        if self.state() == 'normal':
            save_window_geometry(self)
        self.destroy()

    def _update_sash_cover_position(self, event=None):
        try:
            x = self.paned_window.sashpos(0)
            self.sash_cover.place(x=x, y=0, anchor="nw", relheight=1.0)
        except Exception:
            pass

    def _on_manual_sash_move(self, event=None):
        self.sash_pos_normal = self.paned_window.sashpos(0)
        self._update_sash_cover_position()

    def create_handlers(self):
        self.item_map = {}
        self.path_to_item_id = {}
        listbox_buttons = {
            'top': self.move_to_top_button, 'up': self.move_up_button,
            'remove': self.remove_button, 'down': self.move_down_button,
            'bottom': self.move_to_bottom_button
        }
        self.selection_handler = SelectionListController(
            self, self.merge_order_list, listbox_buttons, self.base_dir, self.default_editor,
            self.on_selection_list_changed, self.token_count_enabled
        )
        self.tree_handler = FileTreeHandler(
            self, self.tree, self.tree_action_button, self.item_map, self.path_to_item_id,
            lambda path: path in [f['path'] for f in self.selection_handler.ordered_selection],
            self.on_file_toggled
        )
        self.tree_action_button.command = self.tree_handler.toggle_selection_for_selected
        self.move_to_top_button.command = self.selection_handler.move_to_top
        self.move_up_button.command = self.selection_handler.move_up
        self.move_down_button.command = self.selection_handler.move_down
        self.move_to_bottom_button.command = self.selection_handler.move_to_bottom
        self.remove_button.command = self.selection_handler.remove_selected

    def populate_tree(self, filter_text=""):
        # Get currently expanded directories before clearing the tree
        expanded_dirs_before_rebuild = set(self.tree_handler.get_expanded_dirs())

        for item in self.tree.get_children(): self.tree.delete(item)
        self.item_map.clear(); self.path_to_item_id.clear()
        selected_paths = {f['path'] for f in self.selection_handler.ordered_selection}
        tree_data = build_file_tree_data(
            self.base_dir,
            self.file_extensions,
            self.gitignore_patterns,
            filter_text,
            self.is_extension_filter_active,
            selected_paths,
            self.is_gitignore_filter_active
        )
        def _insert_nodes(parent_id, nodes):
            for node in nodes:
                tags = ()
                if node['type'] == 'file' and node['path'] in self.newly_detected_files:
                    tags += ('new_file_highlight',)

                # A directory should be open if it was already open in the current session,
                # or if it was saved as expanded from a previous session.
                is_open = node.get('path') in expanded_dirs_before_rebuild or \
                          node.get('path') in self.project_config.expanded_dirs

                item_id = self.tree.insert(parent_id, 'end', text=node['name'], open=is_open, tags=tags)
                self.item_map[item_id] = {'path': node['path'], 'type': node['type']}
                self.path_to_item_id[node['path']] = item_id
                if node['type'] == 'dir':
                    _insert_nodes(item_id, node.get('children', []))
                else: # file
                    self.tree_handler.update_checkbox_display(item_id)
        _insert_nodes('', tree_data)

    def on_selection_list_changed(self):
        self.tree_handler.update_all_checkboxes()
        self.update_all_button_states()
        self.data_controller.run_token_recalculation()
        self.ui_controller.update_active_folder_tooltip()

    def on_file_toggled(self, path):
        self.selection_handler.toggle_file(path)
        self.tree_handler.update_checkbox_display(self.path_to_item_id.get(path))
        self.update_all_button_states()
        self.sync_highlights()

    def handle_tree_select(self, event):
        if self.tree.selection(): self.merge_order_list.clear_selection()
        self.sync_highlights()
        self.update_all_button_states()

    def handle_merge_order_tree_select(self, event):
        if self.merge_order_list.curselection() and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.sync_highlights()
        self.update_all_button_states()

    def update_all_button_states(self):
        self.tree_handler.update_action_button_state()
        self.selection_handler.update_button_states()

    def sync_highlights(self):
        for item_id in self.tree.tag_has('subtle_highlight'):
            self.tree.item(item_id, tags=())
        self.merge_order_list.clear_highlights()
        selected_path, source = (None, None)
        if self.tree.selection():
            item_id = self.tree.selection()[0]
            if self.item_map.get(item_id, {}).get('type') == 'file':
                selected_path, source = (self.item_map[item_id]['path'], self.tree)
        elif self.merge_order_list.curselection():
            idx = self.merge_order_list.curselection()[0]
            selected_path, source = (self.merge_order_list.get_item_data(idx), self.merge_order_list)
        if not selected_path: return
        if source == self.tree:
            try:
                paths = [f['path'] for f in self.selection_handler.ordered_selection]
                self.merge_order_list.highlight_item(paths.index(selected_path))
            except ValueError: pass
        elif source == self.merge_order_list and selected_path in self.path_to_item_id:
            item_id = self.path_to_item_id[selected_path]
            self.tree.item(item_id, tags=('subtle_highlight',))
            self.tree.see(item_id)

        self.ui_controller.refresh_hover_icon()