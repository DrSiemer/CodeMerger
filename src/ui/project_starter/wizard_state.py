import tkinter as tk
import os
from . import session_manager
from ... import constants as c
from .segment_manager import SegmentManager

class WizardState:
    """
    Manages the data and progress state of the Project Wizard.
    Handles persistence via the session_manager.
    """
    def __init__(self):
        self.current_step = 1
        self.max_accessible_step = 1

        self.project_data = {
            "name": tk.StringVar(),
            "parent_folder": tk.StringVar(value=""),
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
        c_segs = self.project_data.get("concept_segments", {})
        t_segs = self.project_data.get("todo_segments", {})

        concept_md_to_save = self.project_data.get("concept_md", "") if not c_segs else ""
        todo_md_to_save = self.project_data.get("todo_md", "") if not t_segs else ""

        return {
            "current_step": self.current_step,
            "name": self.project_data["name"].get(),
            "parent_folder": self.project_data["parent_folder"].get(),
            "stack": self.project_data["stack"].get(),
            "goal": self.project_data.get("goal", ""),
            "concept_md": concept_md_to_save,
            "todo_md": todo_md_to_save,
            "base_project_path": self.project_data["base_project_path"].get(),
            "base_project_files": self.project_data["base_project_files"],
            "include_base_reference": self.project_data["include_base_reference"].get(),
            "concept_segments": c_segs,
            "concept_signoffs": self.project_data.get("concept_signoffs", {}),
            "todo_phases": self.project_data.get("todo_phases", []),
            "todo_segments": t_segs,
            "todo_signoffs": self.project_data.get("todo_signoffs", {})
        }

    def save(self, *args):
        session_manager.save_session_data(self.get_dict())

    def load(self, filepath=None):
        loaded_data = session_manager.load_session_data(filepath)
        self.project_data["name"].set(loaded_data.get("name", ""))
        loaded_parent = loaded_data.get("parent_folder", "")
        self.project_data["parent_folder"].set(loaded_parent if loaded_parent and os.path.isdir(loaded_parent) else "")
        self.project_data["stack"].set(loaded_data.get("stack", ""))
        self.project_data["goal"] = loaded_data.get("goal", "")
        self.project_data["base_project_path"].set(loaded_data.get("base_project_path", ""))
        self.project_data["base_project_files"] = loaded_data.get("base_project_files", [])
        self.project_data["include_base_reference"].set(loaded_data.get("include_base_reference", True))

        self.project_data["concept_segments"] = loaded_data.get("concept_segments", {})
        self.project_data["concept_signoffs"] = loaded_data.get("concept_signoffs", {})
        if self.project_data["concept_segments"]:
            self.project_data["concept_md"] = SegmentManager.assemble_document(self.project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS)
        else:
            self.project_data["concept_md"] = loaded_data.get("concept_md", "")

        self.project_data["todo_phases"] = loaded_data.get("todo_phases", [])
        self.project_data["todo_segments"] = loaded_data.get("todo_segments", {})
        self.project_data["todo_signoffs"] = loaded_data.get("todo_signoffs", {})
        if self.project_data["todo_segments"]:
            self.project_data["todo_md"] = SegmentManager.assemble_document(self.project_data["todo_segments"], c.TODO_ORDER, c.TODO_PHASES)
        else:
            self.project_data["todo_md"] = loaded_data.get("todo_md", "")

        # Recalc validity to set the initial accessible step
        self._recalc_progress()

        saved_step = loaded_data.get("current_step", 1)
        if saved_step <= self.max_accessible_step:
            self.current_step = saved_step
        else:
            self.current_step = self.max_accessible_step

    def reset(self):
        self.project_data["name"].set("")
        self.project_data["parent_folder"].set("")
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
        """Calculates logic flags and updates max_accessible_step."""
        has_details = bool(self.project_data["name"].get())

        c_segs = self.project_data.get("concept_segments", {})
        c_signs = self.project_data.get("concept_signoffs", {})
        has_concept = False
        if c_segs:
            if all(c_signs.get(k) for k in c_segs.keys()):
                has_concept = True
        elif self.project_data.get("concept_md"):
            has_concept = True

        t_segs = self.project_data.get("todo_segments", {})
        t_signs = self.project_data.get("todo_signoffs", {})
        has_todo = False
        if t_segs:
            if all(t_signs.get(k) for k in t_segs.keys()):
                has_todo = True
        elif self.project_data.get("todo_md"):
            has_todo = True

        # Determine target max based on validity
        target_max = 1
        if has_details:
            target_max = 3
            if has_concept:
                target_max = 5
                if has_todo:
                    target_max = 6

        # NAVIGATION PROTECTION:
        # We only update max_accessible_step if the new calculated max is HIGHER.
        # This prevents tabs from "locking" if the user navigates backward into
        # a step that is in an intermediate state (e.g. they unsign a segment).
        if target_max > self.max_accessible_step:
            self.max_accessible_step = target_max

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
            view_type = str(type(view))
            if "Concept" in view_type: self.project_data["concept_md"] = content
            elif "Todo" in view_type: self.project_data["todo_md"] = content

        self._recalc_progress()