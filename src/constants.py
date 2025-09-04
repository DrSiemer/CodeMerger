# --- Application Constants ---
from .core.paths import CONFIG_FILE_PATH, DEFAULT_FILETYPES_CONFIG_PATH, VERSION_FILE_PATH

# --- Paths and Files ---
CONFIG_FILE = CONFIG_FILE_PATH
DEFAULT_FILETYPES_CONFIG = DEFAULT_FILETYPES_CONFIG_PATH
VERSION_FILE = VERSION_FILE_PATH
REGISTRY_KEY_PATH = r"Software\CodeMerger" # Windows Registry path

# --- Application Behavior ---
RECENT_PROJECTS_MAX = 10
MAX_SECRET_SCAN_REPORT_LINES = 10

# --- Default Content ---
DEFAULT_COPY_MERGED_PROMPT = "Here is the most recent code, please use this when making changes:\n"
DEFAULT_INTRO_PROMPT = 'Hi! I am working on REPLACE_ME.\n\nQUESTION\n\n'
DEFAULT_OUTRO_PROMPT = 'DO:\n- always return full code, unless a change is VERY small (a single line or a short connected segment)\n- make sure empty lines are actually empty: avoid generating lines of spaces or tabs\nalways place closing triple backticks (```) on their own, new line\n\nDo NOT:\n- remove my original comments\n- return diff files\n- use numbered steps (e.g., "1.") in comments\n- use <summary> tags\n- end comments with dots (unless you are using multiple sentences)\n- call something "final" or "definitive"; it usually isn\'t\n- use double newlines between code\n\nUse the following format if you want to add temporary notification comments: // [KEYWORD] Comment (e.g., [FIX], [MODIFIED]). These comments are transient and exist only to show the user what you\'ve changed. If you find them in code you are reviewing, remove these comments as the user will have already seen them.'

# --- UI Theming & Configuration ---
PROJECT_TITLE_MAX_LENGTH = 64
COMPACT_MODE_BG_COLOR = "#6f6f6f"

# --- UI Color Palette ---
DARK_BG = '#2E2E2E'
TOP_BAR_BG = '#252525'
TEXT_COLOR = '#FFFFFF'
TEXT_SUBTLE_COLOR = '#A0A0A0'
TEXT_INPUT_BG = '#3C3C3C'
BTN_BLUE = '#0078D4'
BTN_BLUE_TEXT = '#FFFFFF'
BTN_GRAY_BG = '#CCCCCC'
BTN_GRAY_TEXT = '#333333'
WRAPPER_BORDER = '#555555'
STATUS_BG = '#3A3A3A'
STATUS_FG = '#D3D3D3'
SUBTLE_HIGHLIGHT_COLOR = "#555555"