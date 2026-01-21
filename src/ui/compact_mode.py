import tkinter as tk
from tkinter import messagebox
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
        self.new_files_button = None
        self.show_wrapped_button = show_wrapped_button
        self.current_new_file_count = 0

        # --- Style and Layout Constants ---
        BAR_COLOR = instance_color
        BORDER_COLOR = "#CCCCCC"
        BORDER_WIDTH = c.COMPACT_MODE_BORDER_WIDTH
        MOVE_BAR_HEIGHT = c.COMPACT_MODE_MOVE_BAR_HEIGHT
        text_hex_color = c.TEXT_COLOR if font_color_name == 'light' else '#000000'

        # --- Window Configuration ---
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(bg=BORDER_COLOR, padx=BORDER_WIDTH, pady=BORDER_WIDTH)

        # --- Internal State for Dragging ---
        self._offset_x = 0
        self._offset_y = 0

        # Main internal container
        self.main_container = tk.Frame(self, bg=c.DARK_BG)
        self.main_container.pack(fill='both', expand=True)

        # --- Move Bar (Header) ---
        self.move_bar = tk.Frame(self.main_container, height=MOVE_BAR_HEIGHT, bg=BAR_COLOR, cursor="fleur")
        self.move_bar.pack(fill='x', side='top')

        # --- App Icon ---
        self.app_icon_image = self.parent.assets.compact_icon_tk
        if self.app_icon_image:
            self.app_icon_label = tk.Label(self.move_bar, image=self.app_icon_image, bg=BAR_COLOR)
            self.app_icon_label.pack(side='left', padx=(2, 1), pady=3)

        # --- Project title abbreviation logic ---
        max_len = c.COMPACT_MODE_PROJECT_TITLE_MAX_LENGTH
        capital_indices = [i for i, char in enumerate(project_name) if 'A' <= char <= 'Z']

        if len(capital_indices) > 1:
            lowercase_indices = [i for i, char in enumerate(project_name) if 'a' <= char <= 'z']
            lowercase_needed = max_len - len(capital_indices)

            if lowercase_needed > 0:
                indices_to_keep = capital_indices + lowercase_indices[:lowercase_needed]
            else:
                indices_to_keep = capital_indices[:max_len]

            indices_to_keep.sort()
            title_abbr = "".join(project_name[i] for i in indices_to_keep)
        else:
            no_space_title = project_name.replace(' ', '')
            title_abbr = no_space_title[:max_len]

        self.title_label = tk.Label(self.move_bar, text=title_abbr, bg=BAR_COLOR, fg=text_hex_color, font=c.FONT_COMPACT_TITLE)
        self.title_label.pack(side='left', padx=(0, 4))

        # --- Right-aligned icons container ---
        self.right_icons_frame = tk.Frame(self.move_bar, bg=BAR_COLOR)
        self.right_icons_frame.pack(side='right')

        # --- Close Button ---
        self.close_button = tk.Label(self.right_icons_frame, image=self.parent.assets.compact_mode_close_image, bg=BAR_COLOR, cursor="hand2")
        self.close_button.pack(side='right', padx=(0, 1))

        # --- Button Container (Body) ---
        button_container = tk.Frame(self.main_container, bg=c.DARK_BG, padx=4, pady=0)
        button_container.pack(fill='x', side='top')

        button_font = c.FONT_COMPACT_BUTTON
        button_height = 24
        button_radius = 4
        button_fg = '#FFFFFF'

        # Unified copy button
        copy_button_text = "Copy" if self.show_wrapped_button else "Copy Code Only"
        copy_button_bg = c.BTN_BLUE if self.show_wrapped_button else c.BTN_GRAY_BG
        copy_button_fg = c.BTN_BLUE_TEXT if self.show_wrapped_button else c.BTN_GRAY_TEXT
        self.copy_button = RoundedButton(
            button_container, text=copy_button_text, font=button_font,
            bg=copy_button_bg, fg=copy_button_fg,
            command=None,
            height=button_height, radius=button_radius, cursor='hand2'
        )
        self.copy_button.pack(fill='x', pady=(4, 2))

        self.paste_button = RoundedButton(
            button_container, text="Paste", font=button_font,
            bg=c.BTN_GREEN, fg=button_fg,
            command=None,
            height=button_height, radius=button_radius, cursor='hand2'
        )
        self.paste_button.pack(fill='x', pady=(2, 4))

        # Override the command with specific bindings for ctrl-click
        self.copy_button.bind("<Button-1>", self.on_copy_click)
        self.copy_button.unbind("<ButtonRelease-1>")
        self.copy_button.bind("<ButtonRelease-1>", self.on_copy_release)

        self.paste_button.bind("<Button-1>", self.on_paste_click)
        self.paste_button.unbind("<ButtonRelease-1>")
        self.paste_button.bind("<ButtonRelease-1>", self.on_paste_release)

        # --- Bindings ---
        self.move_bar.bind("<ButtonPress-1>", self.on_press_drag)
        self.move_bar.bind("<B1-Motion>", self.on_drag)
        self.move_bar.bind("<ButtonRelease-1>", self.on_release_drag)
        self.move_bar.bind("<Double-Button-1>", self.close_window)
        self.title_label.bind("<ButtonPress-1>", self.on_press_drag)
        self.title_label.bind("<B1-Motion>", self.on_drag)
        self.title_label.bind("<ButtonRelease-1>", self.on_title_release)
        self.title_label.bind("<Double-Button-1>", self.close_window)
        self.right_icons_frame.bind("<ButtonPress-1>", self.on_press_drag)
        self.right_icons_frame.bind("<B1-Motion>", self.on_drag)
        self.right_icons_frame.bind("<ButtonRelease-1>", self.on_release_drag)
        self.right_icons_frame.bind("<Double-Button-1>", self.close_window)
        self.close_button.bind("<ButtonRelease-1>", self.close_window)

        if self.app_icon_image:
            self.app_icon_label.bind("<ButtonPress-1>", self.on_press_drag)
            self.app_icon_label.bind("<B1-Motion>", self.on_drag)
            self.app_icon_label.bind("<ButtonRelease-1>", self.on_release_drag)
            self.app_icon_label.bind("<Double-Button-1>", self.close_window)

        # Tooltips
        copy_tooltip_text = "Copy with instructions (Ctrl+Click for 'Code Only')" if self.show_wrapped_button else "Copy just the code"
        self.copy_button.bind("<Enter>", lambda e: self.show_tooltip(copy_tooltip_text))
        self.copy_button.bind("<Leave>", self.hide_tooltip)
        self.paste_button.bind("<Enter>", lambda e: self.show_tooltip("Open paste window\n(Ctrl+Click to paste from clipboard)"))
        self.paste_button.bind("<Leave>", self.hide_tooltip)
        self.close_button.bind("<Enter>", lambda e: self.show_tooltip("Restore window (Ctrl+Click to exit app)"))
        self.close_button.bind("<Leave>", self.hide_tooltip)

        # Keyboard shortcuts
        self.bind("<Control-c>", lambda event: self.parent.action_handlers.copy_wrapped_code())
        self.bind("<Control-Shift-C>", lambda event: self.parent.action_handlers.copy_merged_code())
        self.bind("<Control-v>", lambda event: self.parent.action_handlers.open_paste_changes_dialog())
        self.bind("<Control-Shift-V>", lambda event: self.parent.action_handlers.apply_changes_from_clipboard())

    def on_title_release(self, event):
        """Handles clicks on the title for shortcuts while maintaining drag logic."""
        self.on_release_drag(event)

        # Check if click was inside label boundaries
        if 0 <= event.x <= self.title_label.winfo_width() and 0 <= event.y <= self.title_label.winfo_height():
            is_ctrl = (event.state & 0x0004)
            is_alt = (event.state & 0x20000)

            # Only trigger if a shortcut modifier is held to avoid opening explorer on a standard drag/click
            if is_ctrl or is_alt:
                self.parent.action_handlers.open_project_folder(event)

    def on_copy_click(self, event):
        self.copy_button._draw(self.copy_button.click_color)

    def on_copy_release(self, event):
        if 0 <= event.x <= self.copy_button.winfo_width() and 0 <= event.y <= self.copy_button.winfo_height():
            self.copy_button._draw(self.copy_button.hover_color)
            is_ctrl = (event.state & 0x0004)
            if is_ctrl:
                self.parent.action_handlers.copy_merged_code(self.copy_button)
            else:
                if self.show_wrapped_button:
                    self.parent.action_handlers.copy_wrapped_code(self.copy_button)
                else:
                    self.parent.action_handlers.copy_merged_code(self.copy_button)
        else:
            self.copy_button._draw(self.copy_button.base_color)

    def on_paste_click(self, event):
        self.paste_button._draw(self.paste_button.click_color)

    def on_paste_release(self, event):
        if 0 <= event.x <= self.paste_button.winfo_width() and 0 <= event.y <= self.paste_button.winfo_height():
            self.paste_button._draw(self.paste_button.hover_color)
            is_ctrl = (event.state & 0x0004)
            if is_ctrl:
                self.parent.action_handlers.apply_changes_from_clipboard()
            else:
                self.parent.action_handlers.open_paste_changes_dialog()
        else:
            self.paste_button._draw(self.paste_button.base_color)

    def _exit_and_open_file_manager(self):
        self.close_callback()
        self.parent.after(int(c.ANIMATION_DURATION_SECONDS * 1000) + 50, self.parent.action_handlers.manage_files)

    def on_new_files_release(self, event):
        if self.new_files_button:
            if 0 <= event.x <= self.new_files_button.winfo_width() and 0 <= event.y <= self.new_files_button.winfo_height():
                self.new_files_button._draw(self.new_files_button.hover_color)
                self.hide_tooltip()
                is_ctrl = (event.state & 0x0004)
                if is_ctrl:
                    if self.current_new_file_count > 20:
                        if not messagebox.askyesno("Confirm Add All", f"You are about to add {self.current_new_file_count} files to the merge list.\n\nAre you sure?", parent=self):
                            self.new_files_button._draw(self.new_files_button.base_color)
                            return
                    self.parent.action_handlers.add_new_files_to_merge_order()
                else:
                    self._exit_and_open_file_manager()
            else:
                self.new_files_button._draw(self.new_files_button.base_color)

    def show_warning(self, file_count, project_name):
        self.current_new_file_count = file_count
        bg_color = self.move_bar.cget('bg')

        # Select the appropriate icon based on the threshold
        if file_count > 20:
            icon_image = self.parent.assets.new_files_many_compact_pil
        else:
            icon_image = self.parent.assets.new_files_compact_pil

        if not self.new_files_button:
            self.new_files_button = RoundedButton(
                self.right_icons_frame,
                command=None,
                image=icon_image,
                bg=bg_color,
                width=20,
                height=14,
                radius=3,
                cursor="hand2"
            )
            self.new_files_button.pack(side='left', padx=(0, 2))
            self.new_files_button.unbind("<ButtonRelease-1>")
            self.new_files_button.bind("<ButtonRelease-1>", self.on_new_files_release)
            tooltip_text = "New files found.\nClick: Open manager\nCtrl+Click: Add all to merge"
            self.new_files_button.bind("<Enter>", lambda e, text=tooltip_text: self.show_tooltip(text))
            self.new_files_button.bind("<Leave>", self.hide_tooltip)
        else:
            # If the button exists but the image requirement changed (e.g. crossed threshold), recreate it
            if self.new_files_button.image != icon_image:
                self.new_files_button.destroy()
                self.new_files_button = RoundedButton(
                    self.right_icons_frame,
                    command=None,
                    image=icon_image,
                    bg=bg_color,
                    width=20,
                    height=14,
                    radius=3,
                    cursor="hand2"
                )
                self.new_files_button.pack(side='left', padx=(0, 2))
                self.new_files_button.unbind("<ButtonRelease-1>")
                self.new_files_button.bind("<ButtonRelease-1>", self.on_new_files_release)
                tooltip_text = "New files found.\nClick: Open manager\nCtrl+Click: Add all to merge"
                self.new_files_button.bind("<Enter>", lambda e, text=tooltip_text: self.show_tooltip(text))
                self.new_files_button.bind("<Leave>", self.hide_tooltip)

    def hide_warning(self, project_name):
        if self.new_files_button:
            self.new_files_button.destroy()
            self.new_files_button = None

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
        if event and not (0 <= event.x <= event.widget.winfo_width() and 0 <= event.y <= event.widget.winfo_height()):
            return
        if event and (event.state & 0x0004):
            self.parent.event_handlers.on_app_close()
        elif self.close_callback:
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