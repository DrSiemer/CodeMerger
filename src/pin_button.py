import tkinter as tk
from .constants import PINBUTTON_BG_COLOR

class PinButton(tk.Toplevel):
    """
    A frameless, always-on-top, draggable window that acts as a button.
    It features a separate move bar at the top to prevent accidental clicks
    when repositioning the window. Double-clicking the move bar brings the
    main application window into focus.

    A border is added to the left, right, and bottom of the button graphic,
    using the same color as the move bar.
    """
    def __init__(self, parent, on_close_callback=None, image_up=None, image_down=None):
        super().__init__(parent)
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.image_up = image_up
        self.image_down = image_down

        # --- Style and Layout Constants ---
        BAR_AND_BORDER_COLOR = PINBUTTON_BG_COLOR
        BORDER_WIDTH = 1
        MOVE_BAR_HEIGHT = 8

        # --- Window Configuration ---
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(bg=BAR_AND_BORDER_COLOR)

        # --- Internal State for Dragging ---
        self._offset_x = 0
        self._offset_y = 0

        # --- Move Bar (for dragging and double-click) ---
        self.move_bar = tk.Frame(
            self,
            height=MOVE_BAR_HEIGHT,
            bg=BAR_AND_BORDER_COLOR,
            cursor="fleur"
        )
        self.move_bar.pack(fill='x', side='top')

        # --- Border Frame ---
        border_frame = tk.Frame(self, bg=BAR_AND_BORDER_COLOR)
        border_frame.pack(side='bottom', fill='both', expand=True)

        # --- Button (for clicking) ---
        self.button_label = tk.Label(
            border_frame,
            image=self.image_up,
            bd=0,
            bg='white'
        )
        self.button_label.pack(
            padx=(BORDER_WIDTH, BORDER_WIDTH),
            pady=(0, BORDER_WIDTH)
        )

        # --- Bindings ---
        # Drag functionality is bound to the move bar
        self.move_bar.bind("<ButtonPress-1>", self.on_press_drag)
        self.move_bar.bind("<B1-Motion>", self.on_drag)
        # Double-click to focus main window is bound ONLY to the move bar
        self.move_bar.bind("<Double-Button-1>", self.on_double_click_bar)
        # Click functionality is bound ONLY to the button image
        self.button_label.bind("<ButtonPress-1>", self.on_press_click)
        self.button_label.bind("<ButtonRelease-1>", self.on_release_click)

    def on_press_drag(self, event):
        """Records the initial click position on the move bar."""
        self._offset_x = event.x
        self._offset_y = event.y

    def on_drag(self, event):
        """Moves the window based on the mouse's motion."""
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def on_double_click_bar(self, event):
        """Brings the main application window to the front."""
        self.parent.show_and_raise()

    def on_press_click(self, event):
        """Changes the button image to its 'pressed' state."""
        if self.image_down:
            self.button_label.config(image=self.image_down)

    def on_release_click(self, event):
        """Restores the button image and triggers the copy action."""
        if self.image_up:
            self.button_label.config(image=self.image_up)
        # Trigger the main app's copy function. Does NOT change focus.
        self.parent.copy_merged_code()

    def destroy(self):
        """Overrides destroy to call the callback if one is provided."""
        if self.on_close_callback:
            self.on_close_callback()
        super().destroy()