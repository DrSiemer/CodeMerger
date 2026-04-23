# Application Behavior
RECENT_PROJECTS_MAX = 25
MAX_SECRET_SCAN_REPORT_LINES = 10
TOKEN_COUNT_ENABLED_DEFAULT = True
ADD_ALL_WARNING_THRESHOLD_DEFAULT = 100
NEW_FILE_ALERT_THRESHOLD_DEFAULT = 5
STATUS_FADE_SECONDS = 5

# Performance Thresholds
# Projects larger than this will trigger CPU protection/throttling
LARGE_PROJECT_THRESHOLD = 1000
# Scans faster than this will ignore adaptive throttling multipliers
FAST_SCAN_THRESHOLD_SECONDS = 0.5

# File System
# Explicit directories to ignore for performance during recursive scans
SPECIAL_FILES_TO_IGNORE = {
    '.codemerger', '.allcode', '.allcode.bak', '.gitignore', 'package-lock.json',
    'node_modules', '.git', '.venv', '__pycache__', '.idea', '.vscode',
    '.vs', 'bin', 'obj', 'dist', 'build'
}
# Files treated as selected to prevent folders from appearing unselected if they are the only unselected items
FILES_TO_IGNORE_FOR_VISUAL_COMPLETENESS = {'__init__.py'}
# Prefix for transient files created during atomic writes
CODEMERGER_TEMP_PREFIX = '.cm_tmp_'

# API Endpoints
GITHUB_API_URL = "https://api.github.com/repos/DrSiemer/codemerger/releases/latest"

# Logging
LOG_FILENAME = "codemerger.log"
LOG_MAX_BYTES = 5 * 1024 * 1024
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

# Self-hosting safe markers built with fragments to avoid triggering regex during bundling
MARKER_PREFIX = "--- "
MARKER_FILE = "File" + ": "
MARKER_EOF = "End of " + "file"

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

# System Design Segments
DESIGN_SEGMENTS = {
    "arch_overview": "Architecture Overview",
    "data_models": "Data Models & State",
    "component_breakdown": "Component Breakdown"
}

DESIGN_ORDER = [
    "arch_overview", "data_models", "component_breakdown"
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

# TODO document section order
TODO_ORDER = [
    "setup", "database", "api", "frontend", "logic", "polish", "deployment"
]

# UI Theming & Configuration
COMPACT_MODE_BG_COLOR = "#6f6f6f"

# Compact Window Dimensions (Logical Units)
COMPACT_WINDOW_WIDTH_LOGICAL = 131
COMPACT_WINDOW_HEIGHT_LOGICAL = 112
ULTRA_COMPACT_WINDOW_WIDTH_LOGICAL = 76
ULTRA_COMPACT_WINDOW_HEIGHT_LOGICAL = 86

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