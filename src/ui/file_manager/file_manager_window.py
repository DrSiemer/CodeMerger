import tkinter as tk
from tkinter import Toplevel, StringVar, ttk, messagebox
import json
import pyperclip

from ...core.utils import parse_gitignore
from ...core.merger import generate_output_string
from .file_tree_builder import build_file_tree_data
from .file_tree_handler import FileTreeHandler
from .selection_list_controller import SelectionListController
from .ui_setup import setup_file_manager_ui
from .ui_controller import FileManagerUIController
from .data_controller import FileManagerDataController
from .state_controller import FileManagerStateController
from ... import constants as c
from ...core.paths import ICON_PATH
from ..window_utils import position_window, save_window_geometry
from ..tooltip import ToolTip
from ..assets import assets
from ..multiline_input_dialog import MultilineInputDialog

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
        self.hovered_file_path = None
        self.current_total_tokens = self.project_config.total_tokens
        self.sash_pos_normal = None
        self.order_request_click_job = None
        # [ADD] Add the missing attribute to self to allow child dialogs to work correctly
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
            self.expand_and_scroll_to_new_files()

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        if self.state() == 'normal':
            # [MODIFIED] Pass self (FileManagerWindow) to save_window_geometry
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

    def expand_and_scroll_to_new_files(self):
        """
        Expands parent directories of newly detected files and scrolls the first one to the top of the view.
        """
        if not self.newly_detected_files:
            return

        first_file_path = sorted(self.newly_detected_files)[0]
        first_item_id = self.path_to_item_id.get(first_file_path)

        if first_item_id:
            # This command ensures all parent folders are expanded so the item is reachable.
            self.tree.see(first_item_id)

            def scroll_when_ready(retries=15):
                """Polls until the item is rendered, then scrolls it to the top."""
                if retries <= 0:
                    return

                try:
                    # If bbox is available, the item is rendered. Proceed with scrolling.
                    if self.tree.bbox(first_item_id):
                        # This logic robustly finds the item's visible index and scrolls it to the top.
                        visible_items = []
                        def _collect_visible_items(parent_id):
                            if parent_id != '' and not self.tree.item(parent_id, 'open'): return
                            for child_id in self.tree.get_children(parent_id):
                                visible_items.append(child_id)
                                _collect_visible_items(child_id)
                        _collect_visible_items('')

                        if not visible_items: return
                        total_visible = len(visible_items)
                        target_index = visible_items.index(first_item_id) if first_item_id in visible_items else -1

                        if target_index != -1:
                            target_fraction = target_index / total_visible
                            self.tree.yview_moveto(max(0.0, min(1.0, target_fraction)))
                    else:
                        # If bbox is not ready, schedule another check shortly.
                        self.after(10, scroll_when_ready, retries - 1)

                except tk.TclError:
                    # Window was likely closed during polling.
                    pass

            # Start the polling process.
            self.after(10, scroll_when_ready)

    def handle_order_request_click(self, event=None):
        """Manages single and double clicks for the order request button."""
        if self.order_request_click_job:
            self.after_cancel(self.order_request_click_job)
            self.order_request_click_job = None
            self._handle_order_request_reorder()
        else:
            self.order_request_click_job = self.after(300, self._handle_order_request_copy)

    def _handle_order_request_copy(self):
        """Copies a formatted order request to the clipboard."""
        self.order_request_click_job = None
        ordered_files_info = self.selection_handler.ordered_selection
        if not ordered_files_info:
            self.status_var.set("No files in merge order to create a request for.")
            return

        # Create a temporary config object to pass to the merger
        temp_project_config = self.project_config
        temp_project_config.selected_files = ordered_files_info

        # Generate the merged code content first
        merged_code, _ = generate_output_string(
            base_dir=self.base_dir,
            project_config=temp_project_config,
            use_wrapper=False,
            copy_merged_prompt=""
        )

        if not merged_code:
            self.status_var.set("Failed to generate merged code for the request.")
            return

        # Now, construct the full request string
        paths = [f['path'] for f in ordered_files_info]
        prepend_text = "Please provide me with the optimal order in which to present these files to a language model. Only return the file list in the exact same format I will use here:\n\n"
        json_payload = json.dumps(paths, indent=2)
        content_intro = "Here's the content of the files, to help you determine the best order:"

        final_string = f"{prepend_text}{json_payload}\n\n{content_intro}\n\n{merged_code}"
        pyperclip.copy(final_string)
        self.status_var.set("Order request with file content copied to clipboard.")

    def _handle_order_request_reorder(self):
        """Opens a dialog to paste a new file order and updates the list."""
        current_selection = self.selection_handler.ordered_selection
        if not current_selection:
            self.status_var.set("Merge order is empty, nothing to reorder.")
            return

        dialog = MultilineInputDialog(
            parent=self,
            title="Update Merge Order",
            prompt="Paste the language model response containing the new file order."
        )
        pasted_text = dialog.result

        if not pasted_text:
            return

        # Find the JSON array within the pasted text
        try:
            start_index = pasted_text.find('[')
            end_index = pasted_text.rfind(']') + 1
            if start_index == -1 or end_index == 0:
                raise ValueError("Could not find a JSON array (starting with '[' and ending with ']').")

            json_str = pasted_text[start_index:end_index]
            new_order_list = json.loads(json_str)

            if not isinstance(new_order_list, list):
                raise ValueError("The parsed JSON is not a list.")

        except (ValueError, json.JSONDecodeError) as e:
            messagebox.showwarning("Parsing Error", f"Could not parse the new file order.\n\nError: {e}", parent=self)
            return

        # Validate the received list against the current list
        current_paths_set = {f['path'] for f in current_selection}
        new_paths_set = set(new_order_list)

        missing_files = current_paths_set - new_paths_set
        unknown_files = new_paths_set - current_paths_set

        if missing_files or unknown_files:
            error_message = "The provided file list is invalid.\n"
            if missing_files:
                error_message += f"\nMissing files:\n- " + "\n- ".join(sorted(list(missing_files)))
            if unknown_files:
                error_message += f"\nUnknown files:\n- " + "\n- ".join(sorted(list(unknown_files)))
            messagebox.showwarning("Validation Error", error_message, parent=self)
            return

        # If validation passes, reorder the selection
        path_map = {f['path']: f for f in current_selection}
        new_ordered_selection = [path_map[p] for p in new_order_list]

        self.selection_handler.data_manager.ordered_selection = new_ordered_selection
        self.selection_handler.ui_manager.update_list_display(new_ordered_selection, is_reorder=True)
        self.selection_handler.on_change() # Trigger token recalc and button state update
        self.status_var.set("File merge order updated successfully.")

    def save_and_close(self):
        self.state_controller.save_and_close()

    def select_all_files(self):
        self.state_controller.select_all_files()

    def remove_all_files(self):
        self.state_controller.remove_all_files()

    def toggle_full_path_view(self):
        self.ui_controller.toggle_full_path_view()

    def toggle_extension_filter(self):
        """Toggles the filetype extension filter on and off."""
        self.is_extension_filter_active = not self.is_extension_filter_active

        self.filter_button_tooltip.cancel_show()
        self.filter_button_tooltip.hide_tooltip()

        if self.is_extension_filter_active:
            self.toggle_filter_button.config(image=assets.filter_icon)
            self.filter_button_tooltip.text = "Filetype filter is ON. Click to show all files."
        else:
            self.toggle_filter_button.config(image=assets.filter_icon_active)
            self.filter_button_tooltip.text = "Filetype filter is OFF. Click to show only allowed filetypes."

        # Show the new tooltip immediately. It will be hidden automatically on <Leave>.
        self.filter_button_tooltip.show_tooltip()

        # Repopulate tree using the current text filter value
        self.populate_tree(self.filter_text.get())

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
        for item in self.tree.get_children(): self.tree.delete(item)
        self.item_map.clear(); self.path_to_item_id.clear()
        selected_paths = {f['path'] for f in self.selection_handler.ordered_selection}
        tree_data = build_file_tree_data(
            self.base_dir,
            self.file_extensions,
            self.gitignore_patterns,
            filter_text,
            self.is_extension_filter_active,
            selected_paths
        )
        def _insert_nodes(parent_id, nodes):
            for node in nodes:
                tags = ()
                if node['type'] == 'file' and node['path'] in self.newly_detected_files:
                    tags += ('new_file_highlight',)
                item_id = self.tree.insert(parent_id, 'end', text=node['name'], open=node.get('path') in self.project_config.expanded_dirs, tags=tags)
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