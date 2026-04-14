import json
import logging
import pyperclip
import time
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
                # Coordination: Confirmation needs to happen on whatever window is active
                active_win = self._window_manager.compact_window if (self._window_manager.compact_window and self._window_manager.compact_window.visible) else self._window_manager.main_window
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

    def request_remote_paste(self, revert_on_close, auto_apply):
        """
        Special cross-window method called by Compact mode.
        Reads clipboard, parses plan, and either applies it or notifies the Main window to show review.
        """
        if not self._window_manager or not self._window_manager.main_window:
            return False

        # OVERWRITE CHECK: Ask user if they want to discard unapplied changes in memory
        status = self.check_for_pending_changes()
        if status.get('has_pending'):
            msg = "An AI response is already in memory with changes that have not been applied yet.\n\nDo you want to overwrite it with the new response from your clipboard?"
            # Use compact window as it currently has focus during this request
            proceed = self._window_manager.compact_window.create_confirmation_dialog("Confirm Overwrite", msg)
            if not proceed:
                return False

        # Access system clipboard using Python to bypass browser permission restrictions
        text = pyperclip.paste()
        if not text or not text.strip():
            return "Clipboard is empty."

        project_config = self.project_manager.get_current_project()
        if not project_config:
            return "No active project."

        plan = change_applier.parse_and_plan_changes(project_config.base_dir, text)
        if plan.get('status') == 'ERROR':
            return False

        # Store for persistence across window handoffs
        self._last_parsed_plan = plan

        # AUTO-APPLY LOGIC (Ctrl-click behavior)
        if auto_apply and plan.get('status') != 'UNFORMATTED':
            creations = plan.get('creations', {})
            updates = plan.get('updates', {})
            deletions = plan.get('deletions_proposed', [])
            skipped = set(plan.get('skipped_files', []))

            # Filter out no-ops to see if there is actually work to do
            actual_updates = {p: c for p, c in updates.items() if p not in skipped}
            actual_deletions = [p for p in deletions if p not in skipped]

            if not actual_updates and not creations and not actual_deletions:
                return "Everything is already up to date."

            threshold = self.app_state.config.get('new_file_alert_threshold', 5)
            dangerous_actions = []
            if len(creations) > threshold: dangerous_actions.append(f"CREATE {len(creations)} file(s)")
            if actual_deletions: dangerous_actions.append(f"DELETE {len(actual_deletions)} file(s)")

            proceed = True
            if dangerous_actions:
                msg = "This operation will perform the following actions:\n\n- " + "\n- ".join(dangerous_actions) + "\n\nDo you want to proceed?"
                proceed = self._window_manager.compact_window.create_confirmation_dialog("Confirm File Actions", msg)

            if proceed:
                success, msg = self.apply_full_plan(plan)
                if success:
                    self._window_manager.main_window.evaluate_js('window.dispatchEvent(new CustomEvent("cm-project-reloaded"))')
                    return msg

        # FALLBACK: Send signal to Main Window for review
        # Restore main window FIRST to ensure the Vue instance is active and ready to receive events.
        self._window_manager.restore_main()

        # Give the OS and Browser a moment to render/focus before sending the event
        time.sleep(0.1)

        js_cmd = f"window.dispatchEvent(new CustomEvent('cm-remote-paste-request', {{ detail: {{ revertOnClose: {'true' if revert_on_close else 'false'} }} }}))"
        try:
            self._window_manager.main_window.evaluate_js(js_cmd)
            return True
        except Exception as e:
            log.error(f"Failed to trigger remote paste signal: {e}")
            return False

    def request_remote_review(self, revert_on_close):
        """
        Special cross-window method called by Compact mode to show the review
        modal in the main window for the response currently in memory.
        """
        if not self._window_manager or not self._window_manager.main_window:
            return False

        if not self._last_parsed_plan:
            return "No response in memory to review."

        self._window_manager.restore_main()

        # Brief delay to allow OS focus transition
        time.sleep(0.1)

        js_cmd = f"window.dispatchEvent(new CustomEvent('cm-remote-review-request', {{ detail: {{ revertOnClose: {'true' if revert_on_close else 'false'} }} }}))"
        try:
            self._window_manager.main_window.evaluate_js(js_cmd)
            return True
        except Exception as e:
            log.error(f"Failed to trigger remote review signal: {e}")
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