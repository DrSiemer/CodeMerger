# --- Application Behavior ---
RECENT_PROJECTS_MAX = 10
MAX_SECRET_SCAN_REPORT_LINES = 10
TOKEN_COUNT_ENABLED_DEFAULT = True
ADD_ALL_WARNING_THRESHOLD_DEFAULT = 100
STATUS_FADE_SECONDS = 5

# --- Default Content ---
DEFAULT_COPY_MERGED_PROMPT = "Here is the most recent code, please use this when making changes:\n"
DEFAULT_INTRO_PROMPT = 'Hi! I am working on REPLACE_ME.\n\nQUESTION\n\n'
DEFAULT_OUTRO_PROMPT = 'DO:\n- always return full code, unless a change is VERY small (a single line or a short connected segment)\n- make sure empty lines are actually empty: avoid generating lines of spaces or tabs\nalways place closing triple backticks (```) on their own, new line\n\nDo NOT:\n- remove my original comments\n- return diff files\n- use numbered steps (e.g., "1.") in comments\n- use <summary> tags\n- end comments with dots (unless you are using multiple sentences)\n- call something "final" or "definitive"; it usually isn\'t\n- use double newlines between code\n- add comments if the code itself makes it pretty clear what it does\n\nUse the following format if you want to add temporary notification comments: `// [KEYWORD] Comment` (e.g., `[FIX] Now using correct value`, `[MODIFIED] Improved algorithm`). These comments are transient and exist only to show the user what you\'ve changed. If you find them in code you are reviewing, remove these comments as the user will have already seen them.'

# --- UI Theming & Configuration ---
PROJECT_TITLE_MAX_LENGTH = 64
COMPACT_MODE_BG_COLOR = "#6f6f6f"
TOKEN_COLOR_RANGE_MIN_MAX = 2500

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
BTN_BLUE_TEXT = '#FFFFFF'

## Colors
BTN_BLUE = '#0078D4'
NOTE = "#B77B06"
WARN = "#DF2622"
ATTENTION = "#DE6808"

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