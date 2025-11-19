import re
import shutil
import logging
from pathlib import Path

log = logging.getLogger("CodeMerger")

def sanitize_project_name(name):
    """Sanitizes the project name for use as a folder name."""
    return re.sub(r'[^a-zA-Z0-9_-]+', '-', name.lower()).strip('-')

def prepare_project_directory(parent_folder, project_name, overwrite=False):
    """
    Prepares the target directory.
    Returns: (success: bool, path: Path, message: str)
    """
    sanitized_name = sanitize_project_name(project_name)
    base_dir = Path(parent_folder)
    project_path = base_dir / sanitized_name

    if project_path.exists():
        if overwrite:
            try:
                shutil.rmtree(project_path)
            except Exception as e:
                return False, project_path, f"Failed to delete existing folder: {e}"
        else:
            return False, project_path, "Project folder already exists."

    try:
        project_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, project_path, f"Failed to create project directory: {e}"

    return True, project_path, ""

def parse_and_write_files(project_path, llm_output):
    """
    Parses the LLM response for file blocks and writes them to the project path.
    Returns: (success: bool, files_created: list, message: str)
    """
    # Regex to find --- File: `path` --- blocks
    file_pattern = re.compile(r"--- File: `(.+?)` ---\s*```.*?$(.*?)```", re.MULTILINE | re.DOTALL)
    matches = file_pattern.finditer(llm_output)

    files_created = []
    found_any = False

    for match in matches:
        found_any = True
        file_path_str, content = match.groups()
        # Remove 'boilerplate/' prefix if the LLM kept it from the source context
        clean_rel_path = file_path_str.replace("boilerplate/", "")
        relative_path = Path(clean_rel_path)
        full_path = project_path / relative_path

        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content.lstrip(), encoding="utf-8")
            files_created.append(str(relative_path))
        except Exception as e:
            log.error(f"Failed to write file {relative_path}: {e}")

    if not found_any:
        return False, [], "Could not find any files to create in the LLM output. Ensure the format is correct."

    return True, files_created, ""