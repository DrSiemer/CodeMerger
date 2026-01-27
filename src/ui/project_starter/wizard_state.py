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
            "todo_md": "",
            "base_project_path": tk.StringVar(),
            "base_project_files": [],
            "include_base_reference": tk.BooleanVar(value=True),

            "concept_segments": {},
            "concept_signoffs": {},
            "todo_phases": [],
            "todo_segments": {},
            "todo_signoffs": {},
        }

        self.project_data["name"].trace_add("write", self.save)
        self.project_data["parent_folder"].trace_add("write", self.save)
        self.project_data["stack"].trace_add("write", self.save)
        self.project_data["base_project_path"].trace_add("write", self.save)

    def get_dict(self):
        return {
            "current_step": self.current_step,
            "name": self.project_data["name"].get(),
            "parent_folder": self.project_data["parent_folder"].get(),
            "stack": self.project_data["stack"].get(),
            "goal": self.project_data.get("goal", ""),
            "concept_md": self.project_data.get("concept_md", ""),
            "todo_md": self.project_data.get("todo_md", ""),
            "base_project_path": self.project_data["base_project_path"].get(),
            "base_project_files": self.project_data["base_project_files"],
            "include_base_reference": self.project_data["include_base_reference"].get(),

            "concept_segments": self.project_data.get("concept_segments", {}),
            "concept_signoffs": self.project_data.get("concept_signoffs", {}),
            "todo_phases": self.project_data.get("todo_phases", []),
            "todo_segments": self.project_data.get("todo_segments", {}),
            "todo_signoffs": self.project_data.get("todo_signoffs", {})
        }

    def save(self, *args):
        session_manager.save_session_data(self.get_dict())

    def load(self, filepath=None):
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
        self.project_data["base_project_path"].set(loaded_data.get("base_project_path", ""))
        self.project_data["base_project_files"] = loaded_data.get("base_project_files", [])
        self.project_data["include_base_reference"].set(loaded_data.get("include_base_reference", True))

        self.project_data["concept_segments"] = loaded_data.get("concept_segments", {})
        self.project_data["concept_signoffs"] = loaded_data.get("concept_signoffs", {})
        self.project_data["todo_phases"] = loaded_data.get("todo_phases", [])
        self.project_data["todo_segments"] = loaded_data.get("todo_segments", {})
        self.project_data["todo_signoffs"] = loaded_data.get("todo_signoffs", {})

        self._recalc_progress()

        saved_step = loaded_data.get("current_step", 1)
        if saved_step <= self.max_accessible_step:
            self.current_step = saved_step
        else:
            self.current_step = self.max_accessible_step

    def reset(self):
        self.project_data["name"].set("")
        self.project_data["parent_folder"].set(self.default_parent_folder)
        self.project_data["stack"].set("")
        self.project_data["goal"] = ""
        self.project_data["concept_md"] = ""
        self.project_data["todo_md"] = ""
        self.project_data["base_project_path"].set("")
        self.project_data["base_project_files"] = []
        self.project_data["include_base_reference"].set(True)

        self.project_data["concept_segments"] = {}
        self.project_data["concept_signoffs"] = {}
        self.project_data["todo_phases"] = []
        self.project_data["todo_segments"] = {}
        self.project_data["todo_signoffs"] = {}

        session_manager.clear_default_session()
        self.current_step = 1
        self.max_accessible_step = 1

    def _recalc_progress(self):
        has_details = bool(self.project_data["name"].get() and self.project_data["parent_folder"].get())

        c_segs = self.project_data.get("concept_segments", {})
        c_signs = self.project_data.get("concept_signoffs", {})
        has_concept = False
        if c_segs:
            has_concept = all(c_signs.get(k) for k in c_segs.keys())
        elif self.project_data.get("concept_md"):
            has_concept = True

        t_segs = self.project_data.get("todo_segments", {})
        t_signs = self.project_data.get("todo_signoffs", {})
        has_todo = False
        if t_segs:
            has_todo = all(t_signs.get(k) for k in t_segs.keys())
        elif self.project_data.get("todo_md"):
            has_todo = True

        self.max_accessible_step = 1

        if has_details:
            self.max_accessible_step = 3
            if has_concept:
                self.max_accessible_step = 5
                if has_todo:
                    self.max_accessible_step = 6

    def update_from_view(self, view):
        if not view or not view.winfo_exists(): return

        if hasattr(view, 'save_state'):
             view.save_state()

        if hasattr(view, 'get_goal_content'):
            self.project_data["goal"] = view.get_goal_content()

        if hasattr(view, 'get_stack_content'):
            self.project_data["stack"].set(view.get_stack_content())

        if hasattr(view, 'get_assembled_content'):
            content, _, _ = view.get_assembled_content()
            # Determine which step we are in to update correct assembled field
            view_type = str(type(view))
            if "Concept" in view_type:
                self.project_data["concept_md"] = content
            elif "Todo" in view_type:
                self.project_data["todo_md"] = content

        self._recalc_progress()