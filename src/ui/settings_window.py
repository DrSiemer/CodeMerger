import os
import tkinter as tk
from tkinter import Toplevel, Frame, Label, Entry, filedialog, StringVar, BooleanVar, ttk, Text
from ..core.utils import load_config, save_config
from ..core.registry import get_setting, save_setting
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from .window_utils import position_window, save_window_geometry

class SettingsWindow(Toplevel):
    def __init__(self, parent, updater, on_close_callback=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.updater = updater
        self.on_close_callback = on_close_callback

        config = load_config()
        self.editor_path = StringVar(value=config.get('default_editor', ''))
        self.scan_for_secrets = BooleanVar(value=config.get('scan_for_secrets', False))
        self.check_for_updates = BooleanVar(value=get_setting('AutomaticUpdates', True))
        self.enable_new_file_check = BooleanVar(value=config.get('enable_new_file_check', True))
        self.new_file_check_interval = StringVar(value=str(config.get('new_file_check_interval', 5)))
        self.line_count_enabled = BooleanVar(value=config.get('line_count_enabled', c.LINE_COUNT_ENABLED_DEFAULT))
        self.line_count_threshold = StringVar(value=str(config.get('line_count_threshold', c.LINE_COUNT_THRESHOLD_DEFAULT)))

        # --- Style Definitions ---
        self.font_family = "Segoe UI"
        self.font_normal = (self.font_family, 12)
        self.font_bold = (self.font_family, 12, 'bold')
        self.font_button = (self.font_family, 16)

        # --- Window Setup ---
        self.title("Settings")
        self.iconbitmap(ICON_PATH)
        self.geometry("600x550")
        self.minsize(500, 300)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Main container frame ---
        main_frame = Frame(self, bg=c.DARK_BG)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # --- UI Layout with managed Scrollbar ---
        self.canvas = tk.Canvas(main_frame, bg=c.DARK_BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg=c.DARK_BG, padx=20, pady=20)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<MouseWheel>", self._on_mousewheel)

        # --- Style for ttk Widgets ---
        self.option_add('*TCombobox*Listbox.background', c.TEXT_INPUT_BG)
        self.option_add('*TCombobox*Listbox.foreground', c.TEXT_COLOR)
        self.option_add('*TCombobox*Listbox.selectBackground', c.BTN_BLUE)
        self.option_add('*TCombobox*Listbox.selectForeground', c.BTN_BLUE_TEXT)
        s = ttk.Style()
        s.theme_use('default')
        s.configure('Dark.TCheckbutton', background=c.DARK_BG, foreground=c.TEXT_COLOR, font=self.font_normal)
        s.map('Dark.TCheckbutton', background=[('active', c.DARK_BG)], indicatorcolor=[('selected', c.BTN_BLUE), ('!selected', c.TEXT_INPUT_BG)], indicatorrelief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        s.configure('Dark.TCombobox', fieldbackground=c.TEXT_INPUT_BG, background=c.TEXT_INPUT_BG, arrowcolor=c.TEXT_COLOR, foreground=c.TEXT_COLOR, selectbackground=c.TEXT_INPUT_BG, selectforeground=c.TEXT_COLOR)
        s.map('Dark.TCombobox', foreground=[('readonly', c.TEXT_COLOR)], fieldbackground=[('readonly', c.TEXT_INPUT_BG)])

        # --- All content goes into the scrollable_frame ---
        Label(self.scrollable_frame, text="Application Updates", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        updates_frame = Frame(self.scrollable_frame, bg=c.DARK_BG)
        updates_frame.pack(fill='x', expand=True, pady=(0, 15))

        self.check_now_button = RoundedButton(
            updates_frame,
            text="Check Now",
            command=self.run_manual_update_check,
            bg=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT,
            font=(self.font_family, 9),
            height=22,
            radius=4
        )
        self.check_now_button.pack(side='right', padx=(10, 0))

        self.update_checkbox = ttk.Checkbutton(updates_frame, text="Automatically check for updates daily", variable=self.check_for_updates, style='Dark.TCheckbutton')
        self.update_checkbox.pack(side='left')

        Label(self.scrollable_frame, text="File System Monitoring", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        file_system_frame = Frame(self.scrollable_frame, bg=c.DARK_BG)
        file_system_frame.pack(fill='x', expand=True, pady=(0, 15))
        self.new_file_check_checkbox = ttk.Checkbutton(file_system_frame, text="Periodically check for new project files", variable=self.enable_new_file_check, style='Dark.TCheckbutton', command=self.toggle_interval_selector)
        self.new_file_check_checkbox.pack(anchor='w')
        interval_frame = Frame(file_system_frame, bg=c.DARK_BG)
        interval_frame.pack(fill='x', padx=(25, 0), pady=(5, 0))
        self.interval_label = Label(interval_frame, text="Check every:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal)
        self.interval_label.pack(side='left', padx=(0, 10))
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.new_file_check_interval, values=['2', '5', '10', '30', '60'], state='readonly', width=5, style='Dark.TCombobox')
        self.interval_combo.pack(side='left')
        Label(interval_frame, text="seconds", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal).pack(side='left', padx=(5, 0))
        self.toggle_interval_selector()

        Label(self.scrollable_frame, text="Secret Scanning", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        secrets_frame = Frame(self.scrollable_frame, bg=c.DARK_BG)
        secrets_frame.pack(fill='x', expand=True, pady=(0, 15))
        self.scan_checkbox = ttk.Checkbutton(secrets_frame, text="Scan for secrets on copy (slower)", variable=self.scan_for_secrets, style='Dark.TCheckbutton')
        self.scan_checkbox.pack(anchor='w')

        Label(self.scrollable_frame, text="Line Counting", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        line_count_frame = Frame(self.scrollable_frame, bg=c.DARK_BG)
        line_count_frame.pack(fill='x', expand=True, pady=(0, 15))
        self.line_count_checkbox = ttk.Checkbutton(line_count_frame, text="Count lines of code for selected files", variable=self.line_count_enabled, style='Dark.TCheckbutton', command=self.toggle_threshold_selector)
        self.line_count_checkbox.pack(anchor='w')
        threshold_frame = Frame(line_count_frame, bg=c.DARK_BG)
        threshold_frame.pack(fill='x', padx=(25, 0), pady=(5, 0))
        self.threshold_label = Label(threshold_frame, text="Only show count for files longer than:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal)
        self.threshold_label.pack(side='left', padx=(0, 10))
        vcmd = (self.register(self.validate_integer), '%P')
        self.threshold_entry = Entry(threshold_frame, textvariable=self.line_count_threshold, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=self.font_normal, validate='key', validatecommand=vcmd)
        self.threshold_entry.pack(side='left')
        self.lines_label = Label(threshold_frame, text="lines", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=self.font_normal)
        self.lines_label.pack(side='left', padx=(5, 0))
        self.toggle_threshold_selector()

        self.copy_merged_prompt_text = self._create_collapsible_text_section(self.scrollable_frame, '"Copy Merged" Prompt', config.get('copy_merged_prompt', ''), c.DEFAULT_COPY_MERGED_PROMPT)
        self.default_intro_text = self._create_collapsible_text_section(self.scrollable_frame, 'Default Intro Prompt', config.get('default_intro_prompt', ''), c.DEFAULT_INTRO_PROMPT)
        self.default_outro_text = self._create_collapsible_text_section(self.scrollable_frame, 'Default Outro Prompt', config.get('default_outro_prompt', ''), c.DEFAULT_OUTRO_PROMPT)

        Label(self.scrollable_frame, text="Default Editor", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        editor_frame = Frame(self.scrollable_frame, bg=c.DARK_BG)
        editor_frame.pack(fill='x', expand=True)
        self.editor_entry = Entry(editor_frame, textvariable=self.editor_path, state='readonly', readonlybackground=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, relief='flat', font=self.font_normal)
        self.editor_entry.pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=4)
        self.browse_button = RoundedButton(editor_frame, text="Browse...", command=self.browse_for_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=self.font_button)
        self.browse_button.pack(side='left', padx=(0, 5))
        self.clear_button = RoundedButton(editor_frame, text="Clear", command=self.clear_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=self.font_button)
        self.clear_button.pack(side='left')

        # --- Action Buttons (Outside scroll area) ---
        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=20, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        self.save_button = RoundedButton(button_frame, text="Save and Close", command=self.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=self.font_button)
        self.save_button.grid(row=0, column=1, sticky='e')

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Escape>', lambda e: self.on_closing())

        self._position_window()
        self.deiconify()

    def validate_integer(self, value_if_allowed):
        """Validation function to allow only integers in an Entry widget."""
        if value_if_allowed == "":
            return True
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._manage_scrollbar()

    def _on_canvas_configure(self, event=None):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)

        # Do not scroll the main canvas if the cursor is over a Text widget
        w = widget_under_cursor
        while w is not None:
            if isinstance(w, Text):
                return
            if w == self:
                break
            w = w.master

        if self.scrollbar.winfo_ismapped():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _manage_scrollbar(self):
        self.update_idletasks()
        frame_height = self.scrollable_frame.winfo_reqheight()
        canvas_height = self.canvas.winfo_height()
        if frame_height > canvas_height:
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.grid(row=0, column=1, sticky='ns')
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.grid_remove()

    def _create_collapsible_text_section(self, parent, title, initial_text, default_text):
        section_frame = Frame(parent, bg=c.DARK_BG)
        section_frame.pack(fill='x', expand=True, pady=(15, 0))

        header_frame = Frame(section_frame, bg=c.DARK_BG)
        header_frame.pack(fill='x', expand=True)

        body_frame = Frame(section_frame, bg=c.DARK_BG)
        text_frame = Frame(body_frame, bd=1, relief='sunken')
        text_frame.pack(fill='x', expand=True, padx=(22, 0))
        text_widget = Text(text_frame, wrap='word', undo=True, height=4, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', bd=0, highlightthickness=0, font=self.font_normal)
        text_widget.pack(fill='x', expand=True, ipady=4, ipadx=4)
        text_widget.insert('1.0', initial_text)

        icon_label = Label(header_frame, text="▶", font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR, cursor="hand2")
        icon_label.pack(side='left', padx=(0, 5))

        title_label = Label(header_frame, text=title, font=self.font_bold, bg=c.DARK_BG, fg=c.TEXT_COLOR, cursor="hand2")
        title_label.pack(side='left')

        def do_reset():
            text_widget.delete('1.0', 'end')
            text_widget.insert('1.0', default_text)

        reset_button = RoundedButton(
            header_frame,
            text="Reset",
            command=do_reset,
            bg=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT,
            font=(self.font_family, 9),
            height=22,
            radius=4
        )
        reset_button.pack(side='right', padx=(5, 0))

        is_expanded = BooleanVar(value=False)
        def toggle_section(event=None):
            is_expanded.set(not is_expanded.get())
            if is_expanded.get():
                body_frame.pack(fill='x', expand=True, pady=(2, 0))
                icon_label.config(text="▼")
            else:
                body_frame.pack_forget()
                icon_label.config(text="▶")
            self.after(5, self._on_frame_configure)

        icon_label.bind("<Button-1>", toggle_section)
        title_label.bind("<Button-1>", toggle_section)

        return text_widget

    def run_manual_update_check(self):
        """Triggers the manual update check in the updater module."""
        self.updater.check_for_updates_manual()

    def toggle_interval_selector(self):
        new_state = 'normal' if self.enable_new_file_check.get() else 'disabled'
        self.interval_label.config(state=new_state)
        self.interval_combo.config(state='readonly' if self.enable_new_file_check.get() else 'disabled')

    def toggle_threshold_selector(self):
        new_state = 'normal' if self.line_count_enabled.get() else 'disabled'
        self.threshold_label.config(state=new_state)
        self.threshold_entry.config(state=new_state)
        self.lines_label.config(state=new_state)

    def browse_for_editor(self):
        file_types = [("Executable files", "*.exe"), ("All files", "*.*")] if os.name == 'nt' else []
        filepath = filedialog.askopenfilename(title="Select Editor Application", filetypes=file_types, parent=self)
        if filepath:
            self.editor_path.set(filepath)

    def clear_editor(self):
        self.editor_path.set('')

    def on_closing(self):
        self._close_and_save_geometry()

    def save_and_close(self):
        config = load_config()
        config['default_editor'] = self.editor_path.get()
        config['scan_for_secrets'] = self.scan_for_secrets.get()
        config['copy_merged_prompt'] = self.copy_merged_prompt_text.get('1.0', 'end-1c')
        config['default_intro_prompt'] = self.default_intro_text.get('1.0', 'end-1c')
        config['default_outro_prompt'] = self.default_outro_text.get('1.0', 'end-1c')
        config['enable_new_file_check'] = self.enable_new_file_check.get()
        config['line_count_enabled'] = self.line_count_enabled.get()

        try:
            config['new_file_check_interval'] = int(self.new_file_check_interval.get())
        except ValueError:
            config['new_file_check_interval'] = 5

        try:
            threshold_val = self.line_count_threshold.get()
            config['line_count_threshold'] = int(threshold_val) if threshold_val else 0
        except ValueError:
            config['line_count_threshold'] = c.LINE_COUNT_THRESHOLD_DEFAULT

        save_config(config)
        save_setting('AutomaticUpdates', self.check_for_updates.get())
        if self.on_close_callback:
            self.on_close_callback()
        self._close_and_save_geometry()