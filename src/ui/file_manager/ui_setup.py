from tkinter import Frame, Label, ttk, font, Button, Entry
from ..widgets.rounded_button import RoundedButton
from ..widgets.two_column_list import TwoColumnList
from ... import constants as c
from ...constants import SUBTLE_HIGHLIGHT_COLOR
from ..assets import assets
from ..tooltip import ToolTip

def setup_file_manager_ui(window):
    """Creates and packs all the UI widgets for the FileManagerWindow"""
    font_config = c.FONT_SMALL_BUTTON
    window.font_small = font.Font(family=font_config[0], size=font_config[1])

    main_frame = Frame(window, bg=c.DARK_BG)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=0)
    main_frame.grid_columnconfigure(0, weight=1)

    # --- Paned Window for a truly resizable and seamless layout ---
    window.paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
    window.paned_window.grid(row=0, column=0, sticky='nsew')

    # --- Left Panel (Available Files) ---
    left_panel = Frame(window.paned_window, bg=c.DARK_BG)
    left_panel.grid_columnconfigure(0, weight=1)
    left_panel.grid_rowconfigure(1, weight=1)
    window.paned_window.add(left_panel, weight=1)

    # --- Right Panel (Merge Order) ---
    right_panel = Frame(window.paned_window, bg=c.DARK_BG)
    right_panel.grid_columnconfigure(0, weight=1)
    right_panel.grid_rowconfigure(1, weight=1)
    window.paned_window.add(right_panel, weight=1)
    window.sash_cover = Frame(window.paned_window, bg=c.DARK_BG, width=6, cursor="sb_h_double_arrow")

    # Bind events to the centralized methods in the main window class
    window.paned_window.bind("<<SashMoved>>", window._on_manual_sash_move)
    window.paned_window.bind("<Configure>", window._update_sash_cover_position)
    window.after(10, window._update_sash_cover_position) # Initial placement

    # ===============================
    # === WIDGETS FOR LEFT PANEL ====
    # ===============================
    available_files_title_frame = Frame(left_panel, bg=c.DARK_BG)
    available_files_title_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
    available_files_title_frame.grid_columnconfigure(1, weight=1) # Middle column expands to push sides apart.

    title_sub_frame = Frame(available_files_title_frame, bg=c.DARK_BG)
    title_sub_frame.grid(row=0, column=0, sticky='w')
    Label(title_sub_frame, text="Available Files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(side='left')
    Label(title_sub_frame, text="(double click or enter to add/remove)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='left', padx=(5,0))

    right_buttons_frame = Frame(available_files_title_frame, bg=c.DARK_BG)
    right_buttons_frame.grid(row=0, column=2, sticky='e')

    window.toggle_gitignore_button = Button(
        right_buttons_frame,
        image=assets.git_files_icon,
        command=window.ui_controller.toggle_gitignore_filter,
        bg=c.DARK_BG,
        activebackground=c.SUBTLE_HIGHLIGHT_COLOR,
        relief='flat',
        bd=0,
        cursor='hand2'
    )
    window.toggle_gitignore_button.pack(side='left')
    window.gitignore_button_tooltip = ToolTip(window.toggle_gitignore_button, ".gitignore filter is ON. Click to show all files.")

    window.toggle_filter_button = Button(
        right_buttons_frame,
        image=assets.filter_icon,
        command=window.ui_controller.toggle_extension_filter,
        bg=c.DARK_BG,
        activebackground=c.SUBTLE_HIGHLIGHT_COLOR,
        relief='flat',
        bd=0,
        cursor='hand2'
    )
    window.toggle_filter_button.pack(side='left', padx=(5, 0))
    window.filter_button_tooltip = ToolTip(window.toggle_filter_button, "Filetype filter is ON. Click to show all files.")

    style = ttk.Style()
    style.theme_use('default')
    style.configure("Treeview", background=c.TEXT_INPUT_BG, foreground=c.TEXT_COLOR, fieldbackground=c.TEXT_INPUT_BG, borderwidth=0, font=c.FONT_NORMAL, rowheight=25)
    style.map("Treeview", background=[('selected', c.BTN_BLUE)], foreground=[('selected', c.BTN_BLUE_TEXT)])

    window.tree = ttk.Treeview(left_panel, show='tree', selectmode='extended')
    window.tree.grid(row=1, column=0, sticky='nsew')
    tree_scroll = ttk.Scrollbar(left_panel, orient='vertical', command=window.tree.yview)
    tree_scroll.grid(row=1, column=1, sticky='ns')
    window.tree.config(yscrollcommand=tree_scroll.set)

    window.folder_icon_labels = {
        'default': Label(window.tree, image=assets.folder_reveal_icon, bg=c.TEXT_INPUT_BG, cursor="hand2"),
        'selected': Label(window.tree, image=assets.folder_reveal_icon, bg=c.BTN_BLUE, cursor="hand2"),
        'highlight': Label(window.tree, image=assets.folder_reveal_icon, bg=c.SUBTLE_HIGHLIGHT_COLOR, cursor="hand2")
    }
    for label in window.folder_icon_labels.values():
        label.bind("<ButtonRelease-1>", window.ui_controller.on_folder_icon_click)
        ToolTip(label, text="Open file in folder", delay=500)

    tree_actions_frame = Frame(left_panel, bg=c.DARK_BG)
    tree_actions_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))
    tree_actions_frame.columnconfigure(0, weight=1)
    tree_actions_frame.columnconfigure(1, weight=2)

    window.tree_action_button = RoundedButton(tree_actions_frame, text="Add to Merge List", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, h_padding=180, cursor='hand2')
    window.tree_action_button.grid(row=0, column=0, sticky='ew')
    window.tree_action_button.set_state('disabled')

    filter_container = Frame(tree_actions_frame, bg=c.DARK_BG)
    filter_container.grid(row=0, column=1, sticky='ew', padx=(10, 0))
    Label(filter_container, text="Filter:", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='left')
    window.filter_input_frame = Frame(filter_container, bg=c.TEXT_INPUT_BG, highlightthickness=1, highlightbackground=c.TEXT_INPUT_BG)
    window.filter_input_frame.pack(side='left', padx=(5,0), fill='x', expand=True)
    window.filter_entry = Entry(window.filter_input_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, width=25)
    window.filter_entry.pack(side='left', fill='x', expand=True, ipady=3, padx=(5, 20))

    window.clear_filter_button = Label(window.filter_input_frame, image=assets.compact_mode_close_image, bg=c.TEXT_INPUT_BG, cursor="hand2")
    window.clear_filter_button.place(relx=1.0, rely=0.5, anchor='e', x=-5)
    window.clear_filter_button.place_forget()
    window.clear_filter_button.bind("<Enter>", lambda e: window.clear_filter_button.config(bg=c.SUBTLE_HIGHLIGHT_COLOR))
    window.clear_filter_button.bind("<Leave>", lambda e: window.clear_filter_button.config(bg=c.TEXT_INPUT_BG))
    window.clear_filter_button.bind("<ButtonRelease-1>", window.ui_controller.clear_filter)

    window.tree.tag_configure('subtle_highlight', background=SUBTLE_HIGHLIGHT_COLOR, foreground=c.TEXT_COLOR)
    window.tree.tag_configure('new_file_highlight', foreground="#40C040")

    # ===============================
    # === WIDGETS FOR RIGHT PANEL ===
    # ===============================
    title_frame = Frame(right_panel, bg=c.DARK_BG)
    title_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=(10, 0))
    title_frame.columnconfigure(1, weight=1)

    Label(title_frame, text="Merge Order", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=0, column=0, sticky='w')
    window.merge_order_details_label = Label(title_frame, text="", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)
    window.merge_order_details_label.grid(row=0, column=1, sticky='w', padx=(5,0))
    window.token_count_tooltip = ToolTip(window.merge_order_details_label, text="", delay=300)

    window.order_request_button = Button(
        title_frame,
        image=assets.order_request_icon,
        command=window.order_request_handler.handle_click,
        bg=c.DARK_BG,
        activebackground=c.SUBTLE_HIGHLIGHT_COLOR,
        relief='flat',
        bd=0,
        cursor='hand2'
    )
    window.order_request_button.grid(row=0, column=2, sticky='e', padx=(5,0))
    ToolTip(window.order_request_button, "Single-click: Copy order request to clipboard.\nDouble-click: Paste new order from clipboard.")

    window.toggle_paths_button = Button(title_frame, image=assets.paths_icon, command=window.ui_controller.toggle_full_path_view, bg=c.DARK_BG, activebackground=c.SUBTLE_HIGHLIGHT_COLOR, relief='flat', bd=0, cursor='hand2')
    window.toggle_paths_button.grid(row=0, column=3, sticky='e', padx=(5,0))
    ToolTip(window.toggle_paths_button, "Toggle full path")

    list_frame = Frame(right_panel, bg=c.DARK_BG)
    list_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=(10, 0))
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)

    window.merge_order_list = TwoColumnList(list_frame, right_col_font=window.font_small, right_col_width=50)
    window.merge_order_list.grid(row=0, column=0, sticky='nsew')
    list_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=window.merge_order_list.yview)
    list_scroll.grid(row=0, column=1, sticky='ns')
    window.merge_order_list.config(yscrollcommand=list_scroll.set)
    window.merge_order_list.link_scrollbar(list_scroll)

    move_buttons_frame = Frame(right_panel, bg=c.DARK_BG)
    move_buttons_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0), padx=(10, 0))
    move_buttons_frame.grid_columnconfigure(0, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(1, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(2, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(3, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(4, weight=1, uniform="group1")

    narrow_padding = 20
    window.move_to_top_button = RoundedButton(move_buttons_frame, text="↑↑ Top", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, h_padding=narrow_padding, cursor='hand2')
    window.move_to_top_button.grid(row=0, column=0, sticky='ew', padx=(0, 2))
    window.move_up_button = RoundedButton(move_buttons_frame, text="↑ Up", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, h_padding=narrow_padding, cursor='hand2')
    window.move_up_button.grid(row=0, column=1, sticky='ew', padx=(2, 2))
    window.remove_button = RoundedButton(move_buttons_frame, text="Remove", command=None, fg=c.TEXT_COLOR, font=c.FONT_FILE_MANAGER_BUTTON, hollow=True, h_padding=narrow_padding, cursor='hand2')
    window.remove_button.grid(row=0, column=2, sticky='ew', padx=2)
    window.move_down_button = RoundedButton(move_buttons_frame, text="↓ Down", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, h_padding=narrow_padding, cursor='hand2')
    window.move_down_button.grid(row=0, column=3, sticky='ew', padx=(2, 2))
    window.move_to_bottom_button = RoundedButton(move_buttons_frame, text="↓↓ Bottom", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, h_padding=narrow_padding, cursor='hand2')
    window.move_to_bottom_button.grid(row=0, column=4, sticky='ew', padx=(2, 0))

    for btn in [window.move_to_top_button, window.move_up_button, window.remove_button, window.move_down_button, window.move_to_bottom_button]:
        btn.set_state('disabled')

    # ===============================================
    # === BOTTOM BUTTONS (Back in main_frame) =======
    # ===============================================
    bulk_action_frame = Frame(main_frame, bg=c.DARK_BG)
    bulk_action_frame.grid(row=1, column=0, sticky='ew', pady=(20, 0))
    RoundedButton(bulk_action_frame, text="Add all", command=window.state_controller.select_all_files, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, cursor='hand2').pack(side='left')
    RoundedButton(bulk_action_frame, text="Remove all", command=window.state_controller.remove_all_files, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, cursor='hand2').pack(side='right')
    RoundedButton(bulk_action_frame, text="Save and Close", command=window.state_controller.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, width=240, cursor='hand2').pack()