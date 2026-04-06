import tkinter as tk
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..tooltip import ToolTip

class StarterUIBuilder:
    def __init__(self, dialog):
        self.dialog = dialog

    def build_ui(self):
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(1, weight=1)

        header_frame = tk.Frame(self.dialog, bg=c.DARK_BG, padx=10, pady=10)
        header_frame.grid(row=0, column=0, sticky="ew")

        self.dialog.tabs_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        self.dialog.tabs_frame.pack(side="left", fill='x', expand=True)

        right_header_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        right_header_frame.pack(side="right")

        if self.dialog.app.assets.trash_icon_image:
             self.dialog.btn_clear = RoundedButton(
                right_header_frame, command=self.dialog.actions.clear_session_data,
                image=self.dialog.app.assets.trash_icon_image,
                bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, width=32, height=32, radius=6, cursor="hand2"
            )
             self.dialog.btn_clear.pack(side="right", padx=(0, 0))
             ToolTip(self.dialog.btn_clear, "Clear all starter progress and start fresh", delay=500)

        self.dialog.btn_save = RoundedButton(
            right_header_frame, text="Save Config", command=self.dialog.actions.save_config,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=32, radius=6, cursor="hand2"
        )
        self.dialog.btn_save.pack(side="right", padx=(0, 10))
        ToolTip(self.dialog.btn_save, "Save current project configuration to a file", delay=500)

        self.dialog.btn_load = RoundedButton(
            right_header_frame, text="Load Config", command=self.dialog.actions.load_config,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=32, radius=6, cursor="hand2"
        )
        self.dialog.btn_load.pack(side="right", padx=(0, 10))
        ToolTip(self.dialog.btn_load, "Load a previously saved project configuration file", delay=500)

        self.dialog.content_frame = tk.Frame(self.dialog, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        self.dialog.content_frame.grid(row=1, column=0, sticky="nsew", padx=10)

        self.dialog.nav_frame = tk.Frame(self.dialog, bg=c.DARK_BG, padx=10, pady=10)
        self.dialog.nav_frame.grid(row=2, column=0, sticky="ew")

        self.dialog.prev_button = RoundedButton(self.dialog.nav_frame, text="< Prev", command=self.dialog.navigation.go_to_prev_step, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        ToolTip(self.dialog.prev_button, "Go back to the previous step", delay=500)

        self.dialog.start_over_button = RoundedButton(self.dialog.nav_frame, text="Reset step", command=self.dialog.actions.start_over, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        ToolTip(self.dialog.start_over_button, "Clear the inputs for the current step", delay=500)

        self.dialog.next_button = RoundedButton(self.dialog.nav_frame, text="Next >", command=self.dialog.navigation.go_to_next_step, height=30, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.dialog.next_tooltip = ToolTip(self.dialog.next_button, "Validate current inputs and proceed", delay=500)

    def refresh_tabs(self):
        if not self.dialog.tabs_frame: return
        for t in self.dialog.tabs: t.destroy()
        self.dialog.tabs = []
        active_steps = self.dialog.navigation.get_active_steps()
        for i, step_id in enumerate(active_steps):
            name = self.dialog.steps_map[step_id]
            tab = RoundedButton(self.dialog.tabs_frame, command=lambda s=step_id: self.dialog.navigation.go_to_step(s), text=f"{i+1}. {name}", font=c.FONT_NORMAL, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, height=32, radius=6, hollow=True, cursor="hand2")
            tab.pack(side="left", padx=(0, 5), fill='x', expand=True)
            ToolTip(tab, f"Jump to {name} step", delay=500)
            self.dialog.tabs.append(tab)
        self.update_tab_styles()

    def update_tab_styles(self):
        active_steps = self.dialog.navigation.get_active_steps()
        for i, tab in enumerate(self.dialog.tabs):
            step_id = active_steps[i]
            is_active = (step_id == self.dialog.starter_state.current_step)
            is_accessible = (step_id <= self.dialog.starter_state.max_accessible_step) or (step_id == 2)
            tab.set_state('normal' if is_accessible else 'disabled')
            tab.config(hollow=(not is_active), bg=(c.BTN_BLUE if is_active else c.BTN_GRAY_BG), fg=(c.BTN_BLUE_TEXT if is_active else (c.TEXT_COLOR if is_accessible else c.BTN_GRAY_TEXT)))