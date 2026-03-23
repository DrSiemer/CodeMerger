from tkinter import messagebox
from ... import constants as c
from . import starter_validator

class StarterNavigation:
    def __init__(self, dialog):
        self.dialog = dialog

    def get_active_steps(self):
        steps = [1]
        if self.dialog.starter_state.project_data["base_project_path"].get():
            steps.append(2)
        steps.extend([3, 4, 5, 6])
        return steps

    def go_to_next_step(self):
        active_steps = self.get_active_steps()
        if self.dialog.starter_state.current_step in active_steps:
            current_idx = active_steps.index(self.dialog.starter_state.current_step)
            if current_idx < len(active_steps) - 1:
                self.go_to_step(active_steps[current_idx + 1])

    def go_to_prev_step(self):
        active_steps = self.get_active_steps()
        if self.dialog.starter_state.current_step in active_steps:
            current_idx = active_steps.index(self.dialog.starter_state.current_step)
            if current_idx > 0:
                self.go_to_step(active_steps[current_idx - 1])

    def go_to_step(self, target_step_id):
        if target_step_id == self.dialog.starter_state.current_step: return
        is_accessible = (target_step_id <= self.dialog.starter_state.max_accessible_step) or (target_step_id == 2)
        if not is_accessible: return

        self.dialog.starter_state.update_from_view(self.dialog.current_view)
        self.dialog.starter_state.save()

        if target_step_id > self.dialog.starter_state.current_step:
            is_valid, err_title, err_msg = starter_validator.validate_step(self.dialog.starter_state.current_step, self.dialog.starter_state.project_data)
            if not is_valid:
                messagebox.showerror(err_title, err_msg, parent=self.dialog)
                return
            self.dialog.starter_state.max_accessible_step = max(self.dialog.starter_state.max_accessible_step, target_step_id)

        self.dialog.starter_state.current_step = target_step_id
        self.dialog._show_current_step_view()

    def update_navigation_controls(self):
        self.dialog.prev_button.pack_forget()
        self.dialog.start_over_button.pack_forget()
        self.dialog.next_button.pack_forget()

        active_steps = self.get_active_steps()
        current_idx = active_steps.index(self.dialog.starter_state.current_step)

        if current_idx < len(active_steps) - 1:
            self.dialog.next_button.pack(side="right")

        can_reset = False
        if self.dialog.current_view:
            if hasattr(self.dialog.current_view, 'is_step_in_progress'):
                can_reset = self.dialog.current_view.is_step_in_progress()
            elif hasattr(self.dialog.current_view, 'is_editor_visible'):
                can_reset = self.dialog.current_view.is_editor_visible()

        if can_reset:
            self.dialog.start_over_button.pack(side="right", padx=(0, 10))

        if current_idx > 0:
            self.dialog.prev_button.pack(side="right", padx=(0, 10))

        self.update_nav_state()

    def update_nav_state(self):
        if self.dialog.starter_state.current_step == 6: return
        self.dialog.next_button.config(text="Next >")

        if self.dialog.starter_state.current_step == 2:
            self.dialog.next_button.set_state('normal')
            self.dialog.next_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.dialog.next_tooltip.text = "Skip or confirm base files and proceed"
            return

        if self.dialog.starter_state.current_step == 4:
            stack_val = self.dialog.starter_state.project_data["stack"].get()
            if not stack_val.strip():
                self.dialog.next_button.config(text="Skip", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
                self.dialog.next_tooltip.text = "Proceed without defining a specific stack"
            else:
                self.dialog.next_button.config(text="Next >", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
                self.dialog.next_tooltip.text = "Confirm stack and proceed to TODO plan"
            self.dialog.next_button.set_state('normal')
            return

        is_valid, _, _ = starter_validator.validate_step(self.dialog.starter_state.current_step, self.dialog.starter_state.project_data)
        if is_valid:
            self.dialog.next_button.set_state('normal')
            self.dialog.next_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.dialog.next_tooltip.text = "Move to the next step"
        else:
            self.dialog.next_button.set_state('disabled')
            self.dialog.next_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.dialog.next_tooltip.text = "Please complete the required fields to continue"