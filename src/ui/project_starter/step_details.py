import tkinter as tk
from tkinter import filedialog, messagebox
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..tooltip import ToolTip

class DetailsView(tk.Frame):
    def __init__(self, parent, project_data, starter_controller=None):
        super().__init__(parent, bg=c.DARK_BG)
        self.project_data = project_data
        self.starter_controller = starter_controller # Access to starter methods
        self.config(padx=10, pady=10)

        tk.Label(self, text="Project Details", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=10, anchor="w")
        tk.Label(self, text="Enter the initial details for your new project.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(pady=5, anchor="w")

        form_grid = tk.Frame(self, bg=c.DARK_BG)
        form_grid.pack(pady=20, fill="x", anchor="w")

        form_grid.grid_columnconfigure(0, minsize=150)
        form_grid.grid_columnconfigure(1, weight=1)

        # Row 0: Project Name
        self.name_label_frame = tk.Frame(form_grid, bg=c.DARK_BG)
        self.name_label_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        tk.Label(self.name_label_frame, text="Project Name:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(anchor="w")
        tk.Label(self.name_label_frame, text="(used for folder name)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=(c.FONT_FAMILY_PRIMARY, 8)).pack(anchor="w")

        self.name_entry = tk.Entry(form_grid, textvariable=self.project_data["name"], width=50, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief="flat", font=c.FONT_NORMAL)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, ipady=4, sticky="ew")

        # Divider
        tk.Frame(self, height=1, bg=c.WRAPPER_BORDER).pack(fill='x', pady=20)

        # Base Project Section
        base_title_frame = tk.Frame(self, bg=c.DARK_BG)
        base_title_frame.pack(anchor="w", pady=(0, 5))

        tk.Label(base_title_frame, text="Or start from an existing project ", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side="left")
        tk.Label(base_title_frame, text="(OPTIONAL):", bg=c.DARK_BG, fg=c.NOTE, font=c.FONT_BOLD).pack(side="left")

        base_frame = tk.Frame(self, bg=c.DARK_BG)
        base_frame.pack(fill='x', anchor='w')

        self.base_btn = RoundedButton(base_frame, text="Select base project", command=self._select_base_project, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.base_btn.pack(side='left')
        ToolTip(self.base_btn, "Pick an existing folder to use its merge list as a reference", delay=500)

        self.base_path_label = tk.Label(base_frame, text="No base project selected", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)
        self.base_path_label.pack(side='left', padx=10)

        # Update label if path already exists
        self._update_base_label()

        # Tips Section at Bottom
        tips_frame = tk.Frame(self, bg=c.DARK_BG)
        tips_frame.pack(side="bottom", fill="x", anchor="w", pady=(40, 0))

        tk.Label(tips_frame, text="💡 LLM Best Practices", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.NOTE).pack(anchor="w", pady=(0, 2))
        tk.Label(tips_frame, text="- Always start a new conversation with the LLM when pasting a prompt from CodeMerger.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(anchor="w")

    def register_info(self, info_mgr):
        """Registers step-specific widgets for Info Mode."""
        if not info_mgr: return
        info_mgr.register(self.name_label_frame, "starter_details_name")
        info_mgr.register(self.name_entry, "starter_details_name")
        info_mgr.register(self.base_btn, "starter_details_base")
        info_mgr.register(self.base_path_label, "starter_details_base")

    def _select_base_project(self):
        folder_selected = filedialog.askdirectory(title="Select Base Project")
        if folder_selected:
            self.project_data["base_project_path"].set(folder_selected)
            self._update_base_label()
            if self.starter_controller:
                self.starter_controller.on_base_project_selected(folder_selected)

    def _update_base_label(self):
        path = self.project_data["base_project_path"].get()
        if path:
            self.base_path_label.config(text=path, fg=c.TEXT_COLOR)
        else:
            self.base_path_label.config(text="No base project selected", fg=c.TEXT_SUBTLE_COLOR)

    def handle_reset(self):
        """Resets the input fields for this step."""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset project details?", parent=self):
            self.project_data["name"].set("")
            self.project_data["base_project_path"].set("")
            self._update_base_label()