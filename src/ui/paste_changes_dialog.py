import os
from tkinter import Toplevel, Frame, Label, messagebox
from .. import constants as c
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_text import ScrollableText
from ..core import change_applier
from .window_utils import position_window
from .custom_error_dialog import CustomErrorDialog

class PasteChangesDialog(Toplevel):
    def __init__(self, parent, project_base_dir, status_var, initial_content=None):
        super().__init__(parent)
        self.parent = parent
        self.base_dir = project_base_dir
        self.status_var = status_var
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

        if initial_content:
            self.text_widget.insert('1.0', initial_content)

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
        self.lift()
        self.focus_force()
        self.text_widget.text_widget.focus_set()
        self.wait_window(self)

    def on_apply(self):
        markdown_text = self.text_widget.get('1.0', 'end-1c')
        if not markdown_text.strip():
            messagebox.showwarning("Input Error", "The text input cannot be empty.", parent=self)
            return

        plan = change_applier.parse_and_plan_changes(self.base_dir, markdown_text)

        status = plan.get('status')
        message = plan.get('message')

        if status == 'ERROR':
            CustomErrorDialog(self, title="Error", message=message)
            return

        if status == 'CONFIRM_CREATION':
            creations = plan.get('creations', {})
            # Get relative paths for display in the confirmation dialog
            creation_rel_paths = [os.path.relpath(p, self.base_dir).replace('\\', '/') for p in creations.keys()]

            confirm_message = (
                f"This operation will create {len(creations)} new file(s):\n\n"
                f" - " + "\n - ".join(creation_rel_paths) +
                "\n\nDo you want to proceed?"
            )

            if not messagebox.askyesno("Confirm New Files", confirm_message, parent=self):
                self.status_var.set("Operation cancelled by user.")
                return

        # Proceed if status was 'SUCCESS' or if user confirmed creation
        updates = plan.get('updates', {})
        creations = plan.get('creations', {})

        success, final_message = change_applier.execute_plan(updates, creations)

        if success:
            self.status_var.set(final_message)
            self.destroy()
        else:
            CustomErrorDialog(self, title="File Write Error", message=final_message)

    def on_cancel(self, event=None):
        self.destroy()