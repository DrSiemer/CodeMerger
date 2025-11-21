import tkinter as tk
import os
from . import session_manager

class WizardState:
    """
    Manages the data and progress state of the Project Wizard.
    Handles persistence via the session_manager.
    """
    def __init__(self, default_parent_folder):
        self.default_parent_folder = default_parent_folder
        self.current_step = 1
        self.max_accessible_step = 1

        self.project_data = {
            "name": tk.StringVar(),
            "parent_folder": tk.StringVar(value=default_parent_folder),
            "stack": tk.StringVar(),
            "goal": "",
            "concept_md": "",
            "todo_md": ""
        }

        # Setup auto-save triggers for UI-bound variables
        self.project_data["name"].trace_add("write", self.save)
        self.project_data["parent_folder"].trace_add("write", self.save)
        self.project_data["stack"].trace_add("write", self.save)

    def get_dict(self):
        """Returns a plain dictionary of the current state."""
        return {
            "name": self.project_data["name"].get(),
            "parent_folder": self.project_data["parent_folder"].get(),
            "stack": self.project_data["stack"].get(),
            "goal": self.project_data.get("goal", ""),
            "concept_md": self.project_data.get("concept_md", ""),
            "todo_md": self.project_data.get("todo_md", "")
        }

    def save(self, *args):
        """Persists the current state to the default session file."""
        session_manager.save_session_data(self.get_dict())

    def load(self, filepath=None):
        """
        Loads state from a file (or default session).
        Updates StringVars and recalculates max_accessible_step.
        """
        loaded_data = session_manager.load_session_data(filepath)
        self.project_data["name"].set(loaded_data.get("name", ""))

        loaded_parent = loaded_data.get("parent_folder", "")
        if loaded_parent and os.path.isdir(loaded_parent):
            self.project_data["parent_folder"].set(loaded_parent)
        else:
             self.project_data["parent_folder"].set(self.default_parent_folder)

        self.project_data["stack"].set(loaded_data.get("stack", ""))
        self.project_data["goal"] = loaded_data.get("goal", "")
        self.project_data["concept_md"] = loaded_data.get("concept_md", "")
        self.project_data["todo_md"] = loaded_data.get("todo_md", "")

        self._recalc_progress()

    def reset(self):
        """Clears all data and resets progress."""
        self.project_data["name"].set("")
        self.project_data["parent_folder"].set(self.default_parent_folder)
        self.project_data["stack"].set("")
        self.project_data["goal"] = ""
        self.project_data["concept_md"] = ""
        self.project_data["todo_md"] = ""
        session_manager.clear_default_session()
        self.current_step = 1
        self.max_accessible_step = 1

    def _recalc_progress(self):
        """Determines how far the user can navigate based on completed data."""
        has_details = self.project_data["name"].get() and self.project_data["parent_folder"].get()
        has_concept = bool(self.project_data["concept_md"])
        has_stack = bool(self.project_data["stack"].get())
        has_todo = bool(self.project_data["todo_md"])

        if has_details and has_concept and has_stack and has_todo:
            self.max_accessible_step = 5
        elif has_details and has_concept and has_stack:
            self.max_accessible_step = 4
        elif has_details and has_concept:
            self.max_accessible_step = 3
        elif has_details:
             self.max_accessible_step = 2
        else:
            self.max_accessible_step = 1

    def update_from_view(self, view):
        """Extracts data from the current view widget to update the state model."""
        if not view or not view.winfo_exists(): return

        # Step 1 data is bound to StringVars, updated automatically
        if self.current_step == 2:
            self.project_data["concept_md"] = view.get_concept_content()
            if hasattr(view, 'get_goal_content'):
                self.project_data["goal"] = view.get_goal_content()
        elif self.current_step == 3:
            self.project_data["stack"].set(view.get_stack_content())
        elif self.current_step == 4:
            self.project_data["todo_md"] = view.get_todo_content()