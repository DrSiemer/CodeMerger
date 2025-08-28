import time
import os
from tkinter import messagebox, TclError
from PIL import Image, ImageTk
from .compact_mode import CompactMode
from ..core.paths import COMPACT_MODE_ICON_PATH, COMPACT_MODE_ACTIVE_ICON_PATH, COMPACT_MODE_CLOSE_ICON_PATH

class ViewManager:
    """
    Manages the visual state of the application, specifically the
    transition between the full view and compact mode
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.in_compact_mode = False
        self.is_animating = False
        self.compact_mode_window = None
        self.compact_mode_last_x = None
        self.compact_mode_last_y = None
        self.main_window_geom = None
        self.load_compact_mode_images()

    def load_compact_mode_images(self):
        """Loads and prepares the compact mode graphics"""
        try:
            button_size = (64, 64)
            up_img_src = Image.open(COMPACT_MODE_ICON_PATH).resize(button_size, Image.Resampling.LANCZOS)
            self.compact_mode_image_up = ImageTk.PhotoImage(up_img_src)
            down_img_src = Image.open(COMPACT_MODE_ACTIVE_ICON_PATH).resize(button_size, Image.Resampling.LANCZOS)
            self.compact_mode_image_down = ImageTk.PhotoImage(down_img_src)
            close_img_src = Image.open(COMPACT_MODE_CLOSE_ICON_PATH)
            self.compact_mode_close_image = ImageTk.PhotoImage(close_img_src)
        except Exception:
            self.compact_mode_image_up = None
            self.compact_mode_image_down = None
            self.compact_mode_close_image = None

    def on_main_window_restored(self, event=None):
        """
        Called when the main window is restored. If this happens while in compact
        mode, it means the user wants the main window back, so we exit compact mode.
        """
        if self.in_compact_mode and not self.is_animating:
            self.toggle_compact_mode()

    def _animate_window(self, start_time, duration, start_geom, end_geom, is_shrinking):
        """Helper method to animate the main window's geometry and alpha"""
        self.is_animating = True
        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / duration)

        start_x, start_y, start_w, start_h = start_geom
        end_x, end_y, end_w, end_h = end_geom

        curr_x = int(start_x + (end_x - start_x) * progress)
        curr_y = int(start_y + (end_y - start_y) * progress)
        curr_w = int(start_w + (end_w - start_w) * progress)
        curr_h = int(start_h + (end_h - start_h) * progress)

        alpha = 1.0 - progress if is_shrinking else progress
        if not is_shrinking and alpha == 0.0: alpha = 0.01

        self.main_window.geometry(f"{max(1, curr_w)}x{max(1, curr_h)}+{curr_x}+{curr_y}")
        try:
            self.main_window.attributes("-alpha", alpha)
        except TclError:
            pass

        if progress < 1.0:
            self.main_window.after(15, self._animate_window, start_time, duration, start_geom, end_geom, is_shrinking)
        else:
            self.is_animating = False
            if is_shrinking:
                self.main_window.withdraw()
                self.main_window.attributes("-alpha", 1.0)
                if self.compact_mode_window and self.compact_mode_window.winfo_exists():
                    self.compact_mode_window.deiconify()
            else:
                self.main_window.geometry(f"{end_geom[2]}x{end_geom[3]}+{end_geom[0]}+{end_geom[1]}")
                self.main_window.attributes("-alpha", 1.0)
                if self.compact_mode_window and self.compact_mode_window.winfo_exists():
                    self.compact_mode_window.destroy()
                self.compact_mode_window = None

    def toggle_compact_mode(self):
        """Switches the application state between main view and compact mode with animation"""
        if self.is_animating:
            return

        animation_duration = 0.25

        if self.in_compact_mode:
            self.in_compact_mode = False
            if not self.compact_mode_window or not self.compact_mode_window.winfo_exists():
                self.main_window.show_and_raise()
                return

            self.compact_mode_last_x = self.compact_mode_window.winfo_x()
            self.compact_mode_last_y = self.compact_mode_window.winfo_y()
            start_geom = (self.compact_mode_window.winfo_x(), self.compact_mode_window.winfo_y(), self.compact_mode_window.winfo_width(), self.compact_mode_window.winfo_height())
            end_geom = self.main_window_geom

            self.compact_mode_window.withdraw()
            self.main_window.deiconify()
            self.main_window.attributes("-alpha", 0.01)
            self.main_window.geometry(f"{start_geom[2]}x{start_geom[3]}+{start_geom[0]}+{start_geom[1]}")
            self._animate_window(time.time(), animation_duration, start_geom, end_geom, is_shrinking=False)
        else:
            if not self.compact_mode_image_up or not self.compact_mode_close_image:
                messagebox.showerror("Asset Error", "Could not load compact mode graphics")
                return

            self.in_compact_mode = True
            self.main_window_geom = (self.main_window.winfo_x(), self.main_window.winfo_y(), self.main_window.winfo_width(), self.main_window.winfo_height())

            active_dir = self.main_window.active_dir.get()
            project_name = os.path.basename(active_dir) if active_dir and "No project" not in active_dir else ""

            self.compact_mode_window = CompactMode(
                parent=self.main_window,
                close_callback=self.toggle_compact_mode,
                project_name=project_name,
                image_up=self.compact_mode_image_up,
                image_down=self.compact_mode_image_down,
                image_close=self.compact_mode_close_image,
                instance_color=self.main_window.project_color
            )
            self.compact_mode_window.withdraw()
            self.compact_mode_window.update_idletasks()
            widget_w, widget_h = self.compact_mode_window.winfo_reqwidth(), self.compact_mode_window.winfo_reqheight()

            if self.compact_mode_last_x is not None and self.compact_mode_last_y is not None:
                target_x, target_y = self.compact_mode_last_x, self.compact_mode_last_y
            else:
                screen_w, screen_h = self.main_window.winfo_screenwidth(), self.main_window.winfo_screenheight()
                main_x, main_y, main_w, _ = self.main_window_geom
                ideal_x, ideal_y = main_x + main_w - widget_w - 20, main_y + 20
                margin = 10
                target_x = max(margin, min(ideal_x, screen_w - widget_w - margin))
                target_y = max(margin, min(ideal_y, screen_h - widget_h - margin))

            start_geom, end_geom = self.main_window_geom, (target_x, target_y, widget_w, widget_h)
            self.compact_mode_window.geometry(f"+{target_x}+{target_y}")
            self._animate_window(time.time(), animation_duration, start_geom, end_geom, is_shrinking=True)