from PIL import Image, ImageTk
from ..core.paths import (
    TRASH_ICON_PATH, NEW_FILES_ICON_PATH, DEFAULTS_ICON_PATH,
    COMPACT_MODE_ICON_PATH, COMPACT_MODE_ACTIVE_ICON_PATH, COMPACT_MODE_CLOSE_ICON_PATH,
    FOLDER_ICON_PATH, PATHS_ICON_PATH, PATHS_ACTIVE_ICON_PATH
)

class AppAssets:
    """A central class to load and hold all application image assets."""
    def __init__(self):
        self.trash_icon_pil = self._load_image(TRASH_ICON_PATH, (18, 18))
        self.new_files_pil = self._load_image(NEW_FILES_ICON_PATH, (24, 24))
        self.defaults_pil = self._load_image(DEFAULTS_ICON_PATH, (24, 24))
        self.folder_icon_pil = self._load_image(FOLDER_ICON_PATH, (28, 22))
        self.paths_icon_pil = self._load_image(PATHS_ICON_PATH, (16, 12))
        self.paths_icon_active_pil = self._load_image(PATHS_ACTIVE_ICON_PATH, (16, 12))

        button_size = (64, 64)
        self.compact_mode_pil_up = self._load_image(COMPACT_MODE_ICON_PATH, button_size)
        self.compact_mode_pil_down = self._load_image(COMPACT_MODE_ACTIVE_ICON_PATH, button_size)
        self.compact_mode_close_pil = self._load_image(COMPACT_MODE_CLOSE_ICON_PATH)

        self.trash_icon_image = self.trash_icon_pil 
        self.new_files_icon = None
        self.defaults_icon = None
        self.folder_icon = None
        self.paths_icon = None
        self.paths_icon_active = None
        self.compact_mode_image_up = None
        self.compact_mode_image_down = None
        self.compact_mode_close_image = None

    def load_tk_images(self):
        """
        Converts the loaded PIL images into Tkinter PhotoImage objects.
        This method MUST be called after the Tk() root window has been created.
        """
        self.new_files_icon = self._pil_to_photoimage(self.new_files_pil)
        self.defaults_icon = self._pil_to_photoimage(self.defaults_pil)
        self.folder_icon = self._pil_to_photoimage(self.folder_icon_pil)
        self.paths_icon = self._pil_to_photoimage(self.paths_icon_pil)
        self.paths_icon_active = self._pil_to_photoimage(self.paths_icon_active_pil)
        self.compact_mode_image_up = self._pil_to_photoimage(self.compact_mode_pil_up)
        self.compact_mode_image_down = self._pil_to_photoimage(self.compact_mode_pil_down)
        self.compact_mode_close_image = self._pil_to_photoimage(self.compact_mode_close_pil)

    def _load_image(self, path, resize=None):
        try:
            img = Image.open(path)
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
            return img
        except Exception:
            return Image.new('RGB', resize if resize else (16, 16), 'red')

    def _pil_to_photoimage(self, pil_image):
        if pil_image:
            return ImageTk.PhotoImage(pil_image)
        return None

assets = AppAssets()