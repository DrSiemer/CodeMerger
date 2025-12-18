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
        self.questions_frame_visible = True
        self.editor_is_active = False

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
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return []

    def show_initial_view(self):
        self._clear_frame()
        self.editor_is_active = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        tk.Label(self, text="Describe Your Goal", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=10, sticky="w")
        tk.Label(self, text="Briefly describe what you want to build. This will be used to generate a structured concept document from the template.", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").grid(row=1, column=0, pady=5, sticky="w")

        self.goal_text = ScrollableText(self, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.goal_text.grid(row=2, column=0, pady=10, sticky="ew")

        existing_goal = self.project_data.get("goal", "").strip()
        if existing_goal:
            self.goal_text.insert("1.0", existing_goal)
        else:
            self.goal_text.insert("1.0", DEFAULT_GOAL_TEXT)

        self.goal_text.text_widget.bind("<KeyRelease>", self._update_button_state)

        self.generate_btn = RoundedButton(self, text="Generate Concept Prompt", command=self.handle_prompt_generation, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.generate_btn.grid(row=3, column=0, pady=10, sticky="e")
        self._update_button_state()

        tk.Frame(self, bg=c.DARK_BG).grid(row=4, column=0)

    def _update_button_state(self, event=None):
        content = self.goal_text.get("1.0", "end-1c").strip()
        if content and content != DEFAULT_GOAL_TEXT:
            self.generate_btn.set_state('normal')
        else:
            self.generate_btn.set_state('disabled')

    def _get_base_project_content(self):
        base_path = self.project_data.get("base_project_path", tk.StringVar()).get()
        base_files = self.project_data.get("base_project_files", [])

        if not base_path or not base_files:
            return ""

        content_blocks = []
        content_blocks.append("\n### Example Project Code (For Reference Only)\n")
        content_blocks.append("The user has provided an example project. You may refer to this for context on their coding style or architecture preferences, but do NOT copy it directly.\n")

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

    def handle_prompt_generation(self):
        user_goal = self.goal_text.get("1.0", 'end-1c')
        if not user_goal.strip() or user_goal.strip() == DEFAULT_GOAL_TEXT:
            messagebox.showerror("Error", "Please describe your goal before generating the prompt.", parent=self)
            return

        template_path = os.path.join(REFERENCE_DIR, "concept.md")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                concept_template = f.read()
        except FileNotFoundError:
             messagebox.showerror("Error", f"Concept template not found at {template_path}", parent=self)
             return

        example_code = self._get_base_project_content()

        prompt = f"""Based on the following user goal, expand it into a full project concept document. Use the provided template as a strict guide for the structure.

### User Goal
```
{user_goal.strip()}
```

### Template (`concept.md`)```markdown
{concept_template}
```

{example_code}

### Instructions
1.  Fill in every section of the template that is relevant to the user's goal.
2.  If a section from the template is not applicable, omit that section from the output.
3.  Interpret the user's goal to generate plausible details for features, principles, and the data synchronization strategy.
4.  Return *only* the generated markdown content for the new `concept.md` file, without any extra explanations or pleasantries.
"""
        self.show_generation_view(prompt)

    def _copy_prompt_to_clipboard(self, button):
        if hasattr(self, 'prompt_area') and self.prompt_area.winfo_exists():
            prompt_content = self.prompt_area.get('1.0', 'end-1c')
            self.clipboard_clear()
            self.clipboard_append(prompt_content)
            original_text = button.text
            original_bg = button.original_bg_color
            button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, state='disabled')
            self.after(2000, lambda: button.config(text=original_text, bg=original_bg, fg=c.BTN_GRAY_TEXT, state='normal'))

    def show_generation_view(self, prompt):
        self._clear_frame()
        self.editor_is_active = False
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        prompt_header = tk.Frame(self, bg=c.DARK_BG)
        prompt_header.grid(row=0, column=0, pady=(0, 5), sticky="ew")
        tk.Label(prompt_header, text="1. Copy Prompt for LLM", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')
        copy_btn = RoundedButton(prompt_header, text="Copy", command=lambda: self._copy_prompt_to_clipboard(copy_btn), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        copy_btn.pack(side='right')

        self.prompt_area = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.prompt_area.insert("1.0", prompt)
        self.prompt_area.grid(row=1, column=0, sticky='nsew')

        tk.Label(self, text="2. Paste LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=2, column=0, pady=(10, 5), sticky="w")
        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.llm_response_text.grid(row=3, column=0, sticky='nsew')

        RoundedButton(self, text="Expand to Editor", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2").grid(row=4, column=0, pady=(10,0), sticky="e")

    def handle_llm_response(self):
        raw_content = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw_content:
            messagebox.showerror("Error", "The LLM response is empty.", parent=self)
            return

        # Strip wrapper if present
        self.concept_content = strip_markdown_wrapper(raw_content)
        self.project_data["concept_md"] = self.concept_content
        self.show_editor_view(self.concept_content)

    def show_editor_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        header_frame = tk.Frame(self, bg=c.DARK_BG)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(header_frame, text="Edit Your Concept", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        action_buttons_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        action_buttons_frame.pack(side="right")
        tk.Label(action_buttons_frame, text="Raw", font=c.FONT_NORMAL, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='left', padx=(0,5))
        self.view_switch = SwitchButton(action_buttons_frame, command=self._toggle_view, initial_state=False)
        self.view_switch.pack(side='left')
        tk.Label(action_buttons_frame, text="Rendered", font=c.FONT_NORMAL, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='left', padx=(5,10))

        self.editor_frame = tk.Frame(self, bg=c.DARK_BG)
        self.editor_frame.grid(row=1, column=0, sticky="nsew")
        self.editor_frame.grid_rowconfigure(0, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        self.editor_text = ScrollableText(self.editor_frame, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.editor_text.insert("1.0", content)
        self.editor_text.text_widget.bind('<KeyRelease>', self._sync_editor_to_state)

        self.markdown_renderer = MarkdownRenderer(self.editor_frame)

        self._toggle_view(self.view_switch.get_state())

        if self.questions and self.questions_frame_visible:
            self._create_question_prompter(self)

        self._sync_editor_to_state() # Trigger initial validation
        self.wizard_controller._update_navigation_controls()

    def _sync_editor_to_state(self, event=None):
        """Updates the project data and triggers validation check."""
        content = self.editor_text.get("1.0", "end-1c").strip()
        self.project_data["concept_md"] = content
        self.wizard_controller.update_nav_state()

    def is_editor_visible(self):
        return self.editor_is_active

    def _toggle_view(self, is_rendered):
        if is_rendered:
            self.editor_text.grid_forget()
            markdown_content = self.editor_text.get("1.0", "end-1c")
            self.markdown_renderer.set_markdown(markdown_content)
            self.markdown_renderer.grid(row=0, column=0, sticky="nsew")
        else:
            self.markdown_renderer.grid_forget()
            self.editor_text.grid(row=0, column=0, sticky="nsew")

    def _create_question_prompter(self, parent):
        self.questions_frame = tk.Frame(parent, bg=c.STATUS_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        self.questions_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        content = tk.Frame(self.questions_frame, bg=c.STATUS_BG, padx=10, pady=10)
        content.pack(fill='x', expand=True)
        self.question_label = tk.Label(content, text="", wraplength=500, justify="left", anchor="w", font=c.FONT_NORMAL, bg=c.STATUS_BG, fg=c.TEXT_COLOR)
        self.question_label.pack(side='left', fill='x', expand=True)
        actions_frame = tk.Frame(content, bg=c.STATUS_BG)
        actions_frame.pack(side='left', padx=(10,0))

        nav_frame = tk.Frame(actions_frame, bg=c.STATUS_BG)
        nav_frame.pack()
        self.prev_question_button = RoundedButton(nav_frame, text="<", command=self._show_prev_question, width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.prev_question_button.pack(side="left")
        self.next_question_button = RoundedButton(nav_frame, text=">", command=self._show_next_question, width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.next_question_button.pack(side="left", padx=2)

        bottom_actions = tk.Frame(actions_frame, bg=c.STATUS_BG)
        bottom_actions.pack(pady=(2,0))
        copy_btn = RoundedButton(bottom_actions, text="Copy", command=lambda: self._copy_question_prompt(copy_btn), width=40, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        copy_btn.pack(side='left')
        remove_btn = RoundedButton(bottom_actions, text='X', command=self._remove_current_question, width=24, height=24, font=(c.FONT_SMALL_BUTTON[0], 10, 'bold'), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        remove_btn.pack(side='left', padx=2)
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
            concept_content = self.editor_text.get("1.0", "end-1c").strip()
            current_question = self.questions[self.current_question_index]
            prompt_text = f"""Please act as a senior software developer and provide critical feedback on the following project concept document.

### Your Task
{current_question}

---

### Project Concept Document
```markdown
{concept_content}
```"""
            self.clipboard_clear()
            self.clipboard_append(prompt_text)
            original_text = button.text
            original_bg = button.original_bg_color
            button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, state='disabled')
            self.after(2000, lambda: button.config(text=original_text, bg=original_bg, fg=c.BTN_GRAY_TEXT, state='normal'))
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy to clipboard: {e}", parent=self)

    def _remove_current_question(self):
        if not self.questions or not hasattr(self, 'questions_frame') or not self.questions_frame.winfo_exists(): return
        del self.questions[self.current_question_index]
        if not self.questions:
            self.questions_frame_visible = False
            self.questions_frame.destroy()
            return
        if self.current_question_index >= len(self.questions):
            self.current_question_index = len(self.questions) - 1
        self._update_question_display()

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over? The current concept text will be lost.", parent=self):
            self.project_data["concept_md"] = ""
            self.project_data["goal"] = ""
            self.concept_content = ""
            self.questions = self._load_questions()
            self.questions_frame_visible = True
            self.current_question_index = 0
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
        for i in range(self.grid_size()[1]):
            self.grid_rowconfigure(i, weight=0)
        for i in range(self.grid_size()[0]):
            self.grid_columnconfigure(i, weight=0)
        for widget in self.winfo_children():
            widget.destroy()