# Application Behavior
RECENT_PROJECTS_MAX = 25
MAX_SECRET_SCAN_REPORT_LINES = 10
TOKEN_COUNT_ENABLED_DEFAULT = True
ADD_ALL_WARNING_THRESHOLD_DEFAULT = 100
NEW_FILE_ALERT_THRESHOLD_DEFAULT = 5
STATUS_FADE_SECONDS = 5

# API Endpoints
GITHUB_API_URL = "https://api.github.com/repos/DrSiemer/codemerger/releases/latest"

# File System
# Explicit directories to ignore for performance during recursive scans
SPECIAL_FILES_TO_IGNORE = {'.allcode', '.gitignore', 'package-lock.json', 'node_modules', '.git', '.venv', '__pycache__', '.idea', '.vscode'}
# Files treated as selected to prevent folders from appearing unselected if they are the only unselected items
FILES_TO_IGNORE_FOR_VISUAL_COMPLETENESS = {'__init__.py'}

# Logging
LOG_FILENAME = "codemerger.log"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# Behavioral Magic Numbers
ANTIALIASING_SCALE_FACTOR = 2
FONT_LUMINANCE_THRESHOLD = 150
LAZY_LAYOUT_DELAY_MS = 250

# Timing (in seconds or milliseconds)
ANIMATION_DURATION_SECONDS = 0.25
ANIMATION_START_DELAY_MS = 20
DOUBLE_CLICK_INTERVAL_SECONDS = 0.4
STATUS_FADE_DURATION_SECONDS = 0.5

# Visual Defaults
TOKEN_THRESHOLD_WARNING_TEXT = "You are close to the current maximum tokens\nfor currently available language models"

# Project Starter Logic
DELIMITER_TEMPLATE = '<SECTION name="{name}">'

# Concept Generation Segments
CONCEPT_SEGMENTS = {
    "problem_statement": "Problem & Audience",
    "core_principles": "Core Principles",
    "key_features": "Key Features",
    "user_flows": "User Actions & Flows",
    "tech_constraints": "Data & Tech Constraints"
}

CONCEPT_ORDER = [
    "problem_statement", "core_principles", "key_features", "user_flows", "tech_constraints"
]

# TODO Generation Phases
TODO_PHASES = {
    "setup": "Environment Setup",
    "database": "Database & Schema",
    "api": "API & Backend",
    "frontend": "Frontend & UI",
    "logic": "Core Logic & Actions",
    "polish": "Automation & Polish",
    "deployment": "Deployment"
}

# TODO configuration UI
TODO_DESCRIPTIONS = {
    "setup": "Project initialization, folder structure, and basic 'go' automation scripts.",
    "database": "Data modeling, schema implementation, migrations, and initial seed data.",
    "api": "Server-side architecture, controllers, business logic, and API documentation.",
    "frontend": "User interface components, layout, client-side routing, and styling.",
    "logic": "State management, complex algorithms, and third-party integrations.",
    "polish": "Error handling, animations, responsive design, and final code cleanup.",
    "deployment": "Production builds, environment variables, and hosting configuration."
}

# TODO document section order
TODO_ORDER = [
    "setup", "database", "api", "frontend", "logic", "polish", "deployment"
]

# UI Theming & Configuration
PROJECT_TITLE_MAX_LENGTH = 64
COMPACT_MODE_PROJECT_TITLE_MAX_LENGTH = 8
COMPACT_MODE_BG_COLOR = "#6f6f6f"
TOKEN_COUNT_ENABLED_DEFAULT = True
TOKEN_COLOR_RANGE_MIN_MAX = 2500
COMPACT_MODE_MOVE_BAR_HEIGHT = 14
COMPACT_MODE_BORDER_WIDTH = 1
DEFAULT_LIST_ITEM_HEIGHT = 25

# UI Default Dimensions
DEFAULT_WINDOW_GEOMETRY = "660x360"
MIN_WINDOW_WIDTH = 550
MIN_WINDOW_HEIGHT = 360
FILE_MANAGER_DEFAULT_GEOMETRY = "1000x700"
FILE_MANAGER_MIN_WIDTH = 600
FILE_MANAGER_MIN_HEIGHT = 200
SETTINGS_WINDOW_DEFAULT_GEOMETRY = "500x640"
SETTINGS_WINDOW_MIN_WIDTH = 500
SETTINGS_WINDOW_MIN_HEIGHT = 300
FILETYPES_WINDOW_DEFAULT_GEOMETRY = "330x550"
INSTRUCTIONS_WINDOW_DEFAULT_GEOMETRY = "700x500"
PROJECT_SELECTOR_WIDTH = 450
TITLE_EDIT_DIALOG_WIDTH = 400
PROJECT_STARTER_GEOMETRY = "1000x750"
NOTES_DIALOG_DEFAULT_GEOMETRY = "600x350"

# UI Color Palette (dark to light)

# Grayscale
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
INFO_PANEL_BG = "#1A1A1A"

# Colors
BTN_GREEN = '#0D8319'
BTN_BLUE = '#0078D4'
NOTE = "#B77B06"
WARN = "#DF2622"
ATTENTION = "#DE6808"
FILTER_ACTIVE_BORDER = '#009900'
TEXT_FILTERED_COLOR = '#BB86FC'

# Diff Colors - Optimized for Dark Theme Legibility
DIFF_ADD_BG = '#1e301e'
DIFF_ADD_FG = '#a7f0a7'
DIFF_REMOVE_BG = '#3a1e1e'
DIFF_REMOVE_FG = '#f0a7a7'
DIFF_HEADER_FG = '#85b5d5'

# UI Fonts
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
FONT_LOADING_TITLE = (FONT_FAMILY_PRIMARY, 18, 'bold')
FONT_LARGE_BOLD = (FONT_FAMILY_PRIMARY, 24, 'bold')
FONT_H2 = (FONT_FAMILY_PRIMARY, 18, 'bold')
FONT_H3 = (FONT_FAMILY_PRIMARY, 14, 'bold')
FONT_TOOLTIP = (FONT_FAMILY_TOOLTIP, 8, "normal")
FONT_INFO_PANEL = (FONT_FAMILY_PRIMARY, 10)

# Info Mode Config
INFO_PANEL_HEIGHT = 80

# Data Mappings
LANGUAGE_MAP = {
    '.bat': 'batch',
    '.c': 'c',
    '.conf': 'ini',
    '.cpp': 'cpp',
    '.cs': 'csharp',
    '.csproj': 'xml',
    '.css': 'css',
    '.fx': 'c',
    '.glsl': 'c',
    '.go': 'go',
    '.h': 'c',
    '.html': 'html',
    '.htm': 'html',
    '.ino': 'c',
    '.iss': 'pascal',
    '.java': 'java',
    '.js': 'javascript',
    '.jsx': 'jsx',
    '.json': 'json',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.less': 'less',
    '.md': 'markdown',
    '.mjs': 'javascript',
    '.nsi': 'nsis',
    '.php': 'php',
    '.ps1': 'powershell',
    '.py': 'python',
    '.r': 'r',
    '.rb': 'ruby',
    '.rs': 'rust',
    '.sass': 'sass',
    '.scss': 'scss',
    '.sh': 'shell',
    '.sln': 'text',
    '.spec': 'python',
    '.sql': 'sql',
    '.swift': 'swift',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.txt': 'text',
    '.vue': 'vue',
    '.xaml': 'xml',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    'caddyfile': 'caddyfile'
}