import tkinter as tk
import os
import logging
from pathlib import Path
from tkinter import messagebox, filedialog
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..style_manager import apply_dark_theme
from .step1_details import Step1DetailsView
from .step2_concept import Step2ConceptView
from .step3_stack import Step3StackView
from .step4_todo import Step4TodoView
from .step5_generate import Step5GenerateView
from .success_view import SuccessView
from ..window_utils import position_window
from . import session_manager, generator, wizard_state, wizard_validator

log = logging.getLogger("CodeMerger")

class ProjectStarterDialog(tk.Toplevel):
    """
    A wizard dialog for bootstrapping new software projects.
    Delegates state to WizardState and validation to WizardValidator.
    """
    def __init__(self, parent, app, default_parent_folder):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.app = app

        self.state = wizard_state.WizardState(default_parent_folder)

        self.title("Project Starter Wizard")
        if parent.iconbitmap():
            try:
                self.iconbitmap(parent.iconbitmap())
            except Exception: pass

        self.geometry(c.PROJECT_STARTER_GEOMETRY)
        self.minsize(700, 600)
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        apply_dark_theme(self)

        self.current_view = None
        self._build_ui()

        # Load previous session
        self.state.load()

        # Add traces to trigger validation updates when data changes
        self.state.project_data["name"].trace_add("write", lambda *args: self.update_nav_state())
        self.state.project_data["parent_folder"].trace_add("write", lambda *args: self.update_nav_state())
        self.state.project_data["stack"].trace_add("write", lambda *args: self.update_nav_state())

        self._show_current_step_view()

        position_window(self)
        self.deiconify()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=c.DARK_BG, padx=10, pady=10)
        main_frame.pack(expand=True, fill="both")

        # --- Header & Tabs ---
        header_frame = tk.Frame(main_frame, bg=c.DARK_BG)
        header_frame.pack(fill="x", pady=(0, 10), side="top")

        tabs_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        tabs_frame.pack(side="left", fill='x', expand=True)

        self.tabs = []
        tab_names = ["1. Details", "2. Concept", "3. Stack", "4. TODO", "5. Generate"]
        for i, name in enumerate(tab_names):
            tab = RoundedButton(
                tabs_frame,
                command=lambda step=i + 1: self._go_to_step(step),
                text=name, font=c.FONT_NORMAL, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT,
                height=32, radius=6, hollow=True, cursor="hand2"
            )
            tab.pack(side="left", padx=(0, 5), fill='x', expand=True)
            self.tabs.append(tab)

        # --- Header Buttons ---
        right_header_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        right_header_frame.pack(side="right")

        if self.app.assets.trash_icon_image:
             RoundedButton(
                right_header_frame, command=self._clear_session_data,
                image=self.app.assets.trash_icon_image,
                bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, width=32, height=32, radius=6, cursor="hand2"
            ).pack(side="right", padx=(0, 0))

        RoundedButton(
            right_header_frame, text="Load Config", command=self.load_config_from_dialog,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=32, radius=6, cursor="hand2"
        ).pack(side="right", padx=(0, 10))

        # --- Footer Nav ---
        self.nav_frame = tk.Frame(main_frame, bg=c.DARK_BG)
        self.nav_frame.pack(fill="x", pady=(10, 0), side="bottom")

        self.prev_button = RoundedButton(self.nav_frame, text="< Prev", command=self._go_to_prev_step, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.start_over_button = RoundedButton(self.nav_frame, text="Reset this step", command=self._start_over, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.next_button = RoundedButton(self.nav_frame, text="Next >", command=self._go_to_next_step, height=30, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor="hand2")

        # --- Main Content ---
        self.content_frame = tk.Frame(main_frame, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        self.content_frame.pack(expand=True, fill="both", side="top")

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
        self.state.save() # Save to session immediately
        self.state.current_step = 1
        self._show_current_step_view()

    def _start_over(self):
        if self.current_view and hasattr(self.current_view, 'handle_reset'):
            self.current_view.handle_reset()
            self.state.update_from_view(self.current_view)
            self.state.save()

    def _clear_session_data(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all project data and start fresh?", parent=self):
            self.state.reset()
            self._show_current_step_view()

    def _go_to_next_step(self):
        if self.state.current_step < 5:
            self._go_to_step(self.state.current_step + 1)

    def _go_to_prev_step(self):
        if self.state.current_step > 1:
            self._go_to_step(self.state.current_step - 1)

    def _go_to_step(self, target_step):
        if target_step == self.state.current_step: return

        # Save current view data before moving
        self.state.update_from_view(self.current_view)
        self.state.save()

        # Validate if moving forward
        if target_step > self.state.current_step:
            is_valid, err_title, err_msg = wizard_validator.validate_step(self.state.current_step, self.state.project_data)
            if not is_valid:
                messagebox.showerror(err_title, err_msg, parent=self)
                return
            # Update max accessible step
            self.state.max_accessible_step = max(self.state.max_accessible_step, target_step)

        if target_step > self.state.max_accessible_step:
            return

        self.state.current_step = target_step
        self._show_current_step_view()

    def _show_current_step_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view_frame = tk.Frame(self.content_frame, bg=c.DARK_BG, padx=10, pady=10)
        view_frame.pack(expand=True, fill="both")

        step = self.state.current_step

        # Pre-check dependencies
        if step > 2 and not self.state.project_data["concept_md"]:
            messagebox.showerror("Concept Missing", "Complete Concept step first.", parent=self)
            self._go_to_step(2); return
        if step > 3 and not self.state.project_data["stack"].get():
            messagebox.showerror("Stack Missing", "Complete Code Stack step first.", parent=self)
            self._go_to_step(3); return
        if step == 5 and not self.state.project_data["todo_md"]:
            messagebox.showerror("Content Missing", "Complete TODO step first.", parent=self)
            self._go_to_step(4); return

        if step == 1:
            self.current_view = Step1DetailsView(view_frame, self.state.project_data)
        elif step == 2:
            self.current_view = Step2ConceptView(view_frame, self, self.state.project_data)
        elif step == 3:
            self.current_view = Step3StackView(view_frame, self, self.state.project_data)
        elif step == 4:
            self.current_view = Step4TodoView(view_frame, self, self.state.project_data)
        elif step == 5:
            self.current_view = Step5GenerateView(view_frame, self.state.project_data, self.create_project)

        if self.current_view:
            self.current_view.pack(expand=True, fill="both")

        self._update_tab_styles()
        self._update_navigation_controls()

    def _update_navigation_controls(self):
        self.prev_button.pack_forget()
        self.start_over_button.pack_forget()
        self.next_button.pack_forget()

        if self.state.current_step > 1: self.prev_button.pack(side="left")
        if self.state.current_step < 5: self.next_button.pack(side="right")

        can_reset = False
        if self.current_view:
            if hasattr(self.current_view, 'is_step_in_progress'):
                can_reset = self.current_view.is_step_in_progress()
            elif hasattr(self.current_view, 'is_editor_visible'):
                can_reset = self.current_view.is_editor_visible()

        if can_reset: self.start_over_button.pack()

        # Trigger validation state for Next button
        self.update_nav_state()

    def update_nav_state(self):
        """Checks the current step's validity and enables/disables the Next button."""
        if self.state.current_step < 5:
            # We temporarily update the model from the view if possible, to get real-time text widget data
            # This allows validation without saving to disk every keystroke
            if self.current_view and hasattr(self.current_view, 'get_stack_content') and self.state.current_step == 3:
                 # Special handling for Step 3 to get live text without forcing a save
                 pass

            is_valid, _, _ = wizard_validator.validate_step(self.state.current_step, self.state.project_data)
            self.next_button.set_state('normal' if is_valid else 'disabled')

    def _update_tab_styles(self):
        for i, tab in enumerate(self.tabs):
            is_active = (i + 1) == self.state.current_step
            is_accessible = (i + 1) <= self.state.max_accessible_step

            tab.set_state('normal' if is_accessible else 'disabled')
            tab.config(hollow=(not is_active),
                      bg=(c.BTN_BLUE if is_active else c.BTN_GRAY_BG),
                      fg=(c.BTN_BLUE_TEXT if is_active else (c.TEXT_COLOR if is_accessible else c.BTN_GRAY_TEXT)))

    def create_project(self, llm_output):
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

        # 2. Write Files
        success, files_created, msg = generator.parse_and_write_files(project_path, llm_output)
        if not success:
            messagebox.showerror("Error", msg, parent=self)
            return

        # 3. Save Config to new project
        self.state.update_from_view(self.current_view)
        self.state.save()
        session_manager.save_session_data(self.state.get_dict(), project_path / "project-starter.json")

        self._display_success_screen(project_path.name, files_created, parent_folder)

    def _display_success_screen(self, project_name, files, parent_folder):
        for w in self.content_frame.winfo_children(): w.destroy()
        self.nav_frame.pack_forget()

        def on_start_work():
            full_path = str(Path(parent_folder) / project_name)
            # Load defaults
            from ...core.utils import load_config
            conf = load_config()
            intro = conf.get('default_intro_prompt', c.DEFAULT_INTRO_PROMPT).replace('REPLACE_ME', project_name)
            outro = conf.get('default_outro_prompt', c.DEFAULT_OUTRO_PROMPT)

            self.app.project_manager.create_project_with_defaults(full_path, intro, outro)
            self.state.reset()
            self.app.ui_callbacks.on_directory_selected(full_path)
            self.destroy()

        SuccessView(self.content_frame, project_name, files, on_start_work, parent_folder).pack(expand=True, fill="both")