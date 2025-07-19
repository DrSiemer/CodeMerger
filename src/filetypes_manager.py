import tkinter as tk
from tkinter import Toplevel, Frame, Label, Button, Entry, messagebox, ttk
from .utils import load_all_filetypes, save_filetypes

class FiletypesManagerWindow(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.filetypes_data = load_all_filetypes()

        # --- Window Setup ---
        self.title("Manage Filetypes")
        self.geometry("450x550")
        self.transient(parent)
        self.grab_set()

        # --- UI Layout ---
        main_frame = Frame(self, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        # --- Filetypes List ---
        tree_frame = Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        Label(tree_frame, text="Allowed Filetypes").pack(anchor='w')

        self.tree = ttk.Treeview(tree_frame, columns=('ext',), show='tree headings')
        self.tree.heading('ext', text='Extension')
        self.tree.pack(side='left', fill='both', expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        tree_scroll.pack(side='right', fill='y')
        self.tree.config(yscrollcommand=tree_scroll.set)

        # --- Add/Delete Buttons ---
        list_button_frame = Frame(main_frame)
        list_button_frame.pack(fill='x', pady=5)
        self.delete_button = Button(list_button_frame, text="Delete Selected", command=self.delete_selected_filetype, state='disabled')
        self.delete_button.pack(side='right')

        # --- Add New Filetype ---
        add_frame = Frame(main_frame)
        add_frame.pack(fill='x', pady=5)
        Label(add_frame, text="Add new:").pack(side='left', padx=(0, 5))
        self.add_entry = Entry(add_frame)
        self.add_entry.pack(side='left', expand=True, fill='x')
        Button(add_frame, text="Add", command=self.add_new_filetype).pack(side='left', padx=(5, 0))

        # --- Main Action Button ---
        Button(self, text="Save and Close", command=self.save_and_close).pack(pady=10)

        # --- Bindings ---
        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.populate_tree()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.filetypes_data.sort(key=lambda x: x['ext'])
        for item in self.filetypes_data:
            check_char = "☑" if item['active'] else "☐"
            display_text = f"{check_char} {item['ext']}"
            self.tree.insert('', 'end', values=(display_text,), iid=item['ext'])

    def on_tree_selection_change(self, event=None):
        self.delete_button['state'] = 'normal' if self.tree.selection() else 'disabled'

    def handle_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        item_iid = self.tree.identify_row(event.y)
        if not item_iid: return

        for item in self.filetypes_data:
            if item['ext'] == item_iid:
                item['active'] = not item['active']
                break

        self.populate_tree()
        self.tree.selection_set(item_iid)

    def add_new_filetype(self):
        new_ext = self.add_entry.get().strip().lower()
        if not new_ext:
            messagebox.showwarning("Input Error", "Extension cannot be empty.", parent=self)
            return
        if not new_ext.startswith('.'):
            new_ext = '.' + new_ext

        if any(item['ext'] == new_ext for item in self.filetypes_data):
            messagebox.showwarning("Duplicate", f"The extension '{new_ext}' already exists.", parent=self)
            return

        self.filetypes_data.append({"ext": new_ext, "active": True})
        self.add_entry.delete(0, 'end')
        self.populate_tree()

    def delete_selected_filetype(self):
        selected_iids = self.tree.selection()
        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(selected_iids)} filetype(s)?", parent=self):
            return

        self.filetypes_data = [item for item in self.filetypes_data if item['ext'] not in selected_iids]
        self.populate_tree()

    def on_closing(self):
        saved_data = sorted(load_all_filetypes(), key=lambda x: x['ext'])
        current_data = sorted(self.filetypes_data, key=lambda x: x['ext'])
        if saved_data != current_data:
            if messagebox.askyesno("Unsaved Changes", "Save changes before closing?", parent=self):
                self.save_and_close()
                return

        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()

    def save_and_close(self):
        save_filetypes(self.filetypes_data)
        messagebox.showinfo("Saved", "Filetype configuration has been saved.", parent=self.parent)
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()