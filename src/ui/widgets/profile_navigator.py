import tkinter as tk
from tkinter import Frame, Label, font as tkFont
from ... import constants as c

class ProfileNavigator(Frame):
    """
    A custom widget for navigating between project profiles using Previous/Next buttons.
    """
    def __init__(self, parent, on_change_callback, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.on_change = on_change_callback

        self.profiles = []
        self.current_index = -1
        self.font = tkFont.Font(family=c.FONT_NORMAL[0], size=c.FONT_NORMAL[1])

        # --- Widgets ---
        button_font = (c.FONT_FAMILY_PRIMARY, 16, 'bold')
        self.prev_button = tk.Button(
            self, text="<", font=button_font,
            bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR,
            activebackground=c.DARK_BG, activeforeground=c.BTN_BLUE,
            command=self._on_prev, relief='flat', bd=0, cursor='hand2'
        )

        self.label_container = Frame(self, bg=c.DARK_BG)
        self.label_container.pack_propagate(False)

        self.profile_label = Label(
            self.label_container, text="", font=self.font,
            bg=c.DARK_BG, fg=c.TEXT_COLOR,
            anchor='w'
        )

        self.next_button = tk.Button(
            self, text=">", font=button_font,
            bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR,
            activebackground=c.DARK_BG, activeforeground=c.BTN_BLUE,
            command=self._on_next, relief='flat', bd=0, cursor='hand2'
        )

        self.prev_button.pack(side='left', padx=(0, 0))
        self.label_container.pack(side='left', fill='y')
        self.profile_label.pack(expand=True, fill='both', padx=(10, 0))
        self.next_button.pack(side='left', padx=(0, 0))

    def set_profiles(self, profile_list, active_profile_name):
        """
        Sets the list of available profiles, calculates required width, and sets the active profile.
        """
        self.profiles = profile_list
        try:
            self.current_index = self.profiles.index(active_profile_name)
        except ValueError:
            self.current_index = 0 if self.profiles else -1

        # Calculate and set a consistent width for the label area.
        if self.profiles:
            max_w = 0
            for name in self.profiles:
                max_w = max(max_w, self.font.measure(name))

            MIN_WIDTH = 80
            MAX_WIDTH = 120

            final_width = max(MIN_WIDTH, min(max_w + 10, MAX_WIDTH))
            self.label_container.config(width=final_width)
        else:
            self.label_container.config(width=0)

        self._update_display()

    def _update_display(self):
        """
        Updates the displayed profile name and button visibility.
        """
        if self.current_index != -1 and self.profiles:
            self.profile_label.config(text=self.profiles[self.current_index])
        else:
            self.profile_label.config(text="")

        self.prev_button.config(state='normal')
        self.next_button.config(state='normal')

    def _on_prev(self):
        """Cycles to the previous profile."""
        if not self.profiles: return
        self.current_index = (self.current_index - 1) % len(self.profiles)
        new_profile = self.profiles[self.current_index]
        self.profile_label.config(text=new_profile)
        self.on_change(new_profile)

    def _on_next(self):
        """Cycles to the next profile."""
        if not self.profiles: return
        self.current_index = (self.current_index + 1) % len(self.profiles)
        new_profile = self.profiles[self.current_index]
        self.profile_label.config(text=new_profile)
        self.on_change(new_profile)