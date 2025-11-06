import json
import pyperclip
from tkinter import messagebox
from ...core.merger import generate_output_string
from ..multiline_input_dialog import MultilineInputDialog

class OrderRequestHandler:
    """Handles the logic for creating and applying file order requests."""
    def __init__(self, fm_window):
        self.window = fm_window
        self.order_request_click_job = None

    def handle_click(self, event=None):
        """Manages single and double clicks for the order request button."""
        if self.order_request_click_job:
            self.window.after_cancel(self.order_request_click_job)
            self.order_request_click_job = None
            self._apply_reorder()
        else:
            self.order_request_click_job = self.window.after(300, self._copy_request)

    def _copy_request(self):
        """Copies a formatted order request with full file content to the clipboard."""
        self.order_request_click_job = None
        ordered_files_info = self.window.selection_handler.ordered_selection
        if not ordered_files_info:
            self.window.status_var.set("No files in merge order to create a request for.")
            return

        temp_project_config = self.window.project_config
        temp_project_config.selected_files = ordered_files_info
        merged_code, _ = generate_output_string(
            base_dir=self.window.base_dir,
            project_config=temp_project_config,
            use_wrapper=False,
            copy_merged_prompt=""
        )
        if not merged_code:
            self.window.status_var.set("Failed to generate merged code for the request.")
            return

        paths = [f['path'] for f in ordered_files_info]
        prepend_text = "Please provide me with the optimal order in which to present these files to a language model. Only return the file list in the exact same format I will use here:\n\n"
        json_payload = json.dumps(paths, indent=2)
        content_intro = "Here's the content of the files, to help you determine the best order:"

        final_string = f"{prepend_text}{json_payload}\n\n{content_intro}\n\n{merged_code}"
        pyperclip.copy(final_string)
        self.window.status_var.set("Order request with file content copied to clipboard.")

    def _apply_reorder(self):
        """Opens a dialog to paste a new file order and updates the list."""
        current_selection = self.window.selection_handler.ordered_selection
        if not current_selection:
            self.window.status_var.set("Merge order is empty, nothing to reorder.")
            return

        dialog = MultilineInputDialog(
            parent=self.window,
            title="Update Merge Order",
            prompt="Paste the language model response containing the new file order."
        )
        pasted_text = dialog.result
        if not pasted_text:
            return

        try:
            start_index = pasted_text.find('[')
            end_index = pasted_text.rfind(']') + 1
            if start_index == -1 or end_index == 0:
                raise ValueError("Could not find a JSON array (starting with '[' and ending with ']').")
            json_str = pasted_text[start_index:end_index]
            new_order_list = json.loads(json_str)
            if not isinstance(new_order_list, list):
                raise ValueError("The parsed JSON is not a list.")
        except (ValueError, json.JSONDecodeError) as e:
            self.window.show_error_dialog("Parsing Error", f"Could not parse the new file order.\n\nError: {e}")
            return

        current_paths_set = {f['path'] for f in current_selection}
        new_paths_set = set(new_order_list)
        missing_files = current_paths_set - new_paths_set
        unknown_files = new_paths_set - current_paths_set

        if missing_files or unknown_files:
            error_message = "The provided file list is invalid.\n"
            if missing_files: error_message += f"\nMissing files:\n- " + "\n- ".join(sorted(list(missing_files)))
            if unknown_files: error_message += f"\nUnknown files:\n- " + "\n- ".join(sorted(list(unknown_files)))
            self.window.show_error_dialog("Validation Error", error_message)
            return

        path_map = {f['path']: f for f in current_selection}
        new_ordered_selection = [path_map[p] for p in new_order_list]
        self.window.selection_handler.data_manager.ordered_selection = new_ordered_selection
        self.window.selection_handler.ui_manager.update_list_display(new_ordered_selection, is_reorder=True)
        self.window.selection_handler.on_change()
        self.window.status_var.set("File merge order updated successfully.")