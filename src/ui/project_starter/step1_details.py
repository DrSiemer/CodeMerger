import tkinter as tk
from tkinter import filedialog
from ... import constants as c
from ..widgets.rounded_button import RoundedButton

class Step1DetailsView(tk.Frame):
    def __init__(self, parent, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.project_data = project_data
        self.config(padx=10, pady=10)

        tk.Label(self, text="Project Details", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=10, anchor="w")
        tk.Label(self, text="Enter the initial details for your new project.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(pady=5, anchor="w")

        form_grid = tk.Frame(self, bg=c.DARK_BG)
        form_grid.pack(pady=20, fill="x", anchor="w")

        form_grid.grid_columnconfigure(0, minsize=200)
        form_grid.grid_columnconfigure(1, weight=1)

        # Row 0: Project Name
        tk.Label(form_grid, text="Project Name:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(form_grid, textvariable=self.project_data["name"], width=50, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief="flat", font=c.FONT_NORMAL).grid(row=0, column=1, padx=5, pady=5, ipady=4, sticky="ew")

        # Row 1: Parent Folder
        tk.Label(form_grid, text="Parent Folder:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        folder_frame = tk.Frame(form_grid, bg=c.DARK_BG)
        folder_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)

        tk.Entry(folder_frame, textvariable=self.project_data["parent_folder"], bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief="flat", font=c.FONT_NORMAL).grid(row=0, column=0, ipady=4, sticky="ew")
        RoundedButton(folder_frame, text="Browse", command=self._browse_folder, height=28, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2").grid(row=0, column=1, padx=(5, 0))

        # Row 2: Code Stack
        tk.Label(form_grid, text="Code Stack:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(form_grid, textvariable=self.project_data["stack"], width=50, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief="flat", font=c.FONT_NORMAL).grid(row=2, column=1, padx=5, pady=5, ipady=4, sticky="ew")

        # Row 3: Description
        tk.Label(form_grid, text="Short Project Description:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        desc_frame = tk.Frame(form_grid, bg=c.TEXT_INPUT_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        desc_frame.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.description_text_widget = tk.Text(
            desc_frame, wrap=tk.WORD, height=3, width=50, relief="flat", borderwidth=0,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL
        )
        self.description_text_widget.pack(expand=True, fill="both", padx=5, pady=5)

        if self.project_data["description"]:
            self.description_text_widget.insert("1.0", self.project_data["description"])

    def _browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.project_data["parent_folder"].set(folder_selected)

    def get_description(self):
        if self.description_text_widget and self.description_text_widget.winfo_exists():
            return self.description_text_widget.get("1.0", tk.END).strip()
        return ""