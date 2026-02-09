import os
import tkinter as tk
from tkinter import Toplevel, Frame, Label, filedialog, StringVar, Entry, messagebox
import sys
import subprocess
import json
from ..core.project_config import ProjectConfig
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_frame import ScrollableFrame

from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import save_window_geometry, get_monitor_work_area
from .assets import assets

class DirectoryDialog(Toplevel):
    """
    A dialog window for selecting a recent or new project directory.
    Features a scrollable list and a filter.
    """
    def __init__(self, parent, app_bg_color, recent_projects, on_select_callback, on_remove_callback):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.app_bg_color = app_bg_color
        self.recent_projects = recent_projects
        self.on_select_callback = on_select_callback
        self.on_remove_callback = on_remove_callback
        self.tooltip = None
        self.project_widgets = []
        self.non_list_height = 0
        self.project_metadata_cache = {}
        # Instance variables to reliably store the current position.
        self.current_x = 0
        self.current_y = 0

        self.title("Select Project")
        self.iconbitmap(ICON_PATH)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=self.app_bg_color)
        self.resizable(False, False)

        self.dialog_width = c.DIRECTORY_DIALOG_WIDTH

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        message = "Select a recent project or browse for a new one" if self.recent_projects else "Browse for a project folder to get started"
        self.info_label = Label(self, text=message, padx=20, pady=10, bg=self.app_bg_color, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.info_label.grid(row=0, column=0, sticky='ew', pady=(5, 0))

        # --- Filter Bar ---
        self.filter_frame = Frame(self, bg=c.DARK_BG, padx=20)
        self.filter_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        Label(self.filter_frame, text="Filter:", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='left')
        self.filter_var = StringVar()
        self.filter_entry = Entry(self.filter_frame, textvariable=self.filter_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.filter_entry.pack(side='left', fill='x', expand=True, padx=(5,0), ipady=3)
        self.filter_var.trace_add('write', self._filter_projects)

        # --- Scrollable List Container ---
        self.list_container = Frame(self, bg=self.app_bg_color)
        self.list_container.grid(row=2, column=0, sticky='nsew')
        self.list_container.grid_rowconfigure(0, weight=1)
        self.list_container.grid_columnconfigure(0, weight=1)
        self.scroll_frame = ScrollableFrame(self.list_container, bg=self.app_bg_color)
        self.scroll_frame.grid(row=0, column=0, sticky='nsew')
        self.recent_dirs_frame = self.scroll_frame.scrollable_frame

        # --- "Add Project" Button ---
        self.browse_btn = RoundedButton(
            self, text="Add project", command=self.browse_for_new_dir,
            bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor='hand2'
        )
        self.browse_btn.grid(row=3, column=0, sticky='ew', pady=20, padx=20)

        # Let the window calculate its size with no list items.
        self.update_idletasks()
        initial_height = self.winfo_reqheight()
        x, y = 0, 0
        saved_geometry = None

        if hasattr(self.parent, 'window_geometries'):
            saved_geometry = self.parent.window_geometries.get(self.__class__.__name__)

        if saved_geometry:
            try:
                parts = saved_geometry.replace('+', ' ').replace('x', ' ').split()
                if len(parts) == 4:
                    _, _, x, y = map(int, parts)
                else:
                    saved_geometry = None
            except (ValueError, IndexError):
                saved_geometry = None

        if not saved_geometry:
            parent_x, parent_y = self.parent.winfo_rootx(), self.parent.winfo_rooty()
            parent_w, parent_h = self.parent.winfo_width(), self.parent.winfo_height()
            x = parent_x + (parent_w - self.dialog_width) // 2
            y = parent_y + (parent_h - initial_height) // 2

        # Store the calculated position reliably.
        self.current_x = x
        self.current_y = y

        self.geometry(f"{self.dialog_width}x{initial_height}+{self.current_x}+{self.current_y}")

        self._populate_projects(self.recent_projects)

        self.protocol("WM_DELETE_WINDOW", self._close_and_save_geometry)
        self.bind('<Escape>', lambda e: self._close_and_save_geometry())
        self.bind('<Configure>', self._on_drag)
        self.deiconify()

        if self.filter_frame.winfo_ismapped():
            self.filter_entry.focus_set()

    def _on_drag(self, event):
        """Updates the stored position when the window is moved by the user."""
        if self.state() == 'normal':
            self.current_x = self.winfo_x()
            self.current_y = self.winfo_y()

    def _filter_projects(self, *args):
        query = self.filter_var.get().lower()
        filtered_list = [
            path for path in self.recent_projects
            if not query or query in os.path.basename(path).lower() or query in path.lower()
        ]
        self._populate_projects(filtered_list)

    def _get_project_metadata(self, path):
        """
        Retrieves project name and color from a cache to avoid repeated file I/O.
        If not in cache, reads .allcode, caches the data, and returns it.
        """
        if path in self.project_metadata_cache:
            return self.project_metadata_cache[path]

        allcode_path = os.path.join(path, '.allcode')
        name = os.path.basename(path)
        color = c.COMPACT_MODE_BG_COLOR

        if os.path.isfile(allcode_path):
            try:
                with open(allcode_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    if content:
                        data = json.loads(content)
                        name = data.get('project_name', name)
                        color = data.get('project_color', color)
            except (IOError, json.JSONDecodeError):
                pass # Use defaults if file is unreadable

        metadata = {'name': name, 'color': color}
        self.project_metadata_cache[path] = metadata
        return metadata

    def _populate_projects(self, project_list):
        for widget in self.project_widgets:
            widget.destroy()
        self.project_widgets.clear()

        # Update filter bar visibility: Hide if user has less than 5 projects total
        if len(self.recent_projects) >= 5:
            if not self.filter_frame.winfo_ismapped():
                self.filter_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        else:
            if self.filter_frame.winfo_ismapped():
                self.filter_frame.grid_forget()
                # Clear filter when hidden to avoid being stuck in a filtered state
                if self.filter_var.get():
                    self.filter_var.set("")
                    return # Trace will trigger re-populate

        for path in project_list:
            entry_frame = self._create_recent_dir_entry(path)
            self.project_widgets.append(entry_frame)

        self._adjust_height()

    def _adjust_height(self):
        """
        Calculates and applies the height of the inner scrollable area
        and allows the window to naturally shrink-wrap around all content.
        """
        num_items = len(self.project_widgets)

        # Determine row height (default to 38 if not yet rendered)
        item_h = 38
        if num_items > 0:
            self.update_idletasks()
            item_h = self.project_widgets[0].winfo_reqheight() + 6 # req + padding

        # 1. Set the specific height for the Canvas (cap at 10 rows)
        list_h = min(num_items, 10) * item_h
        self.scroll_frame.canvas.config(height=list_h)

        # 2. Tell the window to reset its geometry calculation
        self.geometry("")
        self.update_idletasks()

        # 3. Get the calculated natural height
        win_w, win_h = self.dialog_width, self.winfo_reqheight()

        # 4. Final Position and screen constraint
        x, y = self.current_x, self.current_y
        mon_left, mon_top, mon_right, mon_bottom = get_monitor_work_area((x, y))
        mon_bottom -= 50; mon_right -= 20; mon_left += 10; mon_top += 10
        if x + win_w > mon_right: x = mon_right - win_w
        if y + win_h > mon_bottom: y = mon_bottom - win_h
        if x < mon_left: x = mon_left
        if y < mon_top: y = mon_top

        self.geometry(f"{win_w}x{win_h}+{x}+{y}")

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def _show_trash_button(self, container):
        if hasattr(container, 'trash_button'):
            container.trash_button.pack(side='left', padx=(10, 0))

    def _hide_trash_button(self, container):
        if hasattr(container, 'trash_button'):
            container.trash_button.pack_forget()

    def _create_recent_dir_entry(self, path):
        entry_frame = Frame(self.recent_dirs_frame, bg=self.app_bg_color)
        entry_frame.pack(fill='x', padx=20, pady=3)

        metadata = self._get_project_metadata(path)
        display_text = metadata['name']
        project_color = metadata['color']

        logo_image = self.parent.assets.create_masked_logo_small(project_color)
        color_swatch = Label(entry_frame, image=logo_image, bg=self.app_bg_color)
        color_swatch.image = logo_image # Prevent garbage collection
        color_swatch.pack(side='left', padx=(0, 10))

        # This container will hold the main project button and the trash button
        buttons_container = Frame(entry_frame, bg=self.app_bg_color)
        buttons_container.pack(side='left', expand=True, fill='x')

        btn = RoundedButton(
            buttons_container, text=display_text, command=None,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, height=32, cursor='hand2', text_align='left'
        )
        btn.pack(side='left', expand=True, fill='x')

        if assets.trash_icon_image:
            remove_btn = RoundedButton(
                parent=buttons_container, command=lambda p=path: self.remove_and_update_dialog(p),
                image=assets.trash_icon_image, bg=c.BTN_GRAY_BG, width=32, height=32, cursor='hand2'
            )
            # The button is created but not packed initially. It will be shown on hover.
            buttons_container.trash_button = remove_btn

        # --- Event Bindings ---
        btn.bind("<ButtonRelease-1>", lambda e, p=path: self.on_project_button_release(e, p))
        btn.bind("<Enter>", lambda e, p=path: self.show_path_tooltip(e, p))
        btn.bind("<Leave>", self.hide_path_tooltip)

        # Bind hover events to the entire row for a better user experience
        entry_frame.bind("<Enter>", lambda e, c=buttons_container: self._show_trash_button(c))
        entry_frame.bind("<Leave>", lambda e, c=buttons_container: self._hide_trash_button(c))

        return entry_frame

    def on_project_button_release(self, event, path):
        widget = event.widget
        # Only proceed if the release happens within the button's boundaries
        if 0 <= event.x <= widget.winfo_width() and 0 <= event.y <= widget.winfo_height():
            # Provide visual feedback of release/hover state
            if hasattr(widget, '_draw') and hasattr(widget, 'hover_color'):
                widget._draw(widget.hover_color)

            # Ctrl key is state 4
            is_ctrl = (event.state & 0x0004)
            if is_ctrl:
                self.open_project_folder(path)
            else:
                self.select_and_close(path)
        else:
            # If released outside, reset visual state to normal
            if hasattr(widget, '_draw') and hasattr(widget, 'base_color'):
                widget._draw(widget.base_color)

    def open_project_folder(self, path):
        if not (path and os.path.isdir(path)):
            return
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}", parent=self)

    def show_path_tooltip(self, event, path):
        if self.tooltip: self.tooltip.destroy()
        x, y = event.widget.winfo_rootx(), event.widget.winfo_rooty() + event.widget.winfo_height() + 1
        self.tooltip = Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = Label(self.tooltip, text=path+" (ctrl-click to open)", justify='left', bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1, font=c.FONT_TOOLTIP, padx=4, pady=2)
        label.pack(ipadx=2, ipady=1)

    def hide_path_tooltip(self, event):
        if self.tooltip: self.tooltip.destroy(); self.tooltip = None

    def select_and_close(self, path):
        if self.on_select_callback: self.on_select_callback(path)
        self._close_and_save_geometry()

    def browse_for_new_dir(self):
        new_path = filedialog.askdirectory(title="Select Project Folder", parent=self)
        if new_path: self.select_and_close(new_path)

    def remove_and_update_dialog(self, path_to_remove):
        self.on_remove_callback(path_to_remove)
        self.recent_projects = [p for p in self.recent_projects if p != path_to_remove]
        self._filter_projects()

        if not self.recent_projects:
            self.info_label.config(text="Browse for a project folder to get started")

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()