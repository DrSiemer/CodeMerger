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
        self.tooltip_window = None
        self.tooltip_job = None
        self.listbox.bind_event('<<ListSelectionChanged>>', self.on_list_selection_change)
        self.listbox.bind_event('<Double-1>', self.open_selected_file)
        self.listbox.bind_event('<Motion>', self._schedule_tooltip)
        self.listbox.bind_event('<Leave>', self._hide_tooltip)

    def set_initial_selection(self, selection_list):
        self.ordered_selection = list(selection_list)
        self._update_list_display(is_reorder=False)

    def _update_list_display(self, is_reorder=False):
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

        if is_reorder:
            self.listbox.reorder_and_update(display_items)
        else:
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
        self._update_list_display(is_reorder=False)
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
        self._update_list_display(is_reorder=False)
        self.on_change()

    def remove_all_files(self):
        self.ordered_selection.clear()
        self._update_list_display(is_reorder=False)
        self.on_change()

    def move_to_top(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices: return
        moved_items = [self.ordered_selection[i] for i in selection_indices]
        for index in sorted(selection_indices, reverse=True):
            del self.ordered_selection[index]
        self.ordered_selection = moved_items + self.ordered_selection
        new_selection_indices = range(len(moved_items))
        self._update_list_display(is_reorder=True)
        self.listbox.selection_set(new_selection_indices[0], new_selection_indices[-1])
        self.listbox.see(new_selection_indices[0])
        self.on_change()

    def move_up(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices or selection_indices[0] == 0:
            return

        # Grouped move logic
        moved_items = [self.ordered_selection[i] for i in selection_indices]

        # Remove selected items by iterating backwards to preserve indices
        for index in sorted(selection_indices, reverse=True):
            del self.ordered_selection[index]

        # Calculate the new insertion point. It's just before the original
        # position of the first selected item.
        insert_index = selection_indices[0] - 1

        # Re-insert the block of moved items
        for i, item in enumerate(moved_items):
            self.ordered_selection.insert(insert_index + i, item)

        # Update selection and view
        new_selection_indices = range(insert_index, insert_index + len(moved_items))
        self._update_list_display(is_reorder=True)
        self.listbox.selection_set(new_selection_indices[0], new_selection_indices[-1])
        self.listbox.see(new_selection_indices[0])
        self.on_change()

    def move_down(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices or selection_indices[-1] >= len(self.ordered_selection) - 1:
            return

        # Grouped move logic
        moved_items = [self.ordered_selection[i] for i in selection_indices]

        # Remove selected items by iterating backwards
        for index in sorted(selection_indices, reverse=True):
            del self.ordered_selection[index]

        # Calculate the new insertion index. It's one position after the
        # original start of the selection.
        insert_index = selection_indices[0] + 1

        # Re-insert the block of moved items
        for i, item in enumerate(moved_items):
            self.ordered_selection.insert(insert_index + i, item)

        # Update selection and view
        new_selection_indices = range(insert_index, insert_index + len(moved_items))
        self._update_list_display(is_reorder=True)
        self.listbox.selection_set(new_selection_indices[0], new_selection_indices[-1])
        self.listbox.see(new_selection_indices[-1])
        self.on_change()

    def move_to_bottom(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices: return
        moved_items = [self.ordered_selection[i] for i in selection_indices]
        for index in sorted(selection_indices, reverse=True):
            del self.ordered_selection[index]
        new_start_index = len(self.ordered_selection)
        self.ordered_selection.extend(moved_items)
        self._update_list_display(is_reorder=True)
        self.listbox.selection_set(new_start_index, len(self.ordered_selection) - 1)
        self.listbox.see(len(self.ordered_selection) - 1)
        self.on_change()

    def remove_selected(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices: return
        # Remove from data model by iterating backwards
        for index in sorted(selection_indices, reverse=True):
            del self.ordered_selection[index]
        self._update_list_display(is_reorder=False)
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

    def _schedule_tooltip(self, event):
        """Schedules a tooltip to appear after a delay, cancelling any existing ones."""
        # Hide any visible tooltip and cancel any pending show request.
        self._hide_tooltip()
        # Schedule a new tooltip to appear after the delay.
        self.tooltip_job = self.listbox.after(500, lambda e=event: self._show_tooltip(e))

    def _show_tooltip(self, event):
        """Creates and displays the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

        # Determine which list item is under the cursor
        index = int(self.listbox.canvasy(event.y) // self.listbox.row_height)
        if not (0 <= index < len(self.ordered_selection)):
            return

        item_info = self.ordered_selection[index]
        path = item_info.get('path')
        if not path:
            return

        # Decide which tooltip to show based on horizontal position
        is_over_line_count_area = event.x > (self.listbox.winfo_width() - self.listbox.right_col_width)
        tooltip_text = None

        if is_over_line_count_area and self.line_count_enabled:
            # Re-check if a line count is actually VISIBLE for this item
            line_count = -1
            try:
                with open(os.path.join(self.base_dir, path), 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = len(f.readlines())
            except (IOError, OSError):
                pass # line_count remains -1

            # Tooltip should only show if the text is visible (i.e., over the threshold)
            if line_count > self.line_count_threshold:
                tooltip_text = f"{line_count} lines of text"

        # If we are not showing the line count tooltip, fall back to the path tooltip
        if tooltip_text is None:
            basename = os.path.basename(path)
            full_path_display = path.replace('/', os.sep)
            if basename != full_path_display:
                tooltip_text = full_path_display

        # Now, create and display the tooltip window with the determined text
        if not tooltip_text:
            return

        x = event.x_root + 15
        y = event.y_root + 10
        self.tooltip_window = Toplevel(self.parent)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = Label(self.tooltip_window, text=tooltip_text, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=4, ipady=2)

    def _hide_tooltip(self, event=None):
        """Cancels any pending tooltip job and destroys any visible tooltip window."""
        if self.tooltip_job:
            self.listbox.after_cancel(self.tooltip_job)
            self.tooltip_job = None

        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None