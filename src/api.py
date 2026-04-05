import webview
import os
import logging

log = logging.getLogger("CodeMerger")

class Api:
    """
    The Python API bridge exposed to the Vue 3 frontend via PyWebView.
    Methods defined here can be called directly from JavaScript using `window.pywebview.api.method_name()`.
    """
    def __init__(self):
        # Prefixing with an underscore prevents PyWebView from inspecting this attribute
        # during JS API generation, which avoids a premature DOM evaluation crash.
        self._window = None

    def set_window(self, window):
        """Sets the active PyWebView window reference."""
        self._window = window

    def test(self):
        """A simple test method to verify the Vue -> Python bridge is working."""
        log.info("API test method called from Vue frontend.")
        return "Hello from Python API! The bridge is working perfectly."

    def select_directory(self):
        """
        Opens the native OS directory selection dialog.
        Returns the selected path, or None if cancelled.
        """
        if not self._window:
            log.warning("select_directory called but window reference is missing.")
            return None

        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            selected_path = result[0]
            log.info(f"Directory selected via native dialog: {selected_path}")
            return selected_path

        log.info("Directory selection cancelled.")
        return None