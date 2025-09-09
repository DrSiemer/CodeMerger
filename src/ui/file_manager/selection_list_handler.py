import os
import sys
import subprocess
from tkinter import messagebox, Toplevel, Label
from ... import constants as c

class SelectionListHandler:
    """
    Manages the 'Merge Order' listbox and its associated buttons,
    handling the data model (ordered_selection) and user actions
    """
    def __init__(self, parent, listbox_widget, buttons, base_dir, default_editor, on_change_callback):
        self.parent = parent
        self.listbox = listbox_widget
        self.move_to_top_button = buttons['top']
        self.move_up_button = buttons['up']
        self.remove_button = buttons['remove']
        self.move_down_button = buttons['down']
        self.move_to_bottom_button = buttons['bottom']
        self.base_dir = base_dir
        self.default_editor = default_editor
        self.on_change = on_change_callback # Callback to notify coordinator of changes
        self.ordered_selection = []
        self.tooltip_window = None
        self._tooltip_job = None

        self.listbox.bind('<<ListboxSelect>>', self.on_list_selection_change)
        self.listbox.bind('<Double-1>', self.open_selected_file)
        self.listbox.bind('<Motion>', self.schedule_tooltip)
        self.listbox.bind('<Leave>', self.hide_tooltip)

    def set_initial_selection(self, selection_list):
        self.ordered_selection = list(selection_list)
        self.update_listbox_from_data()

    def update_listbox_from_data(self):
        """Refreshes the merge order listbox with the current data model"""
        self.listbox.delete(0, 'end')
        for path in self.ordered_selection:
            self.listbox.insert('end', os.path.basename(path))

    def schedule_tooltip(self, event):
        """Schedules a tooltip to appear after a short delay."""
        if self._tooltip_job:
            self.parent.after_cancel(self._tooltip_job)
            self._tooltip_job = None
        
        self.hide_tooltip()

        current_index = self.listbox.nearest(event.y)
        if current_index != -1:
            bbox = self.listbox.bbox(current_index)
            if bbox and bbox[1] <= event.y < bbox[1] + bbox[3]:
                self._tooltip_job = self.parent.after(350, lambda idx=current_index: self.show_tooltip(idx))

    def show_tooltip(self, index):
        """Creates and displays the tooltip window."""
        if self.tooltip_window or index >= len(self.ordered_selection):
            return

        full_path = self.ordered_selection[index]
        if full_path == os.path.basename(full_path):
            return

        bbox = self.listbox.bbox(index)
        if not bbox: return

        x = self.listbox.winfo_rootx() + 5
        y = self.listbox.winfo_rooty() + bbox[1] + bbox[3] + 2

        self.tooltip_window = Toplevel(self.listbox)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = Label(self.tooltip_window, text=full_path, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=4, ipady=2)

    def hide_tooltip(self, event=None):
        """Destroys the tooltip window and cancels any pending show job."""
        if self._tooltip_job:
            self.parent.after_cancel(self._tooltip_job)
            self._tooltip_job = None
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def on_list_selection_change(self, event=None):
        """Callback for when the listbox selection changes"""
        self.parent.handle_list_select(event)

    def update_button_states(self):
        """Enables or disables the listbox action buttons based on selection"""
        new_state = 'normal' if self.listbox.curselection() else 'disabled'
        self.move_to_top_button.config(state=new_state)
        self.move_up_button.config(state=new_state)
        self.remove_button.config(state=new_state)
        self.move_down_button.config(state=new_state)
        self.move_to_bottom_button.config(state=new_state)


    def toggle_file(self, path):
        """Adds or removes a file from the selection"""
        if path in self.ordered_selection:
            self.ordered_selection.remove(path)
        else:
            self.ordered_selection.append(path)
        self.update_listbox_from_data()
        self.on_change()

    def add_files(self, paths_to_add):
        """Adds multiple files to the selection if they aren't already present"""
        for path in paths_to_add:
            if path not in self.ordered_selection:
                self.ordered_selection.append(path)
        self.update_listbox_from_data()
        self.on_change()

    def remove_all_files(self):
        """Clears the entire selection list"""
        self.ordered_selection.clear()
        self.update_listbox_from_data()
        self.on_change()

    def move_to_top(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices or selection_indices[0] == 0:
            return

        moved_paths = [self.ordered_selection[i] for i in selection_indices]
        for index in sorted(selection_indices, reverse=True):
            self.ordered_selection.pop(index)

        self.ordered_selection = moved_paths + self.ordered_selection

        self.update_listbox_from_data()
        self.listbox.selection_set(0, len(moved_paths) - 1)
        self.listbox.activate(0)
        self.listbox.see(0)
        self.on_change()

    def move_up(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices or selection_indices[0] == 0:
            return

        moved_paths = [self.ordered_selection[i] for i in selection_indices]
        for index in sorted(selection_indices, reverse=True):
            self.ordered_selection.pop(index)

        new_start_index = selection_indices[0] - 1
        for i, path in enumerate(moved_paths):
            self.ordered_selection.insert(new_start_index + i, path)

        self.update_listbox_from_data()

        self.listbox.selection_set(new_start_index, new_start_index + len(moved_paths) - 1)
        self.listbox.activate(new_start_index)
        self.listbox.see(new_start_index)
        self.on_change()

    def move_down(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices or selection_indices[-1] >= len(self.ordered_selection) - 1:
            return

        moved_paths = [self.ordered_selection[i] for i in selection_indices]
        for index in sorted(selection_indices, reverse=True):
            self.ordered_selection.pop(index)

        new_start_index = selection_indices[0] + 1
        for i, path in enumerate(moved_paths):
            self.ordered_selection.insert(new_start_index + i, path)

        self.update_listbox_from_data()
        self.listbox.selection_set(new_start_index, new_start_index + len(moved_paths) - 1)
        self.listbox.activate(new_start_index)
        self.listbox.see(new_start_index)
        self.on_change()

    def move_to_bottom(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices or selection_indices[-1] >= len(self.ordered_selection) - 1:
            return

        moved_paths = [self.ordered_selection[i] for i in selection_indices]
        for index in sorted(selection_indices, reverse=True):
            self.ordered_selection.pop(index)

        new_start_index = len(self.ordered_selection)
        self.ordered_selection.extend(moved_paths)

        self.update_listbox_from_data()

        self.listbox.selection_set(new_start_index, len(self.ordered_selection) - 1)
        self.listbox.activate(new_start_index)
        self.listbox.see(new_start_index)
        self.on_change()

    def remove_selected(self):
        selection_indices = self.listbox.curselection()
        if not selection_indices:
            return

        # Remove from data model by iterating backwards to avoid index shifting issues
        for index in sorted(selection_indices, reverse=True):
            self.ordered_selection.pop(index)

        self.update_listbox_from_data()
        self.on_change()

    def open_selected_file(self, event=None):
        if event:
            clicked_index = self.listbox.nearest(event.y)
            if clicked_index == -1: return "break"
            bbox = self.listbox.bbox(clicked_index)
            if not bbox or event.y < bbox[1] or event.y > bbox[1] + bbox[3]: return "break"

        selection = self.listbox.curselection()
        if not selection: return "break"

        relative_path = self.ordered_selection[selection[0]]
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