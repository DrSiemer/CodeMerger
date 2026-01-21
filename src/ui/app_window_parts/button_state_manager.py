import os
from ... import constants as c

class ButtonStateManager:
    """Handles updating the state of buttons and UI elements in the main window."""
    def __init__(self, app):
        """
        Initializes the ButtonStateManager.
        Args:
            app: The main App instance.
        """
        self.app = app

    def update_button_states(self, *args):
        """Updates button states based on the active directory and .allcode file."""
        app = self.app
        active_dir_path = app.active_dir.get()
        is_loading = active_dir_path == "Loading..."
        is_dir_active = os.path.isdir(active_dir_path)
        dir_dependent_state = 'normal' if is_dir_active else 'disabled'
        project_config = app.project_manager.get_current_project()

        # Handle the loading state for the Select Project button
        if is_loading:
            app.select_project_button.set_state('disabled')
        else:
            app.select_project_button.set_state('normal')  # Re-enable the button first
            if is_dir_active:
                app.select_project_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            else:
                app.select_project_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)

        app.manage_files_button.set_state(dir_dependent_state)

        # Update Manage Files button appearance based on token limit
        token_limit = app.app_state.config.get('token_limit', 0)
        current_tokens = project_config.total_tokens if project_config else 0

        if is_dir_active and token_limit > 0 and current_tokens > token_limit:
            app.manage_files_button.config(bg=c.WARN, fg='#FFFFFF') # Red bg
            app.manage_files_tooltip.text = f"Token limit exceeded!\nCurrent: {current_tokens:,}\nLimit: {token_limit:,}"
        else:
            app.manage_files_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            app.manage_files_tooltip.text = "Manage project files"

        # --- Check for Start Work File ---
        has_start_file = False
        if is_dir_active:
            start_file_path = os.path.join(active_dir_path, c.START_WORK_FILENAME)
            has_start_file = os.path.exists(start_file_path)

        if has_start_file:
            app.start_work_button.grid(row=0, column=1, padx=(10, 0))
        else:
            app.start_work_button.grid_remove()

        if is_dir_active:
            app.folder_icon_label.grid(row=0, column=1, sticky='e', padx=(10, 0))
            # Generate the masked logo image and apply it to the label
            app.masked_logo_tk = app.assets.create_masked_logo(app.project_color)
            app.color_swatch.config(image=app.masked_logo_tk, bg=c.TOP_BAR_BG)
            if not app.color_swatch.winfo_ismapped():
                 app.color_swatch.pack(side='left', padx=(0, 15), before=app.title_container)
        else:
             app.folder_icon_label.grid_forget()
             if app.color_swatch.winfo_ismapped():
                app.color_swatch.pack_forget()

        if not is_dir_active:
            app.wrapper_box_title.pack_forget()
            app.button_grid_frame.pack_forget()
            app.no_project_label.pack(pady=(20, 30), padx=30)
            app.wrapper_text_button.set_state('disabled')
            app.copy_merged_button.set_state('disabled')
            app.copy_wrapped_button.set_state('disabled')
            app.paste_changes_button.set_state('disabled')
            app.cleanup_comments_button.place_forget()
        else:
            app.no_project_label.pack_forget()
            app.wrapper_box_title.pack(pady=(10, 5))
            app.button_grid_frame.pack(pady=(5, 18), padx=30)
            app.wrapper_text_button.set_state('normal')
            app.paste_changes_button.set_state('normal')
            app.cleanup_comments_button.place(relx=1.0, y=14, anchor='ne', x=-22)

            copy_buttons_state = 'disabled'
            has_wrapper_text = False

            if project_config:
                if project_config.selected_files:
                    copy_buttons_state = 'normal'
                intro = project_config.intro_text
                outro = project_config.outro_text
                if intro or outro:
                    has_wrapper_text = True

            app.copy_merged_button.set_state(copy_buttons_state)
            app.copy_wrapped_button.set_state(copy_buttons_state)

            app.copy_wrapped_button.grid_remove()
            app.copy_merged_button.grid_remove()
            app.wrapper_text_button.grid_remove()
            app.paste_changes_button.grid_remove()

            gap = 5

            if has_wrapper_text:
                # Row 0: Both large copy buttons
                app.copy_wrapped_button.grid(row=0, column=0, sticky='ew', pady=(0, 5), padx=(0, gap))
                app.copy_merged_button.grid(row=0, column=1, sticky='ew', pady=(0, 5), padx=(gap, 0))
            else:
                # Row 0: The single large copy button spans the full width
                app.copy_merged_button.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5), padx=0)

            # Row 1: Small configuration buttons
            app.wrapper_text_button.grid(row=1, column=0, sticky='ew', padx=(0, gap))
            app.paste_changes_button.grid(row=1, column=1, sticky='ew', padx=(gap, 0))