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

class Step5GenerateView(tk.Frame):
    def __init__(self, parent, project_data, create_project_callback):
        super().__init__(parent, bg=c.DARK_BG)
        self.create_project_callback = create_project_callback
        self.project_data = project_data

        prompt = self._generate_master_prompt(project_data)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(6, weight=1)

        tk.Label(self, text="Finalize and Generate", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=(0, 10), sticky="w")

        prompt_header = tk.Frame(self, bg=c.DARK_BG)
        prompt_header.grid(row=1, column=0, pady=(0, 5), sticky="ew")
        tk.Label(prompt_header, text="1. Review and Copy the Master Prompt", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")
        copy_btn = RoundedButton(prompt_header, text="Copy", command=lambda: self._copy_prompt_to_clipboard(copy_btn), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        copy_btn.pack(side="right")

        tk.Label(self, text="Review, edit if needed, and then copy the master prompt to paste into your preferred Large Language Model.", wraplength=680, justify="left", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).grid(row=2, column=0, sticky="w")

        self.prompt_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL, insertbackground=c.TEXT_COLOR)
        self.prompt_text.insert(tk.END, prompt)
        self.prompt_text.grid(row=3, column=0, pady=10, sticky="nsew")

        tk.Label(self, text="2. Paste the Result", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=4, column=0, pady=(10, 5), sticky="w")
        tk.Label(self, text="Paste the full, unmodified response from the LLM into the text area below.", wraplength=680, justify="left", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).grid(row=5, column=0, sticky="w")

        self.llm_result_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.llm_result_text.grid(row=6, column=0, pady=10, sticky="nsew")

        # Bind to text changes to validate input
        self.llm_result_text.text_widget.bind('<KeyRelease>', self._validate_input)
        self.llm_result_text.text_widget.bind('<<Paste>>', self._validate_input)

        self.create_button = RoundedButton(self, text="Create Project Files", command=self.on_create_project, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, height=40, cursor="hand2")
        self.create_button.grid(row=7, column=0, pady=10, sticky="ew")
        self.create_button.set_state('disabled')

        # Additional options
        if self.project_data["base_project_path"].get():
            ttk.Checkbutton(self, text="Include base project merge list in 'project_reference.md'", variable=self.project_data["include_base_reference"], style='Dark.TCheckbutton').grid(row=8, column=0, sticky='w')

    def _validate_input(self, event=None):
        content = self.llm_result_text.get("1.0", "end-1c")
        if re.search(r"--- File: `.+?` ---", content):
            self.create_button.set_state('normal')
        else:
            self.create_button.set_state('disabled')

    def _get_base_project_content(self):
        base_path = self.project_data.get("base_project_path", tk.StringVar()).get()
        base_files = self.project_data.get("base_project_files", [])
        if not base_path or not base_files: return ""

        content_blocks = ["\n### Example Project Code (For Reference Only)\n"]
        for file_info in base_files:
            rel_path = file_info['path']
            full_path = os.path.join(base_path, rel_path)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                content_blocks.append("--- File: `" + rel_path + "` ---\n```\n" + content + "\n```\n")
            except Exception: pass
        return "\n".join(content_blocks)

    def _generate_master_prompt(self, project_data):
        name = project_data['name'].get()
        stack = project_data['stack'].get()

        # Assemble Content from Segments
        concept = ""
        if project_data.get("concept_segments"):
            concept = SegmentManager.assemble_document(
                project_data["concept_segments"],
                c.CONCEPT_ORDER,
                c.CONCEPT_SEGMENTS
            )
        else:
            concept = project_data.get("concept_md", "")

        todo = ""
        if project_data.get("todo_segments"):
            todo = SegmentManager.assemble_document(
                project_data["todo_segments"],
                c.TODO_ORDER,
                c.TODO_PHASES
            )
        else:
            todo = project_data.get("todo_md", "")

        boilerplate_files = ["README.md", "llm.md", "release.bat", "version.txt", "go_docker.bat", "go_nodejs.bat", "go_python.bat", "_start.txt"]
        prompt_content = ""
        for filename in boilerplate_files:
            path = os.path.join(BOILERPLATE_DIR, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    prompt_content += "--- File: `boilerplate/" + filename + "` ---\n```\n" + f.read() + "\n```\n\n"
            except Exception: pass

        example_code = self._get_base_project_content()

        parts = [
            "You are a senior developer creating a boilerplate for: " + name,
            "Stack: " + stack,
            "\n### Provided Files\n" + prompt_content,
            "\n### Project Concept\n```markdown\n" + concept + "\n```",
            "\n### TODO Plan\n```markdown\n" + todo + "\n```",
            example_code,
            "\n### Core Instructions",
            "1. Select the appropriate `go_*.bat` and rename it to `go.bat`.",
            "2. Populate placeholders in `README.md` and `_start.txt`.",
            "3. Return the complete source code for every file using this exact format:",
            "--- File: `path/to/file.ext` ---",
            "```language",
            "[content]",
            "```",
            "--- End of file ---",
            "\nCRITICAL: Do NOT omit the '--- End of file ---' marker for any block."
        ]
        return "\n".join(parts)

    def _copy_prompt_to_clipboard(self, button):
        prompt_content = self.prompt_text.get('1.0', 'end-1c')
        self.clipboard_clear()
        self.clipboard_append(prompt_content)
        original_text = button.text
        original_bg = button.original_bg_color
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, state='disabled')
        self.after(2000, lambda: button.config(text=original_text, bg=original_bg, fg=c.BTN_GRAY_TEXT, state='normal'))

    def on_create_project(self):
        raw = self.llm_result_text.get("1.0", "end-1c").strip()
        if raw: self.create_project_callback(strip_markdown_wrapper(raw), self.project_data["include_base_reference"].get())