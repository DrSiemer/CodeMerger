import os
import json
import pyperclip
import time
from tkinter import Tk, Toplevel, Frame, Label, Button, StringVar, messagebox, filedialog, TclError
from PIL import Image, ImageTk

from .utils import load_config, save_config, load_active_file_extensions
from .file_manager import FileManagerWindow
from .filetypes_manager import FiletypesManagerWindow
from .settings_window import SettingsWindow
from .wrapper_text_window import WrapperTextWindow
from .constants import RECENT_DIRS_MAX
from .paths import ICON_PATH, COMPACT_MODE_ICON_PATH, COMPACT_MODE_ACTIVE_ICON_PATH, COMPACT_MODE_CLOSE_ICON_PATH
from .compact_mode import CompactMode

class App(Tk):
    def __init__(self, file_extensions, app_version=""):
        super().__init__()
        self.file_extensions = file_extensions
        self.app_bg_color = '#FFFFFF'

        # Compact Mode State
        self.in_compact_mode = False
        self.is_animating = False
        self.compact_mode_window = None
        self.compact_mode_last_x = None
        self.compact_mode_last_y = None
        self.main_window_geom = None
        self.load_compact_mode_images()

        # Window Setup
        self.title(f"CodeMerger [ {app_version} ]")
        self.iconbitmap(ICON_PATH)
        self.geometry("500x250")
        self.configure(bg=self.app_bg_color)

        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.bind("<Map>", self.on_main_window_restored)

        # Load Configuration & Validate Active Directory
        self.config = load_config()
        self.default_editor = self.config.get('default_editor', '')
        active_dir_path = self.config.get('active_directory', '')

        # Check for existence of the active directory on boot. Reset if not found
        if active_dir_path and not os.path.isdir(active_dir_path):
            self.config['active_directory'] = ''
            save_config(self.config)
            active_dir_path = ''

        self.active_dir = StringVar()
        self.active_dir.trace_add('write', self.update_button_states)

        self.recent_dirs = self.config.get('recent_directories', [])

        # UI Layout
        main_frame = Frame(self, padx=15, pady=15, bg=self.app_bg_color)
        main_frame.pack(fill='both', expand=True)

        # Top Section
        top_frame = Frame(main_frame, bg=self.app_bg_color)
        top_frame.pack(side='top', fill='x')
        dir_label = Label(top_frame, text="Active Directory:", font=('Helvetica', 10, 'bold'), bg=self.app_bg_color)
        dir_label.pack(anchor='w')
        active_dir_display = Label(top_frame, textvariable=self.active_dir, fg="blue", wraplength=450, justify='left', bg=self.app_bg_color)
        active_dir_display.pack(anchor='w', fill='x', pady=(0, 10))
        top_button_frame = Frame(top_frame, bg=self.app_bg_color)
        top_button_frame.pack(fill='x', pady=5)
        self.wrapper_text_button = Button(top_button_frame, text="Wrapper Text", command=self.open_wrapper_text_window)
        self.wrapper_text_button.pack(side='right', padx=(3, 0))
        self.manage_files_button = Button(top_button_frame, text="Manage Files", command=self.manage_files)
        self.manage_files_button.pack(side='right', expand=True, fill='x')
        Button(top_button_frame, text="Select Directory", command=self.open_change_directory_dialog).pack(side='right', expand=True, fill='x', padx=(0, 3))


        # Bottom Config Frame
        config_frame = Frame(main_frame, bg=self.app_bg_color)
        config_frame.pack(side='bottom', fill='x', pady=(5, 0))
        settings_button = Button(config_frame, text="Settings", command=self.open_settings_window, relief='flat', fg='gray')
        settings_button.pack(side='left')
        config_button = Button(config_frame, text="Manage Filetypes", command=self.open_filetypes_manager, relief='flat', fg='gray')
        config_button.pack(side='left', padx=10)
        self.compact_mode_toggle = Button(config_frame, text="Compact Mode", command=self.toggle_compact_mode, relief='flat', fg='gray')
        self.compact_mode_toggle.pack(side='right')

        # Central Copy Buttons
        copy_button_frame = Frame(main_frame, bg=self.app_bg_color)
        copy_button_frame.pack(fill='both', expand=True, pady=10)

        copy_button_frame.grid_rowconfigure(0, weight=1)
        copy_button_frame.grid_columnconfigure(0, weight=1)

        button_row = Frame(copy_button_frame, bg=self.app_bg_color)
        button_row.grid(row=0, column=0, sticky='ew')

        self.copy_wrapped_button = Button(button_row, text="Copy Wrapped", command=self.copy_wrapped_code, font=('Helvetica', 14, 'bold'), pady=5)
        self.copy_wrapped_button.pack(side='left', padx=(0, 5))

        self.copy_merged_button = Button(button_row, text="Copy Merged", command=self.copy_merged_code, font=('Helvetica', 14, 'bold'), pady=5)
        self.copy_merged_button.pack(side='left', expand=True, fill='x', padx=(5, 0))


        # Status bar
        self.status_var = StringVar(value="Ready")
        status_bar = Label(self, textvariable=self.status_var, bd=1, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')

        # Set the active directory
        self.set_active_dir_display(active_dir_path)

    def load_compact_mode_images(self):
        """Loads and prepares the compact mode graphics"""
        try:
            button_size = (64, 64)
            up_img_src = Image.open(COMPACT_MODE_ICON_PATH).resize(button_size, Image.Resampling.LANCZOS)
            self.compact_mode_image_up = ImageTk.PhotoImage(up_img_src)
            down_img_src = Image.open(COMPACT_MODE_ACTIVE_ICON_PATH).resize(button_size, Image.Resampling.LANCZOS)
            self.compact_mode_image_down = ImageTk.PhotoImage(down_img_src)
            close_img_src = Image.open(COMPACT_MODE_CLOSE_ICON_PATH)
            self.compact_mode_close_image = ImageTk.PhotoImage(close_img_src)
        except Exception:
            self.compact_mode_image_up = None
            self.compact_mode_image_down = None
            self.compact_mode_close_image = None

    def on_app_close(self):
        """Safely destroys child windows before closing the main app"""
        if self.compact_mode_window and self.compact_mode_window.winfo_exists():
            self.compact_mode_window.destroy()
        self.destroy()

    def on_main_window_restored(self, event=None):
        """
        Called when the main window is restored. If this happens while in compact
        mode, it means the user wants the main window back, so we exit compact mode.
        The animation flag prevents this from firing during the exit animation itself
        """
        if self.in_compact_mode and not self.is_animating:
            self.toggle_compact_mode()

    def show_and_raise(self):
        """De-minimizes, raises, and focuses the main window"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def set_active_dir_display(self, path):
        """Sets the display string for the active directory's StringVar"""
        if path and os.path.isdir(path):
            self.active_dir.set(path)
        else:
            self.active_dir.set("No directory selected.")

    def update_button_states(self, *args):
        """Updates button states based on the active directory and .allcode file"""
        is_dir_active = os.path.isdir(self.active_dir.get())
        dir_dependent_state = 'normal' if is_dir_active else 'disabled'
        copy_buttons_state = 'disabled'
        has_wrapper_text = False

        if hasattr(self, 'manage_files_button'):
            self.manage_files_button.config(state=dir_dependent_state)
        if hasattr(self, 'wrapper_text_button'):
            self.wrapper_text_button.config(state=dir_dependent_state)

        if is_dir_active:
            allcode_path = os.path.join(self.active_dir.get(), '.allcode')
            if os.path.isfile(allcode_path):
                try:
                    if os.path.getsize(allcode_path) > 0:
                        with open(allcode_path, 'r', encoding='utf-8-sig') as f:
                            data = json.load(f)
                            if data.get('selected_files'):
                                copy_buttons_state = 'normal'
                            # Check for wrapper text
                            intro = data.get('intro_text', '').strip()
                            outro = data.get('outro_text', '').strip()
                            if intro or outro:
                                has_wrapper_text = True
                except (json.JSONDecodeError, IOError):
                    pass

        if hasattr(self, 'copy_merged_button'):
            self.copy_merged_button.config(state=copy_buttons_state)
        if hasattr(self, 'copy_wrapped_button'):
            self.copy_wrapped_button.config(state=copy_buttons_state)

        # Update button layout based on wrapper text
        self.copy_wrapped_button.pack_forget()
        self.copy_merged_button.pack_forget()

        if has_wrapper_text:
            # Show "Copy Wrapped" and adjust "Copy Merged" to original layout
            self.copy_wrapped_button.pack(side='left', padx=(0, 5))
            self.copy_merged_button.pack(side='left', expand=True, fill='x', padx=(5, 0))
        else:
            # Hide "Copy Wrapped" and make "Copy Merged" full-width
            self.copy_merged_button.pack(expand=True, fill='x')

    def _animate_window(self, start_time, duration, start_geom, end_geom, is_shrinking):
        """Helper method to animate the main window's geometry and alpha"""
        self.is_animating = True
        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / duration)

        # Interpolate geometry and alpha
        start_x, start_y, start_w, start_h = start_geom
        end_x, end_y, end_w, end_h = end_geom

        curr_x = int(start_x + (end_x - start_x) * progress)
        curr_y = int(start_y + (end_y - start_y) * progress)
        curr_w = int(start_w + (end_w - start_w) * progress)
        curr_h = int(start_h + (end_h - start_h) * progress)

        # Fade out when shrinking, fade in when expanding
        alpha = 1.0 - progress if is_shrinking else progress
        if not is_shrinking and alpha == 0.0: alpha = 0.01

        self.geometry(f"{max(1, curr_w)}x{max(1, curr_h)}+{curr_x}+{curr_y}")
        try:
            self.attributes("-alpha", alpha)
        except TclError:
            pass

        if progress < 1.0:
            self.after(15, self._animate_window, start_time, duration, start_geom, end_geom, is_shrinking)
        else:
            self.is_animating = False
            if is_shrinking:
                self.withdraw()
                self.attributes("-alpha", 1.0)
                if self.compact_mode_window and self.compact_mode_window.winfo_exists():
                    self.compact_mode_window.deiconify()  # Show the widget
            else:
                self.geometry(f"{end_geom[2]}x{end_geom[3]}+{end_geom[0]}+{end_geom[1]}")
                self.attributes("-alpha", 1.0)
                if self.compact_mode_window and self.compact_mode_window.winfo_exists():
                    self.compact_mode_window.destroy()
                self.compact_mode_window = None

    def toggle_compact_mode(self):
        """Switches the application state between main view and compact mode with animation"""
        if self.is_animating:
            return

        animation_duration = 0.25

        # Exit compact mode: Animate from widget to full window
        if self.in_compact_mode:
            self.in_compact_mode = False
            if not self.compact_mode_window or not self.compact_mode_window.winfo_exists():
                self.show_and_raise()
                return

            # Store compact window's final position for next time
            self.compact_mode_last_x = self.compact_mode_window.winfo_x()
            self.compact_mode_last_y = self.compact_mode_window.winfo_y()

            # Start geometry is the compact widget's geometry
            start_geom = (
                self.compact_mode_window.winfo_x(),
                self.compact_mode_window.winfo_y(),
                self.compact_mode_window.winfo_width(),
                self.compact_mode_window.winfo_height(),
            )

            # End geometry is the main window's stored original geometry
            end_geom = self.main_window_geom

            # Hide compact widget, then show main window (at start position) to begin animation
            self.compact_mode_window.withdraw()
            self.deiconify()
            self.attributes("-alpha", 0.01)
            self.geometry(f"{start_geom[2]}x{start_geom[3]}+{start_geom[0]}+{start_geom[1]}")

            self._animate_window(time.time(), animation_duration, start_geom, end_geom, is_shrinking=False)

        # Enter compact mode: Animate from full window to widget
        else:
            if not self.compact_mode_image_up or not self.compact_mode_close_image:
                messagebox.showerror("Asset Error", "Could not load compact mode graphics.")
                return

            self.in_compact_mode = True

            # Store main window's current geometry to animate from and return to
            self.main_window_geom = (self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height())

            # Create the compact mode window, but keep it hidden for now
            self.compact_mode_window = CompactMode(
                self,
                image_up=self.compact_mode_image_up,
                image_down=self.compact_mode_image_down,
                image_close=self.compact_mode_close_image
            )
            self.compact_mode_window.withdraw()
            self.compact_mode_window.update_idletasks()

            widget_w = self.compact_mode_window.winfo_reqwidth()
            widget_h = self.compact_mode_window.winfo_reqheight()

            # Determine target X, Y for the compact widget
            if self.compact_mode_last_x is not None and self.compact_mode_last_y is not None:
                target_x, target_y = self.compact_mode_last_x, self.compact_mode_last_y
            else:
                # First time: Calculate a smart default position that is on-screen
                screen_w = self.winfo_screenwidth()
                screen_h = self.winfo_screenheight()
                main_x, main_y, main_w, _ = self.main_window_geom

                # Ideal position: top-right of the main window, offset slightly
                ideal_x = main_x + main_w - widget_w - 20
                ideal_y = main_y + 20

                # Clamp the position to be within screen bounds, leaving a small margin
                margin = 10
                target_x = max(margin, min(ideal_x, screen_w - widget_w - margin))
                target_y = max(margin, min(ideal_y, screen_h - widget_h - margin))

            # This is the single source of truth for the animation's destination
            start_geom = self.main_window_geom
            end_geom = (target_x, target_y, widget_w, widget_h)

            # Tell the widget where to appear *after* the animation finishes
            self.compact_mode_window.geometry(f"+{target_x}+{target_y}")

            # Start the animation using the definitive end_geom
            self._animate_window(time.time(), animation_duration, start_geom, end_geom, is_shrinking=True)

    def on_settings_closed(self):
        self.config = load_config()
        self.default_editor = self.config.get('default_editor', '')
        self.status_var.set("Settings updated.")

    def open_settings_window(self):
        SettingsWindow(self, on_close_callback=self.on_settings_closed)

    def open_wrapper_text_window(self):
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid directory first.")
            return
        wt_window = WrapperTextWindow(self, base_dir, self.status_var, on_close_callback=self.update_button_states)
        self.wait_window(wt_window)

    def open_filetypes_manager(self):
        FiletypesManagerWindow(self, on_close_callback=self.reload_active_extensions)

    def reload_active_extensions(self):
        self.file_extensions = load_active_file_extensions()
        self.status_var.set("Filetype configuration updated.")

    def remove_recent_directory(self, path_to_remove):
        if path_to_remove in self.recent_dirs:
            self.recent_dirs.remove(path_to_remove)
            self.config['recent_directories'] = self.recent_dirs
            save_config(self.config)
            self.status_var.set(f"Removed '{os.path.basename(path_to_remove)}' from recent directories.")

    def update_active_dir(self, new_dir):
        if not new_dir or not os.path.isdir(new_dir):
            return
        self.config['active_directory'] = new_dir
        if new_dir in self.recent_dirs:
            self.recent_dirs.remove(new_dir)
        self.recent_dirs.insert(0, new_dir)
        self.recent_dirs = self.recent_dirs[:RECENT_DIRS_MAX]
        self.config['recent_directories'] = self.recent_dirs
        save_config(self.config)
        self.set_active_dir_display(new_dir)
        self.status_var.set(f"Active directory changed to: {os.path.basename(new_dir)}")

    def open_change_directory_dialog(self):
        # Prune non-existent directories first
        initial_count = len(self.recent_dirs)
        self.recent_dirs = [d for d in self.recent_dirs if os.path.isdir(d)]
        if len(self.recent_dirs) != initial_count:
            self.config['recent_directories'] = self.recent_dirs
            save_config(self.config)

        dialog = Toplevel(self)
        dialog.title("Select Directory")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=self.app_bg_color)

        screen_width = self.winfo_screenwidth()
        dialog_width = max(400, min(int(screen_width * 0.5), 800))

        # Determine initial message and height based on whether recent directories exist
        if self.recent_dirs:
            message = "Select a recent directory or browse for a new one."
            dialog_height = 280
        else:
            message = "Browse for a directory to get started."
            dialog_height = 120

        dialog.geometry(f"{dialog_width}x{dialog_height}")
        info_label = Label(dialog, text=message, padx=10, pady=10, bg=self.app_bg_color)
        info_label.pack(pady=(0, 5))

        def select_and_close(path):
            """Final action: update active dir and close the selection dialog"""
            self.update_active_dir(path)
            dialog.destroy()

        def browse_for_new_dir():
            """Opens file dialog and processes the result, handling cancellation"""
            new_path = filedialog.askdirectory(title="Select Project Directory", parent=dialog)
            if new_path:  # Only proceed if a directory was actually selected
                select_and_close(new_path)

        # Create a frame for recent directories; it will be shown or hidden as needed
        recent_dirs_frame = Frame(dialog, bg=self.app_bg_color)

        def remove_and_update_dialog(path_to_remove, widget_to_destroy):
            """Removes a recent directory and dynamically updates the dialog's UI"""
            self.remove_recent_directory(path_to_remove)
            widget_to_destroy.destroy()
            if not self.recent_dirs:
                info_label.config(text="Browse for a directory to get started.")
                dialog.geometry(f"{dialog_width}x120")
                recent_dirs_frame.pack_forget()  # Hide the frame for a clean layout

        # Populate Recent Directories List (if any)
        if self.recent_dirs:
            recent_dirs_frame.pack(fill='x', expand=False, pady=5)
            for path in self.recent_dirs:
                entry_frame = Frame(recent_dirs_frame, bg=self.app_bg_color)
                entry_frame.pack(fill='x', padx=10, pady=2)
                btn = Button(entry_frame, text=path, command=lambda p=path: select_and_close(p), anchor='w', justify='left')
                btn.pack(side='left', expand=True, fill='x')
                remove_btn = Button(entry_frame, text="X", command=lambda p=path, w=entry_frame: remove_and_update_dialog(p, w), width=3)
                remove_btn.pack(side='left', padx=(5, 0))

        # Browse Button
        browse_btn = Button(dialog, text="Browse for Directory...", command=browse_for_new_dir)
        browse_btn.pack(pady=10, padx=10)

    def _perform_copy(self, use_wrapper: bool):
        """
        Core logic for merging files and copying to clipboard.
        Can operate in 'merged' or 'wrapped' mode
        """
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid directory first.")
            self.status_var.set("Error: Invalid directory.")
            return

        config_path = os.path.join(base_dir, '.allcode')
        if not os.path.isfile(config_path):
            messagebox.showerror("Error", f"No .allcode file found in {base_dir}")
            self.status_var.set("Error: .allcode file not found.")
            return

        try:
            with open(config_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

            final_ordered_list = data.get('selected_files', [])
            if not final_ordered_list:
                self.status_var.set("No files selected to copy.")
                return

            output_blocks = []
            skipped_files = []
            for path in final_ordered_list:
                full_path = os.path.join(base_dir, path)
                if not os.path.isfile(full_path):
                    skipped_files.append(path)
                    continue
                with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as code_file:
                    content = code_file.read()
                output_blocks.append(f'--- {path} ---\n```\n{content}\n```')

            merged_code = '\n\n\n'.join(output_blocks)

            if use_wrapper:
                intro_text = data.get('intro_text', '').strip()
                outro_text = data.get('outro_text', '').strip()
                merged_code_with_header = f"Here's all the relevant code:\n\n{merged_code}"

                final_parts = []
                if intro_text:
                    final_parts.append(intro_text)
                final_parts.append(merged_code_with_header)
                if outro_text:
                    final_parts.append(outro_text)

                final_content = '\n\n\n'.join(final_parts)
                status_message = "Wrapped code copied to clipboard."
            else:
                final_content = f"Here's all the most recent code:\n\n{merged_code}"
                status_message = "Merged code copied to clipboard."

            pyperclip.copy(final_content)

            if skipped_files:
                status_message += f" Skipped {len(skipped_files)} missing file(s)."
            self.status_var.set(status_message)

        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Error", f"Could not read .allcode file. Is it empty or corrupt?\n\nDetails: {e}")
            self.status_var.set("Error: Could not read .allcode file.")
        except Exception as e:
            messagebox.showerror("Merging Error", f"An error occurred: {e}")
            self.status_var.set(f"Error during merging: {e}")

    def copy_merged_code(self):
        """Merges selected files (without wrapper text) and copies the result to the clipboard"""
        self._perform_copy(use_wrapper=False)

    def copy_wrapped_code(self):
        """Merges selected files with wrapper text and copies the result to the clipboard"""
        self._perform_copy(use_wrapper=True)

    def manage_files(self):
        base_dir = self.active_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Error", "Please select a valid directory first.")
            return
        fm_window = FileManagerWindow(self, base_dir, self.status_var, self.file_extensions, self.default_editor)
        self.wait_window(fm_window)
        self.update_button_states()