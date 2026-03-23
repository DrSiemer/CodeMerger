from tkinter import messagebox, filedialog
from . import session_manager

class StarterActions:
    def __init__(self, dialog):
        self.dialog = dialog

    def save_config(self):
        self.dialog.starter_state.update_from_view(self.dialog.current_view)
        project_name = self.dialog.starter_state.project_data["name"].get().strip()
        initial_file = f"{project_name}.json" if project_name else "project-config.json"
        filepath = filedialog.asksaveasfilename(title="Save Project Configuration", defaultextension=".json", initialfile=initial_file, filetypes=[("JSON files", "*.json")], parent=self.dialog)

        if not filepath: return

        session_manager.save_session_data(self.dialog.starter_state.get_dict(), filepath)
        messagebox.showinfo("Success", f"Configuration saved to:\n{filepath}", parent=self.dialog)

    def load_config(self):
        filepath = filedialog.askopenfilename(title="Load Project Configuration", filetypes=[("JSON files", "*.json")], defaultextension=".json", parent=self.dialog)
        if not filepath: return

        self.dialog.starter_state.update_from_view(self.dialog.current_view)
        self.dialog.starter_state.load(filepath)
        self.dialog.starter_state.save()
        self.dialog.starter_state.current_step = 1

        self.dialog.ui_builder.refresh_tabs()
        self.dialog._show_current_step_view()

    def start_over(self):
        if self.dialog.current_view and hasattr(self.dialog.current_view, 'handle_reset'):
            self.dialog.current_view.handle_reset()
            self.dialog.starter_state.update_from_view(self.dialog.current_view)
            self.dialog.starter_state.save()
            self.dialog.navigation.update_nav_state()

    def clear_session_data(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all project data and start fresh?", parent=self.dialog):
            self.dialog.starter_state.reset()
            self.dialog.ui_builder.refresh_tabs()
            self.dialog._show_current_step_view()