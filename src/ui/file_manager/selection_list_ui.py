import os
from ... import constants as c
from ...core.utils import is_ignored

class SelectionListUI:
    def __init__(self, list_widget, token_count_enabled):
        self.listbox = list_widget
        self.token_count_enabled = token_count_enabled
        self.show_full_paths = False

    def _interpolate_color(self, color1_hex, color2_hex, factor):
        """Linearly interpolates between two hex colors based on a factor from 0.0 to 1.0."""
        r1, g1, b1 = tuple(int(color1_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(color2_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        r = int(r1 + (r2 - r1) * factor); g = int(g1 + (g2 - g1) * factor); b = int(b1 + (b2 - b1) * factor)
        return f'#{r:02x}{g:02x}{b:02x}'

    def _get_color_for_token_count(self, count, min_val, max_val):
        """Calculates a color from a 5-stop gradient based on the token count's position in the range."""
        if min_val >= max_val: return c.TEXT_SUBTLE_COLOR
        p = (count - min_val) / (max_val - min_val)
        colors = [c.TEXT_SUBTLE_COLOR, c.TEXT_SUBTLE_COLOR, c.NOTE, c.ATTENTION, c.WARN]
        if p <= 0: return colors[0]
        if p >= 1: return colors[-1]
        scaled_p = p * (len(colors) - 1)
        idx1 = int(scaled_p)
        idx2 = min(idx1 + 1, len(colors) - 1)
        local_p = scaled_p - idx1
        return self._interpolate_color(colors[idx1], colors[idx2], local_p)

    def toggle_full_path_view(self):
        """Toggles the display of full paths."""
        self.show_full_paths = not self.show_full_paths
        return self.show_full_paths

    def update_list_display(self, ordered_selection, base_dir, file_extensions, gitignore_patterns, is_reorder=False, filter_text="", animate=False):
        """Refreshes the merge order list."""
        items_to_display = ordered_selection
        if filter_text:
            items_to_display = [item for item in ordered_selection if filter_text in item['path'].lower()]

        # Prepare filter logic data
        extensions = {ext for ext in file_extensions if ext.startswith('.')}
        exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}

        min_tokens, max_tokens = 0, c.TOKEN_COLOR_RANGE_MIN_MAX
        if self.token_count_enabled:
            # Filter out ignored files when calculating the range to prevent large files from skewing the gradient
            token_counts = [
                f.get('tokens', 0) for f in items_to_display
                if f.get('tokens', -1) >= 0 and not f.get('ignore_tokens', False)
            ]
            if token_counts:
                min_tokens = min(token_counts)
                max_tokens = max(max(token_counts), c.TOKEN_COLOR_RANGE_MIN_MAX)

        display_items = []
        for file_info in items_to_display:
            path = file_info['path']
            file_name = os.path.basename(path)
            display_text = path if self.show_full_paths else file_name

            # --- Filter Check Logic ---
            file_name_lower = file_name.lower()
            file_ext = os.path.splitext(file_name_lower)[1]

            is_valid_ext = file_ext in extensions or file_name_lower in exact_filenames
            is_git_ignored = is_ignored(os.path.join(base_dir, path), base_dir, gitignore_patterns)

            # If it's ignored by Git OR has an unsupported extension, it's "filtered"
            is_filtered = is_git_ignored or (not is_valid_ext)
            left_col_color = c.TEXT_FILTERED_COLOR if is_filtered else c.TEXT_COLOR
            # --------------------------

            right_col_text, right_col_color = "", c.TEXT_SUBTLE_COLOR
            if self.token_count_enabled:
                token_count = file_info.get('tokens', -1)
                is_ignored_token = file_info.get('ignore_tokens', False)

                if token_count >= 0:
                    if is_ignored_token:
                        right_col_text = f"[{token_count}]"
                        right_col_color = "#666666"
                    else:
                        right_col_text = str(token_count)
                        right_col_color = self._get_color_for_token_count(token_count, min_tokens, max_tokens)
                else:
                    right_col_text = "?"

            display_items.append({
                'left': display_text,
                'left_fg': left_col_color,
                'right': right_col_text,
                'right_fg': right_col_color,
                'data': path
            })

        if is_reorder:
            self.listbox.reorder_and_update(display_items)
        else:
            self.listbox.set_items(display_items)

        if animate:
            self.listbox.animate_pulse()