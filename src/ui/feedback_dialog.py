import tkinter as tk
import os
from tkinter import Frame, Label, ttk, BooleanVar
from .. import constants as c
from .widgets.rounded_button import RoundedButton
from .widgets.markdown_renderer import MarkdownRenderer
from .window_utils import position_window
from .style_manager import apply_dark_theme
from ..core.paths import ICON_PATH
from ..core.utils import save_config

class FeedbackDialog(tk.Toplevel):
    def __init__(self, parent, plan, on_apply=None, on_refuse=None):
        super().__init__(parent)
        self.parent = parent
        self.plan = plan
        self.on_apply = on_apply
        self.on_refuse = on_refuse
        self.app_state = parent.app_state if hasattr(parent, 'app_state') else parent.master.app_state
        self.withdraw()
        self.title("AI Response Review")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        apply_dark_theme(self)

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        title_text = "Review Proposed Update" if on_apply else "Review Last Update"
        Label(main_frame, text=title_text, font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        self.renderers =[]

        tab_indices = {}
        current_idx = 0

        # Preserve the preferred order: Intro, Answers, Changes, Verification
        if plan.get('intro'):
            self._add_tab("Intro", plan.get('intro'))
            tab_indices['intro'] = current_idx
            current_idx += 1

        if plan.get('answers'):
            self._add_tab("Answers", plan.get('answers'))
            tab_indices['answers'] = current_idx
            current_idx += 1

        if plan.get('changes'):
            self._add_tab("Changes", plan.get('changes'))
            tab_indices['changes'] = current_idx
            current_idx += 1

        if plan.get('verification'):
            self._add_tab("Verification", plan.get('verification'))
            tab_indices['verification'] = current_idx
            current_idx += 1

        # Tab Selection Priority
        if 'answers' in tab_indices:
            self.notebook.select(tab_indices['answers'])
        elif 'verification' in tab_indices:
            self.notebook.select(tab_indices['verification'])
        elif current_idx > 0:
            self.notebook.select(0)

        bottom_frame = Frame(main_frame, bg=c.DARK_BG)
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))

        # Checkbox
        self.show_var = BooleanVar(value=self.app_state.config.get('show_feedback_on_paste', True))
        chk = ttk.Checkbutton(bottom_frame, text="Show this window automatically on paste", variable=self.show_var, style='Dark.TCheckbutton', command=self._save_setting)
        chk.pack(side="left")

        if self.on_apply:
            apply_btn = RoundedButton(bottom_frame, text="Apply Changes", command=self._handle_apply, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=130, height=30, cursor="hand2")
            apply_btn.pack(side="right")

            refuse_btn = RoundedButton(bottom_frame, text="Refuse Update", command=self._handle_refuse, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=120, height=30, cursor="hand2")
            refuse_btn.pack(side="right", padx=(0, 10))
        else:
            ok_button = RoundedButton(bottom_frame, text="OK", command=self.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
            ok_button.pack(side="right")

        self.bind("<Escape>", lambda e: self.destroy() if not self.on_apply else self._handle_refuse())
        self.protocol("WM_DELETE_WINDOW", self._handle_refuse if self.on_apply else self.destroy)

        self.geometry("900x750")
        self.minsize(600, 500)
        position_window(self)

        self.deiconify()
        self.wait_window(self)

    def _add_tab(self, title, markdown_text):
        frame = Frame(self.notebook, bg=c.DARK_BG)
        self.notebook.add(frame, text=title)
        renderer = MarkdownRenderer(frame, base_font_size=11, on_zoom=self._adjust_font_size)
        renderer.pack(fill="both", expand=True)
        renderer.set_markdown(markdown_text.strip())
        self.renderers.append(renderer)

    def _adjust_font_size(self, delta):
        if not self.renderers: return
        new_size = self.renderers[0].base_font_size + delta
        new_size = max(8, min(new_size, 40))
        for r in self.renderers:
            r.set_font_size(new_size)

    def _save_setting(self):
        self.app_state.config['show_feedback_on_paste'] = self.show_var.get()
        save_config(self.app_state.config)

    def _handle_apply(self):
        if self.on_apply:
            self.on_apply()
        self.destroy()

    def _handle_refuse(self):
        if self.on_refuse:
            self.on_refuse()
        self.destroy()