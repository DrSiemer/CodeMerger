import os
import json
import shutil
import tempfile
import logging
from tkinter import Tk, StringVar

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

log = logging.getLogger("CodeMerger")

class App(Tk):
    def __init__(self, file_extensions, app_version="", initial_project_path=None, newly_added_filetypes=None):
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

        # Core Components
        self.app_state = AppState()
        self.view_manager = ViewManager(self)
        self.updater = Updater(self, self.app_state, self.app_version)
        self.project_manager = ProjectManager(lambda: self.file_extensions)
        self.file_monitor = FileMonitor(self)
        self.button_manager = ButtonStateManager(self)

        # Refactored Logic Handlers
        self.action_handlers = ActionHandlers(self)
        self.event_handlers = EventHandlers(self)
        self.project_actions = ProjectActions(self)
        self.profile_actions = ProfileActions(self)
        self.ui_callbacks = UICallbacks(self)
        self.helpers = AppHelpers(self)

        # Window Setup
        self.title(f"CodeMerger [ {app_version} ]")
        self.iconbitmap(ICON_PATH)
        self.geometry(c.DEFAULT_WINDOW_GEOMETRY)
        self.minsize(c.MIN_WINDOW_WIDTH, c.MIN_WINDOW_HEIGHT)
        self.configure(bg=self.app_bg_color)

        # Bindings
        self.protocol("WM_DELETE_WINDOW", self.event_handlers.on_app_close)
        self.bind("<Map>", self.view_manager.on_main_window_restored)
        self.bind("<Unmap>", self.view_manager.on_main_window_minimized)
        self.bind("<Configure>", self.event_handlers.on_window_configure)

        # Keyboard shortcuts
        self.bind("<Control-c>", lambda event: self.action_handlers.copy_wrapped_code())
        self.bind("<Control-Shift-C>", lambda event: self.action_handlers.copy_merged_code())
        self.bind("<Control-v>", lambda event: self.action_handlers.open_paste_changes_dialog())
        self.bind("<Control-Shift-V>", lambda event: self.action_handlers.apply_changes_from_clipboard())

        # Initialize StringVar members before UI build
        self.active_dir = StringVar()
        self.project_title_var = StringVar()
        self.status_var = StringVar(value="")
        self.active_dir.trace_add('write', self.button_manager.update_button_states)

        setup_ui(self)
        self.bind("<Configure>", self.event_handlers.update_responsive_layout, add='+')
        self.after(50, self.event_handlers.update_responsive_layout)

        self.status_bar_manager = StatusBarManager(self, self.status_bar, self.status_var)

        # Project Loading Logic
        if initial_project_path and os.path.isdir(initial_project_path):
            self.app_state.update_active_dir(initial_project_path)
            self.project_actions.set_active_dir_display(initial_project_path)
        else:
            self.project_actions.set_active_dir_display(self.app_state.active_directory)

        self.after(1500, self.updater.check_for_updates)

        if newly_added_filetypes:
            self.after(500, lambda: NewFiletypesDialog(self, newly_added_filetypes))

        self.deiconify()
        self.lift()
        self.focus_force()

    def _run_update_cleanup(self):
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

    # For convenience, keep these direct calls
    def show_and_raise(self):
        self.helpers.show_and_raise()

    def show_error_dialog(self, title, message):
        self.helpers.show_error_dialog(title, message)