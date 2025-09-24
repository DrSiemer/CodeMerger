import os
import sys
import subprocess
from tkinter import messagebox, Toplevel, Label
from ... import constants as c
from .selection_data_manager import SelectionDataManager
from .selection_list_ui import SelectionListUI

class SelectionListController:
    """
    Orchestrates the data, UI, and user interactions for the 'Merge Order' list.
    """
    def __init__(self, parent, list_widget, buttons, base_dir, default_editor, on_change_callback, token_count_enabled):
        self.parent = parent
        self.listbox = list_widget
        self.buttons = buttons
        self.base_dir = base_dir
        self.default_editor = default_editor
        self.on_change = on_change_callback
        self.is_filtered = False
        self.tooltip_window = None
        self.tooltip_job = None

        self.data_manager = SelectionDataManager(base_dir, token_count_enabled, parent)
        self.ui_manager = SelectionListUI(list_widget, token_count_enabled)

        self._bind_events()

    @property
    def ordered_selection(self):
        return self.data_manager.ordered_selection

    def _bind_events(self):
        """Binds all widget events to their respective handlers."""
        self.listbox.bind_event('<<ListSelectionChanged>>', self.on_list_selection_change)
        self.listbox.bind_event('<Double-1>', self.open_selected_file)
        self.listbox.bind_event('<Motion>', self._schedule_tooltip)
        self.listbox.bind_event('<Leave>', self._hide_tooltip)
        self.listbox.bind_event('<MouseWheel>', self._on_scroll, add='+')
        # Button commands will be set in file_manager_window.py

    def set_initial_selection(self, selection_list):
        self.data_manager.set_initial_selection(selection_list)
        self.ui_manager.update_list_display(self.ordered_selection)

    def _update_and_notify(self, is_reorder=False):
        """Helper to refresh the UI display and invoke the parent callback."""
        self.ui_manager.update_list_display(self.ordered_selection, is_reorder=is_reorder)
        self.on_change()

    def toggle_file(self, path):
        self.data_manager.toggle_file(path)
        self._update_and_notify()

    def add_files(self, paths_to_add):
        self.data_manager.add_files(paths_to_add)
        self._update_and_notify()

    def remove_all_files(self):
        self.data_manager.remove_all()
        self._update_and_notify()

    def move_to_top(self):
        indices = self.listbox.curselection()
        if not indices: return
        new_selection = self.data_manager.reorder_move_to_top(indices)
        self._update_and_notify(is_reorder=True)
        self.listbox.selection_set(new_selection.start, new_selection.stop - 1)
        self.listbox.see(new_selection.start)

    def move_up(self):
        indices = self.listbox.curselection()
        new_selection = self.data_manager.reorder_move_up(indices)
        if new_selection:
            self._update_and_notify(is_reorder=True)
            self.listbox.selection_set(new_selection.start, new_selection.stop - 1)
            self.listbox.see(new_selection.start)

    def move_down(self):
        indices = self.listbox.curselection()
        new_selection = self.data_manager.reorder_move_down(indices)
        if new_selection:
            self._update_and_notify(is_reorder=True)
            self.listbox.selection_set(new_selection.start, new_selection.stop - 1)
            self.listbox.see(new_selection.stop - 1)

    def move_to_bottom(self):
        indices = self.listbox.curselection()
        if not indices: return
        new_selection = self.data_manager.reorder_move_to_bottom(indices)
        self._update_and_notify(is_reorder=True)
        self.listbox.selection_set(new_selection.start, new_selection.stop - 1)
        self.listbox.see(new_selection.stop - 1)

    def remove_selected(self):
        indices = self.listbox.curselection()
        if not indices: return
        self.data_manager.remove_by_indices(indices)
        self._update_and_notify()

    def on_list_selection_change(self, event=None):
        self.parent.handle_merge_order_tree_select(event)

    def update_button_states(self):
        selection_exists = self.listbox.curselection()
        sort_buttons = [self.buttons['top'], self.buttons['up'], self.buttons['down'], self.buttons['bottom']]
        sort_button_state = 'disabled' if self.is_filtered else ('normal' if selection_exists else 'disabled')
        for btn in sort_buttons:
            btn.set_state(sort_button_state)
        self.buttons['remove'].set_state('normal' if selection_exists else 'disabled')

    def set_filtered_state(self, is_filtered):
        self.is_filtered = is_filtered
        self.update_button_states()

    def filter_list(self, filter_text):
        self.ui_manager.update_list_display(self.ordered_selection, is_reorder=False, filter_text=filter_text.lower())

    def toggle_full_path_view(self):
        self.ui_manager.toggle_full_path_view()
        self.ui_manager.update_list_display(self.ordered_selection, is_reorder=False)

    def open_selected_file(self, event=None):
        indices = self.listbox.curselection()
        if not indices: return "break"
        relative_path = self.listbox.get_item_data(indices[0])
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

    def _on_scroll(self, event=None):
        self._hide_tooltip()

    def _schedule_tooltip(self, event):
        self._hide_tooltip()
        self.tooltip_job = self.listbox.after(500, lambda e=event: self._show_tooltip(e))

    def _show_tooltip(self, event):
        if self.tooltip_window: self.tooltip_window.destroy(); self.tooltip_window = None
        index = int(self.listbox.canvasy(event.y) // self.listbox.row_height)
        if not (0 <= index < len(self.ordered_selection)): return

        item_info = self.ordered_selection[index]
        path = item_info.get('path')
        if not path: return

        is_over_token_area = event.x > (self.listbox.winfo_width() - self.listbox.right_col_width)
        tooltip_text = None
        if is_over_token_area and self.ui_manager.token_count_enabled:
            tokens, lines = item_info.get('tokens', -1), item_info.get('lines', -1)
            if tokens >= 0: tooltip_text = f"{tokens} tokens, {lines} lines"
        elif not self.ui_manager.show_full_paths:
            basename, full_path_display = os.path.basename(path), path.replace('/', os.sep)
            if basename != full_path_display: tooltip_text = full_path_display

        if not tooltip_text: return

        x, y = event.x_root + 15, event.y_root + 10
        self.tooltip_window = Toplevel(self.parent)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = Label(self.tooltip_window, text=tooltip_text, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=c.FONT_TOOLTIP)
        label.pack(ipadx=4, ipady=2)

    def _hide_tooltip(self, event=None):
        if self.tooltip_job: self.listbox.after_cancel(self.tooltip_job); self.tooltip_job = None
        if self.tooltip_window: self.tooltip_window.destroy(); self.tooltip_window = None