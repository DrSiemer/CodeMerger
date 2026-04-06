import json
import logging
import pyperclip
from src.core.secret_scanner import scan_for_secrets
from src.core.merger import generate_output_string
from src.core import change_applier

log = logging.getLogger("CodeMerger")

class ClipboardApi:
    """API methods for accessing the clipboard and copying finalized prompts."""

    def copy_code(self, use_wrapper):
        """
        Merges the selected files and copies the result to the clipboard.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config or not project_config.selected_files:
            return "No files selected to copy."

        base_dir = self.app_state.active_directory
        files_to_copy = [f['path'] for f in project_config.selected_files]

        if self.app_state.scan_for_secrets:
            report = scan_for_secrets(base_dir, files_to_copy)
            if report:
                warning_message = f"Warning: Potential secrets were detected in your selection.\n\n{report}\n\nDo you still want to copy this content to your clipboard?"
                # Confirmation needs to happen on whatever window is active
                active_win = self._window_manager.compact_window if self._window_manager.compact_window.visible else self._window_manager.main_window
                proceed = active_win.create_confirmation_dialog("Secrets Detected", warning_message)
                if not proceed:
                    return "Copy cancelled due to potential secrets."

        final_content, status_message = generate_output_string(
            base_dir,
            project_config,
            use_wrapper,
            self.app_state.copy_merged_prompt
        )

        if final_content is not None:
            pyperclip.copy(final_content)
            return status_message

        return status_message or "Error: Could not generate content."

    def request_remote_paste(self, revert_on_close):
        """
        Special cross-window method called by Compact mode.
        Reads clipboard, parses plan, and notifies the Main window to show review.
        """
        if not self._window_manager or not self._window_manager.main_window:
            return False

        text = pyperclip.paste()
        if not text or not text.strip():
            return False

        project_config = self.project_manager.get_current_project()
        if not project_config:
            return False

        plan = change_applier.parse_and_plan_changes(project_config.base_dir, text)
        if plan.get('status') == 'ERROR':
            # We don't alert here to avoid focus stealing artifacts on Compact Mode
            return False

        # Prepare payload for Main Window
        payload = {
            'plan': plan,
            'revertOnClose': revert_on_close
        }
        json_payload = json.dumps(payload)

        # Inject command into main window's memory
        js_cmd = f"window.dispatchEvent(new CustomEvent('cm-remote-paste', {{ detail: {json_payload} }}))"
        try:
            self._window_manager.main_window.evaluate_js(js_cmd)
            self._window_manager.restore_main()
            return True
        except Exception as e:
            log.error(f"Failed to trigger remote paste: {e}")
            return False

    def get_clipboard_text(self):
        """
        Reads text from the system clipboard using the Python pyperclip library.
        Bypasses browser permission gated navigator.clipboard.readText() API.
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            log.error(f"Failed to read system clipboard: {e}")
            return ""