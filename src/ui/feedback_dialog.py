import tkinter as tk
import os
from tkinter import Frame, Label, ttk, BooleanVar, messagebox
from PIL import Image, ImageDraw, ImageTk
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

        # Generate vertical accent bars for all tabs
        self._gray_accent = self._create_vertical_accent(c.TEXT_SUBTLE_COLOR)  # Intro
        self._cyan_accent = self._create_vertical_accent("#00BCD4")           # Answers
        self._blue_accent = self._create_vertical_accent(c.BTN_BLUE)          # Changes
        self._red_accent = self._create_vertical_accent(c.WARN)               # Delete
        self._green_accent = self._create_vertical_accent(c.BTN_GREEN)        # Verification

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        title_text = "Review Proposed Update" if on_apply else "Review Last Update"
        Label(main_frame, text=title_text, font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        self.renderers =[]

        self.tab_indices = {}
        current_idx = 0

        # Preferred order: Intro, Answers, Changes, Delete, Verification
        if plan.get('intro'):
            self._add_tab("Intro", plan.get('intro'), icon=self._gray_accent)
            self.tab_indices['intro'] = current_idx
            current_idx += 1

        if plan.get('answers'):
            self._add_tab("Answers", plan.get('answers'), icon=self._cyan_accent)
            self.tab_indices['answers'] = current_idx
            current_idx += 1

        if plan.get('changes'):
            self._add_tab("Changes", plan.get('changes'), icon=self._blue_accent)
            self.tab_indices['changes'] = current_idx
            current_idx += 1

        if plan.get('delete'):
            self._add_tab("Delete", plan.get('delete'), icon=self._red_accent)
            self.tab_indices['delete'] = current_idx
            current_idx += 1

        if plan.get('verification'):
            self._add_tab("Verification", plan.get('verification'), icon=self._green_accent)
            self.tab_indices['verification'] = current_idx
            current_idx += 1

        # Tab Selection Priority: answers, delete, verification
        if 'answers' in self.tab_indices:
            self.notebook.select(self.tab_indices['answers'])
        elif 'delete' in self.tab_indices:
            self.notebook.select(self.tab_indices['delete'])
        elif 'verification' in self.tab_indices:
            self.notebook.select(self.tab_indices['verification'])
        elif current_idx > 0:
            self.notebook.select(0)

        self.bottom_frame = Frame(main_frame, bg=c.DARK_BG)
        self.bottom_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))

        # Checkbox
        self.show_var = BooleanVar(value=self.app_state.config.get('show_feedback_on_paste', True))
        chk = ttk.Checkbutton(self.bottom_frame, text="Show this window automatically on paste", variable=self.show_var, style='Dark.TCheckbutton', command=self._save_setting)
        chk.pack(side="left")

        if self.on_apply:
            self.apply_btn = RoundedButton(self.bottom_frame, text="Apply Changes", command=self._handle_apply, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=130, height=30, cursor="hand2")
            self.apply_btn.pack(side="right")

            self.cancel_btn = RoundedButton(self.bottom_frame, text="Cancel", command=self._handle_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
            self.cancel_btn.pack(side="right", padx=(0, 10))
        else:
            self.ok_button = RoundedButton(self.bottom_frame, text="OK", command=self.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
            self.ok_button.pack(side="right")

        self.bind("<Escape>", lambda e: self.destroy() if not self.on_apply else self._on_close_request())
        self.protocol("WM_DELETE_WINDOW", self._on_close_request if self.on_apply else self.destroy)

        self.geometry("900x750")
        self.minsize(600, 500)
        position_window(self)

        self.deiconify()
        self.wait_window(self)

    def _create_vertical_accent(self, hex_color):
        """Creates a sharpened vertical bar PhotoImage shifted down 1px."""
        size = (14, 22)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 1, 3, 20], radius=1, fill=hex_color)
        return ImageTk.PhotoImage(img)

    def _add_tab(self, title, markdown_text, icon=None):
        frame = Frame(self.notebook, bg=c.DARK_BG)
        if icon:
            self.notebook.add(frame, text=title, image=icon, compound="left")
        else:
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
        """Applies the changes. If verification steps exist, remains open to show them."""
        if self.on_apply:
            self.on_apply()
            # Clear callbacks once executed to indicate the update is no longer pending.
            # This suppresses the "Discard Update?" warning on window close.
            self.on_apply = None
            self.on_refuse = None

        if 'verification' in self.tab_indices:
            # Changes applied, so hide the decision buttons
            self.apply_btn.pack_forget()
            self.cancel_btn.pack_forget()

            # Add a final Close/OK button to exit the window after verification is read
            self.ok_button = RoundedButton(
                self.bottom_frame, text="Close", command=self.destroy,
                bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL,
                width=100, height=30, cursor="hand2"
            )
            self.ok_button.pack(side="right")

            # Navigate to verification steps automatically
            self.notebook.select(self.tab_indices['verification'])
        else:
            self.destroy()

    def _handle_cancel(self):
        """Discards the update immediately. Used by the explicit 'Cancel' button."""
        if self.on_refuse:
            self.on_refuse()
        self.destroy()

    def _on_close_request(self):
        """Warns the user before discarding the update if the window is closed manually."""
        if self.on_apply:
            if not messagebox.askyesno(
                "Discard Update?",
                "You are currently reviewing a proposed update. Closing this window will discard the changes and they will not be applied to your project files.\n\nAre you sure you want to discard this update?",
                parent=self
            ):
                return

        self._handle_cancel()