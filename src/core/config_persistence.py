import os
import json
import time
import hashlib
import logging
from .utils import calculate_font_color
from .config_io import generate_random_color, atomic_write, ensure_dir_hidden, write_hi_text
from .profile_logic import sanitize_profile_name, create_empty_profile_dict
from .file_metadata import clean_and_update_metadata

log = logging.getLogger("CodeMerger")

def calculate_content_hash(config_instance):
    """Generates an MD5 hash of the current project state to detect internal changes."""
    state = {
        "name": config_instance.project_name,
        "color": config_instance.project_color,
        "profiles": config_instance.profiles,
        "active": config_instance.active_profile_name,
        "known": config_instance.known_files
    }
    return hashlib.md5(json.dumps(state, sort_keys=True).encode()).hexdigest()

def has_external_config_changes(config_instance):
    """Checks mtimes of config files to identify modifications from outside the app."""
    if config_instance.is_dirty: return False
    if not os.path.isfile(config_instance.config_file): return False
    try:
        if abs(os.path.getmtime(config_instance.config_file) - config_instance._last_mtimes.get(config_instance.config_file, 0)) > 0.1:
            return True

        safe_active = sanitize_profile_name(config_instance.active_profile_name)
        active_profile_dir = os.path.join(config_instance.profiles_dir, safe_active)

        if os.path.isdir(active_profile_dir):
            for sub_file in os.listdir(active_profile_dir):
                if sub_file.endswith('.json'):
                    sub_path = os.path.join(active_profile_dir, sub_file)
                    if abs(os.path.getmtime(sub_path) - config_instance._last_mtimes.get(sub_path, 0)) > 0.1:
                        return True
        return False
    except OSError: return False

def load_project_config(config_instance):
    """Executes the procedural logic to load and reconcile project configuration chunks."""
    if not os.path.isfile(config_instance.config_file) and not os.path.isfile(config_instance.legacy_allcode_path):
        config_instance._load_successful = True
        return False

    if not os.path.isfile(config_instance.config_file) and os.path.isfile(config_instance.legacy_allcode_path):
        from .config_migration import migrate_legacy_project
        return migrate_legacy_project(config_instance)

    loaded_data = {}
    loaded_profiles = {}
    config_was_updated = False
    files_were_cleaned_globally = False

    max_retries = 5
    last_err = None
    for attempt in range(max_retries):
        try:
            if not os.path.isfile(config_instance.config_file): return False
            if os.path.getsize(config_instance.config_file) == 0:
                time.sleep(0.1)
                continue

            config_instance._last_mtimes[config_instance.config_file] = os.path.getmtime(config_instance.config_file)
            with open(config_instance.config_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if content:
                    try:
                        loaded_data = json.loads(content)
                        last_err = None
                        break
                    except json.JSONDecodeError:
                        json_start_index = content.find('{')
                        if json_start_index != -1:
                            loaded_data = json.loads(content[json_start_index:])
                            config_was_updated = True
                            last_err = None
                            break
        except (IOError, OSError) as e:
            last_err = e
            time.sleep(0.1)

    if last_err or not loaded_data:
        log.warning(f"ProjectConfig: Transient load failure: {last_err or 'Empty file'}")
        return False

    all_found_known = {p.replace('\\', '/') for p in loaded_data.get('known_files', [])}

    if os.path.isdir(config_instance.profiles_dir):
        for item_name in os.listdir(config_instance.profiles_dir):
            full_path = os.path.join(config_instance.profiles_dir, item_name)
            if os.path.isfile(full_path) and item_name.endswith('.json'):
                profile_id = sanitize_profile_name(item_name[:-5])
                try:
                    with open(full_path, 'r', encoding='utf-8-sig') as f:
                        p_data = json.load(f)
                        if 'name' not in p_data: p_data['name'] = item_name[:-5]
                        if 'known_files' in p_data:
                            for p in p_data.pop('known_files', []): all_found_known.add(p.replace('\\', '/'))
                        loaded_profiles[profile_id] = p_data
                    config_was_updated = True
                except Exception: pass
            elif os.path.isdir(full_path):
                profile_id = sanitize_profile_name(item_name)
                profile_data = create_empty_profile_dict(name=item_name)

                def load_segment(filename, key, default):
                    filepath = os.path.join(full_path, filename)
                    if os.path.isfile(filepath):
                        try:
                            if os.path.getsize(filepath) == 0: return False
                            config_instance._last_mtimes[filepath] = os.path.getmtime(filepath)
                            with open(filepath, 'r', encoding='utf-8-sig') as f:
                                profile_data[key] = json.load(f)
                            return True
                        except Exception: return False
                    else:
                        profile_data[key] = default
                        return True

                load_segment('instructions.json', 'inst', None)
                if not profile_data.get('inst'): load_segment('settings.json', 'inst', None)

                if profile_data.get('inst'):
                    inst = profile_data.pop('inst')
                    profile_data['intro_text'] = inst.get('intro_text', '')
                    profile_data['outro_text'] = inst.get('outro_text', '')
                    if 'total_tokens' in inst: profile_data['total_tokens'] = inst['total_tokens']

                load_segment('selection.json', 'selected_files', [])
                load_segment('files.json', 'files_data', None)
                if profile_data.get('files_data'):
                    fd = profile_data.pop('files_data')
                    profile_data['unknown_files'] = fd.get('unknown_files', [])
                    profile_data['total_tokens'] = fd.get('total_tokens', profile_data.get('total_tokens', 0))
                    for p in fd.get('known_files', []): all_found_known.add(p.replace('\\', '/'))

                load_segment('ui.json', 'ui_data', None)
                if profile_data.get('ui_data'):
                    ui_data = profile_data.pop('ui_data')
                    profile_data['name'] = ui_data.get('name', item_name)
                    profile_data['expanded_dirs'] = ui_data.get('expanded_dirs', [])

                load_segment('visualizer.json', 'visualizer_map', None)
                if profile_id not in loaded_profiles: loaded_profiles[profile_id] = profile_data

    if not loaded_profiles:
        if os.path.isfile(config_instance.config_file) and os.path.getsize(config_instance.config_file) > 10:
            log.error("ProjectConfig: Configuration exists but profiles are missing.")
            return False
        loaded_profiles['default'] = create_empty_profile_dict(name='Default')
        config_was_updated = True

    config_instance.project_name = loaded_data.get('project_name', os.path.basename(config_instance.base_dir))
    config_instance.project_color = loaded_data.get('project_color', generate_random_color())
    config_instance.project_font_color = loaded_data.get('project_font_color', calculate_font_color(config_instance.project_color))
    config_instance.active_profile_name = sanitize_profile_name(loaded_data.get('active_profile', 'default'))
    config_instance.profiles = loaded_profiles

    for profile_name, profile_data in config_instance.profiles.items():
        profile_data['unknown_files'] = sorted(list({p.replace('\\', '/') for p in profile_data.get('unknown_files', [])}))
        for f_info in profile_data.get('selected_files', []):
            path = f_info['path'] if isinstance(f_info, dict) else f_info
            all_found_known.add(path.replace('\\', '/'))
        files_cleaned, profile_updated = clean_and_update_metadata(config_instance, profile_data)
        if files_cleaned: files_were_cleaned_globally = True
        if profile_updated: config_was_updated = True

    config_instance.known_files = sorted(list(all_found_known))
    config_instance._load_successful = True

    new_hash = calculate_content_hash(config_instance)
    content_changed = (config_instance._last_content_hash is not None and new_hash != config_instance._last_content_hash)
    if files_were_cleaned_globally: content_changed = True
    config_instance._last_content_hash = new_hash

    if config_was_updated or files_were_cleaned_globally: config_instance.save()
    config_instance.is_dirty = False
    return content_changed

def save_project_config(config_instance):
    """Segments the project state and performs atomic writes for the master config and each profile."""
    if not config_instance._load_successful and (os.path.isfile(config_instance.config_file) or os.path.isfile(config_instance.legacy_allcode_path)):
        return

    config_instance.is_dirty = False
    os.makedirs(config_instance.config_dir, exist_ok=True)
    ensure_dir_hidden(config_instance.config_dir)
    os.makedirs(config_instance.profiles_dir, exist_ok=True)
    write_hi_text(config_instance.hi_file)

    config_data = {
        "project_name": config_instance.project_name,
        "project_color": config_instance.project_color,
        "project_font_color": config_instance.project_font_color,
        "active_profile": config_instance.active_profile_name
    }

    atomic_write(config_instance.config_file, config_data)
    config_instance._last_mtimes[config_instance.config_file] = os.path.getmtime(config_instance.config_file)

    for profile_name, profile_data in config_instance.profiles.items():
        safe_name = sanitize_profile_name(profile_name)
        profile_dir = os.path.join(config_instance.profiles_dir, safe_name)
        os.makedirs(profile_dir, exist_ok=True)

        def _save_chunk(filename, data):
            filepath = os.path.join(profile_dir, filename)
            atomic_write(filepath, data)
            config_instance._last_mtimes[filepath] = os.path.getmtime(filepath)

        _save_chunk('instructions.json', {
            'intro_text': profile_data.get('intro_text', ''),
            'outro_text': profile_data.get('outro_text', '')
        })
        _save_chunk('selection.json', profile_data.get('selected_files', []))
        _save_chunk('ui.json', {
            'name': profile_data.get('name', profile_name),
            'expanded_dirs': profile_data.get('expanded_dirs', [])
        })
        _save_chunk('files.json', {
            'known_files': sorted(list(set(config_instance.known_files))),
            'unknown_files': profile_data.get('unknown_files', []),
            'total_tokens': profile_data.get('total_tokens', 0)
        })
        _save_chunk('visualizer.json', profile_data.get('visualizer_map', None))

    config_instance._last_content_hash = calculate_content_hash(config_instance)