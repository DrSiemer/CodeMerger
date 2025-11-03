import os
import tkinter as tk
from tkinter import Toplevel, Frame, Label, filedialog, StringVar, Entry
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
    Features a scrollable list and a search filter.
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

        # --- Search Bar ---
        self.search_frame = Frame(self, bg=c.DARK_BG, padx=20)
        self.search_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        Label(self.search_frame, text="Search:", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='left')
        self.search_var = StringVar()
        search_entry = Entry(self.search_frame, textvariable=self.search_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        search_entry.pack(side='left', fill='x', expand=True, padx=(5,0), ipady=3)
        self.search_var.trace_add('write', self._filter_projects)

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
        search_entry.focus_set()

    def _on_drag(self, event):
        """Updates the stored position when the window is moved by the user."""
        if self.state() == 'normal':
            self.current_x = self.winfo_x()
            self.current_y = self.winfo_y()

    def _filter_projects(self, *args):
        query = self.search_var.get().lower()
        filtered_list = [
            path for path in self.recent_projects
            if not query or query in os.path.basename(path).lower() or query in path.lower()
        ]
        self._populate_projects(filtered_list)

    def _populate_projects(self, project_list):
        for widget in self.project_widgets:
            widget.destroy()
        self.project_widgets.clear()

        for path in project_list:
            entry_frame = self._create_recent_dir_entry(path)
            self.project_widgets.append(entry_frame)

        self._adjust_height()

    def _adjust_height(self):
        self.update_idletasks()

        if self.non_list_height == 0:
            h_info = self.info_label.winfo_reqheight()
            h_search = self.search_frame.winfo_reqheight()
            h_button = self.browse_btn.winfo_reqheight()
            total_padding = 5 + 10 + 20 + 20
            self.non_list_height = h_info + h_search + h_button + total_padding

        num_items = len(self.project_widgets)
        list_items_height = 0
        if num_items > 0:
            first_item = self.project_widgets[0]
            first_item.update_idletasks()
            item_height = first_item.winfo_reqheight() + 6
            max_visible_items = 10
            visible_items = min(num_items, max_visible_items)
            list_items_height = visible_items * item_height

        final_height = self.non_list_height + list_items_height

        x, y = self.current_x, self.current_y

        win_w, win_h = self.dialog_width, final_height
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

    def _create_recent_dir_entry(self, path):
        entry_frame = Frame(self.recent_dirs_frame, bg=self.app_bg_color)
        entry_frame.pack(fill='x', padx=20, pady=3)

        pc = ProjectConfig(path)
        pc.load()
        display_text = pc.project_name

        logo_image = self.parent.assets.create_masked_logo_small(pc.project_color)
        color_swatch = Label(entry_frame, image=logo_image, bg=self.app_bg_color)
        color_swatch.image = logo_image # Prevent garbage collection
        color_swatch.pack(side='left', padx=(0, 10))

        btn = RoundedButton(
            entry_frame, text=display_text, command=lambda p=path: self.select_and_close(p),
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, height=32, cursor='hand2'
        )
        btn.pack(side='left', expand=True, fill='x')
        btn.bind("<Enter>", lambda e, p=path: self.show_path_tooltip(e, p))
        btn.bind("<Leave>", self.hide_path_tooltip)

        if assets.trash_icon_image:
            remove_btn = RoundedButton(
                parent=entry_frame, command=lambda p=path, w=entry_frame: self.remove_and_update_dialog(p, w),
                image=assets.trash_icon_image, bg=c.BTN_GRAY_BG, width=32, height=32, cursor='hand2'
            )
            remove_btn.pack(side='left', padx=(10, 0))

        return entry_frame

    def show_path_tooltip(self, event, path):
        if self.tooltip: self.tooltip.destroy()
        x, y = event.widget.winfo_rootx(), event.widget.winfo_rooty() + event.widget.winfo_height() + 1
        self.tooltip = Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = Label(self.tooltip, text=path, justify='left', bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1, font=c.FONT_TOOLTIP, padx=4, pady=2)
        label.pack(ipadx=2, ipady=1)

    def hide_path_tooltip(self, event):
        if self.tooltip: self.tooltip.destroy(); self.tooltip = None

    def select_and_close(self, path):
        if self.on_select_callback: self.on_select_callback(path)
        self._close_and_save_geometry()

    def browse_for_new_dir(self):
        new_path = filedialog.askdirectory(title="Select Project Folder", parent=self)
        if new_path: self.select_and_close(new_path)

    def remove_and_update_dialog(self, path_to_remove, widget_to_destroy):
        self.on_remove_callback(path_to_remove)
        self.recent_projects = [p for p in self.recent_projects if p != path_to_remove]
        self._filter_projects()

        if not self.recent_projects:
            self.info_label.config(text="Browse for a project folder to get started")