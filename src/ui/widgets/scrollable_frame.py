import tkinter as tk
from tkinter import ttk

class ScrollableFrame(tk.Frame):
    """
    A reusable frame that contains a scrollable area.
    Widgets should be added to the `self.scrollable_frame` attribute.
    """
    def __init__(self, parent, *args, **kwargs):
        bg_color = kwargs.get('bg', parent.cget('bg'))
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<MouseWheel>", self._on_mousewheel)
        # Propagate mousewheel events from all children to this widget
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel, add=True)

    def _on_frame_configure(self, event=None):
        # Update the scrollable area when the inner frame's size changes
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._manage_scrollbar()

    def _on_canvas_configure(self, event=None):
        # Ensure the inner frame always fills the width of the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._manage_scrollbar()

    def _on_mousewheel(self, event):
        # Prevent this widget from scrolling if the cursor is over a child Text widget
        widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)
        w = widget_under_cursor
        while w is not None:
            if isinstance(w, tk.Text):
                return
            if w == self:
                break
            w = w.master

        if self.scrollbar.winfo_ismapped():
            # Handle platform-specific scroll directions and speeds
            if event.num == 5 or event.delta == -120:
                delta = 1
            elif event.num == 4 or event.delta == 120:
                delta = -1
            else:
                delta = -1 * (event.delta // 120)

            self.canvas.yview_scroll(delta, "units")

    def _manage_scrollbar(self):
        scrollregion = self.canvas.cget("scrollregion")
        if scrollregion:
            try:
                content_height = int(scrollregion.split(' ')[3])
                canvas_height = self.canvas.winfo_height()

                if content_height > canvas_height:
                    if not self.scrollbar.winfo_ismapped():
                        self.scrollbar.pack(side="right", fill="y")
                else:
                    if self.scrollbar.winfo_ismapped():
                        self.scrollbar.pack_forget()
            except (ValueError, IndexError):
                if self.scrollbar.winfo_ismapped():
                    self.scrollbar.pack_forget()
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.pack_forget()

    def destroy(self):
        # Unbind the global mousewheel event to prevent errors after destruction
        self.scrollable_frame.unbind_all("<MouseWheel>")
        super().destroy()