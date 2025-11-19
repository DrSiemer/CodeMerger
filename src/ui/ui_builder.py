from tkinter import Frame, Label, font as tkFont
from .. import constants as c
from .widgets.rounded_button import RoundedButton
from .widgets.profile_navigator import ProfileNavigator
from .tooltip import ToolTip
from .assets import assets

def setup_ui(app):
    """Creates and places all the UI widgets for the main application window"""
    # --- Window Grid Configuration ---
    app.columnconfigure(0, weight=1)
    app.rowconfigure(2, weight=1) # Central content row expands vertically
    app.rowconfigure(3, weight=0) # Status bar row is fixed height

    # --- Top Bar (Row 0) ---
    top_bar = Frame(app, bg=c.TOP_BAR_BG, padx=20, pady=15)
    top_bar.grid(row=0, column=0, sticky='ew')
    top_bar.columnconfigure(1, weight=1) # Make the center area expand

    # Left-aligned items
    left_frame = Frame(top_bar, bg=c.TOP_BAR_BG)
    left_frame.grid(row=0, column=0, sticky='w')

    app.color_swatch = Label(left_frame, cursor="hand2", bg=c.TOP_BAR_BG, bd=0, highlightthickness=0)
    app.color_swatch.bind("<Button-1>", app.action_handlers.open_color_chooser)
    ToolTip(app.color_swatch, "Click to change the project color", delay=500)

    app.title_container = Frame(left_frame, bg=c.TOP_BAR_BG, cursor="hand2")
    app.title_container.pack(side='left')

    # Use grid within the title container to manage a minimum height, preventing layout shifts
    app.title_container.grid_rowconfigure(0, weight=1)
    app.title_container.grid_columnconfigure(0, weight=1)

    app.title_label = Label(app.title_container, textvariable=app.project_title_var, font=c.FONT_LARGE_BOLD, bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, anchor='w', cursor="hand2")
    app.title_label.grid(row=0, column=0, sticky='w')

    # Set a minimum height on the container's grid row based on the label's actual required height
    app.update_idletasks()
    required_height = app.title_label.winfo_reqheight()
    app.title_container.grid_rowconfigure(0, minsize=required_height)

    app.title_label.bind("<Button-1>", app.action_handlers.handle_title_click)
    app.title_label.bind("<Double-Button-1>", app.action_handlers.edit_project_title)
    app.title_container.bind("<Button-1>", app.action_handlers.handle_title_click)
    app.title_container.bind("<Double-Button-1>", app.action_handlers.edit_project_title)
    ToolTip(app.title_container, "Click to select project, double-click to edit title", delay=500)

    # Right-aligned items
    right_frame = Frame(top_bar, bg=c.TOP_BAR_BG)
    right_frame.grid(row=0, column=2, sticky='e')
    right_frame.grid_rowconfigure(0, weight=1) # Center items vertically in the row

    # New files warning icon
    app.new_files_label = Label(right_frame, image=assets.new_files_icon, bg=c.TOP_BAR_BG, cursor="hand2")
    app.new_files_label.bind("<Button-1>", app.action_handlers.on_new_files_click)
    app.new_files_tooltip = ToolTip(app.new_files_label, text="")

    # Open folder icon
    app.folder_icon_label = Label(right_frame, image=assets.folder_icon, bg=c.TOP_BAR_BG, cursor="hand2")
    app.folder_icon_label.bind("<Button-1>", app.action_handlers.open_project_folder)
    ToolTip(app.folder_icon_label, "Open project folder\nCtrl+Click: Copy path\nCtrl+Alt+Click: Open console", delay=500)

    # --- Top-Level Buttons (Row 1) ---
    app.top_buttons_container = Frame(app, bg=c.DARK_BG, padx=20, height=32)
    app.top_buttons_container.grid(row=1, column=0, sticky='ew', pady=(15, 0))
    app.top_buttons_container.grid_propagate(False)
    app.top_buttons_container.columnconfigure(1, weight=1) # Make the central column expandable
    app.top_buttons_container.rowconfigure(0, weight=1) # Center all content vertically

    # Column 0: Manage Files Button
    app.manage_files_button = RoundedButton(app.top_buttons_container, text="Manage Files", font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.action_handlers.manage_files, cursor='hand2')
    app.manage_files_button.grid(row=0, column=0, sticky='w')

    # Column 1: Middle Container (Profiles + Start Button)
    app.middle_container = Frame(app.top_buttons_container, bg=c.DARK_BG)
    app.middle_container.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
    app.middle_container.columnconfigure(0, weight=0) # Profile Frame
    app.middle_container.columnconfigure(1, weight=0) # Start Button

    # --- Profile Management Frame ---
    app.profile_frame = Frame(app.middle_container, bg=c.DARK_BG)
    app.profile_frame.grid(row=0, column=0, sticky='w')

    # --- Profile Widgets ---
    app.profile_navigator = ProfileNavigator(app.profile_frame, on_change_callback=app.profile_actions.on_profile_switched)
    app.add_profile_button = RoundedButton(app.profile_frame, text="+", font=(c.FONT_BOLD[0], c.FONT_BOLD[1]), bg=c.BTN_GRAY_BG, fg=c.TEXT_COLOR, command=app.profile_actions.open_new_profile_dialog, cursor='hand2', width=20, height=28, hollow=True)
    ToolTip(app.add_profile_button, "Create an additional project profile", delay=500)
    app.delete_profile_button = RoundedButton(app.profile_frame, text="-", font=(c.FONT_BOLD[0], c.FONT_BOLD[1]), bg=c.BTN_GRAY_BG, fg=c.TEXT_COLOR, command=app.profile_actions.delete_current_profile, cursor='hand2', width=20, height=28, hollow=True)
    ToolTip(app.delete_profile_button, "Delete the current profile", delay=500)

    # --- Start Work Button ---
    # Placed in Column 1 of middle_container, initially hidden/shown by ButtonStateManager
    app.start_work_button = Label(app.middle_container, image=assets.start_work_icon, bg=c.DARK_BG, cursor="hand2")
    app.start_work_button.bind("<Button-1>", app.action_handlers.start_work_on_click)
    app.start_work_button.bind("<Enter>", lambda e: app.start_work_button.config(image=assets.start_work_active_icon))
    app.start_work_button.bind("<Leave>", lambda e: app.start_work_button.config(image=assets.start_work_icon))
    ToolTip(app.start_work_button, "Start Work: Copy code with '_start.txt' instructions\nAlt+Click to delete start file", delay=500)

    # Column 2: Right Controls (Wizard + Select Project)
    right_controls_frame = Frame(app.top_buttons_container, bg=c.DARK_BG)
    right_controls_frame.grid(row=0, column=2, sticky='e')

    app.project_starter_button = Label(right_controls_frame, image=assets.project_starter_icon, bg=c.DARK_BG, cursor="hand2")
    app.project_starter_button.pack(side='left', padx=(0, 10))
    app.project_starter_button.bind("<Enter>", lambda e: app.project_starter_button.config(image=assets.project_starter_active_icon))
    app.project_starter_button.bind("<Leave>", lambda e: app.project_starter_button.config(image=assets.project_starter_icon))
    app.project_starter_button.bind("<Button-1>", app.action_handlers.open_project_starter)
    ToolTip(app.project_starter_button, "New Project Wizard", delay=500)

    app.select_project_button = RoundedButton(right_controls_frame, text="Select Project", font=c.FONT_BUTTON, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=app.action_handlers.open_change_directory_dialog, cursor='hand2')
    app.select_project_button.pack(side='left')

    # --- Center Content Area (Row 2) ---
    center_frame = Frame(app, bg=c.DARK_BG)
    center_frame.grid(row=2, column=0, sticky='nsew')
    center_frame.grid_rowconfigure(0, weight=1)
    center_frame.grid_columnconfigure(0, weight=1)
    app.center_frame = center_frame

    # A container for the icon buttons, placed in the main central frame.
    # It sticks to the bottom-right corner.
    app.bottom_buttons_container = Frame(center_frame, bg=c.DARK_BG)
    app.bottom_buttons_container.grid(row=0, column=0, sticky='se', padx=20, pady=(0, 18))

    app.filetypes_button = Label(app.bottom_buttons_container, image=assets.filetypes_icon, bg=c.DARK_BG, cursor='hand2')
    app.filetypes_button.pack(side='top')
    ToolTip(app.filetypes_button, "Manage Filetypes", delay=500)

    app.settings_button = Label(app.bottom_buttons_container, image=assets.settings_icon, bg=c.DARK_BG, cursor='hand2')
    app.settings_button.pack(side='top', pady=(10, 0))
    ToolTip(app.settings_button, "Settings", delay=500)

    # This frame holds the actions box. Its alignment is controlled by the responsive layout function.
    app.main_content_frame = Frame(center_frame, bg=c.DARK_BG)
    app.main_content_frame.grid(row=0, column=0, sticky='') # Starts centered
    app.main_content_frame.grid_rowconfigure(0, weight=1)
    app.main_content_frame.grid_columnconfigure(0, weight=1)

    app.wrapper_box = Frame(app.main_content_frame, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
    app.wrapper_box.grid(row=0, column=0, sticky='s') # Aligns to the bottom of its cell

    app.wrapper_box_title = Label(app.wrapper_box, text="Actions", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL, pady=2)

    app.no_project_label = Label(app.wrapper_box, text="Select a project to get started", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)

    app.button_grid_frame = Frame(app.wrapper_box, bg=c.DARK_BG)
    app.button_grid_frame.columnconfigure(0, weight=1, uniform="group1")
    app.button_grid_frame.columnconfigure(1, weight=1, uniform="group1")

    copy_button_height = 60
    app.paste_changes_button = RoundedButton(app.button_grid_frame, text="Paste Changes", height=30, font=c.FONT_BUTTON, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, command=None, cursor='hand2')
    app.copy_wrapped_button = RoundedButton(app.button_grid_frame, height=copy_button_height, text="Copy with Instructions", font=c.FONT_BUTTON, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=app.action_handlers.copy_wrapped_code, cursor='hand2')
    app.wrapper_text_button = RoundedButton(app.button_grid_frame, text="Define Instructions", height=30, font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.action_handlers.open_instructions_window, cursor='hand2')
    app.copy_merged_button = RoundedButton(app.button_grid_frame, height=copy_button_height, text="Copy Code Only", font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.action_handlers.copy_merged_code, cursor='hand2')

    app.paste_changes_button.bind("<Button-1>", app.action_handlers.on_paste_click)
    app.paste_changes_button.unbind("<ButtonRelease-1>")
    app.paste_changes_button.bind("<ButtonRelease-1>", app.action_handlers.on_paste_release)

    ToolTip(app.paste_changes_button, "Open paste window\n(Ctrl+Click to paste from clipboard)", delay=500)
    ToolTip(app.copy_wrapped_button, "Copy all included code with your custom intro/outro instructions", delay=500)
    ToolTip(app.copy_merged_button, "Copy just the merged code with a default prompt", delay=500)

    app.settings_button.bind("<Enter>", lambda e: app.settings_button.config(image=assets.settings_icon_active), add='+')
    app.settings_button.bind("<Leave>", lambda e: app.settings_button.config(image=assets.settings_icon), add='+')
    app.settings_button.bind("<Button-1>", lambda e: app.action_handlers.open_settings_window())

    app.filetypes_button.bind("<Enter>", lambda e: app.filetypes_button.config(image=assets.filetypes_icon_active), add='+')
    app.filetypes_button.bind("<Leave>", lambda e: app.filetypes_button.config(image=assets.filetypes_icon), add='+')
    app.filetypes_button.bind("<Button-1>", lambda e: app.action_handlers.open_filetypes_manager())

    # --- Status Bar (Row 3) ---
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
    app.status_bar.grid(row=3, column=0, sticky='ew')