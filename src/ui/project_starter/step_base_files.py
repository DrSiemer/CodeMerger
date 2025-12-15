import os
import tkinter as tk
from tkinter import messagebox, ttk
from ...core.project_config import ProjectConfig
from ...core.utils import parse_gitignore
from ... import constants as c
from ..file_manager.ui_setup import setup_file_manager_ui
from ..file_manager.ui_controller import FileManagerUIController
from ..file_manager.data_controller import FileManagerDataController
from ..file_manager.selection_list_controller import SelectionListController
from ..file_manager.file_tree_handler import FileTreeHandler
from ..file_manager.state_controller import FileManagerStateController
from ..file_manager.order_request_handler import OrderRequestHandler
from ..widgets.rounded_button import RoundedButton

class StepBaseFilesView(tk.Frame):
    def __init__(self, parent, wizard_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.wizard_controller = wizard_controller
        self.project_data = project_data
        self.app = wizard_controller.app
        self.base_dir = project_data["base_project_path"].get()

        # Mock/Proxy attributes expected by FileManager controllers
        self.status_var = tk.StringVar()
        self.file_extensions = self.app.file_extensions
        self.default_editor = self.app.app_state.default_editor
        self.app_state = self.app.app_state
        self.newly_detected_files = []
        self.full_paths_visible = False
        self.token_count_enabled = self.app_state.config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT)
        self.is_extension_filter_active = True
        self.is_gitignore_filter_active = True
        self.hovered_file_path = None
        self.sash_pos_normal = None
        self.current_total_tokens = 0

        # Initialize Project Config (Read-Only usage)
        self.project_config = ProjectConfig(self.base_dir)
        self.project_config.load() # Load existing .allcode if present

        # Handle Profile Selection if needed
        self._check_profiles()

        # Restore previous selection from wizard state if available, else use project config
        saved_files = self.project_data["base_project_files"]
        if saved_files:
            self.project_config.selected_files = saved_files
            self.project_config.total_tokens = sum(f.get('tokens', 0) for f in saved_files)

        self.current_total_tokens = self.project_config.total_tokens

        # Setup UI
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header_frame = tk.Frame(self, bg=c.DARK_BG)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(10, 5), padx=10)
        tk.Label(header_frame, text="Select Base Files", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')

        self.profile_selector_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        self.profile_selector_frame.pack(side='right')

        tk.Label(self, text="Choose files from the existing project to use as a reference. These will be included in the context for the LLM.", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").grid(row=1, column=0, sticky='w', padx=10)

        # Main File Manager Area - The container for the file manager UI
        self.fm_frame = tk.Frame(self, bg=c.DARK_BG)
        self.fm_frame.grid(row=2, column=0, sticky='nsew')

        # Initialize Controllers
        self.gitignore_patterns = parse_gitignore(self.base_dir)
        self.ui_controller = FileManagerUIController(self)
        self.data_controller = FileManagerDataController(self)
        # We don't use the standard state controller's save logic, but we need it for "Add All" etc.
        self.state_controller = FileManagerStateController(self)
        self.order_request_handler = OrderRequestHandler(self)

        # Setup File Manager UI within fm_frame
        # Pass self.fm_frame as the container so UI elements are packed into it,
        # while 'self' (the View) remains the controller object holding attributes.
        setup_file_manager_ui(self, container=self.fm_frame, include_save_button=False)

        self.create_handlers()

        # Status Bar for this view
        self.status_label = tk.Label(self, textvariable=self.status_var, bg=c.DARK_BG, fg=c.STATUS_FG, font=c.FONT_STATUS_BAR, anchor='w')
        self.status_label.grid(row=3, column=0, sticky='ew', padx=10, pady=5)

        # Initial Population
        self.filter_text = tk.StringVar()
        self.filter_entry.config(textvariable=self.filter_text)
        self.filter_text.trace_add('write', self.ui_controller.apply_filter)
        self.clear_filter_button.bind("<Button-1>", self.ui_controller.clear_filter)

        self.tree.bind("<Motion>", self.ui_controller.on_tree_motion)
        self.tree.bind("<Leave>", self.ui_controller.on_tree_leave)

        self.data_controller.validate_and_update_cache()
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.populate_tree()
        self.data_controller.run_token_recalculation()
        self.update_all_button_states()

    def _check_profiles(self):
        profiles = self.project_config.get_profile_names()
        if len(profiles) > 1:
            tk.Label(self.profile_selector_frame, text="Load Profile:", bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left', padx=5)
            self.profile_var = tk.StringVar(value=self.project_config.active_profile_name)
            cb = ttk.Combobox(self.profile_selector_frame, textvariable=self.profile_var, values=profiles, state="readonly", width=15)
            cb.pack(side='left')
            cb.bind("<<ComboboxSelected>>", self._on_profile_change)

    def _on_profile_change(self, event):
        new_profile = self.profile_var.get()
        self.project_config.active_profile_name = new_profile
        # Reload selection from config
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.current_total_tokens = self.project_config.total_tokens
        self.update_all_button_states()
        self.status_var.set(f"Loaded profile: {new_profile}")

    def save_state(self):
        """Updates the wizard state with the current selection."""
        self.project_data["base_project_files"] = self.selection_handler.ordered_selection

    # --- Methods mimicking FileManagerWindow ---
    def create_handlers(self):
        self.item_map = {}
        self.path_to_item_id = {}
        listbox_buttons = {
            'top': self.move_to_top_button, 'up': self.move_up_button,
            'remove': self.remove_button, 'down': self.move_down_button,
            'bottom': self.move_to_bottom_button
        }
        # Pass self.save_state as callback to ensure state is updated on every change
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
        # Reuse existing logic
        from ..file_manager.file_tree_builder import build_file_tree_data

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

                # Check for expanded state in both current UI and saved project config
                is_open = (node.get('path') in expanded_dirs_before_rebuild) or \
                          (node.get('path') in self.project_config.expanded_dirs)

                item_id = self.tree.insert(parent_id, 'end', text=node['name'], open=is_open, tags=tags)
                self.item_map[item_id] = {'path': node['path'], 'type': node['type']}
                self.path_to_item_id[node['path']] = item_id
                if node['type'] == 'dir':
                    _insert_nodes(item_id, node.get('children', []))
                else:
                    self.tree_handler.update_checkbox_display(item_id)
        _insert_nodes('', tree_data)

    def on_selection_list_changed(self):
        self.tree_handler.update_all_checkboxes()
        self.update_all_button_states()
        self.data_controller.run_token_recalculation()
        self.save_state()

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

    # Stub methods for compatibility with controllers
    def show_error_dialog(self, title, message):
        messagebox.showerror(title, message, parent=self)

    def _close_and_save_geometry(self):
        pass # Not applicable for wizard view

    def _update_sash_cover_position(self, event=None):
        try:
            x = self.paned_window.sashpos(0)
            self.sash_cover.place(x=x, y=0, anchor="nw", relheight=1.0)
        except Exception: pass

    def _on_manual_sash_move(self, event=None):
        self.sash_pos_normal = self.paned_window.sashpos(0)
        self._update_sash_cover_position()