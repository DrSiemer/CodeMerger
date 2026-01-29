import tkinter as tk
from tkinter import ttk
from ... import constants as c

class ScrollableText(tk.Frame):
    """
    A frame that contains a Text widget and a Scrollbar that automatically
    appears and disappears based on content overflow.
    """
    def __init__(self, parent, on_zoom=None, **kwargs):
        super().__init__(parent, bd=1, relief='sunken')
        self.on_zoom = on_zoom

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        text_kwargs = {
            'wrap': 'word', 'undo': True,
            'relief': 'flat', 'bd': 0, 'highlightthickness': 0
        }

        # Extract initial font if provided to determine family and size
        initial_font = kwargs.get('font', c.FONT_NORMAL)
        if isinstance(initial_font, str):
            # Handle string fonts (e.g. Tkinter named fonts) if passed
            self.font_family = c.FONT_FAMILY_PRIMARY
            self.current_font_size = 12
        else:
            # Assume tuple (Family, Size)
            self.font_family = initial_font[0]
            self.current_font_size = initial_font[1]

        text_kwargs.update(kwargs)

        self.text_widget = tk.Text(self, **text_kwargs)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        self.text_widget.grid(row=0, column=0, sticky='nsew')

        self.text_widget.bind("<KeyRelease>", lambda e: self.after_idle(self._manage_scrollbar))
        self.text_widget.bind("<Configure>", lambda e: self.after_idle(self._manage_scrollbar))

        # Zoom binding
        self.text_widget.bind("<Control-MouseWheel>", self._on_mousewheel_zoom)

    def _on_mousewheel_zoom(self, event):
        if self.on_zoom:
            # Standard Windows delta is 120.
            # Up (positive) = Zoom In, Down (negative) = Zoom Out
            delta = 1 if event.delta > 0 else -1
            self.on_zoom(delta)
            return "break" # Prevent scrolling while zooming

    def set_font_size(self, size):
        """Updates the font size of the internal text widget."""
        self.current_font_size = size
        new_font = (self.font_family, size)
        self.text_widget.configure(font=new_font)
        # Font change alters height/wrapping, so check scrollbar
        self.after_idle(self._manage_scrollbar)

    def _manage_scrollbar(self):
        """
        Forces a layout update and then checks if the text content is taller
        than the visible widget area, showing or hiding the scrollbar.
        """
        # Note: We do NOT call update_idletasks() here if called via after_idle,
        # as it can cause recursion or stutter.

        top_fraction, bottom_fraction = self.text_widget.yview()
        # A scrollbar is needed if the top is scrolled down (top > 0) OR
        # if the bottom isn't visible (bottom < 1.0). This covers all overflow cases.
        is_needed = top_fraction > 0.0 or bottom_fraction < 1.0
        is_visible = self.scrollbar.winfo_ismapped()

        if is_needed and not is_visible:
            self.scrollbar.grid(row=0, column=1, sticky='ns')
        elif not is_needed and is_visible:
            self.scrollbar.grid_forget()

    def insert(self, index, chars, *args):
        self.text_widget.insert(index, chars, *args)
        self.after_idle(self._manage_scrollbar)

    def delete(self, index1, index2=None):
        self.text_widget.delete(index1, index2)
        self.after_idle(self._manage_scrollbar)

    def get(self, index1, index2=None):
        return self.text_widget.get(index1, index2)