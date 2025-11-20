import os
from PIL import Image, ImageTk, ImageColor
from ..core.paths import (
    TRASH_ICON_PATH, NEW_FILES_ICON_PATH, DEFAULTS_ICON_PATH,
    LOGO_MASK_PATH, LOGO_MASK_SMALL_PATH, ICON_PATH,
    COMPACT_MODE_CLOSE_ICON_PATH,
    FOLDER_ICON_PATH, FOLDER_REVEAL_ICON_PATH, PATHS_ICON_PATH, PATHS_ACTIVE_ICON_PATH,
    EXTRA_FILES_ICON_PATH, EXTRA_FILES_ICON_ACTIVE_PATH, ORDER_REQUEST_ICON_PATH,
    GIT_FILES_ICON_PATH, GIT_FILES_ACTIVE_ICON_PATH,
    SETTINGS_ICON_PATH, FILETYPES_ICON_PATH, SETTINGS_ICON_ACTIVE_PATH, FILETYPES_ICON_ACTIVE_PATH,
    PROJECT_STARTER_ICON_PATH, PROJECT_STARTER_ACTIVE_ICON_PATH, START_WORK_ICON_PATH, START_WORK_ACTIVE_ICON_PATH
)

class AppAssets:
    """A central class to load and hold all application image assets."""
    def __init__(self):
        self.logo_mask_cache = {}
        self.logo_mask_small_cache = {}
        self.logo_mask_pil = self._load_image(LOGO_MASK_PATH, (48, 48)) if os.path.exists(LOGO_MASK_PATH) else None
        self.logo_mask_small_pil = self._load_image(LOGO_MASK_SMALL_PATH, (28, 28)) if os.path.exists(LOGO_MASK_SMALL_PATH) else None

        # Load main icons
        self.compact_icon_pil = self._load_image(ICON_PATH, (12, 12))
        self.trash_icon_pil = self._load_image(TRASH_ICON_PATH, (18, 18))
        self.new_files_pil = self._load_image(NEW_FILES_ICON_PATH, (24, 24))
        self.new_files_compact_pil = self._load_image(NEW_FILES_ICON_PATH, (12, 12))
        self.defaults_pil = self._load_image(DEFAULTS_ICON_PATH, (24, 24))
        self.folder_icon_pil = self._load_image(FOLDER_ICON_PATH, (28, 22))
        self.folder_reveal_pil = self._load_image(FOLDER_REVEAL_ICON_PATH)
        self.paths_icon_pil = self._load_image(PATHS_ICON_PATH, (16, 12))
        self.paths_icon_active_pil = self._load_image(PATHS_ACTIVE_ICON_PATH, (16, 12))
        self.order_request_pil = self._load_image(ORDER_REQUEST_ICON_PATH, (14, 12))
        self.git_files_icon_pil = self._load_image(GIT_FILES_ICON_PATH, (20, 10))
        self.git_files_icon_active_pil = self._load_image(GIT_FILES_ACTIVE_ICON_PATH, (20, 10))
        self.filter_icon_pil = self._load_image(EXTRA_FILES_ICON_PATH, (20, 10))
        self.filter_icon_active_pil = self._load_image(EXTRA_FILES_ICON_ACTIVE_PATH, (20, 10))
        self.settings_icon_pil = self._load_image(SETTINGS_ICON_PATH, (30, 30))
        self.filetypes_icon_pil = self._load_image(FILETYPES_ICON_PATH, (30, 30))
        self.settings_icon_active_pil = self._load_image(SETTINGS_ICON_ACTIVE_PATH, (30, 30))
        self.filetypes_icon_active_pil = self._load_image(FILETYPES_ICON_ACTIVE_PATH, (30, 30))

        # New Project Starter Icons
        self.project_starter_pil = self._load_image(PROJECT_STARTER_ICON_PATH, (29, 29))
        self.project_starter_active_pil = self._load_image(PROJECT_STARTER_ACTIVE_ICON_PATH, (28, 28))
        self.start_work_pil = self._load_image(START_WORK_ICON_PATH, (30, 30))
        self.start_work_active_pil = self._load_image(START_WORK_ACTIVE_ICON_PATH, (30, 30))

        self.compact_mode_close_pil = self._load_image(COMPACT_MODE_CLOSE_ICON_PATH)

        # Placeholders for Tk images
        self.trash_icon_image = self.trash_icon_pil
        self.compact_icon_tk = None
        self.new_files_icon = None
        self.defaults_icon = None
        self.folder_icon = None
        self.folder_reveal_icon = None
        self.paths_icon = None
        self.paths_icon_active = None
        self.order_request_icon = None
        self.git_files_icon = None
        self.git_files_icon_active = None
        self.filter_icon = None
        self.filter_icon_active = None
        self.compact_mode_close_image = None
        self.settings_icon = None
        self.filetypes_icon = None
        self.settings_icon_active = None
        self.filetypes_icon_active = None
        self.project_starter_icon = None
        self.project_starter_active_icon = None
        self.start_work_icon = None
        self.start_work_active_icon = None

    def load_tk_images(self):
        """
        Converts the loaded PIL images into Tkinter PhotoImage objects.
        This method MUST be called after the Tk() root window has been created.
        """
        self.compact_icon_tk = self._pil_to_photoimage(self.compact_icon_pil)
        self.new_files_icon = self._pil_to_photoimage(self.new_files_pil)
        self.defaults_icon = self._pil_to_photoimage(self.defaults_pil)
        self.folder_icon = self._pil_to_photoimage(self.folder_icon_pil)
        self.folder_reveal_icon = self._pil_to_photoimage(self.folder_reveal_pil)
        self.paths_icon = self._pil_to_photoimage(self.paths_icon_pil)
        self.paths_icon_active = self._pil_to_photoimage(self.paths_icon_active_pil)
        self.order_request_icon = self._pil_to_photoimage(self.order_request_pil)
        self.git_files_icon = self._pil_to_photoimage(self.git_files_icon_pil)
        self.git_files_icon_active = self._pil_to_photoimage(self.git_files_icon_active_pil)
        self.filter_icon = self._pil_to_photoimage(self.filter_icon_pil)
        self.filter_icon_active = self._pil_to_photoimage(self.filter_icon_active_pil)
        self.compact_mode_close_image = self._pil_to_photoimage(self.compact_mode_close_pil)
        self.settings_icon = self._pil_to_photoimage(self.settings_icon_pil)
        self.filetypes_icon = self._pil_to_photoimage(self.filetypes_icon_pil)
        self.settings_icon_active = self._pil_to_photoimage(self.settings_icon_active_pil)
        self.filetypes_icon_active = self._pil_to_photoimage(self.filetypes_icon_active_pil)
        self.project_starter_icon = self._pil_to_photoimage(self.project_starter_pil)
        self.project_starter_active_icon = self._pil_to_photoimage(self.project_starter_active_pil)
        self.start_work_icon = self._pil_to_photoimage(self.start_work_pil)
        self.start_work_active_icon = self._pil_to_photoimage(self.start_work_active_pil)

    def create_masked_logo(self, color_hex):
        """Creates a PhotoImage by using the logo's alpha channel as a mask for the project color."""
        if color_hex in self.logo_mask_cache:
            return self.logo_mask_cache[color_hex]

        if not self.logo_mask_pil:
            try:
                img = Image.new('RGB', (48, 48), color_hex)
                return ImageTk.PhotoImage(img)
            except ValueError:
                return None

        try:
            color_img = Image.new("RGBA", self.logo_mask_pil.size, color_hex)
            alpha_mask = self.logo_mask_pil.getchannel('A')
            result_img = Image.new("RGBA", self.logo_mask_pil.size, (0, 0, 0, 0))
            result_img.paste(color_img, (0, 0), alpha_mask)
            result_tk = ImageTk.PhotoImage(result_img)
            self.logo_mask_cache[color_hex] = result_tk
            return result_tk
        except (ValueError, AttributeError, IndexError):
            img = Image.new('RGB', (48, 48), "#FF0000")
            return ImageTk.PhotoImage(img)

    def create_masked_logo_small(self, color_hex):
        """Creates a smaller (28x28) PhotoImage for the project selector."""
        if color_hex in self.logo_mask_small_cache:
            return self.logo_mask_small_cache[color_hex]

        if not self.logo_mask_small_pil:
            try:
                img = Image.new('RGB', (28, 28), color_hex)
                result_tk = ImageTk.PhotoImage(img)
                self.logo_mask_small_cache[color_hex] = result_tk
                return result_tk
            except ValueError:
                return None

        try:
            color_img = Image.new("RGBA", self.logo_mask_small_pil.size, color_hex)
            alpha_mask = self.logo_mask_small_pil.getchannel('A')
            result_img = Image.new("RGBA", self.logo_mask_small_pil.size, (0, 0, 0, 0))
            result_img.paste(color_img, (0, 0), alpha_mask)
            result_tk = ImageTk.PhotoImage(result_img)
            self.logo_mask_small_cache[color_hex] = result_tk
            return result_tk
        except (ValueError, AttributeError, IndexError):
            img = Image.new('RGB', (28, 28), "#FF0000")
            return ImageTk.PhotoImage(img)

    def _load_image(self, path, resize=None):
        try:
            img = Image.open(path)
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
            return img
        except Exception:
            # Fallback blank image
            return Image.new('RGB', resize if resize else (16, 16), '#444444')

    def _pil_to_photoimage(self, pil_image):
        if pil_image:
            return ImageTk.PhotoImage(pil_image)
        return None

assets = AppAssets()