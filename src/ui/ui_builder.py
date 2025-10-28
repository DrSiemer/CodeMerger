from tkinter import Frame, Label, ttk
from .. import constants as c
from .widgets.rounded_button import RoundedButton
from .tooltip import ToolTip
from .assets import assets

def setup_ui(app):
    """Creates and places all the UI widgets for the main application window"""
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
    ToolTip(app.color_swatch, "Click to change the project color", delay=500)

    app.title_container = Frame(left_frame, bg=c.TOP_BAR_BG, cursor="hand2")
    app.title_container.pack(side='left')

    app.title_label = Label(app.title_container, textvariable=app.project_title_var, font=c.FONT_LARGE_BOLD, bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, anchor='w', cursor="hand2")
    app.title_label.pack(side='left')
    app.title_label.bind("<Button-1>", app.handle_title_click)
    app.title_label.bind("<Double-Button-1>", app.edit_project_title)
    app.title_container.bind("<Button-1>", app.handle_title_click)
    app.title_container.bind("<Double-Button-1>", app.edit_project_title)
    ToolTip(app.title_container, "Click to select project, double-click to edit title", delay=500)

    # Right-aligned items
    right_frame = Frame(top_bar, bg=c.TOP_BAR_BG)
    right_frame.grid(row=0, column=2, sticky='e')
    right_frame.grid_rowconfigure(0, weight=1) # Center items vertically in the row

    # New files warning icon
    app.new_files_label = Label(right_frame, image=assets.new_files_icon, bg=c.TOP_BAR_BG, cursor="hand2")
    app.new_files_label.bind("<Button-1>", lambda e: app.manage_files())
    app.new_files_tooltip = ToolTip(app.new_files_label, text="")

    # Open folder icon
    app.folder_icon_label = Label(right_frame, image=assets.folder_icon, bg=c.TOP_BAR_BG, cursor="hand2")
    app.folder_icon_label.bind("<Button-1>", app.open_project_folder)
    ToolTip(app.folder_icon_label, "Open project folder (Ctrl+Click to copy path)", delay=500)

    # --- Top-Level Buttons (Row 1) ---
    top_buttons_container = Frame(app, bg=c.DARK_BG, padx=20)
    top_buttons_container.grid(row=1, column=0, sticky='ew', pady=(15, 0))
    top_buttons_container.columnconfigure(1, weight=1) # Make the central column expandable

    app.manage_files_button = RoundedButton(top_buttons_container, text="Manage Files", font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.manage_files, cursor='hand2')
    app.manage_files_button.grid(row=0, column=0, sticky='w')

    # --- Profile Management Frame (centered) ---
    profile_frame = Frame(top_buttons_container, bg=c.DARK_BG)
    profile_frame.grid(row=0, column=1, sticky='we') # This will center the frame's content
    profile_frame.grid_columnconfigure(0, weight=1) # Pad left
    profile_frame.grid_columnconfigure(1, weight=0) # Combobox
    profile_frame.grid_columnconfigure(2, weight=0) # Button
    profile_frame.grid_columnconfigure(3, weight=1) # Pad right

    # --- Profile Selector Combobox ---
    s = ttk.Style(app) # Need a style object
    app.option_add('*TCombobox*Listbox.background', c.TEXT_INPUT_BG)
    app.option_add('*TCombobox*Listbox.foreground', c.TEXT_COLOR)
    app.option_add('*TCombobox*Listbox.selectBackground', c.BTN_BLUE)
    app.option_add('*TCombobox*Listbox.selectForeground', c.BTN_BLUE_TEXT)
    s.configure('Profile.TCombobox',
        fieldbackground=c.TEXT_INPUT_BG,
        background=c.TEXT_INPUT_BG,
        arrowcolor=c.TEXT_COLOR,
        foreground=c.TEXT_COLOR,
        selectbackground=c.TEXT_INPUT_BG,
        selectforeground=c.TEXT_COLOR,
        font=c.FONT_NORMAL,
        padding=(10, 6)
    )
    s.map('Profile.TCombobox',
        foreground=[('readonly', c.TEXT_COLOR)],
        fieldbackground=[('readonly', c.TEXT_INPUT_BG)]
    )

    app.profile_selector = ttk.Combobox(profile_frame, textvariable=app.active_profile_var, state='readonly', style='Profile.TCombobox', width=20)
    app.profile_selector.bind('<<ComboboxSelected>>', app.on_profile_switched)

    # --- Add Profile Button ---
    app.add_profile_button = RoundedButton(profile_frame, text="+", font=(c.FONT_BOLD[0], c.FONT_BOLD[1]), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.open_new_profile_dialog, cursor='hand2', width=20, height=28)
    app.add_profile_button.grid(row=0, column=2, sticky='w', padx=10)
    ToolTip(app.add_profile_button, "Create a new project profile", delay=500)

    app.select_project_button = RoundedButton(top_buttons_container, text="Select Project", font=c.FONT_BUTTON, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=app.open_change_directory_dialog, cursor='hand2')
    app.select_project_button.grid(row=0, column=2, sticky='e')

    # --- Center "Actions" Box (Row 2) ---
    center_frame = Frame(app, bg=c.DARK_BG)
    center_frame.grid(row=2, column=0, sticky='nsew', pady=0)

    wrapper_box = Frame(center_frame, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
    wrapper_box.place(relx=0.5, rely=0.55, anchor='center')

    app.wrapper_box_title = Label(wrapper_box, text="Actions", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL, pady=2)

    # This label is shown when no project is selected
    app.no_project_label = Label(wrapper_box, text="Select a project to get started", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)

    app.button_grid_frame = Frame(wrapper_box, bg=c.DARK_BG)
    # Configure the grid columns to have equal weight. This is the key to alignment.
    app.button_grid_frame.columnconfigure(0, weight=1, uniform="group1")
    app.button_grid_frame.columnconfigure(1, weight=1, uniform="group1")

    copy_button_height = 60
    app.paste_changes_button = RoundedButton(app.button_grid_frame, text="Paste Changes", height=30, font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.open_paste_changes_dialog, cursor='hand2')
    app.copy_wrapped_button = RoundedButton(app.button_grid_frame, height=copy_button_height, text="Copy Wrapped", font=c.FONT_BUTTON, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=app.copy_wrapped_code, cursor='hand2')
    app.wrapper_text_button = RoundedButton(app.button_grid_frame, text="Define Wrapper Texts", height=30, font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.open_wrapper_text_window, cursor='hand2')
    app.copy_merged_button = RoundedButton(app.button_grid_frame, height=copy_button_height, text="Copy Merged", font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.copy_merged_code, cursor='hand2')

    ToolTip(app.copy_wrapped_button, "Copy all included code with custom intro + outro\n(use this to start new conversations)", delay=500)
    ToolTip(app.copy_merged_button, "Copy all included code with custom intro\n(use this to update an LLM of your code changes)", delay=500)

    # --- Bottom Bar (Row 3) ---
    bottom_bar = Frame(app, bg=c.DARK_BG)
    bottom_bar.grid(row=3, column=0, sticky='ew', pady=(20, 15))
    bottom_buttons_container = Frame(bottom_bar, bg=c.DARK_BG)
    bottom_buttons_container.pack(side='left', padx=20)

    RoundedButton(bottom_buttons_container, text="Manage Filetypes", font=c.FONT_BUTTON, fg=c.TEXT_COLOR, command=app.open_filetypes_manager, hollow=True, cursor='hand2').pack(side='left')
    RoundedButton(bottom_buttons_container, text="Settings", font=c.FONT_BUTTON, fg=c.TEXT_COLOR, command=app.open_settings_window, hollow=True, cursor='hand2').pack(side='left', padx=(10, 0))

    # --- Status Bar (Row 4) ---
    app.status_bar = Label(
        app,
        textvariable=app.status_var,
        relief='flat',
        anchor='w',
        bg=c.STATUS_BG,
        fg=c.STATUS_FG,
        font=c.FONT_STATUS_BAR,
        padx=20,
        pady=4
    )
    app.status_bar.grid(row=4, column=0, sticky='ew')