from tkinter import Toplevel, Frame, Label, messagebox
from .. import constants as c
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_text import ScrollableText
from ..core import change_applier
from .window_utils import position_window

class PasteChangesDialog(Toplevel):
    def __init__(self, parent, project_base_dir):
        super().__init__(parent)
        self.parent = parent
        self.base_dir = project_base_dir
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title("Paste and Apply File Changes")
        self.iconbitmap(ICON_PATH)
        self.result = None

        self.configure(bg=c.DARK_BG)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        Label(
            main_frame,
            text="Paste the markdown from the language model below.",
            wraplength=550, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR
        ).grid(row=0, column=0, pady=(0, 10), sticky='w')

        self.text_widget = ScrollableText(
            main_frame, height=15, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL
        )
        self.text_widget.grid(row=1, column=0, sticky='nsew', pady=5)
        self.text_widget.text_widget.focus_set()

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=2, column=0, pady=(15, 0), sticky='e')

        ok_button = RoundedButton(
            button_frame, text="Apply Changes", command=self.on_apply,
            bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL,
            width=140, height=30, cursor='hand2'
        )
        ok_button.pack(side='right')

        cancel_button = RoundedButton(
            button_frame, text="Cancel", command=self.on_cancel,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL,
            width=90, height=30, cursor='hand2'
        )
        cancel_button.pack(side='right', padx=(0, 10))

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.bind("<Escape>", self.on_cancel)

        self.geometry("600x500")
        self.minsize(500, 400)
        position_window(self)
        self.deiconify()
        self.wait_window(self)

    def on_apply(self):
        markdown_text = self.text_widget.get('1.0', 'end-1c')
        if not markdown_text.strip():
            messagebox.showwarning("Input Error", "The text input cannot be empty.", parent=self)
            return

        success, message = change_applier.apply_changes_from_markdown(self.base_dir, markdown_text)

        if success:
            messagebox.showinfo("Success", message, parent=self.parent)
            self.destroy()
        else:
            messagebox.showerror("Error", message, parent=self)

    def on_cancel(self, event=None):
        self.destroy()