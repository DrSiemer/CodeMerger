from tkinter import Frame, Label
from .. import constants as c
from .custom_widgets import RoundedButton
from .tooltip import ToolTip

def setup_ui(app):
    """Creates and places all the UI widgets for the main application window"""
    # --- Style Definitions ---
    font_family = "Segoe UI"
    font_normal = (font_family, 12)
    font_large_bold = (font_family, 24, 'bold')
    font_button = (font_family, 16)

    # --- Window Grid Configuration ---
    app.columnconfigure(0, weight=1)
    app.rowconfigure(2, weight=1)

    # --- Top Bar (Row 0) ---
    top_bar = Frame(app, bg=c.TOP_BAR_BG, padx=20, pady=15)
    top_bar.grid(row=0, column=0, sticky='ew')
    top_bar.columnconfigure(1, weight=1) # Make the center area expand

    # Left-aligned items
    left_frame = Frame(top_bar, bg=c.TOP_BAR_BG)
    left_frame.grid(row=0, column=0, sticky='w')

    app.color_swatch = Frame(left_frame, width=48, height=48, cursor="hand2")
    app.color_swatch.pack_propagate(False)
    app.color_swatch.bind("<Button-1>", app.open_color_chooser)
    app.color_swatch.config(bg=c.TOP_BAR_BG)

    app.title_label = Label(left_frame, textvariable=app.project_title_var, font=font_large_bold, bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, anchor='w', cursor="hand2")
    app.title_label.pack(side='left')
    app.title_label.bind("<Button-1>", app.edit_project_title)
    app.title_label.bind("<Enter>", app.on_title_area_enter)
    app.title_label.bind("<Leave>", app.on_title_area_leave)

    app.edit_icon_label = Label(left_frame, image=app.edit_icon, bg=c.TOP_BAR_BG, cursor="hand2")
    if app.edit_icon:
        app.edit_icon_label.bind("<Button-1>", app.edit_project_title)
        app.edit_icon_label.bind("<Enter>", app.on_title_area_enter)
        app.edit_icon_label.bind("<Leave>", app.on_title_area_leave)

    # Right-aligned items
    right_frame = Frame(top_bar, bg=c.TOP_BAR_BG)
    right_frame.grid(row=0, column=2, sticky='e')

    # New files warning icon
    app.new_files_label = Label(right_frame, image=app.new_files_icon, bg=c.TOP_BAR_BG, cursor="hand2")
    app.new_files_label.bind("<Button-1>", lambda e: app.manage_files())
    app.new_files_tooltip = ToolTip(app.new_files_label, text="")

    # --- Top-Level Buttons (Row 1) ---
    top_buttons_container = Frame(app, bg=c.DARK_BG, padx=20)
    top_buttons_container.grid(row=1, column=0, sticky='ew', pady=(15, 0))
    top_buttons_container.columnconfigure(1, weight=1)

    left_buttons = Frame(top_buttons_container, bg=c.DARK_BG)
    left_buttons.grid(row=0, column=0, sticky='w')

    app.select_project_button = RoundedButton(left_buttons, text="Select Project", font=font_button, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=app.open_change_directory_dialog)
    app.select_project_button.pack(side='left')
    app.manage_files_button = RoundedButton(left_buttons, text="Manage Files", font=font_button, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.manage_files)
    app.manage_files_button.pack(side='left', padx=(10, 0))

    right_buttons = Frame(top_buttons_container, bg=c.DARK_BG)
    right_buttons.grid(row=0, column=2, sticky='e')
    app.compact_mode_button = RoundedButton(right_buttons, text="Compact Mode", font=font_button, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.view_manager.toggle_compact_mode)
    app.compact_mode_button.pack()

    # --- Center "Wrapper & Output" Box (Row 2) ---
    center_frame = Frame(app, bg=c.DARK_BG)
    center_frame.grid(row=2, column=0, sticky='nsew', pady=0)

    wrapper_box = Frame(center_frame, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
    wrapper_box.place(relx=0.5, rely=0.55, anchor='center')

    app.wrapper_box_title = Label(wrapper_box, text="Wrapper & Output", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal, pady=2)

    # This label is shown when no project is selected
    app.no_project_label = Label(wrapper_box, text="Select a project to get started", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=font_normal)

    app.button_grid_frame = Frame(wrapper_box, bg=c.DARK_BG)
    # Configure the grid columns to have equal weight. This is the key to alignment.
    app.button_grid_frame.columnconfigure(0, weight=1, uniform="group1")
    app.button_grid_frame.columnconfigure(1, weight=1, uniform="group1")

    copy_button_height = 60
    app.copy_wrapped_button = RoundedButton(app.button_grid_frame, height=copy_button_height, text="Copy Wrapped", font=font_button, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=app.copy_wrapped_code)
    app.wrapper_text_button = RoundedButton(app.button_grid_frame, text="Define Wrapper Texts", height=30, font=font_button, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.open_wrapper_text_window)
    app.copy_merged_button = RoundedButton(app.button_grid_frame, height=copy_button_height, text="Copy Merged", font=font_button, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.copy_merged_code)

    ToolTip(app.copy_wrapped_button, "Copy all included code with custom intro + outro\n(use this to start new conversations)", delay=500)
    ToolTip(app.copy_merged_button, "Copy all included code with custom intro\n(use this to update an LLM of your code changes)", delay=500)

    # --- Bottom Bar (Row 3) ---
    bottom_bar = Frame(app, bg=c.DARK_BG)
    bottom_bar.grid(row=3, column=0, sticky='ew', pady=(20, 15))
    bottom_buttons_container = Frame(bottom_bar, bg=c.DARK_BG)
    bottom_buttons_container.pack(side='left', padx=20)

    RoundedButton(bottom_buttons_container, text="Manage Filetypes", font=font_button, fg=c.TEXT_COLOR, command=app.open_filetypes_manager, hollow=True).pack(side='left')
    RoundedButton(bottom_buttons_container, text="Settings", font=font_button, fg=c.TEXT_COLOR, command=app.open_settings_window, hollow=True).pack(side='left', padx=(10, 0))

    # --- Status Bar (Row 4) ---
    app.status_var = app.status_var # This should already exist
    status_bar = Label(
        app,
        textvariable=app.status_var,
        relief='flat',
        anchor='w',
        bg=c.STATUS_BG,
        fg=c.STATUS_FG,
        font=(font_family, 9),
        padx=20,
        pady=4
    )
    status_bar.grid(row=4, column=0, sticky='ew')