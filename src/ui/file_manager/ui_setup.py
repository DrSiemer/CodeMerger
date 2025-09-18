from tkinter import Frame, Label, ttk, font, Button
from ..widgets.rounded_button import RoundedButton
from ..widgets.two_column_list import TwoColumnList
from ... import constants as c
from ...constants import SUBTLE_HIGHLIGHT_COLOR
from ..assets import assets
from ..tooltip import ToolTip

def setup_file_manager_ui(window):
    """Creates and packs all the UI widgets for the FileManagerWindow"""
    font_family = "Segoe UI"
    font_normal = (font_family, 12)
    font_button = (font_family, 14)
    # Define a smaller font for the token counts
    window.font_small = font.Font(family=font_family, size=9)

    main_frame = Frame(window, bg=c.DARK_BG)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(2, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)

    available_files_title_frame = Frame(main_frame, bg=c.DARK_BG)
    available_files_title_frame.grid(row=0, column=0, columnspan=2, sticky='w')
    Label(available_files_title_frame, text="Available Files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal).pack(side='left')
    Label(available_files_title_frame, text="(double click or enter to add/remove)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=font_normal).pack(side='left')

    # --- Treeview Styling ---
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Treeview", background=c.TEXT_INPUT_BG, foreground=c.TEXT_COLOR, fieldbackground=c.TEXT_INPUT_BG, borderwidth=0, font=font_normal, rowheight=25)
    style.map("Treeview", background=[('selected', c.BTN_BLUE)], foreground=[('selected', c.BTN_BLUE_TEXT)])

    window.tree = ttk.Treeview(main_frame, show='tree')
    window.tree.grid(row=1, column=0, sticky='nsew')
    tree_scroll = ttk.Scrollbar(main_frame, orient='vertical', command=window.tree.yview)
    tree_scroll.grid(row=1, column=1, sticky='ns')
    window.tree.config(yscrollcommand=tree_scroll.set)
    window.tree_action_button = RoundedButton(main_frame, text="Add to Merge List", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button, width=220, cursor='hand2')
    window.tree_action_button.grid(row=2, column=0, sticky='w', pady=(10, 0))
    window.tree_action_button.set_state('disabled')
    window.tree.tag_configure('subtle_highlight', background=SUBTLE_HIGHLIGHT_COLOR, foreground=c.TEXT_COLOR)
    window.tree.tag_configure('new_file_highlight', foreground="#40C040") # Bright Green

    title_frame = Frame(main_frame, bg=c.DARK_BG)
    title_frame.grid(row=0, column=2, columnspan=2, sticky='nsew', padx=(10, 0))
    title_frame.columnconfigure(1, weight=1)

    Label(title_frame, text="Merge Order", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font_normal).grid(row=0, column=0, sticky='w')
    window.merge_order_details_label = Label(title_frame, text="", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=font_normal)
    window.merge_order_details_label.grid(row=0, column=1, sticky='w', padx=(5,0))

    window.toggle_paths_button = Button(
        title_frame,
        image=assets.paths_icon,
        command=window.toggle_full_path_view,
        bg=c.DARK_BG,
        activebackground=c.SUBTLE_HIGHLIGHT_COLOR,
        relief='flat',
        bd=0,
        cursor='hand2'
    )
    window.toggle_paths_button.grid(row=0, column=2, sticky='e', padx=(5,0))
    ToolTip(window.toggle_paths_button, "Toggle full path view")

    # --- Merge Order List (Custom Widget) ---
    list_frame = Frame(main_frame, bg=c.DARK_BG)
    list_frame.grid(row=1, column=2, columnspan=2, sticky='nsew', padx=(10, 0))
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)

    window.merge_order_list = TwoColumnList(
        list_frame,
        right_col_font=window.font_small,
        right_col_width=50
    )
    window.merge_order_list.grid(row=0, column=0, sticky='nsew')

    list_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=window.merge_order_list.yview)
    # The scrollbar is gridded here, but its visibility will be managed by the TwoColumnList widget
    list_scroll.grid(row=0, column=1, sticky='ns')
    window.merge_order_list.config(yscrollcommand=list_scroll.set)
    # Link the scrollbar to the list widget for automatic hiding
    window.merge_order_list.link_scrollbar(list_scroll)

    move_buttons_frame = Frame(main_frame, bg=c.DARK_BG)
    move_buttons_frame.grid(row=2, column=2, sticky='ew', pady=(10, 0), padx=(10, 0))
    # Configure grid columns to have equal weight, forcing buttons to the same size
    move_buttons_frame.grid_columnconfigure(0, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(1, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(2, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(3, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(4, weight=1, uniform="group1")

    narrow_padding = 20
    window.move_to_top_button = RoundedButton(move_buttons_frame, text="↑↑ Top", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button, h_padding=narrow_padding, cursor='hand2')
    window.move_to_top_button.grid(row=0, column=0, sticky='ew', padx=(0, 2))
    window.move_up_button = RoundedButton(move_buttons_frame, text="↑ Up", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button, h_padding=narrow_padding, cursor='hand2')
    window.move_up_button.grid(row=0, column=1, sticky='ew', padx=(2, 2))
    window.remove_button = RoundedButton(move_buttons_frame, text="Remove", command=None, fg=c.TEXT_COLOR, font=font_button, hollow=True, h_padding=narrow_padding, cursor='hand2')
    window.remove_button.grid(row=0, column=2, sticky='ew', padx=2)
    window.move_down_button = RoundedButton(move_buttons_frame, text="↓ Down", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button, h_padding=narrow_padding, cursor='hand2')
    window.move_down_button.grid(row=0, column=3, sticky='ew', padx=(2, 2))
    window.move_to_bottom_button = RoundedButton(move_buttons_frame, text="↓↓ Bottom", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button, h_padding=narrow_padding, cursor='hand2')
    window.move_to_bottom_button.grid(row=0, column=4, sticky='ew', padx=(2, 0))

    # Disable all move buttons initially
    for btn in [window.move_to_top_button, window.move_up_button, window.remove_button, window.move_down_button, window.move_to_bottom_button]:
        btn.set_state('disabled')

    bulk_action_frame = Frame(main_frame, bg=c.DARK_BG)
    bulk_action_frame.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(20, 0))
    RoundedButton(bulk_action_frame, text="Add all", command=window.select_all_files, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button, cursor='hand2').pack(side='left')
    RoundedButton(bulk_action_frame, text="Remove all", command=window.remove_all_files, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=font_button, cursor='hand2').pack(side='right')
    RoundedButton(bulk_action_frame, text="Save and Close", command=window.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=("Segoe UI", 16), width=240, cursor='hand2').pack()