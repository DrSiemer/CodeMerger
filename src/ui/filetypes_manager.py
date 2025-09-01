import tkinter as tk
import time
import re
from tkinter import Toplevel, Frame, Label, Entry, messagebox, ttk
from ..core.utils import load_all_filetypes, save_filetypes
from ..core.paths import ICON_PATH
from .custom_widgets import RoundedButton
from .. import constants as c


class FiletypesManagerWindow(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.filetypes_data = load_all_filetypes()
        self.last_tree_click_time = 0

        # --- Style Definitions ---
        font_family = "Segoe UI"
        font_normal = (font_family, 12)
        font_button = (font_family, 16)

        # --- Window Setup ---
        self.title("Manage Filetypes")
        self.iconbitmap(ICON_PATH)
        self.geometry("450x550")
        self.transient(parent)
        self.grab_set()
        self.configure(bg=c.DARK_BG)

        # --- UI Layout ---
        main_frame = Frame(self, padx=15, pady=15, bg=c.DARK_BG)
        main_frame.pack(fill='both', expand=True)

        tree_frame = Frame(main_frame, bg=c.DARK_BG)
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        Label(tree_frame, text="Allowed Filetypes (double click to toggle)", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal).pack(anchor='w', pady=(0,5))

        # --- Treeview Styling ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background=c.TEXT_INPUT_BG, foreground=c.TEXT_COLOR, fieldbackground=c.TEXT_INPUT_BG, borderwidth=0, font=font_normal, rowheight=25)
        style.map("Treeview", background=[('selected', c.BTN_BLUE)], foreground=[('selected', c.BTN_BLUE_TEXT)])
        style.configure("Treeview.Heading", font=(font_family, 12, 'bold')) # Not used here, but good practice

        self.tree = ttk.Treeview(tree_frame, show='tree', selectmode='browse')
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        tree_scroll.pack(side='right', fill='y')
        self.tree.config(yscrollcommand=tree_scroll.set)

        # --- Add/Delete Buttons ---
        list_button_frame = Frame(main_frame, bg=c.DARK_BG)
        list_button_frame.pack(fill='x', pady=5)
        self.delete_button = RoundedButton(list_button_frame, text="Delete Selected", command=self.delete_selected_filetype, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button)
        self.delete_button.pack(side='right')
        self.delete_button.set_state('disabled') # Start disabled

        # --- Add New Filetype ---
        add_frame = Frame(main_frame, bg=c.DARK_BG)
        add_frame.pack(fill='x', pady=10)
        Label(add_frame, text="Add new:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal).pack(side='left', padx=(0, 5))
        self.add_entry = Entry(add_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=font_normal)
        self.add_entry.pack(side='left', expand=True, fill='x', ipady=4)
        RoundedButton(add_frame, text="Add", command=self.add_new_filetype, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button).pack(side='left', padx=(10, 0))

        # --- Main Action Button ---
        RoundedButton(self, text="Save and Close", command=self.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=font_button).pack(pady=10)

        # --- Bindings ---
        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.populate_tree()

    def populate_tree(self):
        selection = self.tree.selection()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.filetypes_data.sort(key=lambda x: x['ext'])
        for item in self.filetypes_data:
            check_char = "☑" if item['active'] else "☐"
            display_text = f"{check_char} {item['ext']}"
            self.tree.insert('', 'end', text=display_text, iid=item['ext'])
        if selection:
            try:
                self.tree.selection_set(selection)
            except tk.TclError:
                pass

    def on_tree_selection_change(self, event=None):
        state = 'normal' if self.tree.selection() else 'disabled'
        self.delete_button.set_state(state)

    def handle_tree_click(self, event):
        current_time = time.time()
        time_diff = current_time - self.last_tree_click_time
        self.last_tree_click_time = current_time
        if time_diff < 0.4:
            self.toggle_active_state_for_selected()
            self.last_tree_click_time = 0

    def toggle_active_state_for_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        item_iid = selection[0]
        for item in self.filetypes_data:
            if item['ext'] == item_iid:
                item['active'] = not item['active']
                break
        self.populate_tree()

    def add_new_filetype(self):
        new_ext = self.add_entry.get().strip().lower()
        if not new_ext:
            messagebox.showwarning("Input Error", "Extension or filename cannot be empty.", parent=self)
            return
        if re.search(r'[\\/*?:"<>|]', new_ext):
            messagebox.showwarning("Invalid Characters", "Extensions or filenames cannot contain \\ / * ? : \" < > |", parent=self)
            return
        if any(item['ext'] == new_ext for item in self.filetypes_data):
            messagebox.showwarning("Duplicate", f"The entry '{new_ext}' already exists.", parent=self)
            return
        self.filetypes_data.append({"ext": new_ext, "active": True})
        self.add_entry.delete(0, 'end')
        self.populate_tree()

    def delete_selected_filetype(self):
        """
        Deletes the selected filetype(s).
        """
        selected_iids = self.tree.selection()
        if not selected_iids:
            return
        self.filetypes_data = [item for item in self.filetypes_data if item['ext'] not in selected_iids]
        self.populate_tree()

    def on_closing(self):
        """
        Handles the window close event (clicking the 'X' button).
        """
        saved_data = sorted(load_all_filetypes(), key=lambda x: (x['ext'], x['active']))
        current_data = sorted(self.filetypes_data, key=lambda x: (x['ext'], x['active']))

        if saved_data != current_data:
            if messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Save before closing?", parent=self):
                self.save_and_close()
                return

        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()

    def save_and_close(self):
        """Saves the configuration and then closes the window."""
        save_filetypes(self.filetypes_data)
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()