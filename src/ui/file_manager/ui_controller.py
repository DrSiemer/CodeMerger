import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, Toplevel, Label
from ... import constants as c
from ..assets import assets

class FileManagerUIController:
    def __init__(self, window):
        self.window = window
        self.active_folder_icon_label = None
        self.folder_tooltip_window = None
        self.folder_tooltip_label = None
        self.folder_tooltip_job = None
        self.hovered_folder_id = None

    def _is_click_in_widget(self, event):
        """Helper to check if the release event occurred inside the widget."""
        if event is None: return True
        return 0 <= event.x <= event.widget.winfo_width() and 0 <= event.y <= event.widget.winfo_height()

    def clear_filter(self, event=None):
        if not self._is_click_in_widget(event): return
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

    def _show_icon_for_item(self, item_id):
        if not item_id:
            self.on_tree_leave()
            return

        item_info = self.window.item_map.get(item_id, {})
        if item_info.get('type') != 'file':
            self.on_tree_leave()
            return

        bbox = self.window.tree.bbox(item_id)
        if not bbox:
            self.on_tree_leave()
            return

        # Determine the correct state and select the pre-built label
        current_state = 'default'
        tags = self.window.tree.item(item_id, 'tags')
        if item_id in self.window.tree.selection():
            current_state = 'selected'
        elif 'subtle_highlight' in tags:
            current_state = 'highlight'

        label_to_show = self.window.folder_icon_labels[current_state]

        # Swap the visible label only if it has changed
        if self.active_folder_icon_label is not label_to_show:
            if self.active_folder_icon_label:
                self.active_folder_icon_label.place_forget()
            self.active_folder_icon_label = label_to_show

        # Calculate position and place the icon
        tree_width = self.window.tree.winfo_width()
        icon_width = assets.folder_reveal_icon.width()
        icon_height = assets.folder_reveal_icon.height()
        icon_x = tree_width - icon_width - 8
        icon_y = bbox[1] + (bbox[3] // 2) - (icon_height // 2)

        self.active_folder_icon_label.place(x=icon_x, y=icon_y)
        self.window.hovered_file_path = item_info['path']

    def refresh_hover_icon(self):
        if self.window.hovered_file_path:
            item_id = self.window.path_to_item_id.get(self.window.hovered_file_path)
            if item_id:
                self._show_icon_for_item(item_id)

    def on_tree_motion(self, event):
        item_id = self.window.tree.identify_row(event.y)
        self._show_icon_for_item(item_id)

        # Cancel any pending job and hide the current tooltip.
        if self.folder_tooltip_job:
            self.window.after_cancel(self.folder_tooltip_job)
            self.folder_tooltip_job = None
        self._hide_folder_tooltip()

        self.hovered_folder_id = None

        if item_id:
            item_info = self.window.item_map.get(item_id, {})
            if item_info.get('type') == 'dir':
                self.hovered_folder_id = item_id
                self.folder_tooltip_job = self.window.after(500, lambda e=event, iid=item_id: self._show_folder_tooltip(e, iid))

    def on_tree_leave(self, event=None):
        if self.active_folder_icon_label:
            self.active_folder_icon_label.place_forget()
            self.active_folder_icon_label = None
        self.window.hovered_file_path = None

        if self.folder_tooltip_job:
            self.window.after_cancel(self.folder_tooltip_job)
            self.folder_tooltip_job = None
        self._hide_folder_tooltip()
        self.hovered_folder_id = None

    def _get_folder_tooltip_text(self, item_id):
        """Calculates the dynamic text for the folder tooltip."""
        files_in_subtree = self.window.tree_handler._get_all_files_in_subtree(item_id)
        if not files_in_subtree:
            return None

        current_selection_paths = {f['path'] for f in self.window.selection_handler.ordered_selection}
        subtree_paths_set = set(files_in_subtree)
        is_fully_selected = subtree_paths_set.issubset(current_selection_paths)

        action_text = "remove" if is_fully_selected else "add"
        return f"Alt+Click to {action_text} all files in this folder"

    def _show_folder_tooltip(self, event, item_id):
        self._hide_folder_tooltip()

        text = self._get_folder_tooltip_text(item_id)
        if not text:
            return

        x, y = event.x_root + 15, event.y_root + 10
        self.folder_tooltip_window = Toplevel(self.window)
        self.folder_tooltip_window.wm_overrideredirect(True)
        self.folder_tooltip_window.wm_geometry(f"+{x}+{y}")
        self.folder_tooltip_label = Label(self.folder_tooltip_window, text=text, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=c.FONT_TOOLTIP)
        self.folder_tooltip_label.pack(ipadx=4, ipady=2)

    def _hide_folder_tooltip(self):
        if self.folder_tooltip_window:
            self.folder_tooltip_window.destroy()
        self.folder_tooltip_window = None
        self.folder_tooltip_label = None

    def update_active_folder_tooltip(self):
        """Refreshes the folder tooltip text if it's currently visible."""
        if self.hovered_folder_id and self.folder_tooltip_window and self.folder_tooltip_label:
            new_text = self._get_folder_tooltip_text(self.hovered_folder_id)
            if new_text:
                self.folder_tooltip_label.config(text=new_text)
            else:
                self._hide_folder_tooltip()

    def on_folder_icon_click(self, event=None):
        if not self._is_click_in_widget(event): return
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
            except tk.TclError: pass
        self.window.after(10, adjust_sash)

    def toggle_gitignore_filter(self):
        """Toggles the .gitignore file filter on and off."""
        self.window.is_gitignore_filter_active = not self.window.is_gitignore_filter_active

        self.window.gitignore_button_tooltip.cancel_show()
        self.window.gitignore_button_tooltip.hide_tooltip()

        if self.window.is_gitignore_filter_active:
            self.window.toggle_gitignore_button.config(image=assets.git_files_icon)
            self.window.gitignore_button_tooltip.text = ".gitignore filter is ON. Click to show all files."
        else:
            self.window.toggle_gitignore_button.config(image=assets.git_files_icon_active)
            self.window.gitignore_button_tooltip.text = ".gitignore filter is OFF. Click to hide ignored files."

        self.window.gitignore_button_tooltip.show_tooltip()
        self.window.populate_tree(self.window.filter_text.get())

    def toggle_extension_filter(self):
        """Toggles the filetype extension filter on and off."""
        self.window.is_extension_filter_active = not self.window.is_extension_filter_active

        self.window.filter_button_tooltip.cancel_show()
        self.window.filter_button_tooltip.hide_tooltip()

        if self.window.is_extension_filter_active:
            self.window.toggle_filter_button.config(image=assets.filter_icon)
            self.window.filter_button_tooltip.text = "Filetype filter is ON. Click to show all files."
        else:
            self.window.toggle_filter_button.config(image=assets.filter_icon_active)
            self.window.filter_button_tooltip.text = "Filetype filter is OFF. Click to show only allowed filetypes."

        # Show the new tooltip immediately. It will be hidden automatically on <Leave>.
        self.window.filter_button_tooltip.show_tooltip()

        # Repopulate tree using the current text filter value
        self.window.populate_tree(self.window.filter_text.get())

    def expand_and_scroll_to_new_files(self):
        """Expands parent directories of newly detected files and scrolls to the first one."""
        if not self.window.newly_detected_files:
            return

        # Expand all parent directories for each new file.
        for file_path in self.window.newly_detected_files:
            item_id = self.window.path_to_item_id.get(file_path)
            if item_id:
                parent_id = self.window.tree.parent(item_id)
                while parent_id:
                    self.window.tree.item(parent_id, open=True)
                    parent_id = self.window.tree.parent(parent_id)

        # Scroll to the first new file alphabetically.
        first_file_path = sorted(self.window.newly_detected_files)[0]
        first_item_id = self.window.path_to_item_id.get(first_file_path)

        if first_item_id:
            # Use 'after' to give the UI time to update with the new expansions
            # before trying to scroll. This prevents a race condition.
            def scroll_if_ready():
                try:
                    self.window.tree.see(first_item_id)
                except tk.TclError:
                    # Window might have been closed during the delay
                    pass
            self.window.after(50, scroll_if_ready)