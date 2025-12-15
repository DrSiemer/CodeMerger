import tkinter as tk
from tkinter import filedialog
from ... import constants as c
from ..widgets.rounded_button import RoundedButton

class Step1DetailsView(tk.Frame):
    def __init__(self, parent, project_data, wizard_controller=None):
        super().__init__(parent, bg=c.DARK_BG)
        self.project_data = project_data
        self.wizard_controller = wizard_controller # Access to wizard methods
        self.config(padx=10, pady=10)

        tk.Label(self, text="Project Details", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=10, anchor="w")
        tk.Label(self, text="Enter the initial details for your new project.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(pady=5, anchor="w")

        form_grid = tk.Frame(self, bg=c.DARK_BG)
        form_grid.pack(pady=20, fill="x", anchor="w")

        form_grid.grid_columnconfigure(0, minsize=150)
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

        # Divider
        tk.Frame(self, height=1, bg=c.WRAPPER_BORDER).pack(fill='x', pady=20)

        # Base Project Section
        tk.Label(self, text="Or start from an existing project:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(anchor="w", pady=(0, 5))

        base_frame = tk.Frame(self, bg=c.DARK_BG)
        base_frame.pack(fill='x', anchor='w')

        RoundedButton(base_frame, text="Select base project", command=self._select_base_project, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2").pack(side='left')

        self.base_path_label = tk.Label(base_frame, text="No base project selected", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)
        self.base_path_label.pack(side='left', padx=10)

        # Update label if path already exists
        self._update_base_label()

    def _browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.project_data["parent_folder"].set(folder_selected)

    def _select_base_project(self):
        folder_selected = filedialog.askdirectory(title="Select Base Project")
        if folder_selected:
            self.project_data["base_project_path"].set(folder_selected)
            self._update_base_label()
            if self.wizard_controller:
                self.wizard_controller.on_base_project_selected(folder_selected)

    def _update_base_label(self):
        path = self.project_data["base_project_path"].get()
        if path:
            self.base_path_label.config(text=path, fg=c.TEXT_COLOR)
        else:
            self.base_path_label.config(text="No base project selected", fg=c.TEXT_SUBTLE_COLOR)