import os
import tkinter as tk
from tkinter import Toplevel, Frame, Label, filedialog
from ..core.project_config import ProjectConfig
from .custom_widgets import RoundedButton
from .. import constants as c

class DirectoryDialog(Toplevel):
    """
    A dialog window for selecting a recent or new project directory
    """
    def __init__(self, parent, app_bg_color, recent_projects, on_select_callback, on_remove_callback, trash_icon_image=None):
        super().__init__(parent)
        self.parent = parent
        self.app_bg_color = app_bg_color # This is c.DARK_BG
        self.recent_projects = recent_projects
        self.on_select_callback = on_select_callback
        self.on_remove_callback = on_remove_callback
        self.trash_icon_image = trash_icon_image
        self.tooltip = None

        # --- Style Definitions ---
        font_family = "Segoe UI"
        font_normal = (font_family, 12)
        font_button = (font_family, 16)

        self.title("Select project")
        self.transient(parent)
        self.grab_set()
        self.configure(bg=self.app_bg_color)
        self.resizable(False, False)

        self.dialog_width = 450

        if self.recent_projects:
            message = "Select a recent project or browse for a new one"
        else:
            message = "Browse for a project folder to get started"

        self.info_label = Label(self, text=message, padx=20, pady=10, bg=self.app_bg_color, fg=c.TEXT_COLOR, font=font_normal)
        self.info_label.pack(pady=(5, 10), anchor='w')

        self.recent_dirs_frame = Frame(self, bg=self.app_bg_color)

        if self.recent_projects:
            self.recent_dirs_frame.pack(fill='x', expand=False, pady=5)
            for path in self.recent_projects:
                self.create_recent_dir_entry(path, font_button)

        browse_btn = RoundedButton(
            self,
            text="Select Project folder...",
            command=self.browse_for_new_dir,
            bg=c.BTN_BLUE,
            fg=c.BTN_BLUE_TEXT,
            font=font_button
        )
        browse_btn.pack(pady=20, padx=20)

        # Update the window to fit the content
        self.update_idletasks()
        required_height = self.winfo_reqheight()
        self.geometry(f"{self.dialog_width}x{required_height}")
        self.bind('<Escape>', lambda e: self.destroy())

    def create_recent_dir_entry(self, path, font):
        """Creates a single row in the recent projects list"""
        entry_frame = Frame(self.recent_dirs_frame, bg=self.app_bg_color)
        entry_frame.pack(fill='x', padx=20, pady=3)

        pc = ProjectConfig(path)
        pc.load()
        display_text = pc.project_name

        color_swatch = Frame(entry_frame, width=28, height=28, bg=pc.project_color, relief='flat')
        color_swatch.pack(side='left', padx=(0, 10))
        color_swatch.pack_propagate(False)

        btn = RoundedButton(
            entry_frame,
            text=display_text,
            command=lambda p=path: self.select_and_close(p),
            bg=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT,
            font=font,
            height=32
        )
        btn.pack(side='left', expand=True, fill='x')

        btn.bind("<Enter>", lambda e, p=path: self.show_path_tooltip(e, p))
        btn.bind("<Leave>", self.hide_path_tooltip)

        if self.trash_icon_image:
            remove_btn = RoundedButton(
                parent=entry_frame,
                command=lambda p=path, w=entry_frame: self.remove_and_update_dialog(p, w),
                image=self.trash_icon_image,
                bg=c.BTN_GRAY_BG,
                width=32,
                height=32
            )
            remove_btn.pack(side='left', padx=(10, 0))


    def show_path_tooltip(self, event, path):
        """Displays a tooltip with the full path of the project"""
        if self.tooltip:
            self.tooltip.destroy()

        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height() + 1

        self.tooltip = Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = Label(self.tooltip, text=path, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"), padx=4, pady=2)
        label.pack(ipadx=2, ipady=1)

    def hide_path_tooltip(self, event):
        """Hides the path tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def select_and_close(self, path):
        """Final action: update active dir and close the selection dialog"""
        if self.on_select_callback:
            self.on_select_callback(path)
        self.destroy()

    def browse_for_new_dir(self):
        """Opens file dialog and processes the result, handling cancellation"""
        new_path = filedialog.askdirectory(title="Select Project Folder", parent=self)
        if new_path:
            self.select_and_close(new_path)

    def remove_and_update_dialog(self, path_to_remove, widget_to_destroy):
        """Removes a recent directory and dynamically updates the dialog's UI"""
        # The callback handles the data model modification in AppState
        self.on_remove_callback(path_to_remove)
        # This function handles the UI update
        widget_to_destroy.destroy()

        # Check if the recent projects list is now empty
        if not self.recent_dirs_frame.winfo_children():
            self.info_label.config(text="Browse for a project folder to get started")
            self.recent_dirs_frame.pack_forget()

        # Update the window to fit the new content size
        self.update_idletasks()
        required_height = self.winfo_reqheight()
        self.geometry(f"{self.dialog_width}x{required_height}")