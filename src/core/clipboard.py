import pyperclip
import json
from tkinter import messagebox
from .merger import generate_output_string
from .secret_scanner import scan_for_secrets

def copy_project_to_clipboard(parent, base_dir, project_config, use_wrapper, copy_merged_prompt, scan_secrets_enabled):
    """
    Handles the entire process of scanning for secrets, generating the output string,
    and copying it to the clipboard. Returns a status message string.
    """
    try:
        files_to_copy = project_config.selected_files
        if not files_to_copy:
            return "No files selected to copy."

        if scan_secrets_enabled:
            report = scan_for_secrets(base_dir, files_to_copy)
            if report:
                warning_message = (
                    "Warning: Potential secrets were detected in your selection.\n\n"
                    f"{report}\n\n"
                    "Do you still want to copy this content to your clipboard?"
                )
                proceed = messagebox.askyesno("Secrets Detected", warning_message, parent=parent)
                if not proceed:
                    return "Copy cancelled due to potential secrets."

        final_content, status_message = generate_output_string(base_dir, use_wrapper, copy_merged_prompt)

        if final_content is not None:
            pyperclip.copy(final_content)
            return status_message
        else:
            return status_message or "Error: Could not generate content."

    except FileNotFoundError:
        messagebox.showerror("Error", f"No .allcode file found in {base_dir}", parent=parent)
        return "Error: .allcode file not found"
    except (json.JSONDecodeError, IOError) as e:
        messagebox.showerror("Error", f"Could not read .allcode file. Is it empty or corrupt?\n\nDetails: {e}", parent=parent)
        return "Error: Could not read .allcode file"
    except Exception as e:
        messagebox.showerror("Merging Error", f"An error occurred: {e}", parent=parent)
        return f"Error during merging: {e}"