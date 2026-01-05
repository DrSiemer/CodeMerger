import time
import os
from tkinter import messagebox, Toplevel
from .compact_mode import CompactMode
from .assets import assets
from .window_utils import get_monitor_work_area
from .. import constants as c

class ViewManager:
    """
    Manages the visual state of the application, specifically the
    transition between the full view and compact mode using a state machine
    to animate correctly while avoiding OS window manager race conditions.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        # State machine states
        self.STATE_NORMAL = 'normal'
        self.STATE_SHRINKING = 'shrinking'
        self.STATE_COMPACT = 'compact'
        self.STATE_GROWING = 'growing'
        self.current_state = self.STATE_NORMAL

        self.compact_mode_window = None
        self.compact_mode_last_x = None
        self.compact_mode_last_y = None
        self.main_window_geom = None

    def on_main_window_minimized(self, event=None):
        """
        Called when the main window is unmapped (minimized).
        """
        # Only start transition if we are in normal state and setting is enabled.
        if self.current_state == self.STATE_NORMAL and self.main_window.app_state.enable_compact_mode_on_minimize:
            # We use a small delay to ensure the OS has finished processing the
            # minimization state before we attempt to deiconify and animate.
            def check_and_transition():
                # Double-check state inside the timer to prevent race conditions
                # causing double animations.
                if self.current_state == self.STATE_NORMAL and self.main_window.state() == 'iconic':
                    self.transition_to_compact()

            self.main_window.after(50, check_and_transition)

    def on_main_window_restored(self, event=None):
        """
        Called when the main window is restored (e.g., from the taskbar).
        """
        if self.current_state == self.STATE_COMPACT:
            self.transition_to_normal()

    def exit_compact_mode_manually(self):
        """
        A dedicated method for when the user closes the compact window directly.
        """
        if self.current_state == self.STATE_COMPACT:
            self.transition_to_normal()

    def on_compact_mode_moved(self):
        """Callback executed when the compact mode window is moved by the user."""
        if self.compact_mode_window and self.compact_mode_window.winfo_exists():
            self.compact_mode_last_x = self.compact_mode_window.winfo_x()
            self.compact_mode_last_y = self.compact_mode_window.winfo_y()

    def invalidate_compact_mode_position(self):
        """Forgets the last position, forcing recalculation on the next compact transition."""
        self.compact_mode_last_x = None
        self.compact_mode_last_y = None

    def _animate_window(self, start_time, duration, start_geom, end_geom, is_shrinking):
        """Helper method to animate the main window's geometry and alpha with easing."""
        if not self.main_window.winfo_exists():
            return

        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / duration)
        # Cubic easing for smoother start/stop
        eased_progress = progress * progress * (3.0 - 2.0 * progress)

        start_x, start_y, start_w, start_h = start_geom
        end_x, end_y, end_w, end_h = end_geom

        curr_x = int(start_x + (end_x - start_x) * eased_progress)
        curr_y = int(start_y + (end_y - start_y) * eased_progress)
        curr_w = int(start_w + (end_w - start_w) * eased_progress)
        curr_h = int(start_h + (end_h - start_h) * eased_progress)

        alpha = 1.0 - progress if is_shrinking else progress
        # Ensure window is never quite 0 alpha while visible to avoid some OS glitches
        if not is_shrinking and alpha < 0.01: alpha = 0.01

        try:
            self.main_window.geometry(f"{max(1, curr_w)}x{max(1, curr_h)}+{curr_x}+{curr_y}")
            self.main_window.attributes("-alpha", alpha)
        except Exception:
            pass

        if progress < 1.0:
            self.main_window.after(15, self._animate_window, start_time, duration, start_geom, end_geom, is_shrinking)
        else:
            self._on_animation_complete(is_shrinking, end_geom)

    def _on_animation_complete(self, is_shrinking, final_geom):
        """Handles state changes after an animation finishes."""
        if is_shrinking:
            # Restore main window to full size/buffer before officially hiding it.
            # This ensures the taskbar thumbnail reflects the full app, not a shrunken sliver.
            if self.main_window_geom:
                w, h, x, y = self.main_window_geom[2], self.main_window_geom[3], self.main_window_geom[0], self.main_window_geom[1]
                self.main_window.geometry(f"{w}x{h}+{x}+{y}")
                self.main_window.attributes("-alpha", 0.01)
                self.main_window.update()

            self.main_window.iconify()
            if self.compact_mode_window and self.compact_mode_window.winfo_exists():
                self.compact_mode_window.deiconify()
                self.compact_mode_window.lift()
            self.current_state = self.STATE_COMPACT
        else:
            self.main_window.geometry(f"{final_geom[2]}x{final_geom[3]}+{final_geom[0]}+{final_geom[1]}")
            self.main_window.attributes("-alpha", 1.0)
            self.main_window.minsize(c.MIN_WINDOW_WIDTH, c.MIN_WINDOW_HEIGHT)
            if self.compact_mode_window and self.compact_mode_window.winfo_exists():
                self.compact_mode_window.destroy()
                self.compact_mode_window = None
            self.current_state = self.STATE_NORMAL

    def transition_to_compact(self):
        """Starts the process of shrinking the main window and showing the compact view."""
        if self.current_state != self.STATE_NORMAL:
            return

        self.current_state = self.STATE_SHRINKING

        # Capture current geometry immediately before we start messing with transparency/state
        self.main_window_geom = (
            self.main_window.winfo_x(), self.main_window.winfo_y(),
            self.main_window.winfo_width(), self.main_window.winfo_height()
        )

        # Make transparent and deiconify to take control of the animation
        self.main_window.attributes("-alpha", 0.0)
        self.main_window.deiconify()

        self.main_window.after(c.ANIMATION_START_DELAY_MS, self._start_shrink_animation)

    def _start_shrink_animation(self):
        """The actual animation logic for shrinking."""
        if not self.main_window.winfo_exists(): return

        start_geom = self.main_window_geom
        self.main_window.attributes("-alpha", 1.0)
        self.main_window.minsize(1, 1)

        self._prepare_compact_mode_window()
        # Force the compact window to calculate its dimensions so we have an accurate target
        self.compact_mode_window.update_idletasks()
        widget_w = self.compact_mode_window.winfo_reqwidth()
        widget_h = self.compact_mode_window.winfo_reqheight()

        use_saved_position = self.compact_mode_last_x is not None

        if use_saved_position:
            target_x, target_y = self.compact_mode_last_x, self.compact_mode_last_y
        else:
            mon_x, mon_y, mon_right, mon_bottom = get_monitor_work_area(self.main_window)
            main_x, main_y, main_w, _ = start_geom

            # Default placement: Top right of the main window area
            ideal_x, ideal_y = main_x + main_w - widget_w - 20, main_y + 20
            margin = 10

            target_x = max(mon_x + margin, min(ideal_x, mon_right - widget_w - margin))
            target_y = max(mon_y + margin, min(ideal_y, mon_bottom - widget_h - margin))

        end_geom = (target_x, target_y, widget_w, widget_h)

        # Position the compact window but keep it hidden until animation is done
        self.compact_mode_window.geometry(f"+{target_x}+{target_y}")
        self.compact_mode_window.withdraw()

        self._animate_window(time.time(), c.ANIMATION_DURATION_SECONDS, start_geom, end_geom, is_shrinking=True)

    def transition_to_normal(self):
        """Starts the process of growing the main window back to its normal state."""
        if self.current_state != self.STATE_COMPACT:
            return

        if not self.compact_mode_window or not self.compact_mode_window.winfo_exists():
            self.current_state = self.STATE_NORMAL
            self.main_window.show_and_raise()
            return

        self.current_state = self.STATE_GROWING

        # Save last known good position
        self.compact_mode_last_x = self.compact_mode_window.winfo_x()
        self.compact_mode_last_y = self.compact_mode_window.winfo_y()

        start_geom = (self.compact_mode_last_x, self.compact_mode_last_y, self.compact_mode_window.winfo_width(), self.compact_mode_window.winfo_height())

        # Fallback if main geometry was lost
        if not self.main_window_geom:
            self.main_window_geom = (100, 100, 660, 360)

        end_geom = self.main_window_geom

        self.compact_mode_window.withdraw()

        self.main_window.attributes("-alpha", 0.0)
        self.main_window.deiconify()
        self.main_window.geometry(f"{start_geom[2]}x{start_geom[3]}+{start_geom[0]}+{start_geom[1]}")

        self._animate_window(time.time(), c.ANIMATION_DURATION_SECONDS, start_geom, end_geom, is_shrinking=False)

    def _prepare_compact_mode_window(self):
        """Creates the CompactMode Toplevel window and configures it."""
        if self.compact_mode_window and self.compact_mode_window.winfo_exists():
             self.compact_mode_window.destroy()

        project_name = "CodeMerger"
        has_wrapper_text = False
        project_font_color_name = 'light'
        project_config = self.main_window.project_manager.get_current_project()

        if project_config:
            project_name = project_config.project_name
            project_font_color_name = project_config.project_font_color
            if project_config.intro_text or project_config.outro_text:
                has_wrapper_text = True

        self.compact_mode_window = CompactMode(
            parent=self.main_window,
            close_callback=self.exit_compact_mode_manually,
            on_move_callback=self.on_compact_mode_moved,
            project_name=project_name,
            instance_color=self.main_window.project_color,
            font_color_name=project_font_color_name,
            show_wrapped_button=has_wrapper_text
        )
        self.main_window.file_monitor._update_warning_ui()
        self.compact_mode_window.withdraw()