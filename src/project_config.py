import os
import json

class ProjectConfig:
    """
    Manages loading and saving the .allcode configuration for a project directory
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.allcode_path = os.path.join(self.base_dir, '.allcode')
        self.selected_files = []
        self.expanded_dirs = set()
        self.total_tokens = 0
        self.intro_text = ''
        self.outro_text = ''

    def load(self):
        """
        Loads the .allcode config, and crucially, cleans out any references
        to files that no longer exist on the filesystem. Returns True if
        the file list was modified during the cleaning process
        """
        data = {}
        try:
            if os.path.isfile(self.allcode_path):
                with open(self.allcode_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    if content:
                        data = json.loads(content)
        except (json.JSONDecodeError, IOError):
            pass # Treat corrupt/unreadable files as empty

        self.intro_text = data.get('intro_text', '')
        self.outro_text = data.get('outro_text', '')
        self.expanded_dirs = set(data.get('expanded_dirs', []))
        original_selection = data.get('selected_files', [])

        # Filter out files that no longer exist on disk
        cleaned_selection = [
            f for f in original_selection
            if os.path.isfile(os.path.join(self.base_dir, f))
        ]
        self.selected_files = cleaned_selection

        files_were_cleaned = len(cleaned_selection) < len(original_selection)

        if files_were_cleaned:
            self.total_tokens = 0 # Invalidate token count if files are missing
            # Auto-save the cleaned config
            self.save(self.selected_files, self.expanded_dirs, self.total_tokens)
        else:
            # The file list is intact, so the cached token count is trustworthy
            self.total_tokens = data.get('total_tokens', 0)

        return files_were_cleaned

    def save(self, selected_files, expanded_dirs, total_tokens):
        """Saves the configuration to the .allcode file"""
        self.selected_files = selected_files
        self.expanded_dirs = expanded_dirs
        self.total_tokens = total_tokens

        # Build the dictionary in the desired order to control the JSON output
        final_data = {
            "expanded_dirs": sorted(list(self.expanded_dirs)),
            "selected_files": self.selected_files,
            "total_tokens": self.total_tokens,
            "intro_text": self.intro_text,
            "outro_text": self.outro_text
        }
        with open(self.allcode_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)