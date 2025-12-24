import os
from ...core.utils import get_file_hash, get_token_count_for_text
from ... import constants as c

class FileManagerDataController:
    def __init__(self, window):
        self.window = window

    def validate_and_update_cache(self):
        cache_was_updated = False
        for file_info in self.window.project_config.selected_files:
            path = file_info.get('path')
            if not path: continue
            full_path = os.path.join(self.window.base_dir, path)
            if self._needs_recalculation(file_info, full_path):
                self._recalculate_stats(file_info, full_path)
                cache_was_updated = True
        if cache_was_updated:
            self.window.project_config.save()
            self.window.status_var.set("File cache updated for modified files.")

    def _needs_recalculation(self, file_info, full_path):
        if 'tokens' not in file_info or 'lines' not in file_info:
            return True
        if self.window.token_count_enabled and file_info.get('tokens', -1) == 0:
            try:
                if os.path.getsize(full_path) > 0: return True
            except OSError: return False
        try:
            current_mtime = os.path.getmtime(full_path)
            if current_mtime != file_info.get('mtime'): return True
            current_hash = get_file_hash(full_path)
            if current_hash is not None and current_hash != file_info.get('hash'): return True
        except OSError:
            return False
        return False

    def _recalculate_stats(self, file_info, full_path):
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            file_info['mtime'] = os.path.getmtime(full_path)
            file_info['hash'] = get_file_hash(full_path)
            if self.window.token_count_enabled:
                file_info['tokens'] = get_token_count_for_text(content)
                file_info['lines'] = content.count('\n') + 1
            else:
                file_info['tokens'], file_info['lines'] = 0, 0
        except (OSError, IOError):
            file_info['tokens'], file_info['lines'] = -1, -1

    def run_token_recalculation(self):
        if self.window.token_count_enabled:
            total_tokens = sum(f.get('tokens', 0) for f in self.window.selection_handler.ordered_selection)
            self._update_title(total_tokens)
        else:
            self._update_title(None)

    def _update_title(self, total_tokens):
        num_files = len(self.window.selection_handler.ordered_selection)
        file_text = "files" if num_files != 1 else "file"
        details_text = f"({num_files} {file_text} selected)"
        label_fg = c.TEXT_SUBTLE_COLOR
        tooltip_text = ""

        if total_tokens is not None:
            self.window.current_total_tokens = total_tokens
            if total_tokens >= 0:
                formatted_tokens = f"{total_tokens:,}".replace(',', '.')
                details_text = f"({num_files} {file_text} selected, {formatted_tokens} tokens)"

                # Check thresholds
                token_limit = self.window.app_state.config.get('token_limit', 0)

                if token_limit > 0 and total_tokens > token_limit:
                    label_fg = c.WARN
                    tooltip_text = f"Token limit exceeded! (Limit: {token_limit:,})"
                elif total_tokens > c.TOKEN_THRESHOLD_WARNING:
                    label_fg = c.WARN
                    tooltip_text = c.TOKEN_THRESHOLD_WARNING_TEXT
            else:
                details_text = f"({num_files} {file_text} selected, token count error)"
        else:
            self.window.current_total_tokens = 0

        self.window.merge_order_details_label.config(text=details_text, fg=label_fg)
        if hasattr(self.window, 'token_count_tooltip'):
            self.window.token_count_tooltip.text = tooltip_text