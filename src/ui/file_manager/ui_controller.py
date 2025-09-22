import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from ... import constants as c
from ..assets import assets

class FileManagerUIController:
    def __init__(self, window):
        self.window = window

    def clear_filter(self, event=None):
        self.window.filter_text.set("")
        self.window.focus_force()

    def apply_filter(self, *args):
        filter_query = self.window.filter_text.get().lower()
        is_active = bool(filter_query)

        color = c.FILTER_ACTIVE_BORDER if is_active else c.TEXT_INPUT_BG
        self.window.filter_input_frame.config(highlightbackground=color, highlightcolor=color)

        if is_active:
            self.window.clear_filter_button.place(relx=1.0, rely=0.5, anchor='e', x=-5)
        else:
            self.window.clear_filter_button.place_forget()

        self.window.selection_handler.set_filtered_state(is_active)
        self.window.populate_tree(filter_query)
        self.window.selection_handler.filter_list(filter_query)

    def on_tree_motion(self, event):
        item_id = self.window.tree.identify_row(event.y)
        if item_id:
            item_info = self.window.item_map.get(item_id, {})
            if item_info.get('type') == 'file':
                bbox = self.window.tree.bbox(item_id)
                if not bbox:
                    self.on_tree_leave()
                    return

                tree_width = self.window.tree.winfo_width()
                icon_width = assets.folder_reveal_icon.width()
                icon_height = assets.folder_reveal_icon.height()
                icon_x = tree_width - icon_width - 8
                icon_y = bbox[1] + (bbox[3] // 2) - (icon_height // 2)

                self.window.folder_icon_label.place(x=icon_x, y=icon_y)
                self.window.hovered_file_path = item_info['path']
                return
        self.on_tree_leave()

    def on_tree_leave(self, event=None):
        self.window.folder_icon_label.place_forget()
        self.window.hovered_file_path = None

    def on_folder_icon_click(self, event=None):
        if self.window.hovered_file_path:
            self._open_file_location(self.window.hovered_file_path)

    def _open_file_location(self, relative_path):
        full_path = os.path.join(self.window.base_dir, relative_path)
        if not os.path.exists(full_path):
            messagebox.showwarning("File Not Found", f"The file '{relative_path}' could not be found.", parent=self.window)
            return
        try:
            if sys.platform == "win32":
                subprocess.run(['explorer', '/select,', os.path.normpath(full_path)])
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", full_path])
            else:
                dir_path = os.path.dirname(full_path)
                if os.path.isdir(dir_path):
                    subprocess.run(["xdg-open", dir_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file location: {e}", parent=self.window)

    def toggle_full_path_view(self):
        self.window.full_paths_visible = not self.window.full_paths_visible
        self.window.selection_handler.toggle_full_path_view()

        def adjust_sash():
            try:
                self.window.update_idletasks()
                total_width = self.window.paned_window.winfo_width()

                if total_width <= 1: return

                if self.window.full_paths_visible:
                    self.window.sash_pos_normal = self.window.paned_window.sashpos(0)
                    sash_position = int(total_width * 0.4)
                    self.window.toggle_paths_button.config(image=assets.paths_icon_active)
                else:
                    sash_position = self.window.sash_pos_normal or (total_width // 2)
                    self.window.toggle_paths_button.config(image=assets.paths_icon)

                self.window.paned_window.sashpos(0, sash_position)
                self.window._update_sash_cover_position()

            except tk.TclError:
                pass

        self.window.after(10, adjust_sash)