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

class Step3TodoView(tk.Frame):
    def __init__(self, parent, wizard_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.wizard_controller = wizard_controller
        self.project_data = project_data

        self.todo_content = self.project_data.get("todo_md", "")
        self.questions = self._load_questions()
        self.current_question_index = 0
        self.questions_frame_visible = True
        self.editor_is_active = False

        if self.todo_content:
            self.show_editor_view(self.todo_content)
        else:
            self.show_generation_view()

    def _load_questions(self):
        questions_path = os.path.join(REFERENCE_DIR, "todo_questions.json")
        try:
            with open(questions_path, "r", encoding="utf-8") as f:
                content = f.read()
                if not content: return []
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return []

    def _generate_prompt(self):
        concept_md = self.project_data.get("concept_md")
        if not concept_md:
            messagebox.showerror("Error", "Concept.md content is missing. Please complete Step 2 first.", parent=self)
            return None

        template_path = os.path.join(REFERENCE_DIR, "todo.md")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                todo_template = f.read()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Reference file not found: {template_path}", parent=self)
            return None

        prompt = f"""Based on the following project `concept.md`, generate a detailed `todo.md` file. Use the provided `todo.md` template as a strict guide for the structure and phases.

### Project Concept (`concept.md`)
```markdown
{concept_md}
```

### TODO Template (`/reference/todo.md`)```markdown
{todo_template}
```

### Instructions
1.  Read the `concept.md` to understand the project's goals, features, and technical details.
2.  Fill out the tasks in each phase of the `todo.md` template with specific actions relevant to the project described in the concept.
3.  Be specific. Instead of a generic task like "Set up the database," write "Design and implement tables for `users` and `[primary_resource]` as defined in `concept.md`."
4.  Return *only* the generated markdown content for the new `todo.md` file, without any extra explanations or pleasantries.
"""
        return prompt

    def _copy_prompt_to_clipboard(self, button):
        if hasattr(self, 'prompt_area') and self.prompt_area.winfo_exists():
            prompt_content = self.prompt_area.get('1.0', 'end-1c')
            self.clipboard_clear()
            self.clipboard_append(prompt_content)
            original_text = button.text
            original_bg = button.original_bg_color
            button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, state='disabled')
            self.after(2000, lambda: button.config(text=original_text, bg=original_bg, fg=c.BTN_GRAY_TEXT, state='normal'))

    def show_generation_view(self):
        self._clear_frame()
        self.editor_is_active = False
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        prompt = self._generate_prompt()
        if prompt is None:
            tk.Label(self, text="Could not generate prompt. Please ensure Step 2 is complete.", bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0)
            return

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

        self.todo_content = strip_markdown_wrapper(raw_content)
        self.project_data["todo_md"] = self.todo_content
        self.show_editor_view(self.todo_content)

    def show_editor_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        header_frame = tk.Frame(self, bg=c.DARK_BG)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(header_frame, text="Edit Your TODO Plan", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

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
        self.markdown_renderer = MarkdownRenderer(self.editor_frame)

        self._toggle_view(self.view_switch.get_state())

        if self.questions and self.questions_frame_visible:
            self._create_question_prompter(self)

        self.wizard_controller._update_navigation_controls()

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
            todo_content = self.editor_text.get("1.0", "end-1c").strip()
            current_question = self.questions[self.current_question_index]
            prompt_text = f"""Please act as a senior project manager and provide critical feedback on the following project plan.

### Your Task
{current_question}

---

### Project TODO Plan
```markdown
{todo_content}
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
        if messagebox.askyesno("Confirm", "Are you sure you want to start over? The current TODO plan will be lost.", parent=self):
            self.project_data["todo_md"] = ""
            self.todo_content = ""
            self.questions = self._load_questions()
            self.questions_frame_visible = True
            self.current_question_index = 0
            self.show_generation_view()
            self.wizard_controller._update_navigation_controls()

    def get_todo_content(self):
        if hasattr(self, 'editor_text') and self.editor_text.winfo_exists():
            return self.editor_text.get("1.0", "end-1c").strip()
        return self.todo_content

    def _clear_frame(self):
        for i in range(self.grid_size()[1]):
            self.grid_rowconfigure(i, weight=0)
        for i in range(self.grid_size()[0]):
            self.grid_columnconfigure(i, weight=0)
        for widget in self.winfo_children():
            widget.destroy()