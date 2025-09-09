import tkinter as tk
from tkinter import font as tkFont
import sys
from ... import constants as c

class TwoColumnList(tk.Canvas):
    """A custom listbox widget that displays two columns with independent styling."""
    def __init__(self, parent, right_col_font, right_col_width, **kwargs):
        super().__init__(parent, bg=c.TEXT_INPUT_BG, highlightthickness=0, **kwargs)
        self.items = []
        self.selected_indices = set()
        self.highlighted_indices = set()
        self.row_height = 25
        self.left_col_font = tkFont.Font(family="Segoe UI", size=12)
        self.right_col_font = right_col_font
        self.right_col_width = right_col_width
        self.scrollbar = None
        self.last_clicked_index = None
        self.bind("<ButtonPress-1>", self._on_click)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Configure>", self._redraw)
        # This is the key: the yscrollcommand will be set externally by the scrollbar.
        # We wrap the default yview methods to trigger a redraw *after* they have moved the canvas.
        self._original_yview = self.yview
        self._original_yview_scroll = self.yview_scroll
        self._original_yview_moveto = self.yview_moveto
        self.yview = self._yview_wrapper
        self.yview_scroll = self._yview_scroll_wrapper
        self.yview_moveto = self._yview_moveto_wrapper

    def _yview_wrapper(self, *args):
        # The wrapper must return the result of the original method call
        result = self._original_yview(*args)
        self._redraw()
        return result

    def _yview_scroll_wrapper(self, *args):
        # This wrapper must also return the result of the original call
        result = self._original_yview_scroll(*args)
        self._redraw()
        return result

    def _yview_moveto_wrapper(self, *args):
        # This wrapper must also return the result of the original call
        result = self._original_yview_moveto(*args)
        self._redraw()
        return result

    def link_scrollbar(self, scrollbar):
        """Links a ttk.Scrollbar widget to this list for visibility management."""
        self.scrollbar = scrollbar

    def bind_event(self, sequence=None, func=None, add=None):
        self.bind(sequence, func, add)

    def _on_mousewheel(self, event):

        if not self.scrollbar or not self.scrollbar.winfo_ismapped():
            return

        start, end = self.scrollbar.get()
        delta = -1 * (event.delta // 120) if sys.platform == "win32" else event.delta

        if delta < 0 and start <= 0.0:
            return
        if delta > 0 and end >= 1.0:
            return

        self.yview_scroll(delta, "units")

    def _on_click(self, event):
        self.focus_set()
        # Use canvasy to get the coordinate relative to the scrollable area
        clicked_index = int(self.canvasy(event.y) // self.row_height)
        if 0 <= clicked_index < len(self.items):
            is_shift = (event.state & 0x0001)
            is_ctrl = (event.state & 0x0004)

            if is_shift and self.last_clicked_index is not None:
                # Shift-click range selection
                start = min(self.last_clicked_index, clicked_index)
                end = max(self.last_clicked_index, clicked_index)
                new_selection = set(range(start, end + 1))
                if is_ctrl:
                    # If Ctrl is also held, add the range to the existing selection
                    self.selected_indices.update(new_selection)
                else:
                    # Otherwise, replace the selection with the new range
                    self.selected_indices = new_selection
            elif is_ctrl:
                if clicked_index in self.selected_indices:
                    self.selected_indices.remove(clicked_index)
                else:
                    self.selected_indices.add(clicked_index)
                self.last_clicked_index = clicked_index # Update anchor on ctrl-click
            else: # Simple click
                self.selected_indices = {clicked_index}
                self.last_clicked_index = clicked_index # Set anchor on simple click

            self.event_generate("<<ListSelectionChanged>>")
            self._redraw()

    def _update_scrollregion(self):
        total_height = len(self.items) * self.row_height
        self.config(scrollregion=(0, 0, self.winfo_width(), total_height))

    def _update_scrollbar_visibility(self):
        """Shows or hides the linked scrollbar based on content height."""
        if not self.scrollbar:
            return
        self.update_idletasks() # Ensure winfo_height() is accurate
        content_height = len(self.items) * self.row_height
        canvas_height = self.winfo_height()
        # If the content is taller than the canvas, we need the scrollbar
        if content_height > canvas_height:
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.grid() # grid() remembers previous options
        # Otherwise, hide it
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.grid_remove()

    def _redraw(self, event=None):
        self.delete("all")
        self._update_scrollregion()
        self._update_scrollbar_visibility()
        width = self.winfo_width()
        # Determine the visible range of items based on the canvas's current view
        view_y_start = self.canvasy(0)
        view_y_end = self.canvasy(self.winfo_height())
        start_index = max(0, int(view_y_start // self.row_height))
        end_index = min(len(self.items), int(view_y_end // self.row_height) + 2)
        for i in range(start_index, end_index):
            if i >= len(self.items): continue
            item = self.items[i]
            y = i * self.row_height
            # Draw background for selection or highlight
            bg_color = ""
            if i in self.selected_indices:
                bg_color = c.BTN_BLUE
            elif i in self.highlighted_indices:
                bg_color = c.SUBTLE_HIGHLIGHT_COLOR
            if bg_color:
                self.create_rectangle(0, y, width, y + self.row_height, fill=bg_color, outline="")
            left_fg = c.BTN_BLUE_TEXT if i in self.selected_indices else c.TEXT_COLOR
            # Draw left column (filename)
            self.create_text(
                5, y + self.row_height / 2,
                anchor='w',
                text=item.get('left', ''),
                font=self.left_col_font,
                fill=left_fg
            )
            # Draw right column (line count)
            self.create_text(
                width - 5, y + self.row_height / 2,
                anchor='e',
                text=item.get('right', ''),
                font=self.right_col_font,
                fill=item.get('right_fg', c.TEXT_SUBTLE_COLOR)
            )

    def set_items(self, items):
        selection_paths = {self.get_item_data(i) for i in self.curselection()}
        self.items = items
        # Restore selection based on data, not index
        new_selection = set()
        for i, item in enumerate(self.items):
            if item.get('data') in selection_paths:
                new_selection.add(i)
        self.selected_indices = new_selection
        self._redraw()

    def curselection(self):
        return sorted(list(self.selected_indices))

    def clear_selection(self):
        self.selected_indices.clear()
        self._redraw()

    def see(self, index):
        """Scrolls the list to make the item at the given index visible."""
        if not (0 <= index < len(self.items)):
            return
        item_y_start = index * self.row_height
        item_y_end = item_y_start + self.row_height
        view_y_start = self.canvasy(0)
        view_y_end = view_y_start + self.winfo_height()
        total_height = len(self.items) * self.row_height
        if total_height == 0: return
        if item_y_start < view_y_start:
            # Item is above the view, scroll up
            fraction = item_y_start / total_height
            self.yview_moveto(fraction)
        elif item_y_end > view_y_end:
            # Item is below the view, scroll down
            fraction = (item_y_end - self.winfo_height()) / total_height
            self.yview_moveto(fraction)

    def selection_set(self, start, end=None):
        self.selected_indices = set(range(start, (end if end is not None else start) + 1))
        self._redraw()

    def get_item_data(self, index):
        if 0 <= index < len(self.items):
            return self.items[index].get('data')
        return None

    def highlight_item(self, index):
        self.highlighted_indices.add(index)
        self._redraw()

    def clear_highlights(self):
        self.highlighted_indices.clear()
        self._redraw()