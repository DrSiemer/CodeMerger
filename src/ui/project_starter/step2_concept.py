import os
import json
import tkinter as tk
import pyperclip
from tkinter import messagebox
from ... import constants as c
from ...core.paths import REFERENCE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.markdown_renderer import MarkdownRenderer
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from ..widgets.switch_button import SwitchButton

DEFAULT_GOAL_TEXT = "The plan is to build a..."

class Step2ConceptView(tk.Frame):
    def __init__(self, parent, wizard_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.wizard_controller = wizard_controller
        self.project_data = project_data

        self.concept_content = self.project_data.get("concept_md", "")
        self.questions = self._load_questions()
        self.current_question_index = 0
        self.editor_is_active = False
        self.generation_mode_active = False

        self.questions_visible = False
        self.questions_frame = None

        if self.concept_content:
            self.show_editor_view(self.concept_content)
        else:
            self.show_initial_view()

    def _load_questions(self):
        questions_path = os.path.join(REFERENCE_DIR, "concept_questions.json")
        try:
            with open(questions_path, "r", encoding="utf-8") as f:
                content = f.read()
                if not content: return []
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

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

        # ACTION BUTTON AT BOTTOM
        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        self.generate_btn = RoundedButton(btn_container, text="Generate Concept Prompt", command=self.handle_prompt_generation, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.generate_btn.pack(side='right')

        # TOP CONTENT
        tk.Label(self, text="Describe Your Goal", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 5))
        tk.Label(self, text="Briefly describe what you want to build. This will be used to generate a structured concept document from the template.", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").pack(side='top', anchor="w", pady=(0, 10))

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
        template_path = os.path.join(REFERENCE_DIR, "concept.md")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                concept_template = f.read()
        except FileNotFoundError: return ""

        parts = [
            "Based on the following user goal, expand it into a full project concept document. Use the provided template as a strict guide for the structure.",
            "\n### User Goal\n```\n" + user_goal.strip() + "\n```",
            "\n### Template (`concept.md`)\n```markdown\n" + concept_template + "\n```",
            self._get_base_project_content(),
            "\n### Instructions\n1. Fill in every section of the template that is relevant to the user's goal.\n2. Return *only* the generated markdown content for the new `concept.md` file."
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

        # ACTION BUTTON AT BOTTOM
        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        RoundedButton(btn_container, text="Expand to Editor", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2").pack(side='right')

        # TOP CONTENT
        tk.Label(self, text="Generate Concept", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        instr_frame = tk.Frame(self, bg=c.DARK_BG)
        instr_frame.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(instr_frame, text="1. Copy prompt and paste it into your LLM.", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        copy_btn = RoundedButton(instr_frame, text="Copy Prompt", command=lambda: self._copy_to_clip(copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, radius=6, cursor="hand2")
        copy_btn.pack(side='left', padx=15)

        tk.Label(self, text="2. Paste LLM Response below", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 0))
        tk.Label(self, text="Hint: use the 'Copy as Markdown' option in the LLM if available", font=c.FONT_NORMAL, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='top', anchor="w", pady=(0, 5))

        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.llm_response_text.pack(side='top', fill="both", expand=True, pady=5)

    def _copy_to_clip(self, button, text):
        pyperclip.copy(text)
        orig_text, orig_bg = button.text, button.original_bg_color
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text=orig_text, bg=orig_bg, fg=c.BTN_GRAY_TEXT))

    def handle_llm_response(self):
        raw = self.llm_response_text.get("1.0", "end-1c").strip()
        if raw:
            self.concept_content = strip_markdown_wrapper(raw)
            self.project_data["concept_md"] = self.concept_content
            self.show_editor_view(self.concept_content)

    def show_editor_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        header = tk.Frame(self, bg=c.DARK_BG)
        header.pack(side='top', fill="x", pady=(0, 5))
        tk.Label(header, text="Edit Your Concept", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        actions = tk.Frame(header, bg=c.DARK_BG)
        actions.pack(side="right")

        if self.questions:
            self.toggle_q_btn = RoundedButton(actions, text="Review Questions", command=self._toggle_questions, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=6, hollow=True, cursor='hand2')
            self.toggle_q_btn.pack(side='left', padx=(0, 15))

        tk.Label(actions, text="Raw", font=c.FONT_NORMAL, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='left', padx=(0,5))
        self.view_switch = SwitchButton(actions, command=self._toggle_view, initial_state=False)
        self.view_switch.pack(side='left')
        tk.Label(actions, text="Rendered", font=c.FONT_NORMAL, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='left', padx=(5,10))

        self.q_container = tk.Frame(self, bg=c.DARK_BG)
        # q_container is initialized but NOT packed yet.

        self.editor_frame = tk.Frame(self, bg=c.DARK_BG)
        self.editor_frame.pack(side='top', fill="both", expand=True)

        self.editor_text = ScrollableText(self.editor_frame, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.editor_text.pack(fill="both", expand=True)
        self.editor_text.insert("1.0", content)
        self.editor_text.text_widget.bind('<KeyRelease>', self._sync_editor_to_state)

        self.markdown_renderer = MarkdownRenderer(self.editor_frame)
        self._toggle_view(self.view_switch.get_state())
        self._sync_editor_to_state()
        self.wizard_controller._update_navigation_controls()

    def _toggle_questions(self):
        self.questions_visible = not self.questions_visible
        if self.questions_visible:
            self.q_container.pack(side='top', fill="x", before=self.editor_frame)
            self._create_question_prompter(self.q_container)
            self.toggle_q_btn.config(hollow=False)
        else:
            self.q_container.pack_forget()
            if self.questions_frame:
                self.questions_frame.destroy()
                self.questions_frame = None
            self.toggle_q_btn.config(hollow=True)

    def _sync_editor_to_state(self, event=None):
        if hasattr(self, 'editor_text') and self.editor_text.winfo_exists():
            self.project_data["concept_md"] = self.editor_text.get("1.0", "end-1c").strip()
        self.wizard_controller.update_nav_state()

    def is_editor_visible(self): return self.editor_is_active
    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active

    def _toggle_view(self, is_rendered):
        if is_rendered:
            self.editor_text.pack_forget()
            self.markdown_renderer.set_markdown(self.editor_text.get("1.0", "end-1c"))
            self.markdown_renderer.pack(fill="both", expand=True)
        else:
            self.markdown_renderer.pack_forget()
            self.editor_text.pack(fill="both", expand=True)

    def _create_question_prompter(self, parent):
        self.questions_frame = tk.Frame(parent, bg=c.STATUS_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        self.questions_frame.pack(fill='x', pady=(0, 10))
        content = tk.Frame(self.questions_frame, bg=c.STATUS_BG, padx=10, pady=10)
        content.pack(fill='x', expand=True)
        self.question_label = tk.Label(content, text="", wraplength=600, justify="left", anchor="w", font=c.FONT_NORMAL, bg=c.STATUS_BG, fg=c.TEXT_COLOR)
        self.question_label.pack(side='left', fill='x', expand=True)

        actions = tk.Frame(content, bg=c.STATUS_BG)
        actions.pack(side='right', padx=(10,0))
        nav = tk.Frame(actions, bg=c.STATUS_BG); nav.pack()
        self.prev_question_button = RoundedButton(nav, text="<", command=self._show_prev_question, width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.prev_question_button.pack(side="left")
        self.next_question_button = RoundedButton(nav, text=">", command=self._show_next_question, width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.next_question_button.pack(side="left", padx=2)

        copy_btn = RoundedButton(actions, text="Copy with Concept", command=lambda: self._copy_q_prompt(copy_btn), height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        copy_btn.pack(pady=(4,0), fill='x')
        self._update_question_display()

    def _update_question_display(self):
        if not hasattr(self, 'question_label'): return
        self.question_label.config(text=self.questions[self.current_question_index])
        self.prev_question_button.set_state("normal" if self.current_question_index > 0 else "disabled")
        self.next_question_button.set_state("normal" if self.current_question_index < len(self.questions) - 1 else "disabled")

    def _show_next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1; self._update_question_display()

    def _show_prev_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1; self._update_question_display()

    def _copy_q_prompt(self, button):
        concept = self.editor_text.get("1.0", "end-1c").strip()
        text = "Task: " + self.questions[self.current_question_index] + "\n\nConcept:\n```markdown\n" + concept + "\n```"
        pyperclip.copy(text)
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text="Copy with Concept", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over?", parent=self):
            self.project_data["concept_md"], self.project_data["goal"], self.concept_content = "", "", ""
            self.show_initial_view()
            self.wizard_controller._update_navigation_controls()

    def get_goal_content(self):
        if hasattr(self, 'goal_text') and self.goal_text.winfo_exists():
            return self.goal_text.get("1.0", "end-1c").strip()
        return self.project_data.get("goal", "")

    def get_concept_content(self):
        if hasattr(self, 'editor_text') and self.editor_text.winfo_exists():
            return self.editor_text.get("1.0", "end-1c").strip()
        return self.concept_content

    def _clear_frame(self):
        for widget in self.winfo_children(): widget.destroy()