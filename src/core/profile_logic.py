import re
import os
import shutil
import logging

log = logging.getLogger("CodeMerger")

def sanitize_profile_name(name):
    """Converts profile name to a safe, lowercase kebab-case string for IDs and folders."""
    if not name:
        return "default"
    safe = re.sub(r'[^a-z0-9_-]+', '-', name.lower()).strip('-')
    return safe if safe else "default-profile"

def create_empty_profile_dict(name="Default"):
    """Returns a dictionary with the schema for a new project profile."""
    return {
        "name": name,
        "selected_files": [],
        "total_tokens": 0,
        "intro_text": "",
        "outro_text": "",
        "expanded_dirs": [],
        "unknown_files": [],
        "visualizer_map": None
    }

def create_new_profile(config_instance, name, copy_files, copy_instructions):
    """Initializes a new profile in memory, optionally cloning from the active profile."""
    safe_name = sanitize_profile_name(name)
    if safe_name in config_instance.profiles:
        return None

    if copy_files or copy_instructions:
        source = config_instance.get_active_profile()
        new_profile = {
            "name": name,
            "selected_files": [dict(f) for f in source.get('selected_files', [])] if copy_files else [],
            "total_tokens": source.get('total_tokens', 0) if copy_files else 0,
            "intro_text": source.get('intro_text', '') if copy_instructions else '',
            "outro_text": source.get('outro_text', '') if copy_instructions else '',
            "expanded_dirs": source.get('expanded_dirs', [])[:] if copy_files else [],
            "unknown_files": source.get('unknown_files', [])[:] if copy_files else []
        }
    else:
        new_profile = create_empty_profile_dict(name=name)

    config_instance.profiles[safe_name] = new_profile
    return safe_name

def delete_profile(config_instance, profile_name_to_delete):
    """Removes profile from memory and cleans up its associated filesystem directory."""
    if profile_name_to_delete == "default" or profile_name_to_delete not in config_instance.profiles:
        return False

    safe_name = sanitize_profile_name(profile_name_to_delete)
    profile_dir = os.path.join(config_instance.profiles_dir, safe_name)

    del config_instance.profiles[profile_name_to_delete]

    if config_instance.active_profile_name == profile_name_to_delete:
        config_instance.active_profile_name = "default"

    if os.path.isdir(profile_dir):
        try:
            shutil.rmtree(profile_dir)
        except OSError as e:
            log.error(f"ProfileLogic: Failed to delete profile directory: {e}")

    return True

def update_known_files_logic(config_instance, paths, originating_profile_name=None):
    """Updates project-wide known files and propagates new files to other profile's unknown lists."""
    if not paths:
        return False

    changed = False
    known_set = set(config_instance.known_files)
    actually_new = []

    for path in paths:
        if path not in known_set:
            actually_new.append(path)
            known_set.add(path)
            changed = True

    if actually_new:
        config_instance.known_files = sorted(list(known_set))
        for name, p_data in config_instance.profiles.items():
            if name == originating_profile_name:
                continue
            selected = {f['path'] for f in p_data.get('selected_files', [])}
            unknown = [p for p in actually_new if p not in selected]
            if unknown:
                p_unknown = set(p_data.get('unknown_files', []))
                p_unknown.update(unknown)
                p_data['unknown_files'] = sorted(list(p_unknown))

    return changed