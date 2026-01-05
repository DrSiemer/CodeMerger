from tkinter import messagebox
from ..new_profile_dialog import NewProfileDialog

class ProfileActions:
    def __init__(self, app):
        self.app = app

    def update_profile_selector_ui(self):
        """Refreshes the profile navigator and buttons based on project state."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        profile_frame = app.profile_frame
        profile_frame.grid_rowconfigure(0, weight=1)

        # Clear existing layout
        for widget in profile_frame.winfo_children():
            widget.grid_forget()

        if not project_config:
            app.add_profile_button.set_state('disabled')
            return

        app.add_profile_button.set_state('normal')
        profile_names = project_config.get_profile_names()
        active_name = project_config.active_profile_name

        if len(profile_names) > 1:
            # Multi-profile layout
            profile_frame.grid_columnconfigure(0, weight=1)
            profile_frame.grid_columnconfigure(1, weight=0)
            profile_frame.grid_columnconfigure(2, weight=0)
            profile_frame.grid_columnconfigure(3, weight=0, minsize=25)
            profile_frame.grid_columnconfigure(4, weight=1)

            app.profile_navigator.grid(row=0, column=1, sticky='e')
            app.profile_navigator.set_profiles(profile_names, active_name)
            app.add_profile_button.grid(row=0, column=2, sticky='w', padx=(10, 0))

            if active_name != "Default":
                app.delete_profile_button.grid(row=0, column=3, sticky='w', padx=(5, 0))
        else:
            # Single-profile layout (only show + button)
            profile_frame.grid_columnconfigure(0, weight=0)
            profile_frame.grid_columnconfigure(1, weight=1)
            for i in range(2, 5):
                profile_frame.grid_columnconfigure(i, weight=0, minsize=0)
            app.add_profile_button.grid(row=0, column=0, sticky='w', padx=(10, 0))

    def on_profile_switched(self, new_profile_name):
        """Switches the active profile and refreshes independent file tracking."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        if new_profile_name != project_config.active_profile_name:
            project_config.active_profile_name = new_profile_name
            project_config.save()
            app.status_var.set(f"Switched to profile: {new_profile_name}")

            # --- Reset Independent File Tracking ---
            # Clear the monitor's local cache so it pulls the
            # new profile's specific 'unknown_files' list.
            app.file_monitor.newly_detected_files = []
            app.file_monitor.perform_new_file_check(schedule_next=True)

            app.button_manager.update_button_states()

        self.update_profile_selector_ui()
        app.focus_set()

    def open_new_profile_dialog(self, event=None):
        """Opens dialog to create a new profile with independent file tracking."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        dialog = NewProfileDialog(
            parent=app,
            existing_profile_names=project_config.get_profile_names()
        )
        result = dialog.result

        if result:
            new_name = result['name']
            copy_files = result['copy_files']
            copy_instructions = result['copy_instructions']

            if project_config.create_new_profile(new_name, copy_files, copy_instructions):
                project_config.active_profile_name = new_name
                project_config.save()

                # Rescan for the new profile
                app.file_monitor.newly_detected_files = []
                app.file_monitor.perform_new_file_check(schedule_next=True)

                self.update_profile_selector_ui()
                app.button_manager.update_button_states()
                app.status_var.set(f"Created and switched to profile: {new_name}")
            else:
                app.status_var.set(f"Error: Profile '{new_name}' already exists.")

    def delete_current_profile(self, event=None):
        """Deletes the current profile and reverts to Default."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        profile_to_delete = project_config.active_profile_name
        if profile_to_delete == "Default":
            app.status_var.set("Cannot delete the Default profile.")
            return

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the profile '{profile_to_delete}'?\nThis cannot be undone.",
            parent=app
        ):
            if project_config.delete_profile(profile_to_delete):
                project_config.active_profile_name = "Default"
                project_config.save()

                # Re-sync tracking to the Default profile
                app.file_monitor.newly_detected_files = []
                app.file_monitor.perform_new_file_check(schedule_next=True)

                app.status_var.set(f"Profile '{profile_to_delete}' deleted.")
                self.update_profile_selector_ui()
                app.button_manager.update_button_states()
            else:
                app.status_var.set(f"Error: Could not delete profile '{profile_to_delete}'.")