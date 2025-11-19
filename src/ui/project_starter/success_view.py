import tkinter as tk
from pathlib import Path
from ... import constants as c
from ..widgets.rounded_button import RoundedButton

class SuccessView(tk.Frame):
    def __init__(self, parent, project_folder_name, files_created, on_start_work_callback, parent_folder):
        super().__init__(parent, bg=c.DARK_BG, padx=20, pady=20)

        tk.Label(self, text="Project Created Successfully!", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=10)

        base_path = Path(parent_folder)
        project_path = base_path / project_folder_name
        tk.Label(self, text=f"Your new project is located at:", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(pady=5)

        path_entry = tk.Entry(self, font=c.FONT_NORMAL, relief="flat", justify="center")
        path_entry.insert(0, str(project_path.resolve()))
        path_entry.config(
            state="readonly",
            readonlybackground=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT
        )
        path_entry.pack(fill='x', pady=5)

        tk.Label(self, text="Files Created:", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=(20, 5), anchor="w")

        listbox = tk.Listbox(
            self, height=15, relief="flat",
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            selectbackground=c.BTN_BLUE, selectforeground=c.BTN_BLUE_TEXT
        )
        for f in files_created:
            listbox.insert(tk.END, f)
        listbox.pack(expand=True, fill="both", pady=5)

        RoundedButton(self, text="Open Project in CodeMerger", command=on_start_work_callback, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=40, cursor="hand2").pack(pady=20)