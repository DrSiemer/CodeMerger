import tkinter as tk
import time
import re
import json
from tkinter import Toplevel, Frame, Label, Entry, messagebox, ttk, StringVar
from ..core.utils import load_all_filetypes, save_filetypes
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from .window_utils import position_window, save_window_geometry
from .tooltip import ToolTip

class FiletypesManagerWindow(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.filetypes_data = load_all_filetypes()
        self.last_tree_click_time = 0
        self.tooltip_window = None

        # --- Window Setup ---
        self.title("Manage Filetypes")
        self.iconbitmap(ICON_PATH)
        self.geometry(c.FILETYPES_WINDOW_DEFAULT_GEOMETRY)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

        # --- UI Layout ---
        main_frame = Frame(self, padx=15, pady=15, bg=c.DARK_BG)
        main_frame.pack(fill='both', expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        Label(main_frame, text="Allowed Filetypes (double click to toggle)", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=0, column=0, sticky='w', pady=(0,5))

        tree_frame = Frame(main_frame, bg=c.DARK_BG)
        tree_frame.grid(row=1, column=0, sticky='nsew', pady=(5, 0))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # --- Treeview Styling ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background=c.TEXT_INPUT_BG, foreground=c.TEXT_COLOR, fieldbackground=c.TEXT_INPUT_BG, borderwidth=0, font=c.FONT_NORMAL, rowheight=25)
        style.map("Treeview", background=[('selected', c.BTN_BLUE)], foreground=[('selected', c.BTN_BLUE_TEXT)])

        self.tree = ttk.Treeview(tree_frame, show='tree', selectmode='extended')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.config(yscrollcommand=self.tree_scroll.set)

        # --- Action Button (Delete or Activate/Deactivate) ---
        action_button_frame = Frame(main_frame, bg=c.DARK_BG)
        action_button_frame.grid(row=2, column=0, sticky='ew', pady=(10, 10))
        self.action_button = RoundedButton(action_button_frame, text="", command=self._on_action_button_click, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        self.action_button.pack(fill='x', expand=True)
        self.action_button_tooltip = ToolTip(self.action_button, text="", delay=500)

        # --- Input Section for Adding New Filetypes ---
        input_section_frame = Frame(main_frame, bg=c.DARK_BG)
        input_section_frame.grid(row=3, column=0, sticky='ew', pady=(15, 5))
        input_section_frame.columnconfigure(1, weight=1)

        # Row 0: Add new extension
        Label(input_section_frame, text="Add new:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.add_entry_var = StringVar()
        self.add_entry = Entry(input_section_frame, textvariable=self.add_entry_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.add_entry.grid(row=0, column=1, sticky='ew', ipady=4)
        self.add_entry_var.trace_add('write', self._update_add_button_state)

        # Row 1: Add description
        Label(input_section_frame, text="Description:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(5,0))
        self.new_desc_var = StringVar()
        self.desc_entry = Entry(input_section_frame, textvariable=self.new_desc_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.desc_entry.grid(row=1, column=1, sticky='ew', ipady=4, pady=(5,0))

        # Row 2: Add button, aligned to the right
        add_button_frame = Frame(input_section_frame, bg=c.DARK_BG)
        add_button_frame.grid(row=2, column=1, sticky='e', pady=(10, 0))
        self.add_button = RoundedButton(add_button_frame, text="Add", command=self.add_new_filetype, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        self.add_button.pack()
        self.add_button.set_state('disabled')

        # --- Bindings ---
        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Escape>', lambda e: self.on_closing())
        self.bind('<Configure>', self._on_resize)

        self.populate_tree()
        self.on_tree_selection_change() # Initial state setup

        self._position_window()
        self.deiconify()

    def _save_changes(self):
        save_filetypes(self.filetypes_data)

    def _update_add_button_state(self, *args):
        if self.add_entry_var.get().strip():
            self.add_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.add_button.set_state('normal')
        else:
            self.add_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            self.add_button.set_state('disabled')

    def _on_resize(self, event=None):
        self.after_idle(self._manage_scrollbar)

    def _manage_scrollbar(self):
        self.update_idletasks()
        style = ttk.Style()
        try: row_height = style.lookup("Treeview", "rowheight")
        except tk.TclError: row_height = 25
        content_height = len(self.filetypes_data) * row_height
        visible_height = self.tree.winfo_height()
        if content_height > visible_height:
            if not self.tree_scroll.winfo_ismapped(): self.tree_scroll.grid(row=0, column=1, sticky='ns')
        else:
            if self.tree_scroll.winfo_ismapped(): self.tree_scroll.grid_forget()

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

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
            try: self.tree.selection_set(selection)
            except tk.TclError:
                pass
        self.after_idle(self._manage_scrollbar)

    def on_tree_selection_change(self, event=None):
        selection = self.tree.selection()

        if not selection:
            self.action_button.set_state('disabled')
            self.action_button.config(text="Select a Filetype")
            self.action_button_tooltip.text = ""
            return

        selected_items = [item for item in self.filetypes_data if item['ext'] in selection]
        all_default = all(item.get('default', False) for item in selected_items)
        all_custom = all(not item.get('default', False) for item in selected_items)

        if all_default:
            self.action_button.set_state('normal')
            self.action_button.config(text="Activate/Deactivate")
            self.action_button_tooltip.text = "Toggle the 'active' status for the selected default filetypes."
        elif all_custom:
            self.action_button.set_state('normal')
            self.action_button.config(text="Delete Selected")
            self.action_button_tooltip.text = ""
        else: # Mixed selection
            self.action_button.set_state('disabled')
            self.action_button.config(text="Action")
            self.action_button_tooltip.text = "Cannot perform action on a mixed selection of default and custom filetypes."

    def handle_tree_click(self, event):
        current_time = time.time()
        time_diff = current_time - self.last_tree_click_time
        self.last_tree_click_time = current_time
        if time_diff < c.DOUBLE_CLICK_INTERVAL_SECONDS:
            self.toggle_active_state_for_selected()
            self.last_tree_click_time = 0

    def _on_action_button_click(self):
        button_text = self.action_button.text
        if button_text == "Delete Selected":
            self.delete_selected_filetype()
        elif button_text == "Activate/Deactivate":
            self.toggle_active_state_for_selected()

    def toggle_active_state_for_selected(self):
        selection = self.tree.selection()
        if not selection: return
        for item_iid in selection:
            for item in self.filetypes_data:
                if item['ext'] == item_iid:
                    item['active'] = not item['active']
                    break
        self.populate_tree()
        self._save_changes()

    def add_new_filetype(self):
        new_ext = self.add_entry.get().strip().lower()
        new_desc = self.new_desc_var.get().strip()

        if not new_ext:
            messagebox.showwarning("Input Error", "Extension or filename cannot be empty.", parent=self)
            return
        if re.search(r'[\\/*?:"<>|]', new_ext):
            messagebox.showwarning("Invalid Characters", "Extensions or filenames cannot contain \\ / * ? : \" < > |", parent=self)
            return
        if any(item['ext'] == new_ext for item in self.filetypes_data):
            messagebox.showwarning("Duplicate", f"The entry '{new_ext}' already exists.", parent=self)
            return

        self.filetypes_data.append({"ext": new_ext, "active": True, "description": new_desc, "default": False})
        self.add_entry.delete(0, 'end')
        self.new_desc_var.set("")
        self.populate_tree()
        self._save_changes()

    def delete_selected_filetype(self):
        selected_iids = self.tree.selection()
        if not selected_iids: return

        for iid in selected_iids:
            for item in self.filetypes_data:
                if item['ext'] == iid and item.get('default', False):
                    # This check is redundant due to button state logic but is a good safeguard
                    messagebox.showwarning("Cannot Delete", f"'{iid}' is a default filetype and cannot be deleted.", parent=self)
                    return

        self.filetypes_data = [item for item in self.filetypes_data if item['ext'] not in selected_iids]
        self.populate_tree()
        self.on_tree_selection_change()
        self._save_changes()

    def on_closing(self):
        if self.on_close_callback:
            self.on_close_callback()
        self._close_and_save_geometry()

    def _on_tree_motion(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            for item in self.filetypes_data:
                if item['ext'] == item_id:
                    desc = item.get('description', '')
                    if desc:
                        self._show_tooltip(event.x_root + 15, event.y_root + 10, desc)
                    else:
                        self._hide_tooltip()
                    return
        self._hide_tooltip()

    def _on_tree_leave(self, event):
        self._hide_tooltip()

    def _show_tooltip(self, x, y, text):
        self._hide_tooltip()
        self.tooltip_window = Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=text, justify='left', background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1, font=c.FONT_TOOLTIP, padx=4, pady=2)
        label.pack()

    def _hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None