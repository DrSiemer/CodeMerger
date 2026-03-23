import os
import json
import shutil
import tempfile
import logging
import re
import time
from tkinter import Tk, StringVar, Label

from ..app_state import AppState
from .view_manager import ViewManager
from ..core.paths import ICON_PATH, UPDATE_CLEANUP_FILE_PATH
from .. import constants as c
from ..core.updater import Updater
from .ui_builder import setup_ui
from .file_monitor import FileMonitor
from ..core.project_manager import ProjectManager
from .assets import assets
from .app_window_parts.button_state_manager import ButtonStateManager
from .app_window_parts.status_bar_manager import StatusBarManager
from .new_filetypes_dialog import NewFiletypesDialog
from .app_window_parts.action_handlers import ActionHandlers
from .app_window_parts.event_handlers import EventHandlers
from .app_window_parts.project_actions import ProjectActions
from .app_window_parts.profile_actions import ProfileActions
from .app_window_parts.ui_callbacks import UICallbacks
from .app_window_parts.helpers import AppHelpers
from .info_manager import attach_info_mode

log = logging.getLogger("CodeMerger")

class App(Tk):
    def __init__(self, file_extensions, app_version="", initial_project_path=None, newly_added_filetypes=None, is_second_instance=False):
        super().__init__()
        self.withdraw()
        self._run_update_cleanup()
        assets.load_tk_images()
        self.assets = assets

        self.file_extensions = file_extensions
        self.app_version = app_version
        self.app_bg_color = c.DARK_BG
        self.project_color = c.COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.window_geometries = {}
        self.title_click_job = None
        self.current_monitor_handle = None
        self.masked_logo_tk = None
        self.load_thread = None
        self.load_thread_result = None
        self.loading_animation_job = None
        self.project_starter_window = None
        self.last_ai_response = None

        self.last_move_time = 0.0
        self._lazy_timer = None
        self._is_lazy_hiding = False
        self._last_size = (0, 0)

        # Order of initialization is critical for established logic components
        self.app_state = AppState()
        self.view_manager = ViewManager(self)
        self.updater = Updater(self, self.app_state, self.app_version)
        self.project_manager = ProjectManager(lambda: self.file_extensions)
        self.file_monitor = FileMonitor(self)
        self.button_manager = ButtonStateManager(self)

        self.action_handlers = ActionHandlers(self)
        self.event_handlers = EventHandlers(self)
        self.project_actions = ProjectActions(self)
        self.profile_actions = ProfileActions(self)
        self.ui_callbacks = UICallbacks(self)
        self.helpers = AppHelpers(self)

        self.title(f"CodeMerger [ {app_version} ]")
        self.iconbitmap(ICON_PATH)

        initial_geom = c.DEFAULT_WINDOW_GEOMETRY
        if self.app_state.info_mode_active:
            match = re.match(r"(\d+)x(\d+)", initial_geom)
            if match:
                w, h = map(int, match.groups())
                initial_geom = f"{w}x{h + c.INFO_PANEL_HEIGHT}"

        self.geometry(initial_geom)
        self.minsize(c.MIN_WINDOW_WIDTH, c.MIN_WINDOW_HEIGHT)
        self.configure(bg=self.app_bg_color)

        self.active_dir = StringVar()
        self.project_title_var = StringVar()
        self.status_var = StringVar(value="")

        setup_ui(self)
        self.status_bar_manager = StatusBarManager(self, self.status_bar, self.status_var)
        self.info_mgr = attach_info_mode(self, self.app_state, manager_type='grid', grid_row=4, toggle_btn=self.info_toggle_btn)
        self._register_hover_help()

        self.active_dir.trace_add('write', self.button_manager.update_button_states)
        self.bind("<Configure>", self.event_handlers.update_responsive_layout, add='+')
        self.after(50, self.event_handlers.update_responsive_layout)
        self.protocol("WM_DELETE_WINDOW", self.event_handlers.on_app_close)
        self.bind("<Map>", self.view_manager.on_main_window_restored)
        self.bind("<Unmap>", self.view_manager.on_main_window_minimized)
        self.bind("<Configure>", self._on_configure)
        self.bind("<FocusIn>", self._on_focus_in)

        # Shortcuts
        self.bind("<Control-c>", lambda event: self.action_handlers.copy_wrapped_code())
        self.bind("<Control-Shift-C>", lambda event: self.action_handlers.copy_merged_code())
        self.bind("<Control-v>", lambda event: self.action_handlers.open_paste_changes_dialog())
        self.bind("<Control-Shift-V>", lambda event: self.action_handlers.apply_changes_from_clipboard())
        self.bind("<Escape>", lambda event: self.project_actions.cancel_loading())

        force_selector = is_second_instance and initial_project_path is None

        if initial_project_path and os.path.isdir(initial_project_path):
            self.app_state.update_active_dir(initial_project_path)
            self.project_actions.set_active_dir_display(initial_project_path)
        elif force_selector:
            self.project_actions.set_active_dir_display(None, set_status=False)
        else:
            self.project_actions.set_active_dir_display(self.app_state.active_directory)

        self.after(1500, self.updater.check_for_updates)
        if newly_added_filetypes:
            self.after(500, lambda: NewFiletypesDialog(self, newly_added_filetypes))
        if force_selector:
            self.after(100, self.action_handlers.open_project_selector)

        self.after(100, self.event_handlers.check_for_monitor_change)

        self.deiconify()
        self.lift()
        self.focus_force()

    def _register_hover_help(self):
        """Attaches help panel triggers to main window widgets"""
        mgr = self.info_mgr
        mgr.register(self.select_project_button, "select_project")

        mgr.register(self.title_container, "project_name")
        mgr.register(self.title_label, "project_name")

        mgr.register(self.color_swatch, "color_swatch")
        mgr.register(self.folder_icon_label, "folder_icon")
        mgr.register(self.manage_files_button, "manage_files")
        mgr.register(self.wrapper_text_button, "instructions")
        mgr.register(self.copy_merged_button, "copy_code")
        mgr.register(self.copy_wrapped_button, "copy_with_instructions")
        mgr.register(self.paste_changes_button, "paste_changes")
        mgr.register(self.review_button, "response_review")
        mgr.register(self.cleanup_comments_button, "cleanup")
        mgr.register(self.settings_button, "settings")
        mgr.register(self.filetypes_button, "filetypes")
        mgr.register(self.project_starter_button, "starter")

        mgr.register(self.profile_navigator, "profile_nav")
        mgr.register(self.add_profile_button, "profile_add")
        mgr.register(self.delete_profile_button, "profile_delete")

        mgr.register(self.info_toggle_btn, "info_toggle")

    def _on_configure(self, event):
        """
        Implements 'Lazy Layout' resizing to prevent lag during drag operations
        Tracking movement time assists with Compact Mode positioning
        """
        if event.widget != self:
            return

        new_size = (event.width, event.height)
        if self._last_size == new_size:
            # Captures manual moves when in normal state to avoid polluting restoration targets
            if self.view_manager.current_state == self.view_manager.STATE_NORMAL:
                self.last_move_time = time.time()

            self.event_handlers.on_window_configure(event)
            return

        self._last_size = new_size

        if self.view_manager.current_state != 'normal':
            self.event_handlers.on_window_configure(event)
            return

        # Hide heavy UI components immediately to stop layout thrashing
        if not self._is_lazy_hiding:
            self._start_lazy_layout()

        if self._lazy_timer:
            self.after_cancel(self._lazy_timer)

        self._lazy_timer = self.after(c.LAZY_LAYOUT_DELAY_MS, self._end_lazy_layout)

        self.event_handlers.on_window_configure(event)

    def _start_lazy_layout(self):
        self._is_lazy_hiding = True
        self.top_buttons_container.grid_remove()
        self.center_frame.grid_remove()
        self.status_container.grid_remove()

    def _end_lazy_layout(self):
        self.top_buttons_container.grid()
        self.center_frame.grid()
        self.status_container.grid()
        self._is_lazy_hiding = False
        self._lazy_timer = None
        self.update_idletasks()

    def _on_focus_in(self, event):
        # Triggers immediate file check on application focus to identify external configuration changes
        if event.widget == self and self.project_manager.get_current_project():
            self.file_monitor.perform_new_file_check(schedule_next=False)

    def _run_update_cleanup(self):
        """Safely purges temporary installation files created by the updater"""
        if not os.path.exists(UPDATE_CLEANUP_FILE_PATH):
            return

        log.info("Update cleanup file found. Proceeding with cleanup.")
        try:
            with open(UPDATE_CLEANUP_FILE_PATH, 'r', encoding='utf-8') as f:
                cleanup_data = json.load(f)

            dir_to_delete = cleanup_data.get('temp_dir_to_delete')
            if not dir_to_delete:
                log.warning("Cleanup file exists but contains no directory to delete.")
                return

            system_temp_dir = os.path.realpath(tempfile.gettempdir())
            path_to_delete = os.path.realpath(dir_to_delete)

            if not path_to_delete.startswith(system_temp_dir):
                log.error(f"SECURITY: Update cleanup aborted. Path '{path_to_delete}' is not in temp dir '{system_temp_dir}'.")
                return

            if os.path.isdir(path_to_delete):
                shutil.rmtree(path_to_delete, ignore_errors=True)
                log.info(f"Update Cleanup: Successfully removed temporary directory '{path_to_delete}'.")

        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Update Cleanup Error: Could not read or parse cleanup file. Error: {e}")
        finally:
            try:
                os.remove(UPDATE_CLEANUP_FILE_PATH)
            except OSError as e:
                log.error(f"Failed to remove cleanup file: {e}")

    def show_and_raise(self):
        self.helpers.show_and_raise()

    def show_error_dialog(self, title, message):
        self.helpers.show_error_dialog(title, message)