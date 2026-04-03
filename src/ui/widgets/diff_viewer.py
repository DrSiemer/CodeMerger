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

        self._generate_diff(old_text, new_text)

    def _generate_diff(self, old_text, new_text):
        """Calculates the diff and populates the text widget with tags."""
        # Plain view for new files (no old content)
        if not old_text:
            self.text_widget.config(state='normal')
            self.text_widget.delete("1.0", tk.END)
            if new_text:
                self.text_widget.insert(tk.END, new_text)
                line_count = new_text.count('\n') + 1
            else:
                self.text_widget.insert(tk.END, "(File is empty)")
                line_count = 1
            self.text_widget.config(height=line_count, state='disabled')
            return

        old_lines = old_text.splitlines() if old_text else []
        new_lines = new_text.splitlines() if new_text else []

        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))

        self.text_widget.config(state='normal')
        self.text_widget.delete("1.0", tk.END)

        line_count = 0
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
            line_count += 1

        if not diff:
            self.text_widget.insert(tk.END, "(No changes detected in file content)")
            line_count = 1

        # Adjust height to fit all lines perfectly
        self.text_widget.config(height=line_count)
        self.text_widget.config(state='disabled')