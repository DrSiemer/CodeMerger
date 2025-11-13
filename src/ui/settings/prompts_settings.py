import tkinter as tk
from tkinter import Frame, Label
from .collapsible_section import CollapsibleTextSection
from ... import constants as c

class PromptsSettingsFrame(Frame):
    def __init__(self, parent, config, on_toggle, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)

        self._create_widgets(config, on_toggle)

    def _create_widgets(self, config, on_toggle):
        Label(self, text="Prompts", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15))

        self.copy_merged_prompt = CollapsibleTextSection(
            container, '\"Copy Code Only\" Prompt',
            config.get('copy_merged_prompt', ''), c.DEFAULT_COPY_MERGED_PROMPT,
            on_toggle_callback=on_toggle
        )
        self.copy_merged_prompt.pack(fill='x', expand=True, pady=(5, 0))

        self.default_intro = CollapsibleTextSection(
            container, 'Default Intro Instructions',
            config.get('default_intro_prompt', ''), c.DEFAULT_INTRO_PROMPT,
            on_toggle_callback=on_toggle
        )
        self.default_intro.pack(fill='x', expand=True, pady=(5, 0))

        self.default_outro = CollapsibleTextSection(
            container, 'Default Outro Instructions',
            config.get('default_outro_prompt', ''), c.DEFAULT_OUTRO_PROMPT,
            on_toggle_callback=on_toggle
        )
        self.default_outro.pack(fill='x', expand=True, pady=(5, 0))

    def get_values(self):
        return {
            'copy_merged_prompt': self.copy_merged_prompt.get_text(),
            'default_intro_prompt': self.default_intro.get_text(),
            'default_outro_prompt': self.default_outro.get_text(),
        }