import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from ... import constants as c
from ...core.paths import ICON_PATH
from ..style_manager import apply_dark_theme
from .step_details import DetailsView
from .step_concept import ConceptView
from .step_stack import StackView
from .step_todo import TodoView
from .step_generate import GenerateView
from .step_base_files import StepBaseFilesView
from .success_view import SuccessView
from ..window_utils import get_monitor_work_area
from . import starter_state
from ..info_manager import attach_info_mode
from ..assets import assets

from .starter_ui_builder import StarterUIBuilder
from .starter_navigation import StarterNavigation
from .starter_actions import StarterActions
from .starter_project_creator import StarterProjectCreator

class ProjectStarterDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.app = app

        self.finished_successfully = False
        self.starter_state = starter_state.StarterState()
        self.font_size = c.FONT_NORMAL[1]

        self.title("Project Starter")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)
        self.grab_set()

        apply_dark_theme(self)

        self.current_view = None
        self.tabs_frame = None
        self.tabs = []

        self.steps_map = {
            1: "Details",
            2: "Base Files",
            3: "Concept",
            4: "Stack",
            5: "TODO",
            6: "Generate"
        }

        # Sub-modules
        self.ui_builder = StarterUIBuilder(self)
        self.navigation = StarterNavigation(self)
        self.actions = StarterActions(self)
        self.project_creator = StarterProjectCreator(self)

        self.ui_builder.build_ui()

        self.starter_state.load()

        self.starter_state.project_data["name"].trace_add("write", lambda *args: self.navigation.update_nav_state())
        self.starter_state.project_data["name"].trace_add("write", self._update_window_title)
        self.starter_state.project_data["parent_folder"].trace_add("write", lambda *args: self.navigation.update_nav_state())
        self.starter_state.project_data["stack"].trace_add("write", lambda *args: self.navigation.update_nav_state())

        self.info_toggle_btn = tk.Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")
        self.info_mgr = attach_info_mode(self, self.app.app_state, manager_type='grid', grid_row=3, toggle_btn=self.info_toggle_btn)
        self._register_static_info()

        self.ui_builder.refresh_tabs()
        self._update_window_title()
        self._show_current_step_view()

        m_left, m_top, m_right, m_bottom = get_monitor_work_area(self.parent)
        self.attributes("-alpha", 0.0)
        self.geometry(f"600x400+{m_left + 50}+{m_top + 50}")
        self.deiconify()
        self.update_idletasks()
        self.state('zoomed')
        self.after(200, self._reveal_after_maximized)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Control-0>", self.reset_zoom)

    def _reveal_after_maximized(self):
        if not self.winfo_exists(): return
        self.attributes("-alpha", 1.0)
        self.focus_force()

    def _show_current_step_view(self):
        if hasattr(self, 'info_mgr'):
            self.info_mgr.clear_active_stack()

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view_frame = tk.Frame(self.content_frame, bg=c.DARK_BG)
        view_frame.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        step = self.starter_state.current_step

        if step > 3 and not self.starter_state.project_data["concept_md"]:
             messagebox.showerror("Concept Missing", "You must complete and merge the Concept document before moving to later steps.", parent=self)
             self.navigation.go_to_step(3)
             return
        if step == 6 and not self.starter_state.project_data["todo_md"]:
             messagebox.showerror("Content Missing", "You must complete and merge the TODO Plan before moving to the Generate step.", parent=self)
             self.navigation.go_to_step(5)
             return

        if step == 1: self.current_view = DetailsView(view_frame, self.starter_state.project_data, starter_controller=self)
        elif step == 2: self.current_view = StepBaseFilesView(view_frame, self, self.starter_state.project_data)
        elif step == 3: self.current_view = ConceptView(view_frame, self, self.starter_state.project_data)
        elif step == 4: self.current_view = StackView(view_frame, self, self.starter_state.project_data)
        elif step == 5: self.current_view = TodoView(view_frame, self, self.starter_state.project_data)
        elif step == 6: self.current_view = GenerateView(view_frame, self.starter_state.project_data, self.create_project, starter_controller=self)

        if self.current_view:
            self.current_view.pack(expand=True, fill="both")
            if hasattr(self.current_view, 'register_info'):
                self.current_view.register_info(self.info_mgr)

        self.ui_builder.update_tab_styles()
        self.navigation.update_navigation_controls()

    def _register_static_info(self):
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")
        self.info_mgr.register(self.prev_button, "starter_nav_prev")
        self.info_mgr.register(self.next_button, "starter_nav_next")
        self.info_mgr.register(self.start_over_button, "starter_nav_reset")
        self.info_mgr.register(self.btn_save, "starter_header_save")
        self.info_mgr.register(self.btn_load, "starter_header_load")
        if hasattr(self, 'btn_clear'):
            self.info_mgr.register(self.btn_clear, "starter_header_clear")

    def _update_window_title(self, *args):
        name = self.starter_state.project_data["name"].get().strip()
        if name:
            self.title(f"Project Starter - {name}")
        else:
            self.title("Project Starter")

    def create_project(self, llm_output, include_base_reference=False, project_pitch="a new project"):
        self.project_creator.create_project(llm_output, include_base_reference, project_pitch)

    def _display_success_screen(self, project_name, files, parent_folder, project_color=None):
        self.finished_successfully = True
        for w in self.content_frame.winfo_children(): w.destroy()
        self.nav_frame.grid_forget()
        def on_start_work():
            full_path = str(Path(parent_folder) / project_name)
            self.starter_state.reset()
            self.app.ui_callbacks.on_directory_selected(full_path)
            self.destroy()
            self.app.after(100, self.app.show_and_raise)
        SuccessView(self.content_frame, project_name, files, on_start_work, parent_folder, project_color=project_color).pack(expand=True, fill="both")

    def on_base_project_selected(self, path):
        self.ui_builder.refresh_tabs()

    def on_closing(self):
        self.starter_state.update_from_view(self.current_view)
        self.starter_state.save()
        if not self.finished_successfully:
            last_path = getattr(self.app, '_last_project_path', None)
            if last_path:
                self.app.project_actions.set_active_dir_display(last_path)
        self.destroy()

    def reset_zoom(self, event=None):
        self.font_size = c.FONT_NORMAL[1]
        if self.current_view and hasattr(self.current_view, 'refresh_fonts'):
            self.current_view.refresh_fonts()

    def adjust_font_size(self, delta):
        new_size = self.font_size + delta
        self.font_size = max(8, min(new_size, 40))
        if self.current_view and hasattr(self.current_view, 'refresh_fonts'):
            self.current_view.refresh_fonts()

    def _update_navigation_controls(self):
        self.navigation.update_navigation_controls()

    def update_nav_state(self):
        self.navigation.update_nav_state()