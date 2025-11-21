import tkinter as tk
import json
import re
from tkinter import messagebox
from ... import constants as c
from ...core.utils import save_config, load_config
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText

class Step3StackView(tk.Frame):
    def __init__(self, parent, wizard_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.wizard_controller = wizard_controller
        self.project_data = project_data
        self.app_config = load_config()
        self.saved_experience = self.app_config.get('user_experience', '')
        self.stack_content = self.project_data["stack"].get()

        self.editor_is_active = False
        self.generation_mode_active = False

        # If we have existing content (comma separated), display it as a list
        if self.stack_content:
            display_content = "\n".join([s.strip() for s in self.stack_content.split(',') if s.strip()])
            self.show_editor_view(display_content)
        else:
            self.show_initial_view()

    def show_initial_view(self):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Header ---
        tk.Label(self, text="Your Experience & Environment", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky='w', pady=(10, 5))
        tk.Label(self, text="List your known languages, frameworks, and environment details. This helps the LLM recommend the best stack for you.", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").grid(row=1, column=0, sticky='w')

        # --- Text Area ---
        self.experience_text = ScrollableText(self, height=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.experience_text.grid(row=2, column=0, pady=5, sticky='nsew')
        self.experience_text.insert("1.0", self.saved_experience)
        self.experience_text.text_widget.bind('<KeyRelease>', self._on_exp_change)

        # --- Action Buttons (Bottom Row) ---
        button_frame = tk.Frame(self, bg=c.DARK_BG)
        button_frame.grid(row=3, column=0, pady=15, sticky='ew')
        button_frame.columnconfigure(1, weight=1) # Spacer

        # Save button (Bottom Left) - Hidden initially
        self.save_exp_btn = RoundedButton(button_frame, text="Save Changes", command=self._save_experience, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        # We pack/grid it later in _on_exp_change

        # Generate button (Bottom Right)
        self.generate_btn = RoundedButton(button_frame, text="Generate Stack Recommendation", command=self.handle_prompt_generation, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.generate_btn.pack(side='right')

    def _on_exp_change(self, event=None):
        current_text = self.experience_text.get("1.0", "end-1c")
        if current_text != self.saved_experience:
            if not self.save_exp_btn.winfo_ismapped():
                self.save_exp_btn.pack(side='left')
        else:
            self.save_exp_btn.pack_forget()

    def _save_experience(self):
        new_exp = self.experience_text.get("1.0", "end-1c")
        self.app_config['user_experience'] = new_exp
        save_config(self.app_config)
        self.saved_experience = new_exp
        self.save_exp_btn.pack_forget()
        # Button disappearance confirms save

    def handle_prompt_generation(self):
        concept = self.project_data.get("concept_md", "")
        experience = self.experience_text.get("1.0", "end-1c")

        prompt = f"""Based on the project concept and the developer's experience, recommend the best technical stack for this project.

### Developer Experience
```
{experience if experience.strip() else "No specific experience listed. Recommend standard, modern industry defaults."}
```

### Project Concept
```markdown
{concept}
```

### Instructions
1.  Analyze the concept requirements against the developer's known skills.
2.  Select a cohesive set of technologies (Languages, Frameworks, Database, Tools) that minimizes the learning curve while robustly supporting the project features.
3.  **CRITICAL:** Return the recommended stack as a raw JSON list of strings.
    - Example: `["Python 3.10", "Flask", "SQLite", "HTML/CSS/JS"]`
    - Do not include any other text outside the JSON structure.
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
        self.generation_mode_active = True
        self.wizard_controller._update_navigation_controls()

        self.grid_rowconfigure(1, weight=1) # Prompt area grows
        self.grid_rowconfigure(3, weight=1) # Paste area grows
        self.grid_columnconfigure(0, weight=1)

        # --- Step 1: Copy ---
        prompt_header = tk.Frame(self, bg=c.DARK_BG)
        prompt_header.grid(row=0, column=0, pady=(0, 5), sticky="ew")
        tk.Label(prompt_header, text="1. Copy Prompt", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')
        copy_btn = RoundedButton(prompt_header, text="Copy", command=lambda: self._copy_prompt_to_clipboard(copy_btn), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        copy_btn.pack(side='right')

        self.prompt_area = ScrollableText(self, wrap=tk.WORD, height=10, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.prompt_area.insert("1.0", prompt)
        self.prompt_area.grid(row=1, column=0, sticky='nsew')

        # --- Step 2: Paste ---
        tk.Label(self, text="2. Paste Stack Recommendation", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=2, column=0, pady=(15, 5), sticky="w")

        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, height=10, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.llm_response_text.grid(row=3, column=0, sticky='nsew')

        # --- Action ---
        RoundedButton(self, text="Process Response", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2").grid(row=4, column=0, pady=(10,0), sticky="e")

    def handle_llm_response(self):
        raw_content = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw_content:
            tk.messagebox.showerror("Error", "The response is empty.", parent=self)
            return

        start_idx = raw_content.find('[')
        end_idx = raw_content.rfind(']')

        if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
            tk.messagebox.showerror("Error", "Could not find a valid JSON list [...] in the response.", parent=self)
            return

        json_str = raw_content[start_idx:end_idx+1]

        try:
            stack_list = json.loads(json_str)
            if not isinstance(stack_list, list):
                raise ValueError("JSON is not a list")

            stack_list = [str(item) for item in stack_list]
            display_text = "\n".join(stack_list)

            self.project_data["stack"].set(", ".join(stack_list))
            self.show_editor_view(display_text)

        except (json.JSONDecodeError, ValueError) as e:
            tk.messagebox.showerror("Parsing Error", f"Could not parse JSON response: {e}\n\nPlease check the pasted text.", parent=self)

    def show_editor_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        tk.Label(self, text="Selected Code Stack", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=(10, 5), sticky="w")
        tk.Label(self, text="Edit the stack details below (one item per line).", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).grid(row=1, column=0, sticky="w", pady=(0, 10))

        self.stack_editor = ScrollableText(self, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.stack_editor.insert("1.0", content)
        self.stack_editor.grid(row=2, column=0, sticky="nsew")

        # Bind key release to update the internal variable immediately, which triggers the Next button state
        self.stack_editor.text_widget.bind('<KeyRelease>', self._sync_editor_to_state)

        # Trigger validation immediately to ensure Next button is correct
        self.wizard_controller._update_navigation_controls()
        self.wizard_controller.update_nav_state()

    def _sync_editor_to_state(self, event=None):
        raw_text = self.stack_editor.get("1.0", "end-1c")
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        final_stack_str = ", ".join(lines)

        # Update the StringVar without triggering a full view refresh
        self.project_data["stack"].set(final_stack_str)

        # Tell the wizard to re-check if "Next" should be enabled
        self.wizard_controller.update_nav_state()

    def handle_reset(self):
        if tk.messagebox.askyesno("Confirm", "Reset stack selection?", parent=self):
            self.project_data["stack"].set("")
            self.show_initial_view()
            self.wizard_controller._update_navigation_controls()

    def is_step_in_progress(self):
        """Returns True if we are past the initial screen (Generation or Editor mode)."""
        return self.editor_is_active or self.generation_mode_active

    def get_stack_content(self):
        if hasattr(self, 'stack_editor') and self.stack_editor.winfo_exists():
            raw_text = self.stack_editor.get("1.0", "end-1c")
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            return ", ".join(lines)
        return self.project_data["stack"].get()

    def _clear_frame(self):
        for i in range(self.grid_size()[1]):
            self.grid_rowconfigure(i, weight=0)
        for i in range(self.grid_size()[0]):
            self.grid_columnconfigure(i, weight=0)
        for widget in self.winfo_children():
            widget.destroy()