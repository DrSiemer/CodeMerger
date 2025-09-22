from tkinter import messagebox
from ... import constants as c

class FileManagerStateController:
    def __init__(self, window):
        self.window = window

    def is_state_changed(self):
        if self.window.selection_handler.ordered_selection != self.window.project_config.selected_files:
            return True
        current_expanded = set(self.window.tree_handler.get_expanded_dirs())
        if current_expanded != self.window.project_config.expanded_dirs:
            return True
        return False

    def on_closing(self):
        if self.is_state_changed():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before closing?",
                parent=self.window
            )
            if response is True:
                self.save_and_close()
            elif response is False:
                self.window._close_and_save_geometry()
        else:
            self.window._close_and_save_geometry()

    def save_and_close(self):
        project = self.window.project_config
        project.selected_files = self.window.selection_handler.ordered_selection
        project.expanded_dirs = set(self.window.tree_handler.get_expanded_dirs())
        project.total_tokens = self.window.current_total_tokens
        current_paths = {f['path'] for f in project.selected_files}
        project.known_files = list(set(project.known_files) | current_paths)
        project.save()
        self.window.status_var.set("File selection and order saved to .allcode")
        self.window._close_and_save_geometry()

    def select_all_files(self):
        all_paths = self.window.tree_handler.get_all_file_paths_in_tree_order()
        current_paths = {f['path'] for f in self.window.selection_handler.ordered_selection}
        paths_to_add = [p for p in all_paths if p not in current_paths]

        if not paths_to_add:
            self.window.status_var.set("No new files to add")
            return

        threshold = self.window.app_state.config.get('add_all_warning_threshold', c.ADD_ALL_WARNING_THRESHOLD_DEFAULT)
        if len(paths_to_add) > threshold:
            if not messagebox.askyesno(
                "Confirm Adding Files",
                f"You are about to add {len(paths_to_add)} files to the merge list.\n\nAre you sure?",
                parent=self.window
            ):
                self.window.status_var.set("Operation cancelled by user.")
                return

        self.window.selection_handler.add_files(paths_to_add)
        self.window.status_var.set(f"Added {len(paths_to_add)} file(s) to the merge list")

    def remove_all_files(self):
        if not self.window.selection_handler.ordered_selection:
            self.window.status_var.set("Merge list is already empty")
            return
        if messagebox.askyesno("Confirm Removal", "Remove all files from the merge list?", parent=self.window):
            count = len(self.window.selection_handler.ordered_selection)
            self.window.selection_handler.remove_all_files()
            self.window.status_var.set(f"Removed {count} file(s) from the merge list")