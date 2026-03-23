import tkinter as tk
from tkinter import Frame, Label
from .... import constants as c
from ...assets import assets
from ...tooltip import ToolTip

class SidebarItem(Frame):
    def __init__(self, parent, text, is_overview, status_var=None, command=None):
        super().__init__(parent, bg=c.DARK_BG, cursor="hand2")
        self.command = command
        self.is_selected = False
        self.is_disabled = False
        self.is_updated = False # Indicates content was changed via sync but not viewed
        self.status_var = status_var
        self.is_overview = is_overview
        self.parent_tooltip = None

        # Alignment: Overview (Full Text) is the parent. Segments are children.
        if not is_overview:
            # Indicator for segments (Uses lock graphics)
            self.indicator = Label(self, bg=c.DARK_BG, image=assets.unlocked_icon)
            self.indicator.pack(side="left", padx=(5, 5))
            self.indicator_tooltip = ToolTip(self.indicator, "Lock segment", delay=500)
            text_padx = (0, 10)
        else:
            # No indicator for Full Text, align to far left
            self.indicator = Label(self, bg=c.DARK_BG)
            text_padx = (5, 10)

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
        if hasattr(self, 'indicator') and not self.is_overview:
            # Use dedicated toggle handler for the icon. Bind to Button-1 for instant feedback.
            self.indicator.bind("<Button-1>", self._on_indicator_click, add="+")

            # Tooltip Handoff: Suppress parent tooltip when hovering the lock icon
            self.indicator.bind("<Enter>", self._on_indicator_hover, add="+")
            self.indicator.bind("<Leave>", self._on_indicator_leave, add="+")

    def _unbind_events(self):
        self.unbind("<Button-1>")
        self.label.unbind("<Button-1>")
        if hasattr(self, 'indicator'): self.indicator.unbind("<Button-1>")

    def _on_click(self, event=None):
        if not self.is_disabled and self.command:
            self.command()

    def _on_indicator_click(self, event):
        """Toggles the locked state instantly and prevents navigation."""
        if not self.is_disabled and self.status_var:
            self.status_var.set(not self.status_var.get())
        return "break"

    def _on_indicator_hover(self, event):
        """Hides the parent navigation tooltip so only the lock tooltip shows."""
        if self.parent_tooltip:
            self.parent_tooltip.hide_tooltip()
            self.parent_tooltip.cancel_show()

    def _on_indicator_leave(self, event):
        """Allows the parent tooltip to show again when moving back to the label/frame."""
        if self.parent_tooltip:
            self.parent_tooltip.schedule_show()

    def link_parent_tooltip(self, tooltip_obj):
        """Stores a reference to the tooltip created for the whole sidebar item."""
        self.parent_tooltip = tooltip_obj

    def register_indicator_info(self, info_mgr):
        """Allows external registration of the indicator label with the Info Panel."""
        if hasattr(self, 'indicator') and not self.is_overview:
            info_mgr.register(self.indicator, "starter_seg_indicator")

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
        self.indicator.config(cursor=cursor)

    def set_updated(self, updated):
        """Marks the item as having pending changes from a sync operation."""
        # Don't show updated status if the item is signed off or disabled
        if self.is_disabled or (self.status_var and self.status_var.get()):
            return
        self.is_updated = updated
        self._update_status_icon()

    def _update_status_icon(self, *args):
        if not self.status_var or self.is_overview: return

        is_locked = self.status_var.get()
        if is_locked:
            # Locked: Use locked icon
            self.indicator.config(image=assets.locked_icon)
            if hasattr(self, 'indicator_tooltip'):
                self.indicator_tooltip.text = "Unlock to edit"
        else:
            # Unlocked: Use unlocked icon
            self.indicator.config(image=assets.unlocked_icon)
            if hasattr(self, 'indicator_tooltip'):
                self.indicator_tooltip.text = "Lock segment"

        # Highlight color for sync updates
        if not is_locked and self.is_updated:
            self.label.config(fg=c.ATTENTION)
        else:
            self.label.config(fg=c.TEXT_COLOR if not self.is_disabled else "#666666")