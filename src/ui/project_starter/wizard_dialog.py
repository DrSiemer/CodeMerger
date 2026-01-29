import tkinter as tk
import os
import logging
from pathlib import Path
from tkinter import messagebox, filedialog
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..style_manager import apply_dark_theme
from .step_details import DetailsView
from .step_concept import ConceptView
from .step_stack import StackView
from .step_todo import TodoView
from .step_generate import GenerateView
from .step_base_files import StepBaseFilesView
from .success_view import SuccessView
from ..window_utils import position_window
from . import session_manager, generator, wizard_state, wizard_validator
from ..tooltip import ToolTip

log = logging.getLogger("CodeMerger")

class ProjectStarterDialog(tk.Toplevel):
    """
    A wizard dialog for bootstrapping new software projects.
    Delegates state to WizardState and validation to WizardValidator.
    """
    def __init__(self, parent, app):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.app = app

        # Initialize the state manager
        self.state = wizard_state.WizardState()

        # Font Scaling State (Unified)
        self.font_size = c.FONT_NORMAL[1] # Default 12

        self.title("Project Starter Wizard")
        if parent.iconbitmap():
            try:
                self.iconbitmap(parent.iconbitmap())
            except Exception: pass

        self.geometry(c.PROJECT_STARTER_GEOMETRY)
        self.minsize(900, 700)
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

        self._build_ui()

        # Load previous session
        self.state.load()

        # Add traces to trigger validation updates when data changes
        self.state.project_data["name"].trace_add("write", lambda *args: self.update_nav_state())
        self.state.project_data["parent_folder"].trace_add("write", lambda *args: self.update_nav_state())
        self.state.project_data["stack"].trace_add("write", lambda *args: self.update_nav_state())

        self._refresh_tabs()
        self._show_current_step_view()

        position_window(self)
        self.deiconify()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Control-0>", self.reset_zoom)

    def reset_zoom(self, event=None):
        """Resets font size to default."""
        self.font_size = c.FONT_NORMAL[1]
        if self.current_view and hasattr(self.current_view, 'refresh_fonts'):
            self.current_view.refresh_fonts()

    def adjust_font_size(self, delta):
        """Adjusts the font size for all wizard components simultaneously."""
        new_size = self.font_size + delta
        self.font_size = max(8, min(new_size, 40))
        if self.current_view and hasattr(self.current_view, 'refresh_fonts'):
            self.current_view.refresh_fonts()

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=c.DARK_BG, padx=10, pady=10)
        main_frame.pack(expand=True, fill="both")

        # --- Header & Tabs ---
        header_frame = tk.Frame(main_frame, bg=c.DARK_BG)
        header_frame.pack(fill="x", pady=(0, 10), side="top")

        self.tabs_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        self.tabs_frame.pack(side="left", fill='x', expand=True)

        # --- Header Buttons ---
        right_header_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        right_header_frame.pack(side="right")

        if self.app.assets.trash_icon_image:
             btn_clear = RoundedButton(
                right_header_frame, command=self._clear_session_data,
                image=self.app.assets.trash_icon_image,
                bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, width=32, height=32, radius=6, cursor="hand2"
            )
             btn_clear.pack(side="right", padx=(0, 0))
             ToolTip(btn_clear, "Clear all wizard progress and start fresh", delay=500)

        btn_load = RoundedButton(
            right_header_frame, text="Load Config", command=self.load_config_from_dialog,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=32, radius=6, cursor="hand2"
        )
        btn_load.pack(side="right", padx=(0, 10))
        ToolTip(btn_load, "Load a previously saved project configuration file", delay=500)

        # --- Footer Nav ---
        self.nav_frame = tk.Frame(main_frame, bg=c.DARK_BG)
        self.nav_frame.pack(fill="x", pady=(10, 0), side="bottom")

        self.prev_button = RoundedButton(self.nav_frame, text="< Prev", command=self._go_to_prev_step, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        ToolTip(self.prev_button, "Go back to the previous step", delay=500)

        self.start_over_button = RoundedButton(self.nav_frame, text="Reset this step", command=self._start_over, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        ToolTip(self.start_over_button, "Clear the inputs for the current step", delay=500)

        self.next_button = RoundedButton(self.nav_frame, text="Next >", command=self._go_to_next_step, height=30, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.next_tooltip = ToolTip(self.next_button, "Validate current inputs and proceed", delay=500)

        # --- Main Content ---
        self.content_frame = tk.Frame(main_frame, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        self.content_frame.pack(expand=True, fill="both", side="top")

    def create_project(self, llm_output, include_base_reference=False):
        """Processes the LLM output and creates the actual files on disk."""
        # Validate the current step (6) before proceeding to force folder selection
        is_valid, err_title, err_msg = wizard_validator.validate_step(6, self.state.project_data)
        if not is_valid:
            messagebox.showerror(err_title, err_msg, parent=self)
            return

        if not llm_output.strip():
            messagebox.showerror("Error", "LLM Result text area is empty.", parent=self)
            return

        project_name = self.state.project_data["name"].get()
        parent_folder = self.state.project_data["parent_folder"].get()

        # 1. Prepare Directory
        success, project_path, msg = generator.prepare_project_directory(parent_folder, project_name)
        if not success:
            if "already exists" in msg:
                if messagebox.askyesno("Warning", f"{msg} Overwrite?", parent=self):
                    success, project_path, msg = generator.prepare_project_directory(parent_folder, project_name, overwrite=True)
                else: return

            if not success:
                messagebox.showerror("Error", msg, parent=self)
                return

        # 2. Write Files from LLM
        success, files_created, msg = generator.parse_and_write_files(project_path, llm_output)
        if not success:
            messagebox.showerror("Error", msg, parent=self)
            return

        # 3. Optional: Write Base Project Reference
        if include_base_reference:
            base_path = self.state.project_data["base_project_path"].get()
            base_files = self.state.project_data["base_project_files"]
            if generator.write_base_reference_file(project_path, base_path, base_files):
                files_created.append("project_reference.md")

        # 4. Save Config to new project
        self.state.update_from_view(self.current_view)
        self.state.save()
        session_manager.save_session_data(self.state.get_dict(), project_path / "project-starter.json")

        self._display_success_screen(project_path.name, files_created, parent_folder)

    def _get_active_steps(self):
        """Returns the list of active step IDs based on whether a base project is selected."""
        steps = [1]
        if self.state.project_data["base_project_path"].get():
            steps.append(2)
        steps.extend([3, 4, 5, 6])
        return steps

    def _refresh_tabs(self):
        if not self.tabs_frame: return
        for t in self.tabs: t.destroy()
        self.tabs = []

        active_steps = self._get_active_steps()
        for i, step_id in enumerate(active_steps):
            name = self.steps_map[step_id]
            tab = RoundedButton(
                self.tabs_frame,
                command=lambda s=step_id: self._go_to_step(s),
                text=f"{i+1}. {name}", font=c.FONT_NORMAL, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT,
                height=32, radius=6, hollow=True, cursor="hand2"
            )
            tab.pack(side="left", padx=(0, 5), fill='x', expand=True)
            ToolTip(tab, f"Jump to {name} step", delay=500)
            self.tabs.append(tab)
        self._update_tab_styles()

    def on_base_project_selected(self, path):
        """Called by Step 1 view when a base project is selected."""
        self._refresh_tabs()

    def on_closing(self):
        self.state.update_from_view(self.current_view)
        self.state.save()
        self.destroy()

    def load_config_from_dialog(self):
        filepath = filedialog.askopenfilename(
            title="Load Project Configuration",
            filetypes=[("JSON files", "*.json")],
            defaultextension=".json",
            parent=self
        )
        if not filepath: return
        self.state.update_from_view(self.current_view)
        self.state.load(filepath)
        self.state.save()
        self.state.current_step = 1
        self._refresh_tabs()
        self._show_current_step_view()

    def _start_over(self):
        if self.current_view and hasattr(self.current_view, 'handle_reset'):
            self.current_view.handle_reset()
            self.state.update_from_view(self.current_view)
            self.state.save()
            # Explicitly refresh navigation because the view state changed
            self.update_nav_state()

    def _clear_session_data(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all project data and start fresh?", parent=self):
            self.state.reset()
            self._refresh_tabs()
            self._show_current_step_view()

    def _go_to_next_step(self):
        active_steps = self._get_active_steps()
        if self.state.current_step in active_steps:
            current_idx = active_steps.index(self.state.current_step)
            if current_idx < len(active_steps) - 1:
                self._go_to_step(active_steps[current_idx + 1])

    def _go_to_prev_step(self):
        active_steps = self._get_active_steps()
        if self.state.current_step in active_steps:
            current_idx = active_steps.index(self.state.current_step)
            if current_idx > 0:
                self._go_to_step(active_steps[current_idx - 1])

    def _go_to_step(self, target_step_id):
        if target_step_id == self.state.current_step: return

        # Prevent jumping to locked steps via tab clicks
        is_accessible = (target_step_id <= self.state.max_accessible_step) or (target_step_id == 2)
        if not is_accessible:
            return

        self.state.update_from_view(self.current_view)
        self.state.save()

        if target_step_id > self.state.current_step:
            is_valid, err_title, err_msg = wizard_validator.validate_step(self.state.current_step, self.state.project_data)
            if not is_valid:
                messagebox.showerror(err_title, err_msg, parent=self)
                return
            self.state.max_accessible_step = max(self.state.max_accessible_step, target_step_id)

        self.state.current_step = target_step_id
        self._show_current_step_view()

    def _show_current_step_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view_frame = tk.Frame(self.content_frame, bg=c.DARK_BG, padx=10, pady=10)
        view_frame.pack(expand=True, fill="both")

        step = self.state.current_step
        if step > 3 and not self.state.project_data["concept_md"]:
             messagebox.showerror("Concept Missing", "Complete Concept step first.", parent=self)
             self._go_to_step(3); return
        if step == 6 and not self.state.project_data["todo_md"]:
             messagebox.showerror("Content Missing", "Complete TODO step first.", parent=self)
             self._go_to_step(5); return

        if step == 1:
            self.current_view = DetailsView(view_frame, self.state.project_data, wizard_controller=self)
        elif step == 2:
            self.current_view = StepBaseFilesView(view_frame, self, self.state.project_data)
        elif step == 3:
            self.current_view = ConceptView(view_frame, self, self.state.project_data)
        elif step == 4:
            self.current_view = StackView(view_frame, self, self.state.project_data)
        elif step == 5:
            self.current_view = TodoView(view_frame, self, self.state.project_data)
        elif step == 6:
            self.current_view = GenerateView(view_frame, self.state.project_data, self.create_project, wizard_controller=self)

        if self.current_view:
            self.current_view.pack(expand=True, fill="both")

        self._update_tab_styles()
        self._update_navigation_controls()

    def _update_navigation_controls(self):
        self.prev_button.pack_forget()
        self.start_over_button.pack_forget()
        self.next_button.pack_forget()

        active_steps = self._get_active_steps()
        current_idx = active_steps.index(self.state.current_step)

        if current_idx > 0: self.prev_button.pack(side="left")
        if current_idx < len(active_steps) - 1: self.next_button.pack(side="right")

        can_reset = False
        if self.current_view:
            if hasattr(self.current_view, 'is_step_in_progress'):
                can_reset = self.current_view.is_step_in_progress()
            elif hasattr(self.current_view, 'is_editor_visible'):
                can_reset = self.current_view.is_editor_visible()

        if can_reset: self.start_over_button.pack()
        self.update_nav_state()

    def update_nav_state(self):
        """Updates the visual state and text of the Next button based on phase validity."""
        if self.state.current_step == 6:
            return

        # Default text reset
        self.next_button.config(text="Next >")

        # Step 2 (Base Files) is optional
        if self.state.current_step == 2:
            self.next_button.set_state('normal')
            self.next_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.next_tooltip.text = "Skip or confirm base files and proceed"
            return

        # Step 4 (Stack) is optional but uses "Skip" text if empty
        if self.state.current_step == 4:
            stack_val = self.state.project_data["stack"].get()
            if not stack_val.strip():
                # Blue "Skip" button
                self.next_button.config(text="Skip", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
                self.next_tooltip.text = "Proceed without defining a specific stack"
            else:
                # Green "Next" button
                self.next_button.config(text="Next >", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
                self.next_tooltip.text = "Confirm stack and proceed to TODO plan"
            self.next_button.set_state('normal')
            return

        # Standard Step Validation (1, 3, 5)
        is_valid, _, _ = wizard_validator.validate_step(self.state.current_step, self.state.project_data)

        if is_valid:
            self.next_button.set_state('normal')
            self.next_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.next_tooltip.text = "Move to the next step"
        else:
            self.next_button.set_state('disabled')
            # Reset to default blue when disabled
            self.next_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.next_tooltip.text = "Please complete the required fields to continue"

    def _update_tab_styles(self):
        active_steps = self._get_active_steps()
        for i, tab in enumerate(self.tabs):
            step_id = active_steps[i]
            is_active = (step_id == self.state.current_step)
            is_accessible = (step_id <= self.state.max_accessible_step) or (step_id == 2)
            tab.set_state('normal' if is_accessible else 'disabled')
            tab.config(hollow=(not is_active),
                      bg=(c.BTN_BLUE if is_active else c.BTN_GRAY_BG),
                      fg=(c.BTN_BLUE_TEXT if is_active else (c.TEXT_COLOR if is_accessible else c.BTN_GRAY_TEXT)))

    def _display_success_screen(self, project_name, files, parent_folder):
        for w in self.content_frame.winfo_children(): w.destroy()
        self.nav_frame.pack_forget()

        def on_start_work():
            full_path = str(Path(parent_folder) / project_name)
            from ...core.utils import load_config
            conf = load_config()
            intro = conf.get('default_intro_prompt', c.DEFAULT_INTRO_PROMPT).replace('REPLACE_ME', project_name)
            outro = conf.get('default_outro_prompt', c.DEFAULT_OUTRO_PROMPT)
            normalized_files = [f.replace('\\', '/') for f in files]
            self.app.project_manager.create_project_with_defaults(full_path, intro, outro, initial_selected_files=normalized_files)
            self.state.reset()
            self.app.ui_callbacks.on_directory_selected(full_path)
            self.destroy()
            self.app.after(100, self.app.show_and_raise)

        SuccessView(self.content_frame, project_name, files, on_start_work, parent_folder).pack(expand=True, fill="both")