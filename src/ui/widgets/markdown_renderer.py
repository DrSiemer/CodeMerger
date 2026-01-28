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
    Accepts base_font_size to scale text for better readability.
    """
    def __init__(self, parent, base_font_size=10, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config(bg=c.TEXT_INPUT_BG)
        self.base_font_size = base_font_size

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if MARKDOWN2_INSTALLED:
            self.text_widget = tk.Text(
                self, wrap=tk.WORD, bd=0, highlightthickness=0,
                padx=15, pady=15, font=(c.FONT_FAMILY_PRIMARY, self.base_font_size),
                bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
                spacing2=6, spacing1=4, spacing3=4
            )
            self.text_widget.grid(row=0, column=0, sticky="nsew")

            self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview, style="Vertical.TScrollbar")
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self.text_widget.configure(yscrollcommand=self.scrollbar.set)

            # --- Tag Configurations for Markdown Elements ---
            self.text_widget.tag_configure("h1", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size + 12, 'bold'), spacing1=20, spacing3=10)
            self.text_widget.tag_configure("h2", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size + 6, 'bold'), spacing1=16, spacing3=8)
            self.text_widget.tag_configure("h3", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size + 2, 'bold'), spacing1=12, spacing3=5)
            self.text_widget.tag_configure("bold", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size, 'bold'))
            self.text_widget.tag_configure("italic", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size, 'italic'))
            self.text_widget.tag_configure("code", foreground="#DEB887", font=("Courier New", self.base_font_size - 1))

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

        if not markdown_text:
            self.text_widget.config(state=tk.DISABLED)
            return

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
                tag_name = f"checkbox_indent_{indent_level}"

                # Hanging indent calculation for Checkboxes
                base_indent = 25 + indent_level * 20
                hanging_indent = base_indent + 22

                self.text_widget.tag_configure(tag_name, lmargin1=base_indent, lmargin2=hanging_indent, spacing1=4)
                self.text_widget.insert(tk.END, f"{checkbox} {text.strip()}\n", tag_name)
            elif re.match(r'^\s*[-*]\s', line):
                match = re.match(r'^(\s*)[-*]\s(.*)', line)
                indent, text = match.groups()
                indent_level = len(indent) // 2
                tag_name = f"bullet_indent_{indent_level}"

                # Hanging indent calculation for Bullets
                base_indent = 25 + indent_level * 20
                hanging_indent = base_indent + 15

                self.text_widget.tag_configure(tag_name, lmargin1=base_indent, lmargin2=hanging_indent, spacing1=4)
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

            # Capture existing layout tags (e.g. checkbox_indent_0) to preserve indentation
            # We filter out 'sel' to avoid carrying over selection highlights unintentionally
            existing_tags = [t for t in self.text_widget.tag_names(match_start) if t != 'sel']

            self.text_widget.delete(match_start, match_end_index)

            # Combine existing layout tags with the new styling tag
            final_tags = tuple(existing_tags) + (tag,)

            self.text_widget.insert(match_start, content_text, final_tags)

            start_index = self.text_widget.index(f"{match_start}+{len(content_text)}c")