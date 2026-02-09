import os
import re
import tkinter as tk
import pyperclip
from tkinter import messagebox, ttk, filedialog
from ... import constants as c
from ...core.paths import BOILERPLATE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from .generator import sanitize_project_name
from .segment_manager import SegmentManager
from ..tooltip import ToolTip

class GenerateView(tk.Frame):
    def __init__(self, parent, project_data, create_project_callback, wizard_controller):
        super().__init__(parent, bg=c.DARK_BG)
        self.create_project_callback = create_project_callback
        self.project_data = project_data
        self.wizard_controller = wizard_controller
        self._trace_ids = [] # Track traces for cleanup

        prompt = self._generate_master_prompt(project_data)

        self.grid_columnconfigure(0, weight=1)

        # We assign equal weight to both text areas so they divide
        # the remaining vertical space 50/50.
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(8, weight=1)

        # 0. Header
        tk.Label(self, text="Finalize and Generate", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=(0, 10), sticky="w")

        # 1. Destination Folder Section
        dest_label_frame = tk.Frame(self, bg=c.DARK_BG)
        dest_label_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        tk.Label(dest_label_frame, text="1. Select Parent Folder for the project", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        folder_select_frame = tk.Frame(self, bg=c.DARK_BG)
        folder_select_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        self.folder_entry = tk.Entry(folder_select_frame, textvariable=self.project_data["parent_folder"], bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.folder_entry.pack(side='left', fill='x', expand=True, ipady=4)

        browse_btn = RoundedButton(folder_select_frame, text="Browse", command=self._browse_folder, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, cursor='hand2')
        browse_btn.pack(side='left', padx=(5, 0))

        # 2. Path Preview
        self.preview_container = tk.Frame(self, bg=c.STATUS_BG, padx=10, pady=8)
        self.preview_container.grid(row=3, column=0, sticky="ew", pady=(5, 10))

        tk.Label(self.preview_container, text="A new folder will be created:", font=(c.FONT_FAMILY_PRIMARY, 9, 'bold'), bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack(anchor='w')
        self.preview_path_label = tk.Label(self.preview_container, text="", font=(c.FONT_FAMILY_PRIMARY, 9), bg=c.STATUS_BG, fg=c.BTN_BLUE, wraplength=700, justify='left')
        self.preview_path_label.pack(anchor='w', pady=(2, 0))

        # 3. Prompt Copy Section
        prompt_header = tk.Frame(self, bg=c.DARK_BG)
        prompt_header.grid(row=4, column=0, pady=(5, 5), sticky="ew")
        tk.Label(prompt_header, text="2. Review and Copy the Master Prompt", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        copy_btn = RoundedButton(prompt_header, text="Copy", command=lambda: self._copy_prompt_to_clipboard(copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        copy_btn.pack(side="right")
        ToolTip(copy_btn, "Copy the final master prompt to clipboard", delay=500)

        tk.Label(self, text="Review and copy the prompt to paste into your LLM.", wraplength=680, justify="left", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).grid(row=5, column=0, sticky="w")

        self.prompt_text = ScrollableText(
            self, wrap=tk.WORD, height=2, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.wizard_controller.font_size),
            on_zoom=self.wizard_controller.adjust_font_size
        )
        self.prompt_text.insert(tk.END, prompt)
        self.prompt_text.grid(row=6, column=0, pady=(5, 10), sticky="nsew")

        # 4. Response Section
        tk.Label(self, text="3. Paste the LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=7, column=0, pady=(5, 5), sticky="w")

        self.llm_result_text = ScrollableText(
            self, wrap=tk.WORD, height=2, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.wizard_controller.font_size),
            on_zoom=self.wizard_controller.adjust_font_size
        )
        self.llm_result_text.grid(row=8, column=0, pady=(0, 10), sticky="nsew")

        self.llm_result_text.text_widget.bind('<KeyRelease>', self._validate_input)
        self.llm_result_text.text_widget.bind('<<Paste>>', self._validate_input)

        # 5. Footer
        footer_frame = tk.Frame(self, bg=c.DARK_BG)
        footer_frame.grid(row=9, column=0, sticky="ew", pady=(5, 0))

        if self.project_data["base_project_path"].get():
            ttk.Checkbutton(footer_frame, text="Include base project reference", variable=self.project_data["include_base_reference"], style='Dark.TCheckbutton').pack(side="left")

        self.create_button = RoundedButton(footer_frame, text="Create Project Files", command=self.on_create_project, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, height=40, width=250, cursor="hand2")
        self.create_button.pack(side="right")
        self.create_button.set_state('disabled')

        # Setup preview path tracking with IDs for cleanup
        t1 = self.project_data["parent_folder"].trace_add("write", self._update_preview_path)
        t2 = self.project_data["name"].trace_add("write", self._update_preview_path)
        self._trace_ids = [("parent_folder", t1), ("name", t2)]

        self._update_preview_path()

    def refresh_fonts(self):
        if hasattr(self, 'prompt_text') and self.prompt_text.winfo_exists():
            self.prompt_text.set_font_size(self.wizard_controller.font_size)
        if hasattr(self, 'llm_result_text') and self.llm_result_text.winfo_exists():
            self.llm_result_text.set_font_size(self.wizard_controller.font_size)

    def destroy(self):
        """Cleanup traces when the view is destroyed to prevent TclErrors."""
        for var_name, trace_id in self._trace_ids:
            try:
                self.project_data[var_name].trace_remove("write", trace_id)
            except Exception:
                pass
        super().destroy()

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

        sanitized_name = sanitize_project_name(name)
        full_path = os.path.join(parent, sanitized_name)
        self.preview_path_label.config(text=full_path, fg=c.BTN_BLUE)

    def _browse_folder(self):
        folder = filedialog.askdirectory(parent=self)
        if folder:
            self.project_data["parent_folder"].set(folder)

    def _validate_input(self, event=None):
        content = self.llm_result_text.get("1.0", "end-1c")
        # Validate that we have file blocks AND the strict pitch tag pair
        has_files = re.search(r"--- File: `.+?` ---", content) and "--- End of file ---" in content
        # STRICT Check: Must find the closing tag
        has_pitch = re.search(r"<<PITCH>>.*?<<PITCH>>", content, re.DOTALL)

        if has_files and has_pitch:
            self.create_button.set_state('normal')
        else:
            self.create_button.set_state('disabled')

    def _copy_prompt_to_clipboard(self, button, text):
        content = self.prompt_text.get('1.0', 'end-1c')
        pyperclip.copy(content)
        original_text = button.text
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text=original_text, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

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
                content_blocks.append(f"--- File: `{rel_path}` ---\n```\n{content}\n```\n")
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
                and f not in {'.DS_Store', 'Thumbs.db', '_start.txt'} # Explicitly exclude _start.txt just in case it exists
            ])

            for filename in files:
                path = os.path.join(BOILERPLATE_DIR, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        prompt_content += f"--- File: `boilerplate/{filename}` ---\n```\n{f.read()}\n```\n\n"
                except Exception:
                    pass
        except Exception:
            prompt_content = "Error loading boilerplate files."

        example_code = self._get_base_project_content()

        parts = [
            f"You are a senior developer creating a boilerplate for: {name}",
            f"Stack: {stack}",
            "\n### Provided Files\n" + prompt_content,
            "\n### Project Concept\n```markdown\n" + concept + "\n```",
            "\n### TODO Plan\n```markdown\n" + todo + "\n```",
            example_code,
            "\n### Core Instructions",
            "1. **Select & Rename:** Select the appropriate `go_*.bat` script for the stack and rename it to `go.bat`.",
            "2. **Mandatory README:** You MUST output the `README.md` file. Populate it (or create it) with the project title, the pitch, and specific setup steps derived from the stack.",
            "3. **BOILERPLATE ONLY:** DO NOT implement any of the actual tasks, code, or features described in the TODO plan yet. Your job is ONLY to set up the skeleton/infrastructure (README, batch scripts, config files). Do NOT create source files (like *.js, *.py, *.css) unless they are explicitly part of the standard boilerplate provided above.",
            "4. **Short Description:** At the start of your response, provide a short, one-sentence description (noun phrase) of exactly what this project is (e.g., 'a Python-based CLI tool for image processing'). This description must grammatically fit into the sentence 'We are working on [PITCH].' Wrap this description in `<<PITCH>>` tags. **You MUST close the tag with `<<PITCH>>`. Example: `<<PITCH>>a new CLI tool<<PITCH>>`. Failure to close this tag will break the parser.**",
            "5. **Output Format:** Return the complete source code for every file you are modifying or creating using this exact format:",
            "--- File: `path/to/file.ext` ---",
            "```language",
            "[content]",
            "```",
            "--- End of file ---",
            "\nCRITICAL: Do NOT omit the '--- End of file ---' marker for any block."
        ]
        return "\n".join(parts)

    def on_create_project(self):
        raw = self.llm_result_text.get("1.0", "end-1c").strip()
        if not raw: return

        # Strict Regex: Will only match if closing tag exists
        pitch_match = re.search(r"<<PITCH>>(.*?)<<PITCH>>", raw, re.DOTALL)
        project_pitch = pitch_match.group(1).strip() if pitch_match else "a new project"

        # Now get file content
        content = strip_markdown_wrapper(raw)

        self.create_project_callback(content, self.project_data["include_base_reference"].get(), project_pitch)