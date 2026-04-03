import tkinter as tk
from tkinter import ttk
import difflib
from ... import constants as c

class DiffViewer(tk.Frame):
    """
    A widget that displays a color-coded unified diff between two text strings.
    It grows vertically to fit its content without internal scrollbars.
    """
    def __init__(self, parent, old_text, new_text, *args, **kwargs):
        # We ignore height passed in kwargs to allow dynamic sizing
        kwargs.pop('height', None)
        super().__init__(parent, bg=c.TEXT_INPUT_BG, bd=1, relief='sunken', **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # We use wrap='word' because scrollbars are removed per request
        self.text_widget = tk.Text(
            self, wrap='word', bd=0, highlightthickness=0,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            font=("Consolas", 10), padx=10, pady=10,
            state='disabled'
        )
        self.text_widget.grid(row=0, column=0, sticky='nsew')

        # Tags for highlighting with optimized legibility (foreground and background)
        self.text_widget.tag_configure("add", background=c.DIFF_ADD_BG, foreground=c.DIFF_ADD_FG)
        self.text_widget.tag_configure("remove", background=c.DIFF_REMOVE_BG, foreground=c.DIFF_REMOVE_FG)
        self.text_widget.tag_configure("header", foreground=c.DIFF_HEADER_FG, font=("Consolas", 10, "bold"))

        # Binding to update height when window/container resizes (influences wrap points)
        self.text_widget.bind("<Configure>", self._adjust_height_to_content)

        self._generate_diff(old_text, new_text)

    def _adjust_height_to_content(self, event=None):
        """Calculates and sets the widget height based on visual lines to prevent internal scrolling."""
        if not self.winfo_exists():
            return
        try:
            # We use "displaylines" to account for word wrapping.
            # "end-1c" excludes the trailing newline Tkinter automatically appends.
            result = self.text_widget.count("1.0", "end-1c", "displaylines")
            if result:
                actual_lines = result[0]
                # We add +1 as a buffer to account for internal padding and prevent
                # the "one line short" scrolling artifact.
                self.text_widget.config(height=max(1, actual_lines + 1))
        except tk.TclError:
            pass

    def _generate_diff(self, old_text, new_text):
        """Calculates the diff and populates the text widget with tags."""
        # Plain view for new files (no old content)
        if not old_text:
            self.text_widget.config(state='normal')
            self.text_widget.delete("1.0", tk.END)
            if new_text:
                self.text_widget.insert(tk.END, new_text)
            else:
                self.text_widget.insert(tk.END, "(File is empty)")

            self.text_widget.config(state='disabled')
            self.after_idle(self._adjust_height_to_content)
            return

        old_lines = old_text.splitlines() if old_text else []
        new_lines = new_text.splitlines() if new_text else []

        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))

        self.text_widget.config(state='normal')
        self.text_widget.delete("1.0", tk.END)

        for line in diff:
            tag = None
            if line.startswith('+') and not line.startswith('+++'):
                tag = "add"
            elif line.startswith('-') and not line.startswith('---'):
                tag = "remove"
            elif line.startswith('@@') or line.startswith('---') or line.startswith('+++'):
                tag = "header"

            if tag:
                self.text_widget.insert(tk.END, line + "\n", tag)
            else:
                self.text_widget.insert(tk.END, line + "\n")

        if not diff:
            self.text_widget.insert(tk.END, "(No changes detected in file content)")

        self.text_widget.config(state='disabled')

        # Adjust height to fit all lines perfectly after insertion
        self.after_idle(self._adjust_height_to_content)