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
        parent_folder = state_data["parent_folder"].get()

        if not all([project_name, parent_folder]):
            return False, "Error", "Project Name and Parent Folder are required."

        try:
            path_obj = Path(parent_folder)
            if not path_obj.exists():
                return False, "Invalid Path", f"The parent folder does not exist:\n{parent_folder}"
            if not path_obj.is_dir():
                return False, "Invalid Path", f"The path is not a directory:\n{parent_folder}"
        except Exception as e:
            return False, "Invalid Path", f"The parent folder path is invalid.\nError: {e}"

    elif step == 2:
        return True, "", ""

    elif step == 3:
        concept = state_data["concept_md"]
        if not concept:
            return False, "Error", "The concept document cannot be empty."

    elif step == 4:
        # The Stack step is now optional.
        return True, "", ""

    elif step == 5:
        todo = state_data["todo_md"]
        if not todo:
            return False, "Error", "The TODO plan cannot be empty."

    return True, "", ""