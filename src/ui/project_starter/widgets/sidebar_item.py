import tkinter as tk
from tkinter import Frame, Label
from .... import constants as c

class SidebarItem(Frame):
    def __init__(self, parent, text, is_overview, status_var=None, command=None):
        super().__init__(parent, bg=c.DARK_BG, cursor="hand2")
        self.command = command
        self.is_selected = False
        self.is_disabled = False
        self.is_updated = False # Indicates content was changed via sync but not viewed
        self.status_var = status_var
        self.is_overview = is_overview

        # Alignment: Overview (Full Text) is the parent. Segments are children.
        if not is_overview:
            # Bullet indicator for segments (Uses Unicode Black Circle)
            self.indicator = Label(self, text="●", font=("Arial", 12), bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR)
            self.indicator.pack(side="left", padx=(15, 5))
            text_padx = (0, 10)
        else:
            # No indicator for Full Text, align to far left
            self.indicator = Label(self, bg=c.DARK_BG)
            text_padx = (10, 10)

        label_text = text
        font = c.FONT_BOLD if is_overview else c.FONT_NORMAL

        self.label = Label(self, text=label_text, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font, anchor="w")
        self.label.pack(side="left", fill="x", expand=True, pady=8, padx=text_padx)

        self._bind_events()

        if self.status_var:
            self.status_var.trace_add("write", self._update_status_icon)
            self._update_status_icon()

    def _bind_events(self):
        self.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)
        if hasattr(self, 'indicator') and self.indicator.winfo_ismapped():
            self.indicator.bind("<Button-1>", self._on_click)

    def _unbind_events(self):
        self.unbind("<Button-1>")
        self.label.unbind("<Button-1>")
        if hasattr(self, 'indicator'): self.indicator.unbind("<Button-1>")

    def _on_click(self, event=None):
        if not self.is_disabled and self.command:
            self.command()

    def set_selected(self, selected):
        if self.is_disabled: return
        self.is_selected = selected
        bg = c.TEXT_INPUT_BG if selected else c.DARK_BG
        self.config(bg=bg)
        self.label.config(bg=bg)
        self.indicator.config(bg=bg)

    def set_disabled(self, disabled):
        self.is_disabled = disabled

        if disabled:
            fg = "#666666" # Clearly disabled gray
            cursor = "arrow"
            self._unbind_events()
            # If item was selected, visually deselect it immediately
            if self.is_selected:
                self.is_selected = False
                self.config(bg=c.DARK_BG)
                self.label.config(bg=c.DARK_BG)
                self.indicator.config(bg=c.DARK_BG)
        else:
            fg = c.TEXT_COLOR
            cursor = "hand2"
            self._bind_events()

        self.config(cursor=cursor)
        self.label.config(fg=fg, cursor=cursor)
        self.indicator.config(fg=fg, cursor=cursor)

    def set_updated(self, updated):
        """Marks the item as having pending changes from a sync operation."""
        # Don't show updated status if the item is signed off or disabled
        if self.is_disabled or (self.status_var and self.status_var.get()):
            return
        self.is_updated = updated
        self._update_status_icon()

    def _update_status_icon(self, *args):
        if not self.status_var or self.is_overview: return

        if self.status_var.get():
            # Signed Off: Green Check
            self.indicator.config(text="✓", fg=c.BTN_GREEN)
        elif self.is_updated:
            # Updated / Attention Needed: Orange Dot
            self.indicator.config(text="●", fg=c.ATTENTION)
        else:
            # Default: Gray Dot
            self.indicator.config(text="●", fg=c.TEXT_SUBTLE_COLOR)