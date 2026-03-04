import tkinter as tk
import re
from .. import constants as c
from .assets import assets
from .info_messages import INFO_MESSAGES
from .tooltip import ToolTip

class InfoManager:
    """
    Manages a single window's Info Panel and Toggle Button.
    Subscribes to global AppState for synchronized visibility across windows.
    Automatically grows/shrinks the window height when toggled.
    """
    def __init__(self, window, app_state, manager_type, toggle_btn, grid_row=None):
        self.window = window
        self.app_state = app_state
        self.manager_type = manager_type # 'grid' or 'pack'
        self.grid_row = grid_row
        self.toggle_btn = toggle_btn
        self.panel_height = c.INFO_PANEL_HEIGHT

        # Track currently hovered registered widgets to handle nesting correctly
        # Stores tuples of (widget, key)
        self._active_stack = []

        # --- Info Panel ---
        self.panel = tk.Frame(
            window, bg=c.INFO_PANEL_BG, height=self.panel_height,
            highlightbackground=c.WRAPPER_BORDER, highlightthickness=1
        )
        self.panel.pack_propagate(False)

        # Defensive initial wraplength calculation
        initial_w = window.winfo_width()
        if initial_w <= 1:
            initial_w = window.winfo_reqwidth()
        if initial_w <= 1:
            initial_w = 400

        self.label = tk.Label(
            self.panel, text=INFO_MESSAGES["default"],
            bg=c.INFO_PANEL_BG, fg=c.TEXT_SUBTLE_COLOR,
            font=c.FONT_INFO_PANEL, justify="left",
            wraplength=initial_w - 40, anchor="w"
        )
        self.label.pack(side="left", padx=10, fill="both", expand=True)

        # --- Tooltip ---
        self.button_tooltip = ToolTip(self.toggle_btn, text="Toggle Info Mode")

        # --- Toggle Button Configuration ---
        self.toggle_btn.bind("<Button-1>", lambda e: self.app_state.toggle_info_mode())
        self.toggle_btn.bind("<Enter>", self._on_button_enter, add="+")
        self.toggle_btn.bind("<Leave>", self._on_button_leave, add="+")

        # Sync wraplength to window size changes
        self.window.bind("<Configure>", self._on_window_resize, add="+")

        # Register this instance to receive global state updates
        self.app_state.register_info_observer(self.refresh_visibility)

        # Apply initial UI state without triggering a resize (handled by boot geometry)
        self.is_initialized = False
        self._apply_visibility_ui(self.app_state.info_mode_active)
        self.is_initialized = True

    def clear_active_stack(self):
        """Forcefully clears the hover stack. Call this before destroying widgets in the Wizard."""
        self._active_stack = []
        self._update_display()

    def _on_window_resize(self, event=None):
        if self.panel.winfo_ismapped():
            self.label.config(wraplength=self.window.winfo_width() - 40)

    def _adjust_window_height(self, expand: bool):
        """Physically resizes the window to accommodate the panel appearance."""
        if not self.window.winfo_exists():
            return

        self.window.update_idletasks()
        geom = self.window.geometry()
        match = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
        if not match:
            return

        w, h, x, y = map(int, match.groups())

        if expand:
            new_h = h + self.panel_height
        else:
            new_h = h - self.panel_height

        self.window.geometry(f"{w}x{new_h}+{x}+{y}")

    def refresh_visibility(self, is_active):
        """Global callback to sync visibility and window size."""
        self._apply_visibility_ui(is_active)

        if self.is_initialized:
            self._adjust_window_height(expand=is_active)

    def _apply_visibility_ui(self, is_active):
        """Updates just the widget states using the appropriate geometry manager."""
        if is_active:
            if self.manager_type == 'grid':
                self.panel.grid(row=self.grid_row, column=0, sticky="ew")
            else:
                self.panel.pack(side="bottom", fill="x")
            self.button_tooltip.text = ""
            self.window.update_idletasks()
            self._on_window_resize()
        else:
            if self.manager_type == 'grid':
                self.panel.grid_forget()
            else:
                self.panel.pack_forget()
            self.button_tooltip.text = "Toggle Info Mode"

        self._update_button_icon(is_active)

    def _on_button_enter(self, event):
        self._update_button_icon(True)

    def _on_button_leave(self, event):
        self._update_button_icon(self.app_state.info_mode_active)

    def _update_button_icon(self, show_active_visuals):
        icon = None
        if show_active_visuals:
            if assets.info_icon_active and assets.info_icon_active.width() > 1:
                icon = assets.info_icon_active
                self.toggle_btn.config(image=icon, text="")
            else:
                self.toggle_btn.config(image="", text="ⓘ", fg=c.BTN_BLUE, font=(c.FONT_FAMILY_PRIMARY, 14, 'bold'))
        else:
            if assets.info_icon and assets.info_icon.width() > 1:
                icon = assets.info_icon
                self.toggle_btn.config(image=icon, text="")
            else:
                self.toggle_btn.config(image="", text="ⓘ", fg=c.TEXT_SUBTLE_COLOR, font=(c.FONT_FAMILY_PRIMARY, 14, 'bold'))

        if icon:
            self.toggle_btn.img_ref = icon

    def _update_display(self):
        """Refreshes the info text based on the priority stack."""
        # Filter out destroyed widgets from the stack to prevent help text getting stuck
        self._active_stack = [
            (w, k) for (w, k) in self._active_stack if w.winfo_exists()
        ]

        if not self._active_stack:
            self.label.config(text=INFO_MESSAGES["default"], fg=c.TEXT_SUBTLE_COLOR)
            return

        # Always show info for the most recently entered widget (top of stack)
        _, key = self._active_stack[-1]

        # Ensure wraplength is correct before updating text
        curr_w = self.window.winfo_width()
        if curr_w > 1:
            self.label.config(wraplength=curr_w - 40)

        self.label.config(text=INFO_MESSAGES[key], fg=c.TEXT_COLOR)

    def register(self, widget, key):
        """Binds Enter/Leave events to a widget to trigger info text changes."""
        if key not in INFO_MESSAGES:
            return

        def on_enter(e):
            # Check if already in stack to prevent duplicates from overlapping event firing
            if (widget, key) not in self._active_stack:
                self._active_stack.append((widget, key))
                self._update_display()

        def on_leave(e):
            if (widget, key) in self._active_stack:
                self._active_stack.remove((widget, key))
                self._update_display()

        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")

def attach_info_mode(window, app_state, manager_type, toggle_btn, grid_row=None):
    """Factory helper to link a window to the Info Mode system."""
    return InfoManager(window, app_state, manager_type, toggle_btn, grid_row)