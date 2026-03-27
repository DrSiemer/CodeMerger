import re
import shutil
import logging
import os
from pathlib import Path
from ...core.merger import get_language_from_path

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
                return False, project_path, "Failed to delete existing folder: " + str(e)
        else:
            return False, project_path, "Project folder already exists."

    try:
        project_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, project_path, "Failed to create project directory: " + str(e)

    return True, project_path, ""

def parse_and_write_files(project_path, llm_output):
    """
    Parses the LLM response for file blocks and writes them to the project path.
    Uses a robust regex to handle whitespace variations and short files.
    """
    # Construct counting logic with fragments for self-processing safety
    PREFIX = "--- "
    FILE_LABEL = "File: "
    EOF_LABEL = "End of file"
    EOF_MARKER = PREFIX + EOF_LABEL + " ---"

    # Use anchored line-start counts
    start_count_pattern = r'^' + re.escape(PREFIX) + re.escape(FILE_LABEL)
    end_count_pattern = r'^' + re.escape(PREFIX) + re.escape(EOF_LABEL)

    start_count = len(re.findall(start_count_pattern, llm_output, re.MULTILINE))
    end_count = len(re.findall(end_count_pattern, llm_output, re.MULTILINE))

    if start_count != end_count:
        return False, [], f"Format Error: Marker mismatch detected ({start_count} starts, {end_count} ends). Please ask the AI to provide the full output again."

    # Pattern constructed using fragments for self-processing safety.
    file_pattern = re.compile(
        re.escape(PREFIX) + r'File: `([^\n`]+)` ---\s*[\r\n]+```[^\n]*[\r\n]+(.*?)\n?```\s*[\r\n]+' + re.escape(EOF_MARKER),
        re.DOTALL
    )

    matches = file_pattern.finditer(llm_output)

    files_created = []
    found_any = False

    for match in matches:
        found_any = True
        file_path_str, content = match.groups()

        # Cleanup potential prefixing from LLM
        clean_rel_path = file_path_str.replace("boilerplate/", "").strip().replace('\\', '/')
        relative_path = Path(clean_rel_path)
        full_path = project_path / relative_path

        try:
            # Security check: Ensure we stay within project path
            if not os.path.normpath(str(full_path)).startswith(os.path.normpath(str(project_path))):
                log.warning("Skipped file outside project: " + file_path_str)
                continue

            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Preserve original sanitization logic
            sanitized_content = "\n".join([line.rstrip() for line in content.splitlines()])

            # This overwrites any pre-copied boilerplate files if the LLM included them
            full_path.write_text(sanitized_content, encoding="utf-8")
            files_created.append(str(relative_path))
        except Exception as e:
            log.error("Failed to write file " + str(relative_path) + ": " + str(e))

    if not found_any:
        # Preserve original return error message
        return False, [], "No valid file blocks were found. Make sure each file is wrapped with '--- File: `path` ---' and '--- End of file ---', and ensure the code is wrapped in standard triple backticks."

    return True, files_created, ""

def write_base_reference_file(project_path, base_path, base_files):
    """
    Creates a project_reference.md file containing all files from the base project's merge list.
    """
    if not base_path or not base_files:
        return False

    output_blocks = []
    output_blocks.append("# Base Project Reference\n\nThis file contains the code from the base project: `" + base_path + "`\n")

    # Construct markers via fragments
    PREFIX = "--- "
    FILE_TAG = "File: "
    EOF_TAG = "End of file"

    for file_info in base_files:
        rel_path = file_info['path']
        full_path = os.path.join(base_path, rel_path)
        if not os.path.isfile(full_path):
            continue

        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()

            language = get_language_from_path(rel_path)

            # Use safe concatenation
            header = f"{PREFIX}{FILE_TAG}`{rel_path}` ---"
            footer = f"{PREFIX}{EOF_TAG} ---"

            block = [
                header,
                "```" + language,
                content,
                "```",
                footer
            ]
            output_blocks.append("\n".join(block))
        except Exception as e:
            log.error("Failed to read base file " + rel_path + " for reference: " + str(e))

    final_content = "\n\n".join(output_blocks)
    ref_file_path = project_path / "project_reference.md"

    try:
        ref_file_path.write_text(final_content, encoding="utf-8")
        return True
    except Exception as e:
        log.error("Failed to write project_reference.md: " + str(e))
        return False