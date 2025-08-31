import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os
import sys

# --- Robust Font Finding Logic ---
WINDOWS_FONT_MAP = {
    "segoe ui": ["segoeui.ttf", "seguisb.ttf", "seguili.ttf"],
    "arial": ["arial.ttf", "arialbd.ttf"],
}

def get_pil_font(font_tuple):
    """Tries to find and load a font file for Pillow, with fallbacks."""
    font_family, font_size = font_tuple

    # On Windows, search the system Fonts directory
    if sys.platform == "win32":
        font_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts")
        normalized_family = font_family.lower()

        if normalized_family in WINDOWS_FONT_MAP:
            for font_file in WINDOWS_FONT_MAP[normalized_family]:
                path = os.path.join(font_dir, font_file)
                if os.path.exists(path):
                    try:
                        return ImageFont.truetype(path, font_size)
                    except IOError:
                        continue # Try the next variant

    # Generic fallback for other systems or if the Windows search fails
    try:
        return ImageFont.truetype(f"{font_family.lower()}.ttf", font_size)
    except IOError:
        return ImageFont.load_default()


class RoundedButton(tk.Canvas):
    """A custom anti-aliased rounded button widget for tkinter."""
    def __init__(self, parent, text, command, font=None, bg='#CCCCCC', fg='#000000', width=None, height=35, radius=6):
        self.tk_font_tuple = font if font else tkFont.nametofont("TkDefaultFont")

        # Use the robust font loader
        self.pil_font = get_pil_font(self.tk_font_tuple)

        # Calculate width using the actual Pillow font object
        if width is None:
            text_box = self.pil_font.getbbox(text)
            text_width = text_box[2] - text_box[0]
            self.width = text_width + 40 # Add horizontal padding
        else:
            self.width = width

        self.height = height
        self.radius = radius
        self.command = command
        self.is_enabled = True

        super().__init__(parent, width=self.width, height=self.height, bg=parent.cget('bg'), bd=0, highlightthickness=0)

        self.text = text
        self.original_bg_color = bg
        self.original_fg_color = fg

        self.fg_color = self.original_fg_color
        self.hover_color = self._adjust_brightness(self.original_bg_color, -0.1)
        self.click_color = self._adjust_brightness(self.original_bg_color, -0.2)
        self.disabled_color = '#9E9E9E'

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

        self._draw(self.original_bg_color)

    def _adjust_brightness(self, hex_color, factor):
        """Adjusts the brightness of a hex color."""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]

        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * (1 + factor))))
        g = max(0, min(255, int(g * (1 + factor))))
        b = max(0, min(255, int(b * (1 + factor))))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, color):
        """Draws the anti-aliased button shape and text using Pillow."""
        self.delete("all")

        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle((0, 0, self.width, self.height), radius=self.radius, fill=color)

        text_bbox = self.pil_font.getbbox(self.text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = (self.width - text_width) / 2
        text_y = (self.height - text_height) / 2 - text_bbox[1]

        draw.text((text_x, text_y), self.text, font=self.pil_font, fill=self.fg_color)

        self._button_image = ImageTk.PhotoImage(img)
        self.create_image(0, 0, anchor='nw', image=self._button_image)

    def _on_enter(self, event):
        if self.is_enabled:
            self._draw(self.hover_color)

    def _on_leave(self, event):
        if self.is_enabled:
            self._draw(self.original_bg_color)

    def _on_click(self, event):
        if self.is_enabled:
            self._draw(self.click_color)

    def _on_release(self, event):
        if self.is_enabled:
            self._draw(self.hover_color)
            if self.command:
                self.command()

    def set_state(self, state):
        """Sets the state of the button ('normal' or 'disabled')."""
        if state == 'disabled':
            self.is_enabled = False
            self.fg_color = '#757575'
            self._draw(self.disabled_color)
        else: # 'normal'
            self.is_enabled = True
            self.fg_color = self.original_fg_color
            self._draw(self.original_bg_color)

    def config(self, **kwargs):
        """Allows configuration of button properties like a standard widget."""
        if 'state' in kwargs:
            self.set_state(kwargs['state'])
        super().config(**kwargs)