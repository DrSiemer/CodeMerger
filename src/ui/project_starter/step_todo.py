import os
import json
import tkinter as tk
from tkinter import messagebox
from ... import constants as c
from ...core.paths import REFERENCE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.markdown_renderer import MarkdownRenderer
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from .segment_manager import SegmentManager
from .widgets.segmented_reviewer import SegmentedReviewer
from ..tooltip import ToolTip

class TodoView(tk.Frame):
    def __init__(self, parent, wizard_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.wizard_controller = wizard_controller
        self.project_data = project_data

        self.todo_content = self.project_data.get("todo_md", "")

        # Initialize questions_map before loading questions to prevent AttributeError
        self.questions_map = {}
        self.questions = self._load_questions()

        self.current_question_index = 0
        self.questions_frame_visible = True
        self.editor_is_active = False

        # State for merged view toggle
        self.is_raw_mode = False

        self.has_segments = bool(self.project_data.get("todo_segments"))

        if self.has_segments:
            self.show_editor_view()
        elif self.todo_content:
            # Fallback for manual or legacy content
            self.show_merged_view(self.todo_content)
        else:
            self.show_generation_view()

    def refresh_fonts(self):
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            self.llm_response_text.set_font_size(self.wizard_controller.font_size)
        if hasattr(self, 'editor_text') and self.editor_text.winfo_exists():
            self.editor_text.set_font_size(self.wizard_controller.font_size)
        if hasattr(self, 'markdown_renderer') and self.markdown_renderer.winfo_exists():
            self.markdown_renderer.set_font_size(self.wizard_controller.font_size)
        if hasattr(self, 'reviewer') and self.reviewer.winfo_exists():
            self.reviewer.refresh_fonts(self.wizard_controller.font_size)

    def _load_questions(self):
        questions_path = os.path.join(REFERENCE_DIR, "todo_questions.json")
        try:
            with open(questions_path, "r", encoding="utf-8") as f:
                content = f.read()
                if not content: return []
                # Check if it's the new format (dict of objects) or old (list)
                data = json.loads(content)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Populate the map for the SegmentedReviewer and assembly logic
                    self.questions_map = data
                    # Return empty list for the legacy self.questions used by manual mode
                    # Manual/Merged mode questions will be set explicitly
                    return []
                return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
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

    def _copy_prompt_to_clipboard(self, button, text):
        prompt_content = text
        self.clipboard_clear()
        self.clipboard_append(prompt_content)
        original_text = button.text
        original_bg = button.original_bg_color
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, state='disabled')
        self.after(2000, lambda: button.config(text=original_text, bg=original_bg, fg=c.BTN_GRAY_TEXT, state='normal'))

    def show_generation_view(self, prompt=None):
        if prompt is None:
            prompt = self._get_prompt()

        self._clear_frame()
        self.editor_is_active = False
        self.grid_rowconfigure(2, weight=1) # Response area expands
        self.grid_columnconfigure(0, weight=1)

        # Row 0: Header and Copy Button
        prompt_header = tk.Frame(self, bg=c.DARK_BG)
        prompt_header.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        tk.Label(prompt_header, text="1. Copy Prompt for LLM", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')

        copy_btn = RoundedButton(prompt_header, text="Copy Prompt", command=lambda: self._copy_prompt_to_clipboard(copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        copy_btn.pack(side='left', padx=15)

        # Row 1: Label for Input
        tk.Label(self, text="2. Paste LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=1, column=0, pady=(10, 5), sticky="w")

        # Row 2: Input Field
        self.llm_response_text = ScrollableText(
            self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.wizard_controller.font_size),
            on_zoom=self.wizard_controller.adjust_font_size
        )
        self.llm_response_text.grid(row=2, column=0, sticky='nsew')

        # Row 3: Action Button
        RoundedButton(self, text="Process & Review", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2").grid(row=3, column=0, pady=(10,0), sticky="e")

    def handle_llm_response(self):
        raw_content = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw_content:
            messagebox.showerror("Error", "The LLM response is empty.", parent=self)
            return

        content = strip_markdown_wrapper(raw_content)
        parsed_segments = SegmentManager.parse_segments(content)

        # Fallback to legacy editor if no segments found (e.g. LLM ignored instructions)
        if not parsed_segments:
            self.todo_content = content
            self.project_data["todo_md"] = content
            self.questions = ["Do these TODO steps fully cover everything described in the concept?", "Did we miss anything?"]
            self.wizard_controller.state.save() # Ensure persist even in fallback
            self.show_merged_view(content)
            return

        # Map friendly names back to internal keys if possible
        friendly_to_key = {v.lower(): k for k,v in c.TODO_PHASES.items()}
        mapped_segments = {}

        for name, text in parsed_segments.items():
            # Try exact match, then lower case match
            key = friendly_to_key.get(name.lower())
            if key:
                mapped_segments[key] = text
            else:
                # Store as custom key if not found in standard set
                mapped_segments[name] = text

        self.project_data["todo_segments"].clear()
        self.project_data["todo_segments"].update(mapped_segments)

        self.project_data["todo_signoffs"].clear()
        for k in mapped_segments.keys():
            self.project_data["todo_signoffs"][k] = False

        # CRITICAL FIX: Save state immediately after processing to persist new segments
        self.wizard_controller.state.save()

        self.show_editor_view()

    def show_editor_view(self):
        self._clear_frame()
        self.editor_is_active = True

        header = tk.Frame(self, bg=c.DARK_BG)
        header.pack(side='top', fill="x", pady=(0, 5))
        tk.Label(header, text="Review TODO Plan", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        # Questions for TODO are loaded differently, we might need a map
        questions_path = os.path.join(REFERENCE_DIR, "todo_questions.json")
        try:
            with open(questions_path, "r", encoding="utf-8") as f:
                q_map = json.loads(f.read())
        except Exception: q_map = {}

        # Ensure we have data keys
        data_keys = set(self.project_data["todo_segments"].keys())
        ordered_keys = [k for k in c.TODO_ORDER if k in data_keys]
        # Append any custom/unknown keys at the end
        ordered_keys += [k for k in data_keys if k not in ordered_keys]

        if not ordered_keys:
            self.handle_reset()
            return

        self.reviewer = SegmentedReviewer(
            parent=self,
            segment_keys=ordered_keys,
            friendly_names_map=c.TODO_PHASES,
            segments_data=self.project_data["todo_segments"],
            signoffs_data=self.project_data["todo_signoffs"],
            questions_map=q_map,
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
        self.project_data["todo_segments"].clear()
        self.project_data["todo_signoffs"].clear()
        self.project_data["todo_md"] = full_text

        # Sync the Wizard State immediately to unlock the 'Next' button Logic
        self.wizard_controller.state.update_from_view(self)
        self.wizard_controller.state.save()

        # Set generic questions for the full text
        self.questions = ["Do these TODO steps fully cover everything described in the concept?", "Did we miss anything?"]
        self.show_merged_view(full_text)

    def show_merged_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.grid_rowconfigure(1, weight=0) # Questions (dynamic)
        self.grid_rowconfigure(2, weight=1) # Editor (expands)
        self.grid_columnconfigure(0, weight=1)

        header_frame = tk.Frame(self, bg=c.DARK_BG)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(header_frame, text="Edit Your TODO Plan", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        controls = tk.Frame(header_frame, bg=c.DARK_BG)
        controls.pack(side="right")

        # Questions Toggle (if available)
        if self.questions:
             self.q_btn = RoundedButton(controls, text="Questions", command=self._toggle_questions, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, cursor="hand2")
             self.q_btn.pack(side="left", padx=(0,10))

        # View Switch Button
        self.view_btn = RoundedButton(controls, text="Edit", command=self._toggle_view_mode, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="left", padx=(0, 0))
        self.view_btn_tooltip = ToolTip(self.view_btn, "Switch to raw text editor", delay=500)

        # Questions Container
        self.questions_container = tk.Frame(self, bg=c.DARK_BG)
        self.questions_container.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Editor Frame
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
        # Bind text change for saving
        self.editor_text.text_widget.bind("<KeyRelease>", lambda e: self.project_data.__setitem__("todo_md", self.editor_text.get("1.0", "end-1c").strip()))

        self.markdown_renderer = MarkdownRenderer(
            self.editor_frame,
            base_font_size=self.wizard_controller.font_size,
            on_zoom=self.wizard_controller.adjust_font_size
        )

        # Default to Rendered View
        self.is_raw_mode = False
        self._apply_view_mode()

        self.wizard_controller._update_navigation_controls()

    def is_editor_visible(self):
        return self.editor_is_active

    def _toggle_view_mode(self):
        self.is_raw_mode = not self.is_raw_mode
        self._apply_view_mode()

    def _apply_view_mode(self):
        if self.is_raw_mode:
            self.markdown_renderer.grid_forget()
            self.editor_text.grid(row=0, column=0, sticky="nsew")

            self.view_btn.config(text="Render", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.view_btn_tooltip.text = "Switch to stylized Markdown preview"
        else:
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

    def _copy_question_prompt(self, button):
        try:
            todo_content = self.editor_text.get("1.0", "end-1c").strip()
            current_question = self.questions[self.current_question_index]

            prompt_text = f"### Full TODO Plan\n```markdown\n{todo_content}\n```\n\n### Question\n{current_question}\n\nInstruction: Please answer the question or provide critical feedback regarding the plan. Do NOT rewrite the text."

            self.clipboard_clear()
            self.clipboard_append(prompt_text)

            button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, state='disabled')
            self.after(2000, lambda: button.config(text="Copy Context & Question", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, state='normal'))
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy to clipboard: {e}", parent=self)

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over? Current plan will be lost.", parent=self):
            self.project_data["todo_segments"].clear()
            self.project_data["todo_signoffs"].clear()
            self.project_data["todo_md"] = ""
            self.todo_content = ""
            # Reload questions
            self.questions = self._load_questions()
            self.questions_frame_visible = True
            self.current_question_index = 0
            self.show_generation_view()
            self.wizard_controller._update_navigation_controls()

    def get_assembled_content(self):
        # FIX: If segments are empty (merged mode), return the existing flat MD
        if not self.project_data.get("todo_segments"):
            return self.project_data.get("todo_md", ""), {}, {}

        friendly_map = {k: v["label"] for k, v in self.questions_map.items()} if self.questions_map else c.TODO_PHASES
        full_text = SegmentManager.assemble_document(
            self.project_data["todo_segments"],
            c.TODO_ORDER,
            friendly_map
        )
        return full_text, self.project_data["todo_segments"], self.project_data["todo_signoffs"]

    def get_todo_content(self):
        return self.get_assembled_content()[0]

    def _clear_frame(self):
        for i in range(self.grid_size()[1]):
            self.grid_rowconfigure(i, weight=0)
        for i in range(self.grid_size()[0]):
            self.grid_columnconfigure(i, weight=0)
        for widget in self.winfo_children():
            widget.destroy()