import os
import logging
from src.core.utils import get_token_count_for_text, get_file_hash
from src.core import change_applier

log = logging.getLogger("CodeMerger")

class ChangesApi:
    """API methods routing Markdown parsing, applying changes, and reviewing diffs."""

    def parse_markdown_response(self, text):
        """Parses the provided Markdown string into a structured change plan."""
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return {"status": "ERROR", "message": "No active project loaded."}

        plan = change_applier.parse_and_plan_changes(project_config.base_dir, text)
        return plan

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

        # Standardize for the frontend diff tool
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
            # Synchronize configuration metadata
            # Using the SANITIZED version for token counting consistency
            sanitized = change_applier._sanitize_content(rel_path, content)
            full_path = os.path.join(project_config.base_dir, rel_path)
            tokens = get_token_count_for_text(sanitized)
            lines = sanitized.count('\n') + 1
            mtime = os.path.getmtime(full_path)
            f_hash = get_file_hash(full_path)

            file_was_in_active_list = False
            # Update stats in all profiles to maintain cache consistency
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

            # Ensure file is part of the merge list (matching the Tkinter tool behavior)
            if not file_was_in_active_list:
                project_config.selected_files.append({
                    'path': rel_path, 'tokens': tokens, 'lines': lines,
                    'mtime': mtime, 'hash': f_hash
                })
                # Mark as known globally to prevent "New File" alerts
                if rel_path not in project_config.known_files:
                    project_config.known_files.append(rel_path)
                    project_config.known_files.sort()

            project_config.save()

        return success, err

    def delete_file(self, rel_path):
        """
        Removes file from disk and automatically removes it from all project profiles.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return False, "No active project."

        success, err = change_applier.delete_single_file(project_config.base_dir, rel_path)
        if success:
            # Prune from global known files
            if rel_path in project_config.known_files:
                project_config.known_files.remove(rel_path)

            # Remove from all profile-specific selection lists
            for p_data in project_config.profiles.values():
                p_data['selected_files'] = [f for f in p_data.get('selected_files', []) if f['path'] != rel_path]
                p_data['unknown_files'] = [f for f in p_data.get('unknown_files', []) if f != rel_path]
                # Re-calculate total tokens for each profile
                p_data['total_tokens'] = sum(f.get('tokens', 0) for f in p_data['selected_files'])

            project_config.save()

        return success, err

    def claim_last_plan(self):
        """Used by the main window to retrieve a plan prepared by the compact window."""
        plan = self._last_parsed_plan
        self._last_parsed_plan = None
        return plan

    def apply_full_plan(self, plan):
        """
        Executes a bulk update plan and synchronizes metadata for all processed files.
        Used for 'Auto-Apply' (Ctrl-click) workflows.
        """
        project_config = self.project_manager.get_current_project()
        if not project_config:
            return False, "No active project."

        updates = plan.get('updates', {})
        creations = plan.get('creations', {})
        deletions = plan.get('deletions_proposed', [])
        skipped = set(plan.get('skipped_files', []))

        # Filter plans based on skipped status
        actual_updates = {p: c for p, c in updates.items() if p not in skipped}
        actual_deletions = [p for p in deletions if p not in skipped]

        success, msg = change_applier.execute_plan(
            project_config.base_dir, actual_updates, creations, actual_deletions
        )

        if success:
            # Process Metadata Sync for all created or updated files
            all_changed_paths = set(actual_updates.keys()) | set(creations.keys())

            for rel_path in all_changed_paths:
                full_path = os.path.join(project_config.base_dir, rel_path)
                if not os.path.isfile(full_path):
                    continue

                mtime = os.path.getmtime(full_path)
                f_hash = get_file_hash(full_path)

                # Get content to calculate tokens/lines
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        raw = f.read()
                    sanitized = change_applier._sanitize_content(rel_path, raw)
                    tokens = get_token_count_for_text(sanitized)
                    lines = sanitized.count('\n') + 1
                except Exception:
                    tokens, lines = 0, 0

                # Ensure file is marked as known globally
                if rel_path not in project_config.known_files:
                    project_config.known_files.append(rel_path)

                # Update selected_files and total_tokens for the active profile
                found_in_active = False
                for f_info in project_config.selected_files:
                    if f_info['path'] == rel_path:
                        f_info.update({'tokens': tokens, 'lines': lines, 'mtime': mtime, 'hash': f_hash})
                        found_in_active = True
                        break

                if not found_in_active:
                    project_config.selected_files.append({
                        'path': rel_path, 'tokens': tokens, 'lines': lines,
                        'mtime': mtime, 'hash': f_hash
                    })

            # Cleanup globally after processing all additions
            project_config.known_files.sort()

            # Handle global cleanup for deleted files
            if actual_deletions:
                for rel_path in actual_deletions:
                    if rel_path in project_config.known_files:
                        project_config.known_files.remove(rel_path)

                    # Remove from all profiles
                    for p_data in project_config.profiles.values():
                        p_data['selected_files'] = [f for f in p_data.get('selected_files', []) if f['path'] != rel_path]
                        p_data['unknown_files'] = [f for f in p_data.get('unknown_files', []) if f != rel_path]

            # Recalculate total tokens for active profile
            project_config.total_tokens = sum(f.get('tokens', 0) for f in project_config.selected_files)

            project_config.save()

            if skipped:
                msg = f"Updated {len(all_changed_paths)} file(s). {len(skipped)} file(s) already up to date."

        return success, msg

    def get_admonishment_prompt(self):
        """Generates a specialized prompt for corrected AI output format."""
        LT, RT, PRE = "<", ">", "--- "
        IN_T = "IN" + "TRO"
        ANS_W = "ANS" + "WERS" + " TO DIR" + "ECT USER QUE" + "STIONS"
        CHA_N = "CHA" + "NGES"
        VER_I = "VER" + "IFI" + "CATION"
        UNC_H = "UNC" + "HANGED"

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
        return msg