from tkinter import Toplevel, Frame, Label, Entry, StringVar, BooleanVar, messagebox, ttk
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.paths import ICON_PATH
from .style_manager import apply_dark_theme

class NewProfileDialog(Toplevel):
    def __init__(self, parent, existing_profile_names):
        super().__init__(parent)
        self.parent = parent
        self.existing_names_lower = [name.lower() for name in existing_profile_names]
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title("Create New Profile")
        self.iconbitmap(ICON_PATH)
        self.result = None

        self.configure(bg=c.DARK_BG)
        apply_dark_theme(self)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        Label(main_frame, text="Enter a unique name for the new profile:", bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=(0, 5), anchor='w')

        self.entry_var = StringVar()
        self.entry = Entry(main_frame, textvariable=self.entry_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.entry.pack(pady=5, fill='x', ipady=4)
        self.entry.focus_set()

        options_frame = Frame(main_frame, bg=c.DARK_BG)
        options_frame.pack(fill='x', pady=(15, 0))

        self.copy_files_var = BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Copy current file selection", variable=self.copy_files_var, style='Dark.TCheckbutton').pack(anchor='w')

        self.copy_wrappers_var = BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Copy current wrapper texts", variable=self.copy_wrappers_var, style='Dark.TCheckbutton').pack(anchor='w')

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.pack(pady=(20, 0), fill='x', anchor='e')
        right_buttons_frame = Frame(button_frame, bg=c.DARK_BG)
        right_buttons_frame.pack(side='right')

        ok_button = RoundedButton(right_buttons_frame, text="Create", command=self.on_ok, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        ok_button.pack(side='right')

        cancel_button = RoundedButton(right_buttons_frame, text="Cancel", command=self.on_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        cancel_button.pack(side='right', padx=(0, 10))

        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_cancel)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.update_idletasks()
        required_height = self.winfo_reqheight()
        dialog_width = 400
        self.geometry(f"{dialog_width}x{required_height}")
        self.resizable(False, False)

        parent_x, parent_y = self.parent.winfo_rootx(), self.parent.winfo_rooty()
        parent_w, parent_h = self.parent.winfo_width(), self.parent.winfo_height()
        x = parent_x + (parent_w - dialog_width) // 2
        y = parent_y + (parent_h - required_height) // 2
        self.geometry(f"+{x}+{y}")

        self.deiconify()
        self.wait_window(self)

    def on_ok(self, event=None):
        name = self.entry_var.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Profile name cannot be empty.", parent=self)
            return
        if name.lower() in self.existing_names_lower:
            messagebox.showwarning("Name Exists", f"A profile named '{name}' already exists.", parent=self)
            return

        self.result = {
            "name": name,
            "copy_files": self.copy_files_var.get(),
            "copy_wrappers": self.copy_wrappers_var.get()
        }
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()