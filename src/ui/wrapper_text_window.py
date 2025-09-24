import os
from tkinter import Toplevel, Frame, Label, Text, Scrollbar
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.utils import load_config
from .tooltip import ToolTip
from .window_utils import position_window, save_window_geometry
from .assets import assets

class WrapperTextWindow(Toplevel):
    def __init__(self, parent, project_config, status_var, on_close_callback=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.project_config = project_config
        self.status_var = status_var
        self.on_close_callback = on_close_callback

        # --- Window Setup ---
        self.title("Set Wrapper Text")
        self.iconbitmap(ICON_PATH)
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

        # --- UI Layout ---
        main_frame = Frame(self, padx=15, pady=15, bg=c.DARK_BG)
        main_frame.pack(fill='both', expand=True)

        # --- Action Buttons (pack to bottom first to ensure visibility) ---
        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))

        # --- Place "Load Defaults" icon on the left side of the button bar ---
        config = load_config()
        default_intro = config.get('default_intro_prompt', '').strip()
        default_outro = config.get('default_outro_prompt', '').strip()

        if assets.defaults_icon and (default_intro or default_outro):
            self.defaults_button = Label(button_frame, image=assets.defaults_icon, bg=c.DARK_BG, cursor="hand2")
            self.defaults_button.image = assets.defaults_icon
            self.defaults_button.pack(side='left', padx=(0, 10), anchor='w')
            self.defaults_button.bind("<Button-1>", self.populate_from_defaults)
            ToolTip(self.defaults_button, "Populate fields with default prompts from Settings")

        # --- Save Button on the right ---
        self.save_button = RoundedButton(
            button_frame,
            text="Save and Close",
            command=self.save_and_close,
            bg=c.BTN_BLUE,
            fg=c.BTN_BLUE_TEXT,
            font=c.FONT_BUTTON,
            cursor='hand2'
        )
        self.save_button.pack(side='right')

        # --- Container for text fields that will use grid for equal sizing ---
        fields_container = Frame(main_frame, bg=c.DARK_BG)
        fields_container.pack(fill='both', expand=True)

        # Configure the grid to give equal vertical space to the two text areas
        fields_container.rowconfigure(0, weight=1)
        fields_container.rowconfigure(1, weight=1)
        fields_container.columnconfigure(0, weight=1)

        # --- Intro Text Section ---
        intro_frame = Frame(fields_container, bg=c.DARK_BG)
        intro_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        intro_label_frame = Frame(intro_frame, bg=c.DARK_BG)
        intro_label_frame.pack(anchor='w', pady=(0, 5))
        Label(intro_label_frame, text="Intro Text", font=c.FONT_WRAPPER_TITLE, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')
        Label(intro_label_frame, text="(prepended to the final output):", font=c.FONT_WRAPPER_SUBTITLE, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='left', padx=(4,0))
        intro_text_frame = Frame(intro_frame, bd=1, relief='sunken')
        intro_text_frame.pack(fill='both', expand=True)
        self.intro_text = Text(intro_text_frame, wrap='word', undo=True, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', bd=0, highlightthickness=0)
        intro_scroll = Scrollbar(intro_text_frame, command=self.intro_text.yview)
        self.intro_text.config(yscrollcommand=intro_scroll.set)
        intro_scroll.pack(side='right', fill='y')
        self.intro_text.pack(side='left', fill='both', expand=True)

        # --- Outro Text Section ---
        outro_frame = Frame(fields_container, bg=c.DARK_BG)
        outro_frame.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        outro_label_frame = Frame(outro_frame, bg=c.DARK_BG)
        outro_label_frame.pack(anchor='w', pady=(0, 5))
        Label(outro_label_frame, text="Outro Text", font=c.FONT_WRAPPER_TITLE, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')
        Label(outro_label_frame, text="(appended to the final output):", font=c.FONT_WRAPPER_SUBTITLE, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='left', padx=(4,0))
        outro_text_frame = Frame(outro_frame, bd=1, relief='sunken')
        outro_text_frame.pack(fill='both', expand=True)
        self.outro_text = Text(outro_text_frame, wrap='word', undo=True, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', bd=0, highlightthickness=0)
        outro_scroll = Scrollbar(outro_text_frame, command=self.outro_text.yview)
        self.outro_text.config(yscrollcommand=outro_scroll.set)
        outro_scroll.pack(side='right', fill='y')
        self.outro_text.pack(side='left', fill='both', expand=True)

        # --- Populate Text Fields ---
        self.intro_text.insert('1.0', self.project_config.intro_text)
        self.outro_text.insert('1.0', self.project_config.outro_text)

        self.protocol("WM_DELETE_WINDOW", self._close_and_save_geometry)
        self.bind('<Escape>', lambda e: self._close_and_save_geometry())

        self._position_window()
        self.deiconify()

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def populate_from_defaults(self, event=None):
        config = load_config()
        default_intro = config.get('default_intro_prompt', '')
        default_outro = config.get('default_outro_prompt', '')

        self.intro_text.delete('1.0', 'end')
        self.intro_text.insert('1.0', default_intro)

        self.outro_text.delete('1.0', 'end')
        self.outro_text.insert('1.0', default_outro)

    def save_and_close(self):
        """Saves the intro/outro text to the .allcode file and closes the window"""
        self.project_config.intro_text = self.intro_text.get('1.0', 'end-1c')
        self.project_config.outro_text = self.outro_text.get('1.0', 'end-1c')

        try:
            self.project_config.save()
            self.status_var.set("Wrapper text saved successfully.")
        except IOError as e:
            self.status_var.set(f"Error saving wrapper text: {e}")

        if self.on_close_callback:
            self.on_close_callback()

        self._close_and_save_geometry()