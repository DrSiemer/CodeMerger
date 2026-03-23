import os
import json
import pyperclip
import tkinter as tk
from tkinter import messagebox
from ... import constants as c
from ...core.paths import REFERENCE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from .segment_manager import SegmentManager
from .widgets.segmented_reviewer import SegmentedReviewer
from .widgets.rewrite_dialog import RewriteUnsignedDialog
from .widgets.full_text_reviewer import FullTextReviewer
from ..tooltip import ToolTip
from . import starter_prompts

class TodoView(tk.Frame):
    def __init__(self, parent, starter_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.starter_controller = starter_controller
        self.project_data = project_data

        self.questions_map = {}
        self.manual_questions = self._load_questions()

        self.editor_is_active = False
        self.generation_mode_active = False
        self.has_segments = bool(self.project_data.get("todo_segments"))

        if self.has_segments:
            self.show_editor_view()
        elif self.project_data.get("todo_md"):
            self.show_merged_view(self.project_data.get("todo_md"))
        elif self.project_data.get("todo_llm_response"):
            self.show_generation_view(starter_prompts.get_todo_prompt(self.project_data, self.questions_map))
        else:
            self.show_generation_view()

    def register_info(self, info_mgr):
        if not info_mgr: return
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            info_mgr.register(self.copy_btn, "starter_todo_gen")
            info_mgr.register(self.llm_response_text, "starter_gen_response")
            info_mgr.register(self.btn_process, "starter_gen_process")
        elif hasattr(self, 'reviewer') and self.reviewer.winfo_exists():
            if isinstance(self.reviewer, FullTextReviewer):
                self.reviewer.register_info(info_mgr, "starter_todo_review")
            else:
                self.reviewer.register_info(info_mgr)

    def refresh_fonts(self):
        size = self.starter_controller.font_size
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            self.llm_response_text.set_font_size(size)
        if hasattr(self, 'reviewer') and self.reviewer.winfo_exists():
            self.reviewer.refresh_fonts(size)

    def _load_questions(self):
        path = os.path.join(REFERENCE_DIR, "todo_questions.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
                if isinstance(data, dict):
                    self.questions_map = data
                    return []
                return data if isinstance(data, list) else[]
        except (FileNotFoundError, json.JSONDecodeError): return[]

    def show_generation_view(self, prompt=None):
        if prompt is None: prompt = starter_prompts.get_todo_prompt(self.project_data, self.questions_map)
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = True
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hdr = tk.Frame(self, bg=c.DARK_BG)
        hdr.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        tk.Label(hdr, text="1. Copy Prompt for LLM", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')
        self.copy_btn = RoundedButton(hdr, text="Copy Prompt", command=lambda: self._copy_prompt(prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        self.copy_btn.pack(side='left', padx=15)

        tk.Label(self, text="2. Paste LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=1, column=0, pady=(10, 5), sticky="w")
        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size), on_zoom=self.starter_controller.adjust_font_size)
        self.llm_response_text.grid(row=2, column=0, sticky='nsew')
        self.llm_response_text.insert("1.0", self.project_data.get("todo_llm_response", ""))
        self.llm_response_text.text_widget.bind("<KeyRelease>", self._on_response_change)

        self.btn_process = RoundedButton(self, text="Process & Review", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.btn_process.grid(row=3, column=0, pady=(10,0), sticky="e")
        self._update_process_btn()
        self.register_info(self.starter_controller.info_mgr)

    def _on_response_change(self, event=None):
        self.project_data["todo_llm_response"] = self.llm_response_text.get("1.0", "end-1c").strip()
        self._update_process_btn()

    def _update_process_btn(self):
        content = self.project_data.get("todo_llm_response", "").strip()
        st = 'normal' if content else 'disabled'
        self.btn_process.set_state(st)
        self.btn_process.config(bg=c.BTN_BLUE if st=='normal' else c.BTN_GRAY_BG, fg=c.BTN_BLUE_TEXT if st=='normal' else c.BTN_GRAY_TEXT)

    def _copy_prompt(self, text):
        pyperclip.copy(text)
        self.copy_btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: self.copy_btn.config(text="Copy Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

    def handle_llm_response(self):
        raw = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw: return
        content = strip_markdown_wrapper(raw)
        parsed = SegmentManager.parse_segments(content)
        if not parsed:
            self.project_data["todo_md"] = content
            self.show_merged_view(content)
            return

        friendly = {k: v["label"] for k, v in self.questions_map.items()} if self.questions_map else c.TODO_PHASES
        mapped = SegmentManager.map_parsed_segments_to_keys(parsed, friendly)
        self.project_data["todo_segments"].clear()
        self.project_data["todo_segments"].update(mapped)
        self.project_data["todo_signoffs"].clear()
        for k in mapped: self.project_data["todo_signoffs"][k] = False
        self.project_data["todo_md"] = ""
        self.project_data["todo_llm_response"] = ""
        self.show_editor_view()

    def show_editor_view(self):
        self._clear_frame()
        self.editor_is_active, self.generation_mode_active = True, False
        header = tk.Frame(self, bg=c.DARK_BG)
        header.pack(side='top', fill="x", pady=(0, 5))
        tk.Label(header, text="Review TODO Plan", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        friendly = {k: v["label"] for k, v in self.questions_map.items()} if self.questions_map else c.TODO_PHASES
        ordered_keys = list(self.project_data["todo_segments"].keys())
        if 'deployment' in ordered_keys:
            ordered_keys.remove('deployment'); ordered_keys.append('deployment')

        self.reviewer = SegmentedReviewer(self, ordered_keys, friendly, self.project_data["todo_segments"], self.project_data["todo_signoffs"], self.questions_map, self.starter_controller.update_nav_state, self.handle_merge)
        self.reviewer.pack(fill="both", expand=True, pady=5)
        self.starter_controller._update_navigation_controls()
        self.register_info(self.starter_controller.info_mgr)

    def handle_merge(self, full_text):
        self.project_data["todo_segments"].clear()
        self.project_data["todo_signoffs"].clear()
        self.project_data["todo_md"] = full_text
        self.starter_controller.starter_state.update_from_view(self)
        self.starter_controller.starter_state.save()
        self.show_merged_view(full_text)

    def show_merged_view(self, content):
        self._clear_frame()
        self.editor_is_active, self.generation_mode_active = True, False
        qs = self.manual_questions or["Do these TODO steps cover the concept?", "Did we miss anything?"]
        self.reviewer = FullTextReviewer(self, "Edit Your TODO Plan", content, qs, self._on_merged_change, self._open_rewrite, self._get_prompt_context, self.starter_controller)
        self.reviewer.pack(fill="both", expand=True)
        self.starter_controller._update_navigation_controls()
        self.register_info(self.starter_controller.info_mgr)

    def _get_prompt_context(self):
        """Provides the specific background and focus context for the LLM prompt."""
        concept_md = self.project_data.get("concept_md")
        if not concept_md and self.project_data.get("concept_segments"):
            concept_md = SegmentManager.assemble_document(self.project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS)
        todo_content = self.project_data.get("todo_md", "")

        return (
            "Project Concept",
            "```markdown\n" + (concept_md or "No concept provided") + "\n```",
            "Full TODO Plan",
            "```markdown\n" + todo_content + "\n```"
        )

    def _on_merged_change(self, text):
        self.project_data["todo_md"] = text

    def _open_rewrite(self):
        ctx = {'keys': ['full_content'], 'names': {'full_content': 'Full TODO Plan'}, 'data': {'full_content': self.project_data["todo_md"]}}
        RewriteUnsignedDialog(self, self.starter_controller.app.app_state, ctx, self._apply_rewrite, is_merged_mode=True)

    def _apply_rewrite(self, text):
        clean = strip_markdown_wrapper(text)
        self.project_data["todo_md"] = clean
        self.reviewer.set_content(clean)
        self.starter_controller.update_nav_state()

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over?", parent=self):
            self.project_data["todo_segments"].clear()
            self.project_data["todo_signoffs"].clear()
            self.project_data["todo_md"] = ""
            self.project_data["todo_llm_response"] = ""
            self.editor_is_active, self.generation_mode_active = False, False
            self.show_generation_view()
            self.starter_controller._update_navigation_controls()

    def get_llm_response_content(self):
        return {"todo_llm_response": self.llm_response_text.get("1.0", "end-1c").strip()} if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists() else {}

    def get_assembled_content(self):
        if not self.project_data.get("todo_segments"): return self.project_data.get("todo_md", ""), {}, {}
        keys = list(self.project_data["todo_segments"].keys())
        if 'deployment' in keys: keys.remove('deployment'); keys.append('deployment')
        friendly = {k: v["label"] for k, v in self.questions_map.items()} if self.questions_map else c.TODO_PHASES
        txt = SegmentManager.assemble_document(self.project_data["todo_segments"], keys, friendly)
        return txt, self.project_data["todo_segments"], self.project_data["todo_signoffs"]

    def is_editor_visible(self): return self.editor_is_active
    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active
    def _clear_frame(self):
        for w in self.winfo_children(): w.destroy()