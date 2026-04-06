import tkinter as tk
import os
import json
import pyperclip
from tkinter import messagebox
from ... import constants as c
from ...core.paths import REFERENCE_DIR
from ...core.utils import strip_markdown_wrapper
from ...core.prompts import STARTER_CONCEPT_DEFAULT_GOAL
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from .segment_manager import SegmentManager
from .widgets.segmented_reviewer import SegmentedReviewer
from .widgets.rewrite_dialog import RewriteUnsignedDialog
from .widgets.full_text_reviewer import FullTextReviewer
from ..tooltip import ToolTip
from . import starter_prompts

class ConceptView(tk.Frame):
    def __init__(self, parent, starter_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.starter_controller = starter_controller
        self.project_data = project_data

        self.questions_map = self._load_questions()
        self.has_segments = bool(self.project_data.get("concept_segments"))

        self.editor_is_active = False
        self.generation_mode_active = False

        if self.has_segments:
            self.show_editor_view()
        elif self.project_data.get("concept_md"):
            self.show_merged_view(self.project_data.get("concept_md"))
        elif self.project_data.get("concept_llm_response"):
            self.show_generation_view(starter_prompts.get_concept_prompt(self.project_data, self.questions_map))
        else:
            self.show_initial_view()

    def register_info(self, info_mgr):
        if not info_mgr: return
        if hasattr(self, 'goal_text') and self.goal_text.winfo_exists():
            info_mgr.register(self.goal_text, "starter_concept_goal")
            info_mgr.register(self.generate_btn, "starter_concept_gen")
        elif hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            info_mgr.register(self.copy_btn, "starter_concept_gen")
            info_mgr.register(self.llm_response_text, "starter_gen_response")
            info_mgr.register(self.btn_process, "starter_gen_process")
        elif hasattr(self, 'reviewer') and self.reviewer.winfo_exists():
            if isinstance(self.reviewer, FullTextReviewer):
                self.reviewer.register_info(info_mgr, "starter_concept_review")
            else:
                self.reviewer.register_info(info_mgr)

    def refresh_fonts(self):
        size = self.starter_controller.font_size
        for attr in['goal_text', 'llm_response_text', 'reviewer']:
            if hasattr(self, attr):
                widget = getattr(self, attr)
                if widget.winfo_exists():
                    if hasattr(widget, 'refresh_fonts'): widget.refresh_fonts(size)
                    else: widget.set_font_size(size)

    def _load_questions(self):
        questions_path = os.path.join(REFERENCE_DIR, "concept_questions.json")
        try:
            with open(questions_path, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

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

        self.goal_text = ScrollableText(self, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size), on_zoom=self.starter_controller.adjust_font_size)
        self.goal_text.pack(side='top', fill="both", expand=True, pady=5)
        self.goal_text.insert("1.0", self.project_data.get("goal", "") or STARTER_CONCEPT_DEFAULT_GOAL)
        self.goal_text.text_widget.bind("<KeyRelease>", self._update_goal_state)
        self._update_button_state()
        self.register_info(self.starter_controller.info_mgr)

    def _update_goal_state(self, event=None):
        self.project_data["goal"] = self.goal_text.get("1.0", "end-1c").strip()
        self._update_button_state()

    def _update_button_state(self):
        content = self.project_data.get("goal", "").strip()
        self.generate_btn.set_state('normal' if content and content != STARTER_CONCEPT_DEFAULT_GOAL else 'disabled')

    def handle_prompt_generation(self):
        prompt = starter_prompts.get_concept_prompt(self.project_data, self.questions_map)
        self.show_generation_view(prompt)

    def show_generation_view(self, prompt):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = True
        self.starter_controller._update_navigation_controls()

        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        self.btn_process = RoundedButton(btn_container, text="Process & Review", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.btn_process.pack(side='right')

        tk.Label(self, text="Generate Concept", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        instr_f = tk.Frame(self, bg=c.DARK_BG)
        instr_f.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(instr_f, text="1. Copy prompt", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        self.copy_btn = RoundedButton(instr_f, text="Copy Prompt", command=lambda: self._copy_prompt(prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, radius=6, cursor="hand2")
        self.copy_btn.pack(side='left', padx=15)

        tk.Label(self, text="2. Paste LLM Response (with tags)", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 0))
        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size), on_zoom=self.starter_controller.adjust_font_size)
        self.llm_response_text.pack(side='top', fill="both", expand=True, pady=5)
        self.llm_response_text.insert("1.0", self.project_data.get("concept_llm_response", ""))
        self.llm_response_text.text_widget.bind("<KeyRelease>", self._on_response_change)

        self._update_process_btn()
        self.register_info(self.starter_controller.info_mgr)

    def _on_response_change(self, event=None):
        self.project_data["concept_llm_response"] = self.llm_response_text.get("1.0", "end-1c").strip()
        self._update_process_btn()

    def _update_process_btn(self):
        content = self.project_data.get("concept_llm_response", "").strip()
        st = 'normal' if content else 'disabled'
        self.btn_process.set_state(st)
        self.btn_process.config(bg=c.BTN_BLUE if st=='normal' else c.BTN_GRAY_BG, fg=c.BTN_BLUE_TEXT if st=='normal' else c.BTN_GRAY_TEXT)

    def _copy_prompt(self, text):
        pyperclip.copy(text)
        self.copy_btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: self.copy_btn.config(text="Copy Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if self.copy_btn.winfo_exists() else None)

    def handle_llm_response(self):
        raw = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw: return
        content = strip_markdown_wrapper(raw)
        parsed = SegmentManager.parse_segments(content)
        if not parsed:
            self.project_data["concept_md"] = content
            self.show_merged_view(content)
            return

        friendly = {k: v["label"] for k, v in self.questions_map.items()}
        mapped = SegmentManager.map_parsed_segments_to_keys(parsed, friendly)
        self.project_data["concept_segments"].clear()
        self.project_data["concept_segments"].update(mapped)
        self.project_data["concept_signoffs"].clear()
        for k in mapped: self.project_data["concept_signoffs"][k] = False
        self.project_data["concept_md"] = ""
        self.project_data["concept_llm_response"] = ""
        self.show_editor_view()

    def show_editor_view(self):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        header = tk.Frame(self, bg=c.DARK_BG)
        header.pack(side='top', fill="x", pady=(0, 5))
        tk.Label(header, text="Review Concept Segments", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        friendly = {k: v["label"] for k, v in self.questions_map.items()}
        self.reviewer = SegmentedReviewer(self, list(self.project_data["concept_segments"].keys()), friendly, self.project_data["concept_segments"], self.project_data["concept_signoffs"], self.questions_map, self.starter_controller.update_nav_state, self.handle_merge)
        self.reviewer.pack(fill="both", expand=True, pady=5)
        self.starter_controller._update_navigation_controls()
        self.register_info(self.starter_controller.info_mgr)

    def handle_merge(self, full_text):
        self.project_data["concept_segments"].clear()
        self.project_data["concept_signoffs"].clear()
        self.project_data["concept_md"] = full_text
        self.starter_controller.starter_state.update_from_view(self)
        self.starter_controller.starter_state.save()
        self.show_merged_view(full_text)

    def show_merged_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        qs = ["Is this concept clearly explained?", "Did we miss anything?"]
        self.reviewer = FullTextReviewer(self, "Review Full Concept", content, qs, self._on_merged_change, self._open_rewrite, self._get_prompt_context, self.starter_controller)
        self.reviewer.pack(fill="both", expand=True)

        self.starter_controller._update_navigation_controls()
        self.register_info(self.starter_controller.info_mgr)

    def _get_prompt_context(self):
        """Provides the specific background and focus context for the LLM prompt."""
        full_text = self.project_data.get("concept_md", "")
        return (
            "Full Concept",
            "```markdown\n" + full_text + "\n```",
            "Concept",
            "(Overview above)"
        )

    def _on_merged_change(self, text):
        self.project_data["concept_md"] = text

    def _open_rewrite(self):
        ctx = {'keys': ['full_content'], 'names': {'full_content': 'Full Concept'}, 'data': {'full_content': self.project_data["concept_md"]}}
        RewriteUnsignedDialog(self, self.starter_controller.app.app_state, ctx, self._apply_rewrite, is_merged_mode=True)

    def _apply_rewrite(self, text):
        clean = strip_markdown_wrapper(text)
        self.project_data["concept_md"] = clean
        self.reviewer.set_content(clean)
        self.starter_controller.update_nav_state()

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over?", parent=self):
            self.project_data["concept_segments"].clear()
            self.project_data["concept_signoffs"].clear()
            self.project_data["concept_md"] = ""
            self.project_data["concept_llm_response"] = ""
            self.editor_is_active = False
            self.generation_mode_active = False
            self.show_initial_view()
            self.starter_controller._update_navigation_controls()

    def get_goal_content(self):
        return self.goal_text.get("1.0", "end-1c").strip() if hasattr(self, 'goal_text') and self.goal_text.winfo_exists() else self.project_data.get("goal", "")

    def get_llm_response_content(self):
        return {"concept_llm_response": self.llm_response_text.get("1.0", "end-1c").strip()} if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists() else {}

    def get_assembled_content(self):
        if not self.project_data.get("concept_segments"): return self.project_data.get("concept_md", ""), {}, {}
        friendly = {k: v["label"] for k, v in self.questions_map.items()}
        txt = SegmentManager.assemble_document(self.project_data["concept_segments"], list(self.project_data["concept_segments"].keys()), friendly)
        return txt, self.project_data["concept_segments"], self.project_data["concept_signoffs"]

    def is_editor_visible(self): return self.editor_is_active
    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active
    def _clear_frame(self):
        for w in self.winfo_children(): w.destroy()