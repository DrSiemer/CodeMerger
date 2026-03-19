import os
import re
from tkinter import Toplevel, Frame, Label, messagebox
from .. import constants as c
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_text import ScrollableText
from ..core import change_applier
from .window_utils import position_window
from .custom_error_dialog import CustomErrorDialog
from .info_manager import attach_info_mode
from .assets import assets

class PasteChangesDialog(Toplevel):
    def __init__(self, parent, project_base_dir, status_var, initial_content=None):
        super().__init__(parent)
        self.parent = parent
        self.base_dir = project_base_dir
        self.status_var = status_var
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title("Paste and Apply File Changes")
        self.iconbitmap(ICON_PATH)
        self.result = None

        self.configure(bg=c.DARK_BG)

        # --- Dynamic Geometry for Boot ---
        initial_w, initial_h = 600, 500
        if self.parent.app_state.info_mode_active:
            initial_h += c.INFO_PANEL_HEIGHT

        self.geometry(f"{initial_w}x{initial_h}")
        self.minsize(500, 400)

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        Label(
            main_frame,
            text="Paste the markdown from the language model below.",
            wraplength=550, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR
        ).grid(row=0, column=0, pady=(0, 10), sticky='w')

        self.text_widget = ScrollableText(
            main_frame, height=15, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL
        )
        self.text_widget.grid(row=1, column=0, sticky='nsew', pady=5)

        if initial_content:
            self.text_widget.insert('1.0', initial_content)

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=2, column=0, pady=(15, 0), sticky='ew')
        button_frame.grid_columnconfigure(1, weight=1)

        # Info Toggle: Managed by InfoManager.place
        self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")

        action_btns_frame = Frame(button_frame, bg=c.DARK_BG)
        action_btns_frame.grid(row=0, column=1, sticky='e')

        ok_button = RoundedButton(
            action_btns_frame, text="Apply Changes", command=self.on_apply,
            bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL,
            width=140, height=30, cursor='hand2'
        )
        ok_button.pack(side='right')

        cancel_button = RoundedButton(
            action_btns_frame, text="Cancel", command=self.on_cancel,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL,
            width=90, height=30, cursor='hand2'
        )
        cancel_button.pack(side='right', padx=(0, 10))

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.bind("<Escape>", self.on_cancel)

        # --- Info Mode Integration ---
        self.info_mgr = attach_info_mode(self, self.parent.app_state, manager_type='pack', toggle_btn=self.info_toggle_btn)
        self.info_mgr.register(self.text_widget, "paste_text")
        self.info_mgr.register(ok_button, "paste_apply")
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")

        position_window(self)
        self.deiconify()
        self.lift()
        self.focus_force()
        self.text_widget.text_widget.focus_set()
        self.wait_window(self)

    def on_apply(self):
        markdown_text = self.text_widget.get('1.0', 'end-1c')
        if not markdown_text.strip():
            messagebox.showwarning("Input Error", "The text input cannot be empty.", parent=self)
            return

        plan = change_applier.parse_and_plan_changes(self.base_dir, markdown_text)

        logical_app = self.parent
        while logical_app and not hasattr(logical_app, 'action_handlers'):
            logical_app = logical_app.master

        if logical_app:
            logical_app.action_handlers._handle_parsed_plan(plan, self.base_dir, dialog_to_close=self)

    def on_cancel(self, event=None):
        self.destroy()