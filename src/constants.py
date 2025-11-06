# --- Application Behavior ---
RECENT_PROJECTS_MAX = 25
MAX_SECRET_SCAN_REPORT_LINES = 10
TOKEN_COUNT_ENABLED_DEFAULT = True
ADD_ALL_WARNING_THRESHOLD_DEFAULT = 100
STATUS_FADE_SECONDS = 5

# --- API Endpoints ---
GITHUB_API_URL = "https://api.github.com/repos/DrSiemer/codemerger/releases/latest"

# --- File System ---
SPECIAL_FILES_TO_IGNORE = {'.allcode', '.gitignore', 'package-lock.json'}

# --- Logging ---
LOG_FILENAME = "codemerger.log"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# --- Behavioral Magic Numbers ---
TOKEN_THRESHOLD_WARNING = 800000
ANTIALIASING_SCALE_FACTOR = 4
FONT_LUMINANCE_THRESHOLD = 150

# --- Timing (in seconds or milliseconds) ---
ANIMATION_DURATION_SECONDS = 0.25
ANIMATION_START_DELAY_MS = 20
DOUBLE_CLICK_INTERVAL_SECONDS = 0.4
STATUS_FADE_DURATION_SECONDS = 0.5

# --- Default Content ---
DEFAULT_COPY_MERGED_PROMPT = "Here is the most recent code, please use this when making changes:\n"
DEFAULT_INTRO_PROMPT = 'Hi! I am working on REPLACE_ME.\n\nQUESTION\n\n'
DEFAULT_OUTRO_PROMPT = 'DO:\n- always return full code, unless a change is VERY small (a single line or a short connected segment)\n- wrap each file\'s code block with a `--- File: `path/to/file.ext` ---` header and an `--- End of file ---` footer\n- make sure empty lines are actually empty: avoid generating lines of spaces or tabs\n- always place closing triple backticks (```) on their own, new line, NEVER do this: "</table>```"\n\nDo NOT:\n- remove my original comments\n- return diff files\n- use numbered steps (e.g., "1.") in comments\n- use <summary> tags\n- end comments with dots (unless you are using multiple sentences)\n- call something "final" or "definitive"; it usually isn\'t\n- use double newlines between code\n- add comments if the code itself makes it pretty clear what it does\n- remove logs when you think you have solved a problem; wait for confirmation that the issue is resolved\n\nUse the following format if you want to add temporary notification comments: `// [KEYWORD] Comment` (e.g., `[FIX] Now using correct value`, `[MODIFIED] Improved algorithm`). These comments are transient and exist only to show the user what you\'ve changed. If you find them in code you are reviewing, remove these comments as the user will have already seen them.'
TOKEN_THRESHOLD_WARNING_TEXT = "You are close to the current maximum tokens\nfor currently available language models"

# --- UI Theming & Configuration ---
PROJECT_TITLE_MAX_LENGTH = 64
COMPACT_MODE_BG_COLOR = "#6f6f6f"
TOKEN_COLOR_RANGE_MIN_MAX = 2500
COMPACT_MODE_MOVE_BAR_HEIGHT = 14
COMPACT_MODE_BORDER_WIDTH = 1
DEFAULT_LIST_ITEM_HEIGHT = 25

# --- UI Default Dimensions ---
DEFAULT_WINDOW_GEOMETRY = "660x360"
MIN_WINDOW_WIDTH = 550
MIN_WINDOW_HEIGHT = 360
FILE_MANAGER_DEFAULT_GEOMETRY = "1000x700"
FILE_MANAGER_MIN_WIDTH = 600
FILE_MANAGER_MIN_HEIGHT = 200
SETTINGS_WINDOW_DEFAULT_GEOMETRY = "500x640"
SETTINGS_WINDOW_MIN_WIDTH = 500
SETTINGS_WINDOW_MIN_HEIGHT = 300
FILETYPES_WINDOW_DEFAULT_GEOMETRY = "450x550"
WRAPPER_TEXT_WINDOW_DEFAULT_GEOMETRY = "700x500"
DIRECTORY_DIALOG_WIDTH = 450
TITLE_EDIT_DIALOG_WIDTH = 400

# --- UI Color Palette (dark to light) ---

## Grayscale
TOP_BAR_BG = '#252525'
DARK_BG = '#2E2E2E'
BTN_GRAY_TEXT = '#333333'
STATUS_BG = '#3A3A3A'
TEXT_INPUT_BG = '#3C3C3C'
WRAPPER_BORDER = '#555555'
SUBTLE_HIGHLIGHT_COLOR = "#555555"
TEXT_SUBTLE_COLOR = '#A0A0A0'
BTN_GRAY_BG = '#CCCCCC'
STATUS_FG = '#D3D3D3'
TEXT_COLOR = '#FFFFFF'
BTN_GREEN_TEXT = '#FFFFFF'
BTN_BLUE_TEXT = '#FFFFFF'

## Colors
BTN_GREEN = '#0D8319'
BTN_BLUE = '#0078D4'
NOTE = "#B77B06"
WARN = "#DF2622"
ATTENTION = "#DE6808"
FILTER_ACTIVE_BORDER = '#009900'

# --- UI Fonts ---
FONT_FAMILY_PRIMARY = "Segoe UI"
FONT_FAMILY_SECONDARY = "Helvetica"
FONT_FAMILY_TOOLTIP = "tahoma"

FONT_DEFAULT = (FONT_FAMILY_PRIMARY, 11)
FONT_COMPACT_TITLE = (FONT_FAMILY_PRIMARY, 8)
FONT_COMPACT_BUTTON = (FONT_FAMILY_PRIMARY, 8, 'bold')
FONT_STATUS_BAR = (FONT_FAMILY_PRIMARY, 9)
FONT_SMALL_BUTTON = (FONT_FAMILY_PRIMARY, 9)
FONT_WRAPPER_SUBTITLE = (FONT_FAMILY_SECONDARY, 10)
FONT_WRAPPER_TITLE = (FONT_FAMILY_SECONDARY, 10, 'bold')
FONT_NORMAL = (FONT_FAMILY_PRIMARY, 12)
FONT_BOLD = (FONT_FAMILY_PRIMARY, 12, 'bold')
FONT_FILE_MANAGER_BUTTON = (FONT_FAMILY_PRIMARY, 14)
FONT_BUTTON = (FONT_FAMILY_PRIMARY, 16)
FONT_LARGE_BOLD = (FONT_FAMILY_PRIMARY, 24, 'bold')
FONT_TOOLTIP = (FONT_FAMILY_TOOLTIP, 8, "normal")

# --- Data Mappings ---
LANGUAGE_MAP = {
    '.bat': 'batch',
    '.c': 'c',
    '.conf': 'ini',
    '.cpp': 'cpp',
    '.cs': 'csharp',
    '.css': 'css',
    '.go': 'go',
    '.h': 'c',
    '.html': 'html',
    '.htm': 'html',
    '.java': 'java',
    '.js': 'javascript',
    '.jsx': 'jsx',
    '.json': 'json',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.less': 'less',
    '.md': 'markdown',
    '.php': 'php',
    '.ps1': 'powershell',
    '.py': 'python',
    '.r': 'r',
    '.rb': 'ruby',
    '.rs': 'rust',
    '.sass': 'sass',
    '.scss': 'scss',
    '.sh': 'shell',
    '.sql': 'sql',
    '.swift': 'swift',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.txt': 'text',
    '.vue': 'vue',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml'
}