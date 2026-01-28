from tkinter import ttk
from .. import constants as c

def apply_dark_theme(window):
    """
    Applies a consistent dark theme to all ttk widgets in the application.
    This should be called on any Toplevel window that uses ttk widgets.
    """
    window.option_add('*TCombobox*Listbox.background', c.TEXT_INPUT_BG)
    window.option_add('*TCombobox*Listbox.foreground', c.TEXT_COLOR)
    window.option_add('*TCombobox*Listbox.selectBackground', c.BTN_BLUE)
    window.option_add('*TCombobox*Listbox.selectForeground', c.BTN_BLUE_TEXT)

    s = ttk.Style(window)
    s.theme_use('default')

    # --- Checkbutton Style ---
    s.configure('Dark.TCheckbutton',
        background=c.DARK_BG,
        foreground=c.TEXT_COLOR,
        font=c.FONT_NORMAL
    )
    s.map('Dark.TCheckbutton',
        background=[('active', c.DARK_BG)],
        indicatorcolor=[('selected', c.BTN_BLUE), ('!selected', c.TEXT_INPUT_BG)],
        indicatorrelief=[('pressed', 'sunken'), ('!pressed', 'flat')]
    )

    # --- Large Checkbutton Style (Used in Wizard) ---
    s.configure('Large.TCheckbutton',
        background=c.DARK_BG,
        foreground=c.TEXT_COLOR,
        font=c.FONT_H3,
        padding=(0, 5, 0, 5)
    )
    s.map('Large.TCheckbutton',
        background=[('active', c.DARK_BG)],
        indicatorcolor=[('selected', c.BTN_BLUE), ('!selected', c.TEXT_INPUT_BG)],
        indicatorrelief=[('pressed', 'sunken'), ('!pressed', 'flat')]
    )

    # --- Combobox Style ---
    s.configure('Dark.TCombobox',
        fieldbackground=c.TEXT_INPUT_BG,
        background=c.TEXT_INPUT_BG,
        arrowcolor=c.TEXT_COLOR,
        foreground=c.TEXT_COLOR,
        selectbackground=c.TEXT_INPUT_BG,
        selectforeground=c.TEXT_COLOR
    )
    s.map('Dark.TCombobox',
        foreground=[('readonly', c.TEXT_COLOR)],
        fieldbackground=[('readonly', c.TEXT_INPUT_BG)]
    )