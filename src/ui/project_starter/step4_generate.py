import os
import tkinter as tk
from tkinter import messagebox
from ... import constants as c
from ...core.paths import BOILERPLATE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText

class Step4GenerateView(tk.Frame):
    def __init__(self, parent, project_data, concept_md, todo_md, create_project_callback):
        super().__init__(parent, bg=c.DARK_BG)
        self.create_project_callback = create_project_callback

        prompt = self._generate_master_prompt(project_data, concept_md, todo_md)
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

        RoundedButton(self, text="Create Project Files", command=self.on_create_project, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, height=40, cursor="hand2").grid(row=7, column=0, pady=10, sticky="ew")

    def _generate_master_prompt(self, project_data, concept_md, todo_md):
        name = project_data['name'].get()
        stack = project_data['stack'].get()

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

        prompt = f"""You are a senior software developer creating a project boilerplate. Your task is to take the user's requirements and the provided template files and generate a complete, ready-to-use project structure. Adhere strictly to the provided file formats.

### User Requirements
```yaml
ProjectName: "{name}"
CodeStack: "{stack}"
```

### Provided Files
{prompt_content}
### Core Instructions
1.  Analyze the CodeStack to select the most appropriate `go_*.bat` file.
2.  Rename the selected file to `go.bat`.
3.  Do not include the unselected `go_*.bat` files in the final output.
4.  Using the User Requirements (`ProjectName`, `CodeStack`) and the provided `concept.md`, intelligently populate the placeholders in the boilerplate `README.md` and `_start.txt`.
5.  In `README.md`, generate a plausible 'Prerequisites' and 'Running the Project' section based on the `CodeStack` description.
6.  Infer the 'Primary Data Entity' from the Goal and `ProjectName` (e.g., 'book' for a book tracker) and update the schema in `concept.md` accordingly (e.g., rename the `[primary_resource]` table).
7.  Return the complete, modified source code for every file in the final package, including the populated `_start.txt`, following the exact `--- File: ... ---` format.
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