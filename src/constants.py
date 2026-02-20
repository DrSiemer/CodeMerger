# --- Application Behavior ---
RECENT_PROJECTS_MAX = 25
MAX_SECRET_SCAN_REPORT_LINES = 10
TOKEN_COUNT_ENABLED_DEFAULT = True
ADD_ALL_WARNING_THRESHOLD_DEFAULT = 100
STATUS_FADE_SECONDS = 5

# --- API Endpoints ---
GITHUB_API_URL = "https://api.github.com/repos/DrSiemer/codemerger/releases/latest"

# --- File System ---
# Added explicit directories to ignore for performance (node_modules, .git, .venv, etc)
SPECIAL_FILES_TO_IGNORE = {'.allcode', '.gitignore', 'package-lock.json', 'node_modules', '.git', '.venv', '__pycache__', '.idea', '.vscode'}
# Files that should be treated as "selected" when calculating if a parent folder should be greyed out,
# preventing them from keeping a folder "bright" if they are the only unselected files.
FILES_TO_IGNORE_FOR_VISUAL_COMPLETENESS = {'__init__.py'}

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
DEFAULT_INTRO_PROMPT = "Hi! I am working on REPLACE_ME.\n\nQUESTION\n\n"
DEFAULT_OUTRO_PROMPT = "Stylistic Guidelines\n\nDO:\n- end your output with clear instructions on how to check if the code you proposed works\n- make sure empty lines are actually empty: avoid generating lines of spaces or tabs\n- always place closing triple backticks (```) on their own, new line\n\nDo NOT:\n- remove my original comments\n- shorten code with comments like `... Unchanged` or `Same as before`\n- use numbered steps (e.g., \"1.\") in comments\n- use <summary> tags\n- end comments with dots (unless you are using multiple sentences)\n- call something \"final\" or \"definitive\"; it usually isn't\n- use double newlines between code\n- add comments if the code itself makes it pretty clear what it does\n- remove logs when you think you have solved a problem; wait for confirmation that the issue is resolved\n- use !important to solve HTML styling issues\n\nUse the following format if you want to add temporary notification comments: // [KEYWORD] Comment (e.g., [FIX] Now using correct value, [MODIFIED] Improved algorithm). These comments are transient and exist only to show the user what you've changed. If you find them in code you are reviewing, remove these comments as the user will have already seen them."
TOKEN_THRESHOLD_WARNING_TEXT = "You are close to the current maximum tokens\nfor currently available language models"

COMMENT_CLEANUP_PROMPT = """Let's clean up the comments. Remove all LLM tags (e.g., [MODIFIED], [FIX]), transient feedback, and changelogs. Git handles history; the code shouldn't.

Directive: Optimize the code for a programmer that has never seen this code before. Assume they understand standard syntax; do not explain what the code is doing, only why it is the way it is, if it is non-obvious.

1. Remove Redundancy: Delete comments that explain the obvious or simply restate the code in English (e.g., "Submit button" above a <button>, or "No clicks" next to pointer-events: none)
2. Keep Structure: Retain section headers (e.g., "Navigation", "API Logic") that help file navigation
3. Keep Context: Retain comments that explain the "why" behind complex business logic or workarounds for browser bugs, but clean up the wording
4. Clean Tags: Remove the [TAG] prefix. If the comment remains useful without the tag, keep it; otherwise, delete it
5. Avoid comments directly behind code
6. Do not use numbering in comments
7. Remove dots from the end of single line comments
8. Single line comments for single sentences are preferred, even if that makes them long

Do not change code, only comments."""

# --- Project Starter Wizard Constants ---
DELIMITER_TEMPLATE = "<<SECTION: {name}>>"

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

# Detailed descriptions for the TODO configuration UI
TODO_DESCRIPTIONS = {
    "setup": "Project initialization, folder structure, and basic 'go' automation scripts.",
    "database": "Data modeling, schema implementation, migrations, and initial seed data.",
    "api": "Server-side routes, controllers, business logic, and API documentation.",
    "frontend": "User interface components, layout, client-side routing, and styling.",
    "logic": "State management, complex algorithms, and third-party integrations.",
    "polish": "Error handling, animations, responsive design, and final code cleanup.",
    "deployment": "Production builds, environment variables, and hosting configuration."
}

# Logical order for the TODO document
TODO_ORDER = [
    "setup", "database", "api", "frontend", "logic", "polish", "deployment"
]

# --- Project Starter Wizard Prompt Templates ---
WIZARD_CONCEPT_DEFAULT_GOAL = "The plan is to build a..."
WIZARD_CONCEPT_PROMPT_INTRO = "Based on the following user goal, generate a full project concept document."
WIZARD_CONCEPT_PROMPT_CORE_INSTR = """
### Core Instructions
1. Fill in every section with specific details relevant to the user's goal.
2. Ensure the 'User Flows' section covers the complete lifecycle of the main data entity.
3. **Readability & Formatting:** Use frequent line breaks and short paragraphs to avoid dense blocks of text. Utilize Markdown elements (bullet points, bolding) to ensure the document is highly readable and visually structured.
"""

WIZARD_STACK_PROMPT_INTRO = "Based on the project concept and the developer's experience, recommend the best technical stack for this project."
WIZARD_STACK_PROMPT_INSTR = """
### Instructions
1. Analyze requirements against known skills.
2. Return the recommended stack as a raw JSON list of strings.
   - Example: ["Python 3.10", "Flask"]
3. Return ONLY the JSON.
"""

WIZARD_TODO_PROMPT_INTRO = """You are a Technical Project Manager.
Based on the following project Concept and Tech Stack, create a detailed TODO plan."""

WIZARD_TODO_PROMPT_INSTR = """
### Instructions
1. **Analyze Relevance:** Compare the Reference Template against the Concept. **SKIP** any phase from the template that is not appropriate for this specific project (e.g., remove 'Database' for a static site, remove 'API' for a CLI tool).
2. **Adapt Tasks:** For the phases you keep, adapt the tasks to be specific to this project (e.g., change 'Create tables' to 'Create `users` and `products` tables').
3. **Format:** You MUST output the plan using specific section tags for the phases you decide to include.
   - Use `<<SECTION: Phase Name>>` followed by the content.
   - Allowed Phase Names: {headers_str}.
   - **Do not** output sections for phases you decided to skip.
"""

WIZARD_GENERATE_MASTER_INTRO = "You are a senior developer creating a boilerplate for: {name}\nStack: {stack}"
WIZARD_GENERATE_MASTER_INSTR = """
### Core Instructions
1. **Select & Rename:** Select the appropriate `go_*.bat` script for the stack and rename it to `go.bat`.
2. **Mandatory README:** You MUST output the `README.md` file. Populate it (or create it) with the project title, the pitch, and specific setup steps derived from the stack.
3. **BOILERPLATE ONLY:** DO NOT implement any of the actual tasks, code, or features described in the TODO plan yet. Your job is ONLY to set up the skeleton/infrastructure (README, batch scripts, config files). Do NOT create source files (like *.js, *.py, *.css) unless they are explicitly part of the standard boilerplate provided above.
4. **Short Description:** At the start of your response, provide a short, one-sentence description (noun phrase) of exactly what this project is (e.g., 'a Python-based CLI tool for image processing'). This description must grammatically fit into the sentence 'We are working on [PITCH].' Wrap this description in `<<PITCH>>` tags. **You MUST close the tag with `<<PITCH>>`. Example: `<<PITCH>>a new CLI tool<<PITCH>>`.**
5. **Project Color:** Choose a single accent hex color code (e.g. #4A90E2) that fits the brand or technology of this project. Wrap it in `<<COLOR>>` tags. Example: `<<COLOR>>#4A90E2<<COLOR>>`.
6. **Output Format:** Return the complete source code for every file you are modifying or creating using this exact format:
--- File: `path/to/file.ext` ---
```language
[content]
```
--- End of file ---

CRITICAL: Do NOT omit the '--- End of file ---' marker for any block.
"""

WIZARD_REWRITE_PROMPT_TEMPLATE = """You are a Project Editor.
The user has provided a global instruction to modify the project plan.
Your task is to update ALL *unsigned* drafts listed below to comply with this instruction.

### User Instruction
{instruction}

### Locked Sections (Reference Only - DO NOT CHANGE)
{references}

### Drafts to Update (ALL of these must be processed)
{targets}

### Instructions
1. Review the User Instruction.
2. Rewrite every segment in the 'Drafts to Update' list to incorporate this instruction.
3. Ensure consistency with 'Locked Sections' (if any), but do not modify them.
4. {target_instructions}
5. Output ONLY the updated Drafts."""

WIZARD_SYNC_PROMPT_TEMPLATE = """You are a Consistency Engine. The user has modified section **{current_name}**.
Update *unsigned* drafts to match these changes, respecting *locked* sections.

### New Source of Truth: {current_name}
```
{content}
```
{ref_context}
### Drafts to Update
{target_context}

### Instructions
1. {target_instructions}"""

WIZARD_QUESTION_PROMPT_TEMPLATE = """### {context_label}
{context_content}

### Focus: {focus_name}
{focus_content}

### Question
{question}

Instruction: {instruction_suffix}"""

# --- UI Theming & Configuration ---
PROJECT_TITLE_MAX_LENGTH = 64
COMPACT_MODE_PROJECT_TITLE_MAX_LENGTH = 8
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
FILETYPES_WINDOW_DEFAULT_GEOMETRY = "330x550"
INSTRUCTIONS_WINDOW_DEFAULT_GEOMETRY = "700x500"
PROJECT_SELECTOR_WIDTH = 450
TITLE_EDIT_DIALOG_WIDTH = 400
PROJECT_STARTER_GEOMETRY = "1000x750" # Slightly increased height for better file manager view

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
TEXT_FILTERED_COLOR = '#BB86FC'

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
FONT_LOADING_TITLE = (FONT_FAMILY_PRIMARY, 18, 'bold')
FONT_LARGE_BOLD = (FONT_FAMILY_PRIMARY, 24, 'bold')
FONT_H2 = (FONT_FAMILY_PRIMARY, 18, 'bold')
FONT_H3 = (FONT_FAMILY_PRIMARY, 14, 'bold')
FONT_TOOLTIP = (FONT_FAMILY_TOOLTIP, 8, "normal")

# --- Data Mappings ---
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