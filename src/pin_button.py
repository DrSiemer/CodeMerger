from tkinter import Toplevel, Frame, Label
try:
    from PIL import Image, ImageTk
except ImportError:
    pass

class PinButton(Toplevel):
    """A borderless window with a dedicated drag bar and a separate action button."""
    def __init__(self, parent, on_close_callback, image_up, image_down):
        super().__init__(parent)
        self.on_close_callback = on_close_callback
        self.image_up = image_up
        self.image_down = image_down
        self.offset_x = 0
        self.offset_y = 0

        # --- Window Chrome and Style ---
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # --- Set Window Geometry ---
        button_size = (64, 64)
        drag_bar_height = 14
        window_width = button_size[0]
        window_height = button_size[1] + drag_bar_height
        self.geometry(f"{window_width}x{window_height}")

        # Drag Bar
        self.drag_bar = Frame(self, height=drag_bar_height, bg='#cccccc')
        self.drag_bar.pack(side='top', fill='x')

        # Icon Button
        self.icon_label = Label(self, image=self.image_up, borderwidth=0)
        self.icon_label.pack(side='bottom')

        # --- Bind Events to the Correct Widgets ---
        self.drag_bar.bind("<ButtonPress-1>", self.start_drag)
        self.drag_bar.bind("<B1-Motion>", self.do_drag)
        self.drag_bar.bind("<Double-Button-1>", self.on_double_click)

        self.icon_label.bind("<ButtonPress-1>", self.on_button_press)
        self.icon_label.bind("<ButtonRelease-1>", self.on_button_release)

        self.withdraw()

    def start_drag(self, event):
        """Records the initial click position on the drag bar."""
        self.offset_x = event.x
        self.offset_y = event.y

    def do_drag(self, event):
        """Moves the entire window when the drag bar is moved."""
        new_x = self.winfo_pointerx() - self.offset_x
        new_y = self.winfo_pointery() - self.offset_y
        self.geometry(f"+{new_x}+{new_y}")

    def on_double_click(self, event):
        """Tells the main app window to show itself."""
        self.master.show_and_raise()

    def on_button_press(self, event):
        """When the icon is pressed, show the 'down' image if enabled."""
        if self.master.copy_merged_button['state'] == 'normal':
            self.icon_label.config(image=self.image_down)

    def on_button_release(self, event):
        """When the icon is released, revert to 'up' image and copy if enabled."""
        self.icon_label.config(image=self.image_up)
        if self.master.copy_merged_button['state'] == 'normal':
            self.master.copy_merged_code()