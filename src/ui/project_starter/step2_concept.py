import os
import json
import tkinter as tk
import pyperclip
from tkinter import messagebox
from ... import constants as c
from ...core.paths import REFERENCE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from ..widgets.switch_button import SwitchButton
from .segment_manager import SegmentManager
from .widgets.segmented_reviewer import SegmentedReviewer

DEFAULT_GOAL_TEXT = "The plan is to build a..."

class Step2ConceptView(tk.Frame):
    def __init__(self, parent, wizard_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.wizard_controller = wizard_controller
        self.project_data = project_data

        self.questions_map = self._load_questions()
        self.has_segments = bool(self.project_data.get("concept_segments"))

        if self.has_segments:
            self.show_editor_view()
        elif self.project_data.get("concept_md"):
            self.show_editor_view()
        else:
            self.show_initial_view()

    def _load_questions(self):
        questions_path = os.path.join(REFERENCE_DIR, "concept_questions.json")
        try:
            with open(questions_path, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

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

    def show_initial_view(self):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = False

        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        self.generate_btn = RoundedButton(btn_container, text="Generate Concept Prompt", command=self.handle_prompt_generation, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.generate_btn.pack(side='right')

        tk.Label(self, text="Describe Your Goal", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 5))
        tk.Label(self, text="Briefly describe what you want to build.", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").pack(side='top', anchor="w", pady=(0, 10))

        self.goal_text = ScrollableText(self, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.goal_text.pack(side='top', fill="both", expand=True, pady=5)

        existing_goal = self.project_data.get("goal", "").strip()
        self.goal_text.insert("1.0", existing_goal if existing_goal else DEFAULT_GOAL_TEXT)
        self.goal_text.text_widget.bind("<KeyRelease>", self._update_button_state)
        self._update_button_state()

    def _update_button_state(self, event=None):
        content = self.goal_text.get("1.0", "end-1c").strip()
        self.generate_btn.set_state('normal' if content and content != DEFAULT_GOAL_TEXT else 'disabled')

    def _get_prompt(self):
        user_goal = self.goal_text.get("1.0", 'end-1c')
        friendly_map = {k: v["label"] for k, v in self.questions_map.items()}
        segment_instructions = SegmentManager.build_prompt_instructions(c.CONCEPT_ORDER, friendly_map)

        parts = [
            "Based on the following user goal, generate a full project concept document.",
            "\n### User Goal\n```\n" + user_goal.strip() + "\n```",
            self._get_base_project_content(),
            "\n### Format Instructions",
            segment_instructions,
            "\n### Core Instructions",
            "1. Fill in every section with specific details relevant to the user's goal.",
            "2. Ensure the 'User Flows' section covers the complete lifecycle of the main data entity."
        ]
        return "\n".join(parts)

    def handle_prompt_generation(self):
        if hasattr(self, 'goal_text') and self.goal_text.winfo_exists():
            self.project_data["goal"] = self.goal_text.get("1.0", "end-1c").strip()
        prompt = self._get_prompt()
        if prompt: self.show_generation_view(prompt)

    def show_generation_view(self, prompt):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = True
        self.wizard_controller._update_navigation_controls()

        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        RoundedButton(btn_container, text="Process & Review", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2").pack(side='right')

        tk.Label(self, text="Generate Concept", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        instr_frame = tk.Frame(self, bg=c.DARK_BG)
        instr_frame.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(instr_frame, text="1. Copy prompt", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        copy_btn = RoundedButton(instr_frame, text="Copy Prompt", command=lambda: self._copy_to_clip(copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, radius=6, cursor="hand2")
        copy_btn.pack(side='left', padx=15)

        tk.Label(self, text="2. Paste LLM Response (with tags)", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 0))
        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.llm_response_text.pack(side='top', fill="both", expand=True, pady=5)

    def _copy_to_clip(self, button, text):
        pyperclip.copy(text)
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text="Copy Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

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

        self.project_data["concept_segments"].clear()
        self.project_data["concept_segments"].update(mapped_segments)

        self.project_data["concept_signoffs"].clear()
        for k in mapped_segments.keys():
            self.project_data["concept_signoffs"][k] = False

        self.show_editor_view()

    def show_editor_view(self):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        header = tk.Frame(self, bg=c.DARK_BG)
        header.pack(side='top', fill="x", pady=(0, 5))
        tk.Label(header, text="Review Concept Segments", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        friendly_map = {k: v["label"] for k, v in self.questions_map.items()}

        data_keys = set(self.project_data["concept_segments"].keys())
        ordered_keys = [k for k in c.CONCEPT_ORDER if k in data_keys]
        ordered_keys += [k for k in data_keys if k not in ordered_keys]

        if not ordered_keys:
            self.handle_reset()
            return

        self.reviewer = SegmentedReviewer(
            parent=self,
            segment_keys=ordered_keys,
            friendly_names_map=friendly_map,
            segments_data=self.project_data["concept_segments"],
            signoffs_data=self.project_data["concept_signoffs"],
            questions_map=self.questions_map,
            on_change_callback=self.wizard_controller.update_nav_state
        )
        self.reviewer.pack(fill="both", expand=True, pady=5)
        self.wizard_controller._update_navigation_controls()

    def is_editor_visible(self): return self.editor_is_active
    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over?", parent=self):
            self.project_data["concept_segments"].clear()
            self.project_data["concept_signoffs"].clear()
            self.project_data["concept_md"] = ""
            self.show_initial_view()
            self.wizard_controller._update_navigation_controls()

    def get_goal_content(self):
        if hasattr(self, 'goal_text') and self.goal_text.winfo_exists():
            return self.goal_text.get("1.0", "end-1c").strip()
        return self.project_data.get("goal", "")

    def get_assembled_content(self):
        friendly_map = {k: v["label"] for k, v in self.questions_map.items()}
        full_text = SegmentManager.assemble_document(
            self.project_data["concept_segments"],
            c.CONCEPT_ORDER,
            friendly_map
        )
        return full_text, self.project_data["concept_segments"], self.project_data["concept_signoffs"]

    def get_concept_content(self):
        return self.get_assembled_content()[0]

    def _clear_frame(self):
        for widget in self.winfo_children(): widget.destroy()