import tkinter as tk
from pathlib import Path
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..tooltip import ToolTip
from ...core.project_config import _calculate_font_color

class SuccessView(tk.Frame):
    def __init__(self, parent, project_folder_name, files_created, on_start_work_callback, parent_folder, project_color=None):
        super().__init__(parent, bg=c.DARK_BG, padx=20, pady=20)

        accent_color = project_color if project_color else c.BTN_BLUE
        font_mode = _calculate_font_color(accent_color)
        text_color = "#FFFFFF" if font_mode == 'light' else "#000000"

        tk.Label(self, text="Project Created Successfully!", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=10)

        base_path = Path(parent_folder)
        project_path = base_path / project_folder_name
        tk.Label(self, text=f"Your new project is located at:", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(pady=5)

        self.path_entry = tk.Entry(self, font=c.FONT_NORMAL, relief="flat", justify="center")
        self.path_entry.insert(0, str(project_path.resolve()))
        self.path_entry.config(
            state="readonly",
            readonlybackground=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT
        )
        self.path_entry.pack(fill='x', pady=5)

        tk.Label(self, text="Files Created:", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=(20, 5), anchor="w")

        listbox = tk.Listbox(
            self, height=15, relief="flat",
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            selectbackground=c.BTN_BLUE, selectforeground=c.BTN_BLUE_TEXT
        )
        for f in files_created:
            listbox.insert(tk.END, f)
        listbox.pack(expand=True, fill="both", pady=5)

        btn_row = tk.Frame(self, bg=c.DARK_BG)
        btn_row.pack(pady=20)

        self.activate_btn = RoundedButton(
            btn_row,
            text="Activate Project in CodeMerger",
            command=on_start_work_callback,
            bg=accent_color,
            fg=text_color,
            font=c.FONT_BUTTON,
            height=50,
            width=350,
            cursor="hand2"
        )
        self.activate_btn.pack(side="top")
        ToolTip(self.activate_btn, "Activate this project and close the wizard", delay=500)

        self.exit_btn = RoundedButton(
            btn_row,
            text="Exit",
            command=lambda: self.master.master.on_closing(),
            bg=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT,
            font=c.FONT_NORMAL,
            height=30,
            width=100,
            hollow=True,
            cursor="hand2"
        )
        self.exit_btn.pack(side="top", pady=(15, 0))
        ToolTip(self.exit_btn, "Exit the Project Starter", delay=500)

        # Open in Explorer button next to path
        self.open_btn = RoundedButton(
            self,
            text="Open Folder",
            command=lambda: self._open_path(str(project_path.resolve())),
            bg=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON,
            height=26,
            cursor="hand2"
        )
        self.open_btn.place(in_=self.path_entry, relx=1.0, rely=0.5, anchor="e", x=-5)

    def _open_path(self, path):
        import os, sys, subprocess
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass