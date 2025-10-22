import tkinter as tk
from tkinter import ttk

class ScrollableText(tk.Frame):
    """
    A frame that contains a Text widget and a Scrollbar that automatically
    appears and disappears based on content overflow.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bd=1, relief='sunken')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        text_kwargs = {
            'wrap': 'word', 'undo': True,
            'relief': 'flat', 'bd': 0, 'highlightthickness': 0
        }
        text_kwargs.update(kwargs)

        self.text_widget = tk.Text(self, **text_kwargs)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        self.text_widget.grid(row=0, column=0, sticky='nsew')

        self.text_widget.bind("<KeyRelease>", lambda e: self.after_idle(self._manage_scrollbar))
        self.text_widget.bind("<Configure>", lambda e: self.after_idle(self._manage_scrollbar))

    def _manage_scrollbar(self):
        """
        Forces a layout update and then checks if the text content is taller
        than the visible widget area, showing or hiding the scrollbar.
        """
        self.update_idletasks()

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