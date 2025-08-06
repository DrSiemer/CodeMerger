import os
import sys
import subprocess
from tkinter import messagebox

class SelectionListHandler:
    """
    Manages the 'Merge Order' listbox and its associated buttons,
    handling the data model (ordered_selection) and user actions
    """
    def __init__(self, parent, listbox_widget, buttons, base_dir, default_editor, on_change_callback):
        self.parent = parent
        self.listbox = listbox_widget
        self.move_up_button = buttons['up']
        self.remove_button = buttons['remove']
        self.move_down_button = buttons['down']
        self.base_dir = base_dir
        self.default_editor = default_editor
        self.on_change = on_change_callback # Callback to notify coordinator of changes
        self.ordered_selection = []

        self.listbox.bind('<<ListboxSelect>>', self.on_list_selection_change)
        self.listbox.bind('<Double-1>', self.open_selected_file)

    def set_initial_selection(self, selection_list):
        self.ordered_selection = selection_list
        self.update_listbox_from_data()

    def update_listbox_from_data(self):
        """Refreshes the merge order listbox with the current data model"""
        self.listbox.delete(0, 'end')
        for path in self.ordered_selection:
            self.listbox.insert('end', path)

    def on_list_selection_change(self, event=None):
        """Callback for when the listbox selection changes"""
        # Pass the event to the parent coordinator
        self.parent.handle_list_select(event)

    def update_button_states(self):
        """Enables or disables the listbox action buttons based on selection"""
        new_state = 'normal' if self.listbox.curselection() else 'disabled'
        self.move_up_button.config(state=new_state)
        self.remove_button.config(state=new_state)
        self.move_down_button.config(state=new_state)

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

    def move_up(self):
        selection = self.listbox.curselection()
        if not selection: return
        index = selection[0]
        if index > 0:
            path = self.ordered_selection.pop(index)
            self.ordered_selection.insert(index - 1, path)
            self.update_listbox_from_data()
            self.listbox.select_set(index - 1)
            self.listbox.activate(index - 1)
            self.on_change()

    def move_down(self):
        selection = self.listbox.curselection()
        if not selection: return
        index = selection[0]
        if index < len(self.ordered_selection) - 1:
            path = self.ordered_selection.pop(index)
            self.ordered_selection.insert(index + 1, path)
            self.update_listbox_from_data()
            self.listbox.select_set(index + 1)
            self.listbox.activate(index + 1)
            self.on_change()

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection: return
        path_to_remove = self.ordered_selection[selection[0]]
        self.toggle_file(path_to_remove) # This will remove it and trigger callbacks

    def open_selected_file(self, event=None):
        if event:
            clicked_index = self.listbox.nearest(event.y)
            if clicked_index == -1: return "break"
            bbox = self.listbox.bbox(clicked_index)
            if not bbox or event.y < bbox[1] or event.y > bbox[1] + bbox[3]: return "break"

        selection = self.listbox.curselection()
        if not selection: return "break"

        relative_path = self.listbox.get(selection[0])
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