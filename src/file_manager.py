import os
import sys
import time
import subprocess
import tkinter as tk
from tkinter import Toplevel, Frame, Label, Button, Listbox, messagebox, ttk

from .utils import parse_gitignore
from .constants import SUBTLE_HIGHLIGHT_COLOR
from .project_config import ProjectConfig
from .file_tree_builder import build_file_tree_data
from .merger import recalculate_token_count

class FileManagerWindow(Toplevel):
    def __init__(self, parent, base_dir, status_var, file_extensions, default_editor):
        super().__init__(parent)

        self.base_dir = base_dir
        self.status_var = status_var
        self.file_extensions = file_extensions
        self.default_editor = default_editor

        self.title(f"Manage files for: {os.path.basename(self.base_dir)}")
        self.geometry("850x700")
        self.transient(parent)
        self.grab_set()

        # Used to differentiate single and double clicks on the tree
        self.last_tree_click_time = 0
        self.last_clicked_item_id = None
        self._recalculate_job = None
        self.current_total_tokens = 0

        self.project_config = ProjectConfig(self.base_dir)
        files_were_cleaned = self.project_config.load()
        if files_were_cleaned:
            self.status_var.set("Cleaned missing files from .allcode")

        self.ordered_selection = self.project_config.selected_files
        self.expanded_dirs = self.project_config.expanded_dirs
        self.gitignore_patterns = parse_gitignore(self.base_dir)

        main_frame = Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        Label(main_frame, text="Available Files (double click or enter to add/remove)").grid(row=0, column=0, columnspan=2, sticky='w')
        self.tree = ttk.Treeview(main_frame, show='tree')
        self.tree.grid(row=1, column=0, sticky='nsew')
        tree_scroll = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        tree_scroll.grid(row=1, column=1, sticky='ns')
        self.tree.config(yscrollcommand=tree_scroll.set)
        self.tree_action_button = Button(main_frame, text="Add to Merge List", command=self.toggle_selection_for_selected, state='disabled')
        self.tree_action_button.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        self.tree.tag_configure('subtle_highlight', background=SUBTLE_HIGHLIGHT_COLOR)

        self.merge_order_title_label = Label(main_frame, text="Merge Order")
        self.merge_order_title_label.grid(row=0, column=2, columnspan=2, sticky='w', padx=(10, 0))
        self.merge_order_list = Listbox(main_frame, activestyle='none')
        self.merge_order_list.grid(row=1, column=2, sticky='nsew', padx=(10, 0))
        list_scroll = ttk.Scrollbar(main_frame, orient='vertical', command=self.merge_order_list.yview)
        list_scroll.grid(row=1, column=3, sticky='ns')
        self.merge_order_list.config(yscrollcommand=list_scroll.set)

        move_buttons_frame = Frame(main_frame)
        move_buttons_frame.grid(row=2, column=2, sticky='ew', pady=(5, 0), padx=(10, 0))
        self.move_up_button = Button(move_buttons_frame, text="↑ Move Up", command=self.move_up, state='disabled')
        self.move_up_button.pack(side='left', expand=True, fill='x', padx=(0, 2))
        self.remove_button = Button(move_buttons_frame, text="Remove", command=self.remove_selected, state='disabled')
        self.remove_button.pack(side='left', expand=True, fill='x', padx=2)
        self.move_down_button = Button(move_buttons_frame, text="↓ Move Down", command=self.move_down, state='disabled')
        self.move_down_button.pack(side='left', expand=True, fill='x', padx=(2, 0))

        # --- Bulk Action Buttons ---
        bulk_action_frame = Frame(main_frame)
        bulk_action_frame.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(20, 0))

        self.select_all_button = Button(bulk_action_frame, text="Select all", command=self.select_all_files)
        self.select_all_button.pack(side='left')

        self.remove_all_button = Button(bulk_action_frame, text="Remove all", command=self.remove_all_files)
        self.remove_all_button.pack(side='right')

        self.save_and_close_button = Button(bulk_action_frame, text="Save and Close", command=self.save_and_close)
        self.save_and_close_button.pack()

        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<Return>', self.toggle_selection_for_selected) # For accessibility
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.merge_order_list.bind('<<ListboxSelect>>', self.on_list_selection_change)
        self.merge_order_list.bind('<Double-1>', self.open_selected_file)
        self.tree.bind("<Button-1>", self.handle_tree_deselection_click, add='+')

        self.item_map = {}
        self.path_to_item_id = {}
        self.populate_tree()
        self.update_listbox_from_data()
        self.update_button_states()
        self.update_tree_action_button_state()
        self._update_title(self.project_config.total_tokens)
        if files_were_cleaned:
            self.trigger_recalculation()

    def _update_title(self, total_tokens):
        """Updates the title with the provided token count"""
        self.current_total_tokens = total_tokens
        num_files = len(self.ordered_selection)
        file_text = "files" if num_files != 1 else "file"

        if total_tokens >= 0:
            formatted_tokens = f"{total_tokens:,}".replace(',', '.')
            title = f"Merge Order ({num_files} {file_text} selected, {formatted_tokens} tokens)"
        else:
            title = f"Merge Order ({num_files} {file_text} selected, token count error)"

        self.merge_order_title_label.config(text=title)

    def handle_tree_deselection_click(self, event):
        """Deselects a tree item if a click occurs in an empty area"""
        if not self.tree.identify_row(event.y) and self.tree.selection():
            self.tree.selection_set("")

    def populate_tree(self):
        """Populates the treeview using data from the file_tree_builder"""
        tree_data = build_file_tree_data(self.base_dir, self.file_extensions, self.gitignore_patterns)

        def _insert_nodes(parent_id, nodes):
            for node in nodes:
                if node['type'] == 'dir':
                    is_open = node['path'] in self.expanded_dirs
                    dir_id = self.tree.insert(parent_id, 'end', text=node['name'], open=is_open)
                    self.item_map[dir_id] = {'path': node['path'], 'type': 'dir'}
                    self.path_to_item_id[node['path']] = dir_id
                    _insert_nodes(dir_id, node.get('children', []))
                elif node['type'] == 'file':
                    item_id = self.tree.insert(parent_id, 'end', text=f" {node['name']}", tags=('file',))
                    self.item_map[item_id] = {'path': node['path'], 'type': 'file'}
                    self.path_to_item_id[node['path']] = item_id
                    self.update_checkbox_display(item_id)

        _insert_nodes('', tree_data)


    def on_tree_selection_change(self, event):
        """When a tree item is selected, deselect any listbox item and sync highlights"""
        if self.tree.selection():
            self.merge_order_list.selection_clear(0, 'end')
            self.sync_highlights()
        self.update_button_states()
        self.update_tree_action_button_state()

    def on_list_selection_change(self, event):
        """When a listbox item is selected, deselect any tree item and sync highlights"""
        if self.merge_order_list.curselection():
            if self.tree.selection():
                self.tree.selection_set("")
            self.sync_highlights()
        self.update_button_states()
        self.update_tree_action_button_state()

    def sync_highlights(self):
        """Highlights the corresponding item in the other list when one is selected"""
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
            try:
                list_index = self.ordered_selection.index(selected_path)
                self.merge_order_list.itemconfig(list_index, {'bg': SUBTLE_HIGHLIGHT_COLOR})
            except ValueError:
                pass # Not in the selected list
        elif list_selection:
            if selected_path in self.path_to_item_id:
                item_id = self.path_to_item_id[selected_path]
                self.tree.item(item_id, tags=('file', 'subtle_highlight'))
                self.tree.see(item_id) # Ensure the item is visible

    def clear_all_subtle_highlights(self):
        """Removes all custom background highlights from both lists"""
        for i in range(self.merge_order_list.size()):
            self.merge_order_list.itemconfig(i, {'bg': 'white'})

        for item_id in self.tree.tag_has('subtle_highlight'):
            self.tree.item(item_id, tags=('file',))

    def handle_tree_click(self, event):
        """Detects a double-click on the same treeview item to toggle file selection"""
        item_id = self.tree.identify_row(event.y)
        current_time = time.time()
        time_diff = current_time - self.last_tree_click_time

        # A double-click is a click on the same item within a short time frame
        if time_diff < 0.4 and item_id and item_id == self.last_clicked_item_id:
            self.toggle_selection_for_selected()
            self.last_tree_click_time = 0
            self.last_clicked_item_id = None
        else:
            # Record this as a potential first click of a double-click
            self.last_tree_click_time = current_time
            self.last_clicked_item_id = item_id

    def trigger_recalculation(self):
        """Schedules a token count recalculation, debouncing rapid calls"""
        if self._recalculate_job:
            self.after_cancel(self._recalculate_job)
        # A small delay to batch rapid changes and keep the UI responsive
        self._recalculate_job = self.after(250, self.run_token_recalculation)

    def run_token_recalculation(self):
        """Calls the merger module to count tokens and updates the UI"""
        self._recalculate_job = None # The job is now running, so clear the ID
        total_tokens = recalculate_token_count(self.base_dir, self.ordered_selection)
        self._update_title(total_tokens)

    def update_checkbox_display(self, item_id):
        """Updates the text of a tree item to show a checked or unchecked box"""
        if self.item_map.get(item_id, {}).get('type') != 'file':
            return

        path = self.item_map[item_id]['path']
        is_checked = path in self.ordered_selection
        check_char = "☑" if is_checked else "☐"
        self.tree.item(item_id, text=f"{check_char} {os.path.basename(path)}")

    def update_button_states(self):
        """Enables or disables the listbox action buttons based on selection"""
        new_state = 'normal' if self.merge_order_list.curselection() else 'disabled'
        self.move_up_button.config(state=new_state)
        self.remove_button.config(state=new_state)
        self.move_down_button.config(state=new_state)

    def update_tree_action_button_state(self):
        """Updates the state and text of the button under the treeview"""
        selection = self.tree.selection()
        if not selection:
            self.tree_action_button.config(state='disabled', text="Add to Merge List")
            return

        item_id = selection[0]
        item_info = self.item_map.get(item_id, {})
        if item_info.get('type') != 'file':
            self.tree_action_button.config(state='disabled', text="Add to Merge List")
            return

        self.tree_action_button.config(state='normal')
        if item_info['path'] in self.ordered_selection:
            self.tree_action_button.config(text="Remove from Merge List")
        else:
            self.tree_action_button.config(text="Add to Merge List")

    def toggle_selection_for_selected(self, event=None):
        """Adds or removes the selected file from the merge list"""
        selection = self.tree.selection()
        if not selection: return

        item_id = selection[0]
        if self.item_map.get(item_id, {}).get('type') != 'file': return

        path = self.item_map[item_id]['path']
        if path in self.ordered_selection:
            self.ordered_selection.remove(path)
        else:
            self.ordered_selection.append(path)

        self.update_checkbox_display(item_id)
        self.update_listbox_from_data()
        self.trigger_recalculation()
        self.sync_highlights()
        self.update_button_states()
        self.update_tree_action_button_state()
        return "break"

    def open_selected_file(self, event=None):
        """Opens the selected file using the configured default editor or the system's default"""
        # This block prevents a double-click in an empty listbox area from opening a file
        if event:
            clicked_index = self.merge_order_list.nearest(event.y)
            if clicked_index == -1: return "break"
            bbox = self.merge_order_list.bbox(clicked_index)
            if not bbox or event.y < bbox[1] or event.y > bbox[1] + bbox[3]: return "break"

        selection = self.merge_order_list.curselection()
        if not selection: return "break"

        relative_path = self.merge_order_list.get(selection[0])
        full_path = os.path.join(self.base_dir, relative_path)
        if not os.path.isfile(full_path):
            messagebox.showwarning("File Not Found", f"The file '{relative_path}' could not be found", parent=self)
            return "break"

        try:
            if self.default_editor and os.path.isfile(self.default_editor):
                subprocess.Popen([self.default_editor, full_path])
            else:
                # Fall back to the OS default action
                if sys.platform == "win32":
                    os.startfile(full_path)
                elif sys.platform == "darwin": # macOS
                    subprocess.call(['open', full_path])
                else: # linux
                    subprocess.call(['xdg-open', full_path])
        except (AttributeError, FileNotFoundError):
            messagebox.showinfo("Unsupported Action", "Could not open file with the system default\nPlease configure a default editor in Settings", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}", parent=self)
        return "break"

    def update_listbox_from_data(self):
        """Refreshes the merge order listbox with the current selection"""
        selection = self.merge_order_list.curselection()
        self.merge_order_list.delete(0, 'end')
        for path in self.ordered_selection:
            self.merge_order_list.insert('end', path)
        if selection and selection[0] < self.merge_order_list.size():
            self.merge_order_list.select_set(selection[0])

    def move_up(self):
        """Moves the selected item up in the merge order list"""
        selection = self.merge_order_list.curselection()
        if not selection: return

        index = selection[0]
        if index > 0:
            path = self.ordered_selection.pop(index)
            self.ordered_selection.insert(index - 1, path)
            # This manual UI update is critical for performance and to preserve selection state
            self.merge_order_list.delete(index)
            self.merge_order_list.insert(index - 1, path)
            self.merge_order_list.select_set(index - 1)
            self.trigger_recalculation()
            self.sync_highlights()
            self.update_button_states()

    def move_down(self):
        """Moves the selected item down in the merge order list"""
        selection = self.merge_order_list.curselection()
        if not selection: return

        index = selection[0]
        if index < len(self.ordered_selection) - 1:
            path = self.ordered_selection.pop(index)
            self.ordered_selection.insert(index + 1, path)
            # This manual UI update is critical for performance and to preserve selection state
            self.merge_order_list.delete(index)
            self.merge_order_list.insert(index + 1, path)
            self.merge_order_list.select_set(index + 1)
            self.trigger_recalculation()
            self.sync_highlights()
            self.update_button_states()

    def remove_selected(self):
        """Removes the selected file from the merge list"""
        selection = self.merge_order_list.curselection()
        if not selection: return

        index = selection[0]
        path = self.ordered_selection.pop(index)

        if path in self.path_to_item_id:
            item_id = self.path_to_item_id[path]
            self.update_checkbox_display(item_id)

        self.update_listbox_from_data()
        self.trigger_recalculation()
        self.sync_highlights()
        self.update_button_states()
        self.update_tree_action_button_state()

    def select_all_files(self):
        """Adds all unselected files from the tree to the merge list, in tree order"""
        all_tree_files = []

        def _traverse(parent_id):
            for item_id in self.tree.get_children(parent_id):
                item_info = self.item_map.get(item_id, {})
                if item_info.get('type') == 'file':
                    all_tree_files.append(item_info['path'])
                elif item_info.get('type') == 'dir':
                    _traverse(item_id)

        _traverse('')

        added_count = 0
        current_selection_set = set(self.ordered_selection)

        for path in all_tree_files:
            if path not in current_selection_set:
                self.ordered_selection.append(path)
                item_id = self.path_to_item_id.get(path)
                if item_id:
                    self.update_checkbox_display(item_id)
                added_count += 1

        if added_count > 0:
            self.update_listbox_from_data()
            self.trigger_recalculation()
            self.update_tree_action_button_state()
            self.status_var.set(f"Added {added_count} file(s) to the merge list")
        else:
            self.status_var.set("No new files to add")

    def remove_all_files(self):
        """Removes all files from the merge list after a confirmation"""
        if not self.ordered_selection:
            self.status_var.set("Merge list is already empty")
            return

        if not messagebox.askyesno(
            "Confirm Removal",
            "Are you sure you want to remove all files from the merge list?",
            parent=self
        ):
            return

        paths_to_update = list(self.ordered_selection)
        removed_count = len(paths_to_update)
        self.ordered_selection.clear()

        for path in paths_to_update:
            if path in self.path_to_item_id:
                item_id = self.path_to_item_id[path]
                self.update_checkbox_display(item_id)

        self.update_listbox_from_data()
        self.trigger_recalculation()
        self.sync_highlights()
        self.update_button_states()
        self.update_tree_action_button_state()
        self.status_var.set(f"Removed {removed_count} file(s) from the merge list")

    def save_and_close(self):
        """Saves the selection and order to .allcode and closes the window"""
        expanded_dirs = [
            info['path'] for item_id, info in self.item_map.items()
            if info.get('type') == 'dir' and self.tree.item(item_id, 'open')
        ]

        self.project_config.save(
            self.ordered_selection,
            set(expanded_dirs),
            self.current_total_tokens
        )
        self.status_var.set("File selection and order saved to .allcode")
        self.destroy()