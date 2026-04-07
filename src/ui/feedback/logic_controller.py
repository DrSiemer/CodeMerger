import tkinter as tk
import pyperclip
import time
from tkinter import messagebox
from ... import constants as c
from ..window_utils import position_window, save_window_geometry
from ...core.utils import save_config
from ...core import change_applier

class FeedbackLogicController:
    """
    Handles window-level actions, settings, and high-level logic for the Feedback Dialog.
    """
    def __init__(self, window):
        self.window = window
        self._lazy_timer = None
        self._is_lazy_hiding = False
        self._last_size = (0, 0)

    def finalize_boot(self):
        """Standardizes geometry and focus after construction."""
        window = self.window

        # Position and sizing
        initial_w, initial_h = 900, 750
        if window.app_state and window.app_state.info_mode_active:
            initial_h += c.INFO_PANEL_HEIGHT
        window.geometry(f"{initial_w}x{initial_h}")
        window.minsize(600, 500)
        window.resizable(True, True)
        position_window(window)

        # Bindings
        window.bind("<Escape>", lambda e: self.handle_escape())
        window.protocol("WM_DELETE_WINDOW", self.on_close_request if window.on_apply_executor else window.destroy)
        window.bind("<Configure>", self.on_configure)

        # Tab Selection
        if window.force_verification and 'verification' in window.tab_indices:
            window.notebook.select(window.tab_indices['verification'])
        elif window.notebook.tabs():
            window.notebook.select(0)

        self.window.deiconify()

    def register_info(self, info_mgr):
        """Binds info documentation to top-level window controls."""
        window = self.window
        info_mgr.register(window.notebook, "review_tabs")
        info_mgr.register(window.auto_show_chk, "review_auto_show")
        info_mgr.register(window.info_toggle_btn, "info_toggle")

        if window.on_apply_executor:
            info_mgr.register(window.apply_btn, "review_apply")
            info_mgr.register(window.cancel_btn, "review_cancel")
        else:
            info_mgr.register(window.ok_button, "review_close")

        if hasattr(window, 'admonish_btn'):
            info_mgr.register(window.admonish_btn, "review_admonish")

        for widget, key in window.tab_widgets_for_info:
            info_mgr.register(widget, key)

    def on_configure(self, event):
        """Implements Resize Guard (Lazy Layout) to maintain UI responsiveness."""
        if event.widget != self.window: return
        new_size = (event.width, event.height)
        if self._last_size == new_size: return
        self._last_size = new_size

        if not self._is_lazy_hiding:
            self._start_lazy_layout()

        if self._lazy_timer:
            self.window.after_cancel(self._lazy_timer)
        self._lazy_timer = self.window.after(c.LAZY_LAYOUT_DELAY_MS, self._end_lazy_layout)

    def _start_lazy_layout(self):
        self._is_lazy_hiding = True
        self.window.notebook.grid_remove()

    def _end_lazy_layout(self):
        self.window.notebook.grid()
        self._is_lazy_hiding = False
        self._lazy_timer = None
        self.window.update_idletasks()

    def handle_apply_all(self):
        """Executes the batch apply logic for all pending changes."""
        window = self.window
        plan = window.plan

        pending_updates = {p: c for p, c in plan.get('updates', {}).items() if window.file_states.get(p) == "pending"}
        pending_creations = {p: c for p, c in plan.get('creations', {}).items() if window.file_states.get(p) == "pending"}
        pending_deletions = [p for p in plan.get('deletions_proposed', []) if window.file_states.get(p) == "pending"]

        if not (pending_updates or pending_creations or pending_deletions):
            return

        current_tab_text = window.notebook.tab(window.notebook.select(), "text")
        is_changes_tab = (current_tab_text == "Changes")

        # Create individual backups
        for path in list(pending_updates.keys()) + pending_deletions:
            if path not in window.undo_buffer:
                 window.undo_buffer[path] = change_applier.get_current_file_content(window.base_dir, path)

        if window.on_apply_executor(pending_updates, pending_creations, pending_deletions, is_changes_tab_active=is_changes_tab) is not False:
            for p in pending_updates: window.file_states[p] = "applied"
            for p in pending_creations: window.file_states[p] = "applied"
            for p in pending_deletions: window.file_states[p] = "deleted"

            window.changes.refresh_file_list_ui()

            if 'verification' in window.tab_indices:
                window.changes.update_mass_apply_visibility()
                window.cancel_btn.config(text="Close")
                window.notebook.select(window.tab_indices['verification'])
            else:
                window.destroy()

    def handle_cancel(self):
        """Explicitly refuses the proposed updates and closes the window."""
        if self.window.on_refuse:
            self.window.on_refuse()
        self.window.destroy()

    def handle_escape(self):
        if not self.window.on_apply_executor:
            self.window.destroy()
        else:
            self.on_close_request()

    def on_close_request(self):
        """Prompts user before discarding pending updates via manual close."""
        has_pending = any(s == "pending" for s in self.window.file_states.values())
        if has_pending:
            msg = "You are currently reviewing a proposed update. Closing this window will discard the changes.\n\nAre you sure?"
            if not messagebox.askyesno("Discard Update?", msg, parent=self.window):
                return
        self.handle_cancel()

    def copy_admonishment(self):
        """
        Copies formatting correction prompt to clipboard.
        Uses advanced fragmentation to prevent self-detection during code merging.
        """
        LT = "<"
        RT = ">"
        PRE = "--- "

        # Fragmented Tag names to ensure source file never contains a valid literal tag
        IN_T = "IN" + "TRO"
        ANS_W = "ANS" + "WERS" + " TO DIR" + "ECT USER QUE" + "STIONS"
        CHA_N = "CHA" + "NGES"
        VER_I = "VER" + "IFI" + "CATION"
        UNC_H = "UNC" + "HANGED"

        msg = (
            "Please follow the output format strictly as described in your instructions. "
            "Your previous response did not fully comply with the required formatting standards. "
            "Specifically, please ensure that:\n"
            f"- ALL commentary and explanations must be placed inside one of the allowed XML tags ({LT}{IN_T}{RT}, {LT}{ANS_W}{RT}, {LT}{CHA_N}{RT}, {LT}{VER_I}{RT}, {LT}{UNC_H}{RT}).\n"
            "- No text or commentary exists outside of these tags.\n"
            f"- File markers are present and correctly formatted ({PRE}File: `path` --- and {PRE}End of file ---).\n"
            "- You provide the full, complete code for modified files without using placeholders like '// ... rest of code'.\n"
            "Please re-output the response correctly."
        )
        pyperclip.copy(msg)
        self.window.admonish_btn.config(text="Copied!", bg=c.BTN_GREEN)
        self.window.after(2000, lambda: self.window.admonish_btn.config(text="Copy Correction Prompt", bg=c.ATTENTION) if self.window.admonish_btn.winfo_exists() else None)

    def adjust_font_size(self, delta):
        if not self.window.renderers: return
        new_size = max(8, min(self.window.renderers[0].base_font_size + delta, 40))
        for r in self.window.renderers: r.set_font_size(new_size)

    def save_feedback_setting(self):
        if not self.window.app_state: return
        self.window.app_state.config['show_feedback_on_paste'] = self.window.show_var.get()
        save_config(self.window.app_state.config)
        self.window.app.button_manager.refresh_paste_tooltips()

    def save_window_state(self):
        save_window_geometry(self.window)