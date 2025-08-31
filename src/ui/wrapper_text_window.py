import os
import json
from tkinter import Toplevel, Frame, Label, Button, Text, Scrollbar
from ..core.paths import ICON_PATH

class WrapperTextWindow(Toplevel):
    def __init__(self, parent, project_config, status_var, on_close_callback=None):
        super().__init__(parent)
        self.project_config = project_config
        self.status_var = status_var
        self.on_close_callback = on_close_callback

        # --- Style Definitions ---
        dark_bg = '#2E2E2E'
        text_color = '#FFFFFF'
        btn_blue = '#0078D4'
        text_bg = '#3C3C3C'

        # --- Window Setup ---
        self.title("Set Wrapper Text")
        self.iconbitmap(ICON_PATH)
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()
        self.configure(bg=dark_bg)

        # --- UI Layout ---
        main_frame = Frame(self, padx=15, pady=15, bg=dark_bg)
        main_frame.pack(fill='both', expand=True)

        # --- Action Buttons (pack to bottom first to ensure visibility) ---
        button_frame = Frame(main_frame, bg=dark_bg)
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        self.save_button = Button(button_frame, text="Save and Close", command=self.save_and_close, bg=btn_blue, fg=text_color, relief='flat', padx=10)
        self.save_button.pack(side='right')

        # --- Container for text fields that will use grid for equal sizing ---
        fields_container = Frame(main_frame, bg=dark_bg)
        fields_container.pack(fill='both', expand=True)

        # Configure the grid to give equal vertical space to the two text areas
        fields_container.rowconfigure(0, weight=1)
        fields_container.rowconfigure(1, weight=1)
        fields_container.columnconfigure(0, weight=1)

        # --- Intro Text Section ---
        intro_frame = Frame(fields_container, bg=dark_bg)
        intro_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        Label(intro_frame, text="Intro Text (prepended to the final output):", font=('Helvetica', 10, 'bold'), bg=dark_bg, fg=text_color).pack(anchor='w', pady=(0, 5))
        intro_text_frame = Frame(intro_frame, bd=1, relief='sunken')
        intro_text_frame.pack(fill='both', expand=True)
        self.intro_text = Text(intro_text_frame, wrap='word', undo=True, height=5, bg=text_bg, fg=text_color, insertbackground=text_color, relief='flat')
        intro_scroll = Scrollbar(intro_text_frame, command=self.intro_text.yview)
        self.intro_text.config(yscrollcommand=intro_scroll.set)
        intro_scroll.pack(side='right', fill='y')
        self.intro_text.pack(side='left', fill='both', expand=True)

        # --- Outro Text Section ---
        outro_frame = Frame(fields_container, bg=dark_bg)
        outro_frame.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        Label(outro_frame, text="Outro Text (appended to the final output):", font=('Helvetica', 10, 'bold'), bg=dark_bg, fg=text_color).pack(anchor='w', pady=(0, 5))
        outro_text_frame = Frame(outro_frame, bd=1, relief='sunken')
        outro_text_frame.pack(fill='both', expand=True)
        self.outro_text = Text(outro_text_frame, wrap='word', undo=True, height=5, bg=text_bg, fg=text_color, insertbackground=text_color, relief='flat')
        outro_scroll = Scrollbar(outro_text_frame, command=self.outro_text.yview)
        self.outro_text.config(yscrollcommand=outro_scroll.set)
        outro_scroll.pack(side='right', fill='y')
        self.outro_text.pack(side='left', fill='both', expand=True)

        # --- Populate Text Fields ---
        self.intro_text.insert('1.0', self.project_config.intro_text)
        self.outro_text.insert('1.0', self.project_config.outro_text)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def save_and_close(self):
        """Saves the intro/outro text to the .allcode file and closes the window"""
        self.project_config.intro_text = self.intro_text.get('1.0', 'end-1c').strip()
        self.project_config.outro_text = self.outro_text.get('1.0', 'end-1c').strip()

        try:
            self.project_config.save()
            self.status_var.set("Wrapper text saved successfully.")
        except IOError as e:
            self.status_var.set(f"Error saving wrapper text: {e}")

        if self.on_close_callback:
            self.on_close_callback()

        self.destroy()