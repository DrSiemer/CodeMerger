from ..compact_status import CompactStatusToast

class AppHelpers:
    def __init__(self, app):
        self.app = app

    def show_compact_toast(self, message):
        app = self.app
        compact_window = app.view_manager.compact_mode_window
        if compact_window and compact_window.winfo_exists():
            CompactStatusToast(compact_window, message)
        else:
            app.status_var.set(message)

    def animate_loading(self, step=0):
        app = self.app
        dots = (step % 3) + 1
        app.project_title_var.set("Loading" + "." * dots)
        app.loading_animation_job = app.after(400, self.animate_loading, step + 1)

    def stop_loading_animation(self):
        app = self.app
        if app.loading_animation_job:
            app.after_cancel(app.loading_animation_job)
            app.loading_animation_job = None

    def show_and_raise(self):
        app = self.app
        app.deiconify()
        app.lift()
        app.focus_force()

    def show_error_dialog(self, title, message):
        from ..custom_error_dialog import CustomErrorDialog
        CustomErrorDialog(self.app, title, message)