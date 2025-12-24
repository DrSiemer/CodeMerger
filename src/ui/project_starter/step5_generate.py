import os
import re
import tkinter as tk
from tkinter import messagebox
from ... import constants as c
from ...core.paths import BOILERPLATE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText

class Step5GenerateView(tk.Frame):
    def __init__(self, parent, project_data, create_project_callback):
        super().__init__(parent, bg=c.DARK_BG)
        self.create_project_callback = create_project_callback
        self.project_data = project_data

        prompt = self._generate_master_prompt(project_data)
        if not prompt:
            return

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(6, weight=1)

        tk.Label(self, text="Generate Project Boilerplate", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=(0, 10), sticky="w")

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

    def _validate_input(self, event=None):
        """Checks if the input contains at least one valid file block."""
        content = self.llm_result_text.get("1.0", "end-1c")
        # Simple regex check for the file header pattern
        if re.search(r"--- File: `.+?` ---", content):
            self.create_button.set_state('normal')
        else:
            self.create_button.set_state('disabled')

    def _get_base_project_content(self):
        base_path = self.project_data.get("base_project_path", tk.StringVar()).get()
        base_files = self.project_data.get("base_project_files", [])

        if not base_path or not base_files:
            return ""

        content_blocks = []
        content_blocks.append("\n### Example Project Code (For Reference Only)\n")
        content_blocks.append("The user has provided an example project. You must NOT copy this code directly. Use it ONLY as a cheatsheet for syntax, patterns, and structure.\n")

        for file_info in base_files:
            rel_path = file_info['path']
            full_path = os.path.join(base_path, rel_path)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                content_blocks.append(f"--- File: `{rel_path}` ---\n```\n{file_content}\n```\n")
            except Exception:
                pass

        return "\n".join(content_blocks)

    def _generate_master_prompt(self, project_data):
        name = project_data['name'].get()
        stack = project_data['stack'].get()
        concept_md = project_data.get("concept_md", "")
        todo_md = project_data.get("todo_md", "")

        boilerplate_files = [
            "README.md", "llm.md", "release.bat", "version.txt",
            "go_docker.bat", "go_nodejs.bat", "go_python.bat", "_start.txt"
        ]

        prompt_content = ""
        for filename in boilerplate_files:
            path = os.path.join(BOILERPLATE_DIR, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                prompt_content += f"--- File: `boilerplate/{filename}` ---\n"
                prompt_content += f"```\n{content}\n```\n\n"
            except FileNotFoundError:
                messagebox.showerror("Error", f"Required boilerplate file not found: {path}", parent=self)
                return None

        prompt_content += f"--- File: `concept.md` ---\n"
        prompt_content += f"```markdown\n{concept_md}\n```\n\n"

        prompt_content += f"--- File: `todo.md` ---\n"
        prompt_content += f"```markdown\n{todo_md}\n```\n\n"

        example_code = self._get_base_project_content()

        # Build the User Requirements block, conditionally including the stack
        user_reqs = f'ProjectName: "{name}"\n'
        if stack:
            user_reqs += f'CodeStack: "{stack}"\n'

        prompt = f"""You are a senior software developer creating a project boilerplate. Your task is to take the user's requirements and the provided template files and generate a complete, ready-to-use project structure. Adhere strictly to the provided file formats.

### User Requirements
```yaml
{user_reqs}
```

### Provided Files
{prompt_content}

{example_code}

### Core Instructions
1.  **Selection & Renaming:** Analyze the `CodeStack` (or infer from `concept.md` if unspecified) to select the single most appropriate `go_*.bat` file (e.g. `go_python.bat` for python, `go_nodejs.bat` for node). Rename this file to `go.bat` in your output.
2.  **Exclusion:** You must **NOT** include the unused `go_*.bat` files in your final response. The output should only contain the single selected and renamed `go.bat` file.
3.  Using the User Requirements (`ProjectName`, `CodeStack`) and the provided `concept.md`, intelligently populate the placeholders in the boilerplate `README.md` and `_start.txt`.
4.  In `README.md`, generate a plausible 'Prerequisites' and 'Running the Project' section based on the `CodeStack` description.
5.  Infer the 'Primary Data Entity' from the Goal and `ProjectName` (e.g., 'book' for a book tracker) and update the schema in `concept.md` accordingly (e.g., rename the `[primary_resource]` table).
6.  Return the complete, modified source code for every file in the final package, including the populated `_start.txt`, following the exact `--- File: ... ---` format.
"""
        return prompt

    def _copy_prompt_to_clipboard(self, button):
        prompt_content = self.prompt_text.get('1.0', 'end-1c')
        self.clipboard_clear()
        self.clipboard_append(prompt_content)
        original_text = button.text
        original_bg = button.original_bg_color
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, state='disabled')
        self.after(2000, lambda: button.config(text=original_text, bg=original_bg, fg=c.BTN_GRAY_TEXT, state='normal'))

    def on_create_project(self):
        raw_content = self.llm_result_text.get("1.0", "end-1c").strip()
        if not raw_content:
            messagebox.showerror("Error", "LLM Result text area is empty.", parent=self)
            return

        # Clean wrapper if present
        llm_output = strip_markdown_wrapper(raw_content)
        self.create_project_callback(llm_output)