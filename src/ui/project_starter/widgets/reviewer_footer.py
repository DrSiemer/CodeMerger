import tkinter as tk
from tkinter import Frame, Label
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...tooltip import ToolTip
from ...assets import assets

class ReviewerFooter(Frame):
    """
    Manages the action buttons at the bottom of the SegmentedReviewer.
    """
    def __init__(self, parent, on_sign_off, on_revert, on_sync, on_merge, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.on_sign_off = on_sign_off
        self.on_revert = on_revert
        self.on_sync = on_sync
        self.on_merge = on_merge

        self._build_ui()

    def _build_ui(self):
        self.container = Frame(self, bg=c.DARK_BG)
        self.container.pack(fill='x', expand=True)

        # --- Sign-off Group ---
        self.signoff_group = Frame(self.container, bg=c.DARK_BG)
        Label(self.signoff_group, image=assets.locked_icon, bg=c.DARK_BG).pack(side="left", padx=(0, 10))
        self.signoff_btn = RoundedButton(
            self.signoff_group, text="Lock segment & Next",
            command=self.on_sign_off, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT,
            font=c.FONT_BUTTON, width=200, cursor="hand2"
        )
        self.signoff_btn.pack(side="left")
        ToolTip(self.signoff_btn, "Lock this section and move to the next incomplete part", delay=500)

        # --- Revert Group ---
        self.revert_group = Frame(self.container, bg=c.DARK_BG)
        self.revert_btn = RoundedButton(
            self.revert_group, text="Unlock to edit",
            command=self.on_revert, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON, width=130, cursor="hand2"
        )
        self.revert_btn.pack(side="left")
        Label(self.revert_group, image=assets.unlocked_icon, bg=c.DARK_BG).pack(side="left", padx=(10, 0))
        ToolTip(self.revert_btn, "Release the lock to make further changes to this section", delay=500)

        # --- Utility Buttons ---
        self.sync_btn = RoundedButton(self.container, text="Sync Unsigned", command=self.on_sync, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_SMALL_BUTTON, width=130, cursor="hand2")
        ToolTip(self.sync_btn, "Propagates your changes to other unlocked sections to maintain consistency.", delay=500)

        self.merge_btn = RoundedButton(self.container, text="Merge Segments", command=self.on_merge, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, width=160, cursor="hand2")
        ToolTip(self.merge_btn, "Finalize all segments and merge them into a single document", delay=500)

    def update_state(self, is_signed, all_signed, has_changes, has_other_unsigned, current_text_exists):
        """Orchestrates the visibility of buttons based on the segment state."""
        self.signoff_group.pack_forget()
        self.revert_group.pack_forget()
        self.sync_btn.pack_forget()
        self.merge_btn.pack_forget()

        if all_signed:
            self.merge_btn.pack(side="right")
            self.revert_group.pack(side="left", padx=(0, 10))
            return

        if is_signed:
            self.revert_group.pack(side="left", padx=(0, 10))
        else:
            self.signoff_group.pack(side="right")
            if has_other_unsigned and has_changes and current_text_exists:
                self.sync_btn.pack(side="left")

    def register_info(self, info_mgr):
        info_mgr.register(self.signoff_btn, "starter_seg_signoff")
        info_mgr.register(self.sync_btn, "starter_seg_sync")