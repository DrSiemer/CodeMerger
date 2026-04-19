import os
import logging
import pyperclip
from src.core.utils import get_token_count_for_text, get_file_hash
from src.core import change_applier
from src.core.highlighter import get_highlighted_diff, get_pygments_css

log = logging.getLogger("CodeMerger")

class ChangesApi:
    """API methods routing Markdown parsing, applying changes, and reviewing diffs."""

    def parse_markdown_response(self, text):
        """Parses the provided Markdown string into a structured change plan."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return {"status": "ERROR", "message": "No active project loaded."}

        plan = change_applier.parse_and_plan_changes(project_config.base_dir, text)

        self._last_parsed_plan = plan
        return plan

    def get_syntax_diff(self, old_text, new_text, filename, full_context=False):
        """Called by Vue to fetch the syntax highlighted diff array."""
        return get_highlighted_diff(old_text, new_text, filename, full_context)

    def get_pygments_style(self):
        """Called by Vue once on mount to inject the CSS."""
        return get_pygments_css()

    def sync_plan_states(self, states):
        """
        Synchronizes the review progress from the frontend to the backend.
        'states' is a dict of { rel_path: 'pending'|'applied'|'rejected'|'deleted'|'skipped' }
        Used to determine if the Paste button should turn orange.
        """
        if self._last_parsed_plan:
            self._last_parsed_plan['file_states'] = states
            return True
        return False

    def get_file_content(self, rel_path):
        """
        Reads and returns the current content of a file.
        Passes content through the sanitization pipeline to ensure the "Old"
        text matches the formatting rules of the "New" text for the diff viewer.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return None

        raw_content = change_applier.get_current_file_content(project_config.base_dir, rel_path)
        if raw_content is None:
            return None

        # Standardizes content for the frontend diff tool to prevent phantom diff artifacts
        return change_applier._sanitize_content(rel_path, raw_content)

    def apply_single_file_change(self, rel_path, content):
        """
        Writes content to disk and synchronizes the project merge list.
        Modified files are automatically added or updated in the selection list.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return False, "No active project."

        success, err = change_applier.apply_single_file(project_config.base_dir, rel_path, content)
        if success:
            sanitized = change_applier._sanitize_content(rel_path, content)
            full_path = os.path.join(project_config.base_dir, rel_path)
            tokens = get_token_count_for_text(sanitized)
            lines = sanitized.count('\n') + 1
            mtime = os.path.getmtime(full_path)
            f_hash = get_file_hash(full_path)

            file_was_in_active_list = False
            for p_name, p_data in project_config.profiles.items():
                found = False
                for f_info in p_data.get('selected_files', []):
                    if f_info['path'] == rel_path:
                        f_info.update({'tokens': tokens, 'lines': lines, 'mtime': mtime, 'hash': f_hash})
                        found = True
                        if p_name == project_config.active_profile_name:
                            file_was_in_active_list = True
                if found:
                    p_data['total_tokens'] = sum(f.get('tokens', 0) for f in p_data['selected_files'])

            if not file_was_in_active_list:
                project_config.selected_files.append({
                    'path': rel_path, 'tokens': tokens, 'lines': lines,
                    'mtime': mtime, 'hash': f_hash
                })
                project_config.update_known_files([rel_path], project_config.active_profile_name)

            if self._last_parsed_plan:
                if 'file_states' not in self._last_parsed_plan:
                    self._last_parsed_plan['file_states'] = {}
                self._last_parsed_plan['file_states'][rel_path] = 'applied'

            project_config.save()
            self._broadcast_reload()
        return success, err

    def delete_file(self, rel_path):
        """Removes file from disk and automatically removes it from all project profiles."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return False, "No active project."

        success, err = change_applier.delete_single_file(project_config.base_dir, rel_path)
        if success:
            if rel_path in project_config.known_files:
                project_config.known_files.remove(rel_path)

            for p_data in project_config.profiles.values():
                p_data['selected_files'] = [f for f in p_data.get('selected_files', []) if f['path'] != rel_path]
                p_data['unknown_files'] = [f for f in p_data.get('unknown_files', []) if f != rel_path]
                p_data['total_tokens'] = sum(f.get('tokens', 0) for f in p_data['selected_files'])

            if self._last_parsed_plan:
                if 'file_states' not in self._last_parsed_plan:
                    self._last_parsed_plan['file_states'] = {}
                self._last_parsed_plan['file_states'][rel_path] = 'deleted'

            project_config.save()
            self._broadcast_reload()
        return success, err

    def claim_last_plan(self):
        """Used by the main window to retrieve a plan prepared by the compact window Browser context."""
        return self._last_parsed_plan

    def clear_parsed_plan(self):
        """Removes the stored plan from session memory."""
        self._last_parsed_plan = None

        # Synchronize UI state across windows by broadcasting a clear event
        if self._window_manager:
            js = 'window.dispatchEvent(new CustomEvent("cm-plan-cleared"))'
            for win in [self._window_manager.main_window, self._window_manager.compact_window]:
                if win:
                    try:
                        win.evaluate_js(js)
                    except Exception:
                        pass

        return True

    def check_for_pending_changes(self):
        """
        Returns a status dictionary indicating if a response is in memory
        and if it contains unapplied changes.
        """
        if not self._last_parsed_plan:
            return {"exists": False, "has_pending": False}

        states = self._last_parsed_plan.get('file_states', {})
        skipped = set(self._last_parsed_plan.get('skipped_files', []))

        has_pending = False

        for p in self._last_parsed_plan.get('updates', {}):
            if p not in skipped and states.get(p, 'pending') == 'pending':
                has_pending = True
                break

        if not has_pending:
            for p in self._last_parsed_plan.get('creations', {}):
                if states.get(p, 'pending') == 'pending':
                    has_pending = True
                    break

        if not has_pending:
            for p in self._last_parsed_plan.get('deletions_proposed', []):
                if p not in skipped and states.get(p, 'pending') == 'pending':
                    has_pending = True
                    break

        return {"exists": True, "has_pending": has_pending}

    def apply_full_plan(self, plan):
        """Executes a bulk update plan and synchronizes metadata for all processed files."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return False, "No active project."

        updates = plan.get('updates', {})
        creations = plan.get('creations', {})
        deletions = plan.get('deletions_proposed', [])
        skipped = set(plan.get('skipped_files', []))

        actual_updates = {p: c for p, c in updates.items() if p not in skipped}
        actual_deletions = [p for p in deletions if p not in skipped]

        success, msg = change_applier.execute_plan(
            project_config.base_dir, actual_updates, creations, actual_deletions
        )

        if success:
            all_changed_paths = set(actual_updates.keys()) | set(creations.keys())

            for rel_path in all_changed_paths:
                full_path = os.path.join(project_config.base_dir, rel_path)
                if not os.path.isfile(full_path): continue
                mtime = os.path.getmtime(full_path)
                f_hash = get_file_hash(full_path)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        raw = f.read()
                    sanitized = change_applier._sanitize_content(rel_path, raw)
                    tokens = get_token_count_for_text(sanitized)
                    lines = sanitized.count('\n') + 1
                except Exception:
                    tokens, lines = 0, 0

                found_in_active = False
                for f_info in project_config.selected_files:
                    if f_info['path'] == rel_path:
                        f_info.update({'tokens': tokens, 'lines': lines, 'mtime': mtime, 'hash': f_hash})
                        found_in_active = True
                        break
                if not found_in_active:
                    project_config.selected_files.append({'path': rel_path, 'tokens': tokens, 'lines': lines, 'mtime': mtime, 'hash': f_hash})

            project_config.update_known_files(list(all_changed_paths), project_config.active_profile_name)

            if actual_deletions:
                for rel_path in actual_deletions:
                    if rel_path in project_config.known_files: project_config.known_files.remove(rel_path)
                    for p_data in project_config.profiles.values():
                        p_data['selected_files'] = [f for f in p_data.get('selected_files', []) if f['path'] != rel_path]
                        p_data['unknown_files'] = [f for f in p_data.get('unknown_files', []) if f != rel_path]

            project_config.total_tokens = sum(f.get('tokens', 0) for f in project_config.selected_files)

            if self._last_parsed_plan:
                states = self._last_parsed_plan.setdefault('file_states', {})
                for p in all_changed_paths: states[p] = 'applied'
                for p in actual_deletions: states[p] = 'deleted'

            project_config.save()
            self._broadcast_reload()
            if skipped: msg = f"Updated {len(all_changed_paths)} file(s). {len(skipped)} file(s) already up to date."

        return success, msg

    def copy_admonishment(self):
        """
        Generates and copies a specialized prompt for corrected AI output.
        If the last plan failed due to a Fast-Apply mismatch, it includes
        the full source code of the affected files.
        """
        plan = self._last_parsed_plan

        # Check if we have a specific Fast-Apply failure
        if plan and plan.get('error_type') == 'FAST_APPLY' and plan.get('failed_paths'):
            failed_paths = plan['failed_paths']
            project_config = self.project_manager.get_current_project()

            blocks = []
            for rel_path in failed_paths:
                content = self.get_file_content(rel_path)
                if content is not None:
                    from src.core.merger import get_language_from_path
                    lang = get_language_from_path(rel_path)
                    blocks.append(f"--- File: `{rel_path}` ---\n```{lang}\n{content}\n```\n--- End of file ---")

            paths_str = ", ".join([f"`{p}`" for p in failed_paths])
            msg = (
                "Surgical Patch Mismatch: The ORIGINAL code blocks provided for the following files do not match my current local source:\n"
                f"{paths_str}\n\n"
                "This error occurred because your baseline reference is out of sync with the current evolved state of the project. "
                "To resolve this, I am providing the *actual* up-to-date source code for the affected files below. "
                "Please use this code as your new baseline and return a CORRECTED surgical diff using ORIGINAL/UPDATED blocks.\n\n"
                "CRITICAL: Do NOT return the full file content. Only provide the corrected surgical blocks.\n\n"
                + "\n\n".join(blocks) + "\n\n"
                "Please ensure your new ORIGINAL blocks are a byte-for-byte match to the code provided above."
            )
            try:
                pyperclip.copy(msg)
                return f"Copied surgical correction prompt for {len(failed_paths)} file(s)."
            except Exception:
                return "Failed to copy prompt."

        # Standard Format Admonishment
        LT, RT, PRE = "<", ">", "--- "
        IN_T, ANS_W = "INTRO", "ANSWERS TO DIRECT USER QUESTIONS"
        CHA_N, VER_I, UNC_H = "CHANGES", "VERIFICATION", "UNCHANGED"

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
        try:
            pyperclip.copy(msg)
            return "Copied format correction prompt."
        except Exception:
            return "Failed to copy prompt."

    def copy_order_admonishment(self, error_msg):
        """Generates and copies a specialized prompt to correct a failed file order request."""
        msg = (
            "The file list you provided for the merge order is invalid. "
            "Please provide only the JSON array of strings in the exact same format as requested. "
            "Ensure you do not omit any files from the current selection and do not add files that were not requested.\n\n"
            f"Validation Errors:\n{error_msg}"
        )
        try:
            pyperclip.copy(msg)
            return "Copied order correction prompt."
        except Exception:
            return "Failed to copy prompt."