import os
from .. import constants as c

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
        is_dir_active = os.path.isdir(app.active_dir.get())
        dir_dependent_state = 'normal' if is_dir_active else 'disabled'
        project_config = app.project_manager.get_current_project()

        if is_dir_active:
            app.select_project_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        else:
            app.select_project_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)

        app.manage_files_button.set_state(dir_dependent_state)
        app.compact_mode_button.set_state(dir_dependent_state)

        if is_dir_active:
            app.folder_icon_label.grid(row=0, column=1, sticky='e', padx=(10, 0))
            app.color_swatch.config(bg=app.project_color)
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
        else:
            app.no_project_label.pack_forget()
            app.wrapper_box_title.pack(pady=(10, 5))
            app.button_grid_frame.pack(pady=(5, 18), padx=30)
            app.wrapper_text_button.set_state('normal')

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

            if has_wrapper_text:
                gap = 5
                app.wrapper_text_button.grid(row=0, column=0, columnspan=1, sticky='ew', pady=(0, 5), padx=(0, gap))
                app.copy_wrapped_button.grid(row=1, column=0, sticky='ew', padx=(0, gap))
                app.copy_merged_button.grid(row=1, column=1, sticky='ew', padx=(gap, 0))
            else:
                app.wrapper_text_button.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5), padx=0)
                app.copy_merged_button.grid(row=1, column=0, columnspan=2, sticky='ew', padx=0)