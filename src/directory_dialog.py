import os
from tkinter import Toplevel, Frame, Label, Button, filedialog

class DirectoryDialog(Toplevel):
    """
    A dialog window for selecting a recent or new project directory
    """
    def __init__(self, parent, app_bg_color, recent_dirs, on_select_callback, on_remove_callback):
        super().__init__(parent)
        self.parent = parent
        self.app_bg_color = app_bg_color
        self.recent_dirs = recent_dirs
        self.on_select_callback = on_select_callback
        self.on_remove_callback = on_remove_callback

        self.title("Select Directory")
        self.transient(parent)
        self.grab_set()
        self.configure(bg=self.app_bg_color)

        screen_width = self.winfo_screenwidth()
        self.dialog_width = max(400, min(int(screen_width * 0.5), 800))

        # Determine initial message and height based on whether recent directories exist
        if self.recent_dirs:
            message = "Select a recent directory or browse for a new one"
            dialog_height = 280
        else:
            message = "Browse for a directory to get started"
            dialog_height = 120

        self.geometry(f"{self.dialog_width}x{dialog_height}")
        self.info_label = Label(self, text=message, padx=10, pady=10, bg=self.app_bg_color)
        self.info_label.pack(pady=(0, 5))

        # Create a frame for recent directories; it will be shown or hidden as needed
        self.recent_dirs_frame = Frame(self, bg=self.app_bg_color)

        # Populate Recent Directories List (if any)
        if self.recent_dirs:
            self.recent_dirs_frame.pack(fill='x', expand=False, pady=5)
            for path in self.recent_dirs:
                self.create_recent_dir_entry(path)

        # Browse Button
        browse_btn = Button(self, text="Browse for Directory...", command=self.browse_for_new_dir)
        browse_btn.pack(pady=10, padx=10)

    def create_recent_dir_entry(self, path):
        """Creates a single row in the recent directories list"""
        entry_frame = Frame(self.recent_dirs_frame, bg=self.app_bg_color)
        entry_frame.pack(fill='x', padx=10, pady=2)
        btn = Button(entry_frame, text=path, command=lambda p=path: self.select_and_close(p), anchor='w', justify='left')
        btn.pack(side='left', expand=True, fill='x')
        remove_btn = Button(entry_frame, text="X", command=lambda p=path, w=entry_frame: self.remove_and_update_dialog(p, w), width=3)
        remove_btn.pack(side='left', padx=(5, 0))

    def select_and_close(self, path):
        """Final action: update active dir and close the selection dialog"""
        if self.on_select_callback:
            self.on_select_callback(path)
        self.destroy()

    def browse_for_new_dir(self):
        """Opens file dialog and processes the result, handling cancellation"""
        new_path = filedialog.askdirectory(title="Select Project Directory", parent=self)
        if new_path:  # Only proceed if a directory was actually selected
            self.select_and_close(new_path)

    def remove_and_update_dialog(self, path_to_remove, widget_to_destroy):
        """Removes a recent directory and dynamically updates the dialog's UI"""
        self.on_remove_callback(path_to_remove)
        self.recent_dirs.remove(path_to_remove)
        widget_to_destroy.destroy()

        if not self.recent_dirs:
            self.info_label.config(text="Browse for a directory to get started")
            self.geometry(f"{self.dialog_width}x120")
            self.recent_dirs_frame.pack_forget() # Hide the frame for a clean layout