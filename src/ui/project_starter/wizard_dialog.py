import tkinter as tk
import logging
import json
import os
from pathlib import Path
import shutil
import re
from tkinter import messagebox, filedialog
from ... import constants as c
from ...core.paths import PERSISTENT_DATA_DIR
from ..widgets.rounded_button import RoundedButton
from ..style_manager import apply_dark_theme
from .step1_details import Step1DetailsView
from .step2_concept import Step2ConceptView
from .step3_todo import Step3TodoView
from .step4_generate import Step4GenerateView
from .success_view import SuccessView
from ..window_utils import position_window

log = logging.getLogger("CodeMerger")

class ProjectStarterDialog(tk.Toplevel):
    """
    A wizard dialog for bootstrapping new software projects with persistence.
    """
    def __init__(self, parent, app, default_parent_folder):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.app = app
        self.default_parent_folder = default_parent_folder
        self.session_file = os.path.join(PERSISTENT_DATA_DIR, "project_starter_session.json")

        self.title("Project Starter Wizard")

        if parent.iconbitmap():
            try:
                self.iconbitmap(parent.iconbitmap())
            except Exception:
                pass

        self.geometry(c.PROJECT_STARTER_GEOMETRY)
        self.minsize(700, 600)
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        apply_dark_theme(self)

        # State variables
        self.current_step = 1
        self.max_accessible_step = 1

        self.project_data = {
            "name": tk.StringVar(),
            "parent_folder": tk.StringVar(value=self.default_parent_folder),
            "stack": tk.StringVar(),
            "description": "",
            "goal": "",
            "concept_md": "",
            "todo_md": ""
        }

        # Setup auto-save triggers
        self.project_data["name"].trace_add("write", self._save_state)
        self.project_data["parent_folder"].trace_add("write", self._save_state)
        self.project_data["stack"].trace_add("write", self._save_state)

        self.current_view = None
        self._build_ui()

        # Load previous session or default
        self._load_state()

        self._show_current_step_view()

        position_window(self)
        self.deiconify()
        self.focus_force()

        # Ensure saving on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=c.DARK_BG, padx=10, pady=10)
        main_frame.pack(expand=True, fill="both")

        header_frame = tk.Frame(main_frame, bg=c.DARK_BG)
        header_frame.pack(fill="x", pady=(0, 10), side="top")

        tabs_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        tabs_frame.pack(side="left", fill='x', expand=True)

        self.tabs = []
        tab_names = ["1. Details", "2. Concept", "3. TODO", "4. Generate & Create"]
        for i, name in enumerate(tab_names):
            tab = RoundedButton(
                tabs_frame,
                command=lambda step=i + 1: self._go_to_step(step),
                text=name,
                font=c.FONT_NORMAL,
                bg=c.BTN_BLUE,
                fg=c.BTN_BLUE_TEXT,
                height=32,
                radius=6,
                hollow=True,
                cursor="hand2"
            )
            tab.pack(side="left", padx=(0, 5), fill='x', expand=True)
            self.tabs.append(tab)

        # Create a container for the right-aligned buttons to ensure proper order
        right_header_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        right_header_frame.pack(side="right")

        if self.app.assets.trash_icon_image:
             self.clear_session_button = RoundedButton(
                right_header_frame,
                command=self._clear_session_data,
                image=self.app.assets.trash_icon_image,
                bg=c.BTN_GRAY_BG,
                fg=c.BTN_GRAY_TEXT,
                width=32,
                height=32,
                radius=6,
                cursor="hand2"
            )
             self.clear_session_button.pack(side="right", padx=(0, 0))

        self.load_config_button = RoundedButton(
            right_header_frame,
            text="Load Config",
            command=self.load_config_from_dialog,
            bg=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON,
            height=32,
            radius=6,
            cursor="hand2"
        )
        self.load_config_button.pack(side="right", padx=(0, 10))

        self.nav_frame = tk.Frame(main_frame, bg=c.DARK_BG)
        self.nav_frame.pack(fill="x", pady=(10, 0), side="bottom")

        self.content_frame = tk.Frame(
            main_frame, bg=c.DARK_BG,
            highlightbackground=c.WRAPPER_BORDER, highlightthickness=1
        )
        self.content_frame.pack(expand=True, fill="both", side="top")

        self.prev_button = RoundedButton(self.nav_frame, text="< Prev", command=self._go_to_prev_step, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.start_over_button = RoundedButton(self.nav_frame, text="Reset this step", command=self._start_over, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.next_button = RoundedButton(self.nav_frame, text="Next >", command=self._go_to_next_step, height=30, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor="hand2")

    def on_closing(self):
        """Handles the window close event by saving one last time and exiting."""
        self._save_current_view_data()
        self._save_state()
        self.destroy()

    # --- State Persistence ---

    def _save_state(self, *args):
        """Saves the current project_data to the session file."""
        # If we are currently typing in a text field (description, etc),
        # the trace on StringVars won't catch it. We rely on _save_current_view_data
        # being called before navigation/closing.

        state_to_save = {
            "name": self.project_data["name"].get(),
            "parent_folder": self.project_data["parent_folder"].get(),
            "stack": self.project_data["stack"].get(),
            "description": self.project_data.get("description", ""),
            "goal": self.project_data.get("goal", ""),
            "concept_md": self.project_data.get("concept_md", ""),
            "todo_md": self.project_data.get("todo_md", "")
        }
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(state_to_save, f, indent=2)
        except Exception as e:
            log.error(f"Failed to save project starter session: {e}")

    def _load_state(self, filepath=None):
        """Loads project_data from a given file path (defaults to session file)."""
        target_path = filepath if filepath else self.session_file

        if not os.path.exists(target_path):
            return

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)

            self.project_data["name"].set(loaded_data.get("name", ""))

            # If loading a specific config, use its folder. If loading session, validate it.
            loaded_parent = loaded_data.get("parent_folder", "")
            if loaded_parent and os.path.isdir(loaded_parent):
                self.project_data["parent_folder"].set(loaded_parent)
            else:
                 self.project_data["parent_folder"].set(self.default_parent_folder)

            self.project_data["stack"].set(loaded_data.get("stack", ""))
            self.project_data["description"] = loaded_data.get("description", "")
            self.project_data["goal"] = loaded_data.get("goal", "")
            self.project_data["concept_md"] = loaded_data.get("concept_md", "")
            self.project_data["todo_md"] = loaded_data.get("todo_md", "")

            # Determine progress
            has_details = self.project_data["name"].get() and self.project_data["stack"].get() and self.project_data["description"]
            has_concept = bool(self.project_data["concept_md"])
            has_todo = bool(self.project_data["todo_md"])

            if has_details and has_concept and has_todo:
                self.max_accessible_step = 4
            elif has_details and has_concept:
                self.max_accessible_step = 3
            elif has_details:
                 self.max_accessible_step = 2
            else:
                self.max_accessible_step = 1

        except Exception as e:
            log.error(f"Failed to load configuration file '{target_path}': {e}")
            if filepath: # Only warn if explicitly loading a file
                messagebox.showerror("Error", f"Could not load the configuration file.\nError: {e}", parent=self)

    def load_config_from_dialog(self):
        """Opens a dialog to load a project-starter.json file."""
        filepath = filedialog.askopenfilename(
            title="Load Project Configuration",
            filetypes=[("JSON files", "*.json")],
            defaultextension=".json",
            parent=self
        )
        if not filepath:
            return

        # Save current view just in case
        self._save_current_view_data()

        # Load new data
        self._load_state(filepath)

        # Save immediately to session so it persists
        self._save_state()

        # Refresh UI
        self.current_step = 1 # Reset to start when loading new config
        self._show_current_step_view()

    def _save_current_view_data(self):
        """Extracts data from the current view's text widgets and updates the dictionary."""
        if self.current_view and self.current_view.winfo_exists():
            if self.current_step == 1:
                self.project_data["description"] = self.current_view.get_description()
            elif self.current_step == 2:
                self.project_data["concept_md"] = self.current_view.get_concept_content()
                if hasattr(self.current_view, 'get_goal_content'):
                    self.project_data["goal"] = self.current_view.get_goal_content()
            elif self.current_step == 3:
                self.project_data["todo_md"] = self.current_view.get_todo_content()

    def _start_over(self):
        if self.current_view and hasattr(self.current_view, 'handle_reset'):
            self.current_view.handle_reset()
            # Force save after reset to clear the session file's data for this step
            self._save_current_view_data()
            self._save_state()

    def _clear_session_data(self):
        """Clears all session data and resets the wizard."""
        if not messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all project data and start fresh? This cannot be undone.", parent=self):
            return

        # Reset internal data
        self.project_data["name"].set("")
        self.project_data["parent_folder"].set(self.default_parent_folder)
        self.project_data["stack"].set("")
        self.project_data["description"] = ""
        self.project_data["goal"] = ""
        self.project_data["concept_md"] = ""
        self.project_data["todo_md"] = ""

        # Remove session file
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
            except OSError as e:
                log.error(f"Failed to delete session file: {e}")

        # Reset UI state
        self.max_accessible_step = 1
        self.current_step = 1
        self._show_current_step_view()

    def _update_navigation_controls(self):
        self.prev_button.pack_forget()
        self.start_over_button.pack_forget()
        self.next_button.pack_forget()

        if self.current_step > 1:
            self.prev_button.pack(side="left")

        if self.current_step < 4:
            self.next_button.pack(side="right")

        can_start_over = self.current_view and hasattr(self.current_view, 'is_editor_visible') and self.current_view.is_editor_visible()
        if can_start_over:
            self.start_over_button.pack()

    def _update_tab_styles(self):
        for i, tab in enumerate(self.tabs):
            is_active = (i + 1) == self.current_step
            is_accessible = (i + 1) <= self.max_accessible_step

            if not is_accessible:
                tab.set_state('disabled')
                tab.config(hollow=True, fg=c.BTN_GRAY_TEXT)
            else:
                tab.set_state('normal')
                if is_active:
                    tab.config(hollow=False, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
                else:
                    tab.config(hollow=True, fg=c.TEXT_COLOR)

    def _go_to_next_step(self):
        if self.current_step < 4:
            self._go_to_step(self.current_step + 1)

    def _go_to_prev_step(self):
        if self.current_step > 1:
            self._go_to_step(self.current_step - 1)

    def _go_to_step(self, target_step):
        if target_step == self.current_step:
            return

        self._save_current_view_data()
        self._save_state()

        if target_step > self.current_step:
            if not self._validate_current_step():
                return
            self.max_accessible_step = max(self.max_accessible_step, target_step)

        if target_step > self.max_accessible_step:
            return

        self.current_step = target_step
        self._show_current_step_view()

    def _validate_current_step(self):
        if self.current_step == 1:
            project_name = self.project_data["name"].get()
            parent_folder = self.project_data["parent_folder"].get()
            code_stack = self.project_data["stack"].get()
            description = self.project_data["description"]

            if not all([project_name, parent_folder, code_stack, description]):
                messagebox.showerror("Error", "All fields are required.", parent=self)
                return False

            try:
                path_obj = Path(parent_folder)
                if not path_obj.exists():
                    messagebox.showerror("Invalid Path", f"The parent folder does not exist:\n{parent_folder}", parent=self)
                    return False
                if not path_obj.is_dir():
                    messagebox.showerror("Invalid Path", f"The path is not a directory:\n{parent_folder}", parent=self)
                    return False
            except Exception as e:
                messagebox.showerror("Invalid Path", f"The parent folder path is invalid.\nError: {e}", parent=self)
                return False

        elif self.current_step == 2:
            concept = self.project_data["concept_md"]
            if not concept:
                messagebox.showerror("Error", "The concept document cannot be empty.", parent=self)
                return False

        elif self.current_step == 3:
            todo = self.project_data["todo_md"]
            if not todo:
                messagebox.showerror("Error", "The TODO plan cannot be empty.", parent=self)
                return False

        return True

    def _show_current_step_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view_frame = tk.Frame(self.content_frame, bg=c.DARK_BG, padx=10, pady=10)
        view_frame.pack(expand=True, fill="both")

        if self.current_step == 1:
            self.current_view = Step1DetailsView(view_frame, self.project_data)
        elif self.current_step == 2:
            self.current_view = Step2ConceptView(view_frame, self, self.project_data)
        elif self.current_step == 3:
            if not self.project_data["concept_md"]:
                messagebox.showerror("Concept Missing", "Please complete the Concept step before generating the TODO plan.", parent=self)
                self._go_to_step(2)
                return
            self.current_view = Step3TodoView(view_frame, self, self.project_data)
        elif self.current_step == 4:
            if not self.project_data["concept_md"] or not self.project_data["todo_md"]:
                messagebox.showerror("Content Missing", "Please complete the Concept and TODO steps before generating the project.", parent=self)
                if not self.project_data["concept_md"]:
                    self._go_to_step(2)
                else:
                    self._go_to_step(3)
                return
            self.current_view = Step4GenerateView(view_frame, self.project_data, self.project_data["concept_md"], self.project_data["todo_md"], self.create_project)

        if self.current_view:
            self.current_view.pack(expand=True, fill="both")

        self._update_tab_styles()
        self._update_navigation_controls()

    def create_project(self, llm_output):
        project_name = self.project_data["name"].get()
        parent_folder = self.project_data["parent_folder"].get()

        if not llm_output.strip():
            messagebox.showerror("Error", "LLM Result text area is empty.", parent=self)
            return

        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]+', '-', project_name.lower()).strip('-')
        base_dir = Path(parent_folder)
        project_path = base_dir / sanitized_name

        if project_path.exists():
            if not messagebox.askyesno("Warning", f"Project folder '{sanitized_name}' already exists in '{base_dir}'. Overwrite?", parent=self):
                return
            try:
                shutil.rmtree(project_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete existing folder: {e}", parent=self)
                return

        try:
            project_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project directory: {e}", parent=self)
            return

        file_pattern = re.compile(r"--- File: `(.+?)` ---\s*```.*?$(.*?)```", re.MULTILINE | re.DOTALL)
        files_created = []
        matches = file_pattern.finditer(llm_output)

        for match in matches:
            file_path_str, content = match.groups()
            relative_path = Path(file_path_str.replace("boilerplate/", ""))
            full_path = project_path / relative_path

            try:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content.lstrip(), encoding="utf-8")
                files_created.append(str(relative_path))
            except Exception as e:
                log.error(f"Failed to write file {relative_path}: {e}")

        if not files_created:
            messagebox.showerror("Error", "Could not find any files to create in the LLM output. Ensure the format is correct.", parent=self)
            return

        # Save project config into the new project folder
        self._save_current_view_data()
        self._save_state() # Update session first

        try:
            dest_config = project_path / "project-starter.json"
            shutil.copy(self.session_file, dest_config)
        except Exception as e:
            log.error(f"Failed to save config to project folder: {e}")

        self._display_success_screen(sanitized_name, files_created, parent_folder)

    def _display_success_screen(self, project_folder_name, files_created, parent_folder):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Hide navigation
        self.nav_frame.pack_forget()

        def on_start_work():
            # Close wizard and load project in main app
            full_path = str(Path(parent_folder) / project_folder_name)

            # Apply default prompts to the new project
            from ...core.project_config import ProjectConfig
            from ...core.utils import load_config as load_app_config

            try:
                app_config = load_app_config()
                default_intro = app_config.get('default_intro_prompt', c.DEFAULT_INTRO_PROMPT)
                default_outro = app_config.get('default_outro_prompt', c.DEFAULT_OUTRO_PROMPT)

                # Replace placeholder
                default_intro = default_intro.replace('REPLACE_ME', project_folder_name)

                # We need to initialize a ProjectConfig for the new path
                new_proj_config = ProjectConfig(full_path)
                new_proj_config.load()

                new_proj_config.intro_text = default_intro
                new_proj_config.outro_text = default_outro
                new_proj_config.save()

            except Exception as e:
                log.error(f"Failed to apply default prompts to new project: {e}")

            self.app.ui_callbacks.on_directory_selected(full_path)
            self.destroy()

        success_view = SuccessView(self.content_frame, project_folder_name, files_created, on_start_work, parent_folder)
        success_view.pack(expand=True, fill="both")