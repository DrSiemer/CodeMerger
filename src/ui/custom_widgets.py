import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os
import sys
from .. import constants as c

# --- Robust Font Finding Logic ---
WINDOWS_FONT_MAP = {
    "segoe ui": ["segoeui.ttf", "seguisb.ttf", "seguili.ttf"],
    "calibri": ["calibri.ttf", "calibrib.ttf"],
    "helvetica": ["helvetica.ttf", "helveticab.ttf"],
    "arial": ["arial.ttf", "arialbd.ttf"],
}
FONT_FALLBACK_ORDER = ["Calibri", "Helvetica", "Arial"]
def get_pil_font(font_tuple):
    """
    Tries to find and load a requested font, with a prioritized list of
    fallbacks for cross-platform compatibility.
    """
    requested_family, font_size = font_tuple
    # Create a dynamic search list, starting with the requested font
    search_list = [requested_family] + [f for f in FONT_FALLBACK_ORDER if f.lower() != requested_family.lower()]
    for family in search_list:
        normalized_family = family.lower()
        # On Windows, search the system Fonts directory with known filenames
        if sys.platform == "win32" and normalized_family in WINDOWS_FONT_MAP:
            font_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts")
            for font_file in WINDOWS_FONT_MAP[normalized_family]:
                path = os.path.join(font_dir, font_file)
                if os.path.exists(path):
                    try:
                        return ImageFont.truetype(path, font_size)
                    except IOError:
                        continue # Try the next variant
        # Generic fallback for other systems or if the direct path search fails
        try:
            # Pillow can often find system fonts by name
            return ImageFont.truetype(family, font_size)
        except IOError:
            try:
                # Or by common filename conventions
                return ImageFont.truetype(f"{normalized_family}.ttf", font_size)
            except IOError:
                continue # Font not found, try the next one in the list
    # If none of the preferred fonts are found, use the absolute default
    return ImageFont.load_default()

class RoundedButton(tk.Canvas):
    """A custom anti-aliased rounded button widget for tkinter."""
    def __init__(self, parent, command, text=None, image=None, font=None, bg='#CCCCCC', fg='#000000', width=None, height=30, radius=6, hollow=False, h_padding=None):
        if font:
            # If a tuple like ("Segoe UI", 12) is passed, use it directly
            self.tk_font_tuple = font
        else:
            # If font is None, get the default font and extract its properties
            default_font = tkFont.nametofont("TkDefaultFont")
            self.tk_font_tuple = (default_font.actual("family"), default_font.actual("size"))
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
        super().__init__(parent, width=self.width, height=self.height, bg=parent.cget('bg'), bd=0, highlightthickness=0)
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

class TwoColumnList(tk.Canvas):
    """A custom listbox widget that displays two columns with independent styling."""
    def __init__(self, parent, right_col_font, right_col_width, **kwargs):
        super().__init__(parent, bg=c.TEXT_INPUT_BG, highlightthickness=0, **kwargs)
        self.items = []
        self.selected_indices = set()
        self.highlighted_indices = set()
        self.row_height = 25
        self.left_col_font = tkFont.Font(family="Segoe UI", size=12)
        self.right_col_font = right_col_font
        self.right_col_width = right_col_width
        self.scrollbar = None
        self.bind("<ButtonPress-1>", self._on_click)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Configure>", self._redraw)
        # This is the key: the yscrollcommand will be set externally by the scrollbar.
        # We wrap the default yview methods to trigger a redraw *after* they have moved the canvas.
        self._original_yview = self.yview
        self._original_yview_scroll = self.yview_scroll
        self._original_yview_moveto = self.yview_moveto
        self.yview = self._yview_wrapper
        self.yview_scroll = self._yview_scroll_wrapper
        self.yview_moveto = self._yview_moveto_wrapper

    def _yview_wrapper(self, *args):
        # The wrapper must return the result of the original method call
        result = self._original_yview(*args)
        self._redraw()
        return result

    def _yview_scroll_wrapper(self, *args):
        # This wrapper must also return the result of the original call
        result = self._original_yview_scroll(*args)
        self._redraw()
        return result

    def _yview_moveto_wrapper(self, *args):
        # This wrapper must also return the result of the original call
        result = self._original_yview_moveto(*args)
        self._redraw()
        return result

    def link_scrollbar(self, scrollbar):
        """Links a ttk.Scrollbar widget to this list for visibility management."""
        self.scrollbar = scrollbar

    def bind_event(self, sequence=None, func=None, add=None):
        self.bind(sequence, func, add)

    def _on_mousewheel(self, event):
        # [FIX] This is the robust, final logic for scrolling.
        # It directly checks the scrollbar's state to prevent flicker at the limits.

        # 1. If no scrollbar is linked or it's not visible (content fits), do nothing.
        if not self.scrollbar or not self.scrollbar.winfo_ismapped():
            return

        # 2. Get the scrollbar's current position. It returns (top_fraction, bottom_fraction).
        start, end = self.scrollbar.get()

        # 3. Determine scroll direction.
        delta = -1 * (event.delta // 120) if sys.platform == "win32" else event.delta

        # 4. Check boundaries to prevent scrolling past the limits.
        # If trying to scroll up (delta < 0) but we're already at the top (start == 0.0)...
        if delta < 0 and start <= 0.0:
            return  # ...do nothing.

        # If trying to scroll down (delta > 0) but we're already at the bottom (end == 1.0)...
        if delta > 0 and end >= 1.0:
            return  # ...do nothing.

        # 5. If all checks passed, it's safe to scroll. This will trigger the yview_scroll_wrapper,
        # which correctly redraws the visible items.
        self.yview_scroll(delta, "units")

    def _on_click(self, event):
        self.focus_set()
        # Use canvasy to get the coordinate relative to the scrollable area
        clicked_index = int(self.canvasy(event.y) // self.row_height)
        if 0 <= clicked_index < len(self.items):
            is_shift = (event.state & 0x0001)
            is_ctrl = (event.state & 0x0004)
            if not is_ctrl and not is_shift:
                self.selected_indices = {clicked_index}
            elif is_ctrl:
                if clicked_index in self.selected_indices:
                    self.selected_indices.remove(clicked_index)
                else:
                    self.selected_indices.add(clicked_index)
            self.event_generate("<<ListSelectionChanged>>")
            self._redraw()

    def _update_scrollregion(self):
        total_height = len(self.items) * self.row_height
        self.config(scrollregion=(0, 0, self.winfo_width(), total_height))

    def _update_scrollbar_visibility(self):
        """Shows or hides the linked scrollbar based on content height."""
        if not self.scrollbar:
            return
        self.update_idletasks() # Ensure winfo_height() is accurate
        content_height = len(self.items) * self.row_height
        canvas_height = self.winfo_height()
        # If the content is taller than the canvas, we need the scrollbar
        if content_height > canvas_height:
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.grid() # grid() remembers previous options
        # Otherwise, hide it
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.grid_remove()

    def _redraw(self, event=None):
        self.delete("all")
        self._update_scrollregion()
        self._update_scrollbar_visibility()
        width = self.winfo_width()
        # Determine the visible range of items based on the canvas's current view
        view_y_start = self.canvasy(0)
        view_y_end = self.canvasy(self.winfo_height())
        start_index = max(0, int(view_y_start // self.row_height))
        end_index = min(len(self.items), int(view_y_end // self.row_height) + 2)
        for i in range(start_index, end_index):
            if i >= len(self.items): continue
            item = self.items[i]
            y = i * self.row_height
            # Draw background for selection or highlight
            bg_color = ""
            if i in self.selected_indices:
                bg_color = c.BTN_BLUE
            elif i in self.highlighted_indices:
                bg_color = c.SUBTLE_HIGHLIGHT_COLOR
            if bg_color:
                self.create_rectangle(0, y, width, y + self.row_height, fill=bg_color, outline="")
            left_fg = c.BTN_BLUE_TEXT if i in self.selected_indices else c.TEXT_COLOR
            # Draw left column (filename)
            self.create_text(
                5, y + self.row_height / 2,
                anchor='w',
                text=item.get('left', ''),
                font=self.left_col_font,
                fill=left_fg
            )
            # Draw right column (line count)
            self.create_text(
                width - 5, y + self.row_height / 2,
                anchor='e',
                text=item.get('right', ''),
                font=self.right_col_font,
                fill=item.get('right_fg', c.TEXT_SUBTLE_COLOR)
            )

    def set_items(self, items):
        selection_paths = {self.get_item_data(i) for i in self.curselection()}
        self.items = items
        # Restore selection based on data, not index
        new_selection = set()
        for i, item in enumerate(self.items):
            if item.get('data') in selection_paths:
                new_selection.add(i)
        self.selected_indices = new_selection
        self._redraw()

    def curselection(self):
        return sorted(list(self.selected_indices))

    def clear_selection(self):
        self.selected_indices.clear()
        self._redraw()

    def see(self, index):
        """Scrolls the list to make the item at the given index visible."""
        if not (0 <= index < len(self.items)):
            return
        item_y_start = index * self.row_height
        item_y_end = item_y_start + self.row_height
        view_y_start = self.canvasy(0)
        view_y_end = view_y_start + self.winfo_height()
        total_height = len(self.items) * self.row_height
        if total_height == 0: return
        if item_y_start < view_y_start:
            # Item is above the view, scroll up
            fraction = item_y_start / total_height
            self.yview_moveto(fraction)
        elif item_y_end > view_y_end:
            # Item is below the view, scroll down
            fraction = (item_y_end - self.winfo_height()) / total_height
            self.yview_moveto(fraction)

    def selection_set(self, start, end=None):
        self.selected_indices = set(range(start, (end if end is not None else start) + 1))
        self._redraw()

    def get_item_data(self, index):
        if 0 <= index < len(self.items):
            return self.items[index].get('data')
        return None

    def highlight_item(self, index):
        self.highlighted_indices.add(index)
        self._redraw()

    def clear_highlights(self):
        self.highlighted_indices.clear()
        self._redraw()