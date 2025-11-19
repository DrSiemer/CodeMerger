import json
import os
import logging
from ...core.paths import PERSISTENT_DATA_DIR

log = logging.getLogger("CodeMerger")
SESSION_FILE = os.path.join(PERSISTENT_DATA_DIR, "project_starter_session.json")

def get_session_filepath():
    """Returns the path to the default session file."""
    return SESSION_FILE

def save_session_data(data, filepath=None):
    """Saves the project data dictionary to a JSON file."""
    target = filepath if filepath else SESSION_FILE
    try:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Failed to save session to {target}: {e}")

def load_session_data(filepath=None):
    """
    Loads project data from a JSON file.
    Returns an empty dict if the file doesn't exist or fails to load.
    """
    target = filepath if filepath else SESSION_FILE
    if not os.path.exists(target):
        return {}
    try:
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Failed to load session from {target}: {e}")
        return {}

def clear_default_session():
    """Deletes the default session file if it exists."""
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except OSError as e:
            log.error(f"Failed to delete session file: {e}")