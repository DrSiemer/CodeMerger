import os
import re
import tkinter as tk
import pyperclip
from tkinter import messagebox, ttk, filedialog
from ... import constants as c
from ...core.paths import BOILERPLATE_DIR
from ...core.utils import strip_markdown_wrapper
from ...core.prompts import STARTER_GENERATE_MASTER_INTRO, STARTER_GENERATE_MASTER_INSTR
from ..widgets.rounded_button import RoundedButton
from .segment_manager import SegmentManager
from ..tooltip import ToolTip
# // DO NOT REMOVE [index] (pattern correction)
from ..widgets.scrollable_text import ScrollableText

class GenerateView(tk.Frame):
    def __init__(self, parent, project_data, create_project_callback, starter_controller):
        super().__init__(parent, bg=c.DARK_BG)
        self.create_project_callback = create_project_callback
        self.project_data = project_data
        self.starter_controller = starter_controller
        self._trace_ids = [] # Track traces for cleanup
        self.step3_interacted = False

        self.master_prompt_content = self._generate_master_prompt(project_data)

        self.grid_columnconfigure(0, weight=1)

        # Response area is the primary expanding element
        self.grid_rowconfigure(2, weight=1)

        # Header
        tk.Label(self, text="Finalize and Generate", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=(0, 10), sticky="w")

        # PROMPT COPY SECTION
        self.step1_frame = tk.Frame(self, bg=c.DARK_BG)
        self.step1_frame.grid(row=1, column=0, pady=(10, 0), sticky="ew")

        self.step1_title = tk.Label(self.step1_frame, text="1. Copy Creation Prompt", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.BTN_GREEN)
        self.step1_title.pack(side="top", anchor="w")

        self.copy_btn = RoundedButton(
            self.step1_frame, text="Copy Creation Prompt",
            command=lambda: self._copy_prompt_to_clipboard(self.copy_btn, self.master_prompt_content),
            bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON,
            height=40, width=250, radius=6, cursor="hand2",
            hover_bg=c.BTN_GREEN, # Maintain green on hover even if idle turns grey
            hover_fg="#FFFFFF"    # Maintain white text on hover
        )
        self.copy_btn.pack(side="top", anchor="w", pady=(10, 5))
        ToolTip(self.copy_btn, "Copy the final boilerplate and instructions for your AI", delay=500)

        self.hint_label = tk.Label(self.step1_frame, text="Note: it is recommended to use a smart thinking model for this step", font=(c.FONT_FAMILY_PRIMARY, 9, 'italic'), bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR)
        self.hint_label.pack(side="top", anchor="w")

        # RESPONSE SECTION (Initially Hidden)
        self.step2_frame = tk.Frame(self, bg=c.DARK_BG)

        self.step2_title = tk.Label(self.step2_frame, text="2. Paste the LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR)
        self.step2_title.pack(side="top", anchor="w", pady=(20, 5))

        self.llm_result_text = ScrollableText(
            self.step2_frame, wrap=tk.WORD, height=2, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size),
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.llm_result_text.pack(side="top", fill="both", expand=True, pady=(0, 10))

        # Restore buffer if present
        saved_response = self.project_data.get("generate_llm_response", "")
        if saved_response:
            self.llm_result_text.insert("1.0", saved_response)

        self.llm_result_text.text_widget.bind('<KeyRelease>', self._validate_and_sync)
        self.llm_result_text.text_widget.bind('<<Paste>>', self._validate_and_sync)

        # DESTINATION FOLDER SECTION (Initially Hidden)
        self.step3_frame = tk.Frame(self, bg=c.DARK_BG)

        dest_label_frame = tk.Frame(self.step3_frame, bg=c.DARK_BG)
        dest_label_frame.pack(side="top", fill="x", pady=(10, 5))
        self.step3_title = tk.Label(dest_label_frame, text="3. Select Parent Folder for the project", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR)
        self.step3_title.pack(side="left")

        folder_select_frame = tk.Frame(self.step3_frame, bg=c.DARK_BG)
        folder_select_frame.pack(side="top", fill="x", pady=(0, 5))

        self.folder_entry = tk.Entry(folder_select_frame, textvariable=self.project_data["parent_folder"], bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.folder_entry.pack(side='left', fill='x', expand=True, ipady=4)

        self.browse_btn = RoundedButton(folder_select_frame, text="Browse", command=self._browse_folder, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, cursor='hand2')
        self.browse_btn.pack(side='left', padx=(5, 0))

        # Path Preview (Compact Single Line)
        self.preview_container = tk.Frame(self.step3_frame, bg=c.STATUS_BG, padx=10, pady=4)
        self.preview_container.pack(side="top", fill="x", pady=(5, 10))

        tk.Label(self.preview_container, text="A new folder will be created:", font=(c.FONT_FAMILY_PRIMARY, 9, 'bold'), bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack(side='left')
        self.preview_path_label = tk.Label(self.preview_container, text="", font=(c.FONT_FAMILY_PRIMARY, 9), bg=c.STATUS_BG, fg=c.BTN_BLUE, justify='left')
        self.preview_path_label.pack(side='left', padx=(5, 0))

        # Interaction listeners for Step 3
        self.step3_frame.bind("<Button-1>", self._on_step3_click)
        self.folder_entry.bind("<Button-1>", self._on_step3_click)
        self.browse_btn.bind("<Button-1>", self._on_step3_click, add="+")
        self.preview_container.bind("<Button-1>", self._on_step3_click)

        # Footer
        footer_frame = tk.Frame(self, bg=c.DARK_BG)
        footer_frame.grid(row=4, column=0, sticky="ew", pady=(5, 15))

        if self.project_data["base_project_path"].get():
            ttk.Checkbutton(footer_frame, text="Include base project reference", variable=self.project_data["include_base_reference"], style='Dark.TCheckbutton').pack(side="left")

        self.create_button = RoundedButton(footer_frame, text="Create Project Files", command=self.on_create_project, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, height=40, width=250, cursor="hand2")
        self.create_button.pack(side="right")
        self.create_button.set_state('disabled')

        # Status hint label to explain why the button is disabled
        self.status_hint_label = tk.Label(footer_frame, text="", font=(c.FONT_FAMILY_PRIMARY, 9, 'italic'), bg=c.DARK_BG, fg=c.NOTE, justify='right')
        self.status_hint_label.pack(side="right", padx=15)

        # Setup preview path tracking and validation syncing
        t1 = self.project_data["parent_folder"].trace_add("write", self._update_preview_path)
        t2 = self.project_data["name"].trace_add("write", self._update_preview_path)
        t3 = self.project_data["parent_folder"].trace_add("write", self._validate_and_sync)
        t4 = self.project_data["name"].trace_add("write", self._validate_and_sync)
        t5 = self.project_data["parent_folder"].trace_add("write", self._force_backward_slashes)

        self._trace_ids = [
            ("parent_folder", t1), ("name", t2),
            ("parent_folder", t3), ("name", t4),
            ("parent_folder", t5)
        ]

        # Initial visibility check (handle session restore)
        if saved_response:
            self.step2_frame.grid(row=2, column=0, sticky="nsew")
            self._validate_and_sync()

        self._update_preview_path()
        self._validate_and_sync() # Initial state check
        self.register_info(self.starter_controller.info_mgr)

    def register_info(self, info_mgr):
        """Registers step-specific widgets for Info Mode."""
        if not info_mgr: return
        info_mgr.register(self.step1_title, "starter_gen_prompt")
        info_mgr.register(self.copy_btn, "starter_gen_prompt")
        info_mgr.register(self.step2_title, "starter_gen_response")
        info_mgr.register(self.llm_result_text, "starter_gen_response")
        info_mgr.register(self.step3_title, "starter_gen_parent")
        info_mgr.register(self.folder_entry, "starter_gen_parent")
        info_mgr.register(self.browse_btn, "starter_gen_parent")
        info_mgr.register(self.create_button, "starter_gen_create")

    def refresh_fonts(self):
        if hasattr(self, 'llm_result_text') and self.llm_result_text.winfo_exists():
            self.llm_result_text.set_font_size(self.starter_controller.font_size)

    def destroy(self):
        """Cleanup traces when the view is destroyed to prevent TclErrors."""
        for var_name, trace_id in self._trace_ids:
            try:
                self.project_data[var_name].trace_remove("write", trace_id)
            except Exception:
                pass
        super().destroy()

    def _force_backward_slashes(self, *args):
        """Ensures the parent folder path always uses backslashes."""
        val = self.project_data["parent_folder"].get()
        if '/' in val:
            self.project_data["parent_folder"].set(val.replace('/', '\\'))

    def _update_preview_path(self, *args):
        """Safely updates the preview path label if the widget still exists."""
        if not self.winfo_exists():
            return

        parent = self.project_data["parent_folder"].get().strip()
        name = self.project_data["name"].get().strip()

        if not hasattr(self, 'preview_path_label') or not self.preview_path_label.winfo_exists():
            return

        if not parent or not name:
            self.preview_path_label.config(text="[Incomplete details - please set Name and Parent Folder]", fg=c.TEXT_SUBTLE_COLOR)
            return

        from .generator import sanitize_project_name
        sanitized_name = sanitize_project_name(name)

        # Join components and normalize to backslashes for user preference
        full_path = os.path.join(parent, sanitized_name).replace('/', '\\')
        self.preview_path_label.config(text=full_path, fg=c.BTN_BLUE)

    def _browse_folder(self):
        self._on_step3_click()
        folder = filedialog.askdirectory(parent=self)
        if folder:
            # Normalize to backward slashes immediately after browsing
            normalized = folder.replace('/', '\\')
            self.project_data["parent_folder"].set(normalized)

    def _on_step3_click(self, event=None):
        """Called when user interacts with Step 3."""
        if not self.step3_interacted:
            self.step3_interacted = True
            self.step3_title.config(fg=c.TEXT_COLOR)
            self._validate_and_sync()

    def _validate_and_sync(self, *args):
        """
        Validates all inputs for the generation step and toggles button state.
        Triggered by key release in text area or changes to folder/name variables.
        Updates the status_hint_label with explanations if requirements aren't met.
        """
        if not self.winfo_exists():
            return

        content = self.llm_result_text.get("1.0", "end-1c").strip()

        # Save to buffer for persistence
        self.project_data["generate_llm_response"] = content

        # Handle title highlighting
        if content:
            self.step1_title.config(fg=c.TEXT_COLOR) # Mark Step 1 done
            self.step2_title.config(fg=c.TEXT_COLOR)
            # Reveal Step 3
            if not self.step3_frame.winfo_ismapped():
                self.step3_frame.grid(row=3, column=0, sticky="ew")
                if not self.step3_interacted:
                    self.step3_title.config(fg=c.BTN_GREEN)
        else:
            self.step3_frame.grid_forget()
            # If text is manually cleared or we are in reset, restore Step 1 focus
            self.step1_title.config(fg=c.BTN_GREEN)
            self.step2_title.config(fg=c.TEXT_COLOR)

        # Check Project Details
        project_name = self.project_data["name"].get().strip()
        if not project_name:
            self._set_ui_state("disabled", "Missing project name (Step 1)")
            return

        parent_folder = self.project_data["parent_folder"].get().strip()
        if not parent_folder:
            self._set_ui_state("disabled", "Select a destination folder")
            return

        if not os.path.isdir(parent_folder):
            self._set_ui_state("disabled", "Parent folder path is invalid")
            return

        # Check LLM Content (Files and Pitch tag)
        if not content:
             self._set_ui_state("disabled", "Paste the LLM response first")
             return

        has_files = re.search(r"--- File: `.+?` ---", content) and "--- End of file ---" in content
        if not has_files:
            self._set_ui_state("disabled", "No valid file blocks found in response")
            return

        # STRICT Check: Must find opening and closing tag
        has_pitch = re.search(r"<PITCH>.*?</PITCH>", content, re.DOTALL | re.IGNORECASE)
        if not has_pitch:
            self._set_ui_state("disabled", "Response missing <PITCH> tags")
            return

        # Check Interaction state
        if not self.step3_interacted:
            self._set_ui_state("disabled", "Verify parent folder to continue", use_gray_btn=True)
            return

        # All conditions met
        self._set_ui_state("normal", "")

    def _set_ui_state(self, state, hint_text, use_gray_btn=False):
        """Helper to sync button state and hint label."""
        self.create_button.set_state(state)
        self.status_hint_label.config(text=hint_text)

        if use_gray_btn:
            self.create_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        elif state == 'normal':
            self.create_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)

    def _copy_prompt_to_clipboard(self, button, text):
        pyperclip.copy(text)
        original_text = button.text
        # Change button visual state to indicate action performed
        button.config(text="Prompt Copied!", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        # Ensure that hovering always brings back the white-on-green signal
        button.hover_color = c.BTN_GREEN
        button.hover_fg = "#FFFFFF"

        # Advance focus to Step 2
        self.step1_title.config(fg=c.TEXT_COLOR)
        if not self.step2_frame.winfo_ismapped():
            self.step2_frame.grid(row=2, column=0, sticky="nsew")
            self.step2_title.config(fg=c.BTN_GREEN)
            self.llm_result_text.text_widget.focus_set()

        self.after(2000, lambda: button.config(text=original_text) if button.winfo_exists() else None)

    def _get_base_project_content(self):
        base_path = self.project_data.get("base_project_path", tk.StringVar()).get()
        base_files = self.project_data.get("base_project_files", [])
        if not base_path or not base_files: return ""

        content_blocks = ["\n### Example Project Code (For Reference Only)\n"]
        for file_info in base_files:
            rel_path = file_info['path']
            full_path = os.path.join(base_path, rel_path)
            try:
                with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    content = f.read()
                content_blocks.append(f"--- File: `{rel_path}` ---\n```\n" + content + "\n```\n")
            except Exception: pass
        return "\n".join(content_blocks)

    def _generate_master_prompt(self, project_data):
        name = project_data['name'].get()
        stack = project_data['stack'].get()

        concept = SegmentManager.assemble_document(project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS) if project_data.get("concept_segments") else project_data.get("concept_md", "")
        todo = SegmentManager.assemble_document(project_data["todo_segments"], c.TODO_ORDER, c.TODO_PHASES) if project_data.get("todo_segments") else project_data.get("todo_md", "")

        # DYNAMICALLY LOAD ALL FILES IN BOILERPLATE DIRECTORY
        prompt_content = ""
        try:
            # List all files, ignoring OS-specific junk files
            files = sorted([
                f for f in os.listdir(BOILERPLATE_DIR)
                if os.path.isfile(os.path.join(BOILERPLATE_DIR, f))
                and f not in {'.DS_Store', 'Thumbs.db', '_start.txt'}
            ])

            for filename in files:
                path = os.path.join(BOILERPLATE_DIR, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        # Include the '--- End of file ---' marker for consistency
                        # This teaches the LLM the correct response format by example.
                        prompt_content += f"--- File: `boilerplate/{filename}` ---\n```\n{f.read()}\n```\n--- End of file ---\n\n"
                except Exception:
                    pass
        except Exception:
            prompt_content = "Error loading boilerplate files."

        example_code = self._get_base_project_content()

        parts = [
            STARTER_GENERATE_MASTER_INTRO.format(name=name, stack=stack),
            "\n### Provided Files\n" + prompt_content,
            "\n### Project Concept\n```markdown\n" + concept + "\n```",
            "\n### TODO Plan\n```markdown\n" + todo + "\n```",
            example_code,
            STARTER_GENERATE_MASTER_INSTR
        ]
        return "\n".join(parts)

    def on_create_project(self):
        raw = self.llm_result_text.get("1.0", "end-1c").strip()
        if not raw: return

        # Strict Regex: Will only match if closing tag exists
        pitch_match = re.search(r"<PITCH>(.*?)</PITCH>", raw, re.DOTALL | re.IGNORECASE)
        project_pitch = pitch_match.group(1).strip() if pitch_match else "a new project"

        # Now get file content
        content = strip_markdown_wrapper(raw)

        self.create_project_callback(content, self.project_data["include_base_reference"].get(), project_pitch)

    def get_llm_response_content(self):
        if hasattr(self, 'llm_result_text') and self.llm_result_text.winfo_exists():
            return {"generate_llm_response": self.llm_result_text.get("1.0", "end-1c").strip()}
        return {}

    def handle_reset(self):
        """Resets the input fields for the generate step."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the response and reset this step?", parent=self):
            # Clear text
            self.llm_result_text.text_widget.delete("1.0", "end")
            self.project_data["generate_llm_response"] = ""

            # Reset interaction flag
            self.step3_interacted = False
            self.step3_title.config(fg=c.TEXT_COLOR)

            # Hide section frames
            self.step2_frame.grid_forget()
            self.step3_frame.grid_forget()

            # Reset titles and navigation state
            self.step1_title.config(fg=c.BTN_GREEN)
            self._validate_and_sync()
            self.starter_controller._update_navigation_controls()