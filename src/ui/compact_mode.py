import tkinter as tk
from ..constants import COMPACT_MODE_BG_COLOR

class CompactMode(tk.Toplevel):
    """
    A frameless, always-on-top, draggable window that acts as a button.
    It provides a compact, always-on-top interface while the main window is hidden.
    It features a move bar for dragging, a close button, and the main copy button.
    Double-clicking the move bar or clicking the close button will close this
    window and restore the main application window.
    """
    def __init__(self, parent, close_callback, project_name, image_up=None, image_down=None, image_close=None):
        super().__init__(parent)
        self.parent = parent
        self.close_callback = close_callback
        self.project_name = project_name
        self.image_up = image_up
        self.image_down = image_down
        self.image_close = image_close
        self.tooltip_window = None

        # --- Style and Layout Constants ---
        BAR_AND_BORDER_COLOR = COMPACT_MODE_BG_COLOR
        BORDER_WIDTH = 1
        MOVE_BAR_HEIGHT = 14

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

        # --- Close Button ---
        self.close_button = tk.Label(
            self.move_bar,
            image=self.image_close,
            bg=BAR_AND_BORDER_COLOR,
            cursor="hand2"
        )
        self.close_button.pack(side='right', padx=(0, 1))


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

        # --- Tiny "Copy Wrapped" Button ---
        self.wrapped_button = tk.Button(
            border_frame,
            text="W",
            font=('Helvetica', 8, 'bold'),
            bg="white",
            fg="black",
            bd=1,
            relief="solid",
            cursor="hand2",
            command=self.copy_wrapped
        )
        # Place the button in the bottom-right corner, on top of the main button area
        self.wrapped_button.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor='se', width=18, height=18)


        # --- Bindings ---
        # Drag functionality is bound to the move bar
        self.move_bar.bind("<ButtonPress-1>", self.on_press_drag)
        self.move_bar.bind("<B1-Motion>", self.on_drag)

        # Close functionality is bound to the move bar (double-click) and close button (single-click)
        self.move_bar.bind("<Double-Button-1>", self.close_window)
        self.close_button.bind("<Button-1>", self.close_window)

        # Click functionality is bound ONLY to the button image
        self.button_label.bind("<ButtonPress-1>", self.on_press_click)
        self.button_label.bind("<ButtonRelease-1>", self.on_release_click)

        # Tooltip functionality
        self.bind("<Enter>", self.show_tooltip)
        self.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.project_name:
            return
        x = self.winfo_rootx() + self.winfo_width() // 2
        y = self.winfo_rooty() + self.winfo_height() + 5

        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.project_name, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
        # Center tooltip below the widget
        self.tooltip_window.update_idletasks()
        new_x = x - (self.tooltip_window.winfo_width() // 2)
        self.tooltip_window.wm_geometry(f"+{new_x}+{y}")


    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

    def close_window(self, event=None):
        """Signals the parent app to close this window and show the main one."""
        if self.close_callback:
            self.close_callback()

    def copy_wrapped(self):
        """Triggers the parent's copy_wrapped_code function with visual feedback."""
        self.wrapped_button.config(relief="sunken")
        self.parent.copy_wrapped_code()
        self.after(100, lambda: self.wrapped_button.config(relief="solid"))

    def on_press_drag(self, event):
        """Records the initial click position on the move bar."""
        self._offset_x = event.x
        self._offset_y = event.y

    def on_drag(self, event):
        """Moves the window based on the mouse's motion."""
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

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