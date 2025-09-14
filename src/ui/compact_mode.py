import tkinter as tk
from .. import constants as c
from ..core.paths import NEW_FILES_ICON_PATH
from PIL import Image, ImageTk

class CompactMode(tk.Toplevel):
    """
    A frameless, always-on-top, draggable window that acts as a button.
    It provides a compact, always-on-top interface while the main window is hidden.
    It features a move bar for dragging, a close button, and the main copy button.
    Double-clicking the move bar or clicking the close button will close this
    window and restore the main application window.
    """
    def __init__(self, parent, close_callback, project_name, image_up_pil, image_down_pil, image_up_tk, image_down_tk, image_close, instance_color=c.COMPACT_MODE_BG_COLOR, font_color_name='light', show_wrapped_button=False):
        super().__init__(parent)
        self.parent = parent
        self.close_callback = close_callback
        self.project_name = project_name

        # Store original images (both PIL for composing and Tk for displaying)
        self.image_up_pil = image_up_pil
        self.image_down_pil = image_down_pil
        self.image_up_tk_orig = image_up_tk
        self.image_down_tk_orig = image_down_tk

        self.image_close = image_close
        self.tooltip_window = None
        self.instance_color = instance_color
        self.new_files_pil_img = None
        self.is_showing_warning = False

        # Generated images for the warning state
        self.image_up_tk_warning = None
        self.image_down_tk_warning = None

        # --- Style and Layout Constants ---
        BAR_AND_BORDER_COLOR = self.instance_color # Use the passed-in color
        BORDER_WIDTH = 1
        MOVE_BAR_HEIGHT = 14
        text_hex_color = c.TEXT_COLOR if font_color_name == 'light' else '#000000'

        # --- Window Configuration ---
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(bg=BAR_AND_BORDER_COLOR)

        # --- Internal State for Dragging ---
        self._offset_x = 0
        self._offset_y = 0
        self._is_dragging = False

        # --- Move Bar (for dragging and double-click) ---
        self.move_bar = tk.Frame(self, height=MOVE_BAR_HEIGHT, bg=BAR_AND_BORDER_COLOR, cursor="fleur")
        self.move_bar.pack(fill='x', side='top')

        # Add project title abbreviation
        no_space_title = project_name.replace(' ', '')
        title_abbr = no_space_title[:5]
        self.title_label = tk.Label(
            self.move_bar,
            text=title_abbr,
            bg=BAR_AND_BORDER_COLOR,
            fg=text_hex_color,
            font=('Segoe UI', 8)
        )
        self.title_label.pack(side='left', padx=(4, 0))

        # --- Close Button ---
        self.close_button = tk.Label(self.move_bar, image=self.image_close, bg=BAR_AND_BORDER_COLOR, cursor="hand2")
        self.close_button.pack(side='right', padx=(0, 1))

        # --- Border Frame ---
        border_frame = tk.Frame(self, bg=BAR_AND_BORDER_COLOR)
        border_frame.pack(side='bottom', fill='both', expand=True)

        # --- Button (for clicking) ---
        self.button_label = tk.Label(border_frame, image=self.image_up_tk_orig, bd=0, bg='white')
        self.button_label.pack(padx=(BORDER_WIDTH, BORDER_WIDTH), pady=(0, BORDER_WIDTH))

        # --- Tiny "Copy Wrapped" Button ---
        self.wrapped_button = tk.Button(
            border_frame, text="W", font=('Segoe UI', 8, 'bold'),
            bg="#FFFFFF", fg="#000000", activebackground=c.SUBTLE_HIGHLIGHT_COLOR, activeforeground="#FFFFFF",
            bd=0, relief="flat", cursor="hand2", command=self.copy_wrapped
        )
        if show_wrapped_button:
            self.wrapped_button.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor='se', width=18, height=18)

        # --- Load new files icon (PIL only) ---
        try:
            self.new_files_pil_img = Image.open(NEW_FILES_ICON_PATH).resize((28, 28), Image.Resampling.LANCZOS)
        except Exception:
            self.new_files_pil_img = None

        # --- Bindings ---
        self.move_bar.bind("<ButtonPress-1>", self.on_press_drag)
        self.move_bar.bind("<B1-Motion>", self.on_drag)
        self.move_bar.bind("<ButtonRelease-1>", self.on_release_drag)
        self.move_bar.bind("<Double-Button-1>", self.close_window)
        self.title_label.bind("<ButtonPress-1>", self.on_press_drag)
        self.title_label.bind("<B1-Motion>", self.on_drag)
        self.title_label.bind("<ButtonRelease-1>", self.on_release_drag)
        self.title_label.bind("<Double-Button-1>", self.close_window)
        self.close_button.bind("<Button-1>", self.close_window)
        self.button_label.bind("<ButtonPress-1>", self.on_press_click)
        self.button_label.bind("<ButtonRelease-1>", self.on_release_click)
        self.button_label.bind("<Enter>", self.show_tooltip)
        self.button_label.bind("<Leave>", self.hide_tooltip)

        if show_wrapped_button:
            self.wrapped_button.bind("<Enter>", lambda e: self.show_tooltip(text=f"Copy wrapped {self.project_name} code"))
            self.wrapped_button.bind("<Leave>", self.hide_tooltip)

    def _create_warning_images(self):
        """Composites the warning icon onto the button images."""
        if not self.new_files_pil_img or not self.image_up_pil or not self.image_down_pil:
            return

        # Create "up" state with warning
        up_composite = self.image_up_pil.copy()
        up_composite.paste(self.new_files_pil_img, (4, 4), self.new_files_pil_img)
        self.image_up_tk_warning = ImageTk.PhotoImage(up_composite)

        # Create "down" state with warning
        down_composite = self.image_down_pil.copy()
        down_composite.paste(self.new_files_pil_img, (4, 4), self.new_files_pil_img)
        self.image_down_tk_warning = ImageTk.PhotoImage(down_composite)

    def show_warning(self, file_count, project_name):
        self.is_showing_warning = True
        self.project_name = project_name

        if not self.image_up_tk_warning:
            self._create_warning_images()

        if self.image_up_tk_warning:
            self.button_label.config(image=self.image_up_tk_warning)

    def hide_warning(self, project_name):
        self.is_showing_warning = False
        self.project_name = project_name
        self.button_label.config(image=self.image_up_tk_orig)

    def show_tooltip(self, event=None, text=""):
        if self._is_dragging or self.tooltip_window:
            return

        base_message = text or f"Copy {self.project_name} code"
        text_to_show = base_message

        if self.is_showing_warning:
            count = len(self.parent.file_monitor.newly_detected_files)
            file_str = "file" if count == 1 else "files"
            warning_part = f" - {count} new {file_str} found!"
            text_to_show += warning_part

        if not text_to_show: return

        x = self.winfo_rootx() + self.winfo_width() // 2
        y = self.winfo_rooty() + self.winfo_height() + 5

        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=text_to_show, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=4, ipady=2)
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
        original_bg = self.wrapped_button.cget('bg')
        self.wrapped_button.config(bg=c.SUBTLE_HIGHLIGHT_COLOR)
        self.parent.copy_wrapped_code()
        self.after(150, lambda: self.wrapped_button.config(bg=original_bg))

    def on_press_drag(self, event):
        """Records the initial click position on the move bar."""
        self._is_dragging = True
        self.hide_tooltip()
        self._offset_x = event.x
        self._offset_y = event.y

    def on_drag(self, event):
        """Moves the window based on the mouse's motion."""
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def on_release_drag(self, event):
        """Resets the dragging state when the mouse is released."""
        self._is_dragging = False

    def on_press_click(self, event):
        """Changes the button image to its 'pressed' state."""
        if self.is_showing_warning and self.image_down_tk_warning:
            self.button_label.config(image=self.image_down_tk_warning)
        else:
            self.button_label.config(image=self.image_down_tk_orig)

    def on_release_click(self, event):
        """Restores the button image and triggers the copy action."""
        if self.is_showing_warning and self.image_up_tk_warning:
            self.button_label.config(image=self.image_up_tk_warning)
        else:
            self.button_label.config(image=self.image_up_tk_orig)

        self.parent.copy_merged_code()