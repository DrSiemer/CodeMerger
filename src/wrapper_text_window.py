import os
import json
from tkinter import Toplevel, Frame, Label, Button, Text, Scrollbar
from .paths import ICON_PATH

class WrapperTextWindow(Toplevel):
    def __init__(self, parent, base_dir, status_var, on_close_callback=None):
        super().__init__(parent)
        self.base_dir = base_dir
        self.status_var = status_var
        self.on_close_callback = on_close_callback

        self.allcode_path = os.path.join(self.base_dir, '.allcode')
        self.project_data = self._load_project_data()

        # --- Window Setup ---
        self.title("Set Wrapper Text")
        self.iconbitmap(ICON_PATH)
        self.geometry("700x500") # A more compact default size
        self.transient(parent)
        self.grab_set()

        # --- UI Layout ---
        main_frame = Frame(self, padx=15, pady=15)
        main_frame.pack(fill='both', expand=True)

        # --- Action Buttons (pack to bottom first to ensure visibility) ---
        button_frame = Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        self.save_button = Button(button_frame, text="Save and Close", command=self.save_and_close)
        self.save_button.pack(side='right')

        # --- Container for text fields that will use grid for equal sizing ---
        fields_container = Frame(main_frame)
        fields_container.pack(fill='both', expand=True)

        # Configure the grid to give equal vertical space to the two text areas
        fields_container.rowconfigure(0, weight=1)
        fields_container.rowconfigure(1, weight=1)
        fields_container.columnconfigure(0, weight=1)

        # --- Intro Text Section ---
        intro_frame = Frame(fields_container)
        intro_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        Label(intro_frame, text="Intro Text (prepended to the final output):", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        intro_text_frame = Frame(intro_frame, bd=1, relief='sunken')
        intro_text_frame.pack(fill='both', expand=True)
        self.intro_text = Text(intro_text_frame, wrap='word', undo=True, height=5) # height is now a suggestion
        intro_scroll = Scrollbar(intro_text_frame, command=self.intro_text.yview)
        self.intro_text.config(yscrollcommand=intro_scroll.set)
        intro_scroll.pack(side='right', fill='y')
        self.intro_text.pack(side='left', fill='both', expand=True)

        # --- Outro Text Section ---
        outro_frame = Frame(fields_container)
        outro_frame.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        Label(outro_frame, text="Outro Text (appended to the final output):", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        outro_text_frame = Frame(outro_frame, bd=1, relief='sunken')
        outro_text_frame.pack(fill='both', expand=True)
        self.outro_text = Text(outro_text_frame, wrap='word', undo=True, height=5) # height is now a suggestion
        outro_scroll = Scrollbar(outro_text_frame, command=self.outro_text.yview)
        self.outro_text.config(yscrollcommand=outro_scroll.set)
        outro_scroll.pack(side='right', fill='y')
        self.outro_text.pack(side='left', fill='both', expand=True)

        # --- Populate Text Fields ---
        self.intro_text.insert('1.0', self.project_data.get('intro_text', ''))
        self.outro_text.insert('1.0', self.project_data.get('outro_text', ''))

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _load_project_data(self):
        """Loads data from the .allcode file, creating it if it doesn't exist"""
        if os.path.isfile(self.allcode_path):
            try:
                with open(self.allcode_path, 'r', encoding='utf-8-sig') as f:
                    # Handle empty file case
                    content = f.read()
                    if not content:
                        return {}
                    return json.loads(content)
            except (json.JSONDecodeError, IOError):
                return {} # Return empty if corrupt or unreadable
        return {} # Return empty if it doesn't exist

    def save_and_close(self):
        """Saves the intro/outro text to the .allcode file and closes the window"""
        # Build the dictionary in the desired order to control the JSON output
        final_data = {
            "expanded_dirs": self.project_data.get('expanded_dirs', []),
            "selected_files": self.project_data.get('selected_files', []),
            "total_tokens": self.project_data.get('total_tokens', 0),
            "intro_text": self.intro_text.get('1.0', 'end-1c').strip(),
            "outro_text": self.outro_text.get('1.0', 'end-1c').strip()
        }

        try:
            with open(self.allcode_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2)
            self.status_var.set("Wrapper text saved successfully.")
        except IOError as e:
            self.status_var.set(f"Error saving wrapper text: {e}")

        if self.on_close_callback:
            self.on_close_callback()

        self.destroy()