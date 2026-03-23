import tkinter as tk
from tkinter import Frame
from .... import constants as c
from .sidebar_item import SidebarItem
from ...tooltip import ToolTip

class ReviewerSidebar(Frame):
    """
    Manages the left navigation pane of the SegmentedReviewer.
    """
    def __init__(self, parent, segment_keys, friendly_names_map, signoff_vars, on_navigate_callback, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, width=220, **kwargs)
        self.pack_propagate(False)

        self.segment_keys = segment_keys
        self.friendly_names_map = friendly_names_map
        self.signoff_vars = signoff_vars
        self.on_navigate = on_navigate_callback
        self.items = {}

        self._build_ui()

    def _build_ui(self):
        for key in self.segment_keys:
            name = self.friendly_names_map.get(key, key)
            item = SidebarItem(
                self, name, False,
                status_var=self.signoff_vars[key],
                command=lambda k=key: self.on_navigate(k)
            )
            item.pack(fill="x")

            # Create the parent ToolTip and link it to the item so the item can suppress it
            item_tooltip = ToolTip(item, f"Navigate to {name}", delay=500)
            item.link_parent_tooltip(item_tooltip)

            self.items[key] = item

    def set_active(self, active_key):
        """Updates the selection highlight in the sidebar."""
        for key, item in self.items.items():
            item.set_selected(key == active_key)

    def mark_updated(self, key, is_updated):
        """Marks a segment as having pending sync changes."""
        if key in self.items:
            self.items[key].set_updated(is_updated)

    def register_info(self, info_mgr):
        """Registers sidebar components with the Info Panel."""
        info_mgr.register(self, "starter_seg_nav")
        for item in self.items.values():
            item.register_indicator_info(info_mgr)