import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageDraw, ImageTk
from ... import constants as c
from ..font_utils import get_pil_font

class RoundedButton(tk.Canvas):
    """A custom anti-aliased rounded button widget for tkinter."""
    def __init__(self, parent, command, text=None, image=None, font=None, bg='#CCCCCC', fg='#000000', width=None, height=30, radius=6, hollow=False, h_padding=None, cursor=None):
        if font:
            # If a tuple like ("Segoe UI", 12) is passed, use it directly
            self.tk_font_tuple = font
        else:
            # If font is None, use the default font from constants
            self.tk_font_tuple = c.FONT_DEFAULT
        self.hollow = hollow
        self.image = image # Store the Pillow image object
        # Use the robust font loader
        self.pil_font = get_pil_font(self.tk_font_tuple)
        # Calculate width if not provided
        if width is None:
            if text:
                padding = h_padding if h_padding is not None else 40
                text_box = self.pil_font.getbbox(text)
                text_width = text_box[2] - text_box[0]
                self.width = text_width + padding
            elif image:
                padding = h_padding if h_padding is not None else 20
                self.width = image.width + padding
            else:
                self.width = 40 # Default width if no content
        else:
            self.width = width
        self.height = height
        self.radius = radius
        self.command = command
        self.is_enabled = True
        # Increase the canvas size for hollow buttons to compensate for the border
        if self.hollow:
            self.width += 2
            self.height += 2
        super().__init__(parent, width=self.width, height=self.height, bg=parent.cget('bg'), bd=0, highlightthickness=0, cursor=cursor)
        self.text = text
        self.original_bg_color = bg
        self.original_fg_color = fg
        self.fg_color = self.original_fg_color
        if self.hollow:
            # For hollow buttons, the look is a specific fill with fg text
            self.base_color = c.TOP_BAR_BG # This is the main fill color
            self.hover_color = self._adjust_brightness(self.base_color, 0.2)
            self.click_color = self.base_color # Use base color for click to avoid flicker
            self.disabled_color = self.base_color
            self.disabled_text_color = '#757575'
        else:
            # For solid buttons, colors are based on the background
            self.base_color = self.original_bg_color
            self.hover_color = self._adjust_brightness(self.base_color, -0.1)
            self.click_color = self._adjust_brightness(self.base_color, -0.2)
            self.disabled_color = '#9E9E9E'
        self._last_draw_width = 0
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_resize)
        self._draw(self.base_color)

    def _on_resize(self, event=None):
        """
        Redraws the button if its allocated size has changed.
        This makes the button responsive to layout managers like grid with `sticky`.
        """
        if self.winfo_width() != self._last_draw_width:
            # Redraw with the correct color for the current state
            color = self.base_color if self.is_enabled else self.disabled_color
            self._draw(color)

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
        """Draws the anti-aliased button shape and text/image using Pillow with supersampling."""
        self.delete("all")
        # Use the actual current width of the canvas widget for drawing.
        # This makes the button fill the space allocated by the layout manager.
        draw_width = self.winfo_width()
        if draw_width <= 1: # On first draw, widget may not have a size yet
            draw_width = self.width
        self._last_draw_width = draw_width
        scale = 4  # Use 4x supersampling for smooth edges
        scaled_width = draw_width * scale
        scaled_height = self.height * scale
        scaled_radius = self.radius * scale
        # Create a high-resolution image to draw on
        img = Image.new('RGBA', (scaled_width, scaled_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        if self.hollow:
            border_color = self.disabled_text_color if not self.is_enabled else self.original_fg_color
            scaled_border_width = 1 * scale
            # Inset by half the border width to draw a clean border
            inset = scaled_border_width / 2
            draw.rounded_rectangle(
                (inset, inset, scaled_width - inset, scaled_height - inset),
                radius=scaled_radius,
                fill=color,
                outline=border_color,
                width=scaled_border_width
            )
            text_fill_color = self.disabled_text_color if not self.is_enabled else self.original_fg_color
        else:
            draw.rounded_rectangle((0, 0, scaled_width, scaled_height), radius=scaled_radius, fill=color)
            text_fill_color = self.fg_color
        # --- Draw Content: either text or an image ---
        if self.image:
            scaled_image = self.image.resize((self.image.width * scale, self.image.height * scale), Image.Resampling.LANCZOS)
            paste_x = (scaled_width - scaled_image.width) // 2
            paste_y = (scaled_height - scaled_image.height) // 2
            img.paste(scaled_image, (paste_x, paste_y), scaled_image)
        elif self.text:
            original_font_size = self.tk_font_tuple[1]
            scaled_font = get_pil_font((self.tk_font_tuple[0], original_font_size * scale))
            center_x = scaled_width / 2
            center_y = (scaled_height / 2) - (0.5 * scale)
            draw.text(
                (center_x, center_y),
                self.text,
                font=scaled_font,
                fill=text_fill_color,
                anchor="mm"
            )
        # Scale the high-resolution image down to the final size with a high-quality filter
        img = img.resize((draw_width, self.height), Image.Resampling.LANCZOS)
        self._button_image = ImageTk.PhotoImage(img)
        self.create_image(0, 0, anchor='nw', image=self._button_image)

    def _on_enter(self, event):
        if self.is_enabled:
            self._draw(self.hover_color)

    def _on_leave(self, event):
        if self.is_enabled:
            self._draw(self.base_color)

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
            if not self.hollow:
                self.fg_color = '#757575' # Special for solid disabled
            self._draw(self.disabled_color)
        else: # 'normal'
            self.is_enabled = True
            self.fg_color = self.original_fg_color # Reset text color
            self._draw(self.base_color)

    def config(self, **kwargs):
        """Allows configuration of button properties like a standard widget."""
        text_changed = 'text' in kwargs
        width_changed = 'width' in kwargs
        bg_changed = 'bg' in kwargs
        fg_changed = 'fg' in kwargs
        if text_changed:
            self.text = kwargs.pop('text')
        if width_changed:
            self.width = kwargs.pop('width')
            if self.hollow: self.width += 2 # Re-apply compensation if width is changed
            super().config(width=self.width)
        if bg_changed:
            self.original_bg_color = kwargs.pop('bg')
            if not self.hollow:
                self.base_color = self.original_bg_color
                self.hover_color = self._adjust_brightness(self.base_color, -0.1)
                self.click_color = self._adjust_brightness(self.base_color, -0.2)
        if fg_changed:
            self.original_fg_color = kwargs.pop('fg')
            self.fg_color = self.original_fg_color
        # The 'state' key is the primary driver of redraws
        if 'state' in kwargs:
            self.set_state(kwargs.pop('state'))
        # If any property changed that affects visuals, we need to force a redraw
        elif text_changed or width_changed or bg_changed or fg_changed:
            color = self.base_color if self.is_enabled else self.disabled_color
            self._draw(color)
        # Pass any remaining, non-handled kwargs to the parent canvas
        if kwargs:
            super().config(**kwargs)