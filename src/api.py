from src.api_parts.base_api import BaseApi
from src.api_parts.window_api import WindowApi
from src.api_parts.config_api import ConfigApi
from src.api_parts.project_api import ProjectApi
from src.api_parts.file_api import FileApi
from src.api_parts.clipboard_api import ClipboardApi
from src.api_parts.changes_api import ChangesApi
from src.api_parts.starter_api import StarterApi

class Api(
    WindowApi,
    ConfigApi,
    ProjectApi,
    FileApi,
    ClipboardApi,
    ChangesApi,
    StarterApi,
    BaseApi
):
    """
    The Python API bridge exposed to the Vue 3 frontend via PyWebView.
    Methods defined here can be called directly from JavaScript using `window.pywebview.api.method_name()`.
    """
    def __init__(self, app_state, project_manager):
        BaseApi.__init__(self, app_state, project_manager)