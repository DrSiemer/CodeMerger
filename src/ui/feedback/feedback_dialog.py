import tkinter as tk
from tkinter import Frame
from ...core.paths import ICON_PATH
from .ui_setup import setup_feedback_ui
from .logic_controller import FeedbackLogicController
from .changes_controller import FeedbackChangesController

class FeedbackDialog(tk.Toplevel):
    """
    Orchestrator for the AI Response Review window.
    Coordinates between UI construction, state management, and file system logic.
    """
    def __init__(self, parent, plan, on_apply=None, on_refuse=None, force_verification=False):
        super().__init__(parent)
        self.parent = parent
        self.plan = plan
        self.on_apply_executor = on_apply
        self.on_refuse = on_refuse
        self.force_verification = force_verification

        # Defensive initialization to prevent AttributeErrors during widget population
        self.info_mgr = None

        # Identify root App instance
        self.app = parent
        while self.app and not hasattr(self.app, 'action_handlers'):
            self.app = getattr(self.app, 'parent', getattr(self.app, 'master', None))

        project = self.app.project_manager.get_current_project()
        self.base_dir = project.base_dir if project else ""
        self.app_state = getattr(parent, 'app_state', getattr(parent.master, 'app_state', None))

        # Shared Logic State
        if 'file_states' not in self.plan:
            self.plan['file_states'] = {}
            self.plan['undo_buffer'] = {}

        self.file_states = self.plan['file_states']
        self.undo_buffer = self.plan['undo_buffer']

        # Window Initialization
        self.withdraw()
        self.title("AI Response Review")
        self.iconbitmap(ICON_PATH)

        # Controllers
        self.logic = FeedbackLogicController(self)
        self.changes = FeedbackChangesController(self)

        # Build UI
        setup_feedback_ui(self)

        # Register Logic Components with Info Mode (if available)
        if self.info_mgr:
            self.logic.register_info(self.info_mgr)
            self.changes.register_info(self.info_mgr)
            self.info_toggle_btn.lift()

        self.logic.finalize_boot()

    def destroy(self):
        """Cleans up instance references and saves state."""
        if hasattr(self.app, 'active_feedback_dialog') and self.app.active_feedback_dialog is self:
            self.app.active_feedback_dialog = None
        self.logic.save_window_state()
        super().destroy()