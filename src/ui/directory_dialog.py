import os
from tkinter import Toplevel, Frame, Label, Button, filedialog
from ..core.project_config import ProjectConfig

class DirectoryDialog(Toplevel):
    """
    A dialog window for selecting a recent or new project directory
    """
    def __init__(self, parent, app_bg_color, recent_projects, on_select_callback, on_remove_callback):
        super().__init__(parent)
        self.parent = parent
        self.app_bg_color = app_bg_color
        self.recent_projects = recent_projects
        self.on_select_callback = on_select_callback
        self.on_remove_callback = on_remove_callback
        self.tooltip = None

        # --- Style Definitions ---
        text_color = '#FFFFFF'
        btn_bg = '#CCCCCC'
        btn_fg = '#333333'

        self.title("Select project")
        self.transient(parent)
        self.grab_set()
        self.configure(bg=self.app_bg_color)

        screen_width = self.winfo_screenwidth()
        self.dialog_width = max(350, 250)

        if self.recent_projects:
            message = "Select a recent project or browse for a new one"
            dialog_height = 280
        else:
            message = "Browse for a project folder to get started"
            dialog_height = 120

        self.geometry(f"{self.dialog_width}x{dialog_height}")
        self.info_label = Label(self, text=message, padx=10, pady=10, bg=self.app_bg_color, fg=text_color, font=('Helvetica', 9))
        self.info_label.pack(pady=(0, 5))

        self.recent_dirs_frame = Frame(self, bg=self.app_bg_color)

        if self.recent_projects:
            self.recent_dirs_frame.pack(fill='x', expand=False, pady=5)
            for path in self.recent_projects:
                self.create_recent_dir_entry(path, btn_bg, btn_fg)

        browse_btn = Button(self, text="Select Project folder...", command=self.browse_for_new_dir, bg=btn_bg, fg=btn_fg, relief='flat', padx=10)
        browse_btn.pack(pady=10, padx=10)

    def create_recent_dir_entry(self, path, btn_bg, btn_fg):
        """Creates a single row in the recent projects list"""
        entry_frame = Frame(self.recent_dirs_frame, bg=self.app_bg_color)
        entry_frame.pack(fill='x', padx=10, pady=2)

        pc = ProjectConfig(path)
        pc.load()
        display_text = pc.project_name

        color_swatch = Frame(entry_frame, width=20, height=20, bg=pc.project_color, relief='sunken', borderwidth=1)
        color_swatch.pack(side='left', padx=(0, 5))
        color_swatch.pack_propagate(False)

        btn = Button(entry_frame, text=display_text, command=lambda p=path: self.select_and_close(p), anchor='w', justify='left', bg=btn_bg, fg=btn_fg, relief='flat', font=('Helvetica', 9))
        btn.pack(side='left', expand=True, fill='x')

        btn.bind("<Enter>", lambda e, p=path: self.show_path_tooltip(e, p))
        btn.bind("<Leave>", self.hide_path_tooltip)

        remove_btn = Button(entry_frame, text="Del", command=lambda p=path, w=entry_frame: self.remove_and_update_dialog(p, w), width=4, bg=btn_bg, fg=btn_fg, relief='flat', font=('Helvetica', 8))
        remove_btn.pack(side='left', padx=(5, 0))

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
                      background="#ffffe0", relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
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
        self.on_remove_callback(path_to_remove)
        widget_to_destroy.destroy()

        # Update the list in place to check if it's empty
        self.recent_projects.remove(path_to_remove)

        if not self.recent_projects:
            self.info_label.config(text="Browse for a project folder to get started")
            self.geometry(f"{self.dialog_width}x120")
            self.recent_dirs_frame.pack_forget()