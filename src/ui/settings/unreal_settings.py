import tkinter as tk
from tkinter import Frame, Label, ttk, Entry
from ... import constants as c

class UnrealSettingsFrame(Frame):
    def __init__(self, parent, vars, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.unreal_integration_enabled = vars['unreal_integration_enabled']
        self.unreal_port = vars['unreal_port']

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="Unreal Engine Integration", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15), padx=(25, 0))

        # Enable/Disable
        ttk.Checkbutton(container, text="Enable Remote Connection (Requires UE Python Plugin)", variable=self.unreal_integration_enabled, style='Dark.TCheckbutton', command=self._toggle_port_entry).pack(anchor='w')

        # Port Configuration
        port_frame = Frame(container, bg=c.DARK_BG)
        port_frame.pack(fill='x', expand=True, pady=(10, 0))
        
        self.port_label = Label(port_frame, text="Multicast Port:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.port_label.pack(side='left', padx=(0, 10))
        
        vcmd = (self.register(self._validate_integer), '%P')
        self.port_entry = Entry(port_frame, textvariable=self.unreal_port, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd)
        self.port_entry.pack(side='left')
        
        Label(port_frame, text="(Default: 6766)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='left', padx=(10, 0))

        self._toggle_port_entry()

    def _toggle_port_entry(self):
        state = 'normal' if self.unreal_integration_enabled.get() else 'disabled'
        self.port_label.config(state=state)
        self.port_entry.config(state=state)

    def _validate_integer(self, value_if_allowed):
        if value_if_allowed == "": return True
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False