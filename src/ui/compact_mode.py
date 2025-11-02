import tkinter as tk
from .. import constants as c
from .widgets.rounded_button import RoundedButton

class CompactMode(tk.Toplevel):
    """
    A frameless, always-on-top, draggable window that provides quick access
    to core functions when the main window is minimized.
    """
    def __init__(self, parent, close_callback, project_name, instance_color=c.COMPACT_MODE_BG_COLOR, font_color_name='light', show_wrapped_button=False, on_move_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.close_callback = close_callback
        self.on_move_callback = on_move_callback
        self.project_name = project_name
        self.tooltip_window = None
        self.new_files_label = None

        # --- Style and Layout Constants ---
        BAR_AND_BORDER_COLOR = instance_color
        BORDER_WIDTH = c.COMPACT_MODE_BORDER_WIDTH
        MOVE_BAR_HEIGHT = c.COMPACT_MODE_MOVE_BAR_HEIGHT
        text_hex_color = c.TEXT_COLOR if font_color_name == 'light' else '#000000'

        # --- Window Configuration ---
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(bg=BAR_AND_BORDER_COLOR, padx=BORDER_WIDTH, pady=BORDER_WIDTH)

        # --- Internal State for Dragging ---
        self._offset_x = 0
        self._offset_y = 0

        # --- Move Bar (for dragging and double-click) ---
        self.move_bar = tk.Frame(self, height=MOVE_BAR_HEIGHT, bg=BAR_AND_BORDER_COLOR, cursor="fleur")
        self.move_bar.pack(fill='x', side='top')

        # Project title abbreviation
        no_space_title = project_name.replace(' ', '')
        title_abbr = no_space_title[:5]
        self.title_label = tk.Label(self.move_bar, text=title_abbr, bg=BAR_AND_BORDER_COLOR, fg=text_hex_color, font=c.FONT_COMPACT_TITLE)
        self.title_label.pack(side='left', padx=(4, 0))

        # --- Close Button ---
        self.close_button = tk.Label(self.move_bar, image=self.parent.assets.compact_mode_close_image, bg=BAR_AND_BORDER_COLOR, cursor="hand2")
        self.close_button.pack(side='right', padx=(0, 1))

        # --- Button Container ---
        button_container = tk.Frame(self, bg=c.DARK_BG)
        button_container.pack(fill='both', expand=True, pady=(1,0))

        button_font = c.FONT_SMALL_BUTTON
        button_height = 24
        button_radius = 4
        button_fg = '#FFFFFF'

        if show_wrapped_button:
            self.copy_wrapped_button = RoundedButton(
                button_container, text="Copy Wrapped", font=button_font,
                bg=c.BTN_BLUE, fg=button_fg,
                command=self.parent.copy_wrapped_code,
                height=button_height, radius=button_radius, cursor='hand2'
            )
            self.copy_wrapped_button.pack(fill='x', expand=True, pady=(0, 1))

        self.copy_merged_button = RoundedButton(
            button_container, text="Copy Merged", font=button_font,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            command=self.parent.copy_merged_code,
            height=button_height, radius=button_radius, cursor='hand2'
        )
        self.copy_merged_button.pack(fill='x', expand=True, pady=(0, 1))

        self.paste_button = RoundedButton(
            button_container, text="Paste", font=button_font,
            bg=c.BTN_GREEN, fg=button_fg,
            command=None, # We use custom bindings instead
            height=button_height, radius=button_radius, cursor='hand2'
        )
        self.paste_button.pack(fill='x', expand=True)

        # Override the command with specific bindings for ctrl-click
        self.paste_button.bind("<Button-1>", self.on_paste_click)
        self.paste_button.unbind("<ButtonRelease-1>") # remove the original release binding
        self.paste_button.bind("<ButtonRelease-1>", self.on_paste_release)

        # --- Bindings ---
        self.move_bar.bind("<ButtonPress-1>", self.on_press_drag)
        self.move_bar.bind("<B1-Motion>", self.on_drag)
        self.move_bar.bind("<ButtonRelease-1>", self.on_release_drag)
        self.move_bar.bind("<Double-Button-1>", self.close_window)
        self.title_label.bind("<ButtonPress-1>", self.on_press_drag)
        self.title_label.bind("<B1-Motion>", self.on_drag)
        self.title_label.bind("<ButtonRelease-1>", self.on_release_drag)
        self.title_label.bind("<Double-Button-1>", self.close_window)
        self.close_button.bind("<Button-1>", self.close_window)

        # Tooltips
        if show_wrapped_button:
            self.copy_wrapped_button.bind("<Enter>", lambda e: self.show_tooltip("Copy with intro/outro text"))
            self.copy_wrapped_button.bind("<Leave>", self.hide_tooltip)
        self.copy_merged_button.bind("<Enter>", lambda e: self.show_tooltip("Copy with 'Copy Merged' prompt"))
        self.copy_merged_button.bind("<Leave>", self.hide_tooltip)
        self.paste_button.bind("<Enter>", lambda e: self.show_tooltip("Open paste window (Ctrl+Click to paste from clipboard)"))
        self.paste_button.bind("<Leave>", self.hide_tooltip)

    def on_paste_click(self, event):
        # This re-implements the click visual from RoundedButton
        self.paste_button._draw(self.paste_button.click_color)

    def on_paste_release(self, event):
        # This re-implements the release visual and command logic
        self.paste_button._draw(self.paste_button.hover_color)
        is_ctrl = (event.state & 0x0004)
        if is_ctrl:
            self.parent.apply_changes_from_clipboard()
        else:
            self.parent.open_paste_changes_dialog()

    def show_warning(self, file_count, project_name):
        if not self.new_files_label:
            self.new_files_label = tk.Label(self.move_bar, image=self.parent.assets.new_files_icon, bg=self.move_bar.cget('bg'))
            self.new_files_label.pack(side='right', before=self.close_button)

    def hide_warning(self, project_name):
        if self.new_files_label:
            self.new_files_label.destroy()
            self.new_files_label = None

    def show_tooltip(self, text, event=None):
        if self.tooltip_window: return
        x = self.winfo_rootx() + self.winfo_width() // 2
        y = self.winfo_rooty() + self.winfo_height() + 5
        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=text, justify='left', bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1, font=c.FONT_TOOLTIP)
        label.pack(ipadx=4, ipady=2)
        self.tooltip_window.update_idletasks()
        new_x = x - (self.tooltip_window.winfo_width() // 2)
        self.tooltip_window.wm_geometry(f"+{new_x}+{y}")

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

    def close_window(self, event=None):
        if self.close_callback:
            self.close_callback()

    def on_press_drag(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def on_drag(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def on_release_drag(self, event):
        if self.on_move_callback:
            self.on_move_callback()