import json
import logging
import pyperclip
import time
from src.core.secret_scanner import scan_for_secrets
from src.core.merger import generate_output_string
from src.core import change_applier

log = logging.getLogger("CodeMerger")

class ClipboardApi:
    """API methods for accessing the clipboard and copying finalized prompts"""

    def copy_code(self, use_wrapper, allow_secrets=None):
        """
        Merges selected files and copies the result to the clipboard.
        allow_secrets:
          None  -> Use default blocking dialog (Main window)
          True  -> Copy anyway (Widget confirmation)
          False -> Check and return error if found (Widget initial check)
        """
        project_config = self.project_manager.get_current_project()
        if not project_config or not project_config.selected_files:
            return "No files selected to copy"

        base_dir = self.app_state.active_directory
        files_to_copy = [f['path'] for f in project_config.selected_files]

        if self.app_state.scan_for_secrets:
            report = scan_for_secrets(base_dir, files_to_copy)
            if report:
                # Flow A: Widget non-blocking check
                if allow_secrets is False:
                    return {"status": "SECRETS_DETECTED", "report": report}

                # Flow B: Widget confirmed bypass
                if allow_secrets is True:
                    pass # Continue to copy

                # Flow C: Standard Main Window blocking behavior
                else:
                    warning_message = f"Warning: Potential secrets were detected in your selection.\n\n{report}\n\nDo you still want to copy this content to your clipboard?"
                    proceed = self._show_managed_confirmation("Secrets Detected", warning_message)
                    if not proceed:
                        return "Copy cancelled due to potential secrets."

        final_content, status_message = generate_output_string(
            base_dir,
            project_config,
            use_wrapper,
            self.app_state.copy_merged_prompt,
            enable_fast_apply=self.app_state.enable_fast_apply
        )

        if final_content is not None:
            pyperclip.copy(final_content)
            return status_message

        return status_message or "Error: Could not generate content."

    def request_remote_paste(self, revert_on_close, auto_apply, force_overwrite=False):
        """
        Cross-window method called by Compact mode
        Reads clipboard and either auto-applies or signals Main window for review
        """
        if not self._window_manager or not self._window_manager.main_window:
            return False

        status = self.check_for_pending_changes()
        if status.get('has_pending') and not force_overwrite:
            # Main window still uses blocking confirmation
            # Compact mode checks has_pending locally before calling this with force_overwrite=True
            if not force_overwrite:
                msg = "An AI response is already in memory with changes that have not been applied yet.\n\nDo you want to overwrite it with the new response from your clipboard?"
                proceed = self._show_managed_confirmation("Confirm Overwrite", msg)
                if not proceed:
                    return False

        text = pyperclip.paste()
        if not text or not text.strip():
            return "Clipboard is empty."

        project_config = self.project_manager.get_current_project()
        if not project_config:
            return "No active project."

        plan = change_applier.parse_and_plan_changes(project_config.base_dir, text)
        self._last_parsed_plan = plan

        if plan.get('status') == 'ERROR':
            self._window_manager.restore_main()
            time.sleep(0.1)

            msg_json = json.dumps(plan.get('message', 'Format Error'))
            js_cmd = f"window.dispatchEvent(new CustomEvent('cm-remote-paste-error', {{ detail: {{ message: {msg_json}, revertOnClose: {'true' if revert_on_close else 'false'} }} }}))"
            try:
                self._window_manager.main_window.evaluate_js(js_cmd)
            except Exception as e:
                log.error(f"Failed to trigger remote paste error signal: {e}")
            return False

        if auto_apply and plan.get('status') != 'UNFORMATTED':
            creations = plan.get('creations', {})
            updates = plan.get('updates', {})
            deletions = plan.get('deletions_proposed', [])
            skipped = set(plan.get('skipped_files', []))

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
                proceed = self._show_managed_confirmation("Confirm File Actions", msg)

            if proceed:
                success, msg = self.apply_full_plan(plan)
                if success:
                    self._window_manager.main_window.evaluate_js('window.dispatchEvent(new CustomEvent("cm-project-reloaded"))')
                    self._broadcast_reload()

                    # Fix: Archive verification for auto-applied plan even if Main window is minimized
                    v_text = plan.get('verification', '')
                    if v_text and v_text != '-':
                        v_json = json.dumps(v_text)
                        self._window_manager.main_window.evaluate_js(f"window.dispatchEvent(new CustomEvent('cm-archive-verification', {{ detail: {{ content: {v_json} }} }}))")

                    return msg

        self._window_manager.restore_main()
        time.sleep(0.1)

        js_cmd = f"window.dispatchEvent(new CustomEvent('cm-remote-paste-request', {{ detail: {{ revertOnClose: {'true' if revert_on_close else 'false'} }} }}))"
        try:
            self._window_manager.main_window.evaluate_js(js_cmd)
            return True
        except Exception as e:
            log.error(f"Failed to trigger remote paste signal: {e}")
            return False

    def request_remote_review(self, revert_on_close):
        """Opens the review modal in the main window for the plan in memory"""
        if not self._window_manager or not self._window_manager.main_window:
            return False

        if not self._last_parsed_plan:
            return "No response in memory to review."

        self._window_manager.restore_main()
        time.sleep(0.1)

        js_cmd = f"window.dispatchEvent(new CustomEvent('cm-remote-review-request', {{ detail: {{ revertOnClose: {'true' if revert_on_close else 'false'} }} }}))"
        try:
            self._window_manager.main_window.evaluate_js(js_cmd)
            return True
        except Exception as e:
            log.error(f"Failed to trigger remote review signal: {e}")
            return False

    def get_clipboard_text(self):
        """Accesses system clipboard via Python to bypass browser permission prompts"""
        try:
            return pyperclip.paste()
        except Exception as e:
            log.error(f"Failed to read system clipboard: {e}")
            return ""

    def copy_text(self, text):
        """Copies arbitrary text to the system clipboard via Python."""
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            log.error(f"Failed to copy text to clipboard: {e}")
            return False