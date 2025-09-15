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
        # This is the frame that other widgets will be packed into
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<MouseWheel>", self._on_mousewheel)
        # Also bind mousewheel events on children to the canvas scroll
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel, add=True)


    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._manage_scrollbar()

    def _on_canvas_configure(self, event=None):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # Do not scroll if the cursor is over a Text widget, as it has its own scrolling
        widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)
        w = widget_under_cursor
        while w is not None:
            if isinstance(w, tk.Text):
                return
            if w == self:
                break
            w = w.master

        if self.scrollbar.winfo_ismapped():
            # The direction and scaling of delta can differ between platforms
            if event.num == 5 or event.delta == -120:
                delta = 1
            elif event.num == 4 or event.delta == 120:
                delta = -1
            else: # Fallback for other systems
                delta = -1 * (event.delta // 120)

            self.canvas.yview_scroll(delta, "units")

    def _manage_scrollbar(self):
        self.update_idletasks()
        frame_height = self.scrollable_frame.winfo_reqheight()
        canvas_height = self.canvas.winfo_height()

        if frame_height > canvas_height:
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.pack(side="right", fill="y")
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.pack_forget()

    def destroy(self):
        # Unbind the global mousewheel event to prevent errors after destruction
        self.scrollable_frame.unbind_all("<MouseWheel>")
        super().destroy()