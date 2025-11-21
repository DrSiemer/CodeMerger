import os
import sys
import subprocess
import pyperclip
from tkinter import messagebox, colorchooser

from ... import constants as c
from ..file_manager.file_manager_window import FileManagerWindow
from ..filetypes_manager import FiletypesManagerWindow
from ..settings.settings_window import SettingsWindow
from ..instructions_window import InstructionsWindow
from ..directory_dialog import DirectoryDialog
from ..title_edit_dialog import TitleEditDialog
from ..paste_changes_dialog import PasteChangesDialog
from ..new_profile_dialog import NewProfileDialog
from ..project_starter.wizard_dialog import ProjectStarterDialog
from ...core.clipboard import copy_project_to_clipboard
from ...core import change_applier
from ...core.project_config import _calculate_font_color
from ...core.utils import get_file_hash, get_token_count_for_text

class ActionHandlers:
    def __init__(self, app):
        self.app = app

    def _is_valid_click(self, event):
        """Helper to ensure mouse release happened inside the widget."""
        if event is None: return True
        return 0 <= event.x <= event.widget.winfo_width() and 0 <= event.y <= event.widget.winfo_height()

    def open_project_starter(self, event=None):
        if not self._is_valid_click(event): return

        app = self.app
        if app.project_starter_window and app.project_starter_window.winfo_exists():
            app.project_starter_window.lift()
            app.project_starter_window.focus_force()
            return

        default_parent = app.app_state.config.get('default_parent_folder', '')
        if not default_parent or not os.path.isdir(default_parent):
             # Fallback to user's Desktop directory if not set
             default_parent = os.path.join(os.path.expanduser("~"), "Desktop")

        app.project_starter_window = ProjectStarterDialog(app, app, default_parent)

    def start_work_on_click(self, event):
        """Handles click (copy) and alt-click (delete) on the Start Work button."""
        if not self._is_valid_click(event): return

        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        start_file_path = os.path.join(project_config.base_dir, c.START_WORK_FILENAME)
        if not os.path.exists(start_file_path):
            app.status_var.set(f"File '{c.START_WORK_FILENAME}' not found.")
            app.button_manager.update_button_states()
            return

        is_alt = (event.state & 0x20000) or (event.state & 131072) # Windows/Linux Alt mask

        if is_alt:
            # Delete file
            if messagebox.askyesno("Delete File", f"Delete '{c.START_WORK_FILENAME}' from the project?", parent=app):
                try:
                    os.remove(start_file_path)
                    app.status_var.set(f"Deleted '{c.START_WORK_FILENAME}'.")
                    app.button_manager.update_button_states()
                except OSError as e:
                    app.show_error_dialog("Error", f"Could not delete file: {e}")
        else:
            # Perform Copy with Instructions using _start.txt as intro
            try:
                with open(start_file_path, 'r', encoding='utf-8') as f:
                    start_content = f.read()

                # Temporarily override the config intro/outro
                original_intro = project_config.intro_text

                project_config.intro_text = start_content
                # Keeping existing outro or blank? Usually prompts are self-contained.
                # Let's keep the outro if defined, as it contains formatting rules.

                status_message = copy_project_to_clipboard(
                    parent=app,
                    base_dir=project_config.base_dir,
                    project_config=project_config,
                    use_wrapper=True,
                    copy_merged_prompt="",
                    scan_secrets_enabled=app.app_state.scan_for_secrets
                )

                # Restore
                project_config.intro_text = original_intro
                app.status_var.set(status_message)

            except IOError as e:
                app.show_error_dialog("Error", f"Could not read '{c.START_WORK_FILENAME}': {e}")

    def handle_title_click(self, event=None):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            self.open_change_directory_dialog()
            return

        if app.title_click_job:
            app.after_cancel(app.title_click_job)
            app.title_click_job = None

        app.title_click_job = app.after(250, self.open_change_directory_dialog)

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

    def open_change_directory_dialog(self):
        app = self.app
        app.app_state._prune_recent_projects()
        DirectoryDialog(
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

        # Priority 1: Ctrl + Alt -> Open Console
        if is_ctrl_pressed and is_alt_pressed:
            try:
                if sys.platform == "win32":
                    creationflags = subprocess.CREATE_NEW_CONSOLE
                    subprocess.Popen('cmd.exe', cwd=project_path, creationflags=creationflags)
                    app.status_var.set("Opened console in project folder")
                else:
                    app.status_var.set("Feature only available on Windows.")
            except Exception as e:
                app.show_error_dialog("Error", f"Could not open console: {e}")
            return

        # Priority 2: Ctrl only -> Copy Path
        if is_ctrl_pressed:
            pyperclip.copy(project_path.replace('/', '\\'))
            app.status_var.set("Copied project path to clipboard")
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
            if is_ctrl:
                self.apply_changes_from_clipboard()
            else:
                self.open_paste_changes_dialog()
        else:
            btn._draw(btn.base_color)

    def open_filetypes_manager(self, event=None):
        if not self._is_valid_click(event): return
        app = self.app
        FiletypesManagerWindow(app, on_close_callback=app.ui_callbacks.reload_active_extensions)

    def copy_merged_code(self):
        self._perform_copy(use_wrapper=False)

    def copy_wrapped_code(self):
        self._perform_copy(use_wrapper=True)

    def _perform_copy(self, use_wrapper: bool):
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

        status_message = copy_project_to_clipboard(
            parent=app,
            base_dir=base_dir,
            project_config=project_config,
            use_wrapper=use_wrapper,
            copy_merged_prompt=app.app_state.copy_merged_prompt,
            scan_secrets_enabled=app.app_state.scan_for_secrets
        )
        app.status_var.set(status_message)

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
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        new_files = app.file_monitor.get_newly_detected_files_and_reset()

        if not new_files:
            app.status_var.set("No new files to add.")
            return

        current_selection_paths = {f['path'] for f in project_config.selected_files}
        files_to_add = [path for path in new_files if path not in current_selection_paths]

        if not files_to_add:
            app.status_var.set("New files are already in the merge list.")
            return

        for path in files_to_add:
            new_entry = self._calculate_stats_for_file(path)
            if new_entry:
                project_config.selected_files.append(new_entry)

        project_config.total_tokens = sum(f.get('tokens', 0) for f in project_config.selected_files)
        project_config.save()

        app.status_var.set(f"Added {len(files_to_add)} new file(s) to merge order.")
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
            file_hash = get_file_hash(full_path)

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

    def apply_changes_from_clipboard(self):
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

        status = plan.get('status')
        message = plan.get('message')

        if status == 'ERROR':
            app.show_error_dialog("Parsing Error", message)
            return

        if status == 'CONFIRM_CREATION':
            creations = plan.get('creations', {})
            creation_rel_paths = [os.path.relpath(p, project_config.base_dir).replace('\\', '/') for p in creations.keys()]

            confirm_message = (
                f"This operation will create {len(creations)} new file(s):\n\n"
                f" - " + "\n - ".join(creation_rel_paths) +
                "\n\nDo you want to proceed?"
            )
            dialog_parent = app
            if app.view_manager.current_state == 'compact' and app.view_manager.compact_mode_window and app.view_manager.compact_mode_window.winfo_exists():
                dialog_parent = app.view_manager.compact_mode_window

            if not messagebox.askyesno("Confirm New Files", confirm_message, parent=dialog_parent):
                app.helpers.show_compact_toast("Operation cancelled.")
                return

        updates = plan.get('updates', {})
        creations = plan.get('creations', {})

        success, final_message = change_applier.execute_plan(updates, creations)

        if success:
            app.helpers.show_compact_toast(final_message)
            if creations:
                app.file_monitor.perform_new_file_check()
        else:
            app.show_error_dialog("File Write Error", final_message)