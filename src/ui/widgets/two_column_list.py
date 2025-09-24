import tkinter as tk
from tkinter import font as tkFont
import sys
from ... import constants as c

class TwoColumnList(tk.Canvas):
    """A custom listbox widget that displays two columns with independent styling."""
    def __init__(self, parent, right_col_font, right_col_width, **kwargs):
        super().__init__(parent, bg=c.TEXT_INPUT_BG, highlightthickness=0, **kwargs)
        self.items = []
        self.item_id_map = {}
        self.selected_indices = set()
        self.highlighted_indices = set()
        self.row_height = c.DEFAULT_LIST_ITEM_HEIGHT
        self.left_col_font = tkFont.Font(family=c.FONT_NORMAL[0], size=c.FONT_NORMAL[1])
        self.right_col_font = right_col_font
        self.right_col_width = right_col_width
        self.scrollbar = None
        self.last_clicked_index = None
        self.bind("<ButtonPress-1>", self._on_click)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event=None):
        """
        On resize, repositions existing canvas items instead of redrawing them,
        which is much smoother and avoids flicker.
        """
        width = self.winfo_width()
        for i, item in enumerate(self.items):
            item_path = item.get('data')
            if not item_path or item_path not in self.item_id_map: continue
            ids = self.item_id_map[item_path]

            y = i * self.row_height
            self.coords(ids['bg'], 0, y, width, y + self.row_height)
            self.coords(ids['right'], width - 5, y + self.row_height / 2)

        self._update_scrollregion()
        self._update_scrollbar_visibility()

    def link_scrollbar(self, scrollbar):
        """Links a ttk.Scrollbar widget to this list for visibility management."""
        self.scrollbar = scrollbar

    def bind_event(self, sequence=None, func=None, add=None):
        self.bind(sequence, func, add)

    def _on_mousewheel(self, event):
        if not self.scrollbar or not self.scrollbar.winfo_ismapped(): return
        start, end = self.scrollbar.get()
        delta = -1 * (event.delta // 120) if sys.platform == "win32" else event.delta
        if delta < 0 and start <= 0.0: return
        if delta > 0 and end >= 1.0: return
        self.yview_scroll(delta, "units")

    def _on_click(self, event):
        self.focus_set()
        clicked_index = int(self.canvasy(event.y) // self.row_height)
        if 0 <= clicked_index < len(self.items):
            is_shift = (event.state & 0x0001)
            is_ctrl = (event.state & 0x0004)

            if is_shift and self.last_clicked_index is not None:
                start = min(self.last_clicked_index, clicked_index)
                end = max(self.last_clicked_index, clicked_index)
                new_selection = set(range(start, end + 1))
                if is_ctrl:
                    self.selected_indices.update(new_selection)
                else:
                    self.selected_indices = new_selection
            elif is_ctrl:
                if clicked_index in self.selected_indices: self.selected_indices.remove(clicked_index)
                else: self.selected_indices.add(clicked_index)
                self.last_clicked_index = clicked_index
            else:
                self.selected_indices = {clicked_index}
                self.last_clicked_index = clicked_index

            self.event_generate("<<ListSelectionChanged>>")
            self._update_styles()

    def _update_scrollregion(self):
        total_height = len(self.items) * self.row_height
        self.config(scrollregion=(0, 0, self.winfo_width(), total_height))

    def _update_scrollbar_visibility(self):
        if not self.scrollbar: return
        self.update_idletasks()
        content_height = len(self.items) * self.row_height
        canvas_height = self.winfo_height()
        if content_height > canvas_height:
            if not self.scrollbar.winfo_ismapped(): self.scrollbar.grid()
        else:
            if self.scrollbar.winfo_ismapped(): self.scrollbar.grid_remove()

    def _update_styles(self):
        """
        Efficiently updates the colors of existing canvas items without redrawing them.
        This is the key to flicker-free selection and highlighting.
        """
        for i, item in enumerate(self.items):
            item_path = item.get('data')
            if not item_path or item_path not in self.item_id_map: continue
            ids = self.item_id_map[item_path]

            bg_color = c.TEXT_INPUT_BG
            if i in self.selected_indices: bg_color = c.BTN_BLUE
            elif i in self.highlighted_indices: bg_color = c.SUBTLE_HIGHLIGHT_COLOR

            left_fg = c.BTN_BLUE_TEXT if i in self.selected_indices else c.TEXT_COLOR
            right_fg = item.get('right_fg', c.TEXT_SUBTLE_COLOR)

            self.itemconfig(ids['bg'], fill=bg_color)
            self.itemconfig(ids['left'], fill=left_fg)
            self.itemconfig(ids['right'], fill=right_fg)

    def set_items(self, items):
        """
        Performs a full redraw of the list. Called when the underlying data changes
        (e.g., adding/removing files).
        """
        selection_paths = {self.get_item_data(i) for i in self.curselection()}

        self.delete("all")
        self.item_id_map.clear()
        self.items = items

        width = self.winfo_width()
        if width <= 1: self.update_idletasks(); width = self.winfo_width()

        for i, item in enumerate(self.items):
            y = i * self.row_height
            bg_rect = self.create_rectangle(0, y, width, y + self.row_height, outline="")
            left_text = self.create_text(5, y + self.row_height / 2, anchor='w', text=item.get('left', ''), font=self.left_col_font)
            right_text = self.create_text(width - 5, y + self.row_height / 2, anchor='e', text=item.get('right', ''), font=self.right_col_font)
            # Use the unique file path as the key
            item_path = item.get('data')
            if item_path:
                self.item_id_map[item_path] = {'bg': bg_rect, 'left': left_text, 'right': right_text}

        self._update_scrollregion()
        self._update_scrollbar_visibility()

        new_selection = set()
        for i, item in enumerate(self.items):
            if item.get('data') in selection_paths: new_selection.add(i)
        self.selected_indices = new_selection
        self._update_styles()

    def reorder_and_update(self, new_display_items):
        """
        Moves and updates existing canvas items without a full redraw. This is
        used for reordering operations to prevent flickering.
        """
        self.items = new_display_items
        width = self.winfo_width()
        for new_index, item_data in enumerate(self.items):
            item_path = item_data.get('data')
            if not item_path or item_path not in self.item_id_map:
                continue

            ids = self.item_id_map[item_path]
            new_y = new_index * self.row_height

            # Move existing items
            self.coords(ids['bg'], 0, new_y, width, new_y + self.row_height)
            self.coords(ids['left'], 5, new_y + self.row_height / 2)
            self.coords(ids['right'], width - 5, new_y + self.row_height / 2)

            # Update their content (e.g., line count color might change)
            self.itemconfig(ids['left'], text=item_data.get('left', ''))
            self.itemconfig(ids['right'], text=item_data.get('right', ''), fill=item_data.get('right_fg', c.TEXT_SUBTLE_COLOR))

        self._update_styles()

    def curselection(self):
        return sorted(list(self.selected_indices))

    def clear_selection(self):
        self.selected_indices.clear()
        self._update_styles()

    def see(self, index):
        if not (0 <= index < len(self.items)): return
        item_y_start = index * self.row_height
        item_y_end = item_y_start + self.row_height
        view_y_start = self.canvasy(0)
        view_y_end = view_y_start + self.winfo_height()
        total_height = len(self.items) * self.row_height
        if total_height == 0: return
        if item_y_start < view_y_start: self.yview_moveto(item_y_start / total_height)
        elif item_y_end > view_y_end: self.yview_moveto((item_y_end - self.winfo_height()) / total_height)

    def selection_set(self, start, end=None):
        self.selected_indices = set(range(start, (end if end is not None else start) + 1))
        self._update_styles()

    def get_item_data(self, index):
        if 0 <= index < len(self.items): return self.items[index].get('data')
        return None

    def highlight_item(self, index):
        self.highlighted_indices.add(index)
        self._update_styles()

    def clear_highlights(self):
        self.highlighted_indices.clear()
        self._update_styles()