import os
import json
import hashlib
import logging
import threading
import shutil
import re
from pathlib import Path
from ..constants import COMPACT_MODE_BG_COLOR
from .utils import get_token_count_for_text, calculate_font_color, get_file_hash
from .config_io import (
    generate_random_color, ensure_dir_hidden, write_hi_text,
    atomic_write, read_project_display_info
)

log = logging.getLogger("CodeMerger")

class ProjectConfig:
    """
    Manages loading and saving the .codemerger configuration for a project directory.
    Aggregates known files from all profile segments to maintain project-wide memory.
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.config_dir = os.path.join(self.base_dir, '.codemerger')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.hi_file = os.path.join(self.config_dir, 'hi.txt')
        self.profiles_dir = os.path.join(self.config_dir, 'profiles')
        self.legacy_allcode_path = os.path.join(self.base_dir, '.allcode')

        self.project_name = os.path.basename(self.base_dir)
        self.project_color = COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.known_files = []

        self.profiles = {}
        self.active_profile_name = "default"
        self._last_mtimes = {}
        self._last_content_hash = None

        # State Latch: Prevents background reloads from reverting unsaved memory changes
        self.is_dirty = False

        self._load_successful = False
        self._lock = threading.RLock()

    @staticmethod
    def read_project_display_info(base_dir):
        return read_project_display_info(base_dir)

    def _sanitize_profile_name(self, name):
        """Converts profile name to a safe, lowercase kebab-case string for IDs and folders."""
        if not name:
            return "default"
        safe = re.sub(r'[^a-z0-9_-]+', '-', name.lower()).strip('-')
        return safe if safe else "default-profile"

    def get_active_profile(self):
        if self.active_profile_name not in self.profiles:
            self.profiles[self.active_profile_name] = self._create_empty_profile()
        return self.profiles[self.active_profile_name]

    def _create_empty_profile(self, name="Default"):
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

    @property
    def visualizer_map(self):
        return self.get_active_profile().get('visualizer_map')

    @visualizer_map.setter
    def visualizer_map(self, value):
        self.get_active_profile()['visualizer_map'] = value

    @property
    def selected_files(self):
        return self.get_active_profile().get('selected_files', [])

    @selected_files.setter
    def selected_files(self, value):
        self.get_active_profile()['selected_files'] = value

    @property
    def total_tokens(self):
        return self.get_active_profile().get('total_tokens', 0)

    @total_tokens.setter
    def total_tokens(self, value):
        self.get_active_profile()['total_tokens'] = value

    @property
    def intro_text(self):
        return self.get_active_profile().get('intro_text', '')

    @intro_text.setter
    def intro_text(self, value):
        self.get_active_profile()['intro_text'] = value

    @property
    def outro_text(self):
        return self.get_active_profile().get('outro_text', '')

    @outro_text.setter
    def outro_text(self, value):
        self.get_active_profile()['outro_text'] = value

    @property
    def expanded_dirs(self):
        return set(self.get_active_profile().get('expanded_dirs', []))

    @expanded_dirs.setter
    def expanded_dirs(self, value):
        self.get_active_profile()['expanded_dirs'] = sorted(list(value))

    @property
    def unknown_files(self):
        return self.get_active_profile().get('unknown_files', [])

    @unknown_files.setter
    def unknown_files(self, value):
        self.get_active_profile()['unknown_files'] = sorted(list(set(value)))

    def load(self):
        """
        Loads and reconciles project settings using multi-segment aggregation logic.
        Uses atomic state updates to prevent data loss on transient file access errors.
        """
        with self._lock:
            if self.is_dirty:
                return False

            if not os.path.isfile(self.config_file) and not os.path.isfile(self.legacy_allcode_path):
                self._load_successful = True
                return False

            if not os.path.isfile(self.config_file) and os.path.isfile(self.legacy_allcode_path):
                from .config_migration import migrate_legacy_project
                return migrate_legacy_project(self)

            # Local buffers to ensure atomicity
            loaded_data = {}
            loaded_profiles = {}
            config_was_updated = False
            files_were_cleaned_globally = False

            # Retry loop for transient Windows file locks (crucial when CM edits itself)
            max_retries = 5
            last_err = None
            for attempt in range(max_retries):
                try:
                    if not os.path.isfile(self.config_file):
                        return False
                    if os.path.getsize(self.config_file) == 0:
                        time.sleep(0.1)
                        continue

                    self._last_mtimes[self.config_file] = os.path.getmtime(self.config_file)
                    with open(self.config_file, 'r', encoding='utf-8-sig') as f:
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
                # Log but don't raise; allows ProjectManager to keep current memory state
                log.warning(f"ProjectConfig: Transient load failure (file locked or empty): {last_err or 'Empty file'}")
                return False

            all_found_known = {p.replace('\\', '/') for p in loaded_data.get('known_files', [])}

            if os.path.isdir(self.profiles_dir):
                for item_name in os.listdir(self.profiles_dir):
                    full_path = os.path.join(self.profiles_dir, item_name)

                    if os.path.isfile(full_path) and item_name.endswith('.json'):
                        profile_id = self._sanitize_profile_name(item_name[:-5])
                        try:
                            with open(full_path, 'r', encoding='utf-8-sig') as f:
                                p_data = json.load(f)
                                if 'name' not in p_data:
                                    p_data['name'] = item_name[:-5]
                                if 'known_files' in p_data:
                                    for p in p_data.pop('known_files', []):
                                        all_found_known.add(p.replace('\\', '/'))
                                loaded_profiles[profile_id] = p_data
                            config_was_updated = True
                        except Exception: pass

                    elif os.path.isdir(full_path):
                        profile_id = self._sanitize_profile_name(item_name)
                        profile_data = self._create_empty_profile(name=item_name)

                        def load_segment(filename, key, default):
                            filepath = os.path.join(full_path, filename)
                            if os.path.isfile(filepath):
                                try:
                                    if os.path.getsize(filepath) == 0: return False
                                    self._last_mtimes[filepath] = os.path.getmtime(filepath)
                                    with open(filepath, 'r', encoding='utf-8-sig') as f:
                                        profile_data[key] = json.load(f)
                                    return True
                                except Exception: return False
                            else:
                                profile_data[key] = default
                                return True

                        load_segment('instructions.json', 'inst', None)
                        if not profile_data.get('inst'):
                            load_segment('settings.json', 'inst', None)

                        if profile_data.get('inst'):
                            inst = profile_data.pop('inst')
                            profile_data['intro_text'] = inst.get('intro_text', '')
                            profile_data['outro_text'] = inst.get('outro_text', '')
                            if 'total_tokens' in inst:
                                profile_data['total_tokens'] = inst['total_tokens']

                        load_segment('selection.json', 'selected_files', [])
                        load_segment('files.json', 'files_data', None)
                        if profile_data.get('files_data'):
                            fd = profile_data.pop('files_data')
                            profile_data['unknown_files'] = fd.get('unknown_files', [])
                            profile_data['total_tokens'] = fd.get('total_tokens', profile_data.get('total_tokens', 0))
                            for p in fd.get('known_files', []):
                                all_found_known.add(p.replace('\\', '/'))

                        load_segment('ui.json', 'ui_data', None)
                        if profile_data.get('ui_data'):
                            ui_data = profile_data.pop('ui_data')
                            profile_data['name'] = ui_data.get('name', item_name)
                            profile_data['expanded_dirs'] = ui_data.get('expanded_dirs', [])

                        load_segment('visualizer.json', 'visualizer_map', None)

                        if profile_id not in loaded_profiles:
                            loaded_profiles[profile_id] = profile_data

            if not loaded_profiles:
                if os.path.isfile(self.config_file) and os.path.getsize(self.config_file) > 10:
                    log.error("ProjectConfig: Configuration exists but profiles are missing or inaccessible.")
                    return False

                loaded_profiles['default'] = self._create_empty_profile(name='Default')
                config_was_updated = True

            # Atomic Swap: Apply local buffers to self only after successful sequence
            self.project_name = loaded_data.get('project_name', os.path.basename(self.base_dir))
            self.project_color = loaded_data.get('project_color', generate_random_color())
            self.project_font_color = loaded_data.get('project_font_color', calculate_font_color(self.project_color))
            self.active_profile_name = self._sanitize_profile_name(loaded_data.get('active_profile', 'default'))
            self.profiles = loaded_profiles

            for profile_name, profile_data in self.profiles.items():
                profile_data['unknown_files'] = sorted(list({p.replace('\\', '/') for p in profile_data.get('unknown_files', [])}))
                for f_info in profile_data.get('selected_files', []):
                    path = f_info['path'] if isinstance(f_info, dict) else f_info
                    all_found_known.add(path.replace('\\', '/'))

                files_cleaned, profile_updated = self._clean_profile_files(profile_data)
                if files_cleaned: files_were_cleaned_globally = True
                if profile_updated: config_was_updated = True

            self.known_files = sorted(list(all_found_known))
            self._load_successful = True

            new_hash = self._calculate_hash()
            content_changed = (self._last_content_hash is not None and new_hash != self._last_content_hash)
            if files_were_cleaned_globally: content_changed = True
            self._last_content_hash = new_hash

            if config_was_updated or files_were_cleaned_globally:
                self.save()

            self.is_dirty = False
            return content_changed

    def _calculate_hash(self):
        state = {"name": self.project_name, "color": self.project_color, "profiles": self.profiles, "active": self.active_profile_name, "known": self.known_files}
        return hashlib.md5(json.dumps(state, sort_keys=True).encode()).hexdigest()

    def _clean_profile_files(self, profile_data):
        profile_was_updated = False
        original_selection = profile_data.get('selected_files', [])
        is_new_format = original_selection and isinstance(original_selection[0], dict) and 'path' in original_selection[0]

        cleaned_selection = []
        if not is_new_format:
            if original_selection: profile_was_updated = True
            for f_path in original_selection:
                norm_path = f_path.replace('\\', '/')
                full_path = os.path.join(self.base_dir, norm_path)
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
                        mtime = os.path.getmtime(full_path)
                        file_hash = get_file_hash(full_path)
                        tokens = get_token_count_for_text(content)
                        lines = content.count('\n') + 1
                        cleaned_selection.append({'path': norm_path, 'mtime': mtime, 'hash': file_hash, 'tokens': tokens, 'lines': lines})
                    except OSError: continue
        else:
            for f_info in original_selection:
                rel_path = f_info['path'].replace('\\', '/')
                full_path = os.path.join(self.base_dir, rel_path)
                if os.path.isfile(full_path):
                    f_info['path'] = rel_path
                    # Requirement: Ensure accurate token counts and metadata exist for all entries
                    if any(k not in f_info for k in ['tokens', 'mtime', 'hash', 'lines']):
                        try:
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            f_info['tokens'] = get_token_count_for_text(content)
                            f_info['lines'] = content.count('\n') + 1
                            f_info['mtime'] = os.path.getmtime(full_path)
                            f_info['hash'] = get_file_hash(full_path)
                            profile_was_updated = True
                        except OSError:
                            pass
                    cleaned_selection.append(f_info)

        profile_data['selected_files'] = cleaned_selection
        files_were_cleaned = len(cleaned_selection) < len(original_selection)

        # Recalculate total tokens if files were removed OR if metadata was computed for incomplete entries
        if files_were_cleaned or profile_was_updated:
            profile_data['total_tokens'] = sum(f.get('tokens', 0) for f in cleaned_selection)

        return files_were_cleaned, profile_was_updated

    def save(self):
        """
        Saves configuration by breaking it into logical chunks per profile.
        Orphaned profile cleanup is intentionally excluded here to prevent data loss
        during race conditions; cleanup is handled explicitly in delete_profile.
        """
        with self._lock:
            if not self._load_successful and (os.path.isfile(self.config_file) or os.path.isfile(self.legacy_allcode_path)):
                return

            self.is_dirty = False

            os.makedirs(self.config_dir, exist_ok=True)
            ensure_dir_hidden(self.config_dir)
            os.makedirs(self.profiles_dir, exist_ok=True)
            write_hi_text(self.hi_file)

            config_data = {
                "project_name": self.project_name,
                "project_color": self.project_color,
                "project_font_color": self.project_font_color,
                "active_profile": self.active_profile_name
            }

            atomic_write(self.config_file, config_data)
            self._last_mtimes[self.config_file] = os.path.getmtime(self.config_file)

            for profile_name, profile_data in self.profiles.items():
                safe_name = self._sanitize_profile_name(profile_name)
                profile_dir = os.path.join(self.profiles_dir, safe_name)
                os.makedirs(profile_dir, exist_ok=True)

                def _save_chunk(filename, data):
                    filepath = os.path.join(profile_dir, filename)
                    atomic_write(filepath, data)
                    self._last_mtimes[filepath] = os.path.getmtime(filepath)

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
                    'known_files': sorted(list(set(self.known_files))),
                    'unknown_files': profile_data.get('unknown_files', []),
                    'total_tokens': profile_data.get('total_tokens', 0)
                })
                _save_chunk('visualizer.json', profile_data.get('visualizer_map', None))

            self._last_content_hash = self._calculate_hash()

    def has_external_changes(self):
        """Checks for external modifications by probing chunks of the active profile."""
        if self.is_dirty: return False
        if not os.path.isfile(self.config_file): return False
        try:
            if abs(os.path.getmtime(self.config_file) - self._last_mtimes.get(self.config_file, 0)) > 0.1:
                return True

            safe_active = self._sanitize_profile_name(self.active_profile_name)
            active_profile_dir = os.path.join(self.profiles_dir, safe_active)

            if os.path.isdir(active_profile_dir):
                for sub_file in os.listdir(active_profile_dir):
                    if sub_file.endswith('.json'):
                        sub_path = os.path.join(active_profile_dir, sub_file)
                        if abs(os.path.getmtime(sub_path) - self._last_mtimes.get(sub_path, 0)) > 0.1:
                            return True
            return False
        except OSError: return False

    def get_profile_names(self):
        return sorted(list(self.profiles.keys()))

    def create_new_profile(self, name, copy_files, copy_instructions):
        """Creates a new sanitized profile and returns the resulting safe name."""
        with self._lock:
            safe_name = self._sanitize_profile_name(name)
            if safe_name in self.profiles: return None
            if copy_files or copy_instructions:
                source = self.get_active_profile()
                new_profile = {
                    "name": name,
                    "selected_files": [dict(f) for f in source.get('selected_files', [])] if copy_files else [],
                    "total_tokens": source.get('total_tokens', 0) if copy_files else 0,
                    "intro_text": source.get('intro_text', '') if copy_instructions else '',
                    "outro_text": source.get('outro_text', '') if copy_instructions else '',
                    "expanded_dirs": source.get('expanded_dirs', [])[:] if copy_files else [],
                    "unknown_files": source.get('unknown_files', [])[:] if copy_files else []
                }
            else: new_profile = self._create_empty_profile(name=name)
            self.profiles[safe_name] = new_profile
            return safe_name

    def delete_profile(self, profile_name_to_delete):
        """Explicitly removes a profile from memory and physically deletes its directory."""
        with self._lock:
            if profile_name_to_delete == "default" or profile_name_to_delete not in self.profiles:
                return False

            safe_name = self._sanitize_profile_name(profile_name_to_delete)
            profile_dir = os.path.join(self.profiles_dir, safe_name)

            del self.profiles[profile_name_to_delete]

            if self.active_profile_name == profile_name_to_delete:
                self.active_profile_name = "default"

            if os.path.isdir(profile_dir):
                try:
                    shutil.rmtree(profile_dir)
                except OSError as e:
                    log.error(f"ProjectConfig: Failed to delete profile directory: {e}")

            return True

    def update_known_files(self, paths, originating_profile_name=None):
        if not paths: return False
        changed = False
        known_set = set(self.known_files)
        actually_new = []
        for path in paths:
            if path not in known_set:
                actually_new.append(path)
                known_set.add(path)
                changed = True

        if actually_new:
            self.known_files = sorted(list(known_set))
            for name, p_data in self.profiles.items():
                if name == originating_profile_name: continue
                selected = {f['path'] for f in p_data.get('selected_files', [])}
                unknown = [p for p in actually_new if p not in selected]
                if unknown:
                    p_unknown = set(p_data.get('unknown_files', []))
                    p_unknown.update(unknown)
                    p_data['unknown_files'] = sorted(list(p_unknown))
        return changed