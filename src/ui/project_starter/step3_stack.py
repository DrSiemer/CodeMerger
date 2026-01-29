import tkinter as tk
import json
import pyperclip
from tkinter import messagebox
from ... import constants as c
from ...core.utils import save_config, load_config
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from ..tooltip import ToolTip

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

        if self.stack_content:
            display_content = "\n".join([s.strip() for s in self.stack_content.split(',') if s.strip()])
            self.show_editor_view(display_content)
        else:
            self.show_initial_view()

    def show_initial_view(self):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = False

        # ACTION BUTTON AT BOTTOM
        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill="x", pady=15)
        self.save_exp_btn = RoundedButton(btn_container, text="Save as Default", command=self._save_experience, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        ToolTip(self.save_exp_btn, "Save this experience text to your application settings for future projects", delay=500)

        btn_gen = RoundedButton(btn_container, text="Generate Stack Recommendation", command=self.handle_prompt_generation, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        btn_gen.pack(side='right')
        ToolTip(btn_gen, "Ask the LLM to recommend a technology stack based on your concept and experience", delay=500)

        # TOP CONTENT
        header_text = "Edit your known languages, frameworks, and environment details." if self.saved_experience.strip() else "List your known languages, frameworks, and environment details."
        tk.Label(self, text="Your Experience & Environment", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 5))
        tk.Label(self, text=header_text, wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").pack(side='top', anchor="w", pady=(0, 10))

        self.experience_text = ScrollableText(self, height=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.experience_text.pack(side='top', fill="both", expand=True, pady=5)
        self.experience_text.insert("1.0", self.saved_experience)
        self.experience_text.text_widget.bind('<KeyRelease>', self._on_exp_change)
        self._on_exp_change()

    def _on_exp_change(self, event=None):
        if self.experience_text.get("1.0", "end-1c").strip() != self.saved_experience.strip():
            if not self.save_exp_btn.winfo_ismapped(): self.save_exp_btn.pack(side='left')
        else: self.save_exp_btn.pack_forget()

    def _save_experience(self):
        new_exp = self.experience_text.get("1.0", "end-1c")
        self.app_config['user_experience'] = new_exp
        save_config(self.app_config)
        self.saved_experience = new_exp
        self.save_exp_btn.pack_forget()

    def _get_prompt(self):
        concept = self.project_data.get("concept_md", "")
        experience = self.experience_text.get("1.0", "end-1c")
        parts = [
            "Based on the project concept and the developer's experience, recommend the best technical stack for this project.",
            "\n### Developer Experience\n```\n" + (experience if experience.strip() else "No specific experience listed. Recommend standard industry defaults.") + "\n```",
            "\n### Project Concept\n```markdown\n" + concept + "\n```",
            "\n### Instructions\n1. Analyze requirements against known skills.\n2. Return the recommended stack as a raw JSON list of strings.\n   - Example: [\"Python 3.10\", \"Flask\"]\n3. Return ONLY the JSON."
        ]
        return "\n".join(parts)

    def handle_prompt_generation(self):
        prompt = self._get_prompt()
        self.show_generation_view(prompt)

    def show_generation_view(self, prompt):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = True
        self.wizard_controller._update_navigation_controls()

        # ACTION BUTTON AT BOTTOM
        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        btn_proc = RoundedButton(btn_container, text="Process Response", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        btn_proc.pack(side='right')
        ToolTip(btn_proc, "Parse the LLM's recommended stack list", delay=500)

        # TOP CONTENT
        tk.Label(self, text="Generate Stack", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        instr_frame = tk.Frame(self, bg=c.DARK_BG); instr_frame.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(instr_frame, text="1. Copy prompt and paste it into your LLM.", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        copy_btn = RoundedButton(instr_frame, text="Copy Prompt", command=lambda: self._copy_to_clipboard(copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, radius=6, cursor="hand2")
        copy_btn.pack(side='left', padx=15)
        ToolTip(copy_btn, "Copy the prompt to your clipboard", delay=500)

        tk.Label(self, text="2. Paste Stack Recommendation below", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 5))
        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.llm_response_text.pack(side='top', fill="both", expand=True, pady=5)

    def _copy_to_clipboard(self, button, text):
        pyperclip.copy(text)
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text="Copy Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT))

    def handle_llm_response(self):
        raw_content = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw_content: return
        try:
            start_idx, end_idx = raw_content.find('['), raw_content.rfind(']')
            if start_idx == -1 or end_idx == -1: raise ValueError("No JSON list")
            json_str = raw_content[start_idx:end_idx+1].replace("'", '"')
            stack_list = json.loads(json_str)
            self.project_data["stack"].set(", ".join(stack_list))
            self.show_editor_view("\n".join(stack_list))
        except Exception:
            tk.messagebox.showerror("Error", "Could not parse JSON list.", parent=self)

    def show_editor_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        # HEADER & FOOTER AT EDGES
        tk.Label(self, text="Selected Code Stack", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 5))
        tk.Label(self, text="Do you agree with using this stack for your project? (one subject per line)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='bottom', anchor="w", pady=(5, 0))

        # CENTER CONTENT
        self.stack_editor = ScrollableText(self, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.stack_editor.pack(side='top', fill="both", expand=True, pady=5)
        self.stack_editor.insert("1.0", content)
        self.stack_editor.text_widget.bind('<KeyRelease>', self._sync_editor_to_state)

        # Trigger Wizard UI Update
        self.wizard_controller._update_navigation_controls()
        self.wizard_controller.update_nav_state()

    def _sync_editor_to_state(self, event=None):
        if hasattr(self, 'stack_editor') and self.stack_editor.winfo_exists():
            raw_text = self.stack_editor.get("1.0", "end-1c")
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            self.project_data["stack"].set(", ".join(lines))
        self.wizard_controller.update_nav_state()

    def handle_reset(self):
        if tk.messagebox.askyesno("Confirm", "Reset stack selection?", parent=self):
            self.project_data["stack"].set("")
            self.show_initial_view()
            self.wizard_controller._update_navigation_controls()

    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active

    def get_stack_content(self):
        if hasattr(self, 'stack_editor') and self.stack_editor.winfo_exists():
            raw_text = self.stack_editor.get("1.0", "end-1c")
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            return ", ".join(lines)
        return self.project_data["stack"].get()

    def _clear_frame(self):
        for widget in self.winfo_children(): widget.destroy()