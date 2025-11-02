import tkinter as tk
from .. import constants as c

class CompactStatusToast(tk.Toplevel):
    """
    A temporary, frameless window that displays a status message below its
    parent widget (the compact mode window) and then fades out.
    """
    def __init__(self, parent_widget, message):
        super().__init__(parent_widget)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(bg=c.STATUS_BG, padx=10, pady=5)
        self.attributes("-alpha", 0.0) # Start transparent for fade-in

        label = tk.Label(
            self, text=message, bg=c.STATUS_BG, fg=c.STATUS_FG,
            font=c.FONT_STATUS_BAR, justify='left',
            wraplength=parent_widget.winfo_width()
        )
        label.pack()

        # [FIX] Force an update of the parent's geometry before calculating position
        parent_widget.update_idletasks()
        parent_x = parent_widget.winfo_x()
        parent_y = parent_widget.winfo_y()
        parent_h = parent_widget.winfo_height()

        x = parent_x
        y = parent_y + parent_h + 2
        self.geometry(f"+{x}+{y}")

        self.fade_in()
        # Schedule fade out based on the standard status bar duration
        fade_delay_ms = int((c.STATUS_FADE_SECONDS - 0.5) * 1000)
        self.after(fade_delay_ms, self.fade_out)

    def fade_in(self):
        """Gradually increases the window's alpha to 1.0."""
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.15
            self.attributes("-alpha", min(1.0, alpha))
            self.after(20, self.fade_in)

    def fade_out(self):
        """Gradually decreases the window's alpha to 0.0 and then destroys it."""
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            alpha -= 0.1
            self.attributes("-alpha", max(0.0, alpha))
            self.after(50, self.fade_out)
        else:
            self.destroy()