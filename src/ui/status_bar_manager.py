import time
from .. import constants as c

class StatusBarManager:
    """Manages the behavior and fading animation of the main status bar."""
    def __init__(self, app, status_bar_widget, status_var):
        self.app = app
        self.status_bar = status_bar_widget
        self.status_var = status_var
        self._status_fade_job = None
        self._is_clearing_status = False # Flag to prevent feedback loops
        self.status_var.trace_add('write', self._on_status_update)

    def _interpolate_color(self, start_hex, end_hex, progress):
        """Linearly interpolates between two hex colors."""
        start_r, start_g, start_b = int(start_hex[1:3], 16), int(start_hex[3:5], 16), int(start_hex[5:7], 16)
        end_r, end_g, end_b = int(end_hex[1:3], 16), int(end_hex[3:5], 16), int(end_hex[5:7], 16)

        r = int(start_r + (end_r - start_r) * progress)
        g = int(start_g + (end_g - start_g) * progress)
        b = int(start_b + (end_b - start_b) * progress)

        return f"#{r:02x}{g:02x}{b:02x}"

    def _start_status_fade(self):
        """Kicks off the fade animation."""
        start_time = time.time()
        duration = 0.5  # Fade over half a second
        self._fade_status_step(start_time, duration)

    def _fade_status_step(self, start_time, duration):
        """A single step in the fade animation."""
        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / duration)

        new_color = self._interpolate_color(c.STATUS_FG, c.STATUS_BG, progress)
        self.status_bar.config(fg=new_color)

        if progress < 1.0:
            self._status_fade_job = self.app.after(20, self._fade_status_step, start_time, duration)
        else:
            # Once fully faded, clear the text and reset the color for the next message
            self._is_clearing_status = True
            self.status_var.set("")
            self.status_bar.config(fg=c.STATUS_FG)
            self._is_clearing_status = False
            self._status_fade_job = None

    def _on_status_update(self, *args):
        """When the status text changes, this resets its visibility and schedules the fade-out."""
        if self._is_clearing_status:
            return  # Ignore updates triggered by the fade-out process itself

        # If a fade is already in progress, cancel it.
        if self._status_fade_job:
            self.app.after_cancel(self._status_fade_job)
            self._status_fade_job = None

        # Always reset the color to full visibility when a new message arrives.
        self.status_bar.config(fg=c.STATUS_FG)

        current_message = self.status_var.get()

        # If the new message is not empty, schedule it to start fading out.
        if current_message and current_message.strip():
            # Set a delay, after which the fade will begin.
            fade_delay_ms = int((c.STATUS_FADE_SECONDS - 0.5) * 1000)
            self._status_fade_job = self.app.after(fade_delay_ms, self._start_status_fade)