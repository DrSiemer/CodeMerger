import os
import sys
from PIL import ImageFont

# --- Robust Font Finding Logic ---
WINDOWS_FONT_MAP = {
    "segoe ui": ["segoeui.ttf", "seguisb.ttf", "seguili.ttf"],
    "calibri": ["calibri.ttf", "calibrib.ttf"],
    "helvetica": ["helvetica.ttf", "helveticab.ttf"],
    "arial": ["arial.ttf", "arialbd.ttf"],
}
FONT_FALLBACK_ORDER = ["Calibri", "Helvetica", "Arial"]
def get_pil_font(font_tuple):
    """
    Tries to find and load a requested font, with a prioritized list of
    fallbacks for cross-platform compatibility.
    """
    requested_family, font_size = font_tuple
    # Create a dynamic search list, starting with the requested font
    search_list = [requested_family] + [f for f in FONT_FALLBACK_ORDER if f.lower() != requested_family.lower()]
    for family in search_list:
        normalized_family = family.lower()
        # On Windows, search the system Fonts directory with known filenames
        if sys.platform == "win32" and normalized_family in WINDOWS_FONT_MAP:
            font_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts")
            for font_file in WINDOWS_FONT_MAP[normalized_family]:
                path = os.path.join(font_dir, font_file)
                if os.path.exists(path):
                    try:
                        return ImageFont.truetype(path, font_size)
                    except IOError:
                        continue # Try the next variant
        # Generic fallback for other systems or if the direct path search fails
        try:
            # Pillow can often find system fonts by name
            return ImageFont.truetype(family, font_size)
        except IOError:
            try:
                # Or by common filename conventions
                return ImageFont.truetype(f"{normalized_family}.ttf", font_size)
            except IOError:
                continue # Font not found, try the next one in the list
    # If none of the preferred fonts are found, use the absolute default
    return ImageFont.load_default()