import os
import json
from .config_io import generate_random_color
from .utils import calculate_font_color

def migrate_legacy_project(config_instance):
    """Loads legacy .allcode format and triggers structured migration."""
    try:
        with open(config_instance.legacy_allcode_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to read legacy project config: {e}")

    config_instance.project_name = data.get('project_name', os.path.basename(config_instance.base_dir))
    config_instance.project_color = data.get('project_color', generate_random_color())
    config_instance.project_font_color = data.get('project_font_color', calculate_font_color(config_instance.project_color))

    if 'profiles' in data:
        config_instance.profiles = data.get('profiles', {})
        config_instance.active_profile_name = data.get('active_profile', 'Default')
    elif 'selected_files' in data:
        default_profile = config_instance._create_empty_profile()
        default_profile['intro_text'] = data.get('intro_text', '')
        default_profile['outro_text'] = data.get('outro_text', '')
        default_profile['expanded_dirs'] = data.get('expanded_dirs', [])
        default_profile['selected_files'] = data.get('selected_files', [])
        default_profile['total_tokens'] = data.get('total_tokens', 0)
        config_instance.profiles = {'Default': default_profile}
        config_instance.active_profile_name = 'Default'

    all_found_known = {p.replace('\\', '/') for p in data.get('known_files', [])}
    for p_data in config_instance.profiles.values():
        if 'known_files' in p_data:
            for p in p_data.pop('known_files', []):
                all_found_known.add(p.replace('\\', '/'))

        for f_info in p_data.get('selected_files', []):
            path = f_info['path'] if isinstance(f_info, dict) else f_info
            all_found_known.add(path.replace('\\', '/'))

    config_instance.known_files = sorted(list(all_found_known))
    config_instance._load_successful = True
    config_instance.save()

    try:
        backup_path = config_instance.legacy_allcode_path + '.bak'
        if os.path.exists(backup_path): os.remove(backup_path)
        os.rename(config_instance.legacy_allcode_path, backup_path)
    except OSError: pass

    config_instance._last_content_hash = config_instance._calculate_hash()
    return True