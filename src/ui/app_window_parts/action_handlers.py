import os
import sys
import subprocess
import pyperclip
import time
from tkinter import messagebox, colorchooser

from ... import constants as c
from ..file_manager.file_manager_window import FileManagerWindow
from ..filetypes_manager import FiletypesManagerWindow
from ..settings.settings_window import SettingsWindow
from ..instructions_window import InstructionsWindow
from ..project_selector_dialog import ProjectSelectorDialog
from ..title_edit_dialog import TitleEditDialog
from ..paste_changes_dialog import PasteChangesDialog
from ..new_profile_dialog import NewProfileDialog
from ..project_starter.starter_dialog import ProjectStarterDialog
from ...core.clipboard import copy_project_to_clipboard
from ...core import change_applier
from ...core import prompts as p
from ...core.project_config import _calculate_font_color
from ...core.utils import get_file_hash, get_token_count_for_text

class ActionHandlers:
    def __init__(self, app):
        self.app = app

    def _is_valid_click(self, event):
        """Helper to ensure mouse release happened inside the widget."""
        if event is None: return True
        return 0 <= event.x <= event.widget.winfo_width() and 0 <= event.y <= event.widget.winfo_height()

    def copy_comment_cleanup_prompt(self, event=None):
        """Copies the standard comment cleanup instruction prompt to the clipboard."""
        if not self._is_valid_click(event): return

        pyperclip.copy(p.COMMENT_CLEANUP_PROMPT)
        self.app.helpers.show_compact_toast("Copied comment cleanup prompt")

    def open_project_starter(self, event=None):
        if not self._is_valid_click(event): return

        app = self.app
        if app.project_starter_window and app.project_starter_window.winfo_exists():
            app.project_starter_window.lift()
            app.project_starter_window.focus_force()
            return

        # Store the current project path before clearing the UI so it can be restored
        # if the user cancels the Project Starter.
        current_path = app.active_dir.get()
        if current_path and os.path.isdir(current_path):
            app._last_project_path = current_path
        else:
            app._last_project_path = None

        # Clear project UI to "No project selected" state before launching starter
        app.project_actions._clear_project_ui()

        app.project_starter_window = ProjectStarterDialog(app, app)

    def handle_title_click(self, event=None):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            self.open_project_selector()
            return

        if app.title_click_job:
            app.after_cancel(app.title_click_job)
            app.title_click_job = None

        app.title_click_job = app.after(250, self.open_project_selector)

    def edit_project_title(self, event=None):
        app = self.app
        if app.title_click_job:
            app.after_cancel(app.title_click_job)
            app.title_click_job = None

        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        current_name = project_config.project_name
        dialog = TitleEditDialog(
            parent=app,
            title="Edit Project Title",
            prompt="Enter the new title for the project:",
            initialvalue=current_name,
            max_length=c.PROJECT_TITLE_MAX_LENGTH
        )
        new_name = dialog.result

        if new_name is not None and new_name.strip() and new_name.strip() != current_name:
            new_name = new_name.strip()
            app.project_title_var.set(new_name)
            project_config.project_name = new_name
            project_config.save()
            app.status_var.set(f"Project title changed to '{new_name}'")

    def open_project_selector(self):
        app = self.app
        app.app_state._prune_recent_projects()
        ProjectSelectorDialog(
            parent=app,
            app_bg_color=app.app_bg_color,
            recent_projects=app.app_state.recent_projects,
            on_select_callback=app.ui_callbacks.on_directory_selected,
            on_remove_callback=app.ui_callbacks.on_recent_removed
        )

    def open_color_chooser(self, event=None):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config: return
        result = colorchooser.askcolor(title="Choose project color", initialcolor=app.project_color)
        if result and result[1]:
            new_hex_color = result[1]
            app.project_color = new_hex_color
            project_config.project_color = new_hex_color

            new_font_color = _calculate_font_color(new_hex_color)
            app.project_font_color = new_font_color
            project_config.project_font_color = new_font_color

            project_config.save()
            app.button_manager.update_button_states()

    def open_project_folder(self, event=None):
        if not self._is_valid_click(event): return

        app = self.app
        project_path = app.active_dir.get()

        if not (project_path and os.path.isdir(project_path)):
            app.status_var.set("No active project folder to open.")
            return

        is_ctrl_pressed = event and (event.state & 0x0004)
        is_alt_pressed = event and (event.state & 0x20000)

        # Priority 1: Alt -> Open Console
        if is_alt_pressed:
            try:
                if sys.platform == "win32":
                    # Environment Scrubbing
                    new_env = os.environ.copy()

                    # Strip core environment identification variables
                    venv_root = new_env.pop('VIRTUAL_ENV', None)
                    new_env.pop('PYTHONHOME', None)
                    new_env.pop('PYTHONPATH', None)
                    new_env.pop('PROMPT', None) # Remove the (.venv) prefix from shell prompt

                    # Identify directories to purge from PATH
                    purge_targets = []
                    if venv_root:
                        purge_targets.append(venv_root.lower())

                    bundle_dir = getattr(sys, '_MEIPASS', None)
                    if bundle_dir:
                        purge_targets.append(bundle_dir.lower())

                    # Also include the directory of the current executable/interpreter
                    exec_dir = os.path.dirname(sys.executable).lower()
                    purge_targets.append(exec_dir)

                    # Rebuild PATH correctly using os.pathsep (semicolon on Windows)
                    path_entries = new_env.get('PATH', '').split(os.pathsep)
                    cleaned_entries = []

                    for entry in path_entries:
                        if not entry: continue
                        entry_lower = entry.lower()

                        # Discard path if it starts with or resides within a purge target
                        should_purge = False
                        for target in purge_targets:
                            if entry_lower.startswith(target):
                                should_purge = True
                                break

                        if not should_purge:
                            cleaned_entries.append(entry)

                    new_env['PATH'] = os.pathsep.join(cleaned_entries)

                    # Launch clean shell
                    creationflags = subprocess.CREATE_NEW_CONSOLE
                    subprocess.Popen('cmd.exe', cwd=project_path, creationflags=creationflags, env=new_env)
                    app.helpers.show_compact_toast("Opened clean console in project folder")
                else:
                    app.status_var.set("Feature only available on Windows.")
            except Exception as e:
                app.show_error_dialog("Error", f"Could not open console: {e}")
            return

        # Priority 2: Ctrl -> Copy Path
        if is_ctrl_pressed:
            pyperclip.copy(project_path.replace('/', '\\'))
            app.helpers.show_compact_toast("Copied project path to clipboard")
            return

        # Priority 3: No modifiers -> Open in File Explorer
        try:
            if sys.platform == "win32":
                os.startfile(project_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", project_path])
            else:
                subprocess.Popen(["xdg-open", project_path])
        except Exception as e:
            app.show_error_dialog("Error", f"Could not open folder: {e}")

    def open_settings_window(self, event=None):
        if not self._is_valid_click(event): return
        app = self.app
        SettingsWindow(app, app.updater, on_close_callback=app.ui_callbacks.on_settings_closed)

    def open_instructions_window(self):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return
        wt_window = InstructionsWindow(app, project_config, app.status_var, on_close_callback=app.button_manager.update_button_states)
        app.wait_window(wt_window)

    def open_paste_changes_dialog(self, initial_content=None):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return
        PasteChangesDialog(app, project_config.base_dir, app.status_var, initial_content=initial_content)

    def on_paste_click(self, event):
        self.app.paste_changes_button._draw(self.app.paste_changes_button.click_color)

    def on_paste_release(self, event):
        app = self.app
        btn = app.paste_changes_button
        if 0 <= event.x <= btn.winfo_width() and 0 <= event.y <= btn.winfo_height():
            btn._draw(btn.hover_color)
            is_ctrl = (event.state & 0x0004)
            is_alt = (event.state & 0x20000)

            if is_alt:
                # Manual paste window (old default)
                self.open_paste_changes_dialog()
            elif is_ctrl:
                # Toggle feedback (opposite of setting)
                self.apply_changes_from_clipboard(force_toggle_feedback=True)
            else:
                # Default behavior: Apply changes (follows setting)
                self.apply_changes_from_clipboard(force_toggle_feedback=False)
        else:
            btn._draw(btn.base_color)

    def open_filetypes_manager(self, event=None):
        if not self._is_valid_click(event): return
        app = self.app
        FiletypesManagerWindow(app, on_close_callback=app.ui_callbacks.reload_active_extensions)

    def copy_merged_code(self, button=None):
        self._perform_copy(use_wrapper=False, button=button)

    def copy_wrapped_code(self, button=None):
        self._perform_copy(use_wrapper=True, button=button)

    def _perform_copy(self, use_wrapper: bool, button=None):
        app = self.app
        base_dir = app.active_dir.get()
        if not os.path.isdir(base_dir):
            app.show_error_dialog("Error", "Please select a valid project folder first")
            app.status_var.set("Error: Invalid project folder")
            return

        project_config = app.project_manager.get_current_project()
        if not project_config:
            app.status_var.set("Error: No active project.")
            return

        # Attempt to auto-detect button if none provided (e.g. from keyboard shortcut)
        if button is None:
            if app.view_manager.current_state == 'compact' and app.view_manager.compact_mode_window:
                button = app.view_manager.compact_mode_window.copy_button
            else:
                button = app.copy_wrapped_button if use_wrapper else app.copy_merged_button

        # Visual feedback: set button to loading
        if button:
            button.set_loading(True, "Merging")
            app.update() # Force UI refresh to show loading state

        try:
            status_message = copy_project_to_clipboard(
                parent=app,
                base_dir=base_dir,
                project_config=project_config,
                use_wrapper=use_wrapper,
                copy_merged_prompt=app.app_state.copy_merged_prompt,
                scan_secrets_enabled=app.app_state.scan_for_secrets
            )
            app.status_var.set(status_message)
        finally:
            if button:
                button.set_loading(False)

    def manage_files(self):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return

        files_to_highlight = app.file_monitor.get_newly_detected_files_and_reset()

        fm_window = FileManagerWindow(
            app,
            project_config,
            app.status_var,
            app.file_extensions,
            app.app_state.default_editor,
            app_state=app.app_state,
            newly_detected_files=files_to_highlight
        )
        app.wait_window(fm_window)
        app.button_manager.update_button_states()

    def on_new_files_click(self, event):
        if not self._is_valid_click(event): return
        is_ctrl = (event.state & 0x0004)
        if is_ctrl:
            self.add_new_files_to_merge_order()
        else:
            self.manage_files()

    def add_new_files_to_merge_order(self):
        """Adds current unknown files to the merge order for the active profile."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        # Use the monitor's list which reflects the active profile's unknowns
        new_files = list(app.file_monitor.newly_detected_files)

        if not new_files:
            app.status_var.set("No new files to add.")
            return

        current_selection_paths = {f['path'] for f in project_config.selected_files}
        files_to_add = [path for path in new_files if path not in current_selection_paths]

        if files_to_add:
            for path in files_to_add:
                new_entry = self._calculate_stats_for_file(path)
                if new_entry:
                    project_config.selected_files.append(new_entry)

            project_config.total_tokens = sum(f.get('tokens', 0) for f in project_config.selected_files)
            app.status_var.set(f"Added {len(files_to_add)} new file(s) to merge list.")
        else:
            app.status_var.set("New files already acknowledged.")

        # This method clears the active profile's unknown list and updates the UI
        app.file_monitor.get_newly_detected_files_and_reset()
        app.button_manager.update_button_states()

    def _calculate_stats_for_file(self, path):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config: return None
        full_path = os.path.join(project_config.base_dir, path)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            mtime = os.path.getmtime(full_path)
            file_hash = f"{os.path.getsize(full_path)}-{mtime}" # Simplified hash for speed

            token_count_enabled = app.app_state.config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT)
            if token_count_enabled:
                tokens = get_token_count_for_text(content)
                lines = content.count('\n') + 1
            else:
                tokens, lines = 0, 0

            if file_hash is not None:
                return {'path': path, 'mtime': mtime, 'hash': file_hash, 'tokens': tokens, 'lines': lines}
        except OSError:
            app.show_error_dialog("File Access Error", f"Could not access file to add it to the merge list:\n{path}")
        return None

    def apply_changes_from_clipboard(self, force_toggle_feedback=False):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first", parent=app)
            return

        markdown_text = pyperclip.paste()
        if not markdown_text.strip():
            app.helpers.show_compact_toast("Clipboard is empty.")
            return

        plan = change_applier.parse_and_plan_changes(project_config.base_dir, markdown_text)
        self._handle_parsed_plan(plan, project_config.base_dir, force_toggle_feedback=force_toggle_feedback)

    def _handle_parsed_plan(self, plan, base_dir, dialog_to_close=None, force_toggle_feedback=False):
        status = plan.get('status')
        message = plan.get('message')
        hint = plan.get('hint')

        if status == 'ERROR':
            self.app.show_error_dialog("Parsing Error", message, hint=hint)
            return

        self.app.last_ai_response = plan
        self.app.button_manager.update_button_states()

        def do_execute(filtered_updates=None, filtered_creations=None, filtered_deletions=None, is_changes_tab_active=False):
            """Writes files to disk. Returns True on success, False if cancelled or error."""

            # Use provided lists (from Review window) or default to the full parsed plan
            updates = filtered_updates if filtered_updates is not None else plan.get('updates', {})
            creations = filtered_creations if filtered_creations is not None else plan.get('creations', {})
            deletions = filtered_deletions if filtered_deletions is not None else plan.get('deletions_proposed', [])

            # If we are not in a review window and there are creations OR deletions, warn the user.
            if not dialog_to_close:
                warning_parts = []

                # Creations: Warning is suppressed if user is currently looking at the Changes tab.
                if creations and not is_changes_tab_active:
                    warning_parts.append(f"CREATE {len(creations)} file(s):\n- " + "\n- ".join(creations.keys()))

                # Deletions: ALWAYS warn for safety.
                if deletions:
                    warning_parts.append(f"DELETE {len(deletions)} file(s):\n- " + "\n- ".join(deletions))

                if warning_parts:
                    confirm_message = "This operation will perform the following actions:\n\n" + "\n\n".join(warning_parts) + "\n\nDo you want to proceed?"

                    dialog_parent = self.app
                    if self.app.view_manager.current_state == 'compact' and self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
                        dialog_parent = self.app.view_manager.compact_mode_window

                    if not messagebox.askyesno("Confirm File Actions", confirm_message, parent=dialog_parent):
                        self.app.helpers.show_compact_toast("Operation cancelled.")
                        return False

            success, final_message = change_applier.execute_plan(base_dir, updates, creations, deletions)

            if success:
                self.app.helpers.show_compact_toast(final_message)
                if creations or deletions:
                    self.app.file_monitor.perform_new_file_check()

                # Refresh main UI buttons
                self.app.button_manager.update_button_states()

                return True
            else:
                self.app.show_error_dialog("File Write Error", final_message)
                return False

        def do_refuse():
            self.app.helpers.show_compact_toast("Update refused.")
            if dialog_to_close:
                dialog_to_close.destroy()

        show_feedback_setting = self.app.app_state.config.get('show_feedback_on_paste', True)
        should_show = (not show_feedback_setting) if force_toggle_feedback else show_feedback_setting
        is_unformatted_only = (status == 'UNFORMATTED')

        if should_show:
            if dialog_to_close:
                dialog_to_close.destroy()
                dialog_to_close = None

            on_apply_cb = do_execute if not is_unformatted_only else None
            self.show_response_review(plan=plan, on_apply=on_apply_cb, on_refuse=do_refuse)
        elif not is_unformatted_only:
            do_execute()
        else:
            self.app.helpers.show_compact_toast("Error: LLM response followed no usable format.")

    def show_response_review(self, plan=None, on_apply=None, on_refuse=None, force_verification=False):
        """
        Opens the AI Response Review window.
        Uses either the provided plan (from a fresh paste) or the cached last response.
        Overwrites any currently open review window to allow sequential pasting.
        """
        existing = getattr(self.app, 'active_feedback_dialog', None)
        if existing and existing.winfo_exists():
            if existing.on_apply_executor is not None:
                dialog_parent = self.app
                if self.app.view_manager.current_state == 'compact' and self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
                    dialog_parent = self.app.view_manager.compact_mode_window

                msg = "An AI response review is already open with changes that haven't been applied yet.\n\nAre you sure you want to overwrite it?"
                if not messagebox.askyesno("Confirm Overwrite", msg, parent=dialog_parent):
                    return

            existing.destroy()

        if plan is None:
            plan = getattr(self.app, 'last_ai_response', None)
            if plan and on_apply is None:
                project = self.app.project_manager.get_current_project()
                if project:
                    def do_execute_cached(u=None, c_list=None, d=None, is_changes_tab_active=False):
                        # Re-use the existing do_execute logic
                        updates = u if u is not None else plan.get('updates', {})
                        creations = c_list if c_list is not None else plan.get('creations', {})
                        deletions = d if d is not None else plan.get('deletions_proposed', [])

                        # Pass the tab state to ensure warnings are handled correctly for cached resumes
                        success, final_message = change_applier.execute_plan(project.base_dir, updates, creations, deletions)
                        if success:
                            self.app.helpers.show_compact_toast(final_message)
                            self.app.button_manager.update_button_states()
                            return True
                        else:
                            self.app.show_error_dialog("File Write Error", final_message)
                            return False

                    on_apply = do_execute_cached

        if plan is None:
            self.app.helpers.show_compact_toast("No AI response review available yet.")
            return

        from ..feedback_dialog import FeedbackDialog

        dialog_parent = self.app
        if self.app.view_manager.current_state == 'compact' and self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
            dialog_parent = self.app.view_manager.compact_mode_window

        self.app.active_feedback_dialog = FeedbackDialog(dialog_parent, plan, on_apply=on_apply, on_refuse=on_refuse, force_verification=force_verification)