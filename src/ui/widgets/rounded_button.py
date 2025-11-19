import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageDraw, ImageTk
from ... import constants as c
from ..font_utils import get_pil_font

class RoundedButton(tk.Canvas):
    """A custom anti-aliased rounded button widget for tkinter."""
    def __init__(self, parent, command, text=None, image=None, font=None, bg='#CCCCCC', fg='#000000', width=None, height=30, radius=6, hollow=False, h_padding=None, cursor=None, text_align='center'):
        # If a tuple like ("Segoe UI", 12) is passed, use it directly
        if font:
            self.tk_font_tuple = font
        # If font is None, use the default font from constants
        else:
            self.tk_font_tuple = c.FONT_DEFAULT
        self.hollow = hollow
        self.image = image
        self.text_align = text_align
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
                self.width = 40
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

        # For hollow buttons, the look is a specific fill with fg text
        if self.hollow:
            self.base_color = c.DARK_BG
            self.hover_color = self._adjust_brightness(self.base_color, 0.2)
            self.click_color = self.base_color
            self.disabled_color = self.base_color
            self.disabled_text_color = '#757575'
        # For solid buttons, colors are based on the background
        else:
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
        if self.winfo_width() != self._last_draw_width:
            color = self.base_color if self.is_enabled else self.disabled_color
            self._draw(color)

    def _adjust_brightness(self, hex_color, factor):
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * (1 + factor))))
        g = max(0, min(255, int(g * (1 + factor))))
        b = max(0, min(255, int(b * (1 + factor))))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, color):
        self.delete("all")
        draw_width = self.winfo_width()
        if draw_width <= 1:
            draw_width = self.width
        self._last_draw_width = draw_width
        scale = c.ANTIALIASING_SCALE_FACTOR
        scaled_width = draw_width * scale
        scaled_height = self.height * scale
        scaled_radius = self.radius * scale
        img = Image.new('RGBA', (int(scaled_width), int(scaled_height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if self.hollow:
            border_color = self.disabled_text_color if not self.is_enabled else self.original_fg_color
            scaled_border_width = 1 * scale
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

        if self.image:
            scaled_image = self.image.resize((self.image.width * scale, self.image.height * scale), Image.Resampling.LANCZOS)
            paste_x = (scaled_width - scaled_image.width) // 2
            paste_y = (scaled_height - scaled_image.height) // 2
            img.paste(scaled_image, (int(paste_x), int(paste_y)), scaled_image)
        elif self.text:
            original_font_size = self.tk_font_tuple[1]
            scaled_font = get_pil_font((self.tk_font_tuple[0], int(original_font_size * scale)))
            anchor = "mm"
            text_x = scaled_width / 2
            if self.text_align == 'left':
                anchor = "lm"
                text_x = 10 * scale
            center_y = (scaled_height / 2) - (0.5 * scale)
            draw.text(
                (text_x, center_y),
                self.text,
                font=scaled_font,
                fill=text_fill_color,
                anchor=anchor
            )

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
        if state == 'disabled':
            self.is_enabled = False
            if not self.hollow:
                self.fg_color = '#757575'
            self._draw(self.disabled_color)
        else: # 'normal'
            self.is_enabled = True
            self.fg_color = self.original_fg_color
            self._draw(self.base_color)

    def config(self, **kwargs):
        """
        Allows configuration of button properties.
        CRITICAL: Custom properties like 'hollow' must be popped from kwargs
        before passing the rest to super().config(), otherwise Tkinter will crash.
        """
        text_changed = 'text' in kwargs
        width_changed = 'width' in kwargs
        bg_changed = 'bg' in kwargs
        fg_changed = 'fg' in kwargs
        hollow_changed = 'hollow' in kwargs

        if text_changed:
            self.text = kwargs.pop('text')

        if width_changed:
            self.width = kwargs.pop('width')
            if self.hollow: self.width += 2
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

        if hollow_changed:
            self.hollow = kwargs.pop('hollow')
            if self.hollow:
                self.base_color = c.DARK_BG
                self.hover_color = self._adjust_brightness(self.base_color, 0.2)
                self.click_color = self.base_color
                self.disabled_color = self.base_color
                self.disabled_text_color = '#757575'
            else:
                self.base_color = self.original_bg_color
                self.hover_color = self._adjust_brightness(self.base_color, -0.1)
                self.click_color = self._adjust_brightness(self.base_color, -0.2)

        if 'state' in kwargs:
            self.set_state(kwargs.pop('state'))
        elif text_changed or width_changed or bg_changed or fg_changed or hollow_changed:
            # Force a redraw if appearance changed
            color = self.base_color if self.is_enabled else self.disabled_color
            self._draw(color)

        # Finally, pass any remaining standard Tkinter options to the canvas
        if kwargs:
            super().config(**kwargs)

    def configure(self, **kwargs):
        return self.config(**kwargs)