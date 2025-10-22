import tkinter as tk
from tkinter import ttk

class ScrollableText(tk.Frame):
    """
    A frame that contains a Text widget and a Scrollbar that automatically
    appears and disappears based on content overflow.
    """
    def __init__(self, parent, **kwargs):
        # The main container is a sunken frame to match the original look
        super().__init__(parent, bd=1, relief='sunken')

        # Extract text-specific kwargs and set defaults from the original implementation
        text_kwargs = {
            'wrap': 'word', 'undo': True, 'height': 4,
            'relief': 'flat', 'bd': 0, 'highlightthickness': 0
        }
        text_kwargs.update(kwargs)

        self.text_widget = tk.Text(self, **text_kwargs)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        self.text_widget.pack(side="left", fill="both", expand=True)

        # We use after_idle to ensure the check happens after any pending UI updates.
        self.text_widget.bind("<KeyRelease>", lambda e: self.after_idle(self._manage_scrollbar))
        self.text_widget.bind("<Configure>", lambda e: self.after_idle(self._manage_scrollbar))

    def _manage_scrollbar(self):
        """
        Checks if the text content is taller than the visible widget area and
        shows or hides the scrollbar accordingly.
        """
        # The yview() method returns a tuple (top_fraction, bottom_fraction).
        # If the content fits perfectly or is smaller, bottom_fraction will be 1.0.
        # If the content is overflowing, bottom_fraction will be less than 1.0.
        top_fraction, bottom_fraction = self.text_widget.yview()

        is_needed = bottom_fraction < 1.0

        if is_needed and not self.scrollbar.winfo_ismapped():
            self.scrollbar.pack(side="right", fill="y")
        elif not is_needed and self.scrollbar.winfo_ismapped():
            self.scrollbar.pack_forget()

    # --- Delegate methods to the underlying Text widget for a familiar API ---
    def insert(self, index, chars, *args):
        self.text_widget.insert(index, chars, *args)
        self.after_idle(self._manage_scrollbar)

    def delete(self, index1, index2=None):
        self.text_widget.delete(index1, index2)
        self.after_idle(self._manage_scrollbar)

    def get(self, index1, index2=None):
        return self.text_widget.get(index1, index2)