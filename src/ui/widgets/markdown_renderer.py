import tkinter as tk
from tkinter import ttk
import re
from src import constants as c
try:
    import markdown2
    MARKDOWN2_INSTALLED = True
except ImportError:
    MARKDOWN2_INSTALLED = False

class MarkdownRenderer(tk.Frame):
    """
    A custom markdown renderer using a standard tk.Text widget to provide
    reliable layout, styling, and scrolling.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config(bg=c.TEXT_INPUT_BG)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if MARKDOWN2_INSTALLED:
            self.text_widget = tk.Text(
                self, wrap=tk.WORD, bd=0, highlightthickness=0,
                padx=10, pady=10, font=(c.FONT_FAMILY_PRIMARY, 10),
                bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            )
            self.text_widget.grid(row=0, column=0, sticky="nsew")

            self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview, style="Vertical.TScrollbar")
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self.text_widget.configure(yscrollcommand=self.scrollbar.set)

            # --- Tag Configurations for Markdown Elements ---
            self.text_widget.tag_configure("h1", font=c.FONT_LARGE_BOLD, spacing1=10, spacing3=5)
            self.text_widget.tag_configure("h2", font=c.FONT_H2, spacing1=8, spacing3=4)
            self.text_widget.tag_configure("h3", font=c.FONT_H3, spacing1=6, spacing3=3)
            self.text_widget.tag_configure("bold", font=(c.FONT_FAMILY_PRIMARY, 10, 'bold'))
            self.text_widget.tag_configure("italic", font=(c.FONT_FAMILY_PRIMARY, 10, 'italic'))
            self.text_widget.tag_configure("code", background=c.DARK_BG, font=("Courier", 9), relief="sunken", borderwidth=1)

        else:
            error_message = "Markdown rendering disabled. Please install 'markdown2'."
            self.error_label = tk.Label(
                self, text=error_message, justify="center", font=c.FONT_NORMAL,
                fg=c.TEXT_SUBTLE_COLOR, bg=c.DARK_BG, wraplength=400
            )
            self.error_label.grid(row=0, column=0)

    def set_markdown(self, markdown_text):
        if not MARKDOWN2_INSTALLED: return

        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)

        for line in markdown_text.split('\n'):
            if line.startswith("# "):
                self.text_widget.insert(tk.END, f"{line[2:].strip()}\n", "h1")
            elif line.startswith("## "):
                self.text_widget.insert(tk.END, f"{line[3:].strip()}\n", "h2")
            elif line.startswith("### "):
                self.text_widget.insert(tk.END, f"{line[4:].strip()}\n", "h3")
            elif re.match(r'^\s*-\s*\[( |x)\]', line):
                match = re.match(r'^(\s*)-\s*\[( |x)\]\s*(.*)', line)
                indent, checked, text = match.groups()
                checkbox = '☑' if checked.lower() == 'x' else '☐'
                indent_level = len(indent) // 2
                tag_name = f"indent_{indent_level}"
                self.text_widget.tag_configure(tag_name, lmargin1=25 + indent_level * 20, lmargin2=25 + indent_level * 20)
                self.text_widget.insert(tk.END, f"{checkbox} {text.strip()}\n", tag_name)
            elif re.match(r'^\s*[-*]\s', line):
                match = re.match(r'^(\s*)[-*]\s(.*)', line)
                indent, text = match.groups()
                indent_level = len(indent) // 2
                tag_name = f"bullet_indent_{indent_level}"
                self.text_widget.tag_configure(tag_name, lmargin1=25 + indent_level * 20, lmargin2=25 + indent_level * 20)
                self.text_widget.insert(tk.END, f"• {text.strip()}\n", tag_name)
            else:
                self.text_widget.insert(tk.END, f"{line}\n")

        # This robustly replaces markdown symbols with styled text by finding the
        # content, deleting the original text including symbols, and re-inserting
        # the content with the proper tag.
        self._apply_format_and_hide_symbols(r"\*\*(.*?)\*\*", "bold")
        self._apply_format_and_hide_symbols(r"\*(.*?)\*", "italic")
        self._apply_format_and_hide_symbols(r"`(.*?)`", "code")

        self.text_widget.config(state=tk.DISABLED)

    def _apply_format_and_hide_symbols(self, pattern, tag):
        start_index = "1.0"
        while True:
            match_start = self.text_widget.search(pattern, start_index, stopindex=tk.END, regexp=True)
            if not match_start: break

            line_end = self.text_widget.index(f"{match_start} lineend")
            line_text = self.text_widget.get(match_start, line_end)

            match = re.search(pattern, line_text)
            if not match:
                start_index = self.text_widget.index(f"{match_start}+1c")
                continue

            full_match_text = match.group(0)
            content_text = match.group(1)

            match_end_index = self.text_widget.index(f"{match_start}+{len(full_match_text)}c")

            self.text_widget.delete(match_start, match_end_index)
            self.text_widget.insert(match_start, content_text, tag)

            start_index = self.text_widget.index(f"{match_start}+{len(content_text)}c")