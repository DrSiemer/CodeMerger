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
from ..widgets.markdown_renderer import MarkdownRenderer
from .segment_manager import SegmentManager
from .widgets.segmented_reviewer import SegmentedReviewer
from ..tooltip import ToolTip

class ConceptView(tk.Frame):
    def __init__(self, parent, wizard_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.wizard_controller = wizard_controller
        self.project_data = project_data

        self.questions_map = self._load_questions()
        self.has_segments = bool(self.project_data.get("concept_segments"))

        # State for merged view toggle
        self.is_raw_mode = False

        # State tracking for UI transition
        self.editor_is_active = False
        self.generation_mode_active = False

        if self.has_segments:
            self.show_editor_view()
        elif self.project_data.get("concept_md"):
            self.show_merged_view(self.project_data.get("concept_md"))
        elif self.project_data.get("concept_llm_response"):
            # If we have an unprocessed response, return to that view
            self.show_generation_view(self._get_prompt())
        else:
            self.show_initial_view()

    def refresh_fonts(self):
        """Updates font sizes for all active text/renderer widgets."""
        if hasattr(self, 'goal_text') and self.goal_text.winfo_exists():
            self.goal_text.set_font_size(self.wizard_controller.font_size)
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            self.llm_response_text.set_font_size(self.wizard_controller.font_size)
        if hasattr(self, 'reviewer') and self.reviewer.winfo_exists():
            self.reviewer.refresh_fonts(self.wizard_controller.font_size)
        if hasattr(self, 'editor_text') and self.editor_text.winfo_exists():
            self.editor_text.set_font_size(self.wizard_controller.font_size)
        if hasattr(self, 'markdown_renderer') and self.markdown_renderer.winfo_exists():
            self.markdown_renderer.set_font_size(self.wizard_controller.font_size)

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
        ToolTip(self.generate_btn, "Create a structured prompt for your LLM based on this goal", delay=500)

        tk.Label(self, text="Describe Your Goal", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 5))
        tk.Label(self, text="Briefly describe what you want to build.", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").pack(side='top', anchor="w", pady=(0, 10))

        self.goal_text = ScrollableText(
            self, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.wizard_controller.font_size),
            on_zoom=self.wizard_controller.adjust_font_size
        )
        self.goal_text.pack(side='top', fill="both", expand=True, pady=5)

        existing_goal = self.project_data.get("goal", "").strip()
        self.goal_text.insert("1.0", existing_goal if existing_goal else c.WIZARD_CONCEPT_DEFAULT_GOAL)
        self.goal_text.text_widget.bind("<KeyRelease>", self._update_goal_state)
        self._update_button_state()

    def _update_goal_state(self, event=None):
        self.project_data["goal"] = self.goal_text.get("1.0", "end-1c").strip()
        self._update_button_state()

    def _update_button_state(self, event=None):
        content = self.project_data.get("goal", "").strip()
        self.generate_btn.set_state('normal' if content and content != c.WIZARD_CONCEPT_DEFAULT_GOAL else 'disabled')

    def _get_prompt(self):
        user_goal = self.project_data.get("goal", "")
        friendly_map = {k: v["label"] for k, v in self.questions_map.items()}
        segment_instructions = SegmentManager.build_prompt_instructions(c.CONCEPT_ORDER, friendly_map)

        parts = [
            c.WIZARD_CONCEPT_PROMPT_INTRO,
            "\n### User Goal\n```\n" + user_goal.strip() + "\n```",
            self._get_base_project_content(),
            "\n### Format Instructions",
            segment_instructions,
            c.WIZARD_CONCEPT_PROMPT_CORE_INSTR
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
        btn_process = RoundedButton(btn_container, text="Process & Review", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        btn_process.pack(side='right')
        ToolTip(btn_process, "Parse the LLM's response and open the segmented editor", delay=500)

        tk.Label(self, text="Generate Concept", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        instr_frame = tk.Frame(self, bg=c.DARK_BG)
        instr_frame.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(instr_frame, text="1. Copy prompt", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        copy_btn = RoundedButton(instr_frame, text="Copy Prompt", command=lambda: self._copy_to_clipboard(copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, radius=6, cursor="hand2")
        copy_btn.pack(side='left', padx=15)
        ToolTip(copy_btn, "Copy the prompt to your clipboard for use with an LLM", delay=500)

        tk.Label(self, text="2. Paste LLM Response (with tags)", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 0))
        self.llm_response_text = ScrollableText(
            self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.wizard_controller.font_size),
            on_zoom=self.wizard_controller.adjust_font_size
        )
        self.llm_response_text.pack(side='top', fill="both", expand=True, pady=5)
        self.llm_response_text.insert("1.0", self.project_data.get("concept_llm_response", ""))

        # Sync input area to state to prevent data loss on navigation
        self.llm_response_text.text_widget.bind("<KeyRelease>", lambda e: self.project_data.__setitem__("concept_llm_response", self.llm_response_text.get("1.0", "end-1c").strip()))

    def _copy_to_clipboard(self, button, text):
        pyperclip.copy(text)
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text="Copy Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

    def handle_llm_response(self):
        raw = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw: return

        content = strip_markdown_wrapper(raw)
        parsed_segments = SegmentManager.parse_segments(content)

        if not parsed_segments:
            # Fallback to merged view if tags are missing
            self.project_data["concept_md"] = content
            self.show_merged_view(content)
            return

        friendly_map = {k: v["label"] for k, v in self.questions_map.items()}
        mapped_segments = SegmentManager.map_parsed_segments_to_keys(parsed_segments, friendly_map)

        self.project_data["concept_segments"].clear()
        self.project_data["concept_segments"].update(mapped_segments)

        self.project_data["concept_signoffs"].clear()
        for k in mapped_segments.keys():
            self.project_data["concept_signoffs"][k] = False

        # CRITICAL: Clear merged Markdown when moving back to segments
        self.project_data["concept_md"] = ""
        self.project_data["concept_llm_response"] = "" # Clear the buffer on success
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
            on_change_callback=self.wizard_controller.update_nav_state,
            on_merge_callback=self.handle_merge
        )
        self.reviewer.pack(fill="both", expand=True, pady=5)
        self.wizard_controller._update_navigation_controls()

    def handle_merge(self, full_text):
        """
        Transitions the view to a single full-text editor (merged state).
        Clears segments and performs an immediate hard-save and lock-update.
        """
        self.project_data["concept_segments"].clear()
        self.project_data["concept_signoffs"].clear()
        self.project_data["concept_md"] = full_text

        # Sync the Wizard State immediately to unlock the 'Next' button Logic
        self.wizard_controller.state.update_from_view(self)
        self.wizard_controller.state.save()

        self.show_merged_view(full_text)

    def show_merged_view(self, content):
        """Displays the single text editor for the merged concept."""
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        self.questions = ["Is this concept clearly explained?", "Did we miss anything?"]
        self.current_question_index = 0
        self.questions_frame_visible = False

        # Grid configuration for main layout
        self.grid_rowconfigure(1, weight=0) # Questions Panel (dynamic height)
        self.grid_rowconfigure(2, weight=1) # Editor (expands)
        self.grid_columnconfigure(0, weight=1)

        # Header Control Row
        header_frame = tk.Frame(self, bg=c.DARK_BG)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(header_frame, text="Review Full Concept", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        controls = tk.Frame(header_frame, bg=c.DARK_BG)
        controls.pack(side="right")

        self.q_btn = RoundedButton(controls, text="Questions", command=self._toggle_questions, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, cursor="hand2")
        self.q_btn.pack(side="left", padx=(0,10))

        # Single toggle button for View Mode
        self.view_btn = RoundedButton(controls, text="Edit", command=self._toggle_view_mode, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="left", padx=(0, 0))
        self.view_btn_tooltip = ToolTip(self.view_btn, "Switch to raw text editor", delay=500)

        # Questions Panel Container (Row 1)
        self.questions_container = tk.Frame(self, bg=c.DARK_BG)
        self.questions_container.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Editor Container (Row 2)
        self.editor_frame = tk.Frame(self, bg=c.DARK_BG)
        self.editor_frame.grid(row=2, column=0, sticky="nsew")
        self.editor_frame.grid_rowconfigure(0, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        self.editor_text = ScrollableText(
            self.editor_frame, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.wizard_controller.font_size),
            on_zoom=self.wizard_controller.adjust_font_size
        )
        self.editor_text.insert("1.0", content)
        self.editor_text.text_widget.bind("<KeyRelease>", self._on_merged_text_change)

        self.markdown_renderer = MarkdownRenderer(
            self.editor_frame,
            base_font_size=self.wizard_controller.font_size,
            on_zoom=self.wizard_controller.adjust_font_size
        )

        # Default to Rendered View
        self.is_raw_mode = False
        self._apply_view_mode()

        self.wizard_controller._update_navigation_controls()

    def _on_merged_text_change(self, event=None):
        if hasattr(self, 'editor_text') and self.editor_text.winfo_exists():
            self.project_data["concept_md"] = self.editor_text.get("1.0", "end-1c").strip()

    def _toggle_view_mode(self):
        self.is_raw_mode = not self.is_raw_mode
        self._apply_view_mode()

    def _apply_view_mode(self):
        if self.is_raw_mode:
            # Switch to Editor
            self.markdown_renderer.grid_forget()
            self.editor_text.grid(row=0, column=0, sticky="nsew")

            self.view_btn.config(text="Render", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.view_btn_tooltip.text = "Switch to stylized Markdown preview"
        else:
            # Switch to Renderer
            current_text = self.editor_text.get("1.0", "end-1c")
            self.markdown_renderer.set_markdown(current_text)
            self.editor_text.grid_forget()
            self.markdown_renderer.grid(row=0, column=0, sticky="nsew")

            self.view_btn.config(text="Edit", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            self.view_btn_tooltip.text = "Switch to raw text editor"

        if self.view_btn_tooltip.tooltip_window:
             self.view_btn_tooltip.hide_tooltip()
             self.view_btn_tooltip.show_tooltip()

    def _toggle_questions(self):
        self.questions_frame_visible = not self.questions_frame_visible
        if self.questions_frame_visible:
            self._create_question_prompter()
            self.q_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            for widget in self.questions_container.winfo_children():
                widget.destroy()
            self.q_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _create_question_prompter(self):
        if self.questions_container.winfo_children(): return

        panel = tk.Frame(self.questions_container, bg=c.STATUS_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        panel.pack(fill='x', expand=True)

        content = tk.Frame(panel, bg=c.STATUS_BG, padx=10, pady=10)
        content.pack(fill='x', expand=True)

        self.question_label = tk.Label(content, text="", wraplength=600, justify="left", anchor="w", font=c.FONT_NORMAL, bg=c.STATUS_BG, fg=c.TEXT_COLOR)
        self.question_label.pack(side='left', fill='x', expand=True)

        actions_frame = tk.Frame(content, bg=c.STATUS_BG)
        actions_frame.pack(side='left', padx=(10,0))

        nav_frame = tk.Frame(actions_frame, bg=c.STATUS_BG)
        nav_frame.pack(anchor='e')
        self.prev_question_button = RoundedButton(nav_frame, text="<", command=self._show_prev_question, width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.prev_question_button.pack(side="left")
        self.next_question_button = RoundedButton(nav_frame, text=">", command=self._show_next_question, width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.next_question_button.pack(side="left", padx=2)

        copy_btn_frame = tk.Frame(actions_frame, bg=c.STATUS_BG)
        copy_btn_frame.pack(anchor='e', pady=(5, 0))

        copy_btn = RoundedButton(copy_btn_frame, text="Copy Context & Question", command=lambda: self._copy_question_prompt(copy_btn), width=160, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        copy_btn.pack(side="right")
        ToolTip(copy_btn, "Copy the full text and this question, asking for feedback (no rewrite)", delay=500)

        self._update_question_display()

    def _copy_question_prompt(self, btn):
        try:
            full_text = self.editor_text.get("1.0", "end-1c").strip()
            current_q = self.questions[self.current_question_index]

            prompt = c.WIZARD_QUESTION_PROMPT_TEMPLATE.format(
                context_label="Full Concept",
                context_content="```markdown\n" + full_text + "\n```",
                focus_name="Concept",
                focus_content="(Overview above)",
                question=current_q,
                instruction_suffix="Please answer the question or provide critical feedback regarding the concept. Do NOT rewrite the text."
            )

            self.clipboard_clear()
            self.clipboard_append(prompt)

            btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: btn.config(text="Copy Context & Question", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))
        except tk.TclError:
            messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.", parent=self)

    def _update_question_display(self):
        if not hasattr(self, 'question_label') or not self.question_label.winfo_exists(): return
        self.question_label.config(text=self.questions[self.current_question_index])
        self.prev_question_button.set_state("normal" if self.current_question_index > 0 else "disabled")
        self.next_question_button.set_state("normal" if self.current_question_index < len(self.questions) - 1 else "disabled")

    def _show_next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self._update_question_display()

    def _show_prev_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self._update_question_display()

    def is_editor_visible(self): return self.editor_is_active
    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over?", parent=self):
            self.project_data["concept_segments"].clear()
            self.project_data["concept_signoffs"].clear()
            self.project_data["concept_md"] = ""
            self.project_data["concept_llm_response"] = ""
            self.editor_is_active = False
            self.generation_mode_active = False
            self.show_initial_view()
            self.wizard_controller._update_navigation_controls()

    def get_goal_content(self):
        if hasattr(self, 'goal_text') and self.goal_text.winfo_exists():
            return self.goal_text.get("1.0", "end-1c").strip()
        return self.project_data.get("goal", "")

    def get_llm_response_content(self):
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            return {"concept_llm_response": self.llm_response_text.get("1.0", "end-1c").strip()}
        return {}

    def get_assembled_content(self):
        # FIX: If segments are empty (merged mode), return the existing flat MD
        if not self.project_data.get("concept_segments"):
            return self.project_data.get("concept_md", ""), {}, {}

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