import os
import json
import random
import re
import colorsys
import hashlib
import tempfile
import time
import sys
import logging
import threading
import shutil
from pathlib import Path
from ..constants import COMPACT_MODE_BG_COLOR, CODEMERGER_TEMP_PREFIX
from .utils import get_token_count_for_text, calculate_font_color

log = logging.getLogger("CodeMerger")

def _get_file_hash(full_path):
    try:
        with open(full_path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except (IOError, OSError):
        return None

def _generate_random_color():
    """Generates a random visually pleasing hex color string"""
    hue = random.random()
    saturation = random.uniform(0.5, 0.7)
    value = random.uniform(0.6, 0.8)
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    r_int, g_int, b_int = int(r * 255), int(g * 255), int(b * 255)
    return f"#{r_int:02x}{g_int:02x}{b_int:02x}"

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
        self.active_profile_name = "Default"
        self._last_mtimes = {}
        self._last_content_hash = None

        self._load_successful = False
        self._lock = threading.RLock()

    @staticmethod
    def read_project_display_info(base_dir):
        config_file = os.path.join(base_dir, '.codemerger', 'config.json')
        legacy_path = os.path.join(base_dir, '.allcode')
        project_name = os.path.basename(base_dir)
        project_color = COMPACT_MODE_BG_COLOR

        target_file = config_file if os.path.isfile(config_file) else legacy_path
        if not os.path.isfile(target_file):
            return project_name, project_color

        try:
            with open(target_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if not content: return project_name, project_color
                data = json.loads(content)
                project_name = data.get('project_name', project_name)
                color_value = data.get('project_color')
                if color_value and isinstance(color_value, str) and re.match(r'^#[0-9a-fA-F]{6}$', color_value):
                        project_color = color_value
        except (json.JSONDecodeError, IOError):
            pass

        return project_name, project_color

    def get_active_profile(self):
        if self.active_profile_name not in self.profiles:
            self.profiles[self.active_profile_name] = self._create_empty_profile()
        return self.profiles[self.active_profile_name]

    def _create_empty_profile(self):
        return {
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
        """Loads and reconciles project settings using multi-segment aggregation logic"""
        with self._lock:
            data = {}
            config_was_updated = False
            files_were_cleaned_globally = False

            if not os.path.isfile(self.config_file) and not os.path.isfile(self.legacy_allcode_path):
                self._load_successful = True
                return False

            if not os.path.isfile(self.config_file) and os.path.isfile(self.legacy_allcode_path):
                return self._migrate_legacy_project()

            try:
                self._last_mtimes[self.config_file] = os.path.getmtime(self.config_file)
                if os.path.getsize(self.config_file) == 0:
                    raise RuntimeError("Config file is empty or locked.")

                with open(self.config_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    if content:
                        try:
                            data = json.loads(content)
                        except json.JSONDecodeError:
                            json_start_index = content.find('{')
                            if json_start_index != -1:
                                data = json.loads(content[json_start_index:])
                                config_was_updated = True
                            else:
                                raise RuntimeError("Config file contains no valid JSON.")
            except (json.JSONDecodeError, IOError, OSError) as e:
                raise RuntimeError(f"Failed to read project config: {e}")

            if not data:
                raise RuntimeError("Config file contained an empty JSON object.")

            self.project_name = data.get('project_name', os.path.basename(self.base_dir))
            self.project_color = data.get('project_color', _generate_random_color())
            self.project_font_color = data.get('project_font_color', calculate_font_color(self.project_color))
            self.active_profile_name = data.get('active_profile', 'Default')

            # Global aggregation of known files to prevent false "New File" flags on boot
            all_found_known = set(data.get('known_files', []))

            self.profiles = {}
            if os.path.isdir(self.profiles_dir):
                for item_name in os.listdir(self.profiles_dir):
                    full_path = os.path.join(self.profiles_dir, item_name)

                    if os.path.isfile(full_path) and item_name.endswith('.json'):
                        profile_name = item_name[:-5]
                        try:
                            with open(full_path, 'r', encoding='utf-8-sig') as f:
                                p_data = json.load(f)
                                if 'known_files' in p_data:
                                    all_found_known.update(p_data.pop('known_files', []))
                                self.profiles[profile_name] = p_data
                            config_was_updated = True
                        except Exception: pass

                    elif os.path.isdir(full_path):
                        profile_name = item_name
                        profile_data = self._create_empty_profile()

                        def load_segment(filename, key, default):
                            filepath = os.path.join(full_path, filename)
                            if os.path.isfile(filepath):
                                try:
                                    self._last_mtimes[filepath] = os.path.getmtime(filepath)
                                    with open(filepath, 'r', encoding='utf-8-sig') as f:
                                        profile_data[key] = json.load(f)
                                except Exception: profile_data[key] = default
                            else: profile_data[key] = default

                        # Renamed: instructions.json (Legacy: settings.json)
                        load_segment('instructions.json', 'inst', None)
                        if not profile_data.get('inst'):
                            load_segment('settings.json', 'inst', None)

                        if profile_data.get('inst'):
                            inst = profile_data.pop('inst')
                            profile_data['intro_text'] = inst.get('intro_text', '')
                            profile_data['outro_text'] = inst.get('outro_text', '')
                            if 'total_tokens' in inst: # Migration path from settings.json
                                profile_data['total_tokens'] = inst['total_tokens']

                        load_segment('selection.json', 'selected_files', [])

                        load_segment('files.json', 'files_data', None)
                        if profile_data.get('files_data'):
                            fd = profile_data.pop('files_data')
                            profile_data['unknown_files'] = fd.get('unknown_files', [])
                            profile_data['total_tokens'] = fd.get('total_tokens', profile_data.get('total_tokens', 0))
                            all_found_known.update(fd.get('known_files', []))

                        load_segment('ui.json', 'ui_data', None)
                        if profile_data.get('ui_data'):
                            ui_data = profile_data.pop('ui_data')
                            profile_data['expanded_dirs'] = ui_data.get('expanded_dirs', [])

                        load_segment('visualizer.json', 'visualizer_map', None)

                        if profile_name not in self.profiles:
                            self.profiles[profile_name] = profile_data

            if not self.profiles:
                self.profiles['Default'] = self._create_empty_profile()
                self.active_profile_name = 'Default'
                config_was_updated = True

            for profile_name, profile_data in self.profiles.items():
                profile_data['unknown_files'] = sorted(list(set(profile_data.get('unknown_files', []))))
                for f_info in profile_data.get('selected_files', []):
                    path = f_info['path'] if isinstance(f_info, dict) else f_info
                    all_found_known.add(path)

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

            return content_changed

    def _migrate_legacy_project(self):
        """Loads legacy .allcode format and triggers structured migration."""
        try:
            with open(self.legacy_allcode_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read legacy project config: {e}")

        self.project_name = data.get('project_name', os.path.basename(self.base_dir))
        self.project_color = data.get('project_color', _generate_random_color())
        self.project_font_color = data.get('project_font_color', calculate_font_color(self.project_color))

        if 'profiles' in data:
            self.profiles = data.get('profiles', {})
            self.active_profile_name = data.get('active_profile', 'Default')
        elif 'selected_files' in data:
            default_profile = self._create_empty_profile()
            default_profile['intro_text'] = data.get('intro_text', '')
            default_profile['outro_text'] = data.get('outro_text', '')
            default_profile['expanded_dirs'] = data.get('expanded_dirs', [])
            default_profile['selected_files'] = data.get('selected_files', [])
            default_profile['total_tokens'] = data.get('total_tokens', 0)
            self.profiles = {'Default': default_profile}
            self.active_profile_name = 'Default'

        all_found_known = set(data.get('known_files', []))
        for p_data in self.profiles.values():
            if 'known_files' in p_data: all_found_known.update(p_data.pop('known_files', []))
            for f_info in p_data.get('selected_files', []):
                path = f_info['path'] if isinstance(f_info, dict) else f_info
                all_found_known.add(path)

        self.known_files = sorted(list(all_found_known))
        self._load_successful = True
        self.save()

        try:
            backup_path = self.legacy_allcode_path + '.bak'
            if os.path.exists(backup_path): os.remove(backup_path)
            os.rename(self.legacy_allcode_path, backup_path)
        except OSError: pass

        self._last_content_hash = self._calculate_hash()
        return True

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
                full_path = os.path.join(self.base_dir, f_path)
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
                        mtime = os.path.getmtime(full_path)
                        file_hash = _get_file_hash(full_path)
                        tokens = get_token_count_for_text(content)
                        lines = content.count('\n') + 1
                        cleaned_selection.append({'path': f_path, 'mtime': mtime, 'hash': file_hash, 'tokens': tokens, 'lines': lines})
                    except OSError: continue
        else:
            for f_info in original_selection:
                if os.path.isfile(os.path.join(self.base_dir, f_info['path'])):
                    if 'tokens' not in f_info: profile_was_updated = True
                    cleaned_selection.append(f_info)

        profile_data['selected_files'] = cleaned_selection
        files_were_cleaned = len(cleaned_selection) < len(original_selection)
        if files_were_cleaned:
            profile_data['total_tokens'] = sum(f.get('tokens', 0) for f in cleaned_selection)
            profile_was_updated = True

        return files_were_cleaned, profile_was_updated

    def _ensure_dir_hidden(self, dir_path):
        if sys.platform == "win32" and os.path.exists(dir_path):
            try:
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                attrs = ctypes.windll.kernel32.GetFileAttributesW(dir_path)
                if attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                    ctypes.windll.kernel32.SetFileAttributesW(dir_path, attrs | FILE_ATTRIBUTE_HIDDEN)
            except Exception: pass

    def _write_hi_text(self):
        """Creates a helpful hi.txt file in the .codemerger root."""
        content = """Hi there! This folder contains the configuration and session data for CodeMerger.

CodeMerger helps you bundle your project code for language models while maintaining full custody of your context.

Folder Structure:
- config.json: Project metadata (name, color, and active profile pointer).
- profiles/: Individual directories for your project profiles.
- profiles/[Name]/selection.json: The list and order of files included in your context.
- profiles/[Name]/instructions.json: Your custom Intro and Outro prompts.
- profiles/[Name]/files.json: Profile-specific file states and token counts.

These files are designed to be part of your repository.

Official Repository: https://github.com/DrSiemer/CodeMerger/
"""
        try:
            with open(self.hi_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception: pass

    def _atomic_write(self, target_path, data):
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(target_path), prefix=CODEMERGER_TEMP_PREFIX)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            max_retries = 5
            is_windows = sys.platform == "win32"
            was_hidden = False

            for attempt in range(max_retries):
                try:
                    if is_windows and os.path.exists(target_path):
                        import ctypes
                        FILE_ATTRIBUTE_HIDDEN = 0x02
                        attrs = ctypes.windll.kernel32.GetFileAttributesW(target_path)
                        if attrs != -1 and (attrs & FILE_ATTRIBUTE_HIDDEN):
                            was_hidden = True
                            ctypes.windll.kernel32.SetFileAttributesW(target_path, attrs & ~FILE_ATTRIBUTE_HIDDEN)

                    os.replace(temp_path, target_path)
                    temp_path = None

                    if is_windows and was_hidden:
                        attrs = ctypes.windll.kernel32.GetFileAttributesW(target_path)
                        if attrs != -1:
                            ctypes.windll.kernel32.SetFileAttributesW(target_path, attrs | FILE_ATTRIBUTE_HIDDEN)
                    break
                except PermissionError:
                    if attempt == max_retries - 1: raise
                    time.sleep(0.1)
        finally:
            if temp_path and os.path.exists(temp_path):
                try: os.remove(temp_path)
                except Exception: pass

    def save(self):
        """Saves configuration by breaking it into logical chunks per profile."""
        with self._lock:
            if not self._load_successful and (os.path.isfile(self.config_file) or os.path.isfile(self.legacy_allcode_path)):
                return

            os.makedirs(self.config_dir, exist_ok=True)
            self._ensure_dir_hidden(self.config_dir)
            os.makedirs(self.profiles_dir, exist_ok=True)
            self._write_hi_text()

            config_data = {
                "project_name": self.project_name,
                "project_color": self.project_color,
                "project_font_color": self.project_font_color,
                "active_profile": self.active_profile_name
            }

            self._atomic_write(self.config_file, config_data)
            self._last_mtimes[self.config_file] = os.path.getmtime(self.config_file)

            active_profile_dirs = []
            for profile_name, profile_data in self.profiles.items():
                safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                if not safe_name: safe_name = "default_profile"

                profile_dir = os.path.join(self.profiles_dir, safe_name)
                os.makedirs(profile_dir, exist_ok=True)
                active_profile_dirs.append(profile_dir)

                def _save_chunk(filename, data):
                    filepath = os.path.join(profile_dir, filename)
                    self._atomic_write(filepath, data)
                    self._last_mtimes[filepath] = os.path.getmtime(filepath)

                _save_chunk('instructions.json', {
                    'intro_text': profile_data.get('intro_text', ''),
                    'outro_text': profile_data.get('outro_text', '')
                })
                _save_chunk('selection.json', profile_data.get('selected_files', []))
                _save_chunk('ui.json', {
                    'expanded_dirs': profile_data.get('expanded_dirs', [])
                })
                _save_chunk('files.json', {
                    'known_files': sorted(list(set(self.known_files))),
                    'unknown_files': profile_data.get('unknown_files', []),
                    'total_tokens': profile_data.get('total_tokens', 0)
                })
                _save_chunk('visualizer.json', profile_data.get('visualizer_map', None))

            # Cleanup orphaned profile items or legacy JSON files
            for item_name in os.listdir(self.profiles_dir):
                full_path = os.path.join(self.profiles_dir, item_name)
                if os.path.isdir(full_path):
                    if full_path not in active_profile_dirs:
                        try: shutil.rmtree(full_path)
                        except OSError: pass
                elif os.path.isfile(full_path) and full_path.endswith('.json'):
                    try: os.remove(full_path)
                    except OSError: pass

            self._last_content_hash = self._calculate_hash()

    def has_external_changes(self):
        """Checks for external modifications by probing chunks of the active profile."""
        if not os.path.isfile(self.config_file): return False
        try:
            if abs(os.path.getmtime(self.config_file) - self._last_mtimes.get(self.config_file, 0)) > 0.1:
                return True

            safe_active = "".join(c for c in self.active_profile_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
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
        with self._lock:
            if name in self.profiles: return False
            if copy_files or copy_instructions:
                source = self.get_active_profile()
                new_profile = {
                    "selected_files": [dict(f) for f in source.get('selected_files', [])] if copy_files else [],
                    "total_tokens": source.get('total_tokens', 0) if copy_files else 0,
                    "intro_text": source.get('intro_text', '') if copy_instructions else '',
                    "outro_text": source.get('outro_text', '') if copy_instructions else '',
                    "expanded_dirs": source.get('expanded_dirs', [])[:] if copy_files else [],
                    "unknown_files": source.get('unknown_files', [])[:] if copy_files else []
                }
            else: new_profile = self._create_empty_profile()
            self.profiles[name] = new_profile
            return True

    def delete_profile(self, profile_name_to_delete):
        with self._lock:
            if profile_name_to_delete == "Default" or profile_name_to_delete not in self.profiles:
                return False
            del self.profiles[profile_name_to_delete]
            if self.active_profile_name == profile_name_to_delete:
                self.active_profile_name = "Default"
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