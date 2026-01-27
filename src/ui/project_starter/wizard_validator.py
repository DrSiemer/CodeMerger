from pathlib import Path

def validate_step(step, state_data):
    """
    Validates the data for a specific wizard step.

    Args:
        step (int): The step number to validate.
        state_data (dict): The project_data dictionary from WizardState.

    Returns:
        tuple: (is_valid, error_title, error_message)
    """
    if step == 1:
        project_name = state_data["name"].get()

        if not project_name:
            return False, "Error", "Project Name is required."

    elif step == 2:
        return True, "", ""

    elif step == 3:
        # Strict Check: If segments exist, ALL must be signed off
        segments = state_data.get("concept_segments", {})
        if segments:
            signoffs = state_data.get("concept_signoffs", {})
            # Check if every key in segments has a True value in signoffs
            if not all(signoffs.get(k) for k in segments.keys()):
                return False, "Incomplete", "Please review and sign off on all concept segments."
        else:
            # Fallback: Just check if content exists (legacy or manual paste)
            concept = state_data.get("concept_md", "")
            if not concept:
                return False, "Error", "The concept document cannot be empty."

    elif step == 4:
        # The Stack step is optional.
        return True, "", ""

    elif step == 5:
        # Strict Check: If segments exist, ALL must be signed off
        segments = state_data.get("todo_segments", {})
        if segments:
            signoffs = state_data.get("todo_signoffs", {})
            if not all(signoffs.get(k) for k in segments.keys()):
                return False, "Incomplete", "Please review and sign off on all TODO phases."
        else:
            todo = state_data.get("todo_md", "")
            if not todo:
                return False, "Error", "The TODO plan cannot be empty."

    elif step == 6:
        # Validate parent folder here, right before generation
        parent_folder = state_data["parent_folder"].get()
        if not parent_folder:
             return False, "Error", "Parent Folder is required."

        try:
            path_obj = Path(parent_folder)
            if not path_obj.exists():
                return False, "Invalid Path", f"The parent folder does not exist:\n{parent_folder}"
            if not path_obj.is_dir():
                return False, "Invalid Path", f"The path is not a directory:\n{parent_folder}"
        except Exception as e:
            return False, "Invalid Path", f"The parent folder path is invalid.\nError: {e}"

    return True, "", ""