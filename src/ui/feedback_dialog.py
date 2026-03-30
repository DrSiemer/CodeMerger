import tkinter as tk
import os
import pyperclip
from tkinter import Frame, Label, ttk, BooleanVar, messagebox
from PIL import Image, ImageDraw, ImageTk
from .. import constants as c
from .widgets.rounded_button import RoundedButton
from .widgets.markdown_renderer import MarkdownRenderer
from .window_utils import position_window, save_window_geometry
from .style_manager import apply_dark_theme
from ..core.paths import ICON_PATH
from ..core.utils import save_config
from .tooltip import ToolTip
from .info_manager import attach_info_mode
from .assets import assets

class FeedbackDialog(tk.Toplevel):
    def __init__(self, parent, plan, on_apply=None, on_refuse=None, force_verification=False):
        super().__init__(parent)
        self.parent = parent
        self.plan = plan
        self.on_apply = on_apply
        self.on_refuse = on_refuse

        # Identify the root App instance for global action handling
        self.app = parent
        while self.app and not hasattr(self.app, 'action_handlers'):
            self.app = getattr(self.app, 'parent', getattr(self.app, 'master', None))

        self.app_state = getattr(parent, 'app_state', getattr(parent.master, 'app_state', None))
        self.withdraw()
        self.title("AI Response Review")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)

        # Ensure grid is used on the Toplevel so the main frame and info panel never overlap
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Modality & Layering Logic
        is_parent_topmost = False
        try:
            is_parent_topmost = self.parent.attributes("-topmost")
        except Exception:
            pass

        if is_parent_topmost:
            # If spawned from Compact Mode, stay in front of IDE but don't lock the app
            self.attributes("-topmost", True)
        else:
            # If spawned from main window, behave as a standard dependent window
            self.transient(parent)

        apply_dark_theme(self)

        # Generate vertical accent bars for all tabs
        self._gray_accent = self._create_vertical_accent(c.TEXT_SUBTLE_COLOR)  # Intro / Placeholder
        self._cyan_accent = self._create_vertical_accent("#00BCD4")           # Answers
        self._blue_accent = self._create_vertical_accent(c.BTN_BLUE)          # Changes
        self._red_accent = self._create_vertical_accent(c.WARN)               # Delete
        self._green_accent = self._create_vertical_accent(c.BTN_GREEN)        # Verification
        self._yellow_accent = self._create_vertical_accent(c.ATTENTION)       # Unformatted

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Main Layout Rows: 0=Header, 1=UnformattedAlert, 2=Notebook, 3=BottomActions
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        header_row = Frame(main_frame, bg=c.DARK_BG)
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_row.columnconfigure(0, weight=1)

        title_text = "Review Proposed Update" if on_apply else "Review Last Update"
        Label(
            header_row,
            text=title_text,
            font=c.FONT_LARGE_BOLD,
            bg=c.DARK_BG,
            fg=c.TEXT_COLOR
        ).grid(row=0, column=0, sticky="w")

        # New Files Integration
        self.new_files_btn = None
        self._check_for_new_files(header_row)

        # Global Unformatted Alert Header
        has_any_tags = plan.get('has_any_tags', False)

        ordered_segments = plan.get('ordered_segments', [])
        orphan_segments = [s for s in ordered_segments if s['type'] == 'orphan']
        has_unformatted = len(orphan_segments) > 0

        self.alert_frame = Frame(main_frame, bg=c.DARK_BG)
        if has_unformatted and not has_any_tags:
            self.alert_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

            Label(
                self.alert_frame,
                text="This text was not properly wrapped in the requested XML tags",
                fg=c.WARN, bg=c.DARK_BG, font=c.FONT_NORMAL
            ).pack(side='left')

            self.admonish_btn = RoundedButton(
                self.alert_frame, text="Copy Correction Prompt", command=self._copy_admonishment,
                bg=c.ATTENTION, fg="#FFFFFF", font=c.FONT_SMALL_BUTTON,
                width=200, height=26, cursor="hand2"
            )
            self.admonish_btn.pack(side='right')
            ToolTip(self.admonish_btn, "Copy a prompt to tell the AI to follow the output format")

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        self.renderers = []
        self.tab_widgets_for_info = []

        self.tab_indices = {}

        # Build Tabs Chronologically
        current_idx = 0
        orphan_count = 0
        total_orphans = len(orphan_segments)

        for seg in ordered_segments:
            stype = seg['type']
            content = seg.get('content', "").strip()

            # Skip empty segments unless they are file placeholders (which mark relative positions)
            if not content and stype != 'file_placeholder':
                continue

            if stype == 'tag':
                tag_name = seg['tag']
                title = tag_name.replace("ANSWERS TO DIRECT USER QUESTIONS", "Answers").title()

                # Defaults
                icon = self._gray_accent
                info_key = "review_tab_placeholder"

                if "INTRO" in tag_name:
                    info_key = "review_tab_intro"
                elif "CHANGES" in tag_name:
                    icon = self._blue_accent
                    info_key = "review_tab_changes"
                elif "ANSWERS" in tag_name:
                    icon = self._cyan_accent
                    info_key = "review_tab_answers"
                elif "DELETED" in tag_name:
                    icon = self._red_accent
                    info_key = "review_tab_delete"
                elif "VERIFICATION" in tag_name:
                    icon = self._green_accent
                    info_key = "review_tab_verification"

                self._add_tab(title, content, icon=icon, info_key=info_key)

                # Store verification index for auto-navigation after apply
                if "VERIFICATION" in tag_name:
                    self.tab_indices['verification'] = current_idx

                current_idx += 1

            elif stype == 'orphan':
                orphan_count += 1
                title = "Unformatted output"

                if total_orphans > 1:
                    title = f"Unformatted ({orphan_count})"

                self._add_unformatted_tab(title, content)
                current_idx += 1

        # Placeholder if empty
        if current_idx == 0:
            msg = "The AI response contained only code blocks with no accompanying text or tagged sections."
            self._add_tab("Response Summary", msg, icon=self._gray_accent, info_key="review_tab_placeholder")
            current_idx += 1

        if current_idx > 0:
            # Decide starting tab
            if force_verification and 'verification' in self.tab_indices:
                self.notebook.select(self.tab_indices['verification'])
            else:
                self.notebook.select(0)

        self.bottom_frame = Frame(main_frame, bg=c.DARK_BG)
        self.bottom_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))

        # Checkbox
        show_val = self.app_state.config.get('show_feedback_on_paste', True) if self.app_state else True
        self.show_var = BooleanVar(value=show_val)
        self.auto_show_chk = ttk.Checkbutton(
            self.bottom_frame,
            text="Show this window automatically on paste",
            variable=self.show_var,
            style='Dark.TCheckbutton',
            command=self._save_setting
        )
        self.auto_show_chk.pack(side="left")

        if self.on_apply:
            # Determine if we have actual file content to commit
            has_changes = bool(plan.get('updates')) or bool(plan.get('creations'))

            if has_changes:
                self.apply_btn = RoundedButton(
                    self.bottom_frame, text="Apply Changes", command=self._handle_apply,
                    bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BOLD,
                    width=200, height=30, cursor="hand2"
                )
                self.apply_btn.pack(side="right")
                cancel_text = "Cancel"
            else:
                cancel_text = "Close"

            self.cancel_btn = RoundedButton(
                self.bottom_frame, text=cancel_text, command=self._handle_cancel,
                bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL,
                width=100, height=30, cursor="hand2"
            )
            self.cancel_btn.pack(side="right", padx=(0, 10))
        else:
            self.ok_button = RoundedButton(
                self.bottom_frame, text="OK", command=self.destroy,
                bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL,
                width=100, height=30, cursor="hand2"
            )
            self.ok_button.pack(side="right")

        # Bindings
        self.bind("<Escape>", lambda e: self.destroy() if not self.on_apply else self._on_close_request())

        # Shortcut passthrough allows overwriting via Ctrl+V while the review is active
        self.bind("<Control-v>", lambda e: self.app.action_handlers.apply_changes_from_clipboard(force_toggle_feedback=False))
        self.bind("<Control-Shift-V>", lambda e: self.app.action_handlers.apply_changes_from_clipboard(force_toggle_feedback=True))

        self.protocol("WM_DELETE_WINDOW", self._on_close_request if self.on_apply else self.destroy)

        initial_w, initial_h = 900, 750
        if self.app_state and self.app_state.info_mode_active:
            initial_h += c.INFO_PANEL_HEIGHT

        self.geometry(f"{initial_w}x{initial_h}")
        self.minsize(600, 500)
        position_window(self)

        # Info Mode Integration
        if self.app_state:
            self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")
            self.info_mgr = attach_info_mode(self, self.app_state, manager_type='grid', grid_row=1, toggle_btn=self.info_toggle_btn)

            self.info_mgr.register(self.notebook, "review_tabs")
            self.info_mgr.register(self.auto_show_chk, "review_auto_show")

            if hasattr(self, 'apply_btn'):
                self.info_mgr.register(self.apply_btn, "review_apply")
            if hasattr(self, 'cancel_btn'):
                self.info_mgr.register(self.cancel_btn, "review_cancel")
            if hasattr(self, 'ok_button'):
                self.info_mgr.register(self.ok_button, "review_close")
            if hasattr(self, 'admonish_btn'):
                self.info_mgr.register(self.admonish_btn, "review_admonish")

            # Granular registration for each tab's content
            for renderer, info_key in self.tab_widgets_for_info:
                self.info_mgr.register(renderer, info_key)
                if hasattr(renderer, 'text_widget'):
                    self.info_mgr.register(renderer.text_widget, info_key)

            self.info_mgr.register(self.info_toggle_btn, "info_toggle")
        else:
            self.info_mgr = None

        self.deiconify()

    def _check_for_new_files(self, container):
        """Adds a 'New Files' warning icon if the active project has unacknowledged files."""
        if not self.app:
            return

        new_count = len(self.app.file_monitor.newly_detected_files)
        if new_count > 0:
            icon = assets.new_files_icon
            self.new_files_btn = Label(container, image=icon, bg=c.DARK_BG, cursor="hand2")
            self.new_files_btn.grid(row=0, column=1, sticky="e")

            def handle_add_files(event):
                self.app.action_handlers.add_new_files_to_merge_order()
                self.new_files_btn.grid_forget()
                self.app.helpers.show_compact_toast(f"Added {new_count} new file(s) to merge list")

            self.new_files_btn.bind("<ButtonRelease-1>", handle_add_files)

            hint = f"{new_count} new files found.\nClick to add all to merge order immediately."
            ToolTip(self.new_files_btn, hint)

    def _create_vertical_accent(self, hex_color):
        """Creates a sharpened vertical bar PhotoImage shifted down 1px."""
        size = (14, 22)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 1, 3, 20], radius=1, fill=hex_color)
        return ImageTk.PhotoImage(img)

    def _add_tab(self, title, markdown_text, icon=None, info_key=None):
        frame = Frame(self.notebook, bg=c.DARK_BG)
        if icon:
            self.notebook.add(frame, text=title, image=icon, compound="left")
        else:
            self.notebook.add(frame, text=title)

        renderer = MarkdownRenderer(frame, base_font_size=11, on_zoom=self._adjust_font_size)
        renderer.pack(fill="both", expand=True)
        renderer.set_markdown(markdown_text.strip())
        self.renderers.append(renderer)

        if info_key:
            self.tab_widgets_for_info.append((renderer, info_key))

    def _add_unformatted_tab(self, title, raw_text):
        """Adds a specialized tab for text that wasn't properly wrapped in tags."""
        frame = Frame(self.notebook, bg=c.DARK_BG)
        self.notebook.add(frame, text=title, image=self._yellow_accent, compound="left")

        renderer = MarkdownRenderer(frame, base_font_size=11, on_zoom=self._adjust_font_size)
        renderer.pack(fill="both", expand=True)
        renderer.set_markdown(raw_text.strip())
        self.renderers.append(renderer)

        self.tab_widgets_for_info.append((renderer, "review_tab_unformatted"))

    def _copy_admonishment(self):
        msg = "Please follow the output format as described in your instructions, the tool cannot use this incorrectly formatted text."
        pyperclip.copy(msg)
        self.admonish_btn.config(text="Copied!", bg=c.BTN_GREEN)
        self.after(2000, lambda: self.admonish_btn.config(text="Copy Correction Prompt", bg=c.ATTENTION) if self.admonish_btn.winfo_exists() else None)

    def _adjust_font_size(self, delta):
        if not self.renderers:
            return
        new_size = self.renderers[0].base_font_size + delta
        new_size = max(8, min(new_size, 40))
        for r in self.renderers:
            r.set_font_size(new_size)

    def _save_setting(self):
        if not self.app_state:
            return
        self.app_state.config['show_feedback_on_paste'] = self.show_var.get()
        save_config(self.app_state.config)

        # Find the main App instance to notify it of the change so tooltips can update.
        app = self.parent
        while app and not hasattr(app, 'button_manager'):
            app = getattr(app, 'parent', getattr(app, 'master', None))

        if app and hasattr(app, 'button_manager'):
            app.button_manager.refresh_paste_tooltips()

    def _handle_apply(self):
        """Applies the changes. If verification steps exist, remains open to show them."""
        if self.on_apply:
            if self.on_apply() is False:
                return

            # Clear callbacks once executed to indicate the update is no longer pending.
            self.on_apply = None
            self.on_refuse = None

        if 'verification' in self.tab_indices:
            # Changes applied, so hide the decision buttons
            if hasattr(self, 'apply_btn'):
                self.apply_btn.pack_forget()
            self.cancel_btn.pack_forget()

            # Add a final Close/OK button to exit the window after verification is read
            self.ok_button = RoundedButton(
                self.bottom_frame, text="Close", command=self.destroy,
                bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL,
                width=100, height=30, cursor="hand2"
            )
            self.ok_button.pack(side="right")

            if hasattr(self, 'info_mgr') and self.info_mgr:
                self.info_mgr.register(self.ok_button, "review_close")

            # Navigate to verification steps automatically
            self.notebook.select(self.tab_indices['verification'])
        else:
            self.destroy()

    def _handle_cancel(self):
        """Discards the update immediately. Used by the explicit 'Cancel' button."""
        if self.on_refuse:
            self.on_refuse()
        self.destroy()

    def _on_close_request(self):
        """Warns the user before discarding the update if the window is closed manually."""
        if self.on_apply:
            # Check if there is actual code to discard
            has_changes = bool(self.plan.get('updates')) or bool(self.plan.get('creations'))
            if has_changes:
                if not messagebox.askyesno(
                    "Discard Update?",
                    "You are currently reviewing a proposed update. Closing this window will discard the changes and they will not be applied to your project files.\n\nAre you sure you want to discard this update?",
                    parent=self
                ):
                    return

        self._handle_cancel()

    def destroy(self):
        """Clears active reference and saves geometry before closing."""
        if hasattr(self.app, 'active_feedback_dialog'):
            self.app.active_feedback_dialog = None
        save_window_geometry(self)
        super().destroy()