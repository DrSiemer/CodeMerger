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

        # Lazy Layout variables
        self._lazy_timer = None
        self._is_lazy_hiding = False
        self._last_size = (0, 0)

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
        self.bind("<Configure>", self._on_configure)

        # When app regains focus, immediately check if config changed on disk
        self.bind("<FocusIn>", self._on_focus_in)

        # Keyboard shortcuts
        self.bind("<Control-c>", lambda event: self.action_handlers.copy_wrapped_code())
        self.bind("<Control-Shift-C>", lambda event: self.action_handlers.copy_merged_code())
        self.bind("<Control-v>", lambda event: self.action_handlers.open_paste_changes_dialog())
        self.bind("<Control-Shift-V>", lambda event: self.action_handlers.apply_changes_from_clipboard())
        self.bind("<Escape>", lambda event: self.project_actions.cancel_loading())

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
        # If this is a second instance and we aren't opening a specific path from the shell,
        # we ignore the last active project and force the directory selector.
        force_selector = is_second_instance and initial_project_path is None

        if initial_project_path and os.path.isdir(initial_project_path):
            self.app_state.update_active_dir(initial_project_path)
            self.project_actions.set_active_dir_display(initial_project_path)
        elif force_selector:
            # Don't load any project, prepare for selector
            self.project_actions.set_active_dir_display(None, set_status=False)
        else:
            # Standard launch: load the last used project
            self.project_actions.set_active_dir_display(self.app_state.active_directory)

        self.after(1500, self.updater.check_for_updates)

        if newly_added_filetypes:
            self.after(500, lambda: NewFiletypesDialog(self, newly_added_filetypes))

        # If we need to force the selector, schedule it to open after the main window is ready
        if force_selector:
            self.after(100, self.action_handlers.open_project_selector)

        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_configure(self, event):
        """
        Custom handler for <Configure> to implement 'Lazy Layout' resizing.
        Hides UI on drag-resize and restores after a debounce period to avoid lag.
        """
        if event.widget != self:
            return

        # Distinguish between window movement and size change
        new_size = (event.width, event.height)
        if self._last_size == new_size:
            # Only moved, allow normal move-tracking behavior
            self.event_handlers.on_window_configure(event)
            return

        self._last_size = new_size

        # Don't trigger lazy hiding if we are already in compact mode or animating
        if self.view_manager.current_state != 'normal':
            self.event_handlers.on_window_configure(event)
            return

        # Step 1: Hide heavy UI components immediately
        if not self._is_lazy_hiding:
            self._start_lazy_layout()

        # Step 2: Debounce the restore operation
        if self._lazy_timer:
            self.after_cancel(self._lazy_timer)

        self._lazy_timer = self.after(c.LAZY_LAYOUT_DELAY_MS, self._end_lazy_layout)

        # Continue with standard configure checks (like monitor updates)
        self.event_handlers.on_window_configure(event)

    def _start_lazy_layout(self):
        """Immediately hides content areas to stop layout thrashing during resize."""
        self._is_lazy_hiding = True
        self.top_buttons_container.grid_remove()
        self.center_frame.grid_remove()
        self.status_bar.grid_remove()

    def _end_lazy_layout(self):
        """Restores heavy UI components after resizing has stopped."""
        self.top_buttons_container.grid()
        self.center_frame.grid()
        self.status_bar.grid()
        self._is_lazy_hiding = False
        self._lazy_timer = None
        # Force one final layout calculation
        self.update_idletasks()

    def _on_focus_in(self, event):
        """Called when the application window gains focus."""
        # Only act if the main window itself received focus (not a child widget)
        # or if it is a general activation event.
        if event.widget == self and self.project_manager.get_current_project():
            # Trigger an immediate file check without scheduling a new loop
            # This will detect config changes and reload if needed.
            self.file_monitor.perform_new_file_check(schedule_next=False)

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