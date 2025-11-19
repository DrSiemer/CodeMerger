import tkinter as tk
from ... import constants as c
from PIL import Image, ImageDraw, ImageTk

class SwitchButton(tk.Canvas):
    """
    A custom, animated, anti-aliased toggle switch widget for tkinter.
    """
    def __init__(self, parent, command=None, width=50, height=26, initial_state=False, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent.cget('bg'), highlightthickness=0, **kwargs)
        self.command = command
        self.is_on = initial_state
        self.width = width
        self.height = height
        self.radius = height / 2
        self.padding = 2

        self.knob_radius = (self.height / 2) - self.padding
        self.knob_x = self.padding if not self.is_on else self.width - self.height + self.padding

        self.bind("<Button-1>", self._on_click)
        # To prevent garbage collection
        self._image_ref = None
        self._draw()

    def _draw(self):
        scale = c.ANTIALIASING_SCALE_FACTOR
        scaled_width = self.width * scale
        scaled_height = self.height * scale
        scaled_radius = self.radius * scale
        scaled_padding = self.padding * scale
        scaled_knob_x = self.knob_x * scale

        img = Image.new('RGBA', (int(scaled_width), int(scaled_height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Track
        track_color = c.BTN_BLUE if self.is_on else c.TEXT_INPUT_BG
        track_coords = (scaled_padding, scaled_padding, scaled_width - scaled_padding, scaled_height - scaled_padding)
        draw.rounded_rectangle(track_coords, radius=scaled_radius-scaled_padding, fill=track_color)

        # Knob
        knob_color = "#FFFFFF"
        knob_coords = (
            scaled_knob_x,
            scaled_padding,
            scaled_knob_x + (scaled_height - (2 * scaled_padding)),
            scaled_height - scaled_padding
        )
        draw.ellipse(knob_coords, fill=knob_color)

        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        self._image_ref = ImageTk.PhotoImage(img)
        self.delete("all")
        self.create_image(0, 0, anchor='nw', image=self._image_ref)

    def _on_click(self, event=None):
        self.is_on = not self.is_on
        self._animate_switch()
        if self.command:
            self.command(self.is_on)

    def _animate_switch(self):
        target_x = self.width - self.height + self.padding if self.is_on else self.padding
        self._animate_step(target_x, 10)

    def _animate_step(self, target_x, steps):
        current_pos = self.knob_x
        distance = target_x - current_pos
        if abs(distance) < 1 or steps <= 0:
            self.knob_x = target_x
            self._draw()
            return

        self.knob_x += distance / steps
        self._draw()
        self.after(10, self._animate_step, target_x, steps - 1)

    def get_state(self):
        return self.is_on