import os
from tkinter import Toplevel, Frame, Label, Listbox, messagebox, ttk

from ...core.utils import parse_gitignore
from ...constants import SUBTLE_HIGHLIGHT_COLOR
from ...core.project_config import ProjectConfig
from .file_tree_builder import build_file_tree_data
from ...core.merger import recalculate_token_count
from .file_tree_handler import FileTreeHandler
from .selection_list_handler import SelectionListHandler
from ..custom_widgets import RoundedButton
from ... import constants as c
from ...core.paths import ICON_PATH

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
        self.geometry("850x700")
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
        self.build_ui()
        self.create_handlers()

        # Populate with initial data
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.populate_tree()
        self.update_all_button_states()
        self._update_title(self.project_config.total_tokens)
        if files_were_cleaned:
            self.trigger_recalculation()

        self._position_window()
        self.deiconify()

    def _position_window(self):
        self.update_idletasks()
        window_name = self.__class__.__name__

        if window_name in self.parent.window_geometries:
            self.geometry(self.parent.window_geometries[window_name])
        else:
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_w = self.parent.winfo_width()
            parent_h = self.parent.winfo_height()
            win_w = self.winfo_width()
            win_h = self.winfo_height()
            x = parent_x + (parent_w - win_w) // 2
            y = parent_y + (parent_h - win_h) // 2
            self.geometry(f'+{x}+{y}')

    def _close_and_save_geometry(self):
        self.parent.window_geometries[self.__class__.__name__] = self.geometry()
        self.destroy()

    def build_ui(self):
        """Creates and packs all the UI widgets"""
        font_family = "Segoe UI"
        font_normal = (font_family, 12)
        font_button = (font_family, 14) # Slightly smaller for more buttons

        main_frame = Frame(self, bg=c.DARK_BG)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        available_files_title_frame = Frame(main_frame, bg=c.DARK_BG)
        available_files_title_frame.grid(row=0, column=0, columnspan=2, sticky='w')
        Label(available_files_title_frame, text="Available Files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal).pack(side='left')
        Label(available_files_title_frame, text="(double click or enter to add/remove)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=font_normal).pack(side='left')

        # --- Treeview Styling ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background=c.TEXT_INPUT_BG, foreground=c.TEXT_COLOR, fieldbackground=c.TEXT_INPUT_BG, borderwidth=0, font=font_normal, rowheight=25)
        style.map("Treeview", background=[('selected', c.BTN_BLUE)], foreground=[('selected', c.BTN_BLUE_TEXT)])

        self.tree = ttk.Treeview(main_frame, show='tree')
        self.tree.grid(row=1, column=0, sticky='nsew')
        tree_scroll = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        tree_scroll.grid(row=1, column=1, sticky='ns')
        self.tree.config(yscrollcommand=tree_scroll.set)
        self.tree_action_button = RoundedButton(main_frame, text="Add to Merge List", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button, width=220)
        self.tree_action_button.grid(row=2, column=0, sticky='w', pady=(10, 0))
        self.tree_action_button.set_state('disabled')
        self.tree.tag_configure('subtle_highlight', background=c.SUBTLE_HIGHLIGHT_COLOR, foreground=c.TEXT_COLOR)
        self.tree.tag_configure('new_file_highlight', foreground="#40C040") # Bright Green

        title_frame = Frame(main_frame, bg=c.DARK_BG)
        title_frame.grid(row=0, column=2, columnspan=2, sticky='w', padx=(10, 0))
        Label(title_frame, text="Merge Order", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal).pack(side='left')
        self.merge_order_details_label = Label(title_frame, text="", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=font_normal)
        self.merge_order_details_label.pack(side='left')

        self.merge_order_list = Listbox(main_frame, activestyle='none', selectmode='extended', bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
                                        selectbackground=c.BTN_BLUE, selectforeground=c.BTN_BLUE_TEXT, relief='flat', borderwidth=0,
                                        highlightthickness=0, font=font_normal)
        self.merge_order_list.grid(row=1, column=2, sticky='nsew', padx=(10, 0))
        list_scroll = ttk.Scrollbar(main_frame, orient='vertical', command=self.merge_order_list.yview)
        list_scroll.grid(row=1, column=3, sticky='ns')
        self.merge_order_list.config(yscrollcommand=list_scroll.set)

        move_buttons_frame = Frame(main_frame, bg=c.DARK_BG)
        move_buttons_frame.grid(row=2, column=2, sticky='ew', pady=(10, 0), padx=(10, 0))
        # Configure grid columns to have equal weight, forcing buttons to the same size
        move_buttons_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        move_buttons_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        move_buttons_frame.grid_columnconfigure(2, weight=1, uniform="group1")
        move_buttons_frame.grid_columnconfigure(3, weight=1, uniform="group1")
        move_buttons_frame.grid_columnconfigure(4, weight=1, uniform="group1")
        
        self.move_to_top_button = RoundedButton(move_buttons_frame, text="↑↑ Top", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button)
        self.move_to_top_button.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        self.move_up_button = RoundedButton(move_buttons_frame, text="↑ Up", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button)
        self.move_up_button.grid(row=0, column=1, sticky='ew', padx=(2, 2))
        self.remove_button = RoundedButton(move_buttons_frame, text="Remove", command=None, fg=c.TEXT_COLOR, font=font_button, hollow=True)
        self.remove_button.grid(row=0, column=2, sticky='ew', padx=2)
        self.move_down_button = RoundedButton(move_buttons_frame, text="↓ Down", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button)
        self.move_down_button.grid(row=0, column=3, sticky='ew', padx=(2, 2))
        self.move_to_bottom_button = RoundedButton(move_buttons_frame, text="↓↓ Bottom", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button)
        self.move_to_bottom_button.grid(row=0, column=4, sticky='ew', padx=(2, 0))

        # Disable all move buttons initially
        for btn in [self.move_to_top_button, self.move_up_button, self.remove_button, self.move_down_button, self.move_to_bottom_button]:
            btn.set_state('disabled')

        bulk_action_frame = Frame(main_frame, bg=c.DARK_BG)
        bulk_action_frame.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(20, 0))
        RoundedButton(bulk_action_frame, text="Select all", command=self.select_all_files, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button).pack(side='left')
        RoundedButton(bulk_action_frame, text="Remove all", command=self.remove_all_files, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button).pack(side='right')
        RoundedButton(bulk_action_frame, text="Save and Close", command=self.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=("Segoe UI", 16), width=240).pack()

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
            selected_path = self.merge_order_list.get(self.merge_order_list.curselection()[0])

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