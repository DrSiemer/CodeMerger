import tkinter as tk
import os
import shutil
import logging
import json
import re
from pathlib import Path
from tkinter import messagebox, filedialog
from ... import constants as c
from ...core import prompts as p
from ..widgets.rounded_button import RoundedButton
from ...core.utils import load_config
from ...core.paths import BOILERPLATE_DIR, ICON_PATH
from ..style_manager import apply_dark_theme
from .step_details import DetailsView
from .step_concept import ConceptView
from .step_stack import StackView
from .step_todo import TodoView
from .step_generate import GenerateView
from .step_base_files import StepBaseFilesView
from .success_view import SuccessView
from ..window_utils import position_window, get_monitor_work_area
from . import session_manager, generator, starter_state, starter_validator
from .segment_manager import SegmentManager
from ..tooltip import ToolTip
from ..info_manager import attach_info_mode
from ..assets import assets

log = logging.getLogger("CodeMerger")

class ProjectStarterDialog(tk.Toplevel):
    """
    A dialog for bootstrapping new software projects.
    Uses a 4-row grid system to ensure the Info Panel persists during step transitions.
    """
    def __init__(self, parent, app):
        super().__init__(parent)
        # Hidden initially to allow for flicker-free monitor assignment
        self.withdraw()
        self.parent = parent
        self.app = app

        # Flag to track if a project was finished, preventing restoration of old project
        self.finished_successfully = False

        # Initialize the state manager. Renamed to starter_state to avoid shadowing self.state()
        self.starter_state = starter_state.StarterState()

        # Font Scaling State (Unified)
        self.font_size = c.FONT_NORMAL[1] # Default 12

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

        self._build_ui()

        # Load previous session
        self.starter_state.load()

        # Add traces to trigger validation updates when data changes
        self.starter_state.project_data["name"].trace_add("write", lambda *args: self.update_nav_state())
        self.starter_state.project_data["name"].trace_add("write", self._update_window_title)
        self.starter_state.project_data["parent_folder"].trace_add("write", lambda *args: self.update_nav_state())
        self.starter_state.project_data["stack"].trace_add("write", lambda *args: self.update_nav_state())

        # Info Toggle: Managed by InfoManager.place
        self.info_toggle_btn = tk.Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")

        # --- Info Mode Integration ---
        # Fixed Grid Row (3) ensures panel is not destroyed when Step content is replaced
        self.info_mgr = attach_info_mode(self, self.app.app_state, manager_type='grid', grid_row=3, toggle_btn=self.info_toggle_btn)
        self._register_static_info()

        self._refresh_tabs()
        self._update_window_title()
        self._show_current_step_view()

        # --- Flicker-Free Monitor-Aware Maximization ---
        # 1. Determine the monitor the parent window is currently on
        m_left, m_top, m_right, m_bottom = get_monitor_work_area(self.parent)

        # 2. Make the window invisible but 'mapped'
        self.attributes("-alpha", 0.0)

        # 3. Position the window at a standard size on the target monitor to pin the handle
        self.geometry(f"600x400+{m_left + 50}+{m_top + 50}")
        self.deiconify()

        # 4. Force OS to acknowledge the mapping and coordinate change
        self.update_idletasks()

        # 5. Apply maximized state
        self.state('zoomed')

        # 6. Delay showing the window to hide the OS "zoom" animation jank
        # 200ms is usually sufficient for the DWM to finish its transition.
        self.after(200, self._reveal_after_maximized)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Control-0>", self.reset_zoom)

    def _reveal_after_maximized(self):
        """Finalizes the launch by making the window visible and grabbing focus."""
        if not self.winfo_exists(): return
        self.attributes("-alpha", 1.0)
        self.focus_force()

    def _build_ui(self):
        """Builds a rigid 4-row grid layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Row 1 is the primary content area (Wizard steps)

        # --- Row 0: Header (Tabs + Config buttons) ---
        header_frame = tk.Frame(self, bg=c.DARK_BG, padx=10, pady=10)
        header_frame.grid(row=0, column=0, sticky="ew")

        self.tabs_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        self.tabs_frame.pack(side="left", fill='x', expand=True)

        right_header_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        right_header_frame.pack(side="right")

        if self.app.assets.trash_icon_image:
             self.btn_clear = RoundedButton(
                right_header_frame, command=self._clear_session_data,
                image=self.app.assets.trash_icon_image,
                bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, width=32, height=32, radius=6, cursor="hand2"
            )
             self.btn_clear.pack(side="right", padx=(0, 0))
             ToolTip(self.btn_clear, "Clear all starter progress and start fresh", delay=500)

        self.btn_save = RoundedButton(
            right_header_frame, text="Save Config", command=self.save_config_to_dialog,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=32, radius=6, cursor="hand2"
        )
        self.btn_save.pack(side="right", padx=(0, 10))
        ToolTip(self.btn_save, "Save current project configuration to a file", delay=500)

        self.btn_load = RoundedButton(
            right_header_frame, text="Load Config", command=self.load_config_from_dialog,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=32, radius=6, cursor="hand2"
        )
        self.btn_load.pack(side="right", padx=(0, 10))
        ToolTip(self.btn_load, "Load a previously saved project configuration file", delay=500)

        # --- Row 1: Main Content ---
        self.content_frame = tk.Frame(self, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10)

        # --- Row 2: Navigation Bar ---
        self.nav_frame = tk.Frame(self, bg=c.DARK_BG, padx=10, pady=10)
        self.nav_frame.grid(row=2, column=0, sticky="ew")

        # Buttons are packed and ordered in _update_navigation_controls
        self.prev_button = RoundedButton(self.nav_frame, text="< Prev", command=self._go_to_prev_step, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        ToolTip(self.prev_button, "Go back to the previous step", delay=500)

        self.start_over_button = RoundedButton(self.nav_frame, text="Reset step", command=self._start_over, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        ToolTip(self.start_over_button, "Clear the inputs for the current step", delay=500)

        self.next_button = RoundedButton(self.nav_frame, text="Next >", command=self._go_to_next_step, height=30, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.next_tooltip = ToolTip(self.next_button, "Validate current inputs and proceed", delay=500)

    def _show_current_step_view(self):
        """Destroys current step view and instantiates the new one."""
        if hasattr(self, 'info_mgr'):
            self.info_mgr.clear_active_stack()

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view_frame = tk.Frame(self.content_frame, bg=c.DARK_BG)
        view_frame.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        step = self.starter_state.current_step

        # Step availability logic
        if step > 3 and not self.starter_state.project_data["concept_md"]:
             messagebox.showerror("Concept Missing", "You must complete and merge the Concept document before moving to later steps.", parent=self)
             self._go_to_step(3)
             return
        if step == 6 and not self.starter_state.project_data["todo_md"]:
             messagebox.showerror("Content Missing", "You must complete and merge the TODO Plan before moving to the Generate step.", parent=self)
             self._go_to_step(5)
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

        self._update_tab_styles()
        self._update_navigation_controls()

    def _register_static_info(self):
        """Registers the persistent UI elements for Info Mode."""
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")
        self.info_mgr.register(self.prev_button, "starter_nav_prev")
        self.info_mgr.register(self.next_button, "starter_nav_next")
        self.info_mgr.register(self.start_over_button, "starter_nav_reset")
        self.info_mgr.register(self.btn_save, "starter_header_save")
        self.info_mgr.register(self.btn_load, "starter_header_load")
        if hasattr(self, 'btn_clear'):
            self.info_mgr.register(self.btn_clear, "starter_header_clear")

    def _update_window_title(self, *args):
        """Updates the dialog window title with the project name if set."""
        name = self.starter_state.project_data["name"].get().strip()
        if name:
            self.title(f"Project Starter - {name}")
        else:
            self.title("Project Starter")

    def create_project(self, llm_output, include_base_reference=False, project_pitch="a new project"):
        """Processes the LLM output and creates the actual files on disk."""
        is_valid, err_title, err_msg = starter_validator.validate_step(6, self.starter_state.project_data)
        if not is_valid:
            messagebox.showerror(err_title, err_msg, parent=self)
            return

        if not llm_output.strip():
            messagebox.showerror("Error", "LLM Result text area is empty.", parent=self)
            return

        raw_project_name = self.starter_state.project_data["name"].get()
        parent_folder = self.starter_state.project_data["parent_folder"].get()

        # Parse recommended color from LLM response
        color_match = re.search(r"<<COLOR>>(.*?)<<COLOR>>", llm_output, re.DOTALL)
        recommended_color = color_match.group(1).strip() if color_match else None
        if recommended_color and not re.match(r'^#[0-9a-fA-F]{6}$', recommended_color):
            recommended_color = None

        # Prepare Directory
        success, project_path, msg = generator.prepare_project_directory(parent_folder, raw_project_name)
        if not success:
            if "already exists" in msg:
                if messagebox.askyesno("Warning", f"{msg} Overwrite?", parent=self):
                    success, project_path, msg = generator.prepare_project_directory(parent_folder, raw_project_name, overwrite=True)
                else: return
            if not success:
                messagebox.showerror("Error", msg, parent=self)
                return

        # Write Files from LLM response
        success, files_created, msg = generator.parse_and_write_files(project_path, llm_output)
        if not success:
            messagebox.showerror("Error", msg, parent=self)
            return

        # 1. Add concept.md and todo.md from the Starter state
        try:
            concept_segs = self.starter_state.project_data.get("concept_segments")
            concept_content = SegmentManager.assemble_document(concept_segs, c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS) if concept_segs else self.starter_state.project_data.get("concept_md", "")
            if concept_content:
                (project_path / "concept.md").write_text(concept_content, encoding="utf-8")
                files_created.append("concept.md")

            todo_segs = self.starter_state.project_data.get("todo_segments")
            todo_content = SegmentManager.assemble_document(todo_segs, c.TODO_ORDER, c.TODO_PHASES) if todo_segs else self.starter_state.project_data.get("todo_md", "")
            if todo_content:
                (project_path / "todo.md").write_text(todo_content, encoding="utf-8")
                files_created.append("todo.md")
        except Exception as e:
            log.error(f"Failed to write mandatory documentation files: {e}")

        # 2. Save the Starter config into the project folder for future reloading
        try:
            config_data = self.starter_state.get_dict()
            starter_json_path = project_path / "project-starter.json"
            with open(starter_json_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            files_created.append("project-starter.json")
        except Exception as e:
            log.error(f"Failed to write project-starter.json: {e}")

        # Optional: Write Base Project Reference
        if include_base_reference:
            base_path = self.starter_state.project_data["base_project_path"].get()
            base_files = self.starter_state.project_data["base_project_files"]
            if generator.write_base_reference_file(project_path, base_path, base_files):
                files_created.append("project_reference.md")

        # Create .allcode with custom intro and the filtered list
        conf = load_config()
        intro = f"We are working on {project_pitch}.\n\nContinue work on the plan laid out in `todo.md`. If a bug is reported, fix it first. ONLY output `todo.md` (in full, without omissions) when explicitly updating checkbox status."
        outro = conf.get('default_outro_prompt', p.DEFAULT_OUTRO_PROMPT)

        normalized_files = []
        merge_order_exclusion_list = ['.gitignore', 'project-starter.json', '2do.txt']

        for f in files_created:
             norm = f.replace('\\', '/')
             if os.path.basename(norm) not in merge_order_exclusion_list:
                 normalized_files.append({'path': norm})

        self.app.project_manager.create_project_with_defaults(
            path=str(project_path),
            project_name=raw_project_name,
            intro_text=intro,
            outro_text=outro,
            initial_selected_files=normalized_files,
            project_color=recommended_color
        )

        self._display_success_screen(project_path.name, files_created, parent_folder)

    def _get_active_steps(self):
        steps = [1]
        if self.starter_state.project_data["base_project_path"].get():
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
            tab = RoundedButton(self.tabs_frame, command=lambda s=step_id: self._go_to_step(s), text=f"{i+1}. {name}", font=c.FONT_NORMAL, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, height=32, radius=6, hollow=True, cursor="hand2")
            tab.pack(side="left", padx=(0, 5), fill='x', expand=True)
            ToolTip(tab, f"Jump to {name} step", delay=500)
            self.tabs.append(tab)
        self._update_tab_styles()

    def on_base_project_selected(self, path):
        self._refresh_tabs()

    def on_closing(self):
        self.starter_state.update_from_view(self.current_view)
        self.starter_state.save()
        if not self.finished_successfully:
            last_path = getattr(self.app, '_last_project_path', None)
            if last_path:
                self.app.project_actions.set_active_dir_display(last_path)
        self.destroy()

    def save_config_to_dialog(self):
        self.starter_state.update_from_view(self.current_view)
        project_name = self.starter_state.project_data["name"].get().strip()
        initial_file = f"{project_name}.json" if project_name else "project-config.json"
        filepath = filedialog.asksaveasfilename(title="Save Project Configuration", defaultextension=".json", initialfile=initial_file, filetypes=[("JSON files", "*.json")], parent=self)
        if not filepath: return
        session_manager.save_session_data(self.starter_state.get_dict(), filepath)
        messagebox.showinfo("Success", f"Configuration saved to:\n{filepath}", parent=self)

    def load_config_from_dialog(self):
        filepath = filedialog.askopenfilename(title="Load Project Configuration", filetypes=[("JSON files", "*.json")], defaultextension=".json", parent=self)
        if not filepath: return
        self.starter_state.update_from_view(self.current_view)
        self.starter_state.load(filepath)
        self.starter_state.save()
        self.starter_state.current_step = 1
        self._refresh_tabs()
        self._show_current_step_view()

    def _start_over(self):
        if self.current_view and hasattr(self.current_view, 'handle_reset'):
            self.current_view.handle_reset()
            self.starter_state.update_from_view(self.current_view)
            self.starter_state.save()
            self.update_nav_state()

    def _clear_session_data(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all project data and start fresh?", parent=self):
            self.starter_state.reset()
            self._refresh_tabs()
            self._show_current_step_view()

    def _go_to_next_step(self):
        active_steps = self._get_active_steps()
        if self.starter_state.current_step in active_steps:
            current_idx = active_steps.index(self.starter_state.current_step)
            if current_idx < len(active_steps) - 1:
                self._go_to_step(active_steps[current_idx + 1])

    def _go_to_prev_step(self):
        active_steps = self._get_active_steps()
        if self.starter_state.current_step in active_steps:
            current_idx = active_steps.index(self.starter_state.current_step)
            if current_idx > 0:
                self._go_to_step(active_steps[current_idx - 1])

    def _go_to_step(self, target_step_id):
        if target_step_id == self.starter_state.current_step: return
        is_accessible = (target_step_id <= self.starter_state.max_accessible_step) or (target_step_id == 2)
        if not is_accessible: return
        self.starter_state.update_from_view(self.current_view)
        self.starter_state.save()
        if target_step_id > self.starter_state.current_step:
            is_valid, err_title, err_msg = starter_validator.validate_step(self.starter_state.current_step, self.starter_state.project_data)
            if not is_valid:
                messagebox.showerror(err_title, err_msg, parent=self)
                return
            self.starter_state.max_accessible_step = max(self.starter_state.max_accessible_step, target_step_id)
        self.starter_state.current_step = target_step_id
        self._show_current_step_view()

    def reset_zoom(self, event=None):
        """Resets font size to default."""
        self.font_size = c.FONT_NORMAL[1]
        if self.current_view and hasattr(self.current_view, 'refresh_fonts'):
            self.current_view.refresh_fonts()

    def adjust_font_size(self, delta):
        """Adjusts the font size for all starter components simultaneously."""
        new_size = self.font_size + delta
        self.font_size = max(8, min(new_size, 40))
        if self.current_view and hasattr(self.current_view, 'refresh_fonts'):
            self.current_view.refresh_fonts()

    def _update_navigation_controls(self):
        """Clears and repacks navigation buttons based on current step status, aligning all to the right."""
        self.prev_button.pack_forget()
        self.start_over_button.pack_forget()
        self.next_button.pack_forget()

        active_steps = self._get_active_steps()
        current_idx = active_steps.index(self.starter_state.current_step)

        # Pack from right to left to keep [Prev] [Reset] [Next] order on the right side
        if current_idx < len(active_steps) - 1:
            self.next_button.pack(side="right")

        can_reset = False
        if self.current_view:
            if hasattr(self.current_view, 'is_step_in_progress'):
                can_reset = self.current_view.is_step_in_progress()
            elif hasattr(self.current_view, 'is_editor_visible'):
                can_reset = self.current_view.is_editor_visible()

        if can_reset:
            # Spacing between Reset and Next
            self.start_over_button.pack(side="right", padx=(0, 10))

        if current_idx > 0:
            # Spacing between Prev and whatever is to its right
            self.prev_button.pack(side="right", padx=(0, 10))

        self.update_nav_state()

    def update_nav_state(self):
        if self.starter_state.current_step == 6: return
        self.next_button.config(text="Next >")
        if self.starter_state.current_step == 2:
            self.next_button.set_state('normal')
            self.next_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.next_tooltip.text = "Skip or confirm base files and proceed"
            return
        if self.starter_state.current_step == 4:
            stack_val = self.starter_state.project_data["stack"].get()
            if not stack_val.strip():
                self.next_button.config(text="Skip", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
                self.next_tooltip.text = "Proceed without defining a specific stack"
            else:
                self.next_button.config(text="Next >", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
                self.next_tooltip.text = "Confirm stack and proceed to TODO plan"
            self.next_button.set_state('normal')
            return
        is_valid, _, _ = starter_validator.validate_step(self.starter_state.current_step, self.starter_state.project_data)
        if is_valid:
            self.next_button.set_state('normal')
            self.next_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.next_tooltip.text = "Move to the next step"
        else:
            self.next_button.set_state('disabled')
            self.next_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.next_tooltip.text = "Please complete the required fields to continue"

    def _update_tab_styles(self):
        active_steps = self._get_active_steps()
        for i, tab in enumerate(self.tabs):
            step_id = active_steps[i]
            is_active = (step_id == self.starter_state.current_step)
            is_accessible = (step_id <= self.starter_state.max_accessible_step) or (step_id == 2)
            tab.set_state('normal' if is_accessible else 'disabled')
            tab.config(hollow=(not is_active), bg=(c.BTN_BLUE if is_active else c.BTN_GRAY_BG), fg=(c.BTN_BLUE_TEXT if is_active else (c.TEXT_COLOR if is_accessible else c.BTN_GRAY_TEXT)))

    def _display_success_screen(self, project_name, files, parent_folder):
        self.finished_successfully = True
        for w in self.content_frame.winfo_children(): w.destroy()
        self.nav_frame.grid_forget()
        def on_start_work():
            full_path = str(Path(parent_folder) / project_name)
            self.starter_state.reset()
            self.app.ui_callbacks.on_directory_selected(full_path)
            self.destroy()
            self.app.after(100, self.app.show_and_raise)
        SuccessView(self.content_frame, project_name, files, on_start_work, parent_folder).pack(expand=True, fill="both")