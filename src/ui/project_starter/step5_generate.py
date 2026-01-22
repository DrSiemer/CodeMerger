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

class Step5GenerateView(tk.Frame):
    def __init__(self, parent, project_data, create_project_callback):
        super().__init__(parent, bg=c.DARK_BG)
        self.create_project_callback = create_project_callback
        self.project_data = project_data

        prompt = self._generate_master_prompt(project_data)

        # 1. Action Button at the very bottom
        self.create_button = RoundedButton(self, text="Create Project Files", command=self.on_create_project, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, height=40, cursor="hand2")
        self.create_button.pack(side='bottom', fill="x", pady=10)
        self.create_button.set_state('disabled')

        # 2. Options just above the create button
        if self.project_data["base_project_path"].get():
            ttk.Checkbutton(self, text="Include base project merge list in 'project_reference.md'", variable=self.project_data["include_base_reference"], style='Dark.TCheckbutton').pack(side='bottom', anchor="w", pady=(5,0))

        # 3. Header at the top
        tk.Label(self, text="Finalize and Generate", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        # 4. Destination Folder section
        dest_frame = tk.Frame(self, bg=c.DARK_BG)
        dest_frame.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(dest_frame, text="1. Select Parent Folder for the project", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(anchor='w')

        folder_select_frame = tk.Frame(dest_frame, bg=c.DARK_BG)
        folder_select_frame.pack(side='top', fill='x', pady=(5, 0))
        tk.Entry(folder_select_frame, textvariable=self.project_data["parent_folder"], bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL).pack(side='left', fill='x', expand=True, ipady=4)
        RoundedButton(folder_select_frame, text="Browse", command=self._browse_folder, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, cursor='hand2').pack(side='left', padx=(5, 0))

        # --- Path Preview (Communication Enhancement) ---
        self.preview_container = tk.Frame(dest_frame, bg=c.STATUS_BG, padx=10, pady=8)
        self.preview_container.pack(fill='x', pady=(10, 0))

        tk.Label(self.preview_container, text="A new folder will be created:", font=(c.FONT_FAMILY_PRIMARY, 9, 'bold'), bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack(anchor='w')
        self.preview_path_label = tk.Label(self.preview_container, text="", font=(c.FONT_FAMILY_PRIMARY, 9), bg=c.STATUS_BG, fg=c.BTN_BLUE, wraplength=700, justify='left')
        self.preview_path_label.pack(anchor='w', pady=(2, 0))

        # 5. Prompt Copy section
        prompt_frame = tk.Frame(self, bg=c.DARK_BG)
        prompt_frame.pack(side='top', fill="x", pady=(10, 10))
        tk.Label(prompt_frame, text="2. Copy Master Prompt for LLM", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        copy_btn = RoundedButton(prompt_frame, text="Copy Master Prompt", command=lambda: self._copy_to_clip(copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, radius=6, cursor="hand2")
        copy_btn.pack(side='left', padx=15)

        # 6. Response Label
        tk.Label(self, text="3. Paste the LLM Response below", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 5))

        # 7. LLM Response area (fills remaining space)
        self.llm_result_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.llm_result_text.pack(side='top', fill="both", expand=True, pady=5)

        self.llm_result_text.text_widget.bind('<KeyRelease>', self._validate_input)

        # Listen for changes to update the preview path
        self.project_data["parent_folder"].trace_add("write", self._update_preview_path)
        self.project_data["name"].trace_add("write", self._update_preview_path)
        self._update_preview_path()

    def _update_preview_path(self, *args):
        parent = self.project_data["parent_folder"].get().strip()
        name = self.project_data["name"].get().strip()

        if not parent or not name:
            self.preview_path_label.config(text="[Incomplete details]", fg=c.TEXT_SUBTLE_COLOR)
            return

        sanitized_name = sanitize_project_name(name)
        full_path = os.path.join(parent, sanitized_name)
        self.preview_path_label.config(text=full_path, fg=c.BTN_BLUE)

    def _browse_folder(self):
        folder = filedialog.askdirectory(parent=self)
        if folder: self.project_data["parent_folder"].set(folder)

    def _copy_to_clip(self, button, text):
        pyperclip.copy(text)
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text="Copy Master Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

    def _validate_input(self, event=None):
        content = self.llm_result_text.get("1.0", "end-1c")
        # Check for both header and the required footer
        if re.search(r"--- File: `.+?` ---", content) and "--- End of file ---" in content:
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
        concept = project_data.get("concept_md", "")
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

    def on_create_project(self):
        raw = self.llm_result_text.get("1.0", "end-1c").strip()
        if raw: self.create_project_callback(strip_markdown_wrapper(raw), self.project_data["include_base_reference"].get())