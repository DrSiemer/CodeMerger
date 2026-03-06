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

        # Force absolute zero padding on the button widget itself to touch window borders
        self.toggle_btn.config(borderwidth=0, highlightthickness=0, padx=0, pady=0)

        self._active_stack = []

        # --- Info Panel ---
        self.panel = tk.Frame(
            window, bg=c.INFO_PANEL_BG, height=self.panel_height,
            highlightbackground=c.WRAPPER_BORDER, highlightthickness=1
        )
        self.panel.pack_propagate(False)

        # Robust initial width estimation
        initial_w = window.winfo_width()
        if initial_w <= 1: initial_w = window.winfo_reqwidth()
        if initial_w <= 1: initial_w = 400

        self.label = tk.Label(
            self.panel, text=INFO_MESSAGES["default"],
            bg=c.INFO_PANEL_BG, fg=c.TEXT_SUBTLE_COLOR,
            font=c.FONT_INFO_PANEL, justify="left",
            wraplength=initial_w - 40, anchor="w"
        )
        self.label.pack(side="left", padx=10, fill="both", expand=True)

        self.button_tooltip = ToolTip(self.toggle_btn, text="Toggle Info Mode")

        # --- Toggle Button Configuration ---
        self.toggle_btn.bind("<Button-1>", lambda e: self.app_state.toggle_info_mode())
        self.toggle_btn.bind("<Enter>", self._on_button_enter, add="+")
        self.toggle_btn.bind("<Leave>", self._on_button_leave, add="+")

        # Re-calculate wraplength whenever the window size is updated.
        self.window.bind("<Configure>", self._on_window_resize, add="+")
        self.app_state.register_info_observer(self.refresh_visibility)

        self.is_initialized = False
        self._apply_visibility_ui(self.app_state.info_mode_active)
        self.is_initialized = True

    def clear_active_stack(self):
        """Forcefully clears the hover stack. Call this before destroying widgets in the Wizard."""
        self._active_stack = []
        self._update_display()

    def _on_window_resize(self, event=None):
        """Updates the wraplength to ensure help text uses the available panel width."""
        if self.panel.winfo_ismapped():
            w = self.window.winfo_width()
            if w > 1:
                self.label.config(wraplength=w - 40)

    def _adjust_window_height(self, expand: bool):
        """Physically resizes the window to accommodate the panel appearance."""
        if not self.window.winfo_exists(): return
        self.window.update_idletasks()
        geom = self.window.geometry()
        match = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
        if not match: return
        w, h, x, y = map(int, match.groups())
        new_h = h + self.panel_height if expand else h - self.panel_height
        self.window.geometry(f"{w}x{new_h}+{x}+{y}")

    def refresh_visibility(self, is_active):
        """Global callback to sync visibility and window size."""
        self._apply_visibility_ui(is_active)
        if self.is_initialized: self._adjust_window_height(expand=is_active)

    def _apply_visibility_ui(self, is_active):
        """
        Updates the panel visibility and shifts the toggle button to sit
        exactly flush with the left border, jumping above the panel when active.
        """
        if is_active:
            if self.manager_type == 'grid': self.panel.grid(row=self.grid_row, column=0, sticky="ew")
            else: self.panel.pack(side="bottom", fill="x")
            self.button_tooltip.text = ""
            # Button sits on top of the panel, flush with left window border (x=0)
            self.toggle_btn.place(x=0, rely=1.0, y=-self.panel_height, anchor='sw')
        else:
            if self.manager_type == 'grid': self.panel.grid_forget()
            else: self.panel.pack_forget()
            self.button_tooltip.text = "Toggle Info Mode"
            # Button sits at absolute bottom left corner (x=0)
            self.toggle_btn.place(x=0, rely=1.0, y=0, anchor='sw')

        self.toggle_btn.lift()
        # Like Settings/Filetypes, the resting icon is always the standard one
        self._update_button_icon(False)

    def _on_button_enter(self, event):
        # On hover, always swap to the active (blue) icon
        self._update_button_icon(True)

    def _on_button_leave(self, event):
        # On leave, always return to the standard (gray) icon
        self._update_button_icon(False)

    def _update_button_icon(self, show_active_visuals):
        """Swaps the PhotoImage on the toggle button label."""
        icon = assets.info_icon_active if show_active_visuals else assets.info_icon
        if icon:
            self.toggle_btn.config(image=icon, text="")
            # Keep internal reference to prevent garbage collection
            self.toggle_btn.img_ref = icon
            # Force immediate redraw for responsiveness
            self.toggle_btn.update_idletasks()

    def _update_display(self):
        """Updates the label text and enforces wraplength."""
        self._active_stack = [ (w, k) for (w, k) in self._active_stack if w.winfo_exists() ]
        if not self._active_stack:
            self.label.config(text=INFO_MESSAGES["default"], fg=c.TEXT_SUBTLE_COLOR)
            return

        _, key = self._active_stack[-1]

        # Sync width before showing new text to avoid wrap artifacts
        w = self.window.winfo_width()
        if w > 1:
            self.label.config(wraplength=w - 40)

        self.label.config(text=INFO_MESSAGES[key], fg=c.TEXT_COLOR)

    def register(self, widget, key):
        """Binds Enter/Leave events to a widget to trigger info text changes."""
        if key not in INFO_MESSAGES: return
        widget.bind("<Enter>", lambda e: (self._active_stack.append((widget, key)), self._update_display()), add="+")
        widget.bind("<Leave>", lambda e: ((widget, key) in self._active_stack and self._active_stack.remove((widget, key)), self._update_display()), add="+")

def attach_info_mode(window, app_state, manager_type, toggle_btn, grid_row=None):
    """Factory helper to link a window to the Info Mode system."""
    return InfoManager(window, app_state, manager_type, toggle_btn, grid_row)