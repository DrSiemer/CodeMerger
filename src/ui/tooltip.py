import tkinter as tk
from .. import constants as c

class ToolTip:
    """
    A simple tooltip class for tkinter widgets.
    Creates a toplevel window with a label to display help text.
    """
    def __init__(self, widget, text, delay=0):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.delay = delay
        self._show_job = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        self.schedule_show()

    def on_leave(self, event=None):
        self.cancel_show()
        self.hide_tooltip()

    def schedule_show(self):
        self.cancel_show()
        self._show_job = self.widget.after(self.delay, self.show_tooltip)

    def cancel_show(self):
        if self._show_job:
            self.widget.after_cancel(self._show_job)
            self._show_job = None

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify='left',
            background=c.TOP_BAR_BG,
            fg=c.TEXT_COLOR,
            relief='solid',
            borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None