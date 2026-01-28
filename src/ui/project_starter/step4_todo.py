import os
import json
import tkinter as tk
import pyperclip
from tkinter import messagebox, ttk
from ... import constants as c
from ...core.paths import REFERENCE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from .segment_manager import SegmentManager
from .widgets.segmented_reviewer import SegmentedReviewer
from ..tooltip import ToolTip

class Step4TodoView(tk.Frame):
    def __init__(self, parent, wizard_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.wizard_controller = wizard_controller
        self.project_data = project_data

        self.questions_map = self._load_questions()
        self.editor_is_active = False
        self.generation_mode_active = False

        self.has_segments = bool(self.project_data.get("todo_segments"))

        if self.has_segments:
            self.show_editor_view()
        elif self.project_data.get("todo_md"):
            self.show_editor_view()
        else:
            self.show_generation_view()

    def _load_questions(self):
        questions_path = os.path.join(REFERENCE_DIR, "todo_questions.json")
        try:
            with open(questions_path, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except Exception: return {}

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

    def _get_prompt(self):
        # 1. Concept
        concept_md = self.project_data.get("concept_md")
        if not concept_md and self.project_data.get("concept_segments"):
            c_map_const = {k: v for k,v in c.CONCEPT_SEGMENTS.items()}
            concept_md = SegmentManager.assemble_document(self.project_data["concept_segments"], c.CONCEPT_ORDER, c_map_const)

        # 2. Stack
        stack = self.project_data["stack"].get()

        # 3. Base Code (if any)
        example_code = self._get_base_project_content()

        # 4. Template
        template_path = os.path.join(REFERENCE_DIR, "todo.md")
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                todo_template = f.read()
        except Exception:
            todo_template = "(Template not found)"

        # 5. Section headers for SegmentManager
        # We provide the list of valid headers so LLM knows what tags to use.
        valid_headers = [v for k, v in c.TODO_PHASES.items()]
        headers_str = ", ".join([f'"{h}"' for h in valid_headers])

        parts = [
            "You are a Technical Project Manager.",
            "Based on the following project Concept and Tech Stack, create a detailed TODO plan.",
            "\n### Tech Stack\n" + stack,
            "\n### Project Concept\n```markdown\n" + (concept_md or "No concept provided.") + "\n```",
            example_code,
            "\n### Reference Template (Standard TODO List)\n```markdown\n" + todo_template + "\n```",
            "\n### Instructions",
            "1. **Analyze Relevance:** Compare the Reference Template against the Concept. **SKIP** any phase from the template that is not appropriate for this specific project (e.g., remove 'Database' for a static site, remove 'API' for a CLI tool).",
            "2. **Adapt Tasks:** For the phases you keep, adapt the tasks to be specific to this project (e.g., change 'Create tables' to 'Create `users` and `products` tables').",
            "3. **Format:** You MUST output the plan using specific section tags for the phases you decide to include.",
            f"   - Use `<<SECTION: Phase Name>>` followed by the content.",
            f"   - Allowed Phase Names: {headers_str}.",
            "   - **Do not** output sections for phases you decided to skip."
        ]
        return "\n".join(parts)

    def show_generation_view(self, prompt=None):
        if prompt is None:
            prompt = self._get_prompt()

        self._clear_frame()
        self.generation_mode_active = True
        self.wizard_controller._update_navigation_controls()

        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        btn_proc = RoundedButton(btn_container, text="Process & Review", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        btn_proc.pack(side='right')
        ToolTip(btn_proc, "Parse the LLM's TODO response and open the reviewer", delay=500)

        tk.Label(self, text="Generate TODO Plan", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        instr_frame = tk.Frame(self, bg=c.DARK_BG); instr_frame.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(instr_frame, text="1. Copy prompt", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        copy_btn = RoundedButton(instr_frame, text="Copy", command=lambda: self._copy_to_clip(copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        copy_btn.pack(side='left', padx=15)
        ToolTip(copy_btn, "Copy prompt to clipboard", delay=500)

        tk.Label(self, text="2. Paste Response (with tags)", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 5))
        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.llm_response_text.pack(side='top', fill="both", expand=True, pady=5)

    def _copy_to_clip(self, button, text):
        pyperclip.copy(text)
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text="Copy", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

    def handle_llm_response(self):
        raw = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw: return

        content = strip_markdown_wrapper(raw)
        parsed_segments = SegmentManager.parse_segments(content)

        if not parsed_segments:
            messagebox.showwarning("Parsing Error", "Could not find any <<SECTION: ...>> tags.", parent=self)
            return

        friendly_map = {k: v["label"] for k, v in self.questions_map.items()}
        mapped_segments = SegmentManager.map_parsed_segments_to_keys(parsed_segments, friendly_map)

        self.project_data["todo_segments"].clear()
        self.project_data["todo_segments"].update(mapped_segments)

        self.project_data["todo_signoffs"].clear()
        for k in mapped_segments.keys():
            self.project_data["todo_signoffs"][k] = False

        self.show_editor_view()

    def show_editor_view(self):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        header = tk.Frame(self, bg=c.DARK_BG)
        header.pack(side='top', fill="x", pady=(0, 5))
        tk.Label(header, text="Review TODO Plan", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        friendly_map = {k: v["label"] for k, v in self.questions_map.items()}
        data_keys = set(self.project_data["todo_segments"].keys())
        ordered_keys = [k for k in c.TODO_ORDER if k in data_keys]
        ordered_keys += [k for k in data_keys if k not in ordered_keys]

        if not ordered_keys:
            self.handle_reset()
            return

        self.reviewer = SegmentedReviewer(
            parent=self,
            segment_keys=ordered_keys,
            friendly_names_map=friendly_map,
            segments_data=self.project_data["todo_segments"],
            signoffs_data=self.project_data["todo_signoffs"],
            questions_map=self.questions_map,
            on_change_callback=self.wizard_controller.update_nav_state
        )
        self.reviewer.pack(fill="both", expand=True, pady=5)
        self.wizard_controller._update_navigation_controls()

    def is_step_in_progress(self):
        return self.editor_is_active or self.generation_mode_active

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over? Current plan will be lost.", parent=self):
            self.project_data["todo_segments"].clear()
            self.project_data["todo_signoffs"].clear()
            self.project_data["todo_md"] = ""
            self.show_generation_view()
            self.wizard_controller._update_navigation_controls()

    def get_assembled_content(self):
        friendly_map = {k: v["label"] for k, v in self.questions_map.items()}
        full_text = SegmentManager.assemble_document(
            self.project_data["todo_segments"],
            c.TODO_ORDER,
            friendly_map
        )
        return full_text, self.project_data["todo_segments"], self.project_data["todo_signoffs"]

    def get_todo_content(self):
        return self.get_assembled_content()[0]

    def _clear_frame(self):
        for widget in self.winfo_children(): widget.destroy()