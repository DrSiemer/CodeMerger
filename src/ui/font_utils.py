import os
import sys
from PIL import ImageFont
from functools import lru_cache

# --- Robust Font Finding Logic ---
WINDOWS_FONT_MAP = {
    "segoe ui": ["segoeui.ttf", "seguisb.ttf", "seguili.ttf"],
    "calibri": ["calibri.ttf", "calibrib.ttf"],
    "helvetica": ["helvetica.ttf", "helveticab.ttf"],
    "arial": ["arial.ttf", "arialbd.ttf"],
}
FONT_FALLBACK_ORDER = ["Calibri", "Helvetica", "Arial"]

@lru_cache(maxsize=128)
def get_pil_font(font_tuple):
    """
    Tries to find and load a requested font, with a prioritized list of
    fallbacks for cross-platform compatibility.
    """
    requested_family, font_size, *style = font_tuple
    is_bold = 'bold' in style

    # Create a dynamic search list, starting with the requested font
    search_list = [requested_family] + [f for f in FONT_FALLBACK_ORDER if f.lower() != requested_family.lower()]

    for family in search_list:
        normalized_family = family.lower()
        # On Windows, search the system Fonts directory with known filenames
        if sys.platform == "win32" and normalized_family in WINDOWS_FONT_MAP:
            font_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts")

            variants = WINDOWS_FONT_MAP[normalized_family]
            search_files = [variants[1], variants[0]] if is_bold and len(variants) > 1 else variants

            for font_file in search_files:
                path = os.path.join(font_dir, font_file)
                if os.path.exists(path):
                    try:
                        return ImageFont.truetype(path, font_size)
                    except IOError:
                        continue

        # Generic fallback for other systems
        try:
            return ImageFont.truetype(family, font_size)
        except IOError:
            try:
                # Append 'bd' or similar for bold if path-based fallback is needed
                suffix = "bd" if is_bold else ""
                return ImageFont.truetype(f"{normalized_family}{suffix}.ttf", font_size)
            except IOError:
                continue

    return ImageFont.load_default()