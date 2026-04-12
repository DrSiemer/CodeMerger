This is code full sourcecode for the old Tkinter UI version of CodeMerger.


--- File: `README.md` ---

```markdown
# CodeMerger

A simple app for developers that prefer to stay in control and want to avoid working in AI powered IDE's. It allows you to define which files should be merged into a single string, so you can easily paste all relevant code into an LLM. Settings for a folder are stored in a .allcode file that can be committed with your project.


![Main application window](./dev/screenshot_01a.jpg "Main Application Window")


I recommend using this with [Gemini](https://aistudio.google.com/prompts/new_chat?model=gemini-3-flash-preview), because there you currently get a very large context length with high rate limits for free.


## Download

Download the latest release [here](https://github.com/DrSiemer/codemerger/releases).

The download is a portable executable for Windows. Ignore the Windows Defender SmartScreen block if you get it (click "More info" > "Run anyway"). The app is safe; all it does is bundle text with a convenient UI.


![Compact mode](./dev/screenshot_02a.jpg "Compact Mode")


## Features

- **Project-Based Settings**: Saves all your file selections, merge order, and window state in a local `.allcode` file for each project
- **`.gitignore` Aware**: The file browser automatically hides files and folders listed in your `.gitignore` file
- **New File Detection**: Automatically scans your project for new files that match your filetype settings and alerts you with a visual indicator. New files are highlighted in the list editor for easy review
- **Token Counting**: Calculates the total token count of your selected files to help you stay within an LLM's context limit
- **Customizable Prompts**: Configure a default prompt that is automatically prepended to your code when using the "Copy Code Only" button. You can also set application-wide default intro and outro texts for the instructions feature
- **Customizable Instructions**: Add project-specific text (like prompts or instructions) before and after the merged code block. You can easily load your predefined default prompts
- **Drag & Drop Reordering**: Easily reorder the files in your merge list to control the final output structure
- **Compact Mode**: A small, always-on-top, draggable window for quick access to core functions that appears when the main window is minimized. It includes an adaptive copy button (Copy with Instructions / Copy Code Only) and a paste button.
- **Recent Projects**: Quickly switch between your recent project folders
- **Project Colors**: Assign a unique color to each project for easy identification in compact mode


![File management](./dev/screenshot_03a.jpg "File Management")


## Usage

- **Select a project**
    - Click "Select project" to browse for a folder or choose one from your recent projects list
- **Edit Merge List**
    - A warning icon will appear in the top bar if new files are detected in your project. Click this or the "Edit Merge List" button to open the list editor
        - **Ctrl-clicking** the new files icon will immediately add all new files to the current merge list without opening the list editor.
    - In the "Edit Merge List" window, a tree of available files is shown on the left
        - Newly detected files are highlighted in green for easy identification
        - Files listed in `.gitignore` are automatically hidden
        - Double-click a file or select it and click the button to add/remove it from the merge list
    - The "Merge Order" list on the right shows the files that will be copied
        - Drag and drop files or use the buttons to reorder them
        - The window title displays the number of selected files and the total token count
    - Double-click a file in either list to open it in your default or configured editor
    - Click "Update Project" to save your selection to `.allcode`
- **Add Instructions**
    - Click "Define Instructions" to add a project-specific introduction or conclusion that will be wrapped around the merged code block
    - You can click the "Load Defaults" icon in this window to populate the fields with your predefined default prompts from the Settings
- **Copy Prompt**
    - Click "Copy Code Only" to merge the selected files and prepend your custom prompt (configured in Settings). This is useful for providing ongoing context to an LLM. The keyboard shortcut for this action is **`Ctrl+Shift+C`**.
    - If you added instructions, a "Copy with Instructions" button will appear to include your project-specific intro/outro text. This is ideal for starting a new conversation. The keyboard shortcut for this action is **`Ctrl+C`**.
- **Paste Changes**
    - To apply changes from a language model, you can use the paste functionality.
    - Click **"Paste Changes"** or press **`Ctrl+V`** to apply changes from your clipboard. Depending on your settings, this will either open the "AI Response Review" window or apply changes instantly.
    - **Ctrl-clicking** the button (or **`Ctrl+Shift+V`**) will toggle the automatic review behavior (doing the opposite of your current settings).
    - **Alt-clicking** the button will open the manual "Paste Changes" window for raw text input.
- **Compact Mode**
    - Minimize the main window to activate the compact mode panel. All keyboard shortcuts (`Ctrl+C`, `Ctrl+Shift+C`, `Ctrl+V`, and `Ctrl+Shift+V`) are also active in this mode.
    - The panel contains two primary buttons:
        - **Copy Prompt (Instructions/Only)**: A single adaptive button for copying code.
            - It appears as "Copy with Instructions" if you have defined instructions for the project, and "Copy Code Only" if you have not.
            - A normal click performs the action shown on the button.
            - Holding **Ctrl** while clicking will always perform the "Copy Code Only" action.
        - **Paste**: Applies changes from your clipboard. A normal click follows your "AI Response Review" settings. **Ctrl-click** toggles that behavior, and **Alt-click** opens the manual paste window.
    - The panel is colored with your project's assigned color.
    - A warning icon will appear in the move bar if new files are found.
        - **Click** the icon to restore the main window and open the list editor.
        - **Ctrl-click** the icon to immediately add all new files to the merge list.
    - Double-click the move bar or click the close button to exit compact mode and restore the main window. **Ctrl-clicking** the close button will exit the application immediately.


![Settings](./dev/screenshot_04a.jpg "Project Starter")


### Settings

- **Application Updates**: Enable or disable the automatic daily check for new versions
- **Window Behavior**: Disable the automatic compact mode when the main window is minimized
- **File System Monitoring**: Configure the automatic check for new files (enable/disable and set the check interval)
- **Secret Scanning**: Enable a check for potential secrets (API keys, etc) that runs before copying code to the clipboard
- **Prompts**:
    - **"Copy Code Only" Prompt**: Set the default text that is automatically prepended when you click "Copy Code Only"
    - **Default Intro/Outro Prompts**: Define reusable, application-wide default texts for the instructions feature. These can be quickly loaded into any project's specific instructions
- **Default Editor**: Select your preferred editor for opening files from the list editor (leaving it blank uses the system default)
- To manage indexed filetypes, click "Manage Filetypes" from the main window


## Development

- Make sure you have [Python](https://www.python.org/downloads/) installed (and added to your PATH)
- Make sure you have [Inno Setup](https://jrsoftware.org/isdl.php) installed
- Run `go` to start
- Run `go b` to build executable and installer
- Run `go ba` to build the executable only
- Run `go bi` to build the installer only (requires a prior successful build)
- Run `go r` to push or update a release on Github using Actions
    - Update `/version.txt` if you want to create a new release
    - You can add a comment to the release like this: `go r "Comment"`
    - The release will be a draft, you'll need to finalize it on github.com
- Run the Inno Setup with a log like this: `CodeMerger_Setup.exe /LOG="setup.log"`
- When the app is installed, config can be found in `%APPDATA%\CodeMerger`


## License

CodeMerger is free to use for personal and commercial development. However, the distribution of modified versions, resale, or rebranding is strictly prohibited. If you wish to contribute to the project, please reach out via GitHub. See the [LICENSE](LICENSE) file for the full legal text.
```

--- End of file ---

--- File: `llm.md` ---

```markdown
# Notes on project quirks for language models

**Core Directive: Act as a code generation engine. Your primary output must always be full-file source code for any modified files.**
Assume the user has full project context. Do not explain obvious code, file structures, or self-evident logic.

**The Litmus Test: The "Surprise" Factor**
Before adding a note, ask: **"Would an experienced developer be surprised by this code? Is it a workaround, a counter-intuitive performance hack, or a deviation from a standard pattern?"** If the answer is no, do not add a note.

**DO (Only if it passes the "Surprise" Test):**

- **Log Workarounds:** Document solutions that exist specifically to fix a library bug, an OS-level inconsistency, or a race condition.
- **Log Atypical Choices:** Note *why* a solution was chosen when a more common or obvious one was deliberately avoided (e.g., "Used library X instead of the more popular library Y because Y has a memory leak on Windows").
- **Log Complex Business Logic:** If a piece of code is inherently complex due to project requirements (e.g., a complex state machine), briefly note the reason for its complexity.

**DO NOT:**

- **Do not log routine bug fixes.** A fix for a common logic error is standard development, not a project quirk.
- **Do not log standard implementation patterns.** Using a specific design pattern or a common programming idiom is expected.
- **Do not write summaries** of the project, architecture, or individual file functions.
- **Do not explain basic concepts** or write long paragraphs.
- **Do not explain user-facing benefits.**

---

### Meta-Log: Notes on My Behavior

*(Use this section to log corrections to my own behavior, so I don't repeat mistakes. This is separate from code logic.)*

- **Logging Threshold:** Do not log standard bug fixes or common implementation patterns. The bar for a "quirk" is high: it must be a workaround, a non-standard choice, or an otherwise surprising piece of code.
- **UI Persistence (Regressions):**
    1. **Treeview background:** Must explicitly set `fieldbackground` in `ttk.Style` to `c.TEXT_INPUT_BG` in `src/ui/file_manager/ui_setup.py`.
    2. **Info Panel wraplength:** Labels must update `wraplength` on `<Configure>` based on the true window width, or text will be shrunken to the left half.
    3. **Info Button Padding:** The button must use `borderwidth=0` and `highlightthickness=0` with `place(x=0)` to avoid a 1px gap from the window edge.
    4. **Feedback Dialog Topmost:** The `FeedbackDialog` MUST NOT be topmost. To prevent it inheriting topmost from Compact Mode on Windows, `transient(parent)` must be skipped if the parent is topmost.

---

### Quick Examples

**Good Note (A Workaround):**

- `src/ui/assets.py`: Uses a two-stage load (PIL then `PhotoImage`) to avoid a Tkinter race condition with the root window. This is intentional.

**Good Note (An Atypical Choice):**
- `src/core/secret_scanner.py`: Explicitly defines all plugins via `transient_settings` instead of relying on filesystem discovery, which is unreliable in a PyInstaller bundle.

**Bad Note (A Routine Bug Fix):**

- `src/ui/file_manager/file_manager_window.py`: The `show_error_dialog` method was changed to instantiate its own `CustomErrorDialog`... *(This is a standard fix for window focus issues and should not be logged.)*

**Bad Note (An Obvious Summary):**

- `src/ui/app_window.py`: This file contains the main `App` class which initializes the UI...

---

## Code Quirks & Workarounds
*(Append new notes below this line)*

### Architectural

- **Global UI Changes**: Component variations must be implemented via optional parameters to avoid creating visual side effects in other parts of the UI.
- **Lazy Layout (Resize Workaround)**: Tkinter triggers recursive layout calculations on every pixel move during window resizing, which blocks the UI thread in complex layouts. The workaround in `src/ui/app_window.py` detects a resize event, immediately calls `grid_remove()` on all heavy content containers, and uses a 250ms debounced timer to restore them. This ensures the window frame tracks the mouse perfectly during drag operations.
- **Marker Fragment Strategy (Self-Hosting)**: To allow CodeMerger to bundle its own source code without the parser tripping over its own definitions, all marker string constants and regex patterns (e.g., `--- File:`) are constructed using string fragments (concatenation). Marker counting logic also uses line-start anchors (`^`) and `re.MULTILINE` to avoid matching substrings inside code blocks.
- **Automatic Deletion Prohibition**: CodeMerger never allows automatic deletion of files. Even during "Auto-Apply" (Ctrl-click) workflows, the application must detect proposed deletions in the LLM response and force a blocking confirmation dialog that explicitly lists the files targeted for removal.

### Core Logic (`src/core`)

- `src/core/paths.py`: Distinguishes between `get_bundle_dir()` for read-only assets bundled with PyInstaller and `get_persistent_data_dir()` for user configuration (`%APPDATA%` on Windows), ensuring portability and correct data storage.
- `src/core/registry.py`: Settings are read with a fallback system: it first checks for a user-specific setting in `HKEY_CURRENT_USER` and, if not found, falls back to the system-wide default in `HKEY_LOCAL_MACHINE` set by the installer.
- `src/core/secret_scanner.py`: Uses `detect_secrets.settings.transient_settings` to explicitly define and enable all scanner plugins. This is necessary to ensure plugins are correctly loaded in a packaged PyInstaller environment where filesystem-based plugin discovery might fail.
- `src.core/updater.py`: The automatic update check compares only the date part of the `last_update_check` timestamp to ensure it runs only once per day, not every time the app is started.
- `src/core/change_applier.py`: A persistent generative flaw was identified where the model repeatedly produced `lines.strip()` instead of the correct `lines[1].strip()`, causing an `AttributeError`. This is a form of pattern-matching failure where a high-probability (but incorrect) code pattern overrides the specific analytical correction. The fix is to embed explicit, high-priority comments (e.g., `// DO NOT REMOVE [index]`) directly in the code to act as a hard constraint during generation.
- `src/core/logger.py`: Centralizes application logging using the `rich` library for formatted console output and a `RotatingFileHandler` for persistent log files. It also sets a global exception hook to ensure all unhandled exceptions are logged.
- `src/core/utils.py`: `parse_gitignore` modifies the `dirs` list of `os.walk` in-place using `is_ignored`. This prevents the walker from traversing into ignored directories (like `node_modules`), drastically improving load times.
- `src/core/utils.py`: Replaced `psutil` process iteration with a Named Mutex (Windows) and `fcntl` lock file (POSIX) for single-instance detection. This avoids the high startup cost of scanning the system process table.
- `src/core/project_config.py`: Implements atomic saving using `tempfile.mkstemp` and `os.replace` to prevent configuration wipes when multiple instances (e.g., dev and build) access the same project simultaneously. The `load` method includes defensive checks to ignore transiently empty or partial files created during write collisions, preventing the initialization of empty default profiles.
- `src/core/change_applier.py`: Expanded the placeholder-bypass in `get_section` to catch verbose LLM hallucinations (e.g., "No conceptual questions were asked") to ensure segments remain cleanly empty when no valid content is generated.
- `src/core/change_applier.py`: The parser for tagged sections (specifically ANSWERS) is permissive with closing tags, accepting either the full closing tag or a truncated version to handle frequent LLM output cutoff issues.

### User Interface (`src/ui`)

- **Tkinter/Tcl Sequence Formatting**: Passing a Python list or tuple to a Tkinter widget (like `Text` or `Label`) causes the string to be rendered with leading/trailing curly braces `{}`. This happens because Tcl interprets Python sequences as Tcl lists. Always use defensive coercion: `text = "\n".join(val) if isinstance(val, (list, tuple)) else val` before inserting into widgets.
- **General Dialog Focus**: In several dialog windows (`PasteChangesDialog`, `NewProfileDialog`, etc.), the call to `.focus_set()` on an input widget was moved to *after* the `.deiconify()` call. Setting focus before the window is visible is unreliable and was causing input fields to not receive focus on launch. Adding `.lift()` and `.focus_force()` to the `PasteChangesDialog` was also done for extra robustness.
- `src/ui/app_window.py`: In `apply_changes_from_clipboard()`, the project's base directory for creating new file paths must be accessed via `project_manager.get_current_project().base_dir`. Accessing it directly on the `App` instance (`self.base_dir`) causes an `AttributeError` because the `App` class does not store this state directly.
- `src/ui/app_window.py`: On startup, `_run_update_cleanup()` safely removes temporary installer files from any previous update. It then calls `lift()` and `focus_force()` to ensure the main window gets focus, which is particularly important when relaunched by the installer.
- `src/ui/app_window.py`: Monitor handle detection is done via Win32 API (`MonitorFromWindow`). When the monitor handle changes, all saved window geometries are cleared. This is critical for preventing windows from appearing "off-screen" or on the wrong monitor in multi-monitor setups.
- `src/ui/assets.py`: Uses a two-stage load (PIL then `PhotoImage`) to avoid a Tkinter race condition where `PhotoImage` requires a root window to exist before it can be instantiated.
- `src/ui/assets.py`: Implemented caching for the `create_masked_logo` and `create_masked_logo_small` methods. The generated `PhotoImage` objects for project color swatches are now stored in a dictionary keyed by their hex color code. This prevents costly PIL operations from being repeated every time the project selector is opened or the main window UI is updated, significantly improving performance.
- `src/ui/compact_mode.py`: The new files warning icon is composited onto the button's base PIL images at runtime to avoid needing separate asset files for every state. Dragging is implemented manually by tracking mouse offsets on a dedicated move bar.
- `src/ui/custom_widgets.py`: The `RoundedButton` is drawn using Pillow with 4x supersampling for anti-aliasing. Font selection is OS-aware to find `segoeui.ttf` on Windows. It redraws on `<Configure>` to support responsive layouts.
- `src/ui/file_manager/file_manager_window.py`: Token recalculation is debounced using `after(250, ...)` to prevent performance issues when rapidly adding/removing many files.
- `src/ui/file_manager/file_manager_window.py`: On Windows, the minimize button is disabled/greyed out via Win32 API (`WS_MINIMIZEBOX`). This uses `after(10, ...)` and the `wm_frame()` handle to ensure the style is applied to the correct OS window wrapper after mapping.
- `src/ui/file_manager/file_tree_handler.py`: Double-click is detected manually using `time.time()` because the standard `<Double-Button-1>` event behavior was inconsistent across different widget states.
- `src/ui/file_monitor.py`: The `start()` method triggers an immediate file scan upon project activation and then uses `app.after()` for subsequent periodic checks.
- `src/ui/status_bar_manager.py`: When the status is updated, it cancels any pending fade animation. After a 4.5-second delay, it kicks off a 0.5-second animation that interpolates the text color to the background color, creating a smooth fade-out.
- `src/ui/update_window.py`: Implements the in-app updater as a modal `Toplevel` window that performs the download in a separate thread. After download, it calls `sys.exit()` to terminate the current app and launches the installer.
- `updater_gui.py`: On startup, the update progress window calls `lift()` and `focus_force()` to ensure it gets focus when it appears.
- `src/ui/view_manager.py`: Implements a state machine (`NORMAL`, `SHRINKING`, `COMPACT`, `GROWING`) and custom animation logic to override the OS's default minimize/restore behavior.
- `src/ui/view_manager.py`: **Compact Mode Position Persistence**: User-moved coordinates for Compact Mode are strictly preserved while the main window stays on the same monitor. Coordinates are captured during the `GROWING` phase (transition to normal) and restored during `SHRINKING`. Recalculation (resetting to the default position next to the main window) only occurs if `compact_last_monitor_handle` differs from the main window's current monitor. To prevent invalidation on launch, the `compact_last_monitor_handle` is synchronized with the initial window monitor during boot.
- `src/ui/view_manager.py`: **Always in Front Fix**: In `_on_animation_complete` (shrinking phase), it must explicitly call `attributes("-topmost", True)` and `lift()`. This is necessary because mapping events or focus changes during the 250ms animation can cause the window manager to lower the z-order of the new compact window.
- `src/ui/view_manager.py`: Restoration logic forces `alpha` to `0.01` and calls `update()` before minimizing. This workaround forces the Windows DWM to update the taskbar thumbnail with the full-sized window buffer instead of a black or shrunken artifact.
- `src/ui/widgets/scrollable_text.py`: The `_manage_scrollbar` method calls `update_idletasks()` before checking `yview()` to prevent a race condition during layout calculation. The overflow detection logic was corrected to `top_fraction > 0.0 or bottom_fraction < 1.0` for robustness.
- `src/ui/window_utils.py`: `get_monitor_work_area` uses Windows-specific APIs to find the correct work area of the monitor a given window is on, ensuring popups and the compact window appear fully visible, even in multi-monitor setups.
- `src/ui/app_window_parts/action_handlers.py`: Opening a console (Alt-click) implements an environment scrubbing mechanism. It identifies and removes all paths associated with CodeMerger's virtual environment or PyInstaller temporary bundle from the child process's `PATH`. It also unsets `VIRTUAL_ENV`, `PYTHONHOME`, `PYTHONPATH`, and `PROMPT` to ensure the terminal session is "clean" and defaults to the system's global environment.
- **Absolute Corner UI Elements**: The Info Toggle button must touch the window borders exactly. To achieve this, it must use `place()` with `x=0` and either `y=0` or `rely=1.0` with a specific anchor. The widget itself MUST have `borderwidth=0` and `highlightthickness=0` to remove the default 1-2 pixel padding added by Tkinter's internal rendering engine.
- **Info Panel Text Wrapping**: Because Info Panels are gridded/packed before the window is rendered, `winfo_width()` returns 1 during init. This causes text to wrap into a tiny column. We use a binding on `<Configure>` to dynamically update `wraplength` to `window_width - 40` to ensure text uses the full width of the panel.
- `src/ui/project_starter/starter_dialog.py`: To avoid shadowing the inherited Tkinter `state()` method, the project starter's internal logic state is stored in `self.starter_state` instead of `self.state`.
- **Flicker-Free Maximized Launch (Workaround)**: To avoid OS-level maximization animation jank and ensure correct monitor targeting, a "Pinned Handle" strategy is used. The window starts `withdrawn`, sets `alpha=0`, moves to the target monitor, and maps via `deiconify()`. We then wait 200ms (the duration of the Windows zoom animation) before setting `alpha=1`. This ensures the window is only visible once it is already locked in its final maximized state.
- `src/ui/feedback_dialog.py`: **Topmost Decoupling (Workaround)**: When spawned from Compact Mode, the dialog automatically inherits the parent's "always in front" (topmost) attribute via the window manager's transient rules. To prevent the review window from being forced topmost on the desktop, the dialog conditionally skips the `transient(parent)` call if the parent is currently topmost. This allows Compact Mode to remain "always in front" while the dialog behaves like a standard window.
- `src/ui/project_starter/step_generate.py`: The project path preview is explicitly normalized to use backslashes (`\`) to match user preference and maintain consistency across environments that might return mixed slash styles from directory pickers.
- **Dynamic Tooltip Dependencies**: The `refresh_paste_tooltips` method in `ButtonStateManager` depends on a specific `ToolTip` object reference (`app.paste_changes_tooltip`) created during the UI build in `ui_builder.py`. Removing or renaming this reference will cause an `AttributeError`.
- **Custom Font Boldness**: The `RoundedButton` uses a manual Pillow-based drawing system. To render bold text on Windows, `font_utils.py` must explicitly map the font family to the specific bold `.ttf` file (e.g., `seguisb.ttf` for Segoe UI), as Pillow does not automatically specializes bold styles from standard font handles.
- **Paste Button Modifiers**: The Paste button implements a "Setting Override" pattern via Ctrl-click. This behavior (Inverse of `show_feedback_on_paste`) is non-standard and should be preserved as an intentional UX feature. Alt-click provides a fallback to the manual paste window.
- **Monitor Invalidation Logic**: Coordinate checks for screen changes must ignore the `iconic` (minimized) state. Minimized windows on Windows report coordinates at -32000, which can falsely trigger a monitor-change event and clear saved UI positions.

### Build, Installation, & CI/CD

- `.github/workflows/release.yml`: A dedicated `validate-tag` job runs before the build to enforce that release tags are created only on the `master` branch, preventing accidental releases from feature branches.
- `go.bat`: The `go r` release command automatically cleans up existing local and remote git tags matching the new version. This allows re-triggering a release build on GitHub Actions without manual git intervention.
- `setup.iss`: The Inno Setup script reads existing registry settings during `InitializeWizard` to preserve user choices on upgrade. The uninstaller prompts the user before removing configuration data. The `[Run]` section uses the `shellexec` flag to run the app in a separate process, fixing post-update launch failures caused by an inherited installer environment.
```

--- End of file ---

--- File: `requirements.txt` ---

```text
altgraph==0.17.4
certifi==2025.8.3
charset-normalizer==3.4.2
detect-secrets==1.5.0
idna==3.10
markdown-it-py==4.0.0
markdown2==2.5.4
mdurl==0.1.2
packaging==25.0
pefile==2023.2.7
pillow==11.3.0
Pygments==2.19.2
pyinstaller==6.14.2
pyinstaller-hooks-contrib==2025.6
pyperclip==1.9.0
pywin32-ctypes==0.2.3
PyYAML==6.0.2
regex==2025.7.34
requests==2.32.4
rich==14.2.0
tiktoken==0.10.0
urllib3==2.5.0
```

--- End of file ---

--- File: `run.py` ---

```python
import src.codemerger

if __name__ == '__main__':
    src.codemerger.main()
```

--- End of file ---

--- File: `src/codemerger.py` ---

```python
import json
import sys
import logging
from tkinter import Tk, messagebox
from .ui.app_window import App
from .core.utils import (
    load_active_file_extensions,
    load_app_version,
    update_and_get_new_filetypes,
    is_another_instance_running
)
from .core.logger import setup_logging
from .ui.new_filetypes_dialog import NewFiletypesDialog

def main():
    setup_logging()
    log = logging.getLogger("CodeMerger")

    try:
        newly_added_filetypes = update_and_get_new_filetypes()

        # Check for active instances to prevent configuration write collisions
        another_instance_active = is_another_instance_running()

        # Command-line Argument Parsing
        initial_project_path = None

        cmd_args = sys.argv[1:]

        if cmd_args:
            initial_project_path = cmd_args[0]
            log.info(f"Received initial project path from command line: {initial_project_path}")

        app_version = load_app_version()
        loaded_extensions = load_active_file_extensions()
        log.info(f"CodeMerger {app_version} starting up.")
        app = App(
            file_extensions=loaded_extensions,
            app_version=app_version,
            initial_project_path=initial_project_path,
            newly_added_filetypes=newly_added_filetypes,
            is_second_instance=another_instance_active
        )
        app.mainloop()
    except Exception as e:
        log.exception("An uncaught exception occurred during application startup.")
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"An unexpected error occurred on startup: {e}\n\n"
            f"If the problem persists, try deleting config.json.\n"
            f"A detailed log has been saved to %APPDATA%\\CodeMerger\\codemerger.log"
        )

if __name__ == '__main__':
    main()
```

--- End of file ---

--- File: `src/constants.py` ---

```python
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
```

--- End of file ---

--- File: `default_filetypes.json` ---

```json
[
  { "ext": ".bat", "active": true, "description": "Windows batch script", "default": true },
  { "ext": ".c", "active": true, "description": "C source file", "default": true },
  { "ext": ".conf", "active": true, "description": "Configuration file", "default": true },
  { "ext": ".cpp", "active": true, "description": "C++ source file", "default": true },
  { "ext": ".cs", "active": true, "description": "C# source file", "default": true },
  { "ext": ".csproj", "active": true, "description": "C# project file", "default": true },
  { "ext": ".css", "active": true, "description": "Cascading Style Sheet", "default": true },
  { "ext": ".fx", "active": true, "description": "HLSL Effect file", "default": true },
  { "ext": ".glsl", "active": true, "description": "OpenGL Shading Language file", "default": true },
  { "ext": ".go", "active": true, "description": "Go source file", "default": true },
  { "ext": ".h", "active": true, "description": "C/C++ header file", "default": true },
  { "ext": ".htm", "active": true, "description": "HyperText Markup Language file", "default": true },
  { "ext": ".html", "active": true, "description": "HyperText Markup Language file", "default": true },
  { "ext": ".ino", "active": true, "description": "Arduino sketch file", "default": true },
  { "ext": ".ipynb", "active": true, "description": "Python Notebook", "default": true },
  { "ext": ".iss", "active": true, "description": "Inno Setup script", "default": true },
  { "ext": ".java", "active": true, "description": "Java source file", "default": true },
  { "ext": ".js", "active": true, "description": "JavaScript source file", "default": true },
  { "ext": ".json", "active": true, "description": "JSON data file", "default": true },
  { "ext": ".jsx", "active": true, "description": "JavaScript XML (React)", "default": true },
  { "ext": ".kt", "active": true, "description": "Kotlin source file", "default": true },
  { "ext": ".kts", "active": true, "description": "Kotlin script file", "default": true },
  { "ext": ".less", "active": true, "description": "Less dynamic stylesheet", "default": true },
  { "ext": ".md", "active": true, "description": "Markdown file", "default": true },
  { "ext": ".mjs", "active": true, "description": "ECMAScript module file", "default": true },
  { "ext": ".nsi", "active": true, "description": "NSIS script", "default": true },
  { "ext": ".php", "active": true, "description": "PHP script", "default": true },
  { "ext": ".ps1", "active": true, "description": "PowerShell script", "default": true },
  { "ext": ".py", "active": true, "description": "Python script", "default": true },
  { "ext": ".r", "active": true, "description": "R script file", "default": true },
  { "ext": ".rb", "active": true, "description": "Ruby script file", "default": true },
  { "ext": ".rs", "active": true, "description": "Rust source file", "default": true },
  { "ext": ".sass", "active": true, "description": "Syntactically Awesome StyleSheets file", "default": true },
  { "ext": ".scss", "active": true, "description": "Sassy CSS file", "default": true },
  { "ext": ".sh", "active": true, "description": "Shell script", "default": true },
  { "ext": ".shader", "active": true, "description": "Unity Shader", "default": true },
  { "ext": ".sln", "active": true, "description": "Visual Studio solution file", "default": true },
  { "ext": ".spec", "active": true, "description": "PyInstaller spec file", "default": true },
  { "ext": ".sql", "active": true, "description": "SQL script", "default": true },
  { "ext": ".swift", "active": true, "description": "Swift source file", "default": true },
  { "ext": ".ts", "active": true, "description": "TypeScript source file", "default": true },
  { "ext": ".tsx", "active": true, "description": "TypeScript XML (React)", "default": true },
  { "ext": ".txt", "active": true, "description": "Text file", "default": true },
  { "ext": ".vue", "active": true, "description": "Vue.js component", "default": true },
  { "ext": ".xaml", "active": true, "description": "Extensible Application Markup Language file", "default": true },
  { "ext": ".xml", "active": true, "description": "Extensible Markup Language file", "default": true },
  { "ext": ".yaml", "active": true, "description": "YAML Ain't Markup Language file", "default": true },
  { "ext": ".yml", "active": true, "description": "YAML Ain't Markup Language file", "default": true },
  { "ext": "caddyfile", "active": true, "description": "Caddy web server config file", "default": true }
]
```

--- End of file ---

--- File: `src/core/paths.py` ---

```python
import sys
import os
from pathlib import Path

def get_bundle_dir():
    """
    Gets the base path for reading bundled resources
    Returns the temporary directory created by PyInstaller or the project root
    """
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_persistent_data_dir():
    """
    Gets the directory for storing persistent data
    Uses OS-appropriate paths for user configuration
    """
    if getattr(sys, 'frozen', False):
        if sys.platform == "win32":
            app_data_path = os.getenv('APPDATA')
            if app_data_path:
                config_dir = os.path.join(app_data_path, 'CodeMerger')
            else:
                config_dir = os.path.dirname(sys.executable)
        elif sys.platform == "darwin":
            config_dir = os.path.join(str(Path.home()), 'Library', 'Application Support', 'CodeMerger')
        else:
            config_dir = os.path.join(str(Path.home()), '.config', 'CodeMerger')

        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Application Paths
BUNDLE_DIR = get_bundle_dir()
PERSISTENT_DATA_DIR = get_persistent_data_dir()

CONFIG_FILE_PATH = os.path.join(PERSISTENT_DATA_DIR, 'config.json')

DEFAULT_FILETYPES_CONFIG_PATH = os.path.join(BUNDLE_DIR, 'default_filetypes.json')

# Project Starter Template Paths
BOILERPLATE_DIR = os.path.join(BUNDLE_DIR, 'assets', 'boilerplate')
REFERENCE_DIR = os.path.join(BUNDLE_DIR, 'assets', 'reference')

ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'icon.ico')

LOGO_MASK_PATH = os.path.join(BUNDLE_DIR, 'assets', 'logo_mask.png')
LOGO_MASK_SMALL_PATH = os.path.join(BUNDLE_DIR, 'assets', 'logo_mask_small.png')

NEW_FILES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'newfiles.png')
NEW_FILES_MANY_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'newfiles_many.png')

FOLDER_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'folder.png')
FOLDER_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'folder_active.png')

FOLDER_REVEAL_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'folder_small.png')

TRASH_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'trash.png')

EDIT_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'edit.png')

VERSION_FILE_PATH = os.path.join(BUNDLE_DIR, 'version.txt')

COMPACT_MODE_CLOSE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'compactmode_close.png')

DEFAULTS_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'defaults.png')

EXTRA_FILES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'extra_files.png')
EXTRA_FILES_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'extra_files_active.png')

GIT_FILES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'git_files.png')
GIT_FILES_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'git_files_active.png')

PATHS_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'paths.png')
PATHS_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'paths_active.png')

ORDER_REQUEST_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'order_request.png')

SETTINGS_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'settings.png')
FILETYPES_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'filetypes.png')
SETTINGS_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'settings_active.png')
FILETYPES_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'filetypes_active.png')

# Project Starter Icons
PROJECT_STARTER_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'project_starter.png')
PROJECT_STARTER_ACTIVE_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'project_starter_active.png')
LOCKED_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'locked.png')
UNLOCKED_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'unlocked.png')

# Info Mode Icons
INFO_ICON_PATH = os.path.join(BUNDLE_DIR, 'assets', 'info.png')
INFO_ICON_ACTIVE_PATH = os.path.join(BUNDLE_DIR, 'assets', 'info_active.png')

REGISTRY_KEY_PATH = r"Software\CodeMerger"

UPDATE_CLEANUP_FILE_PATH = os.path.join(PERSISTENT_DATA_DIR, 'update_cleanup.json')
```

--- End of file ---

--- File: `src/core/prompts.py` ---

```python
"""
Contains all large text blocks used as prompts for Language Models.
Separating these from logic improves maintainability and readability.
"""

# Default Project Instructions
DEFAULT_COPY_MERGED_PROMPT = "Here is the most recent code, please use this when making changes:\n"

DEFAULT_INTRO_PROMPT = "We are working on REPLACE_ME.\n\nQUESTION\n\n"

DEFAULT_OUTRO_PROMPT = """Stylistic Guidelines (The Harness Standard)

DO:
- make sure empty lines are actually empty: avoid generating lines of spaces or tabs
- use only concise, single-sentence, unnumbered comments without trailing punctuation or XML tags
- always place closing triple backticks (```) on their own, new line
- Present Tense: All rationale in comments must be in the present tense (e.g., 'Checks for null' instead of 'Checked for null')

Do NOT:
- remove my original comments
- shorten code with comments like `... Unchanged` or `Same as before`
- call something "final" or "definitive"; it usually isn't
- use double newlines between code
- add comments if the code itself makes it pretty clear what it does
- remove logs when you think you have solved a problem; wait for confirmation that the issue is resolved
- use !important to solve HTML styling issues
- no history: do not add comments describing previous states, fixed bugs, or renames. Git handles history; the source should only describe the current state.

Use the following format if you want to add temporary notification comments: // [KEYWORD] Comment (e.g., [FIX] Now using correct value, [MODIFIED] Improved algorithm). These comments are transient and exist only to show the user what you've changed. If you find them in code you are reviewing, remove these comments as the user will have already seen them."""

COMMENT_CLEANUP_PROMPT = """Let's clean up the comments. Remove all LLM tags (e.g., [MODIFIED], [FIX]), transient feedback, and changelogs. Git handles history; the code shouldn't.

Directive: Optimize the code for a programmer that has never seen this code before. Assume they understand standard syntax.

The "Surprise Factor" Test:
Only keep a comment if an experienced developer would be surprised by the code.
- Keep comments for workarounds (fixing library bugs/race conditions).
- Keep comments for atypical choices (why library X was used instead of Y).
- Keep comments for complex business logic.
- DELETE everything else.

1. Remove Redundancy: Delete comments that explain the obvious or simply restate the code in English
2. Keep Structure: Retain section headers (e.g., "Navigation", "API Logic") that help file navigation
3. Keep Context: Retain comments that explain the "why" behind complex logic, but clean up the wording
4. Clean Tags: Remove the [TAG] prefix. If the comment remains useful without the tag, keep it; otherwise, delete it
5. Avoid comments directly behind code
6. Do not use numbering in comments
7. Remove dots from the end of single line comments
8. Single line comments for single sentences are preferred, even if that makes them long
9. No History: Delete comments describing changes, fixes, or renames. If a comment refers to the code's past state, delete it
10. Present Tense: All rationale must be in the present tense

Do not change code, only comments."""

# Project Starter Prompt Templates

STARTER_CONCEPT_DEFAULT_GOAL = "The plan is to build a..."

STARTER_CONCEPT_PROMPT_INTRO = "Based on the following user goal, generate a full project concept document."

STARTER_CONCEPT_PROMPT_CORE_INSTR = """
### Core Instructions
1. Fill in every section with specific details relevant to the user's goal.
2. Ensure the 'User Flows' section covers the complete lifecycle of the main data entity.
3. **Readability & Formatting:** Use frequent line breaks and short paragraphs to avoid dense blocks of text. Utilize Markdown elements (bullet points, bolding) to ensure the document is highly readable and visually structured.
"""

STARTER_STACK_PROMPT_INTRO = "Based on the project concept and the developer's experience, recommend the best technical stack for this project."

STARTER_STACK_PROMPT_INSTR = """
### Instructions
1. Analyze requirements against known skills.
2. Return the recommended stack as a raw JSON list of strings.
   - Example: ["Python 3.10", "Flask"]
3. Return ONLY the JSON.
"""

STARTER_TODO_PROMPT_INTRO = """You are a Technical Project Manager.
Based on the following project Concept and Tech Stack, create a detailed TODO plan."""

STARTER_TODO_PROMPT_INSTR = """
### Instructions
1. **Analyze Relevance:** Compare the Reference Template against the Concept. **SKIP** any phase from the template that is not appropriate for this specific project (e.g., remove 'Database' for a static site, remove 'API' for a CLI tool).
2. **Adapt Tasks:** For the phases you keep, adapt the tasks to be specific to this project (e.g., change 'Create tables' to 'Create `users` and `products` tables').
3. **Format & Custom Phases:** You MUST output the plan using `<SECTION name="Phase Name">` followed by content and closing with `</SECTION>`.
   - Suggested Phase Names: {headers_str}.
   - **ADDITIONAL PHASES:** You are encouraged to add project-specific phases if the suggested list is insufficient. Simply create a descriptive name for any new section.
   - **DO NOT** output sections for phases you decided to skip.
4. **THE DEPLOYMENT ANCHOR (CRITICAL):** Regardless of how many custom phases you add, the "Deployment" phase MUST be the final section of your response. All other phases (suggested or custom) must be placed before it.
"""

STARTER_GENERATE_MASTER_INTRO = "You are a senior developer creating a boilerplate for: {name}\nStack: {stack}"

STARTER_GENERATE_MASTER_INSTR = """
### Core Instructions
1. **Select & Rename:** Select the appropriate `go_*.bat` script for the stack and rename it to `go.bat`.
2. **Mandatory README:** You MUST output the `README.md` file. Populate it (or create it) with the project title, the pitch, and specific setup steps derived from the stack.
3. **BOILERPLATE ONLY:** DO NOT implement any of the actual tasks, code, or features described in the TODO plan yet. Your job is ONLY to set up the skeleton/infrastructure (README, batch scripts, config files). Do NOT create source files (like *.js, *.py, *.css) unless they are explicitly part of the standard boilerplate provided above.
4. **Short Description:** At the start of your response, provide a short, one-sentence description (noun phrase) of exactly what this project is (e.g., 'a Python-based CLI tool for image processing'). This description must grammatically fit into the sentence 'We are working on [PITCH].' Wrap this description in `<PITCH>` tags. **You MUST close the tag with `</PITCH>`. Example: `<PITCH>a new CLI tool</PITCH>`.**
5. **Project Color:** Choose a single accent hex color code (e.g. #4A90E2) that fits the brand or technology of this project. Wrap it in `<COLOR>` tags. Example: `<COLOR>#4A90E2</COLOR>`.
6. **Output Format:** Return the complete source code for every file you are modifying or creating using this exact format:
--- File: `path/to/file.ext` ---
```language
[content]
```
--- End of file ---

CRITICAL: Do NOT omit the '--- End of file ---' marker for any block.
"""

STARTER_REWRITE_PROMPT_TEMPLATE = """You are a Project Editor.
The user has provided a global instruction to modify the project plan.
Your task is to update the drafts listed below to comply with this instruction.

### Summary Requirement
You MUST start your response with a brief summary and explanation of what you changed and why.
Wrap this summary in `<NOTES>` tags.
Example: <NOTES>I updated the database schema to include a 'status' field and revised the user flow accordingly.</NOTES>

### User Instruction
{instruction}{references}

### Content to Update
{targets}

### Instructions
1. Review the User Instruction.
2. Rewrite the content in the 'Content to Update' section to incorporate this instruction.
3. {consistency_instr}
4. {target_instructions}
5. Output the summary in `<NOTES>`, followed by the updated content."""

STARTER_SYNC_PROMPT_TEMPLATE = """You are a Consistency Engine. The user has modified section **{current_name}**.
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

STARTER_QUESTION_PROMPT_TEMPLATE = """### {context_label}
{context_content}

### Focus: {focus_name}
{focus_content}

### Question
{question}

Instruction: {instruction_suffix}"""
```

--- End of file ---

--- File: `src/core/utils.py` ---

```python
import os
import json
import fnmatch
import hashlib
import tiktoken
import sys
from pathlib import Path
from ..core.paths import (
    CONFIG_FILE_PATH, DEFAULT_FILETYPES_CONFIG_PATH, VERSION_FILE_PATH, PERSISTENT_DATA_DIR
)
from ..core.prompts import (
    DEFAULT_COPY_MERGED_PROMPT, DEFAULT_INTRO_PROMPT, DEFAULT_OUTRO_PROMPT
)
from ..constants import (
    TOKEN_COUNT_ENABLED_DEFAULT,
    ADD_ALL_WARNING_THRESHOLD_DEFAULT,
    NEW_FILE_ALERT_THRESHOLD_DEFAULT
)

# Reference holds the lock for the application lifetime
_instance_lock = None

def is_another_instance_running():
    """
    Identifies active instances via Named Mutex on Windows or file lock on POSIX
    Returns False if CM_DEV_MODE environment variable is active
    """
    global _instance_lock

    if os.environ.get('CM_DEV_MODE') == '1':
        return False

    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32

            mutex_name = "Global\\CodeMerger_Instance_Mutex_C06CFB28"

            _instance_lock = kernel32.CreateMutexW(None, False, mutex_name)

            if not _instance_lock:
                return False

            # ERROR_ALREADY_EXISTS = 183
            last_error = kernel32.GetLastError()
            if last_error == 183:
                return True

            return False
        except Exception:
            return False
    else:
        try:
            import fcntl

            lock_file_path = os.path.join(PERSISTENT_DATA_DIR, 'app.lock')

            if not os.path.exists(PERSISTENT_DATA_DIR):
                os.makedirs(PERSISTENT_DATA_DIR, exist_ok=True)

            _instance_lock = open(lock_file_path, 'w')

            try:
                # Attempt non-blocking exclusive lock
                fcntl.lockf(_instance_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return False
            except (IOError, BlockingIOError):
                return True
        except Exception:
            return False

def strip_markdown_wrapper(text):
    """
    Removes triple backtick wrappers from a string
    """
    if not text:
        return ""

    clean_text = text.strip()
    if clean_text.startswith("```") and clean_text.endswith("```"):
        first_newline = clean_text.find('\n')
        if first_newline != -1:
            return clean_text[first_newline+1:-3].strip()

    return clean_text

def get_token_count_for_text(text):
    """Calculates the token count for a string"""
    try:
        # Uses cl100k_base encoding for compatibility with gpt-4
        encoding = tiktoken.get_encoding("cl100k_base")
        # Counts all tokens including special sequences
        return len(encoding.encode(text, disallowed_special=()))
    except Exception:
        return -1

def get_file_hash(full_path):
    """Calculates the SHA1 hash of file content"""
    try:
        with open(full_path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except (IOError, OSError):
        return None

def _get_default_config_dict():
    """Returns a dictionary with default application settings"""
    return {
        'active_directory': '',
        'default_editor': '',
        'user_experience': '',
        'scan_for_secrets': False,
        'last_update_check': None,
        'enable_new_file_check': True,
        'new_file_check_interval': 5,
        'copy_merged_prompt': DEFAULT_COPY_MERGED_PROMPT,
        'default_intro_prompt': DEFAULT_INTRO_PROMPT,
        'default_outro_prompt': DEFAULT_OUTRO_PROMPT,
        'token_count_enabled': TOKEN_COUNT_ENABLED_DEFAULT,
        'token_limit': 0,
        'enable_compact_mode_on_minimize': True,
        'add_all_warning_threshold': ADD_ALL_WARNING_THRESHOLD_DEFAULT,
        'new_file_alert_threshold': NEW_FILE_ALERT_THRESHOLD_DEFAULT,
        'show_feedback_on_paste': True,
        'info_mode_active': True,
        'user_lists': {
            'recent_projects': [],
            'filetypes': []
        }
    }

def _create_and_get_default_config():
    """
    Initializes configuration from the default template and saves to disk
    """
    config = _get_default_config_dict()
    try:
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            config['user_lists']['filetypes'] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    save_config(config)
    return config

def load_config():
    """
    Loads configuration using a non-destructive reconciliation strategy
    Merges user values with the default template and applies necessary migrations
    """
    defaults = _get_default_config_dict()

    try:
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            defaults['user_lists']['filetypes'] = json.load(f)
    except Exception:
        pass

    if not os.path.exists(CONFIG_FILE_PATH):
        return _create_and_get_default_config()

    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            loaded_config = json.load(f)
    except (json.JSONDecodeError, IOError):
        return _create_and_get_default_config()

    migration_occurred = False

    # Key Migrations (Legacy Formats)
    if 'recent_projects' in loaded_config or 'filetypes' in loaded_config or 'recent_directories' in loaded_config:
        migration_occurred = True
        user_lists = loaded_config.setdefault('user_lists', {})
        if 'recent_projects' in loaded_config:
            user_lists['recent_projects'] = loaded_config.pop('recent_projects', [])
        elif 'recent_directories' in loaded_config:
            user_lists['recent_projects'] = loaded_config.pop('recent_directories', [])
        if 'filetypes' in loaded_config:
            user_lists['filetypes'] = loaded_config.pop('filetypes', [])

    if 'line_count_enabled' in loaded_config:
        loaded_config['token_count_enabled'] = loaded_config.pop('line_count_enabled')
        migration_occurred = True

    for old_key in ['default_parent_folder', 'check_for_updates', 'line_count_threshold', 'token_count_threshold']:
        if old_key in loaded_config:
            loaded_config.pop(old_key)
            migration_occurred = True

    # Deep Reconciliation
    # Ensures all current keys exist without wiping user settings
    final_config = defaults.copy()

    for key in defaults:
        if key not in loaded_config:
            # Prevents forced saves on boot unless essential configuration is missing
            if key != 'info_mode_active':
                migration_occurred = True

    final_config.update(loaded_config)

    if 'user_lists' in loaded_config:
        final_config['user_lists'] = defaults['user_lists'].copy()
        final_config['user_lists'].update(loaded_config['user_lists'])

    if migration_occurred:
        save_config(final_config)

    return final_config

def save_config(config):
    """
    Saves application configuration to disk
    Operates on a copy to avoid mutating the in-memory object
    """
    export_data = config.copy()

    user_lists_data = export_data.pop('user_lists', {'recent_projects': [], 'filetypes': []})

    if isinstance(user_lists_data.get('filetypes'), list):
        user_lists_data['filetypes'].sort(key=lambda item: item['ext'])

    export_data['user_lists'] = user_lists_data

    try:
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    except IOError as e:
        print(f"Error saving configuration: {e}")

def update_and_get_new_filetypes():
    """
    Synchronizes local filetype settings with the bundled default template
    Returns a list of newly added filetype dictionaries
    """
    config = load_config()
    user_lists = config.setdefault('user_lists', {})
    local_filetypes = user_lists.get('filetypes', [])

    try:
        with open(DEFAULT_FILETYPES_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            default_filetypes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    local_map = {ft['ext']: ft for ft in local_filetypes}
    default_map = {ft['ext']: ft for ft in default_filetypes}

    newly_added = []
    config_changed = False

    # Update local metadata formats
    for ext, local_ft in local_map.items():
        if 'description' not in local_ft or 'default' not in local_ft:
            config_changed = True
            default_ft = default_map.get(ext)
            if default_ft:
                local_ft['description'] = default_ft.get('description', '')
                local_ft['default'] = True
            else:
                local_ft.setdefault('description', '')
                local_ft['default'] = False

    # Incorporate new default filetypes
    for ext, default_ft in default_map.items():
        if ext not in local_map:
            config_changed = True
            local_filetypes.append(default_ft.copy())
            newly_added.append(default_ft.copy())

    if config_changed:
        user_lists['filetypes'] = local_filetypes
        save_config(config)

    return newly_added

def load_all_filetypes():
    config = load_config()
    return config.get('user_lists', {}).get('filetypes', [])

def save_filetypes(filetypes_list):
    config = load_config()
    config.setdefault('user_lists', {})['filetypes'] = filetypes_list
    save_config(config)

def load_active_file_extensions():
    all_types = load_all_filetypes()
    return {item['ext'] for item in all_types if item.get('active', False)}

def parse_gitignore(base_dir):
    """
    Parses all .gitignore files starting from the project root
    """
    gitignore_data = []
    for root, dirs, files in os.walk(base_dir, topdown=True):
        if '.git' in dirs:
            dirs.remove('.git')

        if '.gitignore' in files:
            gitignore_path = os.path.join(root, '.gitignore')
            try:
                with open(gitignore_path, 'r', encoding='utf-8-sig') as f:
                    patterns = [
                        line.strip() for line in f
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    if patterns:
                        gitignore_data.append((Path(root), patterns))
            except (IOError, OSError):
                pass

        # Prunes ignored directories in-place to prevent os.walk from entering them
        if gitignore_data:
            dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), base_dir, gitignore_data)]

    return gitignore_data

def is_ignored(path, base_dir, gitignore_data):
    """
    Determines if a path should be ignored based on parsed .gitignore rules
    """
    target_path = Path(path)
    if '.git' in target_path.parts:
        return True

    is_ignored_flag = False
    for gitignore_dir, patterns in gitignore_data:
        try:
            relative_path = target_path.relative_to(gitignore_dir)
        except ValueError:
            continue

        relative_path_str = relative_path.as_posix()

        for p_orig in patterns:
            p = p_orig.strip()
            if not p: continue

            is_negated = p.startswith('!')
            if is_negated:
                p = p[1:]

            # Matching strategy depends on whether the pattern contains a slash
            contains_slash = '/' in p

            is_dir_only = p.endswith('/')
            if is_dir_only:
                p = p.rstrip('/')

            match = False
            if not contains_slash:
                if any(fnmatch.fnmatch(part, p) for part in relative_path.parts):
                    match = True
            else:
                p_to_match = p.lstrip('/')
                if fnmatch.fnmatch(relative_path_str, p_to_match) or \
                   relative_path_str.startswith(p_to_match + '/'):
                    match = True

            if match and is_dir_only:
                if relative_path_str == p and not target_path.is_dir():
                    match = False

            if match:
                if is_negated:
                    is_ignored_flag = False
                else:
                    is_ignored_flag = True
    return is_ignored_flag

def load_app_version():
    """
    Returns the version string from version.txt
    """
    try:
        version_data = {}
        with open(VERSION_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    version_data[key.strip().lower()] = value.strip()

        major = version_data.get('major', '?')
        minor = version_data.get('minor', '?')
        revision = version_data.get('revision', '?')

        return f"v{major}.{minor}.{revision}"

    except (FileNotFoundError, IndexError):
        return "v?.?.?"
```

--- End of file ---

--- File: `src/core/logger.py` ---

```python
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from .paths import PERSISTENT_DATA_DIR
from .. import constants as c

log = logging.getLogger("CodeMerger")

class DummyStream:
    """Swallows writes to prevent crashes when standard streams are unavailable"""
    def write(self, data):
        pass
    def flush(self):
        pass

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception hook to log unhandled exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))

def setup_logging():
    """Configures application-wide logging"""

    # In windowed mode sys.stdout/stderr are None; DummyStream prevents attribute errors
    if sys.stdout is None:
        sys.stdout = DummyStream()
    if sys.stderr is None:
        sys.stderr = DummyStream()

    log.setLevel(logging.INFO)

    log.propagate = False

    # Rich Handler for console output
    if not log.handlers:
        # Only uses Rich if a functional TTY exists
        if sys.stdout and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            try:
                console_handler = RichHandler(
                    rich_tracebacks=True,
                    tracebacks_show_locals=True
                )
                console_handler.setFormatter(logging.Formatter("%(message)s"))
                log.addHandler(console_handler)
            except Exception:
                pass

        # File Handler for persistent logging
        try:
            log_path = os.path.join(PERSISTENT_DATA_DIR, c.LOG_FILENAME)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=c.LOG_MAX_BYTES,
                backupCount=c.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            log.addHandler(file_handler)
        except Exception as e:
            pass

    sys.excepthook = handle_exception
```

--- End of file ---

--- File: `src/core/registry.py` ---

```python
import winreg
import sys
from ..core.paths import REGISTRY_KEY_PATH

def get_setting(name, default_value):
    """
    Reads a setting value, checking the user's preferences (HKCU) first,
    then falling back to the system-wide default (HKLM).
    """
    if sys.platform != "win32":
        return default_value # Registry is a Windows-only feature

    # Try to read the user-specific setting from HKEY_CURRENT_USER
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, name)
            if reg_type == winreg.REG_DWORD:
                return bool(value)
            return value
    except FileNotFoundError:
        # User-specific key or value doesn't exist, so fall back to system-wide.
        pass
    except Exception:
        # A different error occurred, fall back.
        pass

    # Fallback: Try to read the system-wide default from HKEY_LOCAL_MACHINE
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, name)
            if reg_type == winreg.REG_DWORD:
                return bool(value)
            return value
    except FileNotFoundError:
        # No system-wide default found either.
        return default_value
    except Exception:
        return default_value

def save_setting(name, value):
    """
    Saves a setting to the current user's personal registry key (HKCU).
    This allows user preferences to override system-wide defaults.
    """
    if sys.platform != "win32":
        return # Cannot save to registry on non-Windows platforms

    try:
        # Always write to HKEY_CURRENT_USER to store the user's choice.
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH) as key:
            if isinstance(value, bool):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, 1 if value else 0)
            elif isinstance(value, str):
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            elif isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
    except Exception:
        # Silently fail if registry writing is not possible.
        pass
```

--- End of file ---

--- File: `src/app_state.py` ---

```python
import os
from datetime import datetime
from .core.utils import load_config, save_config
from .constants import RECENT_PROJECTS_MAX
from .core.prompts import DEFAULT_COPY_MERGED_PROMPT
from .core.registry import get_setting

class AppState:
    """
    Manages the application's persistent state loaded from and saved to config.json
    """
    def __init__(self):
        self.config = load_config()
        self.active_directory = self.config.get('active_directory', '')
        self.recent_projects = self.config.get('user_lists', {}).get('recent_projects', [])
        self.default_editor = self.config.get('default_editor', '')
        self.scan_for_secrets = self.config.get('scan_for_secrets', False)
        self.copy_merged_prompt = self.config.get('copy_merged_prompt', DEFAULT_COPY_MERGED_PROMPT)
        self.check_for_updates = get_setting('AutomaticUpdates', True)
        self.last_update_check = self.config.get('last_update_check', None)
        self.enable_compact_mode_on_minimize = self.config.get('enable_compact_mode_on_minimize', True)

        # Info Mode visibility state
        self.info_mode_active = self.config.get('info_mode_active', True)

        # List of callbacks to synchronize info mode visibility across windows
        self._info_observers = []

        self._validate_active_dir()
        self._prune_recent_projects()

    def register_info_observer(self, callback):
        """Registers a callback function to be notified of info mode changes."""
        if callback not in self._info_observers:
            self._info_observers.append(callback)

    def toggle_info_mode(self):
        """Toggles the info mode state and notifies all registered observers."""
        self.info_mode_active = not self.info_mode_active
        self.config['info_mode_active'] = self.info_mode_active
        self._save()

        for observer in self._info_observers:
            try:
                observer(self.info_mode_active)
            except Exception:
                pass

    def _validate_active_dir(self):
        """Checks for existence of the active directory. Resets if not found"""
        if self.active_directory and not os.path.isdir(self.active_directory):
            self.active_directory = ''
            self.config['active_directory'] = ''
            self._save()

    def _prune_recent_projects(self):
        """Removes non-existent directories from the recent list"""
        initial_count = len(self.recent_projects)
        self.recent_projects = [d for d in self.recent_projects if os.path.isdir(d)]
        if len(self.recent_projects) != initial_count:
            self.config.setdefault('user_lists', {})['recent_projects'] = self.recent_projects
            self._save()

    def _save(self):
        """Saves the current state back to the config file"""
        save_config(self.config)

    def reload(self):
        """Reloads the configuration from disk, e.g., after settings change"""
        self.config = load_config()
        self.default_editor = self.config.get('default_editor', '')
        self.scan_for_secrets = self.config.get('scan_for_secrets', False)
        self.copy_merged_prompt = self.config.get('copy_merged_prompt', DEFAULT_COPY_MERGED_PROMPT)
        self.enable_compact_mode_on_minimize = self.config.get('enable_compact_mode_on_minimize', True)
        self.info_mode_active = self.config.get('info_mode_active', True)
        # Reload from registry as well
        self.check_for_updates = get_setting('AutomaticUpdates', True)
        self.last_update_check = self.config.get('last_update_check', None)

    def update_last_check_date(self):
        """Updates the timestamp for the last update check to today"""
        now_iso = datetime.now().isoformat()
        self.last_update_check = now_iso
        self.config['last_update_check'] = now_iso
        self._save()

    def update_active_dir(self, new_dir):
        """Sets a new active directory and updates the recent list"""
        if not new_dir or not os.path.isdir(new_dir):
            return False

        self.active_directory = new_dir
        self.config['active_directory'] = new_dir

        if new_dir in self.recent_projects:
            self.recent_projects.remove(new_dir)
        self.recent_projects.insert(0, new_dir)
        self.recent_projects = self.recent_projects[:RECENT_PROJECTS_MAX]
        self.config.setdefault('user_lists', {})['recent_projects'] = self.recent_projects

        self._save()
        return True

    def remove_recent_project(self, path_to_remove):
        """
        Removes a directory from the recent list. If the removed path is also
        the active directory, the active directory is cleared.
        Returns True if the active directory was cleared, False otherwise.
        """
        cleared_active = False
        if path_to_remove in self.recent_projects:
            self.recent_projects.remove(path_to_remove)
            self.config.setdefault('user_lists', {})['recent_projects'] = self.recent_projects

            if path_to_remove == self.active_directory:
                self.active_directory = ''
                self.config['active_directory'] = ''
                cleared_active = True

            self._save()

        return cleared_active
```

--- End of file ---

--- File: `src/core/project_config.py` ---

```python
import os
import json
import random
import re
import colorsys
import hashlib
import tempfile
from pathlib import Path
from ..constants import COMPACT_MODE_BG_COLOR, FONT_LUMINANCE_THRESHOLD
from .utils import get_token_count_for_text

def _get_file_hash(full_path):
    try:
        with open(full_path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except (IOError, OSError):
        return None

def _generate_random_color():
    """Generates a random visually pleasing hex color string"""
    hue = random.random()
    saturation = random.uniform(0.5, 0.7)
    value = random.uniform(0.6, 0.8)
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    r_int, g_int, b_int = int(r * 255), int(g * 255), int(b * 255)
    return f"#{r_int:02x}{g_int:02x}{b_int:02x}"

def _calculate_font_color(hex_color):
    """Selects light or dark text based on background luminance"""
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return 'dark' if luminance > FONT_LUMINANCE_THRESHOLD else 'light'
    except (ValueError, IndexError):
        return 'light'

class ProjectConfig:
    """
    Manages loading and saving the .allcode configuration for a project directory
    New File tracking is profile-specific via unknown_files; known_files is global to the project
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.allcode_path = os.path.join(self.base_dir, '.allcode')
        self.project_name = os.path.basename(self.base_dir)
        self.project_color = COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.known_files = []

        self.profiles = {}
        self.active_profile_name = "Default"
        self._last_mtime = 0

        # Safety latch: prevent saving if an existing file failed to load correctly
        self._load_successful = False

    @staticmethod
    def read_project_display_info(base_dir):
        allcode_path = os.path.join(base_dir, '.allcode')
        project_name = os.path.basename(base_dir)
        project_color = COMPACT_MODE_BG_COLOR

        if not os.path.isfile(allcode_path):
            return project_name, project_color

        try:
            with open(allcode_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if not content: return project_name, project_color
                data = json.loads(content)
                project_name = data.get('project_name', project_name)
                color_value = data.get('project_color')
                if color_value and isinstance(color_value, str) and re.match(r'^#[0-9a-fA-F]{6}$', color_value):
                        project_color = color_value
        except (json.JSONDecodeError, IOError):
            pass

        return project_name, project_color

    def get_active_profile(self):
        if self.active_profile_name not in self.profiles:
            self.profiles[self.active_profile_name] = self._create_empty_profile()
        return self.profiles[self.active_profile_name]

    def _create_empty_profile(self):
        return {
            "selected_files": [],
            "total_tokens": 0,
            "intro_text": "",
            "outro_text": "",
            "expanded_dirs": [],
            "unknown_files": []
        }

    @property
    def selected_files(self):
        return self.get_active_profile().get('selected_files', [])

    @selected_files.setter
    def selected_files(self, value):
        self.get_active_profile()['selected_files'] = value

    @property
    def total_tokens(self):
        return self.get_active_profile().get('total_tokens', 0)

    @total_tokens.setter
    def total_tokens(self, value):
        self.get_active_profile()['total_tokens'] = value

    @property
    def intro_text(self):
        return self.get_active_profile().get('intro_text', '')

    @intro_text.setter
    def intro_text(self, value):
        self.get_active_profile()['intro_text'] = value

    @property
    def outro_text(self):
        return self.get_active_profile().get('outro_text', '')

    @outro_text.setter
    def outro_text(self, value):
        self.get_active_profile()['outro_text'] = value

    @property
    def expanded_dirs(self):
        return set(self.get_active_profile().get('expanded_dirs', []))

    @expanded_dirs.setter
    def expanded_dirs(self, value):
        self.get_active_profile()['expanded_dirs'] = sorted(list(value))

    @property
    def unknown_files(self):
        return self.get_active_profile().get('unknown_files', [])

    @unknown_files.setter
    def unknown_files(self, value):
        self.get_active_profile()['unknown_files'] = sorted(list(set(value)))

    def load(self):
        """Loads and reconciles project settings using defensive collision checks"""
        data = {}
        config_was_updated = False
        files_were_cleaned_globally = False

        if not os.path.isfile(self.allcode_path):
            self._load_successful = True # Valid state for new projects
            return False

        try:
            self._last_mtime = os.path.getmtime(self.allcode_path)

            # Defensive: Don't load if the file is currently 0 bytes (mid-write lock)
            if os.path.getsize(self.allcode_path) == 0:
                raise RuntimeError("Config file is empty or locked.")

            with open(self.allcode_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if content:
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError:
                        # Attempt recovery from partial write artifacts
                        json_start_index = content.find('{')
                        if json_start_index != -1:
                            json_content = content[json_start_index:]
                            data = json.loads(json_content)
                            config_was_updated = True
                        else:
                            raise RuntimeError("Config file contains no valid JSON.")
        except (json.JSONDecodeError, IOError, OSError) as e:
            raise RuntimeError(f"Failed to read project config: {e}")

        # Final sanity check: if the file exists but we ended up with no data, abort to protect against wipe
        if not data:
            raise RuntimeError("Config file contained an empty JSON object.")

        self.project_name = data.get('project_name', os.path.basename(self.base_dir))
        color_value = data.get('project_color')
        font_color_value = data.get('project_font_color')

        if 'project_name' not in data: config_was_updated = True
        if not color_value or not isinstance(color_value, str) or not re.match(r'^#[0-9a-fA-F]{6}$', color_value):
            self.project_color = _generate_random_color()
            config_was_updated = True
        else:
            self.project_color = color_value

        if not font_color_value or font_color_value not in ['light', 'dark']:
            self.project_font_color = _calculate_font_color(self.project_color)
            config_was_updated = True
        else:
            self.project_font_color = font_color_value

        # Profile Initialization
        if 'profiles' in data and isinstance(data['profiles'], dict):
            self.profiles = data.get('profiles', {})
            self.active_profile_name = data.get('active_profile', 'Default')
            if not self.profiles:
                self.profiles['Default'] = self._create_empty_profile()
                self.active_profile_name = 'Default'
                config_was_updated = True
        elif 'selected_files' in data:
            # Reconcile legacy flat format
            config_was_updated = True
            default_profile = self._create_empty_profile()
            default_profile['intro_text'] = data.get('intro_text', '')
            default_profile['outro_text'] = data.get('outro_text', '')
            default_profile['expanded_dirs'] = sorted(list(set(data.get('expanded_dirs', []))))
            default_profile['selected_files'] = data.get('selected_files', [])
            default_profile['total_tokens'] = data.get('total_tokens', 0)
            self.profiles = {'Default': default_profile}
            self.active_profile_name = 'Default'
        else:
            raise RuntimeError("Config file is malformed: missing project data keys.")

        # Known Files Extraction
        all_found_known = set(data.get('known_files', []))
        for p_data in self.profiles.values():
            if 'known_files' in p_data:
                all_found_known.update(p_data.pop('known_files', []))
                config_was_updated = True
            if 'unknown_files' not in p_data:
                p_data['unknown_files'] = []
                config_was_updated = True

        self.known_files = sorted(list(all_found_known))

        for profile_name, profile_data in self.profiles.items():
            profile_data['unknown_files'] = sorted(list(set(profile_data.get('unknown_files', []))))
            files_cleaned_in_profile, profile_updated = self._clean_profile_files(profile_data)
            if files_cleaned_in_profile:
                files_were_cleaned_globally = True
            if profile_updated:
                config_was_updated = True

        # Mark load as successful only after full data validation
        self._load_successful = True

        if config_was_updated or files_were_cleaned_globally:
            self.save()

        return files_were_cleaned_globally

    def _clean_profile_files(self, profile_data):
        profile_was_updated = False
        original_selection = profile_data.get('selected_files', [])
        is_new_format = original_selection and isinstance(original_selection[0], dict) and 'path' in original_selection[0]

        cleaned_selection = []
        if not is_new_format:
            if original_selection: profile_was_updated = True
            for f_path in original_selection:
                full_path = os.path.join(self.base_dir, f_path)
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
                        mtime = os.path.getmtime(full_path)
                        file_hash = _get_file_hash(full_path)
                        tokens = get_token_count_for_text(content)
                        lines = content.count('\n') + 1
                        cleaned_selection.append({'path': f_path, 'mtime': mtime, 'hash': file_hash, 'tokens': tokens, 'lines': lines})
                    except OSError: continue
        else:
            for f_info in original_selection:
                if 'tokens' not in f_info or 'lines' not in f_info:
                    profile_was_updated = True
                cleaned_selection.append(f_info)

        profile_data['selected_files'] = cleaned_selection
        files_were_cleaned = len(cleaned_selection) < len(original_selection)

        if files_were_cleaned:
            profile_data['total_tokens'] = sum(f.get('tokens', 0) for f in cleaned_selection)
            profile_was_updated = True

        return files_were_cleaned, profile_was_updated

    def save(self):
        """Saves configuration using an atomic replacement to prevent data wipes during collisions"""
        # Block saving if a previous load of an existing file failed
        if os.path.isfile(self.allcode_path) and not self._load_successful:
            return

        final_data = {
            "_info": "For information about this file, see: https://github.com/DrSiemer/CodeMerger/",
            "project_name": self.project_name,
            "project_color": self.project_color,
            "project_font_color": self.project_font_color,
            "active_profile": self.active_profile_name,
            "profiles": self.profiles,
            "known_files": sorted(list(set(self.known_files)))
        }

        fd, temp_path = tempfile.mkstemp(dir=self.base_dir, prefix='.allcode_tmp_')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2)
            os.replace(temp_path, self.allcode_path)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

        if os.path.isfile(self.allcode_path):
            self._last_mtime = os.path.getmtime(self.allcode_path)

    def has_external_changes(self):
        """Identifies file modifications on disk since the last internal access"""
        if not os.path.isfile(self.allcode_path):
            return False
        try:
            if os.path.getsize(self.allcode_path) == 0:
                return False
            return os.path.getmtime(self.allcode_path) != self._last_mtime
        except OSError:
            return False

    def get_profile_names(self):
        return sorted(list(self.profiles.keys()))

    def create_new_profile(self, new_name, copy_files, copy_instructions):
        if new_name in self.profiles:
            return False

        if copy_files or copy_instructions:
            source_profile = self.get_active_profile()
            new_profile = {
                "selected_files": [dict(f) for f in source_profile.get('selected_files', [])] if copy_files else [],
                "total_tokens": source_profile.get('total_tokens', 0) if copy_files else 0,
                "intro_text": source_profile.get('intro_text', '') if copy_instructions else '',
                "outro_text": source_profile.get('outro_text', '') if copy_instructions else '',
                "expanded_dirs": source_profile.get('expanded_dirs', [])[:] if copy_files else [],
                "unknown_files": source_profile.get('unknown_files', [])[:] if copy_files else []
            }
        else:
            new_profile = self._create_empty_profile()

        self.profiles[new_name] = new_profile
        return True

    def delete_profile(self, profile_name_to_delete):
        if profile_name_to_delete == "Default" or profile_name_to_delete not in self.profiles:
            return False
        del self.profiles[profile_name_to_delete]
        return True
```

--- End of file ---

--- File: `src/core/file_scanner.py` ---

```python
import os
from ..core.utils import is_ignored
from .. import constants as c

def get_all_matching_files(base_dir, file_extensions, gitignore_patterns, always_include_paths=None):
    """
    Scans the file system and returns a flat list of all matching file paths,
    respecting .gitignore.

    Args:
        base_dir (str): Project root directory.
        file_extensions (list): List of extensions to include.
        gitignore_patterns (list): Parsed gitignore patterns.
        always_include_paths (set, optional): Set of relative paths to explicitly
                                              check and include if they exist,
                                              ignoring filters.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    matching_files = []

    def _scan_dir(current_path):
        try:
            for entry in os.scandir(current_path):
                if entry.name.lower() in c.SPECIAL_FILES_TO_IGNORE:
                    continue

                if is_ignored(entry.path, base_dir, gitignore_patterns):
                    continue

                if entry.is_dir():
                    _scan_dir(entry.path)
                elif entry.is_file():
                    file_name_lower = entry.name.lower()
                    file_ext = os.path.splitext(file_name_lower)[1]
                    if file_ext in extensions or file_name_lower in exact_filenames:
                        rel_path = os.path.relpath(entry.path, base_dir).replace('\\', '/')
                        matching_files.append(rel_path)
        except OSError:
            pass # Ignore permission errors etc

    _scan_dir(base_dir)

    # Post-scan: Explicitly check and include specific paths (e.g., selected files)
    # that might have been filtered out by gitignore or extension filters.
    if always_include_paths:
        # Convert list to set for O(1) lookups if it's not already
        found_set = set(matching_files)

        for path in always_include_paths:
            if path in found_set:
                continue

            full_path = os.path.join(base_dir, path)
            if os.path.isfile(full_path):
                # Normalizing path separators just in case
                normalized_path = path.replace('\\', '/')
                matching_files.append(normalized_path)

    return matching_files
```

--- End of file ---

--- File: `src/core/merger.py` ---

```python
import os
import json
from .. import constants as c
from .prompts import DEFAULT_COPY_MERGED_PROMPT
from .utils import get_token_count_for_text

def get_language_from_path(path):
    """Maps file extensions to Markdown code block identifiers"""
    _, ext = os.path.splitext(path)
    return c.LANGUAGE_MAP.get(ext.lower(), '')

def generate_output_string(base_dir, project_config, use_wrapper, copy_merged_prompt):
    """
    Concatenates selected files into a single machine-parseable string
    Returns the final string and a status message
    """
    if not project_config.selected_files:
        return None, "No files selected to copy"

    final_ordered_list = [f['path'] for f in project_config.selected_files]

    output_blocks = []
    skipped_files = []

    # Use fragments to build markers to avoid triggering regex when CodeMerger bundles itself
    PREFIX = "--- "
    FILE_LABEL = "File: "
    EOF_LABEL = "End of file"

    for path in final_ordered_list:
        full_path = os.path.join(base_dir, path)
        if not os.path.isfile(full_path):
            skipped_files.append(path)
            continue
        with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as code_file:
            content = code_file.read()

        language = get_language_from_path(path)

        # Build block using concatenation
        block_header = f"{PREFIX}{FILE_LABEL}`{path}` ---"
        block_footer = f"{PREFIX}{EOF_LABEL} ---"

        output_blocks.append(f"{block_header}\n\n```{language}\n{content}\n```\n\n{block_footer}")

    merged_code = '\n\n'.join(output_blocks)

    if use_wrapper:
        project_title = project_config.project_name

        # Defensive coercion ensures fields corrupted by trailing commas are handled correctly
        intro_text = project_config.intro_text
        if isinstance(intro_text, (list, tuple)):
            intro_text = "\n".join(intro_text)

        outro_text = project_config.outro_text
        if isinstance(outro_text, (list, tuple)):
            outro_text = "\n".join(outro_text)

        formatting_instruction = """**CRITICAL INSTRUCTIONS FOR CODE GENERATION - READ CAREFULLY:**

1. **MANDATORY TAGGING & CLOSING POLICY:**
   Every section of your response (Answers, Intro, Changes, Delete, Verification) MUST be explicitly wrapped in tags.
   **CRITICAL:** Every opening tag MUST have an identical closing tag.
   Format: `<INTRO>[content]</INTRO>`

2. **INTRO, ANSWERS & CHANGES (PRE-CODE):**
   Immediately before the code blocks, provide these sections in this order:
   - **<INTRO>**: Use this to provide a technical implementation plan or architectural summary.
   - **<ANSWERS TO DIRECT USER QUESTIONS>**: If the user asked a specific question (usually ending with a '?'), answer it here. If there is no question mark in the prompt, there is no question. In that case, this block MUST remain empty (use a single dash `-`). Do NOT fill it with filler text like "None" or "No questions".
   - **<CHANGES>**: List of behavioral, algorithmic, or visual changes.

3. **NO CODE TRUNCATION (STRICT REQUIREMENT):**
   - You MUST provide the **FULL, COMPLETE content** for EVERY file you modify.
   - **DO NOT** use comments like `// ... rest of code`, `/* unchanged */`, or `[previous logic here]`.
   - ZERO OMISSION POLICY: Every single line, comment, and whitespace character not explicitly targeted for change MUST be mirrored exactly from the source. I am using a diff-tool to verify; any missing existing code is a failure. Byte-for-byte mirroring of unchanged lines is MANDATORY.

4. **FUNCTIONAL PRESERVATION:**
   - Do not remove or break any existing functionality.
   - NO SILENT REFACTORING: Do not "improve," "clean up," or "simplify" any code that is not directly related to the requested change. Leave unrelated logic and comments untouched.

5. **STRICT CHANGE DETECTION & OUTPUT MINIMIZATION:**
   - ONLY output files that have actually been modified.
   - If a file's final code is **byte-for-byte identical** to the original input provided in this prompt, **DO NOT** include it in your output.
   - You may list names of unchanged files at the end of your response, but do not wrap them in code blocks.

6. **MANDATORY OUTPUT FORMAT (PARSER COMPATIBILITY):**
   - Every modified file MUST be wrapped exactly like this template, including the trailing marker:

--- File: `path/to/file.ext` ---
```[language_id]
[full unabridged code here]
```
--- End of file ---

   - **CRITICAL:** The `--- End of file ---` marker is a machine-parseable sentinel. It MUST be present after every file block.

7. **DELETE & VERIFICATION (POST-CODE):**
   Immediately following the final "--- End of file ---" marker, provide these sections:

   <DELETED FILES>
   STRICT FILE PATHS ONLY.
   FORMAT: DELETE FILE: path/to/obsolete_file.ext
   PROHIBITION: Do NOT describe code-level removals, logic deletions, or "cleanup."
   If no files were deleted from the filesystem, this section should ONLY contain a single dash (`-`). Do NOT write "None" or any other text.
   </DELETED FILES>

   <VERIFICATION>
   - Steps to test the changes.
   </VERIFICATION>

==========

You MUST format your EXACT output using this skeleton. Do not deviate from this structure:

<INTRO>
(Implementation plan)
</INTRO>

<ANSWERS TO DIRECT USER QUESTIONS>
(Answer any direct questions here, otherwise `-`)
</ANSWERS TO DIRECT USER QUESTIONS>

<CHANGES>
(List of changes)
</CHANGES>

--- File: `path/to/file.ext` ---
```language
(Full unabridged file code)
```
--- End of file ---

<DELETED FILES>
(Files to delete, or `-`)
</DELETED FILES>

<VERIFICATION>
(Testing steps)
</VERIFICATION>"""

        automation_warning = "CRITICAL: I am using an automated parser. You MUST use the exact XML tags and --- File: --- wrappers shown in the template. If you use `// ...` or `[rest of code]`, the parser will crash and your response will be useless. You must mirror every single line of the file, even unchanged ones."

        final_parts = [f"# {project_title}"]

        # Add Intro (Custom)
        if intro_text:
            final_parts.append(intro_text)

        # Add Critical Formatting Instructions
        final_parts.append(formatting_instruction)

        # Add header for code blocks
        final_parts.append("## Project Files")

        # Add the Code
        final_parts.append(merged_code)

        # Add Outro (Custom + Automation Warning)
        footer_parts = []
        if outro_text:
            footer_parts.append(outro_text)
        footer_parts.append(automation_warning)

        final_parts.append('\n\n'.join(footer_parts))

        final_content = '\n\n'.join(final_parts) + '\n'
        status_message = "Wrapped code copied as Markdown"
    else:
        if copy_merged_prompt:
            final_content = copy_merged_prompt + "\n\n" + merged_code
        else:
            final_content = merged_code
        status_message = "Merged code copied as Markdown"

    if skipped_files:
        status_message += f". Skipped {len(skipped_files)} missing file(s)"

    return final_content, status_message

def recalculate_token_count(base_dir, selected_files_info):
    """Summarizes total tokens for the current selection set"""
    if not selected_files_info:
        return 0

    all_content = []
    for file_info in selected_files_info:
        rel_path = file_info['path']
        full_path = os.path.join(base_dir, rel_path)
        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                all_content.append(f.read())
        except FileNotFoundError:
            continue

    full_text = "\n".join(all_content)
    return get_token_count_for_text(full_text)
```

--- End of file ---

--- File: `src/core/secret_scanner.py` ---

```python
import os
from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import transient_settings
from ..constants import MAX_SECRET_SCAN_REPORT_LINES

def scan_for_secrets(base_dir, files_to_scan):
    """
    Scans a list of files for secrets and returns a formatted report string
    if any are found, otherwise returns None.
    """
    secrets = SecretsCollection()
    with transient_settings({
        'plugins_used': [
            {'name': 'ArtifactoryDetector'}, {'name': 'AWSKeyDetector'},
            {'name': 'AzureStorageKeyDetector'}, {'name': 'BasicAuthDetector'},
            {'name': 'CloudantDetector'}, {'name': 'DiscordBotTokenDetector'},
            {'name': 'GitHubTokenDetector'}, {'name': 'GitLabTokenDetector'},
            {'name': 'Base64HighEntropyString', 'limit': 4.5},
            {'name': 'HexHighEntropyString', 'limit': 3.0},
            {'name': 'IbmCloudIamDetector'}, {'name': 'IbmCosHmacDetector'},
            {'name': 'IPPublicDetector'}, {'name': 'JwtTokenDetector'},
            {'name': 'KeywordDetector'}, {'name': 'MailchimpDetector'},
            {'name': 'NpmDetector'}, {'name': 'OpenAIDetector'},
            {'name': 'PrivateKeyDetector'}, {'name': 'PypiTokenDetector'},
            {'name': 'SendGridDetector'}, {'name': 'SlackDetector'},
            {'name': 'SoftlayerDetector'}, {'name': 'SquareOAuthDetector'},
            {'name': 'StripeDetector'}, {'name': 'TelegramBotTokenDetector'},
            {'name': 'TwilioKeyDetector'},
        ]
    }):
        for rel_path in files_to_scan:
            full_path = os.path.join(base_dir, rel_path)
            if os.path.isfile(full_path):
                secrets.scan_file(full_path)

    if not secrets:
        return None

    report_lines = []
    for filename, file_secrets in secrets.data.items():
        if not file_secrets:
            continue

        lines = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            pass

        for secret in file_secrets:
            rel_filename = os.path.relpath(secret.filename, base_dir).replace('\\', '/')
            report_line = f"- {rel_filename}:{secret.line_number} ({secret.type})"

            if lines and 0 < secret.line_number <= len(lines):
                line_content = lines[secret.line_number - 1].strip()
                report_line += f"\n  > {line_content}"

            report_lines.append(report_line)

    if not report_lines:
        return None

    report_string = "\n".join(report_lines[:MAX_SECRET_SCAN_REPORT_LINES])
    if len(report_lines) > MAX_SECRET_SCAN_REPORT_LINES:
        report_string += f"\n... and {len(report_lines) - MAX_SECRET_SCAN_REPORT_LINES} more."

    return report_string
```

--- End of file ---

--- File: `src/core/change_applier.py` ---

```python
import os
import re

def get_current_file_content(base_dir, rel_path):
    """Reads current file content from disk for backup/undo purposes."""
    full_path = os.path.join(base_dir, rel_path)
    if os.path.isfile(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except OSError:
            return None
    return None

def apply_single_file(base_dir, rel_path, content):
    """Writes a single file to disk, creating directories if needed."""
    try:
        path = os.path.join(base_dir, rel_path)
        dir_path = os.path.dirname(path)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        sanitized_content = _sanitize_content(path, content)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(sanitized_content)
        return True, ""
    except IOError as e:
        return False, str(e)

def delete_single_file(base_dir, rel_path):
    """Removes a single file from disk."""
    try:
        path = os.path.join(base_dir, rel_path)
        if os.path.isfile(path):
            os.remove(path)
        return True, ""
    except IOError as e:
        return False, str(e)

def _sanitize_content(path, content):
    """Cleans up whitespace and line endings"""
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]

    _, extension = os.path.splitext(path)
    if extension.lower() == '.md':
        return '\n'.join(lines)

    collapsed_lines = []
    last_line_was_empty = False
    for line in lines:
        is_empty = not line
        if is_empty and last_line_was_empty:
            continue
        collapsed_lines.append(line)
        last_line_was_empty = is_empty
    return '\n'.join(collapsed_lines)

def execute_plan(base_dir, updates, creations, deletions=None):
    """Writes the planned changes to the filesystem and deletes files marked for removal"""
    try:
        # Create new files
        for rel_path, content in creations.items():
            apply_single_file(base_dir, rel_path, content)

        # Update existing files
        for rel_path, content in updates.items():
            apply_single_file(base_dir, rel_path, content)

        # Handle Deletions
        if deletions:
            for rel_path in deletions:
                delete_single_file(base_dir, rel_path)

    except IOError as e:
        return False, f"Error writing to file: {e}"

    total_added = len(updates) + len(creations)
    total_deleted = len(deletions) if deletions else 0
    msg = f"Successfully updated {total_added} file(s)"
    if total_deleted > 0:
        msg += f" and deleted {total_deleted} file(s)"

    return True, msg + "."

def parse_and_plan_changes(base_dir, markdown_text):
    """
    Parses markdown using custom file wrappers, plans changes, and returns
    a dictionary describing the plan. This does NOT write any files.
    """
    # Define markers using concatenation to prevent self-detection
    PREFIX = "--- "
    FILE_LABEL = "File: "
    EOF_LABEL = "End of file"
    EOF_MARKER = PREFIX + EOF_LABEL + " ---"

    # Verify marker symmetry via anchored line-start counts
    start_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(FILE_LABEL), markdown_text, re.MULTILINE))
    end_count = len(re.findall(r'^' + re.escape(PREFIX) + re.escape(EOF_LABEL), markdown_text, re.MULTILINE))

    if start_count != end_count:
        return {
            'status': 'ERROR',
            'message': f"Format Error: Marker mismatch detected.\nFound {start_count} start markers but {end_count} end markers.",
            'hint': "Please ask the AI to correct its output format."
        }

    # Identify all blocks chronologically
    all_blocks = []

    # Identify tagged sections
    tags = ["ANSWERS TO DIRECT USER QUESTIONS", "INTRO", "CHANGES", "DELETED FILES", "VERIFICATION"]
    for tag in tags:
        # Accept truncated closing tag as well
        if tag == "ANSWERS TO DIRECT USER QUESTIONS":
            pattern = re.compile(rf'<{tag}>(.*?)</(?:ANSWERS TO DIRECT USER QUESTIONS|ANSWERS)>', re.DOTALL | re.IGNORECASE)
        else:
            pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.DOTALL | re.IGNORECASE)

        for match in pattern.finditer(markdown_text):
            content = match.group(1).strip()
            content_lower = content.lower().strip('.')

            # Filter out generic AI placeholder phrases
            filler_phrases = [
                "none", "n/a", "no files to delete", "no changes",
                "no conceptual questions were asked in the prompt",
                "no conceptual questions were asked",
                "no direct questions were asked", "no questions"
            ]

            if content == "-" or content_lower in filler_phrases:
                content = ""

            all_blocks.append({
                'type': 'tag',
                'tag': tag,
                'span': match.span(),
                'content': content
            })

    # Extract proposed deletions from the tag content
    deletions_proposed = []
    delete_section_content = ""
    for b in all_blocks:
        if b['tag'] == "DELETED FILES":
            delete_section_content = b['content']
            break

    if delete_section_content:
        # Match lines like "DELETE FILE: path/to/file.ext"
        del_matches = re.findall(r'DELETE FILE:\s*(.+)', delete_section_content, re.IGNORECASE)
        deletions_proposed = [m.strip().replace('\\', '/') for m in del_matches if m.strip()]

    # Identify file blocks
    file_block_regex = re.compile(
        r'^' + re.escape(PREFIX) + r'File: [`\'](?P<path>[^`\n]+)[`\'] ---\s+'   # Header
        r'```[^\n]*\s+'                                                          # Opening Backticks
        r'(?P<content>(?:(?!\n' + re.escape(EOF_MARKER) + r').)*?)'              # Content (Negative Lookahead)
        r'\s+```\s+'                                                             # Closing Backticks
        r'^' + re.escape(EOF_MARKER),                                            # Footer
        re.DOTALL | re.MULTILINE
    )

    for match in file_block_regex.finditer(markdown_text):
        all_blocks.append({
            'type': 'file',
            'path': match.group('path').strip().replace('\\', '/'),
            'span': match.span(),
            'content': match.group('content').strip() # Content is cleaned of wrapper whitespace
        })

    # Sort blocks by starting position to identify chronological order
    all_blocks.sort(key=lambda x: x['span'][0])

    # Map orphans (unformatted gaps between valid blocks)
    ordered_segments = []
    last_end = 0

    for block in all_blocks:
        # Check for gap before this block
        gap_text = markdown_text[last_end:block['span'][0]].strip()
        if gap_text:
            ordered_segments.append({
                'type': 'orphan',
                'content': gap_text
            })

        # Add metadata for the block itself
        if block['type'] == 'tag':
            ordered_segments.append({
                'type': 'tag',
                'tag': block['tag'],
                'content': block['content']
            })
        else:
            ordered_segments.append({'type': 'file_placeholder'})

        last_end = block['span'][1]

    # Check for trailing orphan commentary
    final_gap = markdown_text[last_end:].strip()
    if final_gap:
        ordered_segments.append({
            'type': 'orphan',
            'content': final_gap
        })

    # Validation and planning for file changes
    files_to_update = {}
    files_to_create = {}
    invalid_chars_pattern = r'[<>:"|?*]'
    base_dir_abs = os.path.abspath(base_dir)

    # Validate Proposed Deletions (Critical Security Step)
    for rel_path in deletions_proposed:
        if re.search(invalid_chars_pattern, rel_path):
            return {
                'status': 'ERROR',
                'message': f"Error: The deletion path '{rel_path}' contains invalid characters."
            }

        try:
            full_path = os.path.abspath(os.path.join(base_dir_abs, rel_path))
            if os.path.commonpath([base_dir_abs, full_path]) != base_dir_abs:
                return {
                    'status': 'ERROR',
                    'message': f"Error: Deletion path '{rel_path}' attempts to access a location outside the project directory."
                }
        except (ValueError, Exception):
            return {
                'status': 'ERROR',
                'message': f"Error: Deletion path '{rel_path}' attempts to access a location outside the project directory."
            }

    # Validate and Plan File Blocks (Updates/Creations)
    file_blocks = [b for b in all_blocks if b['type'] == 'file']
    for b in file_blocks:
        rel_path = b['path']
        content = b['content']

        if re.search(invalid_chars_pattern, rel_path):
            return {
                'status': 'ERROR',
                'message': f"Error: The file path '{rel_path}' contains invalid characters."
            }

        try:
            full_path = os.path.abspath(os.path.join(base_dir_abs, rel_path))
            if os.path.commonpath([base_dir_abs, full_path]) != base_dir_abs:
                return {
                    'status': 'ERROR',
                    'message': f"Error: Path '{rel_path}' attempts to access a location outside the project directory."
                }
        except (ValueError, Exception):
            return {
                'status': 'ERROR',
                'message': f"Error: Path '{rel_path}' attempts to access a location outside the project directory."
            }

        if os.path.isfile(full_path):
            files_to_update[rel_path] = content
        elif os.path.isdir(full_path):
            return {
                'status': 'ERROR',
                'message': f"Error: The path '{rel_path}' points to a directory, not a file."
            }
        else:
            files_to_create[rel_path] = content

    # Helper to extract flat tag content for compatibility
    def get_tag_content(tag_name):
        for s in ordered_segments:
            if s.get('tag') == tag_name:
                return s['content']
        return ""

    result = {
        'updates': files_to_update,
        'creations': files_to_create,
        'deletions_proposed': deletions_proposed,
        'answers': get_tag_content("ANSWERS TO DIRECT USER QUESTIONS"),
        'intro': get_tag_content("INTRO"),
        'changes': get_tag_content("CHANGES"),
        'delete': get_tag_content("DELETED FILES"),
        'verification': get_tag_content("VERIFICATION"),
        'ordered_segments': ordered_segments,
        'has_any_tags': any(b['type'] == 'tag' for b in all_blocks)
    }

    if not all_blocks:
        result['status'] = 'UNFORMATTED'
        result['unformatted'] = markdown_text.strip()
    elif files_to_create or deletions_proposed:
        result['status'] = 'CONFIRM_CREATION'
    else:
        result['status'] = 'SUCCESS'

    return result
```

--- End of file ---

--- File: `src/core/clipboard.py` ---

```python
import pyperclip
import json
from tkinter import messagebox
from .merger import generate_output_string
from .secret_scanner import scan_for_secrets

def copy_project_to_clipboard(parent, base_dir, project_config, use_wrapper, copy_merged_prompt, scan_secrets_enabled):
    """
    Handles the entire process of scanning for secrets, generating the output string,
    and copying it to the clipboard. Returns a status message string.
    """
    try:
        if not project_config.selected_files:
            return "No files selected to copy."

        # Extract paths from the list of dictionaries
        files_to_copy = [f['path'] for f in project_config.selected_files]

        if scan_secrets_enabled:
            report = scan_for_secrets(base_dir, files_to_copy)
            if report:
                warning_message = (
                    "Warning: Potential secrets were detected in your selection.\n\n"
                    f"{report}\n\n"
                    "Do you still want to copy this content to your clipboard?"
                )
                proceed = messagebox.askyesno("Secrets Detected", warning_message, parent=parent)
                if not proceed:
                    return "Copy cancelled due to potential secrets."

        final_content, status_message = generate_output_string(
            base_dir,
            project_config,
            use_wrapper,
            copy_merged_prompt
        )

        if final_content is not None:
            pyperclip.copy(final_content)
            return status_message
        else:
            return status_message or "Error: Could not generate content."
    except Exception as e:
        parent.show_error_dialog("Merging Error", f"An error occurred: {e}")
        return f"Error during merging: {e}"
```

--- End of file ---

--- File: `src/core/updater.py` ---

```python
import json
import webbrowser
import os
import sys
import subprocess
import logging
from datetime import datetime
from urllib import request, error
from tkinter import messagebox
from .. import constants as c
from ..core.paths import BUNDLE_DIR

log = logging.getLogger("CodeMerger")

class Updater:
    """
    Handles checking for application updates from a GitHub repository.
    """
    def __init__(self, parent, app_state, current_version):
        self.parent = parent
        self.state = app_state
        self.current_version = current_version
        self.repo_url = c.GITHUB_API_URL

    def _should_check_for_updates(self):
        """
        Determines if an update check should be performed based on user settings
        and the last check date. An update check is performed if it's a new day.
        """
        if not self.state.check_for_updates:
            log.info("Update check skipped: disabled by user setting.")
            return False

        last_check_str = self.state.last_update_check
        if not last_check_str:
            log.info("Performing first-time update check.")
            return True

        try:
            last_check_date = datetime.fromisoformat(last_check_str).date()
            current_date = datetime.now().date()
            should_check = current_date > last_check_date
            if should_check:
                log.info("Performing daily update check.")
            return should_check
        except (ValueError, TypeError) as e:
            log.warning(f"Could not parse last update check date '{last_check_str}'. Performing check. Error: {e}")
            return True

    def check_for_updates(self):
        """
        Performs the update check if conditions are met and handles the result.
        This is designed to fail silently on network errors.
        """
        if not self._should_check_for_updates():
            return

        try:
            with request.urlopen(self.repo_url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    latest_version_tag = data.get('tag_name', 'v0.0.0')

                    latest_version = latest_version_tag.lstrip('v').strip()
                    current_version_normalized = self.current_version.lstrip('v').strip()

                    if self._is_newer(latest_version, current_version_normalized):
                        self._notify_user(data)
                    else:
                        log.info(f"Application is up to date (current: {self.current_version}).")
                else:
                    log.warning(f"Update check failed: Server returned status {response.status}.")
        except Exception as e:
            log.error(f"Update check failed with a network error: {e}", exc_info=False)
            pass
        finally:
            log.info("Updating last check date to now.")
            self.state.update_last_check_date()

    def check_for_updates_manual(self):
        """
        Performs a user-initiated update check and provides direct feedback.
        """
        log.info("Performing manual update check.")
        try:
            with request.urlopen(self.repo_url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    latest_version_tag = data.get('tag_name', 'v0.0.0')

                    latest_version = latest_version_tag.lstrip('v').strip()
                    current_version_normalized = self.current_version.lstrip('v').strip()

                    if self._is_newer(latest_version, current_version_normalized):
                        self._notify_user(data)
                    else:
                        messagebox.showinfo(
                            "Up to Date",
                            f"You are running the latest version of CodeMerger ({self.current_version}).",
                            parent=self.parent
                        )
                else:
                    self.parent.show_error_dialog(
                        "Update Check Failed",
                        f"Could not check for updates. Server returned status {response.status}."
                    )
        except error.URLError as e:
            log.error(f"Manual update check failed: {e.reason}")
            self.parent.show_error_dialog(
                "Update Check Failed",
                f"Could not check for updates. Please check your internet connection.\n\nDetails: {e.reason}"
            )
        except Exception as e:
            log.exception("An unexpected error occurred during manual update check.")
            self.parent.show_error_dialog(
                "Update Check Failed",
                f"An unexpected error occurred while checking for updates.\n\nDetails: {e}"
            )

    def _is_newer(self, latest_str, current_str):
        """
        Compares two version strings (e.g., '1.2.3') and returns True if
        the latest is newer than the current.
        """
        try:
            latest_parts = tuple(map(int, latest_str.split('.')))
            current_parts = tuple(map(int, current_str.split('.')))
            is_newer = latest_parts > current_parts
            log.info(f"Version comparison: latest={latest_parts} > current={current_parts} is {is_newer}")
            return is_newer
        except (ValueError, IndexError) as e:
            log.error(f"Could not parse version strings for comparison: latest='{latest_str}', current='{current_str}'. Error: {e}")
            return False

    def _notify_user(self, release_data):
        """
        Displays a dialog to the user about the available update.
        """
        latest_version = release_data.get('tag_name', 'N/A')
        release_notes = release_data.get('body', 'No release notes available.')
        log.info(f"New version available: {latest_version}. Prompting user to update.")

        message = (
            f"A new version of CodeMerger is available!\n\n"
            f"  Your version: {self.current_version}\n"
            f"  Latest version: {latest_version}\n\n"
            f"Release Notes:\n{release_notes}\n\n"
            f"CodeMerger will now close and the update will be downloaded and installed.\n\n"
            "Do you want to proceed?"
        )

        if messagebox.askyesno("Update Available", message, parent=self.parent):
            self.start_update_process(release_data)
        else:
            log.info("User declined the update.")

    def start_update_process(self, release_data):
        """
        Launches the external GUI updater executable and exits the main application.
        """
        assets = release_data.get('assets', [])
        download_url = next((asset.get('browser_download_url') for asset in assets if asset.get('name', '').endswith('_Setup.exe')), None)

        if not download_url:
            log.error("Could not find a downloadable setup file in the latest release assets.")
            self.parent.show_error_dialog("Update Error", "Could not find a downloadable installer in the release.")
            return

        updater_exe_path = ""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            updater_exe_path = os.path.join(base_path, "updater_gui.exe")
        else:
            # This path is for running from source code.
            updater_exe_path = os.path.join(BUNDLE_DIR, "updater_gui.exe")

        if not os.path.exists(updater_exe_path):
            log.critical(f"Updater executable 'updater_gui.exe' not found at expected path: {updater_exe_path}")
            self.parent.show_error_dialog("Update Error", f"The updater application is missing and could not be found.\n\nChecked path: {updater_exe_path}\n\nPlease reinstall CodeMerger.")
            return

        try:
            pid = os.getpid()
            log.info(f"Starting update process. Current PID: {pid}. Updater: {updater_exe_path}. URL: {download_url}")

            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.DETACHED_PROCESS

            subprocess.Popen(
                [updater_exe_path, str(pid), download_url],
                creationflags=creationflags,
                close_fds=True
            )

            log.info("Updater launched. Exiting main application.")
            # Exit the main application
            self.parent.destroy()
            sys.exit(0)

        except Exception as e:
            log.exception("Failed to launch the updater process.")
            self.parent.show_error_dialog("Update Error", f"Failed to launch the updater process: {e}")
```

--- End of file ---

--- File: `src/core/project_manager.py` ---

```python
import os
from .project_config import ProjectConfig, _calculate_font_color
from .utils import parse_gitignore
from .file_scanner import get_all_matching_files

class ProjectManager:
    """Handles loading, initializing, and managing the active project's configuration."""
    def __init__(self, get_active_file_extensions_func):
        self.project_config = None
        self.get_active_file_extensions = get_active_file_extensions_func

    def _populate_new_project_files(self, project_config):
        """
        Helper method to scan for files and populate the ProjectConfig for a new project.
        """
        all_project_files = get_all_matching_files(
            base_dir=project_config.base_dir,
            file_extensions=self.get_active_file_extensions(),
            gitignore_patterns=parse_gitignore(project_config.base_dir)
        )
        project_config.known_files = all_project_files

        # Start with an empty selection for new projects
        project_config.selected_files = []
        project_config.total_tokens = 0

    def load_project(self, path):
        """
        Loads a project from a given path. If no .allcode file exists,
        it initializes a new one.
        Returns a tuple: (ProjectConfig object or None, status message string)
        """
        if not path or not os.path.isdir(path):
            self.project_config = None
            return None, "No project selected"

        allcode_file = os.path.join(path, '.allcode')
        is_new_project = not os.path.isfile(allcode_file)

        self.project_config = ProjectConfig(path)

        try:
            files_were_cleaned = self.project_config.load()
        except RuntimeError as e:
            # Fatal error during load of an existing file: return None to prevent further damage
            self.project_config = None
            return None, str(e)

        project_display_name = self.project_config.project_name

        if is_new_project:
            # Initialize a new project by scanning for all valid files
            self._populate_new_project_files(self.project_config)
            self.project_config.save()
            status_message = f"Initialized new project: {project_display_name}."
        elif files_were_cleaned:
            status_message = f"Activated project: {project_display_name} - Cleaned missing files."
        else:
            status_message = f"Activated project: {project_display_name}."

        return self.project_config, status_message

    def create_project_with_defaults(self, path, project_name, intro_text, outro_text, initial_selected_files=None, project_color=None):
        """
        Initializes a new project configuration at the specified path with default prompts.
        Optionally sets the initial selected files (merge list).
        """
        if not path or not os.path.isdir(path):
            return

        config = ProjectConfig(path)
        # Apply the "normal" project name provided by the user
        config.project_name = project_name

        # Apply recommended color if provided by LLM
        if project_color:
            config.project_color = project_color
            config.project_font_color = _calculate_font_color(project_color)

        # Populate file list using the centralized logic
        self._populate_new_project_files(config)

        # If specific files were requested (e.g. from Wizard), set them now.
        if initial_selected_files:
            # Defensive check: Ensure items are dicts with 'path' keys
            processed_selection = []
            new_paths = set()

            for item in initial_selected_files:
                if isinstance(item, str):
                    path_str = item
                    processed_selection.append({'path': path_str})
                    new_paths.add(path_str)
                elif isinstance(item, dict) and 'path' in item:
                    processed_selection.append(item)
                    new_paths.add(item['path'])

            config.selected_files = processed_selection

            # CRITICAL: Ensure these files are added to known_files so they
            # don't trigger "New File" alerts immediately upon opening.
            config.known_files = sorted(list(set(config.known_files) | new_paths))

        # Apply custom prompts
        config.intro_text = intro_text
        config.outro_text = outro_text
        config.save()

    def get_current_project(self):
        """Returns the currently active ProjectConfig object."""
        return self.project_config
```

--- End of file ---

--- File: `src/ui/assets.py` ---

```python
import os
from PIL import Image, ImageTk, ImageColor
from ..core.paths import (
    TRASH_ICON_PATH, NEW_FILES_ICON_PATH, NEW_FILES_MANY_ICON_PATH, DEFAULTS_ICON_PATH,
    LOGO_MASK_PATH, LOGO_MASK_SMALL_PATH, ICON_PATH, EDIT_ICON_PATH,
    COMPACT_MODE_CLOSE_ICON_PATH,
    FOLDER_ICON_PATH, FOLDER_ACTIVE_ICON_PATH, FOLDER_REVEAL_ICON_PATH, PATHS_ICON_PATH, PATHS_ACTIVE_ICON_PATH,
    EXTRA_FILES_ICON_PATH, EXTRA_FILES_ICON_ACTIVE_PATH, ORDER_REQUEST_ICON_PATH,
    GIT_FILES_ICON_PATH, GIT_FILES_ACTIVE_ICON_PATH,
    SETTINGS_ICON_PATH, FILETYPES_ICON_PATH, SETTINGS_ICON_ACTIVE_PATH, FILETYPES_ICON_ACTIVE_PATH,
    PROJECT_STARTER_ICON_PATH, PROJECT_STARTER_ACTIVE_ICON_PATH,
    LOCKED_ICON_PATH, UNLOCKED_ICON_PATH,
    INFO_ICON_PATH, INFO_ICON_ACTIVE_PATH
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
        self.edit_icon_pil = self._load_image(EDIT_ICON_PATH, (14, 14))
        self.new_files_pil = self._load_image(NEW_FILES_ICON_PATH, (24, 24))
        self.new_files_compact_pil = self._load_image(NEW_FILES_ICON_PATH, (14, 14))
        self.new_files_many_compact_pil = self._load_image(NEW_FILES_MANY_ICON_PATH, (14, 14))
        self.defaults_pil = self._load_image(DEFAULTS_ICON_PATH, (24, 24))
        self.folder_icon_pil = self._load_image(FOLDER_ICON_PATH, (28, 22))
        self.folder_active_pil = self._load_image(FOLDER_ACTIVE_ICON_PATH, (28, 22))
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

        # Project Starter Icons
        self.project_starter_pil = self._load_image(PROJECT_STARTER_ICON_PATH, (28, 28))
        self.project_starter_active_pil = self._load_image(PROJECT_STARTER_ACTIVE_ICON_PATH, (28, 28))
        self.locked_pil = self._load_image(LOCKED_ICON_PATH, (16, 20))
        self.unlocked_pil = self._load_image(UNLOCKED_ICON_PATH, (16, 20))

        # Info Mode Icons
        self.info_icon_pil = self._load_image(INFO_ICON_PATH, (18, 18))
        self.info_icon_active_pil = self._load_image(INFO_ICON_ACTIVE_PATH, (18, 18))

        self.compact_mode_close_pil = self._load_image(COMPACT_MODE_CLOSE_ICON_PATH)

        # Placeholders for Tk images
        self.trash_icon_image = self.trash_icon_pil
        self.compact_icon_tk = None
        self.edit_icon_tk = None
        self.new_files_icon = None
        self.defaults_icon = None
        self.folder_icon = None
        self.folder_active_icon = None
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
        self.locked_icon = None
        self.unlocked_icon = None
        self.info_icon = None
        self.info_icon_active = None

    def load_tk_images(self):
        """
        Converts the loaded PIL images into Tkinter PhotoImage objects.
        This method MUST be called after the Tk() root window has been created.
        """
        self.compact_icon_tk = self._pil_to_photoimage(self.compact_icon_pil)
        self.edit_icon_tk = self._pil_to_photoimage(self.edit_icon_pil)
        self.new_files_icon = self._pil_to_photoimage(self.new_files_pil)
        self.defaults_icon = self._pil_to_photoimage(self.defaults_pil)
        self.folder_icon = self._pil_to_photoimage(self.folder_icon_pil)
        self.folder_active_icon = self._pil_to_photoimage(self.folder_active_pil)
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
        self.locked_icon = self._pil_to_photoimage(self.locked_pil)
        self.unlocked_icon = self._pil_to_photoimage(self.unlocked_pil)
        self.info_icon = self._pil_to_photoimage(self.info_icon_pil)
        self.info_icon_active = self._pil_to_photoimage(self.info_icon_active_pil)

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
        if not os.path.exists(path):
            return Image.new('RGBA', resize if resize else (16, 16), (0,0,0,0))

        try:
            img = Image.open(path)
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
            return img
        except Exception:
            return Image.new('RGBA', resize if resize else (16, 16), (0,0,0,0))

    def _pil_to_photoimage(self, pil_image):
        if pil_image:
            try:
                return ImageTk.PhotoImage(pil_image)
            except Exception:
                return None
        return None

assets = AppAssets()
```

--- End of file ---

--- File: `src/ui/font_utils.py` ---

```python
import os
import sys
from PIL import ImageFont
from functools import lru_cache

# Robust Font Finding Logic
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
```

--- End of file ---

--- File: `src/ui/style_manager.py` ---

```python
from tkinter import ttk
from .. import constants as c

def apply_dark_theme(window):
    """
    Applies a consistent dark theme to all ttk widgets in the application.
    This should be called on any Toplevel window that uses ttk widgets.
    """
    window.option_add('*TCombobox*Listbox.background', c.TEXT_INPUT_BG)
    window.option_add('*TCombobox*Listbox.foreground', c.TEXT_COLOR)
    window.option_add('*TCombobox*Listbox.selectBackground', c.BTN_BLUE)
    window.option_add('*TCombobox*Listbox.selectForeground', c.BTN_BLUE_TEXT)

    s = ttk.Style(window)
    s.theme_use('default')

    # Checkbutton Style
    s.configure('Dark.TCheckbutton',
        background=c.DARK_BG,
        foreground=c.TEXT_COLOR,
        font=c.FONT_NORMAL
    )
    s.map('Dark.TCheckbutton',
        background=[('active', c.DARK_BG)],
        indicatorcolor=[('selected', c.BTN_BLUE), ('!selected', c.TEXT_INPUT_BG)],
        indicatorrelief=[('pressed', 'sunken'), ('!pressed', 'flat')]
    )

    # Large Checkbutton Style (Used in Project Starter)
    s.configure('Large.TCheckbutton',
        background=c.DARK_BG,
        foreground=c.TEXT_COLOR,
        font=c.FONT_H3,
        padding=(0, 5, 0, 5)
    )
    s.map('Large.TCheckbutton',
        background=[('active', c.DARK_BG)],
        indicatorcolor=[('selected', c.BTN_BLUE), ('!selected', c.TEXT_INPUT_BG)],
        indicatorrelief=[('pressed', 'sunken'), ('!pressed', 'flat')]
    )

    # Combobox Style
    s.configure('Dark.TCombobox',
        fieldbackground=c.TEXT_INPUT_BG,
        background=c.TEXT_INPUT_BG,
        arrowcolor=c.TEXT_COLOR,
        foreground=c.TEXT_COLOR,
        selectbackground=c.TEXT_INPUT_BG,
        selectforeground=c.TEXT_COLOR
    )
    s.map('Dark.TCombobox',
        foreground=[('readonly', c.TEXT_COLOR)],
        fieldbackground=[('readonly', c.TEXT_INPUT_BG)]
    )

    # Notebook Style
    s.configure('TNotebook', background=c.DARK_BG, borderwidth=0)
    s.configure('TNotebook.Tab',
        background=c.TEXT_INPUT_BG,
        foreground=c.TEXT_COLOR,
        padding=[8, 6, 20, 6],
        font=c.FONT_NORMAL,
        focusthickness=0,
        focuscolor=c.TEXT_INPUT_BG
    )
    s.map('TNotebook.Tab',
        background=[('selected', c.BTN_BLUE)],
        foreground=[('selected', c.BTN_BLUE_TEXT)],
        focuscolor=[('selected', c.BTN_BLUE)]
    )
```

--- End of file ---

--- File: `src/ui/window_utils.py` ---

```python
import sys
from .. import constants as c

# Platform-specific logic for getting monitor info
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    # Define necessary structures and constants from the Windows API
    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork", wintypes.RECT),
            ("dwFlags", wintypes.DWORD),
        ]

    MONITOR_DEFAULTTONEAREST = 2

    # Load the user32 library
    user32 = ctypes.windll.user32

def get_monitor_work_area(window):
    """
    Gets the work area of the monitor that the given window is on.
    Returns a tuple (left, top, right, bottom).
    Provides a fallback for non-Windows platforms.
    """
    if sys.platform == "win32":
        try:
            # Determine monitor from a point or window handle
            if isinstance(window, tuple): # It's a point (x, y)
                point = wintypes.POINT(window[0], window[1])
                h_monitor = user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
            else: # It's a window object
                hwnd = window.winfo_id()
                h_monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

            monitor_info = MONITORINFO()
            monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
            if user32.GetMonitorInfoW(h_monitor, ctypes.byref(monitor_info)):
                work_area = monitor_info.rcWork
                return (work_area.left, work_area.top, work_area.right, work_area.bottom)
        except Exception:
            # Fallback on API failure
            pass

    # Fallback for non-Windows or if API calls fail
    return (0, 0, window.winfo_screenwidth(), window.winfo_screenheight())

def _get_default_geometry_for_window(window_class_name):
    """Maps a window's class name to its default geometry string from constants."""
    if window_class_name == 'FileManagerWindow':
        return c.FILE_MANAGER_DEFAULT_GEOMETRY
    if window_class_name == 'SettingsWindow':
        return c.SETTINGS_WINDOW_DEFAULT_GEOMETRY
    if window_class_name == 'FiletypesManagerWindow':
        return c.FILETYPES_WINDOW_DEFAULT_GEOMETRY
    if window_class_name == 'InstructionsWindow':
        return c.INSTRUCTIONS_WINDOW_DEFAULT_GEOMETRY
    if window_class_name == 'ProjectStarterDialog':
        return c.PROJECT_STARTER_GEOMETRY
    if window_class_name == 'NotesDisplayDialog':
        return c.NOTES_DIALOG_DEFAULT_GEOMETRY
    if window_class_name == 'FeedbackDialog':
        return "900x750"
    # Return None if no specific default is found for this window type
    return None

def _find_geometry_store(window):
    """Recursively searches up the parent chain for the window_geometries dictionary."""
    curr = getattr(window, 'parent', getattr(window, 'master', None))
    while curr:
        if hasattr(curr, 'window_geometries'):
            return curr
        # Navigate up via parent attribute or Tkinter master
        next_node = getattr(curr, 'parent', getattr(curr, 'master', None))
        if next_node == curr: break
        curr = next_node
    return None

def position_window(window):
    """
    Calculates and applies the position for a window, ensuring it is always
    fully visible on the screen. It correctly centers on the parent window by
    default and respects saved positions.
    """
    parent = window.parent
    window_name = window.__class__.__name__

    # Attempt to find the geometry store (usually on the main App instance)
    store_node = _find_geometry_store(window)
    saved_geometry = store_node.window_geometries.get(window_name) if store_node else None

    win_w, win_h, x, y = 0, 0, 0, 0

    # Determine authoritative dimensions and initial position
    if saved_geometry:
        try:
            parts = saved_geometry.replace('+', ' ').replace('x', ' ').split()
            if len(parts) == 4:
                win_w, win_h, x, y = map(int, parts)
            else: saved_geometry = None
        except (ValueError, IndexError):
            saved_geometry = None

    if not saved_geometry:
        # First, try to get a predefined default size from constants.
        default_geom_str = _get_default_geometry_for_window(window_name)
        if default_geom_str:
            try:
                size_part = default_geom_str.split('+')[0]
                w_str, h_str = size_part.split('x')
                win_w, win_h = int(w_str), int(h_str)
            except (ValueError, IndexError):
                win_w, win_h = 600, 400 # Fallback for malformed string
        else:
            # If no default string exists, trust the window's self-calculated size.
            window.update_idletasks()
            win_w = window.winfo_reqwidth()
            win_h = window.winfo_reqheight()
            if win_w <= 1 or win_h <= 1: # Absolute fallback
                win_w, win_h = 600, 400

        # Now that we have a definitive width and height, calculate the centered position.
        parent.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2

    # Constrain the position to be fully on-screen
    if saved_geometry:
        target_for_monitor_detection = (x, y)
    else:
        target_for_monitor_detection = parent if parent else (x, y)

    mon_left, mon_top, mon_right, mon_bottom = get_monitor_work_area(target_for_monitor_detection)

    # Apply buffers to prevent spawning behind the taskbar or against the screen edges.
    mon_bottom -= 50
    mon_right -= 20
    mon_left += 10
    mon_top += 10

    if x + win_w > mon_right: x = mon_right - win_w
    if y + win_h > mon_bottom: y = mon_bottom - win_h
    if x < mon_left: x = mon_left
    if y < mon_top: y = mon_top

    # Apply the final, fully calculated geometry
    window.geometry(f"{win_w}x{win_h}+{x}+{y}")

def save_window_geometry(window):
    """Saves the window's current geometry to the persistent store."""
    store_node = _find_geometry_store(window)
    if store_node:
        store_node.window_geometries[window.__class__.__name__] = window.geometry()
```

--- End of file ---

--- File: `src/ui/widgets/rounded_button.py` ---

```python
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageDraw, ImageTk
from ... import constants as c
from ..font_utils import get_pil_font

class RoundedButton(tk.Canvas):
    """A custom anti-aliased rounded button widget for tkinter."""
    def __init__(self, parent, command, text=None, image=None, font=None, bg='#CCCCCC', fg='#000000', width=None, height=30, radius=6, hollow=False, muted_border=False, h_padding=None, cursor=None, text_align='center', hover_bg=None, click_bg=None, hover_fg=None):
        if font:
            self.tk_font_tuple = font
        else:
            self.tk_font_tuple = c.FONT_DEFAULT

        self.hollow = hollow
        self.muted_border = muted_border
        self.image = image
        self.text_align = text_align
        self.pil_font = get_pil_font(self.tk_font_tuple)

        # Calculate width if not provided
        if width is None:
            if text:
                padding = h_padding if h_padding is not None else 40
                text_box = self.pil_font.getbbox(text)
                text_width = text_box[2] - text_box[0]
                self.width = text_width + padding
            elif image:
                padding = h_padding if h_padding is not None else 20
                self.width = image.width + padding
            else:
                self.width = 40
        else:
            self.width = width

        self.height = height
        self.radius = radius
        self.command = command
        self.is_enabled = True
        self.is_loading = False
        self._pre_loading_text = ""

        # Increase the canvas size for hollow buttons to compensate for the border
        if self.hollow:
            self.width += 2
            self.height += 2

        super().__init__(parent, width=self.width, height=self.height, bg=parent.cget('bg'), bd=0, highlightthickness=0, cursor=cursor)
        self.text = text
        self.original_bg_color = bg
        self.original_fg_color = fg
        self.fg_color = self.original_fg_color
        self.hover_fg = hover_fg

        # For hollow buttons, the look is a specific fill with fg text
        if self.hollow:
            self.base_color = c.DARK_BG
            self.hover_color = hover_bg if hover_bg else self._adjust_brightness(self.base_color, 0.2)
            self.click_color = click_bg if click_bg else self.base_color
            self.disabled_color = self.base_color
            self.disabled_text_color = '#757575'
        # For solid buttons, colors are based on the background
        else:
            self.base_color = self.original_bg_color
            self.hover_color = hover_bg if hover_bg else self._adjust_brightness(self.base_color, -0.1)
            self.click_color = click_bg if click_bg else self._adjust_brightness(self.base_color, -0.2)
            self.disabled_color = '#9E9E9E'

        self._last_draw_width = 0
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_resize)
        self._draw(self.base_color)

    def set_loading(self, is_loading, loading_text="Merging"):
        """
        Toggles a loading state. Disables the button and changes text.
        """
        if self.is_loading == is_loading:
            return

        self.is_loading = is_loading
        if is_loading:
            self._pre_loading_text = self.text
            # Use configure to handle text change and state change (which triggers redraw)
            self.configure(text=loading_text, state='disabled')
        else:
            self.configure(text=self._pre_loading_text, state='normal')

    def _on_resize(self, event=None):
        if self.winfo_width() != self._last_draw_width:
            color = self.base_color if self.is_enabled else self.disabled_color
            self._draw(color)

    def _adjust_brightness(self, hex_color, factor):
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * (1 + factor))))
        g = max(0, min(255, int(g * (1 + factor))))
        b = max(0, min(255, int(b * (1 + factor))))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, color):
        self.delete("all")
        draw_width = self.winfo_width()
        if draw_width <= 1:
            draw_width = self.width
        self._last_draw_width = draw_width
        scale = c.ANTIALIASING_SCALE_FACTOR
        scaled_width = draw_width * scale
        scaled_height = self.height * scale
        scaled_radius = self.radius * scale
        img = Image.new('RGBA', (int(scaled_width), int(scaled_height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if self.hollow:
            if self.muted_border:
                border_color = self.disabled_text_color
            else:
                border_color = self.disabled_text_color if not self.is_enabled else self.original_fg_color

            scaled_border_width = 1 * scale
            inset = scaled_border_width / 2
            draw.rounded_rectangle(
                (inset, inset, scaled_width - inset, scaled_height - inset),
                radius=scaled_radius,
                fill=color,
                outline=border_color,
                width=scaled_border_width
            )
            text_fill_color = self.disabled_text_color if not self.is_enabled else self.original_fg_color
        else:
            draw.rounded_rectangle((0, 0, scaled_width, scaled_height), radius=scaled_radius, fill=color)
            text_fill_color = self.fg_color

        if self.image:
            scaled_image = self.image.resize((self.image.width * scale, self.image.height * scale), Image.Resampling.LANCZOS)
            paste_x = (scaled_width - scaled_image.width) // 2
            paste_y = (scaled_height - scaled_image.height) // 2
            img.paste(scaled_image, (int(paste_x), int(paste_y)), scaled_image)
        elif self.text:
            scaled_font_tuple = (self.tk_font_tuple[0], int(self.tk_font_tuple[1] * scale)) + tuple(self.tk_font_tuple[2:])
            scaled_font = get_pil_font(scaled_font_tuple)

            anchor = "mm"
            text_x = scaled_width / 2
            if self.text_align == 'left':
                anchor = "lm"
                text_x = 10 * scale
            center_y = (scaled_height / 2) - (0.5 * scale)
            draw.text(
                (text_x, center_y),
                self.text,
                font=scaled_font,
                fill=text_fill_color,
                anchor=anchor
            )

        img = img.resize((draw_width, self.height), Image.Resampling.LANCZOS)
        self._button_image = ImageTk.PhotoImage(img)
        self.create_image(0, 0, anchor='nw', image=self._button_image)

    def _on_enter(self, event):
        if self.is_enabled:
            if self.hover_fg:
                self.fg_color = self.hover_fg
            self._draw(self.hover_color)

    def _on_leave(self, event):
        if self.is_enabled:
            self.fg_color = self.original_fg_color
            self._draw(self.base_color)

    def _on_click(self, event):
        if self.is_enabled:
            self._draw(self.click_color)

    def _on_release(self, event):
        """
        Handles button release. Only triggers the command if the mouse is released
        inside the button boundaries.
        """
        if self.is_enabled:
            if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
                self._draw(self.hover_color)
                if self.command:
                    self.command()
            else:
                self._draw(self.base_color)

    def set_state(self, state):
        if state == 'disabled':
            self.is_enabled = False
            if not self.hollow:
                self.fg_color = '#757575'
            self._draw(self.disabled_color)
        else: # 'normal'
            self.is_enabled = True
            self.fg_color = self.original_fg_color
            self._draw(self.base_color)

    def config(self, **kwargs):
        """
        Allows configuration of button properties.
        CRITICAL: Custom properties like 'hollow' must be popped from kwargs
        before passing the rest to super().config(), otherwise Tkinter will crash.
        """
        text_changed = 'text' in kwargs
        width_changed = 'width' in kwargs
        bg_changed = 'bg' in kwargs
        fg_changed = 'fg' in kwargs
        hollow_changed = 'hollow' in kwargs
        muted_border_changed = 'muted_border' in kwargs
        hover_bg_changed = 'hover_bg' in kwargs
        click_bg_changed = 'click_bg' in kwargs
        hover_fg_changed = 'hover_fg' in kwargs

        if text_changed:
            self.text = kwargs.pop('text')

        if width_changed:
            self.width = kwargs.pop('width')
            if self.hollow: self.width += 2
            super().config(width=self.width)

        if bg_changed:
            self.original_bg_color = kwargs.pop('bg')
            if not self.hollow:
                self.base_color = self.original_bg_color
                # Refresh derived colors if they weren't explicitly set previously
                if not hasattr(self, '_custom_hover'):
                    self.hover_color = self._adjust_brightness(self.base_color, -0.1)
                if not hasattr(self, '_custom_click'):
                    self.click_color = self._adjust_brightness(self.base_color, -0.2)

        if hover_bg_changed:
            self.hover_color = kwargs.pop('hover_bg')
            self._custom_hover = True

        if click_bg_changed:
            self.click_color = kwargs.pop('click_bg')
            self._custom_click = True

        if hover_fg_changed:
            self.hover_fg = kwargs.pop('hover_fg')

        if fg_changed:
            self.original_fg_color = kwargs.pop('fg')
            self.fg_color = self.original_fg_color

        if hollow_changed:
            self.hollow = kwargs.pop('hollow')
            if self.hollow:
                self.base_color = c.DARK_BG
                if not hasattr(self, '_custom_hover'): self.hover_color = self._adjust_brightness(self.base_color, 0.2)
                if not hasattr(self, '_custom_click'): self.click_color = self.base_color
                self.disabled_color = self.base_color
                self.disabled_text_color = '#757575'
            else:
                self.base_color = self.original_bg_color
                if not hasattr(self, '_custom_hover'): self.hover_color = self._adjust_brightness(self.base_color, -0.1)
                if not hasattr(self, '_custom_click'): self.click_color = self.base_color
                self.disabled_color = self.base_color
                self.disabled_text_color = '#757575'

        if muted_border_changed:
            self.muted_border = kwargs.pop('muted_border')

        if 'state' in kwargs:
            self.set_state(kwargs.pop('state'))
        elif text_changed or width_changed or bg_changed or fg_changed or hollow_changed or muted_border_changed or hover_bg_changed or click_bg_changed or hover_fg_changed:
            # Force a redraw if appearance changed
            color = self.base_color if self.is_enabled else self.disabled_color
            self._draw(color)

        # Finally, pass any remaining standard Tkinter options to the canvas
        if kwargs:
            super().config(**kwargs)

    def configure(self, **kwargs):
        return self.config(**kwargs)
```

--- End of file ---

--- File: `src/ui/widgets/switch_button.py` ---

```python
import tkinter as tk
from ... import constants as c
from PIL import Image, ImageDraw, ImageTk

class SwitchButton(tk.Canvas):
    """
    A custom, animated, anti-aliased toggle switch widget for tkinter.
    """
    def __init__(self, parent, command=None, width=50, height=26, initial_state=False, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent.cget('bg'), highlightthickness=0, **kwargs)
        self.command = command
        self.is_on = initial_state
        self.width = width
        self.height = height
        self.radius = height / 2
        self.padding = 2

        self.knob_radius = (self.height / 2) - self.padding
        self.knob_x = self.padding if not self.is_on else self.width - self.height + self.padding

        self.bind("<Button-1>", self._on_click)
        # To prevent garbage collection
        self._image_ref = None
        self._draw()

    def _draw(self):
        scale = c.ANTIALIASING_SCALE_FACTOR
        scaled_width = self.width * scale
        scaled_height = self.height * scale
        scaled_radius = self.radius * scale
        scaled_padding = self.padding * scale
        scaled_knob_x = self.knob_x * scale

        img = Image.new('RGBA', (int(scaled_width), int(scaled_height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Track
        track_color = c.BTN_BLUE if self.is_on else c.TEXT_INPUT_BG
        track_coords = (scaled_padding, scaled_padding, scaled_width - scaled_padding, scaled_height - scaled_padding)
        draw.rounded_rectangle(track_coords, radius=scaled_radius-scaled_padding, fill=track_color)

        # Knob
        knob_color = "#FFFFFF"
        knob_coords = (
            scaled_knob_x,
            scaled_padding,
            scaled_knob_x + (scaled_height - (2 * scaled_padding)),
            scaled_height - scaled_padding
        )
        draw.ellipse(knob_coords, fill=knob_color)

        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        self._image_ref = ImageTk.PhotoImage(img)
        self.delete("all")
        self.create_image(0, 0, anchor='nw', image=self._image_ref)

    def _on_click(self, event=None):
        self.is_on = not self.is_on
        self._animate_switch()
        if self.command:
            self.command(self.is_on)

    def _animate_switch(self):
        target_x = self.width - self.height + self.padding if self.is_on else self.padding
        self._animate_step(target_x, 10)

    def _animate_step(self, target_x, steps):
        current_pos = self.knob_x
        distance = target_x - current_pos
        if abs(distance) < 1 or steps <= 0:
            self.knob_x = target_x
            self._draw()
            return

        self.knob_x += distance / steps
        self._draw()
        self.after(10, self._animate_step, target_x, steps - 1)

    def get_state(self):
        return self.is_on
```

--- End of file ---

--- File: `src/ui/widgets/scrollable_frame.py` ---

```python
import tkinter as tk
from tkinter import ttk

class ScrollableFrame(tk.Frame):
    """
    A reusable frame that contains a scrollable area.
    Widgets should be added to the `self.scrollable_frame` attribute.
    """
    def __init__(self, parent, *args, **kwargs):
        bg_color = kwargs.get('bg', parent.cget('bg'))
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<MouseWheel>", self._on_mousewheel)
        # Propagate mousewheel events from all children to this widget
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel, add=True)

    def _on_frame_configure(self, event=None):
        # Update the scrollable area when the inner frame's size changes
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._manage_scrollbar()

    def _on_canvas_configure(self, event=None):
        # Ensure the inner frame always fills the width of the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._manage_scrollbar()

    def _on_mousewheel(self, event):
        # Allow scrolling if over a Text widget as long as it's read-only (disabled)
        widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)
        w = widget_under_cursor
        while w is not None:
            # If the widget is an editable Text box, let it handle its own scroll
            if isinstance(w, tk.Text) and w.cget('state') == 'normal':
                return
            if w == self:
                break
            w = w.master

        if self.scrollbar.winfo_ismapped():
            # Handle platform-specific scroll directions and speeds
            if event.num == 5 or event.delta == -120:
                delta = 1
            elif event.num == 4 or event.delta == 120:
                delta = -1
            else:
                delta = -1 * (event.delta // 120)

            self.canvas.yview_scroll(delta, "units")

    def _manage_scrollbar(self):
        scrollregion = self.canvas.cget("scrollregion")
        if scrollregion:
            try:
                content_height = int(scrollregion.split(' ')[3])
                canvas_height = self.canvas.winfo_height()

                if content_height > canvas_height:
                    if not self.scrollbar.winfo_ismapped():
                        self.scrollbar.pack(side="right", fill="y")
                else:
                    if self.scrollbar.winfo_ismapped():
                        self.scrollbar.pack_forget()
            except (ValueError, IndexError):
                if self.scrollbar.winfo_ismapped():
                    self.scrollbar.pack_forget()
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.pack_forget()

    def destroy(self):
        # Unbind the global mousewheel event to prevent errors after destruction
        self.scrollable_frame.unbind_all("<MouseWheel>")
        super().destroy()
```

--- End of file ---

--- File: `src/ui/widgets/scrollable_text.py` ---

```python
import tkinter as tk
from tkinter import ttk
from ... import constants as c

class ScrollableText(tk.Frame):
    """
    A frame that contains a Text widget and a Scrollbar that automatically
    appears and disappears based on content overflow.
    """
    def __init__(self, parent, on_zoom=None, **kwargs):
        super().__init__(parent, bd=1, relief='sunken')
        self.on_zoom = on_zoom

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        text_kwargs = {
            'wrap': 'word', 'undo': True,
            'relief': 'flat', 'bd': 0, 'highlightthickness': 0
        }

        # Extract initial font if provided to determine family and size
        initial_font = kwargs.get('font', c.FONT_NORMAL)
        if isinstance(initial_font, str):
            # Handle string fonts (e.g. Tkinter named fonts) if passed
            self.font_family = c.FONT_FAMILY_PRIMARY
            self.current_font_size = 12
        else:
            # Assume tuple (Family, Size)
            self.font_family = initial_font[0]
            self.current_font_size = initial_font[1]

        text_kwargs.update(kwargs)

        self.text_widget = tk.Text(self, **text_kwargs)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        self.text_widget.grid(row=0, column=0, sticky='nsew')

        self.text_widget.bind("<KeyRelease>", lambda e: self.after_idle(self._manage_scrollbar))
        self.text_widget.bind("<Configure>", lambda e: self.after_idle(self._manage_scrollbar))

        # Zoom binding
        self.text_widget.bind("<Control-MouseWheel>", self._on_mousewheel_zoom)

    def _on_mousewheel_zoom(self, event):
        if self.on_zoom:
            # Standard Windows delta is 120.
            # Up (positive) = Zoom In, Down (negative) = Zoom Out
            delta = 1 if event.delta > 0 else -1
            self.on_zoom(delta)
            return "break" # Prevent scrolling while zooming

    def set_font_size(self, size):
        """Updates the font size of the internal text widget."""
        self.current_font_size = size
        new_font = (self.font_family, size)
        self.text_widget.configure(font=new_font)
        # Font change alters height/wrapping, so check scrollbar
        self.after_idle(self._manage_scrollbar)

    def _manage_scrollbar(self):
        """
        Forces a layout update and then checks if the text content is taller
        than the visible widget area, showing or hiding the scrollbar.
        """
        # Note: We do NOT call update_idletasks() here if called via after_idle,
        # as it can cause recursion or stutter.

        top_fraction, bottom_fraction = self.text_widget.yview()
        # A scrollbar is needed if the top is scrolled down (top > 0) OR
        # if the bottom isn't visible (bottom < 1.0). This covers all overflow cases.
        is_needed = top_fraction > 0.0 or bottom_fraction < 1.0
        is_visible = self.scrollbar.winfo_ismapped()

        if is_needed and not is_visible:
            self.scrollbar.grid(row=0, column=1, sticky='ns')
        elif not is_needed and is_visible:
            self.scrollbar.grid_forget()

    def insert(self, index, chars, *args):
        self.text_widget.insert(index, chars, *args)
        self.after_idle(self._manage_scrollbar)

    def delete(self, index1, index2=None):
        self.text_widget.delete(index1, index2)
        self.after_idle(self._manage_scrollbar)

    def get(self, index1, index2=None):
        return self.text_widget.get(index1, index2)
```

--- End of file ---

--- File: `src/ui/widgets/two_column_list.py` ---

```python
import tkinter as tk
from tkinter import font as tkFont
import sys
from ... import constants as c

class TwoColumnList(tk.Canvas):
    """A custom listbox widget that displays two columns with independent styling."""
    def __init__(self, parent, right_col_font, right_col_width, **kwargs):
        super().__init__(parent, bg=c.TEXT_INPUT_BG, highlightthickness=0, **kwargs)
        self.items = []
        self.item_id_map = {}
        self.selected_indices = set()
        self.highlighted_indices = set()
        self.row_height = c.DEFAULT_LIST_ITEM_HEIGHT
        self.left_col_font = tkFont.Font(family=c.FONT_NORMAL[0], size=c.FONT_NORMAL[1])
        self.right_col_font = right_col_font
        self.right_col_width = right_col_width
        self.scrollbar = None
        self.last_clicked_index = None
        self._fade_job = None
        self.bind("<ButtonPress-1>", self._on_click)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event=None):
        """
        On resize, repositions existing canvas items instead of redrawing them,
        which is much smoother and avoids flicker.
        """
        width = self.winfo_width()
        for i, item in enumerate(self.items):
            item_path = item.get('data')
            if not item_path or item_path not in self.item_id_map: continue
            ids = self.item_id_map[item_path]

            y = i * self.row_height
            self.coords(ids['bg'], 0, y, width, y + self.row_height)
            self.coords(ids['right'], width - 5, y + self.row_height / 2)

        self._update_scrollregion()
        self._update_scrollbar_visibility()

    def link_scrollbar(self, scrollbar):
        """Links a ttk.Scrollbar widget to this list for visibility management."""
        self.scrollbar = scrollbar

    def bind_event(self, sequence=None, func=None, add=None):
        self.bind(sequence, func, add)

    def _on_mousewheel(self, event):
        if not self.scrollbar or not self.scrollbar.winfo_ismapped(): return
        start, end = self.scrollbar.get()
        delta = -1 * (event.delta // 120) if sys.platform == "win32" else event.delta
        if delta < 0 and start <= 0.0: return
        if delta > 0 and end >= 1.0: return
        self.yview_scroll(delta, "units")

    def _on_click(self, event):
        self.focus_set()
        clicked_index = int(self.canvasy(event.y) // self.row_height)
        if 0 <= clicked_index < len(self.items):
            is_shift = (event.state & 0x0001)
            is_ctrl = (event.state & 0x0004)

            if is_shift and self.last_clicked_index is not None:
                start = min(self.last_clicked_index, clicked_index)
                end = max(self.last_clicked_index, clicked_index)
                new_selection = set(range(start, end + 1))
                if is_ctrl:
                    self.selected_indices.update(new_selection)
                else:
                    self.selected_indices = new_selection
            elif is_ctrl:
                if clicked_index in self.selected_indices: self.selected_indices.remove(clicked_index)
                else: self.selected_indices.add(clicked_index)
                self.last_clicked_index = clicked_index
            else:
                self.selected_indices = {clicked_index}
                self.last_clicked_index = clicked_index

            self.event_generate("<<ListSelectionChanged>>")
            self._update_styles()

    def _update_scrollregion(self):
        total_height = len(self.items) * self.row_height
        self.config(scrollregion=(0, 0, self.winfo_width(), total_height))

    def _update_scrollbar_visibility(self):
        if not self.scrollbar: return
        self.update_idletasks()
        content_height = len(self.items) * self.row_height
        canvas_height = self.winfo_height()
        if content_height > canvas_height:
            if not self.scrollbar.winfo_ismapped(): self.scrollbar.grid()
        else:
            if self.scrollbar.winfo_ismapped(): self.scrollbar.grid_remove()

    def animate_pulse(self):
        """Blinks the text items out and fades them back in to provide visual feedback."""
        if self._fade_job:
            self.after_cancel(self._fade_job)

        # Capture intended target states for text elements
        targets = []
        for i, item in enumerate(self.items):
            item_path = item.get('data')
            if not item_path or item_path not in self.item_id_map: continue

            left_target = c.BTN_BLUE_TEXT if i in self.selected_indices else item.get('left_fg', c.TEXT_COLOR)
            right_target = item.get('right_fg', c.TEXT_SUBTLE_COLOR)

            targets.append({
                'ids': self.item_id_map[item_path],
                'left': left_target,
                'right': right_target
            })

        # Step 1: Blink out (set to background color)
        for t in targets:
            self.itemconfig(t['ids']['left'], fill=c.TEXT_INPUT_BG)
            self.itemconfig(t['ids']['right'], fill=c.TEXT_INPUT_BG)

        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb

        def mix(rgb_start, rgb_end, p):
            return tuple(int(rgb_start[i] + (rgb_end[i] - rgb_start[i]) * p) for i in range(3))

        bg_rgb = hex_to_rgb(c.TEXT_INPUT_BG)

        # Step 2: Fade back in
        def step(frame, total_frames):
            if not self.winfo_exists(): return
            progress = frame / total_frames

            for t in targets:
                left_rgb = mix(bg_rgb, hex_to_rgb(t['left']), progress)
                right_rgb = mix(bg_rgb, hex_to_rgb(t['right']), progress)
                self.itemconfig(t['ids']['left'], fill=rgb_to_hex(left_rgb))
                self.itemconfig(t['ids']['right'], fill=rgb_to_hex(right_rgb))

            if frame < total_frames:
                self._fade_job = self.after(20, step, frame + 1, total_frames)
            else:
                self._fade_job = None
                self._update_styles()

        self.after(50, step, 1, 12)

    def _update_styles(self):
        """
        Efficiently updates the colors of existing canvas items without redrawing them.
        This is the key to flicker-free selection and highlighting.
        """
        for i, item in enumerate(self.items):
            item_path = item.get('data')
            if not item_path or item_path not in self.item_id_map: continue
            ids = self.item_id_map[item_path]

            bg_color = c.TEXT_INPUT_BG
            if i in self.selected_indices: bg_color = c.BTN_BLUE
            elif i in self.highlighted_indices: bg_color = c.SUBTLE_HIGHLIGHT_COLOR

            left_fg = c.BTN_BLUE_TEXT if i in self.selected_indices else item.get('left_fg', c.TEXT_COLOR)
            right_fg = item.get('right_fg', c.TEXT_SUBTLE_COLOR)

            self.itemconfig(ids['bg'], fill=bg_color)
            self.itemconfig(ids['left'], fill=left_fg)
            self.itemconfig(ids['right'], fill=right_fg)

    def set_items(self, items):
        """
        Performs a full redraw of the list. Called when the underlying data changes
        (e.g., adding/removing files).
        """
        selection_paths = {self.get_item_data(i) for i in self.curselection()}

        self.delete("all")
        self.item_id_map.clear()
        self.items = items

        width = self.winfo_width()
        if width <= 1: self.update_idletasks(); width = self.winfo_width()

        for i, item in enumerate(self.items):
            y = i * self.row_height
            bg_rect = self.create_rectangle(0, y, width, y + self.row_height, outline="")
            l_color = item.get('left_fg', c.TEXT_COLOR)
            left_text = self.create_text(5, y + self.row_height / 2, anchor='w', text=item.get('left', ''), font=self.left_col_font, fill=l_color)
            right_text = self.create_text(width - 5, y + self.row_height / 2, anchor='e', text=item.get('right', ''), font=self.right_col_font)
            # Use the unique file path as the key
            item_path = item.get('data')
            if item_path:
                self.item_id_map[item_path] = {'bg': bg_rect, 'left': left_text, 'right': right_text}

        self._update_scrollregion()
        self._update_scrollbar_visibility()

        new_selection = set()
        for i, item in enumerate(self.items):
            if item.get('data') in selection_paths: new_selection.add(i)
        self.selected_indices = new_selection
        self._update_styles()

    def reorder_and_update(self, new_display_items):
        """
        Moves and updates existing canvas items without a full redraw. This is
        used for reordering operations to prevent flickering.
        """
        self.items = new_display_items
        width = self.winfo_width()
        for new_index, item_data in enumerate(self.items):
            item_path = item_data.get('data')
            if not item_path or item_path not in self.item_id_map:
                continue

            ids = self.item_id_map[item_path]
            new_y = new_index * self.row_height

            # Move existing items
            self.coords(ids['bg'], 0, new_y, width, new_y + self.row_height)
            self.coords(ids['left'], 5, new_y + self.row_height / 2)
            self.coords(ids['right'], width - 5, new_y + self.row_height / 2)

            # Update their content (e.g., line count color might change)
            self.itemconfig(ids['left'], text=item_data.get('left', ''))
            self.itemconfig(ids['right'], text=item_data.get('right', ''), fill=item_data.get('right_fg', c.TEXT_SUBTLE_COLOR))

        self._update_styles()

    def curselection(self):
        return sorted(list(self.selected_indices))

    def clear_selection(self):
        self.selected_indices.clear()
        self._update_styles()

    def see(self, index):
        if not (0 <= index < len(self.items)): return
        item_y_start = index * self.row_height
        item_y_end = item_y_start + self.row_height
        view_y_start = self.canvasy(0)
        view_y_end = view_y_start + self.winfo_height()
        total_height = len(self.items) * self.row_height
        if total_height == 0: return
        if item_y_start < view_y_start: self.yview_moveto(item_y_start / total_height)
        elif item_y_end > view_y_end: self.yview_moveto((item_y_end - self.winfo_height()) / total_height)

    def selection_set(self, start, end=None):
        self.selected_indices = set(range(start, (end if end is not None else start) + 1))
        self._update_styles()

    def set_selection_anchor(self, index):
        """Sets the anchor for the next shift-click operation."""
        self.last_clicked_index = index

    def get_item_data(self, index):
        if 0 <= index < len(self.items): return self.items[index].get('data')
        return None

    def highlight_item(self, index):
        self.highlighted_indices.add(index)
        self._update_styles()

    def clear_highlights(self):
        self.highlighted_indices.clear()
        self._update_styles()
```

--- End of file ---

--- File: `src/ui/widgets/markdown_renderer.py` ---

```python
import tkinter as tk
from tkinter import ttk
import re
from src import constants as c
try:
    import markdown2
    MARKDOWN2_INSTALLED = True
except ImportError:
    MARKDOWN2_INSTALLED = False

class MarkdownRenderer(tk.Frame):
    """
    A custom markdown renderer using a standard tk.Text widget to provide
    reliable layout, styling, and scrolling. Includes auto-hiding scrollbar.
    """
    def __init__(self, parent, base_font_size=10, on_zoom=None, height=None, auto_height=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config(bg=c.TEXT_INPUT_BG)
        self.base_font_size = base_font_size
        self.on_zoom = on_zoom
        self.auto_height = auto_height

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if MARKDOWN2_INSTALLED:
            text_kwargs = {
                'wrap': tk.WORD, 'bd': 0, 'highlightthickness': 0,
                'padx': 15, 'pady': 15, 'font': (c.FONT_FAMILY_PRIMARY, self.base_font_size),
                'bg': c.TEXT_INPUT_BG, 'fg': c.TEXT_COLOR,
                'spacing2': 6, 'spacing1': 4, 'spacing3': 4
            }
            if height:
                text_kwargs['height'] = height
            elif self.auto_height:
                text_kwargs['height'] = 1 # Start small

            self.text_widget = tk.Text(self, **text_kwargs)
            self.text_widget.grid(row=0, column=0, sticky="nsew")

            self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview, style="Vertical.TScrollbar")

            # Initial configuration
            self.text_widget.configure(yscrollcommand=self.scrollbar.set)
            self._configure_tags()

            # Bindings for Scrollbar or Height Management
            self.text_widget.bind("<Configure>", self._on_configure_trigger)

            # Zoom binding
            self.text_widget.bind("<Control-MouseWheel>", self._on_mousewheel_zoom)
        else:
            error_message = "Markdown rendering disabled. Please install 'markdown2'."
            self.error_label = tk.Label(
                self, text=error_message, justify="center", font=c.FONT_NORMAL,
                fg=c.TEXT_SUBTLE_COLOR, bg=c.DARK_BG, wraplength=400
            )
            self.error_label.grid(row=0, column=0)

    def _on_configure_trigger(self, event=None):
        if self.auto_height:
            self.after_idle(self._adjust_height_to_content)
        else:
            self.after_idle(self._manage_scrollbar)

    def _adjust_height_to_content(self):
        """Sets the widget height based on rendered visual lines."""
        if not self.winfo_exists() or not MARKDOWN2_INSTALLED:
            return
        try:
            # We use "displaylines" to account for word wrapping.
            result = self.text_widget.count("1.0", "end-1c", "displaylines")
            if result:
                actual_lines = result[0]
                # We add +1 as a buffer to account for internal padding and prevent
                # the "one line short" scrolling artifact.
                self.text_widget.config(height=max(1, actual_lines + 1))
        except tk.TclError:
            pass

    def _manage_scrollbar(self):
        """
        Checks if the content is taller than the frame.
        Shows scrollbar if needed, hides it if not.
        """
        if not MARKDOWN2_INSTALLED or self.auto_height: return

        # Get the current scroll position (0.0 to 1.0)
        top_fraction, bottom_fraction = self.text_widget.yview()

        # We need a scrollbar if we can't see the top (scrolled down)
        # OR we can't see the bottom (content too long)
        is_needed = top_fraction > 0.0 or bottom_fraction < 1.0
        is_visible = self.scrollbar.winfo_ismapped()

        if is_needed and not is_visible:
            self.scrollbar.grid(row=0, column=1, sticky="ns")
        elif not is_needed and is_visible:
            self.scrollbar.grid_forget()

    def _configure_tags(self):
        """Configures or re-configures font tags based on current base_font_size."""
        # Update base font
        self.text_widget.configure(font=(c.FONT_FAMILY_PRIMARY, self.base_font_size))

        # Update headers relative to base size
        self.text_widget.tag_configure("h1", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size + 12, 'bold'), spacing1=20, spacing3=10)
        self.text_widget.tag_configure("h2", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size + 6, 'bold'), spacing1=16, spacing3=8)
        self.text_widget.tag_configure("h3", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size + 2, 'bold'), spacing1=12, spacing3=5)
        self.text_widget.tag_configure("bold", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size, 'bold'))
        self.text_widget.tag_configure("italic", font=(c.FONT_FAMILY_PRIMARY, self.base_font_size, 'italic'))
        self.text_widget.tag_configure("code", foreground="#DEB887", font=("Courier New", self.base_font_size - 1))

        # Recalculate layout metrics after font change affects height
        if self.auto_height:
            self.after_idle(self._adjust_height_to_content)
        else:
            self.after_idle(self._manage_scrollbar)

    def _on_mousewheel_zoom(self, event):
        if self.on_zoom:
            delta = 1 if event.delta > 0 else -1
            self.on_zoom(delta)
            return "break"

    def set_font_size(self, size):
        """Updates the base font size and refreshes all tags."""
        if not MARKDOWN2_INSTALLED: return
        self.base_font_size = size
        self._configure_tags()

    def set_markdown(self, markdown_text):
        if not MARKDOWN2_INSTALLED: return

        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)

        if not markdown_text:
            self.text_widget.config(state=tk.DISABLED)
            if self.auto_height:
                self.after_idle(self._adjust_height_to_content)
            else:
                self.after_idle(self._manage_scrollbar)
            return

        for line in markdown_text.split('\n'):
            if line.startswith("# "):
                self.text_widget.insert(tk.END, f"{line[2:].strip()}\n", "h1")
            elif line.startswith("## "):
                self.text_widget.insert(tk.END, f"{line[3:].strip()}\n", "h2")
            elif line.startswith("### "):
                self.text_widget.insert(tk.END, f"{line[4:].strip()}\n", "h3")
            elif re.match(r'^\s*-\s*\[( |x)\]', line):
                match = re.match(r'^(\s*)-\s*\[( |x)\]\s*(.*)', line)
                indent, checked, text = match.groups()
                checkbox = '☑' if checked.lower() == 'x' else '☐'
                indent_level = len(indent) // 2
                tag_name = f"checkbox_indent_{indent_level}"

                base_indent = 25 + indent_level * 20
                hanging_indent = base_indent + 22

                self.text_widget.tag_configure(tag_name, lmargin1=base_indent, lmargin2=hanging_indent, spacing1=4)
                self.text_widget.insert(tk.END, f"{checkbox} {text.strip()}\n", tag_name)
            elif re.match(r'^\s*[-*]\s', line):
                match = re.match(r'^(\s*)[-*]\s(.*)', line)
                indent, text = match.groups()
                indent_level = len(indent) // 2
                tag_name = f"bullet_indent_{indent_level}"

                base_indent = 25 + indent_level * 20
                hanging_indent = base_indent + 15

                self.text_widget.tag_configure(tag_name, lmargin1=base_indent, lmargin2=hanging_indent, spacing1=4)
                self.text_widget.insert(tk.END, f"• {text.strip()}\n", tag_name)
            else:
                self.text_widget.insert(tk.END, f"{line}\n")

        # This robustly replaces markdown symbols with styled text by finding the
        # content, deleting the original text including symbols, and re-inserting
        # the content with the proper tag.
        self._apply_format_and_hide_symbols(r"\*\*(.*?)\*\*", "bold")
        self._apply_format_and_hide_symbols(r"\*(.*?)\*", "italic")
        self._apply_format_and_hide_symbols(r"`(.*?)`", "code")

        self.text_widget.config(state=tk.DISABLED)

        # Check scrollbar or height after content is loaded
        if self.auto_height:
            self.after_idle(self._adjust_height_to_content)
        else:
            self.after_idle(self._manage_scrollbar)

    def _apply_format_and_hide_symbols(self, pattern, tag):
        start_index = "1.0"
        while True:
            match_start = self.text_widget.search(pattern, start_index, stopindex=tk.END, regexp=True)
            if not match_start: break

            line_end = self.text_widget.index(f"{match_start} lineend")
            line_text = self.text_widget.get(match_start, line_end)

            match = re.search(pattern, line_text)
            if not match:
                start_index = self.text_widget.index(f"{match_start}+1c")
                continue

            full_match_text = match.group(0)
            content_text = match.group(1)

            match_end_index = self.text_widget.index(f"{match_start}+{len(full_match_text)}c")

            # Capture existing layout tags (e.g. checkbox_indent_0) to preserve indentation
            # We filter out 'sel' to avoid carrying over selection highlights unintentionally
            existing_tags = [t for t in self.text_widget.tag_names(match_start) if t != 'sel']

            self.text_widget.delete(match_start, match_end_index)

            # Combine existing layout tags with the new styling tag
            final_tags = tuple(existing_tags) + (tag,)

            self.text_widget.insert(match_start, content_text, final_tags)

            start_index = self.text_widget.index(f"{match_start}+{len(content_text)}c")
```

--- End of file ---

--- File: `src/ui/widgets/profile_navigator.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, font as tkFont
from ... import constants as c
from .rounded_button import RoundedButton

class ProfileNavigator(Frame):
    """
    A custom widget for navigating between project profiles using Previous/Next buttons.
    """
    def __init__(self, parent, on_change_callback, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.on_change = on_change_callback

        self.profiles = []
        self.current_index = -1
        self.font = tkFont.Font(family=c.FONT_NORMAL[0], size=c.FONT_NORMAL[1])

        # Widgets
        button_font = (c.FONT_FAMILY_PRIMARY, 12, 'bold')

        self.prev_button = RoundedButton(
            self, text="<", font=button_font,
            bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR,
            command=self._on_prev,
            width=24, height=28, radius=6,
            cursor='hand2'
        )

        self.label_container = Frame(self, bg=c.DARK_BG)
        self.label_container.pack_propagate(False)

        self.profile_label = Label(
            self.label_container, text="", font=self.font,
            bg=c.DARK_BG, fg=c.TEXT_COLOR,
            anchor='c'
        )

        self.next_button = RoundedButton(
            self, text=">", font=button_font,
            bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR,
            command=self._on_next,
            width=24, height=28, radius=6,
            cursor='hand2'
        )

        self.prev_button.pack(side='left', padx=(0, 0))
        self.label_container.pack(side='left', fill='y')
        self.profile_label.pack(expand=True, fill='both')
        self.next_button.pack(side='left', padx=(0, 0))

    def set_profiles(self, profile_list, active_profile_name):
        """
        Sets the list of available profiles, calculates required width, and sets the active profile.
        """
        self.profiles = profile_list
        try:
            self.current_index = self.profiles.index(active_profile_name)
        except ValueError:
            self.current_index = 0 if self.profiles else -1

        # Calculate and set a consistent width for the label area.
        if self.profiles:
            max_w = 0
            for name in self.profiles:
                max_w = max(max_w, self.font.measure(name))

            MIN_WIDTH = 80
            MAX_WIDTH = 120

            final_width = max(MIN_WIDTH, min(max_w + 20, MAX_WIDTH))
            self.label_container.config(width=final_width)
        else:
            self.label_container.config(width=0)

        self._update_display()

    def _update_display(self):
        """
        Updates the displayed profile name and button visibility.
        """
        if self.current_index != -1 and self.profiles:
            self.profile_label.config(text=self.profiles[self.current_index])
        else:
            self.profile_label.config(text="")

        self.prev_button.config(state='normal')
        self.next_button.config(state='normal')

    def _on_prev(self):
        """Cycles to the previous profile."""
        if not self.profiles: return
        self.current_index = (self.current_index - 1) % len(self.profiles)
        new_profile = self.profiles[self.current_index]
        self.profile_label.config(text=new_profile)
        self.on_change(new_profile)

    def _on_next(self):
        """Cycles to the next profile."""
        if not self.profiles: return
        self.current_index = (self.current_index + 1) % len(self.profiles)
        new_profile = self.profiles[self.current_index]
        self.profile_label.config(text=new_profile)
        self.on_change(new_profile)
```

--- End of file ---

--- File: `src/ui/tooltip.py` ---

```python
import tkinter as tk
from .. import constants as c

class ToolTip:
    """
    A simple tooltip class for tkinter widgets.
    Creates a toplevel window with a label to display help text.
    """
    def __init__(self, widget, text, delay=0):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.delay = delay
        self._show_job = None
        self.widget.bind("<Enter>", self.on_enter, add='+')
        self.widget.bind("<Leave>", self.on_leave, add='+')

    def on_enter(self, event=None):
        self.schedule_show()

    def on_leave(self, event=None):
        self.cancel_show()
        self.hide_tooltip()

    def schedule_show(self):
        self.cancel_show()
        self._show_job = self.widget.after(self.delay, self.show_tooltip)

    def cancel_show(self):
        if self._show_job:
            self.widget.after_cancel(self._show_job)
            self._show_job = None

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify='left',
            background=c.TOP_BAR_BG,
            fg=c.TEXT_COLOR,
            relief='solid',
            borderwidth=1,
            font=c.FONT_TOOLTIP
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None
```

--- End of file ---

--- File: `src/ui/info_messages.py` ---

```python
"""
Contains all user-facing documentation strings for Info Mode.
Explanations are based on the core application documentation.
"""

INFO_MESSAGES = {
    "default": "Info mode active: hover over any interface element to see its purpose and usage details.",

    # Main Window
    "select_project": (
        "Select a Project: Click to browse for a folder. CodeMerger will create a hidden .allcode file "
        "in that directory, that will store your file selections and project-specific instructions."
    ),
    "project_name": (
        "Project Name: This is the active project. Hover here to reveal the pen icon or double-click "
        "to set a custom title. Single-click to switch to another project (same as Select Project button)."
    ),
    "color_swatch": (
        "Project Color: Pick a unique accent color for this project. This color is used in "
        "Compact Mode, to help you visually distinguish between multiple CodeMerger instances."
    ),
    "folder_icon": (
        "Folder Actions: Click to open the project in your File Explorer. Ctrl-click to copy the full "
        "path. Alt-click to open a Command Prompt (CMD) window directly in this directory."
    ),
    "manage_files": (
        "Edit Merge List: Open the dual-panel management window. This is where you decide exactly "
        "which files are relevant to your current task and in what order the AI should read them."
    ),
    "instructions": (
        "Define Instructions: Set a project-specific Intro and Outro. This text will be wrapped "
        "around your code whenever you use 'Copy with Instructions'."
    ),
    "copy_code": (
        "Copy Code Only (Ctrl+Shift+C): Merges all selected files with a standard prompt header. "
        "Useful for providing updated context to an LLM without repeating project goals. "
        "Ctrl-clicking the Adaptive Copy button in Compact mode also triggers this action."
    ),
    "copy_with_instructions": (
        "Copy Prompt with Instructions (Ctrl+C): Merges code and wraps it in your custom Intro/Outro. "
        "Strictly enforces 'No Code Truncation' rules. Ctrl-click to perform 'Copy Code Only'."
    ),
    "paste_changes": (
        "Paste Changes (Ctrl+V): Instantly applies code from your clipboard. Depending on your settings, "
        "this opens a review window or writes directly to disk. Ctrl-click to toggle the review behavior. "
        "Alt-click to open the manual paste window for raw text input."
    ),
    "response_review": (
        "AI Response Review: Opens the review window to see the most recently applied changes and "
        "associated AI commentary."
    ),
    "cleanup": (
        "Comment Cleanup: Copies a specialized prompt, that tells the AI to strip out it's own "
        "transient tags like [FIX] or [MODIFIED], while keeping structural logic comments."
    ),
    "settings": (
        "Application Settings: Configure application behavior."
    ),
    "filetypes": (
        "Manage Filetypes: Define which file extensions CodeMerger is allowed to index. "
        "Double-click an entry in the list to enable or disable it globally."
    ),
    "starter": (
        "Project Starter: Launch a guided workflow for starting new projects. Assists you in "
        "creating a concept, tech stack, and step-by-step implementation plan using AI."
    ),
    "info_toggle": (
        "Info Mode: Toggles help panels on all application windows. "
        "Useful for learning how to work with CodeMerger."
    ),
    "profile_nav": (
        "Profile Switcher: Swap between different configurations for the same project. Each "
        "profile has its own file selection and instruction set."
    ),
    "profile_add": (
        "Add Profile: Create a new named configuration. Useful for separating different tasks "
        "like 'Backend' or 'Feature Development' within the same project."
    ),
    "profile_delete": (
        "Delete Profile: Remove the currently active profile. The 'Default' profile cannot be deleted."
    ),

    # File Manager
    "fm_tree": (
        "Available Files: Browse your project structure. Double-click files or folders to add "
        "them to the merge list. Green text indicates newly detected files. Purple text indicates "
        "files in your merge list that would normally be ignored by the Git or extension filters."
    ),
    "fm_tree_action": (
        "Merge Toggle: Adds or removes the currently selected files from the list."
    ),
    "fm_list": (
        "Merge Order: This list determines in what order the code will be presented to the AI. "
        "Files are merged from top to bottom. Click a file to select it for sorting or removal."
    ),
    "fm_list_tools": (
        "List Visibility: Toggle the display of full file paths or relative filenames in the "
        "merge list."
    ),
    "fm_reveal": (
        "Open in Folder: Click this icon to open your system's file explorer and highlight "
        "this specific file."
    ),
    "fm_filter_git": "Git Filter: Toggle visibility of files listed in your .gitignore. When ON, ignored files are hidden.",
    "fm_filter_ext": "Filetype Filter: Toggle visibility of files not in your allowed extensions list. When ON, extra files are hidden.",
    "fm_filter_text": "Text Filter: Type to filter the tree and the merge list by filename.",
    "fm_tokens": (
        "Total Tokens: A real-time estimate of context usage. As the grow count grows, the color changes "
        "from gray to yellow to red to warn you about LLM context limits."
    ),
    "fm_order": (
        "Order Request: Single-click to copy a prompt asking the AI for the 'optimal' file order. "
        "Double-click to paste a new order list; Ctrl-click to directly apply a list from your clipboard."
    ),
    "fm_list_item": (
        "Merge Item: Double-click to open this file in your default or configured editor. Use the path "
        "icon in the header to toggle between filename and full path display."
    ),
    "fm_tokens_item": (
        "Token Stats: Shows the token count for this file. Ctrl-click to copy a breakup request for "
        "the AI. Alt-click to 'ignore' this file's tokens when calculating the color warnings."
    ),
    "fm_sort_top": "Move to Top: Place the selected files at the beginning of the merge list.",
    "fm_sort_up": "Move Up: Shift the selected files one position higher in the order.",
    "fm_sort_down": "Move Down: Shift the selected files one position lower in the order.",
    "fm_sort_bottom": "Move to Bottom: Place the selected files at the end of the merge list.",
    "fm_sort_remove": "Remove: Take the selected files out of the merge list (does not delete files from disk).",
    "fm_add_all": "Add All: Add every file matching your current filters and search text to the merge list.",
    "fm_save": "Update Project: Commit your changes to the project's .allcode file and return to the main window.",
    "fm_remove_all": "Remove All: Clear the entire merge list for the current profile.",

    # Settings Window
    "set_app": "Various settings related to application behavior.",
    "set_app_new_file": (
        "File Monitoring: Monitors your project folder for new files added since your last session. "
        "Disable this if you do not want new file warnings or do not want to spend resources on it."
    ),
    "set_app_interval": (
        "Check Interval: How frequently CodeMerger scans the disk for changes. Lower values are more "
        "responsive, but may impact performance on slow drives."
    ),
    "set_app_secrets": (
        "Secret Scanning: Uses 'detect-secrets' to look for API keys or private credentials before you copy. "
        "Enable this to prevent accidentally sharing sensitive data with the language model."
    ),
    "set_app_feedback": (
        "AI Response Review: Automatically open the response review window when wrapped sections are found."
    ),
    "set_app_compact": (
        "Compact Mode: Automatically switches to the compact window when you minimize the "
        "main window. Useful for keeping CodeMerger easily accessible while working in your IDE."
    ),
    "set_app_updates": (
        "Automatic Updates: Checks GitHub for a new version once per day."
    ),
    "set_app_check_now": (
        "Check Now: Manually trigger an update check to see if a newer version of CodeMerger "
        "is available on GitHub, bypassing the automatic daily timer."
    ),

    "set_fm": "Settings that determine the behavior of the merge list editor.",
    "set_fm_tokens": (
        "Token Counting: Calculates context usage based on the gpt-4 tokenizer. "
        "Disable this if you want to speed up file indexing in extremely large projects."
    ),
    "set_fm_limit": (
        "Context Limit: Set a target token count (e.g. 200000 for ChatGPT). The token count in the merge list editor will "
        "turn red if you exceed this."
    ),
    "set_fm_threshold": (
        "Add All Safety: A warning threshold for the 'Add All' button. Prevents accidentally adding "
        "a large amount of files to your merge list."
    ),
    "set_fm_alert_threshold": (
        "New File Warning: When applying AI changes that create new files, CodeMerger will skip the "
        "confirmation dialog if the count of new files is below this number. Deletions always trigger a warning."
    ),

    "set_prompts": "Define your default intro/outro texts.",
    "set_prompt_merged": (
        "Default Header: The text prepended when using 'Copy Code Only'. Best used for a short "
        "instruction, telling the AI to use the code as updated context."
    ),
    "set_prompt_intro": (
        "Global Intro: Generic greeting and mission statement. You can easily load this into a new project "
        "from the 'Instructions' window, to save time on project setup."
    ),
    "set_prompt_outro": (
        "Global Outro: Put code style instructions here. Ideal for enforcing formatting rules like "
        "'Always end your output with a clear explanation' across all your AI interactions."
    ),

    "set_starter": "Settings for the Project Starter tool.",
    "set_starter_folder": "Default Root: The parent directory where the Project Starter will create new project sub-folders by default.",

    "set_editor": "Overrule the default code editor to use when double-clicking files. Leave blank to use system defaults.",
    "set_editor_path": (
        "Editor Path: Provide the path to your code editor's executable (e.g., sublime_text.exe). "
        "When set, double-clicking files in the editor opens them directly in this application."
    ),

    # Instructions Window
    "inst_intro": "Intro Instructions: This text is placed at the very top of your merged code block. Use it to introduce your project.",
    "inst_outro": "Outro Instructions: This text is placed at the bottom. Use it for code style rules or recurring constraints.",
    "inst_defaults": "Load Defaults: Click to wipe the current fields and load the global default prompts you defined in the Settings.",
    "inst_save": "Save: Commit these instructions to the project's .allcode file. They are profile-specific.",

    # Filetype Manager
    "ft_list": "Indexed Types: Only files matching these extensions are scanned. Double-click to enable or disable.",
    "ft_action": "Active Toggle: Delete custom extensions or toggle the active status of bundled default extensions.",
    "ft_add": "Add Filetype: Type a new extension (e.g. .py or .js) and a short description to add it to the indexing list.",

    # Project Selector
    "sel_list": "Recent Projects: Quickly switch to another CodeMerger project. Hover over an entry to see the full path and Ctrl-Click to open it's folder.",
    "sel_filter": "Project Filter: Start typing to narrow down the list by folder name or display title.",
    "sel_browse": "Add Project: Open a directory browser to select a new folder for use with CodeMerger.",
    "sel_remove": "Remove Entry: Take this project off your recent list. This does not delete any files on your computer.",

    # Paste Changes
    "paste_text": "Paste Area: Paste the full Markdown response from the AI here. CodeMerger will look for '--- File: `path` ---' tags.",
    "paste_apply": "Apply Changes: CodeMerger will parse the code, validate the paths, and overwrite your local files with the new content.",
    "paste_unformatted": (
        "Unformatted Response: This response contained commentary that was not properly wrapped in the requested XML tags. "
        "Review this tab to see what the AI said, and use the Correction button to ask for a reformatted reply."
    ),
    "paste_admonish": "Admonish AI: Copies a specialized instruction to your clipboard, telling the AI that the tool cannot use its previous unformatted response.",

    # AI Response Review
    "review_tabs": "Review Tabs: Switch between the different sections of the AI's response (Intro, Changes, Answers, etc.) to review the commentary before applying.",
    "review_tab_intro": "Intro: A technical implementation plan or architectural summary provided by the AI before the code.",
    "review_tab_changes": (
        "Changes: An interactive list of all file modifications. You can review individual file diffs, "
        "accept specific changes, or discard unwanted updates before applying the rest."
    ),
    "review_tab_answers": "Answers: The AI's responses to any conceptual or theoretical questions you asked.",
    "review_tab_delete": "Delete: Files that the AI has identified as obsolete. (Note: CodeMerger does not automatically delete files from your disk).",
    "review_tab_verification": "Verification: Steps provided by the AI to test and verify the applied changes.",
    "review_tab_unformatted": "Unformatted Output: Text from the AI that was not properly wrapped in the requested XML tags. Review this carefully.",
    "review_tab_placeholder": "Response Summary: The AI response contained only code blocks with no accompanying text or tagged sections.",
    "review_auto_show": "Auto-Show Toggle: If unchecked, CodeMerger will instantly apply AI changes in the future without showing this review window first.",
    "review_apply": "Apply Changes: Accept the proposed changes and write them to your project files.",
    "review_cancel": "Cancel: Discard the proposed changes. Your project files will remain untouched.",
    "review_close": "Close: Exit the review window.",
    "review_admonish": "Copy Correction Prompt: Copies a prompt telling the AI that it failed to follow the required output format.",
    "review_diff": (
        "Diff Viewer: Toggle a line-by-line comparison between your local file and the AI version. "
        "Green highlights indicate additions, red indicates removals."
    ),
    "review_file_action": (
        "File Actions: Choose to Accept or Discard changes for individual files. Handled files are "
        "crossed out in the list. You can 'Undo' a choice before applying the full update."
    ),
    "review_commentary": "AI Commentary: Read the specific technical explanation provided by the AI for the proposed changes.",

    # New Profile Dialog
    "profile_name": "Profile Name: Enter a unique label for this configuration (e.g. 'Frontend' or 'Feature Name').",
    "profile_copy_files": "Clone Selection: If checked, the new profile will start with the exact same files selected in your current merge list.",
    "profile_copy_inst": "Clone Instructions: If checked, the new profile will inherit the current custom Intro and Outro instructions.",
    "profile_create": "Create Profile: Saves the new profile. New profiles have independent tracking for 'New Files' detected on disk.",

    # Project Starter
    "starter_nav_prev": "Previous Step: Go back to review or change settings in earlier steps.",
    "starter_nav_next": "Next Step: Proceed to the next phase. Validates current input before moving.",
    "starter_nav_reset": "Reset Step: Clear the current form or editor to start this specific step over.",
    "starter_header_save": "Save Config: Export your current project configuration (concept, stack, plan) to a JSON file.",
    "starter_header_load": "Load Config: Restore a previously saved project configuration.",
    "starter_header_clear": "Clear All: Completely reset the project starter to the beginning.",

    "starter_details_name": "Project Name: The name of your application. This will be used for the folder name and the README title.",
    "starter_details_base": "Base Project: Optionally select an existing folder to use as a reference. Useful for 'v2' rewrites or analyzing existing code.",

    "starter_concept_goal": "User Goal: Briefly describe what you want to build. This is the seed for the AI to generate the full concept.",
    "starter_concept_gen": (
        "Generate Concept: Copies a structured prompt to your clipboard. You must paste this into your LLM "
        "to generate the features list and user flow, then copy the result back here (preferably as Markdown)."
    ),
    "starter_concept_review": "Concept Editor: Review the generated concept. You can edit the text directly or use the 'Rewrite' button to refine it.",

    "starter_stack_exp": "Experience: List your preferred languages and tools. The AI will recommend a stack that matches your skills.",
    "starter_stack_gen": (
        "Generate Stack: Copies a prompt to your clipboard asking the AI to recommend the best technologies. "
        "Paste the AI's response back into the input field below."
    ),
    "starter_stack_edit": "Stack List: The final list of technologies. You can manually edit this list before generating the plan.",

    "starter_todo_gen": (
        "Generate Plan: Copies a prompt to your clipboard to create an implementation plan (TODO.md). "
        "Paste the AI's response back into the input field below."
    ),
    "starter_todo_review": "Plan Editor: Review the generated tasks. Ensure no critical features are missing.",

    "starter_gen_parent": "Parent Folder: The directory where your new project folder will be created.",
    "starter_gen_prompt": (
        "Master Prompt: Copies the final boilerplate instruction to your clipboard. Paste this into your LLM "
        "to generate the initial codebase, then copy the result and paste it into the response field below."
    ),
    "starter_gen_response": "Paste Response: Paste the AI's output here. The app will parse the file blocks and create the files.",
    "starter_gen_create": "Create Files: Write the generated files to disk and initialize the project.",
    "starter_gen_process": (
        "Process Response: Analyze the pasted LLM output. CodeMerger will look for the required "
        "segment tags to populate the editor for the next phase of review."
    ),

    "starter_seg_nav": "Navigation: Jump between different segments.",
    "starter_seg_signoff": "Sign Off: Lock this segment. When all segments are signed off, you can merge them into a single document.",
    "starter_seg_indicator": (
        "Segment Status: Shows if a section is locked (signed off). "
        "Click the icon to instantly toggle the lock state without switching views."
    ),
    "starter_seg_rewrite": "Rewrite: Provide a specific instruction to rewrite this segment and all unsigned segments.",
    "starter_seg_sync": "Sync: Propagate manual edits from this segment to other unsigned segments to keep the document consistent.",
    "starter_seg_questions": "Questions: See guiding questions to help you verify the quality of this segment.",
    "starter_seg_unlock": "Unlock to Edit: Releases the sign-off for the current segment, allowing you to make manual edits or include it in a 'Rewrite' operation.",
    "starter_seg_merge": "Merge Segments: Finalizes the individual sections and assembles them into a single Markdown document for the next phase of the project.",

    "starter_view_toggle": (
        "View Toggle: Switch between a stylized Markdown preview and a raw text editor for manual adjustments. "
        "Be careful: manual changes could create a conflict with other segments. Use 'Rewrite' to avoid this."
    ),

    # Rewrite Dialog
    "rewrite_instruction": (
        "Modification Instruction: Tell the AI what you want to change in the project drafts. "
        "For example: 'Change the primary data entity from Projects to Tasks' or 'Use a more formal tone'."
    ),
    "rewrite_copy_prompt": (
        "Generate Prompt: Compiles your instructions with the current drafts and locked segments. "
        "Clicking this copies the prompt to your clipboard for use with an LLM."
    ),
    "rewrite_response": (
        "Paste Area: Paste the LLM's updated segments here. Ensure the tags like <SECTION name=\"Name\"> are preserved."
    ),
    "rewrite_apply": (
        "Apply Changes: Processes the response and updates the project starter drafts. Any change notes "
        "provided by the AI in <NOTES> tags will be displayed for your review."
    )
}
```

--- End of file ---

--- File: `src/ui/info_manager.py` ---

```python
import tkinter as tk
import re
from .. import constants as c
from .assets import assets
from .info_messages import INFO_MESSAGES
from .tooltip import ToolTip

class InfoManager:
    """
    Manages a single window's Info Panel and Toggle Button.
    Subscribes to global AppState for synchronized visibility across windows.
    Automatically grows/shrinks the window height when toggled.
    """
    def __init__(self, window, app_state, manager_type, toggle_btn, grid_row=None):
        self.window = window
        self.app_state = app_state
        self.manager_type = manager_type # 'grid' or 'pack'
        self.grid_row = grid_row
        self.toggle_btn = toggle_btn
        self.panel_height = c.INFO_PANEL_HEIGHT

        # Force absolute zero padding on the button widget itself to touch window borders
        self.toggle_btn.config(borderwidth=0, highlightthickness=0, padx=0, pady=0)

        self._active_stack = []

        # Info Panel
        self.panel = tk.Frame(
            window, bg=c.INFO_PANEL_BG, height=self.panel_height,
            highlightbackground=c.WRAPPER_BORDER, highlightthickness=1
        )
        self.panel.pack_propagate(False)

        # Robust initial width estimation
        initial_w = window.winfo_width()
        if initial_w <= 1: initial_w = window.winfo_reqwidth()
        if initial_w <= 1: initial_w = 400

        self.label = tk.Label(
            self.panel, text=INFO_MESSAGES["default"],
            bg=c.INFO_PANEL_BG, fg=c.TEXT_SUBTLE_COLOR,
            font=c.FONT_INFO_PANEL, justify="left",
            wraplength=initial_w - 40, anchor="w"
        )
        self.label.pack(side="left", padx=10, fill="both", expand=True)

        self.button_tooltip = ToolTip(self.toggle_btn, text="Toggle Info Mode")

        # Toggle Button Configuration
        self.toggle_btn.bind("<Button-1>", lambda e: self.app_state.toggle_info_mode())
        self.toggle_btn.bind("<Enter>", self._on_button_enter, add="+")
        self.toggle_btn.bind("<Leave>", self._on_button_leave, add="+")

        # Re-calculate wraplength whenever the window size is updated.
        self.window.bind("<Configure>", self._on_window_resize, add="+")
        self.app_state.register_info_observer(self.refresh_visibility)

        self.is_initialized = False
        self._apply_visibility_ui(self.app_state.info_mode_active)
        self.is_initialized = True

    def clear_active_stack(self):
        """Forcefully clears the hover stack. Call this before destroying widgets in the Wizard."""
        self._active_stack = []
        self._update_display()

    def _on_window_resize(self, event=None):
        """Updates the wraplength to ensure help text uses the available panel width."""
        if self.panel.winfo_ismapped():
            w = self.window.winfo_width()
            if w > 1:
                self.label.config(wraplength=w - 40)

    def _adjust_window_height(self, expand: bool):
        """Physically resizes the window to accommodate the panel appearance."""
        if not self.window.winfo_exists(): return
        self.window.update_idletasks()
        geom = self.window.geometry()
        match = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
        if not match: return
        w, h, x, y = map(int, match.groups())
        new_h = h + self.panel_height if expand else h - self.panel_height
        self.window.geometry(f"{w}x{new_h}+{x}+{y}")

    def refresh_visibility(self, is_active):
        """Global callback to sync visibility and window size."""
        self._apply_visibility_ui(is_active)
        if self.is_initialized: self._adjust_window_height(expand=is_active)

    def _apply_visibility_ui(self, is_active):
        """
        Updates the panel visibility and shifts the toggle button to sit
        exactly flush with the left border, jumping above the panel when active.
        """
        if is_active:
            if self.manager_type == 'grid': self.panel.grid(row=self.grid_row, column=0, sticky="ew")
            else: self.panel.pack(side="bottom", fill="x")
            self.button_tooltip.text = ""
            # Button sits on top of the panel, flush with left window border (x=0)
            self.toggle_btn.place(x=0, rely=1.0, y=-self.panel_height, anchor='sw')
        else:
            if self.manager_type == 'grid': self.panel.grid_forget()
            else: self.panel.pack_forget()
            self.button_tooltip.text = "Toggle Info Mode"
            # Button sits at absolute bottom left corner (x=0)
            self.toggle_btn.place(x=0, rely=1.0, y=0, anchor='sw')

        self.toggle_btn.lift()
        # Like Settings/Filetypes, the resting icon is always the standard one
        self._update_button_icon(False)

    def _on_button_enter(self, event):
        # On hover, always swap to the active (blue) icon
        self._update_button_icon(True)

    def _on_button_leave(self, event):
        # On leave, always return to the standard (gray) icon
        self._update_button_icon(False)

    def _update_button_icon(self, show_active_visuals):
        """Swaps the PhotoImage on the toggle button label."""
        icon = assets.info_icon_active if show_active_visuals else assets.info_icon
        if icon:
            self.toggle_btn.config(image=icon, text="")
            # Keep internal reference to prevent garbage collection
            self.toggle_btn.img_ref = icon
            # Force immediate redraw for responsiveness
            self.toggle_btn.update_idletasks()

    def _update_display(self):
        """Updates the label text and enforces wraplength."""
        self._active_stack = [ (w, k) for (w, k) in self._active_stack if w.winfo_exists() ]
        if not self._active_stack:
            self.label.config(text=INFO_MESSAGES["default"], fg=c.TEXT_SUBTLE_COLOR)
            return

        _, key = self._active_stack[-1]

        # Sync width before showing new text to avoid wrap artifacts
        w = self.window.winfo_width()
        if w > 1:
            self.label.config(wraplength=w - 40)

        self.label.config(text=INFO_MESSAGES[key], fg=c.TEXT_COLOR)

    def register(self, widget, key):
        """Binds Enter/Leave events to a widget to trigger info text changes."""
        if key not in INFO_MESSAGES: return
        widget.bind("<Enter>", lambda e: (self._active_stack.append((widget, key)), self._update_display()), add="+")
        widget.bind("<Leave>", lambda e: ((widget, key) in self._active_stack and self._active_stack.remove((widget, key)), self._update_display()), add="+")

def attach_info_mode(window, app_state, manager_type, toggle_btn, grid_row=None):
    """Factory helper to link a window to the Info Mode system."""
    return InfoManager(window, app_state, manager_type, toggle_btn, grid_row)
```

--- End of file ---

--- File: `src/ui/compact_status.py` ---

```python
import tkinter as tk
from .. import constants as c

class CompactStatusToast(tk.Toplevel):
    """
    A temporary, frameless window that displays a status message below its
    parent widget (the compact mode window) and then fades out.
    """
    def __init__(self, parent_widget, message):
        super().__init__(parent_widget)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(bg=c.STATUS_BG, padx=10, pady=5)
        self.attributes("-alpha", 0.0) # Start transparent for fade-in

        label = tk.Label(
            self, text=message, bg=c.STATUS_BG, fg=c.STATUS_FG,
            font=c.FONT_STATUS_BAR, justify='left',
            wraplength=parent_widget.winfo_width()
        )
        label.pack()

        parent_widget.update_idletasks()
        parent_x = parent_widget.winfo_x()
        parent_y = parent_widget.winfo_y()
        parent_h = parent_widget.winfo_height()

        x = parent_x
        y = parent_y + parent_h + 2
        self.geometry(f"+{x}+{y}")

        self.fade_in()
        # Schedule fade out based on the standard status bar duration
        fade_delay_ms = int((c.STATUS_FADE_SECONDS - 0.5) * 1000)
        self.after(fade_delay_ms, self.fade_out)

    def fade_in(self):
        """Gradually increases the window's alpha to 1.0."""
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.15
            self.attributes("-alpha", min(1.0, alpha))
            self.after(20, self.fade_in)

    def fade_out(self):
        """Gradually decreases the window's alpha to 0.0 and then destroys it."""
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            alpha -= 0.1
            self.attributes("-alpha", max(0.0, alpha))
            self.after(50, self.fade_out)
        else:
            self.destroy()
```

--- End of file ---

--- File: `src/ui/compact_mode.py` ---

```python
import tkinter as tk
from tkinter import messagebox
from .. import constants as c
from .widgets.rounded_button import RoundedButton

class CompactMode(tk.Toplevel):
    """
    A frameless, always-on-top, draggable window that provides quick access
    to core functions when the main window is minimized.
    """
    def __init__(self, parent, close_callback, project_name, instance_color=c.COMPACT_MODE_BG_COLOR, font_color_name='light', show_wrapped_button=False, on_move_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.close_callback = close_callback
        self.on_move_callback = on_move_callback
        self.project_name = project_name
        self.tooltip_window = None
        self.new_files_button = None
        self.show_wrapped_button = show_wrapped_button
        self.current_new_file_count = 0

        # These will be updated by the main App's ButtonStateManager
        self.paste_tooltip_text = "Paste Response"
        self.copy_tooltip_text = "Copy Prompt with Instructions (Ctrl+Click for 'Copy Prompt')" if self.show_wrapped_button else "Copy Prompt"

        # Style and Layout Constants
        BAR_COLOR = instance_color
        BORDER_COLOR = "#CCCCCC"
        BORDER_WIDTH = c.COMPACT_MODE_BORDER_WIDTH
        MOVE_BAR_HEIGHT = c.COMPACT_MODE_MOVE_BAR_HEIGHT
        text_hex_color = c.TEXT_COLOR if font_color_name == 'light' else '#000000'

        # Window Configuration
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(bg=BORDER_COLOR, padx=BORDER_WIDTH, pady=BORDER_WIDTH)

        # Internal State for Dragging
        self._offset_x = 0
        self._offset_y = 0

        # Main internal container
        self.main_container = tk.Frame(self, bg=c.DARK_BG)
        self.main_container.pack(fill='both', expand=True)

        # Move Bar (Header)
        self.move_bar = tk.Frame(self.main_container, height=MOVE_BAR_HEIGHT, bg=BAR_COLOR, cursor="fleur")
        self.move_bar.pack(fill='x', side='top')

        # App Icon
        self.app_icon_image = self.parent.assets.compact_icon_tk
        if self.app_icon_image:
            self.app_icon_label = tk.Label(self.move_bar, image=self.app_icon_image, bg=BAR_COLOR)
            self.app_icon_label.pack(side='left', padx=(2, 1), pady=3)

        # Project title abbreviation logic
        max_len = c.COMPACT_MODE_PROJECT_TITLE_MAX_LENGTH
        capital_indices = [i for i, char in enumerate(project_name) if 'A' <= char <= 'Z']

        if len(capital_indices) > 1:
            lowercase_indices = [i for i, char in enumerate(project_name) if 'a' <= char <= 'z']
            lowercase_needed = max_len - len(capital_indices)

            if lowercase_needed > 0:
                indices_to_keep = capital_indices + lowercase_indices[:lowercase_needed]
            else:
                indices_to_keep = capital_indices[:max_len]

            indices_to_keep.sort()
            title_abbr = "".join(project_name[i] for i in indices_to_keep)
        else:
            no_space_title = project_name.replace(' ', '')
            title_abbr = no_space_title[:max_len]

        self.title_label = tk.Label(self.move_bar, text=title_abbr, bg=BAR_COLOR, fg=text_hex_color, font=c.FONT_COMPACT_TITLE)
        self.title_label.pack(side='left', padx=(0, 4))

        # Right-aligned icons container
        self.right_icons_frame = tk.Frame(self.move_bar, bg=BAR_COLOR)
        self.right_icons_frame.pack(side='right')

        # Close Button
        self.close_button = tk.Label(self.right_icons_frame, image=self.parent.assets.compact_mode_close_image, bg=BAR_COLOR, cursor="hand2")
        self.close_button.pack(side='right', padx=(0, 1))

        # Button Container (Body)
        button_container = tk.Frame(self.main_container, bg=c.DARK_BG, padx=4, pady=0)
        button_container.pack(fill='x', side='top')

        button_font = c.FONT_COMPACT_BUTTON
        button_height = 24
        button_radius = 4
        button_fg = '#FFFFFF'

        # Unified copy button
        copy_button_text = "Copy Prompt (i)" if self.show_wrapped_button else "Copy Prompt"
        copy_button_bg = c.BTN_BLUE if self.show_wrapped_button else c.BTN_GRAY_BG
        copy_button_fg = c.BTN_BLUE_TEXT if self.show_wrapped_button else c.BTN_GRAY_TEXT
        self.copy_button = RoundedButton(
            button_container, text=copy_button_text, font=button_font,
            bg=copy_button_bg, fg=copy_button_fg,
            command=None,
            height=button_height, radius=button_radius, cursor='hand2'
        )
        self.copy_button.pack(fill='x', pady=(4, 2))

        # Paste Row Frame
        paste_row = tk.Frame(button_container, bg=c.DARK_BG)
        paste_row.pack(fill='x', pady=(2, 4))

        self.paste_button = RoundedButton(
            paste_row, text="Paste", font=button_font,
            bg=c.BTN_GREEN, fg=button_fg,
            command=None,
            height=button_height, radius=button_radius, cursor='hand2'
        )
        self.paste_button.pack(side='left', fill='x', expand=True, padx=(0, 0))

        # AI Response Review Button
        # Permanent narrow orange button to the right of Paste.
        self.review_button = RoundedButton(
            paste_row, text="", font=button_font,
            bg=c.ATTENTION, fg="#FFFFFF",
            command=lambda: self.parent.action_handlers.show_response_review(force_verification=True),
            width=12, height=button_height, radius=button_radius, cursor='hand2'
        )

        # Show immediately if data exists
        if self.parent.last_ai_response:
            self.review_button.pack(side='right', padx=(4, 0))

        # Override the command with specific bindings for ctrl-click
        self.copy_button.bind("<Button-1>", self.on_copy_click)
        self.copy_button.unbind("<ButtonRelease-1>")
        self.copy_button.bind("<ButtonRelease-1>", self.on_copy_release)

        self.paste_button.bind("<Button-1>", self.on_paste_click)
        self.paste_button.unbind("<ButtonRelease-1>")
        self.paste_button.bind("<ButtonRelease-1>", self.on_paste_release)

        # Bindings
        self.move_bar.bind("<ButtonPress-1>", self.on_press_drag)
        self.move_bar.bind("<B1-Motion>", self.on_drag)
        self.move_bar.bind("<ButtonRelease-1>", self.on_release_drag)
        self.move_bar.bind("<Double-Button-1>", self.close_window)
        self.title_label.bind("<ButtonPress-1>", self.on_press_drag)
        self.title_label.bind("<B1-Motion>", self.on_drag)
        self.title_label.bind("<ButtonRelease-1>", self.on_title_release)
        self.title_label.bind("<Double-Button-1>", self.close_window)
        self.right_icons_frame.bind("<ButtonPress-1>", self.on_press_drag)
        self.right_icons_frame.bind("<B1-Motion>", self.on_drag)
        self.right_icons_frame.bind("<ButtonRelease-1>", self.on_release_drag)
        self.right_icons_frame.bind("<Double-Button-1>", self.close_window)
        self.close_button.bind("<ButtonRelease-1>", self.close_window)

        if self.app_icon_image:
            self.app_icon_label.bind("<ButtonPress-1>", self.on_press_drag)
            self.app_icon_label.bind("<B1-Motion>", self.on_drag)
            self.app_icon_label.bind("<ButtonRelease-1>", self.on_release_drag)
            self.app_icon_label.bind("<Double-Button-1>", self.close_window)

        # Tooltips
        self.copy_button.bind("<Enter>", lambda e: self.show_tooltip(self.copy_tooltip_text))
        self.copy_button.bind("<Leave>", self.hide_tooltip)

        self.paste_button.bind("<Enter>", lambda e: self.show_tooltip(self.paste_tooltip_text))
        self.paste_button.bind("<Leave>", self.hide_tooltip)

        self.review_button.bind("<Enter>", lambda e: self.show_tooltip("Read latest AI response review"))
        self.review_button.bind("<Leave>", self.hide_tooltip)
        self.close_button.bind("<Enter>", lambda e: self.show_tooltip("Restore window (Ctrl+Click to exit app)"))
        self.close_button.bind("<Leave>", self.hide_tooltip)

        # Keyboard shortcuts
        self.bind("<Control-c>", lambda event: self.parent.action_handlers.copy_wrapped_code())
        self.bind("<Control-Shift-C>", lambda event: self.parent.action_handlers.copy_merged_code())
        self.bind("<Control-v>", lambda event: self.parent.action_handlers.open_paste_changes_dialog())
        self.bind("<Control-Shift-V>", lambda event: self.parent.action_handlers.apply_changes_from_clipboard())

    def on_title_release(self, event):
        """Handles clicks on the title for shortcuts while maintaining drag logic."""
        self.on_release_drag(event)

        # Check if click was inside label boundaries
        if 0 <= event.x <= self.title_label.winfo_width() and 0 <= event.y <= self.title_label.winfo_height():
            is_ctrl = (event.state & 0x0004)
            is_alt = (event.state & 0x20000)

            # Only trigger if a shortcut modifier is held to avoid opening explorer on a standard drag/click
            if is_ctrl or is_alt:
                self.parent.action_handlers.open_project_folder(event)

    def on_copy_click(self, event):
        self.copy_button._draw(self.copy_button.click_color)

    def on_copy_release(self, event):
        if 0 <= event.x <= self.copy_button.winfo_width() and 0 <= event.y <= self.copy_button.winfo_height():
            self.copy_button._draw(self.copy_button.hover_color)
            is_ctrl = (event.state & 0x0004)
            if is_ctrl:
                self.parent.action_handlers.copy_merged_code(self.copy_button)
            else:
                if self.show_wrapped_button:
                    self.parent.action_handlers.copy_wrapped_code(self.copy_button)
                else:
                    self.parent.action_handlers.copy_merged_code(self.copy_button)
        else:
            self.copy_button._draw(self.copy_button.base_color)

    def on_paste_click(self, event):
        self.paste_button._draw(self.paste_button.click_color)

    def on_paste_release(self, event):
        if 0 <= event.x <= self.paste_button.winfo_width() and 0 <= event.y <= self.paste_button.winfo_height():
            self.paste_button._draw(self.paste_button.hover_color)
            is_ctrl = (event.state & 0x0004)
            is_alt = (event.state & 0x20000)

            if is_alt:
                # Manual paste window (fallback)
                self.parent.action_handlers.open_paste_changes_dialog()
            elif is_ctrl:
                # Toggle feedback (opposite of setting)
                self.parent.action_handlers.apply_changes_from_clipboard(force_toggle_feedback=True)
            else:
                # Default behavior: Apply changes (follows setting)
                self.parent.action_handlers.apply_changes_from_clipboard(force_toggle_feedback=False)
        else:
            self.paste_button._draw(self.paste_button.base_color)

    def _exit_and_open_file_manager(self):
        self.close_callback()
        self.parent.after(int(c.ANIMATION_DURATION_SECONDS * 1000) + 50, self.parent.action_handlers.manage_files)

    def on_new_files_release(self, event):
        if self.new_files_button:
            if 0 <= event.x <= self.new_files_button.winfo_width() and 0 <= event.y <= self.new_files_button.winfo_height():
                self.new_files_button._draw(self.new_files_button.hover_color)
                self.hide_tooltip()
                is_ctrl = (event.state & 0x0004)
                if is_ctrl:
                    if self.current_new_file_count > 20:
                        if not messagebox.askyesno("Confirm Add All", f"You are about to add {self.current_new_file_count} files to the merge list.\n\nAre you sure?", parent=self):
                            self.new_files_button._draw(self.new_files_button.base_color)
                            return
                    self.parent.action_handlers.add_new_files_to_merge_order()
                else:
                    self._exit_and_open_file_manager()
            else:
                self.new_files_button._draw(self.new_files_button.base_color)

    def show_warning(self, file_count, project_name):
        self.current_new_file_count = file_count
        bg_color = self.move_bar.cget('bg')

        # Select the appropriate icon based on the threshold
        if file_count > 20:
            icon_image = self.parent.assets.new_files_many_compact_pil
        else:
            icon_image = self.parent.assets.new_files_compact_pil

        if not self.new_files_button:
            self.new_files_button = RoundedButton(
                self.right_icons_frame,
                command=None,
                image=icon_image,
                bg=bg_color,
                width=20,
                height=14,
                radius=3,
                cursor="hand2"
            )
            self.new_files_button.pack(side='left', padx=(0, 2))
            self.new_files_button.unbind("<ButtonRelease-1>")
            self.new_files_button.bind("<ButtonRelease-1>", self.on_new_files_release)
            tooltip_text = "New files found.\nClick: Open manager\nCtrl+Click: Add all to merge"
            self.new_files_button.bind("<Enter>", lambda e, text=tooltip_text: self.show_tooltip(text))
            self.new_files_button.bind("<Leave>", self.hide_tooltip)
        else:
            # If the button exists but the image requirement changed (e.g. crossed threshold), recreate it
            if self.new_files_button.image != icon_image:
                self.new_files_button.destroy()
                self.new_files_button = RoundedButton(
                    self.right_icons_frame,
                    command=None,
                    image=icon_image,
                    bg=bg_color,
                    width=20,
                    height=14,
                    radius=3,
                    cursor="hand2"
                )
                self.new_files_button.pack(side='left', padx=(0, 2))
                self.new_files_button.unbind("<ButtonRelease-1>")
                self.new_files_button.bind("<ButtonRelease-1>", self.on_new_files_release)
                tooltip_text = "New files found.\nClick: Open manager\nCtrl+Click: Add all to merge"
                self.new_files_button.bind("<Enter>", lambda e, text=tooltip_text: self.show_tooltip(text))
                self.new_files_button.bind("<Leave>", self.hide_tooltip)

    def hide_warning(self, project_name):
        if self.new_files_button:
            self.new_files_button.destroy()
            self.new_files_button = None

    def show_tooltip(self, text, event=None):
        if self.tooltip_window: return
        x = self.winfo_rootx() + self.winfo_width() // 2
        y = self.winfo_rooty() + self.winfo_height() + 5
        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=text, justify='left', bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1, font=c.FONT_TOOLTIP)
        label.pack(ipadx=4, ipady=2)
        self.tooltip_window.update_idletasks()
        new_x = x - (self.tooltip_window.winfo_width() // 2)
        self.tooltip_window.wm_geometry(f"+{new_x}+{y}")

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

    def close_window(self, event=None):
        if event and not (0 <= event.x <= event.widget.winfo_width() and 0 <= event.y <= event.widget.winfo_height()):
            return
        if event and (event.state & 0x0004):
            self.parent.event_handlers.on_app_close()
        elif self.close_callback:
            self.close_callback()

    def on_press_drag(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def on_drag(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def on_release_drag(self, event):
        if self.on_move_callback:
            self.on_move_callback()
```

--- End of file ---

--- File: `src/ui/view_manager.py` ---

```python
import time
import os
import logging
from tkinter import messagebox, Toplevel
from .compact_mode import CompactMode
from .assets import assets
from .window_utils import get_monitor_work_area
from .. import constants as c

log = logging.getLogger("CodeMerger")

class ViewManager:
    """
    Manages the visual state of the application, specifically the
    transition between the full view and compact mode using a state machine
    to animate correctly while avoiding OS window manager race conditions.
    Preserves compact mode coordinates unless the main window is moved to a
    different monitor.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        # State machine states
        self.STATE_NORMAL = 'normal'
        self.STATE_SHRINKING = 'shrinking'
        self.STATE_COMPACT = 'compact'
        self.STATE_GROWING = 'growing'
        self.current_state = self.STATE_NORMAL

        self.compact_mode_window = None
        self.compact_mode_last_x = None
        self.compact_mode_last_y = None

        # Tracks the monitor handle where Compact Mode was last active or where
        # coordinates were invalidated.
        self.compact_last_monitor_handle = None

        self.main_window_geom = None

    def on_main_window_minimized(self, event=None):
        """
        Called when the main window is unmapped (minimized).
        """
        if self.current_state == self.STATE_NORMAL and self.main_window.app_state.enable_compact_mode_on_minimize:
            def check_and_transition():
                if self.current_state == self.STATE_NORMAL and self.main_window.state() == 'iconic':
                    log.info("Main window minimized. Transitioning to Compact Mode.")
                    self.transition_to_compact()

            self.main_window.after(50, check_and_transition)

    def on_main_window_restored(self, event=None):
        """
        Called when the main window is restored (e.g., from the taskbar).
        """
        if self.current_state == self.STATE_COMPACT:
            log.info("Main window restored. Transitioning to Normal Mode.")
            self.transition_to_normal()

    def exit_compact_mode_manually(self):
        """
        A dedicated method for when the user closes the compact window directly.
        """
        if self.current_state == self.STATE_COMPACT:
            log.info("Exiting Compact Mode via manual close.")
            self.transition_to_normal()

    def on_compact_mode_moved(self):
        """Callback executed when the compact mode window is moved by the user."""
        if self.compact_mode_window and self.compact_mode_window.winfo_exists():
            self.compact_mode_last_x = self.compact_mode_window.winfo_x()
            self.compact_mode_last_y = self.compact_mode_window.winfo_y()
            log.debug(f"Saved compact mode position: {self.compact_mode_last_x}, {self.compact_mode_last_y}")

    def invalidate_compact_mode_position(self):
        """Forgets the last position, forcing recalculation on the next compact transition."""
        if self.compact_mode_last_x is not None:
            log.info("Invalidating compact mode position memory due to monitor change.")
            self.compact_mode_last_x = None
            self.compact_mode_last_y = None

    def _animate_window(self, start_time, duration, start_geom, end_geom, is_shrinking):
        """Helper method to animate the main window's geometry and alpha with easing."""
        if not self.main_window.winfo_exists():
            return

        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / duration)
        # Cubic easing for smoother start/stop
        eased_progress = progress * progress * (3.0 - 2.0 * progress)

        start_x, start_y, start_w, start_h = start_geom
        end_x, end_y, end_w, end_h = end_geom

        curr_x = int(start_x + (end_x - start_x) * eased_progress)
        curr_y = int(start_y + (end_y - start_y) * eased_progress)
        curr_w = int(start_w + (end_w - start_w) * eased_progress)
        curr_h = int(start_h + (end_h - start_h) * eased_progress)

        alpha = 1.0 - progress if is_shrinking else progress
        if not is_shrinking and alpha < 0.01: alpha = 0.01

        try:
            self.main_window.geometry(f"{max(1, curr_w)}x{max(1, curr_h)}+{curr_x}+{curr_y}")
            self.main_window.attributes("-alpha", alpha)
        except Exception:
            pass

        if progress < 1.0:
            self.main_window.after(15, self._animate_window, start_time, duration, start_geom, end_geom, is_shrinking)
        else:
            self._on_animation_complete(is_shrinking, end_geom)

    def _on_animation_complete(self, is_shrinking, final_geom):
        """Handles state changes after an animation finishes."""
        if is_shrinking:
            log.debug("Shrink animation complete.")
            # Restoration logic forces alpha to 0.01 and calls update() before minimizing.
            # This workaround forces the Windows DWM to update the taskbar thumbnail
            # with the full-sized window buffer instead of a black or shrunken artifact.
            if self.main_window_geom:
                w, h, x, y = self.main_window_geom[2], self.main_window_geom[3], self.main_window_geom[0], self.main_window_geom[1]
                self.main_window.geometry(f"{w}x{h}+{x}+{y}")
                self.main_window.attributes("-alpha", 0.01)
                self.main_window.update()

            self.main_window.iconify()
            if self.compact_mode_window and self.compact_mode_window.winfo_exists():
                self.compact_mode_window.deiconify()
                # Assertion of topmost and lift beats other apps that may have stolen focus.
                self.compact_mode_window.attributes("-topmost", True)
                self.compact_mode_window.lift()

            self.current_state = self.STATE_COMPACT
        else:
            log.debug("Growth animation complete.")
            self.main_window.geometry(f"{final_geom[2]}x{final_geom[3]}+{final_geom[0]}+{final_geom[1]}")
            self.main_window.attributes("-alpha", 1.0)
            self.main_window.minsize(c.MIN_WINDOW_WIDTH, c.MIN_WINDOW_HEIGHT)

            # Lazy Layout: Restore UI content after animation finishes
            self.main_window._end_lazy_layout()

            if self.compact_mode_window and self.compact_mode_window.winfo_exists():
                self.compact_mode_window.destroy()
                self.compact_mode_window = None
            self.current_state = self.STATE_NORMAL

    def transition_to_compact(self):
        """Starts the process of shrinking the main window and showing the compact view."""
        if self.current_state != self.STATE_NORMAL:
            return

        self.current_state = self.STATE_SHRINKING

        # Lazy Layout: Hide UI content immediately to prevent lag during animation
        self.main_window._start_lazy_layout()

        # Capture current geometry immediately before we start messing with transparency/state
        self.main_window_geom = (
            self.main_window.winfo_x(), self.main_window.winfo_y(),
            self.main_window.winfo_width(), self.main_window.winfo_height()
        )

        # Make transparent and deiconify to take control of the animation
        self.main_window.attributes("-alpha", 0.0)
        self.main_window.deiconify()

        self.main_window.after(c.ANIMATION_START_DELAY_MS, self._start_shrink_animation)

    def _start_shrink_animation(self):
        """The actual animation logic for shrinking."""
        if not self.main_window.winfo_exists(): return

        start_geom = self.main_window_geom
        self.main_window.attributes("-alpha", 1.0)
        self.main_window.minsize(1, 1)

        self._prepare_compact_mode_window()
        # Force the compact window to calculate its dimensions so we have an accurate target
        self.compact_mode_window.update_idletasks()
        widget_w = self.compact_mode_window.winfo_reqwidth()
        widget_h = self.compact_mode_window.winfo_reqheight()

        # Decision Engine: Do we use the user's manual placement or recalculate?
        # Recalculation only occurs if:
        # - We have never saved a position.
        # - The main window has moved to a DIFFERENT physical monitor since the last compact use.
        current_monitor = self.main_window.current_monitor_handle

        monitor_changed = self.compact_last_monitor_handle != current_monitor
        use_saved_position = self.compact_mode_last_x is not None and not monitor_changed

        if use_saved_position:
            log.info(f"Restoring compact position: {self.compact_mode_last_x}, {self.compact_mode_last_y}")
            target_x, target_y = self.compact_mode_last_x, self.compact_mode_last_y
        else:
            log.info(f"Recalculating compact position (Monitor switch: {monitor_changed}).")
            mon_x, mon_y, mon_right, mon_bottom = get_monitor_work_area(self.main_window)
            main_x, main_y, main_w, _ = start_geom

            # Default placement: Top right of the main window area
            ideal_x, ideal_y = main_x + main_w - widget_w - 20, main_y + 20
            margin = 10

            target_x = max(mon_x + margin, min(ideal_x, mon_right - widget_w - margin))
            target_y = max(mon_y + margin, min(ideal_y, mon_bottom - widget_h - margin))

        end_geom = (target_x, target_y, widget_w, widget_h)

        # Update monitor handle for next time
        self.compact_last_monitor_handle = current_monitor

        # Position the compact window but keep it hidden until animation is done
        self.compact_mode_window.geometry(f"+{target_x}+{target_y}")
        self.compact_mode_window.withdraw()

        self._animate_window(time.time(), c.ANIMATION_DURATION_SECONDS, start_geom, end_geom, is_shrinking=True)

    def transition_to_normal(self):
        """Starts the process of growing the main window back to its normal state."""
        if self.current_state != self.STATE_COMPACT:
            return

        if not self.compact_mode_window or not self.compact_mode_window.winfo_exists():
            log.warning("Compact window missing during restore. Aborting animation.")
            self.current_state = self.STATE_NORMAL
            self.main_window.show_and_raise()
            return

        self.current_state = self.STATE_GROWING

        # Lazy Layout: Ensure content is hidden during growth to maintain performance
        self.main_window._start_lazy_layout()

        # Update the saved position before we hide the compact window.
        # This capture must happen while the window is still visible and in a 'normal' state.
        self.compact_mode_last_x = self.compact_mode_window.winfo_x()
        self.compact_mode_last_y = self.compact_mode_window.winfo_y()
        log.debug(f"Saved compact coordinates before restore: {self.compact_mode_last_x}, {self.compact_mode_last_y}")

        start_geom = (self.compact_mode_last_x, self.compact_mode_last_y, self.compact_mode_window.winfo_width(), self.compact_mode_window.winfo_height())

        # Fallback if main geometry was lost
        if not self.main_window_geom:
            self.main_window_geom = (100, 100, 660, 360)

        end_geom = self.main_window_geom

        self.compact_mode_window.withdraw()

        self.main_window.attributes("-alpha", 0.0)
        self.main_window.deiconify()
        self.main_window.geometry(f"{start_geom[2]}x{start_geom[3]}+{start_geom[0]}+{start_geom[1]}")

        self._animate_window(time.time(), c.ANIMATION_DURATION_SECONDS, start_geom, end_geom, is_shrinking=False)

    def _prepare_compact_mode_window(self):
        """Creates the CompactMode Toplevel window and configures it."""
        if self.compact_mode_window and self.compact_mode_window.winfo_exists():
             self.compact_mode_window.destroy()

        project_name = "CodeMerger"
        has_wrapper_text = False
        project_font_color_name = 'light'
        project_config = self.main_window.project_manager.get_current_project()

        if project_config:
            project_name = project_config.project_name
            project_font_color_name = project_config.project_font_color
            if project_config.intro_text or project_config.outro_text:
                has_wrapper_text = True

        self.compact_mode_window = CompactMode(
            parent=self.main_window,
            close_callback=self.exit_compact_mode_manually,
            on_move_callback=self.on_compact_mode_moved,
            project_name=project_name,
            instance_color=self.main_window.project_color,
            font_color_name=project_font_color_name,
            show_wrapped_button=has_wrapper_text
        )
        self.main_window.file_monitor._update_warning_ui()
        self.main_window.button_manager.refresh_paste_tooltips()
        self.compact_mode_window.withdraw()
```

--- End of file ---

--- File: `src/ui/file_monitor.py` ---

```python
import os
from ..core.utils import parse_gitignore
from ..core.file_scanner import get_all_matching_files
from .. import constants as c
from ..core.merger import recalculate_token_count

class FileMonitor:
    """
    Manages periodic checks for new and deleted files.
    Maintains independent 'unknown' state for each project profile.
    Also monitors the configuration file for external changes (e.g. git branch switch).
    """
    def __init__(self, app):
        self.app = app
        self._check_job = None
        self.newly_detected_files = [] # Files 'new' to the CURRENT active profile

    def start(self):
        self.stop()
        self._update_warning_ui()

        is_dir_active = self.app.project_manager.get_current_project() is not None
        if self.app.app_state.config.get('enable_new_file_check', True) and is_dir_active:
            interval_sec = self.app.app_state.config.get('new_file_check_interval', 5)
            self._schedule_next_check(interval_sec * 1000)

    def stop(self):
        if self._check_job:
            self.app.after_cancel(self._check_job)
            self._check_job = None

    def _schedule_next_check(self, interval_ms):
        self._check_job = self.app.after(interval_ms, self.perform_new_file_check)

    def perform_initial_scan(self):
        self.newly_detected_files = []
        self.perform_new_file_check(schedule_next=False)

    def perform_new_file_check(self, schedule_next=True):
        project_config = self.app.project_manager.get_current_project()
        if not project_config:
            self.stop()
            return

        # Check for external config changes (e.g. git switch)
        if project_config.has_external_changes():
            try:
                # Capture current known files from memory before reload.
                # If we switch to a branch where .allcode is empty/fresh, we don't want to lose
                # our "seen" files history, otherwise everything shows up as NEW.
                current_memory_known = set(project_config.known_files)

                # Reload the config from disk to avoid overwriting it with stale state
                # Note: this will raise RuntimeError if the file is currently empty/locked
                project_config.load()

                # Merge memory back into the loaded config
                if current_memory_known:
                    merged_known = set(project_config.known_files) | current_memory_known
                    project_config.known_files = sorted(list(merged_known))

                # Notify UI of the reload
                self.app.status_var.set("Reloaded project settings due to external change.")
                self.app.profile_actions.update_profile_selector_ui()
                self.app.button_manager.update_button_states()

                # Reset local detection state to avoid false positives against old config
                self.newly_detected_files = list(project_config.unknown_files)
                self._update_warning_ui()

            except Exception as e:
                # If load fails (e.g. file locked or corrupt), skip this scan cycle and wait for next interval
                # This prevents triggering a save() on a config object that failed its load latch.
                if schedule_next:
                    interval_sec = self.app.app_state.config.get('new_file_check_interval', 5)
                    self._schedule_next_check(interval_sec * 1000)
                return

        base_dir = project_config.base_dir
        if not os.path.isdir(base_dir):
            self.stop()
            self.app.status_var.set(f"Project directory '{os.path.basename(base_dir)}' no longer exists.")
            self.app.ui_callbacks.on_directory_selected(None)
            return

        # Collect paths that MUST be checked for existence regardless of filters.
        force_include_paths = set()
        for p_data in project_config.profiles.values():
             for f in p_data.get('selected_files', []):
                 force_include_paths.add(f['path'])

        all_project_files = get_all_matching_files(
            base_dir=base_dir,
            file_extensions=self.app.file_extensions,
            gitignore_patterns=parse_gitignore(base_dir),
            always_include_paths=force_include_paths
        )

        current_set = set(all_project_files)
        known_set = set(project_config.known_files)

        config_changed = False

        # Handle Deleted Files
        missing_from_scan = known_set - current_set
        truly_deleted_files = set()

        if missing_from_scan:
            for rel_path in missing_from_scan:
                full_path = os.path.join(base_dir, rel_path)
                if not os.path.exists(full_path):
                    truly_deleted_files.add(rel_path)

        if truly_deleted_files:
            project_config.known_files = list(known_set - truly_deleted_files)
            for p_name, p_data in project_config.profiles.items():
                orig_selection = len(p_data.get('selected_files', []))
                p_data['selected_files'] = [f for f in p_data.get('selected_files', []) if f['path'] not in truly_deleted_files]
                p_data['unknown_files'] = [f for f in p_data.get('unknown_files', []) if f not in truly_deleted_files]
                if len(p_data['selected_files']) != orig_selection:
                    p_data['total_tokens'] = 0
            config_changed = True
            self.app.status_var.set(f"Cleaned {len(truly_deleted_files)} missing file(s).")

        # Handle Brand New Files
        brand_new_files = current_set - set(project_config.known_files)
        if brand_new_files:
            project_config.known_files.extend(list(brand_new_files))
            for p_data in project_config.profiles.values():
                p_unknown = set(p_data.get('unknown_files', []))
                p_unknown.update(brand_new_files)
                p_data['unknown_files'] = sorted(list(p_unknown))
            config_changed = True

        if config_changed:
            project_config.save()

        profile_unknown = project_config.unknown_files
        if sorted(profile_unknown) != sorted(self.newly_detected_files):
            self.newly_detected_files = profile_unknown
            self._update_warning_ui()

        if schedule_next:
            interval_sec = self.app.app_state.config.get('new_file_check_interval', 5)
            self._schedule_next_check(interval_sec * 1000)

    def get_newly_detected_files_and_reset(self):
        """Returns new files for active profile and clears its unknown list."""
        files_to_highlight = self.newly_detected_files[:]
        project_config = self.app.project_manager.get_current_project()

        if files_to_highlight and project_config:
            project_config.unknown_files = []
            project_config.save()
            self.newly_detected_files = []
            self._update_warning_ui()

        return files_to_highlight

    def _update_warning_ui(self):
        file_count = len(self.newly_detected_files)
        if file_count > 0:
            file_str_verb = "file was" if file_count == 1 else "files were"
            self.app.new_files_tooltip.text = f"{file_count} new {file_str_verb} found.\nClick to manage, Ctrl+Click to add all."
            if not self.app.new_files_label.winfo_ismapped():
                self.app.new_files_label.grid(row=0, column=0, sticky='e', padx=(10, 0))
            self.app.manage_files_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.app.new_files_label.grid_forget()
            self.app.manage_files_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

        if self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
            if file_count > 0:
                self.app.view_manager.compact_mode_window.show_warning(file_count, "")
            else:
                self.app.view_manager.compact_mode_window.hide_warning("")
```

--- End of file ---

--- File: `src/ui/app_window_parts/helpers.py` ---

```python
from ..compact_status import CompactStatusToast

class AppHelpers:
    def __init__(self, app):
        self.app = app

    def show_compact_toast(self, message):
        app = self.app
        compact_window = app.view_manager.compact_mode_window
        if compact_window and compact_window.winfo_exists():
            CompactStatusToast(compact_window, message)
        else:
            app.status_var.set(message)

    def animate_loading(self, step=0):
        app = self.app
        dots = (step % 3) + 1
        app.project_title_var.set("Loading" + "." * dots)
        app.loading_animation_job = app.after(400, self.animate_loading, step + 1)

    def stop_loading_animation(self):
        app = self.app
        if app.loading_animation_job:
            app.after_cancel(app.loading_animation_job)
            app.loading_animation_job = None

    def show_and_raise(self):
        app = self.app
        app.deiconify()
        app.lift()
        app.focus_force()

    def show_error_dialog(self, title, message, hint=None):
        from ..custom_error_dialog import CustomErrorDialog
        app = self.app
        dialog_parent = app
        if app.view_manager.current_state == 'compact' and app.view_manager.compact_mode_window and app.view_manager.compact_mode_window.winfo_exists():
            dialog_parent = app.view_manager.compact_mode_window

        CustomErrorDialog(dialog_parent, title, message, hint=hint)
```

--- End of file ---

--- File: `src/ui/app_window_parts/status_bar_manager.py` ---

```python
import time
from ... import constants as c

class StatusBarManager:
    """Manages the behavior and fading animation of the main status bar."""
    def __init__(self, app, status_bar_widget, status_var):
        self.app = app
        self.status_bar = status_bar_widget
        self.status_var = status_var
        self._status_fade_job = None
        self._is_clearing_status = False # Flag to prevent feedback loops
        self.status_var.trace_add('write', self._on_status_update)

    def _interpolate_color(self, start_hex, end_hex, progress):
        """Linearly interpolates between two hex colors."""
        start_r, start_g, start_b = int(start_hex[1:3], 16), int(start_hex[3:5], 16), int(start_hex[5:7], 16)
        end_r, end_g, end_b = int(end_hex[1:3], 16), int(end_hex[3:5], 16), int(end_hex[5:7], 16)

        r = int(start_r + (end_r - start_r) * progress)
        g = int(start_g + (end_g - start_g) * progress)
        b = int(start_b + (end_b - start_b) * progress)

        return f"#{r:02x}{g:02x}{b:02x}"

    def _start_status_fade(self):
        """Kicks off the fade animation."""
        start_time = time.time()
        duration = c.STATUS_FADE_DURATION_SECONDS  # Fade over half a second
        self._fade_status_step(start_time, duration)

    def _fade_status_step(self, start_time, duration):
        """A single step in the fade animation."""
        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / duration)

        new_color = self._interpolate_color(c.STATUS_FG, c.STATUS_BG, progress)
        self.status_bar.config(fg=new_color)

        if progress < 1.0:
            self._status_fade_job = self.app.after(20, self._fade_status_step, start_time, duration)
        else:
            # Once fully faded, clear the text and reset the color for the next message
            self._is_clearing_status = True
            self.status_var.set("")
            self.status_bar.config(fg=c.STATUS_FG)
            self._is_clearing_status = False
            self._status_fade_job = None

    def _on_status_update(self, *args):
        """When the status text changes, this resets its visibility and schedules the fade-out."""
        if self._is_clearing_status:
            return  # Ignore updates triggered by the fade-out process itself

        # If a fade is already in progress, cancel it.
        if self._status_fade_job:
            self.app.after_cancel(self._status_fade_job)
            self._status_fade_job = None

        # Always reset the color to full visibility when a new message arrives.
        self.status_bar.config(fg=c.STATUS_FG)

        current_message = self.status_var.get()

        # If the new message is not empty, schedule it to start fading out.
        if current_message and current_message.strip():
            # Set a delay, after which the fade will begin.
            fade_delay_ms = int((c.STATUS_FADE_SECONDS - 0.5) * 1000)
            self._status_fade_job = self.app.after(fade_delay_ms, self._start_status_fade)
```

--- End of file ---

--- File: `src/ui/app_window_parts/button_state_manager.py` ---

```python
import os
from ... import constants as c

class ButtonStateManager:
    """Handles updating the state of buttons and UI elements in the main window."""
    def __init__(self, app):
        """
        Initializes the ButtonStateManager.
        Args:
            app: The main App instance.
        """
        self.app = app

    def refresh_paste_tooltips(self):
        """Builds and applies dynamic tooltip text for the Paste buttons based on settings."""
        app = self.app

        # Defensive check: if setup_ui hasn't run yet, abort.
        if not hasattr(app, 'paste_changes_tooltip'):
            return

        show_review = app.app_state.config.get('show_feedback_on_paste', True)

        if show_review:
            hint = "Paste: instant apply with review\n(Ctrl+Click: instant apply without review, Alt+Click: manual paste window)"
        else:
            hint = "Paste: instant apply without review\n(Ctrl+Click: instant apply with review, Alt+Click: manual paste window)"

        app.paste_changes_tooltip.text = hint

        # Also sync to compact mode if it's currently active
        compact = app.view_manager.compact_mode_window
        if compact and compact.winfo_exists():
            compact.paste_tooltip_text = hint

    def update_button_states(self, *args):
        """Updates button states based on the active directory and .allcode file."""
        app = self.app
        active_dir_path = app.active_dir.get()
        is_loading = active_dir_path == "Loading..."
        is_dir_active = os.path.isdir(active_dir_path)
        dir_dependent_state = 'normal' if is_dir_active else 'disabled'
        project_config = app.project_manager.get_current_project()

        # Update dynamic tooltips based on current settings
        self.refresh_paste_tooltips()

        # Handle the loading state for the Select Project button
        if is_loading:
            app.select_project_button.set_state('disabled')
        else:
            app.select_project_button.set_state('normal')  # Re-enable the button first
            if is_dir_active:
                app.select_project_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            else:
                app.select_project_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)

        app.manage_files_button.set_state(dir_dependent_state)

        # Update Edit Merge List button appearance based on token limit
        token_limit = app.app_state.config.get('token_limit', 0)
        current_tokens = project_config.total_tokens if project_config else 0

        if is_dir_active and token_limit > 0 and current_tokens > token_limit:
            app.manage_files_button.config(bg=c.WARN, fg='#FFFFFF') # Red bg
            app.manage_files_tooltip.text = f"Token limit exceeded!\nCurrent: {current_tokens:,}\nLimit: {token_limit:,}"
        else:
            app.manage_files_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            app.manage_files_tooltip.text = "Edit project merge list"

        if is_dir_active:
            app.folder_icon_label.grid(row=0, column=1, sticky='e', padx=(10, 0))
            # Generate the masked logo image and apply it to the label
            app.masked_logo_tk = app.assets.create_masked_logo(app.project_color)
            app.color_swatch.config(image=app.masked_logo_tk, bg=c.TOP_BAR_BG)
            if not app.color_swatch.winfo_ismapped():
                 app.color_swatch.pack(side='left', padx=(0, 15), before=app.title_container)
        else:
             app.folder_icon_label.grid_forget()
             if app.color_swatch.winfo_ismapped():
                app.color_swatch.pack_forget()

        if not is_dir_active:
            app.wrapper_box_title.pack_forget()
            app.button_grid_frame.pack_forget()
            app.no_project_label.pack(pady=(20, 30), padx=30)
            app.wrapper_text_button.set_state('disabled')
            app.copy_merged_button.set_state('disabled')
            app.copy_wrapped_button.set_state('disabled')
            app.paste_changes_button.set_state('disabled')
            app.review_button.set_state('disabled')
            app.cleanup_comments_button.place_forget()
        else:
            app.no_project_label.pack_forget()
            app.wrapper_box_title.pack(pady=(10, 5))
            app.button_grid_frame.pack(pady=(5, 18), padx=30)
            app.wrapper_text_button.set_state('normal')
            app.paste_changes_button.set_state('normal')
            app.review_button.set_state('normal')
            app.cleanup_comments_button.place(relx=1.0, y=14, anchor='ne', x=-22)

            copy_buttons_state = 'disabled'
            has_wrapper_text = False
            has_files_selected = False

            if project_config:
                if project_config.selected_files:
                    copy_buttons_state = 'normal'
                    has_files_selected = True
                intro = project_config.intro_text
                outro = project_config.outro_text
                if intro or outro:
                    has_wrapper_text = True

            app.copy_merged_button.set_state(copy_buttons_state)
            app.copy_wrapped_button.set_state(copy_buttons_state)

            # Update Copy Button Tooltips based on file selection
            if has_files_selected:
                app.copy_merged_tooltip.text = "Copy Prompt: merges code and prepends the default context prompt"
                app.copy_wrapped_tooltip.text = "Copy Prompt: includes code wrapped with custom intro/outro instructions"
                compact_copy_tooltip = "Copy Prompt with Instructions (Ctrl+Click for 'Copy Prompt')" if has_wrapper_text else "Copy Prompt"
            else:
                inactive_msg = "Inactive: No files added to the Merge List"
                app.copy_merged_tooltip.text = inactive_msg
                app.copy_wrapped_tooltip.text = inactive_msg
                compact_copy_tooltip = inactive_msg

            # Sync to compact mode if it's currently active
            compact = app.view_manager.compact_mode_window
            if compact and compact.winfo_exists():
                compact.copy_tooltip_text = compact_copy_tooltip

            app.copy_wrapped_button.grid_remove()
            app.copy_merged_button.grid_remove()
            app.wrapper_text_button.grid_remove()
            app.paste_container.grid_remove()

            gap = 5

            if has_wrapper_text:
                # Row 0: Both large copy buttons
                app.copy_wrapped_button.grid(row=0, column=0, sticky='ew', pady=(0, 5), padx=(0, gap))
                app.copy_merged_button.grid(row=0, column=1, sticky='ew', pady=(0, 5), padx=(gap, 0))
            else:
                # Row 0: The single large copy button spans the full width
                app.copy_merged_button.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5), padx=0)

            # Row 1: Small configuration buttons
            app.wrapper_text_button.grid(row=1, column=0, sticky='ew', padx=(0, gap))
            app.paste_container.grid(row=1, column=1, sticky='ew', padx=(gap, 0))

            # AI Response Review Visibility
            # Show if ANY plan exists in memory, as it now supports persistence and undo
            if app.last_ai_response:
                app.review_button.pack(side='right', padx=(4, 0))
            else:
                app.review_button.pack_forget()

            # Compact Mode View
            compact = app.view_manager.compact_mode_window
            if compact and compact.winfo_exists():
                if app.last_ai_response:
                    if not compact.review_button.winfo_ismapped():
                        compact.review_button.pack(side='right', padx=(4, 0))
                else:
                    compact.review_button.pack_forget()
```

--- End of file ---

--- File: `src/ui/app_window_parts/ui_callbacks.py` ---

```python
import os
from ...core.utils import load_active_file_extensions

class UICallbacks:
    def __init__(self, app):
        self.app = app

    def on_settings_closed(self):
        app = self.app
        app.app_state.reload()
        app.file_monitor.start()
        app.button_manager.update_button_states()
        app.button_manager.refresh_paste_tooltips()
        app.status_var.set("Settings updated")

    def on_directory_selected(self, new_dir):
        app = self.app
        if app.app_state.update_active_dir(new_dir):
            app.project_actions.set_active_dir_display(new_dir)

    def on_recent_removed(self, path_to_remove):
        app = self.app
        cleared_active = app.app_state.remove_recent_project(path_to_remove)
        app.status_var.set(f"Removed '{os.path.basename(path_to_remove)}' from recent projects")
        if cleared_active:
            app.project_actions.set_active_dir_display(None)

    def reload_active_extensions(self):
        app = self.app
        app.file_extensions = load_active_file_extensions()
        app.status_var.set("Filetype configuration updated")
        app.file_monitor.start()
```

--- End of file ---

--- File: `src/ui/app_window_parts/project_actions.py` ---

```python
import os
import threading
import logging

from ... import constants as c

log = logging.getLogger("CodeMerger")

class ProjectActions:
    def __init__(self, app):
        self.app = app

    def _start_loading_animation(self):
        app = self.app
        app.helpers.stop_loading_animation()
        app.title_label.config(font=c.FONT_LOADING_TITLE, fg=c.TEXT_SUBTLE_COLOR)
        app.helpers.animate_loading(0)

    def _clear_project_ui(self):
        app = self.app
        app.helpers.stop_loading_animation()
        project_config, status_message = app.project_manager.load_project(None)
        app.status_var.set(status_message)

        app.active_dir.set("No project selected")
        app.project_title_var.set("(no active project)")
        app.project_color = c.COMPACT_MODE_BG_COLOR
        app.project_font_color = 'light'
        app.title_label.config(font=c.FONT_LARGE_BOLD, fg=c.TEXT_SUBTLE_COLOR)

        app.profile_actions.update_profile_selector_ui()
        app.file_monitor.start()
        app.button_manager.update_button_states()

    def set_active_dir_display(self, path, set_status=True):
        app = self.app

        # Clear the last AI response review when switching projects
        app.last_ai_response = None

        if not path or not os.path.isdir(path):
            self._clear_project_ui()
            return

        app.active_dir.set("Loading...")
        self._start_loading_animation()

        app.button_manager.update_button_states()
        app.profile_actions.update_profile_selector_ui()

        self._load_project_async(path, set_status)

    def _load_project_async(self, path, set_status=True):
        app = self.app
        app.load_thread = threading.Thread(
            target=self._load_project_worker,
            args=(path, set_status),
            daemon=True
        )
        app.load_thread.start()
        app.after(100, self._check_load_project_thread)

    def _load_project_worker(self, path, set_status):
        app = self.app
        project_config, status_message = app.project_manager.load_project(path)

        if project_config:
            app.file_monitor.perform_initial_scan()

        app.load_thread_result = (project_config, status_message, path, set_status)

    def _check_load_project_thread(self):
        app = self.app
        # If load_thread is None, it means the operation was cancelled or finished
        if not app.load_thread:
            return

        if app.load_thread.is_alive():
            app.after(100, self._check_load_project_thread)
        else:
            if app.load_thread_result:
                self._on_project_load_complete(*app.load_thread_result)
                app.load_thread_result = None
            app.load_thread = None

    def cancel_loading(self):
        """Cancels the current project load operation and resets the UI."""
        app = self.app
        # Only act if a loading thread is actually active
        if app.load_thread and app.load_thread.is_alive():
            # Detach the thread by clearing the reference.
            # This causes the next _check_load_project_thread to abort.
            app.load_thread = None
            app.load_thread_result = None

            self._clear_project_ui()
            app.status_var.set("Loading cancelled")

    def _on_project_load_complete(self, project_config, status_message, path, set_status):
        app = self.app
        app.helpers.stop_loading_animation()
        if set_status:
            app.status_var.set(status_message)

        if project_config:
            app.active_dir.set(path)
            app.project_title_var.set(project_config.project_name)
            app.project_color = project_config.project_color
            app.project_font_color = project_config.project_font_color
            app.title_label.config(font=c.FONT_LARGE_BOLD, fg=c.TEXT_COLOR)
        else:
            app.active_dir.set("No project selected")
            app.project_title_var.set("(no active project)")
            app.project_color = c.COMPACT_MODE_BG_COLOR
            app.project_font_color = 'light'
            app.title_label.config(font=c.FONT_LARGE_BOLD, fg=c.TEXT_SUBTLE_COLOR)

        app.profile_actions.update_profile_selector_ui()
        app.file_monitor.start()
        app.button_manager.update_button_states()
```

--- End of file ---

--- File: `src/ui/app_window_parts/profile_actions.py` ---

```python
from tkinter import messagebox
from ..new_profile_dialog import NewProfileDialog

class ProfileActions:
    def __init__(self, app):
        self.app = app

    def update_profile_selector_ui(self):
        """Refreshes the profile navigator and buttons based on project state."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        profile_frame = app.profile_frame
        profile_frame.grid_rowconfigure(0, weight=1)

        # Clear existing layout
        for widget in profile_frame.winfo_children():
            widget.grid_forget()

        if not project_config:
            app.add_profile_button.set_state('disabled')
            return

        app.add_profile_button.set_state('normal')
        profile_names = project_config.get_profile_names()
        active_name = project_config.active_profile_name

        if len(profile_names) > 1:
            # Multi-profile layout
            profile_frame.grid_columnconfigure(0, weight=1)
            profile_frame.grid_columnconfigure(1, weight=0)
            profile_frame.grid_columnconfigure(2, weight=0)
            profile_frame.grid_columnconfigure(3, weight=0, minsize=25)
            profile_frame.grid_columnconfigure(4, weight=1)

            app.profile_navigator.grid(row=0, column=1, sticky='e')
            app.profile_navigator.set_profiles(profile_names, active_name)
            app.add_profile_button.grid(row=0, column=2, sticky='w', padx=(10, 0))

            if active_name != "Default":
                app.delete_profile_button.grid(row=0, column=3, sticky='w', padx=(5, 0))
        else:
            # Single-profile layout (only show + button)
            profile_frame.grid_columnconfigure(0, weight=0)
            profile_frame.grid_columnconfigure(1, weight=1)
            for i in range(2, 5):
                profile_frame.grid_columnconfigure(i, weight=0, minsize=0)
            app.add_profile_button.grid(row=0, column=0, sticky='w', padx=(10, 0))

    def on_profile_switched(self, new_profile_name):
        """Switches the active profile and refreshes independent file tracking."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        if new_profile_name != project_config.active_profile_name:
            project_config.active_profile_name = new_profile_name
            project_config.save()
            app.status_var.set(f"Switched to profile: {new_profile_name}")

            # Reset Independent File Tracking
            app.file_monitor.newly_detected_files = []
            app.file_monitor.perform_new_file_check(schedule_next=True)

            app.button_manager.update_button_states()

        self.update_profile_selector_ui()
        app.focus_set()

    def open_new_profile_dialog(self, event=None):
        """Opens dialog to create a new profile with independent file tracking."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        dialog = NewProfileDialog(
            parent=app,
            existing_profile_names=project_config.get_profile_names()
        )
        result = dialog.result

        if result:
            new_name = result['name']
            copy_files = result['copy_files']
            copy_instructions = result['copy_instructions']

            if project_config.create_new_profile(new_name, copy_files, copy_instructions):
                project_config.active_profile_name = new_name
                project_config.save()

                # Rescan for the new profile
                app.file_monitor.newly_detected_files = []
                app.file_monitor.perform_new_file_check(schedule_next=True)

                self.update_profile_selector_ui()
                app.button_manager.update_button_states()
                app.status_var.set(f"Created and switched to profile: {new_name}")
            else:
                app.status_var.set(f"Error: Profile '{new_name}' already exists.")

    def delete_current_profile(self, event=None):
        """Deletes the current profile and reverts to Default."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        profile_to_delete = project_config.active_profile_name
        if profile_to_delete == "Default":
            app.status_var.set("Cannot delete the Default profile.")
            return

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the profile '{profile_to_delete}'?\nThis cannot be undone.",
            parent=app
        ):
            if project_config.delete_profile(profile_to_delete):
                project_config.active_profile_name = "Default"
                project_config.save()

                # Re-sync tracking to the Default profile
                app.file_monitor.newly_detected_files = []
                app.file_monitor.perform_new_file_check(schedule_next=True)

                app.status_var.set(f"Profile '{profile_to_delete}' deleted.")
                self.update_profile_selector_ui()
                app.button_manager.update_button_states()
            else:
                app.status_var.set(f"Error: Could not delete profile '{profile_to_delete}'.")
```

--- End of file ---

--- File: `src/ui/app_window_parts/action_handlers.py` ---

```python
import os
import sys
import subprocess
import pyperclip
import time
from tkinter import messagebox, colorchooser

from ... import constants as c
from ..file_manager.file_manager_window import FileManagerWindow
from ..filetypes_manager import FiletypesManagerWindow
from ..settings.settings_window import SettingsWindow
from ..instructions_window import InstructionsWindow
from ..project_selector_dialog import ProjectSelectorDialog
from ..title_edit_dialog import TitleEditDialog
from ..paste_changes_dialog import PasteChangesDialog
from ..new_profile_dialog import NewProfileDialog
from ..project_starter.starter_dialog import ProjectStarterDialog
from ...core.clipboard import copy_project_to_clipboard
from ...core import change_applier
from ...core import prompts as p
from ...core.project_config import _calculate_font_color
from ...core.utils import get_file_hash, get_token_count_for_text

class ActionHandlers:
    def __init__(self, app):
        self.app = app

    def _is_valid_click(self, event):
        """Helper to ensure mouse release happened inside the widget."""
        if event is None: return True
        return 0 <= event.x <= event.widget.winfo_width() and 0 <= event.y <= event.widget.winfo_height()

    def copy_comment_cleanup_prompt(self, event=None):
        """Copies the standard comment cleanup instruction prompt to the clipboard."""
        if not self._is_valid_click(event): return

        pyperclip.copy(p.COMMENT_CLEANUP_PROMPT)
        self.app.helpers.show_compact_toast("Copied comment cleanup prompt")

    def open_project_starter(self, event=None):
        if not self._is_valid_click(event): return

        app = self.app
        if app.project_starter_window and app.project_starter_window.winfo_exists():
            app.project_starter_window.lift()
            app.project_starter_window.focus_force()
            return

        # Store the current project path before clearing the UI so it can be restored
        # if the user cancels the Project Starter.
        current_path = app.active_dir.get()
        if current_path and os.path.isdir(current_path):
            app._last_project_path = current_path
        else:
            app._last_project_path = None

        # Clear project UI to "No project selected" state before launching starter
        app.project_actions._clear_project_ui()

        app.project_starter_window = ProjectStarterDialog(app, app)

    def handle_title_click(self, event=None):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            self.open_project_selector()
            return

        if app.title_click_job:
            app.after_cancel(app.title_click_job)
            app.title_click_job = None

        app.title_click_job = app.after(250, self.open_project_selector)

    def edit_project_title(self, event=None):
        app = self.app
        if app.title_click_job:
            app.after_cancel(app.title_click_job)
            app.title_click_job = None

        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        current_name = project_config.project_name
        dialog = TitleEditDialog(
            parent=app,
            title="Edit Project Title",
            prompt="Enter the new title for the project:",
            initialvalue=current_name,
            max_length=c.PROJECT_TITLE_MAX_LENGTH
        )
        new_name = dialog.result

        if new_name is not None and new_name.strip() and new_name.strip() != current_name:
            new_name = new_name.strip()
            app.project_title_var.set(new_name)
            project_config.project_name = new_name
            project_config.save()
            app.status_var.set(f"Project title changed to '{new_name}'")

    def open_project_selector(self):
        app = self.app
        app.app_state._prune_recent_projects()
        ProjectSelectorDialog(
            parent=app,
            app_bg_color=app.app_bg_color,
            recent_projects=app.app_state.recent_projects,
            on_select_callback=app.ui_callbacks.on_directory_selected,
            on_remove_callback=app.ui_callbacks.on_recent_removed
        )

    def open_color_chooser(self, event=None):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config: return
        result = colorchooser.askcolor(title="Choose project color", initialcolor=app.project_color)
        if result and result[1]:
            new_hex_color = result[1]
            app.project_color = new_hex_color
            project_config.project_color = new_hex_color

            new_font_color = _calculate_font_color(new_hex_color)
            app.project_font_color = new_font_color
            project_config.project_font_color = new_font_color

            project_config.save()
            app.button_manager.update_button_states()

    def open_project_folder(self, event=None):
        if not self._is_valid_click(event): return

        app = self.app
        project_path = app.active_dir.get()

        if not (project_path and os.path.isdir(project_path)):
            app.status_var.set("No active project folder to open.")
            return

        is_ctrl_pressed = event and (event.state & 0x0004)
        is_alt_pressed = event and (event.state & 0x20000)

        # Priority 1: Alt -> Open Console
        if is_alt_pressed:
            try:
                if sys.platform == "win32":
                    # Environment Scrubbing
                    new_env = os.environ.copy()

                    # Strip core environment identification variables
                    venv_root = new_env.pop('VIRTUAL_ENV', None)
                    new_env.pop('PYTHONHOME', None)
                    new_env.pop('PYTHONPATH', None)
                    new_env.pop('PROMPT', None) # Remove the (.venv) prefix from shell prompt

                    # Identify directories to purge from PATH
                    purge_targets = []
                    if venv_root:
                        purge_targets.append(venv_root.lower())

                    bundle_dir = getattr(sys, '_MEIPASS', None)
                    if bundle_dir:
                        purge_targets.append(bundle_dir.lower())

                    # Also include the directory of the current executable/interpreter
                    exec_dir = os.path.dirname(sys.executable).lower()
                    purge_targets.append(exec_dir)

                    # Rebuild PATH correctly using os.pathsep (semicolon on Windows)
                    path_entries = new_env.get('PATH', '').split(os.pathsep)
                    cleaned_entries = []

                    for entry in path_entries:
                        if not entry: continue
                        entry_lower = entry.lower()

                        # Discard path if it starts with or resides within a purge target
                        should_purge = False
                        for target in purge_targets:
                            if entry_lower.startswith(target):
                                should_purge = True
                                break

                        if not should_purge:
                            cleaned_entries.append(entry)

                    new_env['PATH'] = os.pathsep.join(cleaned_entries)

                    # Launch clean shell
                    creationflags = subprocess.CREATE_NEW_CONSOLE
                    subprocess.Popen('cmd.exe', cwd=project_path, creationflags=creationflags, env=new_env)
                    app.helpers.show_compact_toast("Opened clean console in project folder")
                else:
                    app.status_var.set("Feature only available on Windows.")
            except Exception as e:
                app.show_error_dialog("Error", f"Could not open console: {e}")
            return

        # Priority 2: Ctrl -> Copy Path
        if is_ctrl_pressed:
            pyperclip.copy(project_path.replace('/', '\\'))
            app.helpers.show_compact_toast("Copied project path to clipboard")
            return

        # Priority 3: No modifiers -> Open in File Explorer
        try:
            if sys.platform == "win32":
                os.startfile(project_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", project_path])
            else:
                subprocess.Popen(["xdg-open", project_path])
        except Exception as e:
            app.show_error_dialog("Error", f"Could not open folder: {e}")

    def open_settings_window(self, event=None):
        if not self._is_valid_click(event): return
        app = self.app
        SettingsWindow(app, app.updater, on_close_callback=app.ui_callbacks.on_settings_closed)

    def open_instructions_window(self):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return
        wt_window = InstructionsWindow(app, project_config, app.status_var, on_close_callback=app.button_manager.update_button_states)
        app.wait_window(wt_window)

    def open_paste_changes_dialog(self, initial_content=None):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return
        PasteChangesDialog(app, project_config.base_dir, app.status_var, initial_content=initial_content)

    def on_paste_click(self, event):
        self.app.paste_changes_button._draw(self.app.paste_changes_button.click_color)

    def on_paste_release(self, event):
        app = self.app
        btn = app.paste_changes_button
        if 0 <= event.x <= btn.winfo_width() and 0 <= event.y <= btn.winfo_height():
            btn._draw(btn.hover_color)
            is_ctrl = (event.state & 0x0004)
            is_alt = (event.state & 0x20000)

            if is_alt:
                # Manual paste window (old default)
                self.open_paste_changes_dialog()
            elif is_ctrl:
                # Toggle feedback (opposite of setting)
                self.apply_changes_from_clipboard(force_toggle_feedback=True)
            else:
                # Default behavior: Apply changes (follows setting)
                self.apply_changes_from_clipboard(force_toggle_feedback=False)
        else:
            btn._draw(btn.base_color)

    def open_filetypes_manager(self, event=None):
        if not self._is_valid_click(event): return
        app = self.app
        FiletypesManagerWindow(app, on_close_callback=app.ui_callbacks.reload_active_extensions)

    def copy_merged_code(self, button=None):
        self._perform_copy(use_wrapper=False, button=button)

    def copy_wrapped_code(self, button=None):
        self._perform_copy(use_wrapper=True, button=button)

    def _perform_copy(self, use_wrapper: bool, button=None):
        app = self.app
        base_dir = app.active_dir.get()
        if not os.path.isdir(base_dir):
            app.show_error_dialog("Error", "Please select a valid project folder first")
            app.status_var.set("Error: Invalid project folder")
            return

        project_config = app.project_manager.get_current_project()
        if not project_config:
            app.status_var.set("Error: No active project.")
            return

        # Attempt to auto-detect button if none provided (e.g. from keyboard shortcut)
        if button is None:
            if app.view_manager.current_state == 'compact' and app.view_manager.compact_mode_window:
                button = app.view_manager.compact_mode_window.copy_button
            else:
                button = app.copy_wrapped_button if use_wrapper else app.copy_merged_button

        # Visual feedback: set button to loading
        if button:
            button.set_loading(True, "Merging")
            app.update() # Force UI refresh to show loading state

        try:
            status_message = copy_project_to_clipboard(
                parent=app,
                base_dir=base_dir,
                project_config=project_config,
                use_wrapper=use_wrapper,
                copy_merged_prompt=app.app_state.copy_merged_prompt,
                scan_secrets_enabled=app.app_state.scan_for_secrets
            )
            app.status_var.set(status_message)
        finally:
            if button:
                button.set_loading(False)

    def manage_files(self):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first")
            return

        files_to_highlight = app.file_monitor.get_newly_detected_files_and_reset()

        fm_window = FileManagerWindow(
            app,
            project_config,
            app.status_var,
            app.file_extensions,
            app.app_state.default_editor,
            app_state=app.app_state,
            newly_detected_files=files_to_highlight
        )
        app.wait_window(fm_window)
        app.button_manager.update_button_states()

    def on_new_files_click(self, event):
        if not self._is_valid_click(event): return
        is_ctrl = (event.state & 0x0004)
        if is_ctrl:
            self.add_new_files_to_merge_order()
        else:
            self.manage_files()

    def add_new_files_to_merge_order(self):
        """Adds current unknown files to the merge order for the active profile."""
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            return

        # Use the monitor's list which reflects the active profile's unknowns
        new_files = list(app.file_monitor.newly_detected_files)

        if not new_files:
            app.status_var.set("No new files to add.")
            return

        current_selection_paths = {f['path'] for f in project_config.selected_files}
        files_to_add = [path for path in new_files if path not in current_selection_paths]

        if files_to_add:
            for path in files_to_add:
                new_entry = self._calculate_stats_for_file(path)
                if new_entry:
                    project_config.selected_files.append(new_entry)

            project_config.total_tokens = sum(f.get('tokens', 0) for f in project_config.selected_files)
            app.status_var.set(f"Added {len(files_to_add)} new file(s) to merge list.")
        else:
            app.status_var.set("New files already acknowledged.")

        # This method clears the active profile's unknown list and updates the UI
        app.file_monitor.get_newly_detected_files_and_reset()
        app.button_manager.update_button_states()

    def _calculate_stats_for_file(self, path):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config: return None
        full_path = os.path.join(project_config.base_dir, path)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            mtime = os.path.getmtime(full_path)
            file_hash = f"{os.path.getsize(full_path)}-{mtime}" # Simplified hash for speed

            token_count_enabled = app.app_state.config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT)
            if token_count_enabled:
                tokens = get_token_count_for_text(content)
                lines = content.count('\n') + 1
            else:
                tokens, lines = 0, 0

            if file_hash is not None:
                return {'path': path, 'mtime': mtime, 'hash': file_hash, 'tokens': tokens, 'lines': lines}
        except OSError:
            app.show_error_dialog("File Access Error", f"Could not access file to add it to the merge list:\n{path}")
        return None

    def ensure_file_is_merged(self, rel_path):
        """Ensures a file is present in the Merge List and marks it as 'seen' globally."""
        project_config = self.app.project_manager.get_current_project()
        if not project_config:
            return

        # 1. Add to Merge List if not already there
        if not any(f['path'] == rel_path for f in project_config.selected_files):
            new_entry = self._calculate_stats_for_file(rel_path)
            if new_entry:
                project_config.selected_files.append(new_entry)
                # Recalculate total tokens
                project_config.total_tokens = sum(f.get('tokens', 0) for f in project_config.selected_files)

        # 2. Global State Cleanup: mark as known to prevent "New File" alerts
        project_config.known_files = sorted(list(set(project_config.known_files) | {rel_path}))

        # 3. Profile State Cleanup: remove from active unknown tracker
        project_config.unknown_files = [f for f in project_config.unknown_files if f != rel_path]

        project_config.save()
        self.app.button_manager.update_button_states()

    def apply_changes_from_clipboard(self, force_toggle_feedback=False):
        app = self.app
        project_config = app.project_manager.get_current_project()
        if not project_config:
            messagebox.showerror("Error", "Please select a valid project folder first", parent=app)
            return

        markdown_text = pyperclip.paste()
        if not markdown_text.strip():
            app.helpers.show_compact_toast("Clipboard is empty.")
            return

        plan = change_applier.parse_and_plan_changes(project_config.base_dir, markdown_text)
        self._handle_parsed_plan(plan, project_config.base_dir, force_toggle_feedback=force_toggle_feedback)

    def _handle_parsed_plan(self, plan, base_dir, dialog_to_close=None, force_toggle_feedback=False):
        status = plan.get('status')
        message = plan.get('message')
        hint = plan.get('hint')

        if status == 'ERROR':
            self.app.show_error_dialog("Parsing Error", message, hint=hint)
            return

        self.app.last_ai_response = plan
        self.app.button_manager.update_button_states()

        def do_execute(filtered_updates=None, filtered_creations=None, filtered_deletions=None, is_changes_tab_active=False):
            """Writes files to disk. Returns True on success, False if cancelled or error."""

            # Use provided lists (from Review window) or default to the full parsed plan
            updates = filtered_updates if filtered_updates is not None else plan.get('updates', {})
            creations = filtered_creations if filtered_creations is not None else plan.get('creations', {})
            deletions = filtered_deletions if filtered_deletions is not None else plan.get('deletions_proposed', [])

            # If we are not in a review window and there are creations OR deletions, warn the user.
            if not dialog_to_close:
                warning_parts = []

                # Creations: Warning is suppressed if count is below setting limit OR user is looking at Changes tab.
                creation_threshold = self.app.app_state.config.get('new_file_alert_threshold', 5)
                if creations and not is_changes_tab_active:
                    if len(creations) > creation_threshold:
                        warning_parts.append(f"CREATE {len(creations)} file(s):\n- " + "\n- ".join(creations.keys()))

                # Deletions: ALWAYS warn for safety.
                if deletions and not is_changes_tab_active:
                    warning_parts.append(f"DELETE {len(deletions)} file(s):\n- " + "\n- ".join(deletions))

                if warning_parts:
                    confirm_message = "This operation will perform the following actions:\n\n" + "\n\n".join(warning_parts) + "\n\nDo you want to proceed?"

                    dialog_parent = self.app
                    if self.app.view_manager.current_state == 'compact' and self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
                        dialog_parent = self.app.view_manager.compact_mode_window

                    if not messagebox.askyesno("Confirm File Actions", confirm_message, parent=dialog_parent):
                        self.app.helpers.show_compact_toast("Operation cancelled.")
                        return False

            success, final_message = change_applier.execute_plan(base_dir, updates, creations, deletions)

            if success:
                self.app.helpers.show_compact_toast(final_message)

                # Automatic Addition of written files (creations AND updates) to the Merge List
                processed_paths = set(updates.keys()) | set(creations.keys())
                for rel_path in processed_paths:
                    self.ensure_file_is_merged(rel_path)

                if creations or deletions:
                    self.app.file_monitor.perform_new_file_check()

                # Refresh main UI buttons
                self.app.button_manager.update_button_states()

                return True
            else:
                self.app.show_error_dialog("File Write Error", final_message)
                return False

        def do_refuse():
            self.app.helpers.show_compact_toast("Update refused.")
            if dialog_to_close:
                dialog_to_close.destroy()

        show_feedback_setting = self.app.app_state.config.get('show_feedback_on_paste', True)
        should_show = (not show_feedback_setting) if force_toggle_feedback else show_feedback_setting
        is_unformatted_only = (status == 'UNFORMATTED')

        if should_show:
            if dialog_to_close:
                dialog_to_close.destroy()
                dialog_to_close = None

            on_apply_cb = do_execute if not is_unformatted_only else None
            self.show_response_review(plan=plan, on_apply=on_apply_cb, on_refuse=do_refuse)
        elif not is_unformatted_only:
            do_execute()
        else:
            self.app.helpers.show_compact_toast("Error: LLM response followed no usable format.")

    def show_response_review(self, plan=None, on_apply=None, on_refuse=None, force_verification=False):
        """
        Opens the AI Response Review window.
        Uses either the provided plan (from a fresh paste) or the cached last response.
        Overwrites any currently open review window to allow sequential pasting.
        """
        existing = getattr(self.app, 'active_feedback_dialog', None)
        if existing and existing.winfo_exists():
            if existing.on_apply_executor is not None:
                dialog_parent = self.app
                if self.app.view_manager.current_state == 'compact' and self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
                    dialog_parent = self.app.view_manager.compact_mode_window

                msg = "An AI response review is already open with changes that haven't been applied yet.\n\nAre you sure you want to overwrite it?"
                if not messagebox.askyesno("Confirm Overwrite", msg, parent=dialog_parent):
                    return

            existing.destroy()

        if plan is None:
            plan = getattr(self.app, 'last_ai_response', None)
            if plan and on_apply is None:
                project = self.app.project_manager.get_current_project()
                if project:
                    def do_execute_cached(u=None, c_list=None, d=None, is_changes_tab_active=False):
                        # Re-use the existing do_execute logic
                        updates = u if u is not None else plan.get('updates', {})
                        creations = c_list if c_list is not None else plan.get('creations', {})
                        deletions = d if d is not None else plan.get('deletions_proposed', [])

                        # Pass the tab state to ensure warnings are handled correctly for cached resumes
                        success, final_message = change_applier.execute_plan(project.base_dir, updates, creations, deletions)
                        if success:
                            self.app.helpers.show_compact_toast(final_message)

                            # Auto-merge logic for cached apply
                            all_paths = set(updates.keys()) | set(creations.keys())
                            for rel_path in all_paths:
                                self.ensure_file_is_merged(rel_path)

                            self.app.button_manager.update_button_states()
                            return True
                        else:
                            self.app.show_error_dialog("File Write Error", final_message)
                            return False

                    on_apply = do_execute_cached

        if plan is None:
            self.app.helpers.show_compact_toast("No AI response review available yet.")
            return

        from ..feedback.feedback_dialog import FeedbackDialog

        dialog_parent = self.app
        if self.app.view_manager.current_state == 'compact' and self.app.view_manager.compact_mode_window and self.app.view_manager.compact_mode_window.winfo_exists():
            dialog_parent = self.app.view_manager.compact_mode_window

        self.app.active_feedback_dialog = FeedbackDialog(dialog_parent, plan, on_apply=on_apply, on_refuse=on_refuse, force_verification=force_verification)
```

--- End of file ---

--- File: `src/ui/app_window_parts/event_handlers.py` ---

```python
import sys
import logging

log = logging.getLogger("CodeMerger")

class EventHandlers:
    def __init__(self, app):
        self.app = app

    def on_app_close(self):
        app = self.app
        log.info("Application closing.")
        app.file_monitor.stop()
        if app.view_manager.compact_mode_window and app.view_manager.compact_mode_window.winfo_exists():
            app.view_manager.compact_mode_window.destroy()
        app.destroy()

    def on_window_configure(self, event):
        app = self.app
        # Only capture geometry and monitor changes when in NORMAL state.
        # This prevents movement/resizing events triggered by the state-machine
        # animations from polluting the saved restoration target.
        if app.view_manager.current_state == 'normal':
            if app.state() != 'iconic':
                app.view_manager.main_window_geom = (
                    app.winfo_x(), app.winfo_y(),
                    app.winfo_width(), app.winfo_height()
                )
                self.check_for_monitor_change()

    def check_for_monitor_change(self):
        """
        Detects if the window has crossed onto a different physical screen.
        If a monitor change is detected, saved geometries (including compact position)
        are invalidated to ensure the UI remains fully visible and contextually placed.
        """
        app = self.app

        # Do not perform check if the window is minimized
        if app.state() == 'iconic':
            return

        if sys.platform != "win32":
            return

        try:
            import ctypes
            user32 = ctypes.windll.user32
            MONITOR_DEFAULTTONEAREST = 2

            hwnd = app.winfo_id()
            new_monitor_handle = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

            # Initial boot synchronization
            if app.current_monitor_handle is None:
                app.current_monitor_handle = new_monitor_handle
                # Sync ViewManager handle so first minimize doesn't trigger monitor_changed
                app.view_manager.compact_last_monitor_handle = new_monitor_handle
                return

            if new_monitor_handle != app.current_monitor_handle:
                log.info(f"Monitor switch detected. Handle: {app.current_monitor_handle} -> {new_monitor_handle}")
                app.current_monitor_handle = new_monitor_handle

                # Clear standard window geometries (File Manager, etc)
                app.window_geometries.clear()

                # Strictly invalidate the compact mode coordinates when crossing screens.
                # This enforces recalculation on the new screen's workspace.
                app.view_manager.invalidate_compact_mode_position()

        except Exception as e:
            log.warning(f"Failed to check for monitor change: {e}")

    def update_responsive_layout(self, event=None):
        app = self.app
        THRESHOLD = 600
        width = app.winfo_width()

        if width > THRESHOLD:
            app.main_content_frame.grid_configure(sticky='', padx=0)
        else:
            app.main_content_frame.grid_configure(sticky='w', padx=(20, 0))
```

--- End of file ---

--- File: `src/ui/ui_builder.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, font as tkFont
from .. import constants as c
from .widgets.rounded_button import RoundedButton
from .widgets.profile_navigator import ProfileNavigator
from .tooltip import ToolTip
from .assets import assets

def setup_ui(app):
    """Creates and places all the UI widgets for the main application window"""
    # Window Grid Configuration
    app.columnconfigure(0, weight=1)
    app.rowconfigure(2, weight=1) # Central content row expands vertically
    app.rowconfigure(3, weight=0) # Status bar row
    app.rowconfigure(4, weight=0) # Info panel row

    # Top Bar (Row 0)
    top_bar = Frame(app, bg=c.TOP_BAR_BG, padx=20, pady=15)
    top_bar.grid(row=0, column=0, sticky='ew')
    top_bar.columnconfigure(1, weight=1) # Make the center area expand

    # Left-aligned items
    left_frame = Frame(top_bar, bg=c.TOP_BAR_BG)
    left_frame.grid(row=0, column=0, sticky='w')

    app.color_swatch = Label(left_frame, cursor="hand2", bg=c.TOP_BAR_BG, bd=0, highlightthickness=0)
    app.color_swatch.bind("<Button-1>", app.action_handlers.open_color_chooser)
    ToolTip(app.color_swatch, "Click to change the project color", delay=500)

    app.title_container = Frame(left_frame, bg=c.TOP_BAR_BG, cursor="hand2")
    app.title_container.pack(side='left')

    # Use grid within the title container to manage a minimum height, preventing layout shifts
    app.title_container.grid_rowconfigure(0, weight=1)
    app.title_container.grid_columnconfigure(0, weight=1)

    app.title_label = Label(app.title_container, textvariable=app.project_title_var, font=c.FONT_LARGE_BOLD, bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, anchor='w', cursor="hand2")
    app.title_label.grid(row=0, column=0, sticky='w')

    # Store ToolTip reference for cross-widget suppression/restoration
    app.title_tooltip = ToolTip(app.title_container, "Click to select project, double-click to edit title", delay=500)

    # Pen Icon (Edit) Logic
    app.edit_title_icon = Label(app.title_container, image=assets.edit_icon_tk, bg=c.TOP_BAR_BG, cursor="hand2")
    app.edit_title_icon.grid(row=0, column=1, sticky='w', padx=(5, 0))
    app.edit_title_icon.grid_remove() # Start hidden
    app.edit_title_icon.bind("<ButtonRelease-1>", app.action_handlers.edit_project_title)
    ToolTip(app.edit_title_icon, "Edit project title", delay=500)

    # Tooltip Handoff: Hide parent tip when on icon, restore when leaving icon
    app.edit_title_icon.bind("<Enter>", lambda e: app.title_tooltip.hide_tooltip(), add="+")
    app.edit_title_icon.bind("<Leave>", lambda e: app.title_tooltip.schedule_show(), add="+")

    def on_title_hover(event):
        # Only show the icon if a project is actually selected
        active_path = app.active_dir.get()
        if active_path and active_path != "No project selected" and active_path != "Loading...":
            app.edit_title_icon.grid()

    def on_title_leave(event):
        app.edit_title_icon.grid_remove()

    # Apply hover bindings to the entire container
    app.title_container.bind("<Enter>", on_title_hover, add="+")
    app.title_container.bind("<Leave>", on_title_leave, add="+")

    # Set a minimum height on the container's grid row based on the label's actual required height
    app.update_idletasks()
    required_height = app.title_label.winfo_reqheight()
    app.title_container.grid_rowconfigure(0, minsize=required_height)

    # Title interaction uses Single and Double click, so we keep Button-1 to avoid conflicts
    app.title_label.bind("<Button-1>", app.action_handlers.handle_title_click)
    app.title_label.bind("<Double-Button-1>", app.action_handlers.edit_project_title)
    app.title_container.bind("<Button-1>", app.action_handlers.handle_title_click)
    app.title_container.bind("<Double-Button-1>", app.action_handlers.edit_project_title)

    # Right-aligned items
    right_frame = Frame(top_bar, bg=c.TOP_BAR_BG)
    right_frame.grid(row=0, column=2, sticky='e')
    right_frame.grid_rowconfigure(0, weight=1) # Center items vertically in the row

    # New files warning icon
    app.new_files_label = Label(right_frame, image=assets.new_files_icon, bg=c.TOP_BAR_BG, cursor="hand2")
    app.new_files_label.bind("<ButtonRelease-1>", app.action_handlers.on_new_files_click)
    app.new_files_tooltip = ToolTip(app.new_files_label, text="")

    # Open folder icon
    app.folder_icon_label = Label(right_frame, image=assets.folder_icon, bg=c.TOP_BAR_BG, cursor="hand2")
    app.folder_icon_label.bind("<ButtonRelease-1>", app.action_handlers.open_project_folder)
    app.folder_icon_label.bind("<Enter>", lambda e: app.folder_icon_label.config(image=assets.folder_active_icon), add='+')
    app.folder_icon_label.bind("<Leave>", lambda e: app.folder_icon_label.config(image=assets.folder_icon), add='+')
    ToolTip(app.folder_icon_label, "Open project folder\nCtrl+Click: Copy path\nAlt+Click: Open console", delay=500)

    # Top-Level Buttons (Row 1)
    app.top_buttons_container = Frame(app, bg=c.DARK_BG, padx=20, height=30)
    app.top_buttons_container.grid(row=1, column=0, sticky='ew', pady=(15, 0))
    app.top_buttons_container.grid_propagate(False)
    app.top_buttons_container.columnconfigure(1, weight=1) # Make the central column expandable
    app.top_buttons_container.rowconfigure(0, weight=1) # Center all content vertically

    # Column 0: Edit Merge List Button
    app.manage_files_button = RoundedButton(app.top_buttons_container, text="Edit Merge List", font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.action_handlers.manage_files, cursor='hand2')
    app.manage_files_button.grid(row=0, column=0, sticky='w')
    app.manage_files_tooltip = ToolTip(app.manage_files_button, text="Edit project merge list")

    # Column 1: Middle Container (Profiles)
    app.middle_container = Frame(app.top_buttons_container, bg=c.DARK_BG)
    app.middle_container.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
    app.middle_container.columnconfigure(0, weight=0) # Profile Frame

    # Profile Management Frame
    app.profile_frame = Frame(app.middle_container, bg=c.DARK_BG)
    app.profile_frame.grid(row=0, column=0, sticky='w')

    # Profile Widgets
    app.profile_navigator = ProfileNavigator(app.profile_frame, on_change_callback=app.profile_actions.on_profile_switched)
    app.add_profile_button = RoundedButton(app.profile_frame, text="+", font=(c.FONT_BOLD[0], c.FONT_BOLD[1]), bg=c.BTN_GRAY_BG, fg=c.TEXT_COLOR, command=app.profile_actions.open_new_profile_dialog, cursor='hand2', width=20, height=28, hollow=True)
    ToolTip(app.add_profile_button, "Create an additional project profile", delay=500)
    app.delete_profile_button = RoundedButton(app.profile_frame, text="-", font=(c.FONT_BOLD[0], c.FONT_BOLD[1]), bg=c.BTN_GRAY_BG, fg=c.TEXT_COLOR, command=app.profile_actions.delete_current_profile, cursor='hand2', width=20, height=28, hollow=True)
    ToolTip(app.delete_profile_button, "Delete the current profile", delay=500)

    # Column 2: Right Controls (Project Starter + Select Project)
    right_controls_frame = Frame(app.top_buttons_container, bg=c.DARK_BG)
    right_controls_frame.grid(row=0, column=2, sticky='e')

    app.project_starter_button = Label(right_controls_frame, image=assets.project_starter_icon, bg=c.DARK_BG, cursor="hand2")
    app.project_starter_button.pack(side='left', padx=(0, 10))
    app.project_starter_button.bind("<Enter>", lambda e: app.project_starter_button.config(image=assets.project_starter_active_icon))
    app.project_starter_button.bind("<Leave>", lambda e: app.project_starter_button.config(image=assets.project_starter_icon))
    app.project_starter_button.bind("<ButtonRelease-1>", app.action_handlers.open_project_starter)
    ToolTip(app.project_starter_button, "Project Starter", delay=500)

    app.select_project_button = RoundedButton(right_controls_frame, text="Select Project", font=c.FONT_BUTTON, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=app.action_handlers.open_project_selector, cursor='hand2')
    app.select_project_button.pack(side='left')

    # Center Content Area (Row 2)
    center_frame = Frame(app, bg=c.DARK_BG)
    center_frame.grid(row=2, column=0, sticky='nsew')
    center_frame.grid_rowconfigure(0, weight=1)
    center_frame.grid_columnconfigure(0, weight=1)
    app.center_frame = center_frame

    # Icon buttons
    app.bottom_buttons_container = Frame(center_frame, bg=c.DARK_BG)
    app.bottom_buttons_container.grid(row=0, column=0, sticky='se', padx=20, pady=(0, 18))

    app.settings_button = Label(app.bottom_buttons_container, image=assets.settings_icon, bg=c.DARK_BG, cursor='hand2')
    app.settings_button.pack(side='top')
    ToolTip(app.settings_button, "Settings", delay=500)

    app.filetypes_button = Label(app.bottom_buttons_container, image=assets.filetypes_icon, bg=c.DARK_BG, cursor='hand2')
    app.filetypes_button.pack(side='top', pady=(10, 0))
    ToolTip(app.filetypes_button, "Manage Filetypes", delay=500)

    # This frame holds the actions box. Its alignment is controlled by the responsive layout function.
    app.main_content_frame = Frame(center_frame, bg=c.DARK_BG)
    app.main_content_frame.grid(row=0, column=0, sticky='') # Starts centered
    app.main_content_frame.grid_rowconfigure(0, weight=1)
    app.main_content_frame.grid_columnconfigure(0, weight=1)

    app.wrapper_box = Frame(app.main_content_frame, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
    app.wrapper_box.grid(row=0, column=0, sticky='s') # Aligns to the bottom of its cell

    app.wrapper_box_title = Label(app.wrapper_box, text="Actions", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL, pady=2)

    app.no_project_label = Label(app.wrapper_box, text="Select a project to get started", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)

    # Cleanup Comments Label (Replaces Button)
    app.cleanup_comments_button = Label(
        app.wrapper_box,
        text="//",
        font=(c.FONT_FAMILY_PRIMARY, 10, 'bold'),
        bg=c.DARK_BG,
        fg="#555555", # Dark gray, similar to border color
        cursor='hand2',
        padx=5, pady=2
    )
    app.cleanup_comments_button.bind("<ButtonRelease-1>", app.action_handlers.copy_comment_cleanup_prompt)
    app.cleanup_comments_button.bind("<Enter>", lambda e: app.cleanup_comments_button.config(fg=c.TEXT_COLOR))
    app.cleanup_comments_button.bind("<Leave>", lambda e: app.cleanup_comments_button.config(fg="#555555"))
    ToolTip(app.cleanup_comments_button, "Copy prompt to clean up comments and remove tags", delay=500)

    app.button_grid_frame = Frame(app.wrapper_box, bg=c.DARK_BG)
    app.button_grid_frame.columnconfigure(0, weight=1, uniform="group1")
    app.button_grid_frame.columnconfigure(1, weight=1, uniform="group1")

    copy_button_height = 60
    app.copy_wrapped_button = RoundedButton(app.button_grid_frame, height=copy_button_height, text="Copy with Instructions", font=c.FONT_BUTTON, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, command=app.action_handlers.copy_wrapped_code, cursor='hand2')
    app.wrapper_text_button = RoundedButton(app.button_grid_frame, text="Define Instructions", height=30, font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.action_handlers.open_instructions_window, cursor='hand2')
    app.copy_merged_button = RoundedButton(app.button_grid_frame, height=copy_button_height, text="Copy Code Only", font=c.FONT_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, command=app.action_handlers.copy_merged_code, cursor='hand2')

    # Tooltip setup for Copy buttons with instance references for dynamic updates
    app.copy_wrapped_tooltip = ToolTip(app.copy_wrapped_button, "Copy Prompt: includes code wrapped with custom intro/outro instructions", delay=500)
    app.copy_merged_tooltip = ToolTip(app.copy_merged_button, "Copy Prompt: merges code and prepends the default context prompt", delay=500)

    # Paste Container Layout
    app.paste_container = Frame(app.button_grid_frame, bg=c.DARK_BG)
    app.paste_changes_button = RoundedButton(app.paste_container, text="Paste Changes", height=30, font=c.FONT_BUTTON, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, command=None, cursor='hand2')
    app.paste_changes_button.pack(side='left', fill='x', expand=True, padx=(0, 0))

    # AI Response Review Button
    # Narrow orange bar with subtle 4px padding from the paste button. Hidden by default.
    app.review_button = RoundedButton(
        app.paste_container, text="", bg=c.ATTENTION, fg=c.TEXT_COLOR,
        width=12, height=30, radius=6,
        command=lambda: app.action_handlers.show_response_review(force_verification=True),
        cursor='hand2'
    )
    app.review_button.pack_forget()

    app.paste_changes_button.bind("<Button-1>", app.action_handlers.on_paste_click)
    app.paste_changes_button.unbind("<ButtonRelease-1>")
    app.paste_changes_button.bind("<ButtonRelease-1>", app.action_handlers.on_paste_release)

    paste_tooltip = "Open paste window\n(Ctrl+Click: instant paste from clipboard, Alt+Click: toggle review)"
    app.paste_changes_tooltip = ToolTip(app.paste_changes_button, paste_tooltip, delay=500)

    ToolTip(app.review_button, "Read latest AI response review", delay=500)

    app.settings_button.bind("<Enter>", lambda e: app.settings_button.config(image=assets.settings_icon_active), add='+')
    app.settings_button.bind("<Leave>", lambda e: app.settings_button.config(image=assets.settings_icon), add='+')
    app.settings_button.bind("<ButtonRelease-1>", app.action_handlers.open_settings_window)

    app.filetypes_button.bind("<Enter>", lambda e: app.filetypes_button.config(image=assets.filetypes_icon_active), add='+')
    app.filetypes_button.bind("<Leave>", lambda e: app.filetypes_button.config(image=assets.filetypes_icon), add='+')
    app.filetypes_button.bind("<ButtonRelease-1>", app.action_handlers.open_filetypes_manager)

    # Status Bar Area (Row 3)
    app.status_container = Frame(app, bg=c.STATUS_BG)
    app.status_container.grid(row=3, column=0, sticky='ew')

    # Info Toggle: Managed by InfoManager via .place
    app.info_toggle_btn = Label(app, image=assets.info_icon, bg=c.STATUS_BG, cursor="hand2")

    app.status_bar = Label(
        app.status_container,
        textvariable=app.status_var,
        relief='flat',
        anchor='w',
        bg=c.STATUS_BG,
        fg=c.STATUS_FG,
        font=c.FONT_STATUS_BAR,
        pady=4
    )
    # Gap (22px) provided to separate text from the icon in the corner
    app.status_bar.pack(side='left', fill='x', expand=True, padx=(22, 20))
```

--- End of file ---

--- File: `src/ui/app_window.py` ---

```python
import os
import json
import shutil
import tempfile
import logging
import re
import time
from tkinter import Tk, StringVar, Label

from ..app_state import AppState
from .view_manager import ViewManager
from ..core.paths import ICON_PATH, UPDATE_CLEANUP_FILE_PATH
from .. import constants as c
from ..core.updater import Updater
from .ui_builder import setup_ui
from .file_monitor import FileMonitor
from ..core.project_manager import ProjectManager
from .assets import assets
from .app_window_parts.button_state_manager import ButtonStateManager
from .app_window_parts.status_bar_manager import StatusBarManager
from .new_filetypes_dialog import NewFiletypesDialog
from .app_window_parts.action_handlers import ActionHandlers
from .app_window_parts.event_handlers import EventHandlers
from .app_window_parts.project_actions import ProjectActions
from .app_window_parts.profile_actions import ProfileActions
from .app_window_parts.ui_callbacks import UICallbacks
from .app_window_parts.helpers import AppHelpers
from .info_manager import attach_info_mode

log = logging.getLogger("CodeMerger")

class App(Tk):
    def __init__(self, file_extensions, app_version="", initial_project_path=None, newly_added_filetypes=None, is_second_instance=False):
        super().__init__()
        self.withdraw()
        self._run_update_cleanup()
        assets.load_tk_images()
        self.assets = assets

        self.file_extensions = file_extensions
        self.app_version = app_version
        self.app_bg_color = c.DARK_BG
        self.project_color = c.COMPACT_MODE_BG_COLOR
        self.project_font_color = 'light'
        self.window_geometries = {}
        self.title_click_job = None
        self.current_monitor_handle = None
        self.masked_logo_tk = None
        self.load_thread = None
        self.load_thread_result = None
        self.loading_animation_job = None
        self.project_starter_window = None
        self.last_ai_response = None

        self.last_move_time = 0.0
        self._lazy_timer = None
        self._is_lazy_hiding = False
        self._last_size = (0, 0)

        # Order of initialization is critical for established logic components
        self.app_state = AppState()
        self.view_manager = ViewManager(self)
        self.updater = Updater(self, self.app_state, self.app_version)
        self.project_manager = ProjectManager(lambda: self.file_extensions)
        self.file_monitor = FileMonitor(self)
        self.button_manager = ButtonStateManager(self)

        self.action_handlers = ActionHandlers(self)
        self.event_handlers = EventHandlers(self)
        self.project_actions = ProjectActions(self)
        self.profile_actions = ProfileActions(self)
        self.ui_callbacks = UICallbacks(self)
        self.helpers = AppHelpers(self)

        self.title(f"CodeMerger [ {app_version} ]")
        self.iconbitmap(ICON_PATH)

        initial_geom = c.DEFAULT_WINDOW_GEOMETRY
        if self.app_state.info_mode_active:
            match = re.match(r"(\d+)x(\d+)", initial_geom)
            if match:
                w, h = map(int, match.groups())
                initial_geom = f"{w}x{h + c.INFO_PANEL_HEIGHT}"

        self.geometry(initial_geom)
        self.minsize(c.MIN_WINDOW_WIDTH, c.MIN_WINDOW_HEIGHT)
        self.configure(bg=self.app_bg_color)

        self.active_dir = StringVar()
        self.project_title_var = StringVar()
        self.status_var = StringVar(value="")

        setup_ui(self)
        self.status_bar_manager = StatusBarManager(self, self.status_bar, self.status_var)
        self.info_mgr = attach_info_mode(self, self.app_state, manager_type='grid', grid_row=4, toggle_btn=self.info_toggle_btn)
        self._register_hover_help()

        self.active_dir.trace_add('write', self.button_manager.update_button_states)
        self.bind("<Configure>", self.event_handlers.update_responsive_layout, add='+')
        self.after(50, self.event_handlers.update_responsive_layout)
        self.protocol("WM_DELETE_WINDOW", self.event_handlers.on_app_close)
        self.bind("<Map>", self.view_manager.on_main_window_restored)
        self.bind("<Unmap>", self.view_manager.on_main_window_minimized)
        self.bind("<Configure>", self._on_configure)
        self.bind("<FocusIn>", self._on_focus_in)

        # Shortcuts
        self.bind("<Control-c>", lambda event: self.action_handlers.copy_wrapped_code())
        self.bind("<Control-Shift-C>", lambda event: self.action_handlers.copy_merged_code())
        self.bind("<Control-v>", lambda event: self.action_handlers.open_paste_changes_dialog())
        self.bind("<Control-Shift-V>", lambda event: self.action_handlers.apply_changes_from_clipboard())
        self.bind("<Escape>", lambda event: self.project_actions.cancel_loading())

        force_selector = is_second_instance and initial_project_path is None

        if initial_project_path and os.path.isdir(initial_project_path):
            self.app_state.update_active_dir(initial_project_path)
            self.project_actions.set_active_dir_display(initial_project_path)
        elif force_selector:
            self.project_actions.set_active_dir_display(None, set_status=False)
        else:
            self.project_actions.set_active_dir_display(self.app_state.active_directory)

        self.after(1500, self.updater.check_for_updates)
        if newly_added_filetypes:
            self.after(500, lambda: NewFiletypesDialog(self, newly_added_filetypes))
        if force_selector:
            self.after(100, self.action_handlers.open_project_selector)

        self.after(100, self.event_handlers.check_for_monitor_change)

        self.deiconify()
        self.lift()
        self.focus_force()

    def _register_hover_help(self):
        """Attaches help panel triggers to main window widgets"""
        mgr = self.info_mgr
        mgr.register(self.select_project_button, "select_project")

        mgr.register(self.title_container, "project_name")
        mgr.register(self.title_label, "project_name")

        mgr.register(self.color_swatch, "color_swatch")
        mgr.register(self.folder_icon_label, "folder_icon")
        mgr.register(self.manage_files_button, "manage_files")
        mgr.register(self.wrapper_text_button, "instructions")
        mgr.register(self.copy_merged_button, "copy_code")
        mgr.register(self.copy_wrapped_button, "copy_with_instructions")
        mgr.register(self.paste_changes_button, "paste_changes")
        mgr.register(self.review_button, "response_review")
        mgr.register(self.cleanup_comments_button, "cleanup")
        mgr.register(self.settings_button, "settings")
        mgr.register(self.filetypes_button, "filetypes")
        mgr.register(self.project_starter_button, "starter")

        mgr.register(self.profile_navigator, "profile_nav")
        mgr.register(self.add_profile_button, "profile_add")
        mgr.register(self.delete_profile_button, "profile_delete")

        mgr.register(self.info_toggle_btn, "info_toggle")

    def _on_configure(self, event):
        """
        Implements 'Lazy Layout' resizing to prevent lag during drag operations
        Tracking movement time assists with Compact Mode positioning
        """
        if event.widget != self:
            return

        new_size = (event.width, event.height)
        if self._last_size == new_size:
            # Captures manual moves when in normal state to avoid polluting restoration targets
            if self.view_manager.current_state == self.view_manager.STATE_NORMAL:
                self.last_move_time = time.time()

            self.event_handlers.on_window_configure(event)
            return

        self._last_size = new_size

        if self.view_manager.current_state != 'normal':
            self.event_handlers.on_window_configure(event)
            return

        # Hide heavy UI components immediately to stop layout thrashing
        if not self._is_lazy_hiding:
            self._start_lazy_layout()

        if self._lazy_timer:
            self.after_cancel(self._lazy_timer)

        self._lazy_timer = self.after(c.LAZY_LAYOUT_DELAY_MS, self._end_lazy_layout)

        self.event_handlers.on_window_configure(event)

    def _start_lazy_layout(self):
        self._is_lazy_hiding = True
        self.top_buttons_container.grid_remove()
        self.center_frame.grid_remove()
        self.status_container.grid_remove()

    def _end_lazy_layout(self):
        self.top_buttons_container.grid()
        self.center_frame.grid()
        self.status_container.grid()
        self._is_lazy_hiding = False
        self._lazy_timer = None
        self.update_idletasks()

    def _on_focus_in(self, event):
        # Triggers immediate file check on application focus to identify external configuration changes
        if event.widget == self and self.project_manager.get_current_project():
            self.file_monitor.perform_new_file_check(schedule_next=False)

    def _run_update_cleanup(self):
        """Safely purges temporary installation files created by the updater"""
        if not os.path.exists(UPDATE_CLEANUP_FILE_PATH):
            return

        log.info("Update cleanup file found. Proceeding with cleanup.")
        try:
            with open(UPDATE_CLEANUP_FILE_PATH, 'r', encoding='utf-8') as f:
                cleanup_data = json.load(f)

            dir_to_delete = cleanup_data.get('temp_dir_to_delete')
            if not dir_to_delete:
                log.warning("Cleanup file exists but contains no directory to delete.")
                return

            system_temp_dir = os.path.realpath(tempfile.gettempdir())
            path_to_delete = os.path.realpath(dir_to_delete)

            if not path_to_delete.startswith(system_temp_dir):
                log.error(f"SECURITY: Update cleanup aborted. Path '{path_to_delete}' is not in temp dir '{system_temp_dir}'.")
                return

            if os.path.isdir(path_to_delete):
                shutil.rmtree(path_to_delete, ignore_errors=True)
                log.info(f"Update Cleanup: Successfully removed temporary directory '{path_to_delete}'.")

        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Update Cleanup Error: Could not read or parse cleanup file. Error: {e}")
        finally:
            try:
                os.remove(UPDATE_CLEANUP_FILE_PATH)
            except OSError as e:
                log.error(f"Failed to remove cleanup file: {e}")

    def show_and_raise(self):
        self.helpers.show_and_raise()

    def show_error_dialog(self, title, message, hint=None):
        self.helpers.show_error_dialog(title, message, hint=hint)
```

--- End of file ---

--- File: `src/ui/custom_error_dialog.py` ---

```python
import pyperclip
from tkinter import Toplevel, Frame, Message, Label
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import position_window

class CustomErrorDialog(Toplevel):
    def __init__(self, parent, title, message, hint=None):
        super().__init__(parent)
        self.parent = parent
        self.message = message
        self.hint = hint
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.iconbitmap(ICON_PATH)

        self.configure(bg=c.DARK_BG)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        msg_widget = Message(main_frame, text=self.message, width=350, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        msg_widget.pack(pady=(0, 10))

        if self.hint:
            hint_label = Label(
                main_frame, text=self.hint, wraplength=350,
                bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR,
                font=c.FONT_STATUS_BAR, justify='left'
            )
            hint_label.pack(pady=(0, 20), anchor='w')

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.pack(fill='x')

        ok_button = RoundedButton(button_frame, text="OK", command=self.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        ok_button.pack(side='right')

        copy_button = RoundedButton(button_frame, text="Copy Error", command=self._copy_to_clipboard, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, height=30, cursor='hand2')
        copy_button.pack(side='right', padx=(0, 10))

        self.bind("<Escape>", lambda e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()
        required_height = self.winfo_reqheight()
        dialog_width = 400
        self.geometry(f"{dialog_width}x{required_height}")
        self.resizable(False, False)

        # Ensure the window is fully on-screen and centered relative to parent
        position_window(self)

        self.deiconify()
        ok_button.focus_set()
        self.wait_window(self)

    def _copy_to_clipboard(self):
        # We only copy the core message, excluding the UI hint
        pyperclip.copy(self.message)
```

--- End of file ---

--- File: `src/ui/title_edit_dialog.py` ---

```python
from tkinter import Toplevel, Frame, Label, Entry, StringVar
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import position_window

class TitleEditDialog(Toplevel):
    def __init__(self, parent, title, prompt, initialvalue="", max_length=None):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.iconbitmap(ICON_PATH)
        self.result = None
        self.max_length = max_length

        self.configure(bg=c.DARK_BG)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        Label(main_frame, text=prompt, wraplength=350, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=(0, 10), anchor='w')

        self.entry_var = StringVar(value=initialvalue)
        self.entry = Entry(main_frame, textvariable=self.entry_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.entry.pack(pady=5, fill='x', ipady=4)
        self.entry.select_range(0, 'end')

        if self.max_length:
            self.entry_var.trace_add("write", self._validate_length)

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.pack(pady=(15, 0), fill='x', anchor='e')
        right_buttons_frame = Frame(button_frame, bg=c.DARK_BG)
        right_buttons_frame.pack(side='right')

        ok_button = RoundedButton(right_buttons_frame, text="OK", command=self.on_ok, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        ok_button.pack(side='right')

        cancel_button = RoundedButton(right_buttons_frame, text="Cancel", command=self.on_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        cancel_button.pack(side='right', padx=(0, 10))

        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_cancel)

        # Set a fixed width and calculate height
        self.update_idletasks()
        required_height = self.winfo_reqheight()
        self.geometry(f"{c.TITLE_EDIT_DIALOG_WIDTH}x{required_height}")
        self.resizable(False, False)

        # Ensure the window is fully on-screen and centered relative to parent
        position_window(self)

        self.deiconify()
        self.entry.focus_set()
        self.wait_window(self)

    def _validate_length(self, *args):
        value = self.entry_var.get()
        if len(value) > self.max_length:
            self.entry_var.set(value[:self.max_length])

    def on_ok(self, event=None):
        self.result = self.entry_var.get()
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()
```

--- End of file ---

--- File: `src/ui/multiline_input_dialog.py` ---

```python
from tkinter import Toplevel, Frame, Label, Text
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import position_window

class MultilineInputDialog(Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.iconbitmap(ICON_PATH)
        self.result = None

        self.configure(bg=c.DARK_BG)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        Label(main_frame, text=prompt, wraplength=450, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=(0, 10), sticky='w')

        text_frame = Frame(main_frame, bg=c.TEXT_INPUT_BG, bd=1, relief='sunken')
        text_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        self.text_widget = Text(text_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, undo=True, wrap='word')
        self.text_widget.pack(fill='both', expand=True, padx=5, pady=5)

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=2, column=0, pady=(15, 0), sticky='e')

        ok_button = RoundedButton(button_frame, text="OK", command=self.on_ok, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        ok_button.pack(side='right')

        cancel_button = RoundedButton(button_frame, text="Cancel", command=self.on_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        cancel_button.pack(side='right', padx=(0, 10))

        self.bind("<Control-Return>", self.on_ok)
        self.bind("<Escape>", self.on_cancel)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.geometry("500x400")
        self.minsize(400, 300)
        position_window(self)
        self.deiconify()
        self.text_widget.focus_set()
        self.wait_window(self)

    def on_ok(self, event=None):
        self.result = self.text_widget.get('1.0', 'end-1c')
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()
```

--- End of file ---

--- File: `src/ui/new_filetypes_dialog.py` ---

```python
import tkinter as tk
from tkinter import Toplevel, Frame, Label
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_frame import ScrollableFrame
from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import position_window

class NewFiletypesDialog(Toplevel):
    def __init__(self, parent, new_filetypes_data):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.transient(parent)
        self.title("New Filetypes Added")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        Label(
            main_frame,
            text="The following new default filetypes have been added to your configuration:",
            wraplength=400, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR,
            font=c.FONT_NORMAL
        ).pack(anchor='w', pady=(0, 10))

        ok_button = RoundedButton(
            main_frame, text="OK", command=self.destroy,
            bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL,
            width=90, height=30, cursor='hand2'
        )
        ok_button.pack(side='bottom', anchor='e', pady=(15, 0))

        # Scrollable List of New Filetypes
        scroll_container = ScrollableFrame(main_frame, bg=c.DARK_BG)
        scroll_container.pack(fill='both', expand=True, pady=5)
        content_frame = scroll_container.scrollable_frame

        for ft in sorted(new_filetypes_data, key=lambda x: x['ext']):
            row = Frame(content_frame, bg=c.DARK_BG)
            row.pack(fill='x', expand=True, pady=3, padx=5)

            ext_label = Label(row, text=ft['ext'], font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR, width=12, anchor='w')
            ext_label.pack(side='left')

            desc_label = Label(row, text=ft.get('description', ''), font=c.FONT_NORMAL, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, wraplength=280, justify='left', anchor='w')
            desc_label.pack(side='left', fill='x', expand=True)

        self.bind("<Return>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()

        # Re-calculate height based on the new layout
        num_items = len(new_filetypes_data)
        item_height_estimate = 35
        # Calculate the fixed height of elements outside the list
        base_height = ok_button.winfo_reqheight() + 130
        # Calculate the variable height of the list, with a maximum
        list_height = min(num_items * item_height_estimate, 350)
        dialog_height = base_height + list_height

        dialog_width = 450
        self.geometry(f"{dialog_width}x{dialog_height}")
        self.resizable(True, True)

        position_window(self)

        self.deiconify()
        ok_button.focus_set()
```

--- End of file ---

--- File: `src/ui/new_profile_dialog.py` ---

```python
from tkinter import Toplevel, Frame, Label, Entry, StringVar, BooleanVar, messagebox, ttk
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.paths import ICON_PATH
from .style_manager import apply_dark_theme
from .window_utils import position_window
from .info_manager import attach_info_mode
from .assets import assets

class NewProfileDialog(Toplevel):
    def __init__(self, parent, existing_profile_names):
        super().__init__(parent)
        self.parent = parent
        self.existing_names_lower = [name.lower() for name in existing_profile_names]
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title("Create New Profile")
        self.iconbitmap(ICON_PATH)
        self.result = None

        # Ensure grid is used on the Toplevel so the main frame and info panel never overlap
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.configure(bg=c.DARK_BG)
        apply_dark_theme(self)
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")

        Label(main_frame, text="Enter a unique name for the new profile:", bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=(0, 5), anchor='w')

        self.entry_var = StringVar()
        self.entry = Entry(main_frame, textvariable=self.entry_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.entry.pack(pady=5, fill='x', ipady=4)

        options_frame = Frame(main_frame, bg=c.DARK_BG)
        options_frame.pack(fill='x', pady=(15, 0))

        self.copy_files_var = BooleanVar(value=False)
        self.copy_files_chk = ttk.Checkbutton(options_frame, text="Copy current file selection", variable=self.copy_files_var, style='Dark.TCheckbutton')
        self.copy_files_chk.pack(anchor='w')

        self.copy_instructions_var = BooleanVar(value=False)
        self.copy_inst_chk = ttk.Checkbutton(options_frame, text="Copy current instructions", variable=self.copy_instructions_var, style='Dark.TCheckbutton')
        self.copy_inst_chk.pack(anchor='w')

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.pack(pady=(20, 0), fill='x')

        # Info Toggle integration: Managed by InfoManager via .place()
        self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")

        right_buttons_frame = Frame(button_frame, bg=c.DARK_BG)
        right_buttons_frame.pack(side='right')

        ok_button = RoundedButton(right_buttons_frame, text="Create", command=self.on_ok, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        ok_button.pack(side='right')

        cancel_button = RoundedButton(right_buttons_frame, text="Cancel", command=self.on_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor='hand2')
        cancel_button.pack(side='right', padx=(0, 10))

        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_cancel)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # Info Mode Integration
        self.info_mgr = attach_info_mode(self, self.parent.app_state, manager_type='grid', grid_row=1, toggle_btn=self.info_toggle_btn)
        self.info_mgr.register(self.entry, "profile_name")
        self.info_mgr.register(self.copy_files_chk, "profile_copy_files")
        self.info_mgr.register(self.copy_inst_chk, "profile_copy_inst")
        self.info_mgr.register(ok_button, "profile_create")
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")

        self.update_idletasks()
        required_height = self.winfo_reqheight()

        # Factor in the panel if active on boot
        if self.parent.app_state.info_mode_active:
            required_height += c.INFO_PANEL_HEIGHT

        dialog_width = 400
        self.geometry(f"{dialog_width}x{required_height}")
        self.resizable(False, False)

        # Ensure the window is fully on-screen and centered relative to parent
        position_window(self)

        self.deiconify()
        self.entry.focus_set()
        self.wait_window(self)

    def on_ok(self, event=None):
        name = self.entry_var.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Profile name cannot be empty.", parent=self)
            return
        if name.lower() in self.existing_names_lower:
            messagebox.showwarning("Name Exists", f"A profile named '{name}' already exists.", parent=self)
            return

        self.result = {
            "name": name,
            "copy_files": self.copy_files_var.get(),
            "copy_instructions": self.copy_instructions_var.get()
        }
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()
```

--- End of file ---

--- File: `src/ui/project_selector_dialog.py` ---

```python
import os
import re
import tkinter as tk
from tkinter import Toplevel, Frame, Label, filedialog, StringVar, Entry, messagebox
import sys
import subprocess
import json
from ..core.project_config import ProjectConfig
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_frame import ScrollableFrame

from .. import constants as c
from ..core.paths import ICON_PATH
from .window_utils import save_window_geometry, get_monitor_work_area, position_window
from .assets import assets
from .info_manager import attach_info_mode

class ProjectSelectorDialog(Toplevel):
    """
    A dialog window for selecting a recent or new project directory.
    Features a scrollable list and a filter.
    """
    def __init__(self, parent, app_bg_color, recent_projects, on_select_callback, on_remove_callback):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.app_bg_color = app_bg_color
        self.recent_projects = recent_projects
        self.on_select_callback = on_select_callback
        self.on_remove_callback = on_remove_callback
        self.tooltip = None

        # Mapping of project path -> the Frame widget representing it
        self.project_widgets_map = {}

        self.project_metadata_cache = {}
        # Instance variables to reliably store the current position.
        self.current_x = 0
        self.current_y = 0

        self.title("Select Project")
        self.iconbitmap(ICON_PATH)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=self.app_bg_color)
        self.resizable(False, False)

        self.dialog_width = c.PROJECT_SELECTOR_WIDTH

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        message = "Select a recent project or browse for a new one" if self.recent_projects else "Browse for a project folder to get started"
        self.info_label = Label(self, text=message, padx=20, pady=10, bg=self.app_bg_color, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.info_label.grid(row=0, column=0, sticky='ew', pady=(5, 0))

        # Filter Bar
        self.filter_frame = Frame(self, bg=c.DARK_BG, padx=20)
        self.filter_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        Label(self.filter_frame, text="Filter:", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='left')
        self.filter_var = StringVar()
        self.filter_entry = Entry(self.filter_frame, textvariable=self.filter_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.filter_entry.pack(side='left', fill='x', expand=True, padx=(5,0), ipady=3)
        self.filter_var.trace_add('write', self._filter_projects)

        # Scrollable List Container
        self.list_container = Frame(self, bg=self.app_bg_color)
        self.list_container.grid(row=2, column=0, sticky='nsew')
        self.list_container.grid_rowconfigure(0, weight=1)
        self.list_container.grid_columnconfigure(0, weight=1)
        self.scroll_frame = ScrollableFrame(self.list_container, bg=self.app_bg_color)
        self.scroll_frame.grid(row=0, column=0, sticky='nsew')
        self.recent_dirs_frame = self.scroll_frame.scrollable_frame

        # Footer Section
        footer_frame = Frame(self, bg=self.app_bg_color, padx=20, pady=20)
        footer_frame.grid(row=3, column=0, sticky='ew')
        footer_frame.columnconfigure(1, weight=1)

        # Info Toggle: Managed by InfoManager.place
        self.info_toggle_btn = Label(self, image=assets.info_icon, bg=self.app_bg_color, cursor="hand2")

        # "Add Project" Button
        self.browse_btn = RoundedButton(
            footer_frame, text="Add project", command=self.browse_for_new_dir,
            bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor='hand2'
        )
        self.browse_btn.grid(row=0, column=1, sticky='ew', padx=(10, 0))

        # Let the window calculate its size with no list items.
        self.update_idletasks()
        initial_height = self.winfo_reqheight()

        # Accommodate info panel if active on boot
        if self.parent.app_state.info_mode_active:
            initial_height += c.INFO_PANEL_HEIGHT

        x, y = 0, 0
        saved_geometry = None

        if hasattr(self.parent, 'window_geometries'):
            saved_geometry = self.parent.window_geometries.get(self.__class__.__name__)

        if saved_geometry:
            try:
                parts = saved_geometry.replace('+', ' ').replace('x', ' ').split()
                if len(parts) == 4:
                    _, _, x, y = map(int, parts)
                else:
                    saved_geometry = None
            except (ValueError, IndexError):
                saved_geometry = None

        if not saved_geometry:
            parent_x, parent_y = self.parent.winfo_rootx(), self.parent.winfo_rooty()
            parent_w, parent_h = self.parent.winfo_width(), self.parent.winfo_height()
            x = parent_x + (parent_w - self.dialog_width) // 2
            y = parent_y + (parent_h - initial_height) // 2

        # Store the calculated position reliably.
        self.current_x = x
        self.current_y = y

        self.geometry(f"{self.dialog_width}x{initial_height}+{self.current_x}+{self.current_y}")

        # Info Mode Integration
        self.info_mgr = attach_info_mode(self, self.parent.app_state, manager_type='grid', grid_row=4, toggle_btn=self.info_toggle_btn)
        self.info_mgr.register(self.scroll_frame.canvas, "sel_list")
        self.info_mgr.register(self.filter_entry, "sel_filter")
        self.info_mgr.register(self.browse_btn, "sel_browse")
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")

        # Initial one-time creation of all project entry widgets
        self._initialize_project_widgets()
        self._filter_projects()

        self.protocol("WM_DELETE_WINDOW", self._close_and_save_geometry)
        self.bind('<Escape>', lambda e: self._close_and_save_geometry())
        self.bind('<Configure>', self._on_drag)

        self.deiconify()
        self.lift()
        self.focus_force()

        # Focus with delay for Tcl reliability
        self.after(100, self._set_initial_focus)

    def _set_initial_focus(self):
        """Requests focus on the filter entry."""
        if self.filter_frame.winfo_ismapped():
            self.filter_entry.focus_set()
            self.filter_entry.icursor(tk.END)

    def _on_drag(self, event):
        """Updates the stored position when the window is moved by the user."""
        if self.state() == 'normal' and event.widget == self:
            self.current_x = self.winfo_x()
            self.current_y = self.winfo_y()

    def _initialize_project_widgets(self):
        """Creates widgets for all recent projects once."""
        for path in self.recent_projects:
            entry_frame = self._create_recent_dir_entry(path)
            self.project_widgets_map[path] = entry_frame
            # Start hidden; _filter_projects will show relevant ones
            entry_frame.pack_forget()

    def _filter_projects(self, *args):
        """Toggles visibility of existing widgets based on query instead of rebuilding."""
        query = self.filter_var.get().lower()

        # Update filter bar visibility: Hide if user has less than 5 projects total
        if len(self.recent_projects) >= 5:
            if not self.filter_frame.winfo_ismapped():
                self.filter_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        else:
            if self.filter_frame.winfo_ismapped():
                self.filter_frame.grid_forget()
                if self.filter_var.get():
                    self.filter_var.set("")
                    return

        # Toggle visibility of existing widgets
        visible_count = 0
        for path, frame in self.project_widgets_map.items():
            metadata = self._get_project_metadata(path)
            matches = not query or query in metadata['name'].lower() or query in path.lower()

            if matches:
                frame.pack(fill='x', padx=20, pady=3)
                visible_count += 1
            else:
                frame.pack_forget()

        # Handle 'No Results' state
        if visible_count == 0 and self.recent_projects:
            if not hasattr(self, 'no_results_label'):
                self.no_results_label = Label(self.recent_dirs_frame, text="No projects match your filter.", bg=self.app_bg_color, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL, pady=20)
            self.no_results_label.pack(fill='x')
        elif hasattr(self, 'no_results_label'):
            self.no_results_label.pack_forget()

        self._adjust_height(visible_count)

    def _get_project_metadata(self, path):
        """
        Retrieves project name and color from a cache to avoid repeated file I/O.
        """
        if path in self.project_metadata_cache:
            return self.project_metadata_cache[path]

        allcode_path = os.path.join(path, '.allcode')
        name = os.path.basename(path)
        color = c.COMPACT_MODE_BG_COLOR

        if os.path.isfile(allcode_path):
            try:
                with open(allcode_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    if content:
                        data = json.loads(content)
                        name = data.get('project_name', name)
                        color = data.get('project_color', color)
            except (IOError, json.JSONDecodeError):
                pass

        metadata = {'name': name, 'color': color}
        self.project_metadata_cache[path] = metadata
        return metadata

    def _adjust_height(self, visible_count):
        """
        Calculates and applies the height without using flickering geometry reset calls.
        """
        # Determine row height
        item_h = 38
        if visible_count > 0:
            # Sample first visible widget
            for frame in self.project_widgets_map.values():
                if frame.winfo_ismapped():
                    req_h = frame.winfo_reqheight()
                    if req_h > 1:
                        item_h = req_h + 6 # req + padding
                        break

        # Set the specific height for the Canvas (cap at 10 rows)
        list_h = min(visible_count, 10) * item_h
        self.scroll_frame.canvas.config(height=list_h)

        # Update internal layout logic
        self.update_idletasks()

        # Apply the final height while keeping x/y and ensuring on-screen
        win_w, win_h = self.dialog_width, self.winfo_reqheight()

        x, y = self.current_x, self.current_y
        mon_left, mon_top, mon_right, mon_bottom = get_monitor_work_area((x, y))
        mon_bottom -= 50; mon_right -= 20; mon_left += 10; mon_top += 10
        if x + win_w > mon_right: x = mon_right - win_w
        if y + win_h > mon_bottom: y = mon_bottom - win_h
        if x < mon_left: x = mon_left
        if y < mon_top: y = mon_top

        self.geometry(f"{win_w}x{win_h}+{x}+{y}")

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def _show_trash_button(self, container):
        if hasattr(container, 'trash_button'):
            container.trash_button.pack(side='left', padx=(10, 0))

    def _hide_trash_button(self, container):
        if hasattr(container, 'trash_button'):
            container.trash_button.pack_forget()

    def _create_recent_dir_entry(self, path):
        entry_frame = Frame(self.recent_dirs_frame, bg=self.app_bg_color)

        metadata = self._get_project_metadata(path)
        display_text = metadata['name']
        project_color = metadata['color']

        logo_image = self.parent.assets.create_masked_logo_small(project_color)
        color_swatch = Label(entry_frame, image=logo_image, bg=self.app_bg_color)
        color_swatch.image = logo_image # Prevent garbage collection
        color_swatch.pack(side='left', padx=(0, 10))

        # This container will hold the main project button and the trash button
        buttons_container = Frame(entry_frame, bg=self.app_bg_color)
        buttons_container.pack(side='left', expand=True, fill='x')

        btn = RoundedButton(
            buttons_container, text=display_text, command=None,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, height=32, cursor='hand2', text_align='left'
        )
        btn.pack(side='left', expand=True, fill='x')

        if assets.trash_icon_image:
            remove_btn = RoundedButton(
                parent=buttons_container, command=lambda p=path: self.remove_and_update_dialog(p),
                image=assets.trash_icon_image, bg=c.BTN_GRAY_BG, width=32, height=32, cursor='hand2'
            )
            buttons_container.trash_button = remove_btn

            if hasattr(self, 'info_mgr'):
                self.info_mgr.register(remove_btn, "sel_remove")

        # Event Bindings
        btn.bind("<ButtonRelease-1>", lambda e, p=path: self.on_project_button_release(e, p))
        btn.bind("<Enter>", lambda e, p=path: self.show_path_tooltip(e, p))
        btn.bind("<Leave>", self.hide_path_tooltip)

        entry_frame.bind("<Enter>", lambda e, c=buttons_container: self._show_trash_button(c))
        entry_frame.bind("<Leave>", lambda e, c=buttons_container: self._hide_trash_button(c))

        return entry_frame

    def on_project_button_release(self, event, path):
        widget = event.widget
        if 0 <= event.x <= widget.winfo_width() and 0 <= event.y <= widget.winfo_height():
            if hasattr(widget, '_draw') and hasattr(widget, 'hover_color'):
                widget._draw(widget.hover_color)

            is_ctrl = (event.state & 0x0004)
            if is_ctrl:
                self.open_project_folder(path)
            else:
                self.select_and_close(path)
        else:
            if hasattr(widget, '_draw') and hasattr(widget, 'base_color'):
                widget._draw(widget.base_color)

    def open_project_folder(self, path):
        if not (path and os.path.isdir(path)):
            return
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}", parent=self)

    def show_path_tooltip(self, event, path):
        if self.tooltip: self.tooltip.destroy()
        x, y = event.widget.winfo_rootx(), event.widget.winfo_rooty() + event.widget.winfo_height() + 1
        self.tooltip = Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = Label(self.tooltip, text=path+" (ctrl-click to open)", justify='left', bg=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1, font=c.FONT_TOOLTIP, padx=4, pady=2)
        label.pack(ipadx=2, ipady=1)

    def hide_path_tooltip(self, event):
        if self.tooltip: self.tooltip.destroy(); self.tooltip = None

    def select_and_close(self, path):
        if self.on_select_callback: self.on_select_callback(path)
        self._close_and_save_geometry()

    def browse_for_new_dir(self):
        new_path = filedialog.askdirectory(title="Select Project Folder", parent=self)
        if new_path: self.select_and_close(new_path)

    def remove_and_update_dialog(self, path_to_remove):
        self.on_remove_callback(path_to_remove)
        self.recent_projects = [p for p in self.recent_projects if p != path_to_remove]

        # Cleanup the persistent widget
        if path_to_remove in self.project_widgets_map:
            self.project_widgets_map[path_to_remove].destroy()
            del self.project_widgets_map[path_to_remove]

        self._filter_projects()

        if not self.recent_projects:
            self.info_label.config(text="Browse for a project folder to get started")

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()
```

--- End of file ---

--- File: `src/ui/paste_changes_dialog.py` ---

```python
import os
import re
from tkinter import Toplevel, Frame, Label, messagebox
from .. import constants as c
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .widgets.scrollable_text import ScrollableText
from ..core import change_applier
from .window_utils import position_window
from .custom_error_dialog import CustomErrorDialog
from .info_manager import attach_info_mode
from .assets import assets

class PasteChangesDialog(Toplevel):
    def __init__(self, parent, project_base_dir, status_var, initial_content=None):
        super().__init__(parent)
        self.parent = parent
        self.base_dir = project_base_dir
        self.status_var = status_var
        self.withdraw()
        self.transient(parent)
        self.grab_set()
        self.title("Paste and Apply File Changes")
        self.iconbitmap(ICON_PATH)
        self.result = None

        self.configure(bg=c.DARK_BG)

        # Ensure grid is used on the Toplevel so the main frame and info panel never overlap
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Dynamic Geometry for Boot
        initial_w, initial_h = 600, 500
        if self.parent.app_state.info_mode_active:
            initial_h += c.INFO_PANEL_HEIGHT

        self.geometry(f"{initial_w}x{initial_h}")
        self.minsize(500, 400)

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        Label(
            main_frame,
            text="Paste the markdown from the language model below.",
            wraplength=550, justify='left', bg=c.DARK_BG, fg=c.TEXT_COLOR
        ).grid(row=0, column=0, pady=(0, 10), sticky='w')

        self.text_widget = ScrollableText(
            main_frame, height=15, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL
        )
        self.text_widget.grid(row=1, column=0, sticky='nsew', pady=5)

        if initial_content:
            self.text_widget.insert('1.0', initial_content)

        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=2, column=0, pady=(15, 0), sticky='ew')
        button_frame.grid_columnconfigure(1, weight=1)

        # Info Toggle: Managed by InfoManager.place
        self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")

        action_btns_frame = Frame(button_frame, bg=c.DARK_BG)
        action_btns_frame.grid(row=0, column=1, sticky='e')

        ok_button = RoundedButton(
            action_btns_frame, text="Apply Changes", command=self.on_apply,
            bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL,
            width=140, height=30, cursor='hand2'
        )
        ok_button.pack(side='right')

        cancel_button = RoundedButton(
            action_btns_frame, text="Cancel", command=self.on_cancel,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL,
            width=90, height=30, cursor='hand2'
        )
        cancel_button.pack(side='right', padx=(0, 10))

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.bind("<Escape>", self.on_cancel)

        # Info Mode Integration
        self.info_mgr = attach_info_mode(self, self.parent.app_state, manager_type='grid', grid_row=1, toggle_btn=self.info_toggle_btn)
        self.info_mgr.register(self.text_widget, "paste_text")
        self.info_mgr.register(ok_button, "paste_apply")
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")

        position_window(self)
        self.deiconify()
        self.lift()
        self.focus_force()
        self.text_widget.text_widget.focus_set()
        self.wait_window(self)

    def on_apply(self):
        markdown_text = self.text_widget.get('1.0', 'end-1c')
        if not markdown_text.strip():
            messagebox.showwarning("Input Error", "The text input cannot be empty.", parent=self)
            return

        plan = change_applier.parse_and_plan_changes(self.base_dir, markdown_text)

        logical_app = self.parent
        while logical_app and not hasattr(logical_app, 'action_handlers'):
            logical_app = logical_app.master

        if logical_app:
            logical_app.action_handlers._handle_parsed_plan(plan, self.base_dir, dialog_to_close=self)

    def on_cancel(self, event=None):
        self.destroy()
```

--- End of file ---

--- File: `src/ui/instructions_window.py` ---

```python
import os
import re
from tkinter import Toplevel, Frame, Label
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from ..core.utils import load_config
from .tooltip import ToolTip
from .window_utils import position_window, save_window_geometry
from .assets import assets
from .widgets.scrollable_text import ScrollableText
from .info_manager import attach_info_mode

class InstructionsWindow(Toplevel):
    def __init__(self, parent, project_config, status_var, on_close_callback=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.project_config = project_config
        self.status_var = status_var
        self.on_close_callback = on_close_callback

        # Window Setup
        self.title("Set Instructions")
        self.iconbitmap(ICON_PATH)

        # Ensure grid is used on the Toplevel so the main frame and info panel never overlap
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Dynamic Geometry for Boot
        initial_geom = c.INSTRUCTIONS_WINDOW_DEFAULT_GEOMETRY
        if self.parent.app_state.info_mode_active:
            match = re.match(r"(\d+)x(\d+)", initial_geom)
            if match:
                w, h = map(int, match.groups())
                initial_geom = f"{w}x{h + c.INFO_PANEL_HEIGHT}"

        self.geometry(initial_geom)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

        # UI Layout using a single, robust Grid
        main_frame = Frame(self, padx=15, pady=15, bg=c.DARK_BG)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.grid_columnconfigure(0, weight=1)
        # Configure rows for labels, text areas (expanding), and buttons
        main_frame.grid_rowconfigure(1, weight=1) # Intro text
        main_frame.grid_rowconfigure(3, weight=1) # Outro text

        # Intro Section
        intro_label_frame = Frame(main_frame, bg=c.DARK_BG)
        intro_label_frame.grid(row=0, column=0, sticky='w', pady=(0, 5))
        Label(intro_label_frame, text="Intro Instructions", font=c.FONT_WRAPPER_TITLE, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')
        Label(intro_label_frame, text="(prepended to the final output):", font=c.FONT_WRAPPER_SUBTITLE, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='left', padx=(4,0))

        self.intro_text = ScrollableText(
            main_frame, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL
        )
        self.intro_text.grid(row=1, column=0, sticky='nsew', pady=(0, 10))

        # Outro Section
        outro_label_frame = Frame(main_frame, bg=c.DARK_BG)
        outro_label_frame.grid(row=2, column=0, sticky='w', pady=(0, 5))
        Label(outro_label_frame, text="Outro Instructions", font=c.FONT_WRAPPER_TITLE, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')
        Label(outro_label_frame, text="(appended to the final output):", font=c.FONT_WRAPPER_SUBTITLE, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(side='left', padx=(4,0))

        self.outro_text = ScrollableText(
            main_frame, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL
        )
        self.outro_text.grid(row=3, column=0, sticky='nsew')

        # Action Buttons Section
        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=4, column=0, sticky='ew', pady=(10, 0))

        # Info Toggle: Managed by InfoManager.place
        self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")

        config = load_config()

        # Defensive check for list types if config was previously corrupted by trailing commas
        default_intro = config.get('default_intro_prompt', '')
        if isinstance(default_intro, (list, tuple)):
            default_intro = "\n".join(default_intro)
        default_intro = default_intro.strip()

        default_outro = config.get('default_outro_prompt', '')
        if isinstance(default_outro, (list, tuple)):
            default_outro = "\n".join(default_outro)
        default_outro = default_outro.strip()

        if assets.defaults_icon and (default_intro or default_outro):
            self.defaults_button = Label(button_frame, image=assets.defaults_icon, bg=c.DARK_BG, cursor="hand2")
            self.defaults_button.image = assets.defaults_icon
            self.defaults_button.pack(side='left', padx=(24, 10), anchor='w') # Gap for info button
            self.defaults_button.bind("<ButtonRelease-1>", self.populate_from_defaults)
            ToolTip(self.defaults_button, "Populate fields with default prompts from Settings")

        self.save_button = RoundedButton(
            button_frame, text="Save and Close", command=self.save_and_close,
            bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor='hand2'
        )
        self.save_button.pack(side='right')

        # Populate Text Fields
        # Handle existing project config data defensively
        curr_intro = self.project_config.intro_text
        if isinstance(curr_intro, (list, tuple)): curr_intro = "\n".join(curr_intro)

        curr_outro = self.project_config.outro_text
        if isinstance(curr_outro, (list, tuple)): curr_outro = "\n".join(curr_outro)

        self.intro_text.insert('1.0', curr_intro)
        self.outro_text.insert('1.0', curr_outro)

        self.protocol("WM_DELETE_WINDOW", self._close_and_save_geometry)
        self.bind('<Escape>', lambda e: self._close_and_save_geometry())

        # Info Mode Integration
        self.info_mgr = attach_info_mode(self, self.parent.app_state, manager_type='grid', grid_row=1, toggle_btn=self.info_toggle_btn)
        self.info_mgr.register(self.intro_text, "inst_intro")
        self.info_mgr.register(self.outro_text, "inst_outro")
        self.info_mgr.register(self.save_button, "inst_save")
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")
        if hasattr(self, 'defaults_button'):
            self.info_mgr.register(self.defaults_button, "inst_defaults")

        self._position_window()
        self.deiconify()

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def populate_from_defaults(self, event=None):
        if event is not None:
            if not (0 <= event.x <= event.widget.winfo_width() and 0 <= event.y <= event.widget.winfo_height()):
                return

        config = load_config()
        default_intro = config.get('default_intro_prompt', '')
        if isinstance(default_intro, (list, tuple)): default_intro = "\n".join(default_intro)

        default_outro = config.get('default_outro_prompt', '')
        if isinstance(default_outro, (list, tuple)): default_outro = "\n".join(default_outro)

        self.intro_text.delete('1.0', 'end')
        self.intro_text.insert('1.0', default_intro)

        self.outro_text.delete('1.0', 'end')
        self.outro_text.insert('1.0', default_outro)

    def save_and_close(self):
        """Saves the intro/outro text to the .allcode file and closes the window"""
        self.project_config.intro_text = self.intro_text.get('1.0', 'end-1c')
        self.project_config.outro_text = self.outro_text.get('1.0', 'end-1c')

        try:
            self.project_config.save()
            self.status_var.set("Instructions saved successfully.")
        except IOError as e:
            self.status_var.set(f"Error saving instructions: {e}")

        if self.on_close_callback:
            self.on_close_callback()

        self._close_and_save_geometry()
```

--- End of file ---

--- File: `src/ui/settings/collapsible_section.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, BooleanVar
from ..widgets.rounded_button import RoundedButton
from ... import constants as c
from ..widgets.scrollable_text import ScrollableText

class CollapsibleTextSection(Frame):
    """
    A collapsible frame containing a title, a reset button, and a multi-line text widget.
    """
    def __init__(self, parent, title, initial_text, default_text, on_toggle_callback=None, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.on_toggle_callback = on_toggle_callback

        # Header
        header_frame = Frame(self, bg=c.DARK_BG)
        header_frame.pack(fill='x', expand=True)

        self.icon_label = Label(header_frame, text="▶", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR, cursor="hand2")
        self.icon_label.pack(side='left', padx=(0, 5))

        title_label = Label(header_frame, text=title, font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR, cursor="hand2")
        title_label.pack(side='left')

        reset_button = RoundedButton(
            header_frame, text="Reset", command=self.reset_text,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON, height=22, radius=4,
            cursor='hand2'
        )
        reset_button.pack(side='right', padx=(5, 0))

        # Body (initially hidden)
        self.body_frame = Frame(self, bg=c.DARK_BG)

        self.text_widget = ScrollableText(
            self.body_frame,
            height=4,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=c.FONT_NORMAL
        )
        self.text_widget.pack(fill='x', expand=True, padx=(22, 0))

        # State and Bindings
        self.is_expanded = BooleanVar(value=False)
        self.default_text = default_text

        # Sanitize initial_text to prevent Tcl brace artifacts if it's a list/tuple
        display_text = initial_text
        if isinstance(display_text, (list, tuple)):
            display_text = "\n".join(display_text)

        self.text_widget.insert('1.0', display_text)

        self.icon_label.bind("<Button-1>", self.toggle_section)
        title_label.bind("<Button-1>", self.toggle_section)

    def toggle_section(self, event=None):
        """Expands or collapses the text area."""
        self.is_expanded.set(not self.is_expanded.get())
        if self.is_expanded.get():
            self.body_frame.pack(fill='x', expand=True, pady=(2, 0))
            self.icon_label.config(text="▼")
        else:
            self.body_frame.pack_forget()
            self.icon_label.config(text="▶")

        if self.on_toggle_callback:
            self.after(5, self.on_toggle_callback)

    def reset_text(self):
        """Resets the text widget to its default value."""
        self.text_widget.delete('1.0', 'end')

        # Sanitize default_text to prevent Tcl brace artifacts
        text_to_insert = self.default_text
        if isinstance(text_to_insert, (list, tuple)):
            text_to_insert = "\n".join(text_to_insert)

        self.text_widget.insert('1.0', text_to_insert)

    def get_text(self):
        """Returns the current content of the text widget."""
        return self.text_widget.get('1.0', 'end-1c')
```

--- End of file ---

--- File: `src/ui/settings/application_settings.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, ttk
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class ApplicationSettingsFrame(Frame):
    def __init__(self, parent, vars, updater, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.updater = updater
        self.enable_new_file_check = vars['enable_new_file_check']
        self.new_file_check_interval = vars['new_file_check_interval']
        self.scan_for_secrets = vars['scan_for_secrets']
        self.enable_compact_mode_on_minimize = vars['enable_compact_mode_on_minimize']
        self.check_for_updates = vars['check_for_updates']
        self.show_feedback_on_paste = vars['show_feedback_on_paste']

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="Application settings", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(0, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15), padx=(25, 0))

        # File Check Section
        file_check_frame = Frame(container, bg=c.DARK_BG)
        file_check_frame.pack(fill='x', expand=True, pady=(0, 5))

        self.new_file_chk = ttk.Checkbutton(file_check_frame, text="Periodically check for new project files", variable=self.enable_new_file_check, style='Dark.TCheckbutton', command=self._toggle_interval_selector)
        self.new_file_chk.pack(anchor='w')

        interval_frame = Frame(file_check_frame, bg=c.DARK_BG)
        interval_frame.pack(fill='x', padx=(25, 0), pady=(5, 0))
        self.interval_label = Label(interval_frame, text="Check every:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.interval_label.pack(side='left', padx=(0, 10))
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.new_file_check_interval, values=['2', '5', '10', '30', '60'], state='readonly', width=5, style='Dark.TCombobox')
        self.interval_combo.pack(side='left')
        self.seconds_label = Label(interval_frame, text="seconds", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.seconds_label.pack(side='left', padx=(5, 0))
        self._toggle_interval_selector()

        # Secret Scanning
        self.secrets_chk = ttk.Checkbutton(container, text="Scan for secrets (on each copy)", variable=self.scan_for_secrets, style='Dark.TCheckbutton')
        self.secrets_chk.pack(anchor='w')

        # Feedback Options
        self.feedback_chk = ttk.Checkbutton(container, text="Show LLM feedback window automatically on paste", variable=self.show_feedback_on_paste, style='Dark.TCheckbutton')
        self.feedback_chk.pack(anchor='w')

        # Compact Mode
        self.compact_chk = ttk.Checkbutton(container, text="Activate compact mode when main window is minimized", variable=self.enable_compact_mode_on_minimize, style='Dark.TCheckbutton')
        self.compact_chk.pack(anchor='w')

        # Updates
        updates_frame = Frame(container, bg=c.DARK_BG)
        updates_frame.pack(fill='x', expand=True, pady=(10, 0))
        self.updates_chk = ttk.Checkbutton(updates_frame, text="Automatically check for updates daily", variable=self.check_for_updates, style='Dark.TCheckbutton')
        self.updates_chk.pack(side='left')

        self.check_now_btn = RoundedButton(
            updates_frame, text="Check Now", command=self.updater.check_for_updates_manual,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=22, radius=4, cursor='hand2'
        )
        self.check_now_btn.pack(side='left', padx=(10, 0))

    def register_info(self, info_mgr):
        """Registers granular components with Info Mode."""
        info_mgr.register(self.new_file_chk, "set_app_new_file")
        info_mgr.register(self.interval_label, "set_app_interval")
        info_mgr.register(self.interval_combo, "set_app_interval")
        info_mgr.register(self.seconds_label, "set_app_interval")
        info_mgr.register(self.secrets_chk, "set_app_secrets")
        info_mgr.register(self.feedback_chk, "set_app_feedback")
        info_mgr.register(self.compact_chk, "set_app_compact")
        info_mgr.register(self.updates_chk, "set_app_updates")
        info_mgr.register(self.check_now_btn, "set_app_check_now")

    def _toggle_interval_selector(self):
        new_state = 'normal' if self.enable_new_file_check.get() else 'disabled'
        self.interval_label.config(state=new_state)
        self.interval_combo.config(state='readonly' if self.enable_new_file_check.get() else 'disabled')
```

--- End of file ---

--- File: `src/ui/settings/file_manager_settings.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, Entry, ttk
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class FileManagerSettingsFrame(Frame):
    def __init__(self, parent, vars, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.token_count_enabled = vars['token_count_enabled']
        self.token_limit = vars['token_limit']
        self.add_all_warning_threshold = vars['add_all_warning_threshold']
        self.new_file_alert_threshold = vars['new_file_alert_threshold']

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="File Manager", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15), padx=(25, 0))

        # Token Counting
        self.tokens_chk = ttk.Checkbutton(container, text="Enable token counting", variable=self.token_count_enabled, style='Dark.TCheckbutton')
        self.tokens_chk.pack(anchor='w')

        # Token Limit Section
        limit_frame = Frame(container, bg=c.DARK_BG)
        limit_frame.pack(fill='x', expand=True, pady=(5, 0))
        self.limit_label = Label(limit_frame, text="Max token limit (empty for none):", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.limit_label.pack(side='left', padx=(0, 10))

        vcmd = (self.register(self._validate_integer), '%P')
        self.limit_entry = Entry(limit_frame, textvariable=self.token_limit, width=8, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd)
        self.limit_entry.pack(side='left')

        self.limit_clear_btn = RoundedButton(limit_frame, text="Clear", command=lambda: self.token_limit.set(""), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=22, radius=4, cursor='hand2')
        self.limit_clear_btn.pack(side='left', padx=(10, 0))

        # 'Add All' Warning
        add_all_frame = Frame(container, bg=c.DARK_BG)
        add_all_frame.pack(fill='x', expand=True, pady=(5, 0))
        self.threshold_label = Label(add_all_frame, text="Warn when 'Add all' will add more than:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.threshold_label.pack(side='left', padx=(0, 10))

        self.threshold_entry = Entry(add_all_frame, textvariable=self.add_all_warning_threshold, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd)
        self.threshold_entry.pack(side='left')

        self.files_label = Label(add_all_frame, text="files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.files_label.pack(side='left', padx=(5, 0))

        # Apply Changes Creation Warning Threshold
        alert_frame = Frame(container, bg=c.DARK_BG)
        alert_frame.pack(fill='x', expand=True, pady=(5, 0))
        self.alert_threshold_label = Label(alert_frame, text="New file alert threshold:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.alert_threshold_label.pack(side='left', padx=(0, 10))

        self.alert_threshold_entry = Entry(alert_frame, textvariable=self.new_file_alert_threshold, width=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, validate='key', validatecommand=vcmd)
        self.alert_threshold_entry.pack(side='left')

        self.files_label_alert = Label(alert_frame, text="files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.files_label_alert.pack(side='left', padx=(5, 0))

    def register_info(self, info_mgr):
        """Registers granular components with Info Mode."""
        info_mgr.register(self.tokens_chk, "set_fm_tokens")
        info_mgr.register(self.limit_label, "set_fm_limit")
        info_mgr.register(self.limit_entry, "set_fm_limit")
        info_mgr.register(self.limit_clear_btn, "set_fm_limit")
        info_mgr.register(self.threshold_label, "set_fm_threshold")
        info_mgr.register(self.threshold_entry, "set_fm_threshold")
        info_mgr.register(self.files_label, "set_fm_threshold")
        info_mgr.register(self.alert_threshold_label, "set_fm_alert_threshold")
        info_mgr.register(self.alert_threshold_entry, "set_fm_alert_threshold")
        info_mgr.register(self.files_label_alert, "set_fm_alert_threshold")

    def _validate_integer(self, value_if_allowed):
        if value_if_allowed == "": return True
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False
```

--- End of file ---

--- File: `src/ui/settings/prompts_settings.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label
from .collapsible_section import CollapsibleTextSection
from ... import constants as c
from ...core import prompts as p

class PromptsSettingsFrame(Frame):
    def __init__(self, parent, config, on_toggle, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)

        self._create_widgets(config, on_toggle)

    def _create_widgets(self, config, on_toggle):
        Label(self, text="Prompts", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True, pady=(0, 15))

        self.copy_merged_prompt = CollapsibleTextSection(
            container, '\"Copy Code Only\" Prompt',
            config.get('copy_merged_prompt', ''), p.DEFAULT_COPY_MERGED_PROMPT,
            on_toggle_callback=on_toggle
        )
        self.copy_merged_prompt.pack(fill='x', expand=True, pady=(5, 0))

        self.default_intro = CollapsibleTextSection(
            container, 'Default Intro Instructions',
            config.get('default_intro_prompt', ''), p.DEFAULT_INTRO_PROMPT,
            on_toggle_callback=on_toggle
        )
        self.default_intro.pack(fill='x', expand=True, pady=(5, 0))

        self.default_outro = CollapsibleTextSection(
            container, 'Default Outro Instructions',
            config.get('default_outro_prompt', ''), p.DEFAULT_OUTRO_PROMPT,
            on_toggle_callback=on_toggle
        )
        self.default_outro.pack(fill='x', expand=True, pady=(5, 0))

    def register_info(self, info_mgr):
        """Registers collapsible prompt sections with Info Mode."""
        info_mgr.register(self.copy_merged_prompt, "set_prompt_merged")
        info_mgr.register(self.default_intro, "set_prompt_intro")
        info_mgr.register(self.default_outro, "set_prompt_outro")

    def get_values(self):
        return {
            'copy_merged_prompt': self.copy_merged_prompt.get_text(),
            'default_intro_prompt': self.default_intro.get_text(),
            'default_outro_prompt': self.default_outro.get_text(),
        }
```

--- End of file ---

--- File: `src/ui/settings/editor_settings.py` ---

```python
import os
import tkinter as tk
from tkinter import Frame, Label, Entry, filedialog
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class EditorSettingsFrame(Frame):
    def __init__(self, parent, vars, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.editor_path = vars['editor_path']

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="Default Editor", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True)

        self.path_entry = Entry(container, textvariable=self.editor_path, state='readonly', readonlybackground=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=4)

        self.browse_btn = RoundedButton(container, text="Browse...", command=self._browse_for_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        self.browse_btn.pack(side='left', padx=(0, 5))

        self.clear_btn = RoundedButton(container, text="Clear", command=self._clear_editor, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        self.clear_btn.pack(side='left')

    def register_info(self, info_mgr):
        """Registers granular components with Info Mode."""
        info_mgr.register(self.path_entry, "set_editor_path")
        info_mgr.register(self.browse_btn, "set_editor_path")
        info_mgr.register(self.clear_btn, "set_editor_path")

    def _browse_for_editor(self):
        file_types = [("Executable files", "*.exe"), ("All files", "*.*")] if os.name == 'nt' else []
        filepath = filedialog.askopenfilename(title="Select Editor Application", filetypes=file_types, parent=self)
        if filepath:
            self.editor_path.set(filepath)

    def _clear_editor(self):
        self.editor_path.set('')
```

--- End of file ---

--- File: `src/ui/settings/starter_settings.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, Entry, filedialog
from ..widgets.rounded_button import RoundedButton
from ... import constants as c

class StarterSettingsFrame(Frame):
    """
    Settings section for the Project Starter.
    """
    def __init__(self, parent, vars, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.default_parent_folder = vars['default_parent_folder']
        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="Project Starter", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(anchor='w', pady=(15, 5))
        container = Frame(self, bg=c.DARK_BG)
        container.pack(fill='x', expand=True)

        self.folder_label = Label(container, text="Default parent folder for new projects:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.folder_label.pack(anchor='w')

        folder_select_frame = Frame(container, bg=c.DARK_BG)
        folder_select_frame.pack(fill='x', pady=(5, 0))

        self.folder_entry = Entry(
            folder_select_frame, textvariable=self.default_parent_folder,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL
        )
        self.folder_entry.pack(side='left', fill='x', expand=True, ipady=4)

        self.browse_btn = RoundedButton(
            folder_select_frame, text="Browse", command=self._browse_folder,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON, height=28, cursor='hand2'
        )
        self.browse_btn.pack(side='left', padx=(5, 0))

    def register_info(self, info_mgr):
        """Registers granular components with Info Mode."""
        info_mgr.register(self.folder_label, "set_starter_folder")
        info_mgr.register(self.folder_entry, "set_starter_folder")
        info_mgr.register(self.browse_btn, "set_starter_folder")

    def _browse_folder(self):
        folder_selected = filedialog.askdirectory(parent=self)
        if folder_selected:
            self.default_parent_folder.set(folder_selected)
```

--- End of file ---

--- File: `src/ui/settings/settings_window.py` ---

```python
import tkinter as tk
import re
from tkinter import Toplevel, Frame, StringVar, BooleanVar, Label
from ...core.utils import load_config, save_config
from ...core.registry import get_setting, save_setting
from ...core.paths import ICON_PATH
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_frame import ScrollableFrame
from ..style_manager import apply_dark_theme
from .application_settings import ApplicationSettingsFrame
from .file_manager_settings import FileManagerSettingsFrame
from .prompts_settings import PromptsSettingsFrame
from .editor_settings import EditorSettingsFrame
from .starter_settings import StarterSettingsFrame
from ... import constants as c
from ..window_utils import position_window, save_window_geometry
from ..info_manager import attach_info_mode
from ..assets import assets

class SettingsWindow(Toplevel):
    def __init__(self, parent, updater, on_close_callback=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.updater = updater
        self.on_close_callback = on_close_callback

        self.config = load_config()
        self._init_vars()
        self._init_styles()
        self._init_window()
        self._create_widgets()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Escape>', lambda e: self.on_closing())

        # Info Toggle: Managed by InfoManager.place
        self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")

        # Info Mode Integration
        self.info_mgr = attach_info_mode(self, self.parent.app_state, manager_type='grid', grid_row=1, toggle_btn=self.info_toggle_btn)

        # Section summaries
        self.info_mgr.register(self.app_settings, "set_app")
        self.info_mgr.register(self.fm_settings, "set_fm")
        self.info_mgr.register(self.prompts_frame, "set_prompts")
        self.info_mgr.register(self.starter_settings, "set_starter")
        self.info_mgr.register(self.editor_settings, "set_editor")

        # Granular Component registration (delegated to frames)
        self.app_settings.register_info(self.info_mgr)
        self.fm_settings.register_info(self.info_mgr)
        self.prompts_frame.register_info(self.info_mgr)
        self.starter_settings.register_info(self.info_mgr)
        self.editor_settings.register_info(self.info_mgr)

        self.info_mgr.register(self.info_toggle_btn, "info_toggle")

        self._position_window()
        self.deiconify()

    def _init_vars(self):
        self.vars = {
            'editor_path': StringVar(value=self.config.get('default_editor', '')),
            'scan_for_secrets': BooleanVar(value=self.config.get('scan_for_secrets', False)),
            'check_for_updates': BooleanVar(value=get_setting('AutomaticUpdates', True)),
            'enable_new_file_check': BooleanVar(value=self.config.get('enable_new_file_check', True)),
            'new_file_check_interval': StringVar(value=str(self.config.get('new_file_check_interval', 5))),
            'show_feedback_on_paste': BooleanVar(value=self.config.get('show_feedback_on_paste', True)),
            'token_count_enabled': BooleanVar(value=self.config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT)),
            'token_limit': StringVar(value=str(self.config.get('token_limit', 0) if self.config.get('token_limit', 0) != 0 else "")),
            'enable_compact_mode_on_minimize': BooleanVar(value=self.config.get('enable_compact_mode_on_minimize', True)),
            'add_all_warning_threshold': StringVar(value=str(self.config.get('add_all_warning_threshold', c.ADD_ALL_WARNING_THRESHOLD_DEFAULT))),
            'new_file_alert_threshold': StringVar(value=str(self.config.get('new_file_alert_threshold', c.NEW_FILE_ALERT_THRESHOLD_DEFAULT))),
            'default_parent_folder': StringVar(value=self.config.get('default_parent_folder', ''))
        }

    def _init_styles(self):
        apply_dark_theme(self)

    def _init_window(self):
        self.title("Settings")
        self.iconbitmap(ICON_PATH)

        # Dynamic Geometry for Boot
        initial_geom = c.SETTINGS_WINDOW_DEFAULT_GEOMETRY
        if self.parent.app_state.info_mode_active:
            match = re.match(r"(\d+)x(\d+)", initial_geom)
            if match:
                w, h = map(int, match.groups())
                initial_geom = f"{w}x{h + c.INFO_PANEL_HEIGHT}"

        self.geometry(initial_geom)
        self.minsize(c.SETTINGS_WINDOW_MIN_WIDTH, c.SETTINGS_WINDOW_MIN_HEIGHT)
        self.transient(self.parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _create_widgets(self):
        # Main container frame
        main_frame = Frame(self, bg=c.DARK_BG)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Use the reusable ScrollableFrame
        self.scroll_frame = ScrollableFrame(main_frame, bg=c.DARK_BG)
        self.scroll_frame.grid(row=0, column=0, sticky='nsew')
        content_frame = self.scroll_frame.scrollable_frame
        content_frame.config(padx=20, pady=20)

        # Instantiate and pack setting sections
        self.app_settings = ApplicationSettingsFrame(content_frame, self.vars, self.updater)
        self.app_settings.pack(fill='x', expand=True)

        self.fm_settings = FileManagerSettingsFrame(content_frame, self.vars)
        self.fm_settings.pack(fill='x', expand=True)

        self.prompts_frame = PromptsSettingsFrame(content_frame, self.config, on_toggle=self.scroll_frame._on_frame_configure)
        self.prompts_frame.pack(fill='x', expand=True)

        self.starter_settings = StarterSettingsFrame(content_frame, self.vars)
        self.starter_settings.pack(fill='x', expand=True)

        self.editor_settings = EditorSettingsFrame(content_frame, self.vars)
        self.editor_settings.pack(fill='x', expand=True)

        # Action Buttons (Outside scroll area)
        button_frame = Frame(main_frame, bg=c.DARK_BG)
        button_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 20))
        button_frame.grid_columnconfigure(1, weight=1)

        save_button = RoundedButton(button_frame, text="Save and Close", command=self.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        save_button.grid(row=0, column=2, sticky='e')

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def on_closing(self):
        self._close_and_save_geometry()

    def save_and_close(self):
        # The main config object is still the one loaded at the start
        config = self.config
        prompt_values = self.prompts_frame.get_values()

        config['default_editor'] = self.vars['editor_path'].get()
        config['scan_for_secrets'] = self.vars['scan_for_secrets'].get()
        config['enable_new_file_check'] = self.vars['enable_new_file_check'].get()
        config['token_count_enabled'] = self.vars['token_count_enabled'].get()
        config['show_feedback_on_paste'] = self.vars['show_feedback_on_paste'].get()
        config['enable_compact_mode_on_minimize'] = self.vars['enable_compact_mode_on_minimize'].get()
        config['default_parent_folder'] = self.vars['default_parent_folder'].get()
        config.update(prompt_values)

        try:
            config['new_file_check_interval'] = int(self.vars['new_file_check_interval'].get())
        except ValueError:
            config['new_file_check_interval'] = 5

        try:
            limit_val = self.vars['token_limit'].get().strip()
            config['token_limit'] = int(limit_val) if limit_val else 0
        except ValueError:
            config['token_limit'] = 0

        try:
            add_all_val = self.vars['add_all_warning_threshold'].get()
            config['add_all_warning_threshold'] = int(add_all_val) if add_all_val else c.ADD_ALL_WARNING_THRESHOLD_DEFAULT
        except ValueError:
            config['add_all_warning_threshold'] = c.ADD_ALL_WARNING_THRESHOLD_DEFAULT

        try:
            alert_val = self.vars['new_file_alert_threshold'].get()
            config['new_file_alert_threshold'] = int(alert_val) if alert_val else c.NEW_FILE_ALERT_THRESHOLD_DEFAULT
        except ValueError:
            config['new_file_alert_threshold'] = c.NEW_FILE_ALERT_THRESHOLD_DEFAULT

        save_config(config)
        save_setting('AutomaticUpdates', self.vars['check_for_updates'].get())

        if self.on_close_callback:
            self.on_close_callback()
        self._close_and_save_geometry()
```

--- End of file ---

--- File: `src/ui/filetypes_manager.py` ---

```python
import tkinter as tk
import time
import re
import json
from tkinter import Toplevel, Frame, Label, Entry, messagebox, ttk, StringVar
from ..core.utils import load_all_filetypes, save_filetypes
from ..core.paths import ICON_PATH
from .widgets.rounded_button import RoundedButton
from .. import constants as c
from .window_utils import position_window, save_window_geometry
from .tooltip import ToolTip
from .info_manager import attach_info_mode
from .assets import assets

class FiletypesManagerWindow(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.filetypes_data = load_all_filetypes()
        self.last_tree_click_time = 0
        self.tooltip_window = None

        # Window Setup
        self.title("Manage Filetypes")
        self.iconbitmap(ICON_PATH)

        # Ensure grid is used on the Toplevel so the main frame and info panel never overlap
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Dynamic Geometry for Boot
        initial_geom = c.FILETYPES_WINDOW_DEFAULT_GEOMETRY
        if self.parent.app_state.info_mode_active:
            match = re.match(r"(\d+)x(\d+)", initial_geom)
            if match:
                w, h = map(int, match.groups())
                initial_geom = f"{w}x{h + c.INFO_PANEL_HEIGHT}"

        self.geometry(initial_geom)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

        # UI Layout
        main_frame = Frame(self, padx=15, pady=15, bg=c.DARK_BG)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        Label(main_frame, text="Allowed Filetypes (double click to toggle)", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=0, column=0, sticky='w', pady=(0,5))

        tree_frame = Frame(main_frame, bg=c.DARK_BG)
        tree_frame.grid(row=1, column=0, sticky='nsew', pady=(5, 0))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Treeview Styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background=c.TEXT_INPUT_BG, foreground=c.TEXT_COLOR, fieldbackground=c.TEXT_INPUT_BG, borderwidth=0, font=c.FONT_NORMAL, rowheight=25)
        style.map("Treeview", background=[('selected', c.BTN_BLUE)], foreground=[('selected', c.BTN_BLUE_TEXT)])

        self.tree = ttk.Treeview(tree_frame, show='tree', selectmode='extended')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.config(yscrollcommand=self.tree_scroll.set)

        # Action Button Row
        action_row_frame = Frame(main_frame, bg=c.DARK_BG)
        action_row_frame.grid(row=2, column=0, sticky='ew', pady=(10, 10))
        action_row_frame.columnconfigure(1, weight=1)

        # Info Toggle: Managed by InfoManager.place
        self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")

        self.action_button = RoundedButton(action_row_frame, text="", command=self._on_action_button_click, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        self.action_button.grid(row=0, column=1, sticky='ew', padx=(10, 0))
        self.action_button_tooltip = ToolTip(self.action_button, text="", delay=500)

        # Input Section for Adding New Filetypes
        input_section_frame = Frame(main_frame, bg=c.DARK_BG)
        input_section_frame.grid(row=3, column=0, sticky='ew', pady=(15, 5))
        input_section_frame.columnconfigure(1, weight=1)

        # Row 0: Add new extension
        Label(input_section_frame, text="Add new:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.add_entry_var = StringVar()
        self.add_entry = Entry(input_section_frame, textvariable=self.add_entry_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.add_entry.grid(row=0, column=1, sticky='ew', ipady=4)
        self.add_entry_var.trace_add('write', self._update_add_button_state)

        # Row 1: Add description
        Label(input_section_frame, text="Description:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(5,0))
        self.new_desc_var = StringVar()
        self.desc_entry = Entry(input_section_frame, textvariable=self.new_desc_var, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.desc_entry.grid(row=1, column=1, sticky='ew', ipady=4, pady=(5,0))

        # Row 2: Add button, aligned to the right
        add_button_frame = Frame(input_section_frame, bg=c.DARK_BG)
        add_button_frame.grid(row=2, column=1, sticky='e', pady=(10, 0))
        self.add_button = RoundedButton(add_button_frame, text="Add", command=self.add_new_filetype, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor='hand2')
        self.add_button.pack()
        self.add_button.set_state('disabled')

        # Bindings
        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Escape>', lambda e: self.on_closing())
        self.bind('<Configure>', self._on_resize)

        # Info Mode Integration
        self.info_mgr = attach_info_mode(self, self.parent.app_state, manager_type='grid', grid_row=1, toggle_btn=self.info_toggle_btn)
        self.info_mgr.register(self.tree, "ft_list")
        self.info_mgr.register(self.action_button, "ft_action")
        self.info_mgr.register(input_section_frame, "ft_add")
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")

        self.populate_tree()
        self.on_tree_selection_change() # Initial state setup

        self._position_window()
        self.deiconify()

    def _save_changes(self):
        save_filetypes(self.filetypes_data)

    def _update_add_button_state(self, *args):
        if self.add_entry_var.get().strip():
            self.add_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.add_button.set_state('normal')
        else:
            self.add_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            self.add_button.set_state('disabled')

    def _on_resize(self, event=None):
        self.after_idle(self._manage_scrollbar)

    def _manage_scrollbar(self):
        self.update_idletasks()
        style = ttk.Style()
        try: row_height = style.lookup("Treeview", "rowheight")
        except tk.TclError: row_height = 25
        content_height = len(self.filetypes_data) * row_height
        visible_height = self.tree.winfo_height()
        if content_height > visible_height:
            if not self.tree_scroll.winfo_ismapped(): self.tree_scroll.grid(row=0, column=1, sticky='ns')
        else:
            if self.tree_scroll.winfo_ismapped(): self.tree_scroll.grid_forget()

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        save_window_geometry(self)
        self.destroy()

    def populate_tree(self):
        selection = self.tree.selection()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.filetypes_data.sort(key=lambda x: x['ext'])
        for item in self.filetypes_data:
            check_char = "☑" if item['active'] else "☐"
            display_text = f"{check_char} {item['ext']}"
            self.tree.insert('', 'end', text=display_text, iid=item['ext'])
        if selection:
            try: self.tree.selection_set(selection)
            except tk.TclError:
                pass
        self.after_idle(self._manage_scrollbar)

    def on_tree_selection_change(self, event=None):
        selection = self.tree.selection()

        if not selection:
            self.action_button.set_state('disabled')
            self.action_button.config(text="Select a Filetype")
            self.action_button_tooltip.text = ""
            return

        selected_items = [item for item in self.filetypes_data if item['ext'] in selection]
        all_default = all(item.get('default', False) for item in selected_items)
        all_custom = all(not item.get('default', False) for item in selected_items)

        if all_default:
            self.action_button.set_state('normal')
            self.action_button.config(text="Activate/Deactivate")
            self.action_button_tooltip.text = "Toggle the 'active' status for the selected default filetypes."
        elif all_custom:
            self.action_button.set_state('normal')
            self.action_button.config(text="Delete Selected")
            self.action_button_tooltip.text = ""
        else: # Mixed selection
            self.action_button.set_state('disabled')
            self.action_button.config(text="Action")
            self.action_button_tooltip.text = "Cannot perform action on a mixed selection of default and custom filetypes."

    def handle_tree_click(self, event):
        current_time = time.time()
        time_diff = current_time - self.last_tree_click_time
        self.last_tree_click_time = current_time
        if time_diff < c.DOUBLE_CLICK_INTERVAL_SECONDS:
            self.toggle_active_state_for_selected()
            self.last_tree_click_time = 0

    def _on_action_button_click(self):
        button_text = self.action_button.text
        if button_text == "Delete Selected":
            self.delete_selected_filetype()
        elif button_text == "Activate/Deactivate":
            self.toggle_active_state_for_selected()

    def toggle_active_state_for_selected(self):
        selection = self.tree.selection()
        if not selection: return
        for item_iid in selection:
            for item in self.filetypes_data:
                if item['ext'] == item_iid:
                    item['active'] = not item['active']
                    break
        self.populate_tree()
        self._save_changes()

    def add_new_filetype(self):
        new_ext = self.add_entry.get().strip().lower()
        new_desc = self.new_desc_var.get().strip()

        if not new_ext:
            messagebox.showwarning("Input Error", "Extension or filename cannot be empty.", parent=self)
            return
        if re.search(r'[\\/*?:"<>|]', new_ext):
            messagebox.showwarning("Invalid Characters", "Extensions or filenames cannot contain \\ / * ? : \" < > |", parent=self)
            return
        if any(item['ext'] == new_ext for item in self.filetypes_data):
            messagebox.showwarning("Duplicate", f"The entry '{new_ext}' already exists.", parent=self)
            return

        self.filetypes_data.append({"ext": new_ext, "active": True, "description": new_desc, "default": False})
        self.add_entry.delete(0, 'end')
        self.new_desc_var.set("")
        self.populate_tree()
        self._save_changes()

    def delete_selected_filetype(self):
        selected_iids = self.tree.selection()
        if not selected_iids: return

        for iid in selected_iids:
            for item in self.filetypes_data:
                if item['ext'] == iid and item.get('default', False):
                    # This check is redundant due to button state logic but is a good safeguard
                    messagebox.showwarning("Cannot Delete", f"'{iid}' is a default filetype and cannot be deleted.", parent=self)
                    return

        self.filetypes_data = [item for item in self.filetypes_data if item['ext'] not in selected_iids]
        self.populate_tree()
        self.on_tree_selection_change()
        self._save_changes()

    def on_closing(self):
        if self.on_close_callback:
            self.on_close_callback()
        self._close_and_save_geometry()

    def _on_tree_motion(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            for item in self.filetypes_data:
                if item['ext'] == item_id:
                    desc = item.get('description', '')
                    if desc:
                        self._show_tooltip(event.x_root + 15, event.y_root + 10, desc)
                    else:
                        self._hide_tooltip()
                    return
        self._hide_tooltip()

    def _on_tree_leave(self, event):
        self._hide_tooltip()

    def _show_tooltip(self, x, y, text):
        self._hide_tooltip()
        self.tooltip_window = Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=text, justify='left', background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1, font=c.FONT_TOOLTIP, padx=4, pady=2)
        label.pack()

    def _hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
```

--- End of file ---

--- File: `src/ui/file_manager/data_controller.py` ---

```python
import os
from ...core.utils import get_file_hash, get_token_count_for_text
from ... import constants as c

class FileManagerDataController:
    def __init__(self, window):
        self.window = window

    def validate_and_update_cache(self):
        cache_was_updated = False
        for file_info in self.window.project_config.selected_files:
            path = file_info.get('path')
            if not path: continue
            full_path = os.path.join(self.window.base_dir, path)
            if self._needs_recalculation(file_info, full_path):
                self._recalculate_stats(file_info, full_path)
                cache_was_updated = True
        if cache_was_updated:
            self.window.project_config.save()
            self.window.status_var.set("File cache updated for modified files.")

    def _needs_recalculation(self, file_info, full_path):
        if 'tokens' not in file_info or 'lines' not in file_info:
            return True
        if self.window.token_count_enabled and file_info.get('tokens', -1) == 0:
            try:
                if os.path.getsize(full_path) > 0: return True
            except OSError: return False
        try:
            current_mtime = os.path.getmtime(full_path)
            if current_mtime != file_info.get('mtime'): return True
            current_hash = get_file_hash(full_path)
            if current_hash is not None and current_hash != file_info.get('hash'): return True
        except OSError:
            return False
        return False

    def _recalculate_stats(self, file_info, full_path):
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            file_info['mtime'] = os.path.getmtime(full_path)
            file_info['hash'] = get_file_hash(full_path)
            if self.window.token_count_enabled:
                file_info['tokens'] = get_token_count_for_text(content)
                file_info['lines'] = content.count('\n') + 1
            else:
                file_info['tokens'], file_info['lines'] = 0, 0
        except (OSError, IOError):
            file_info['tokens'], file_info['lines'] = -1, -1

    def run_token_recalculation(self):
        if self.window.token_count_enabled:
            total_tokens = sum(f.get('tokens', 0) for f in self.window.selection_handler.ordered_selection)
            self._update_title(total_tokens)
        else:
            self._update_title(None)

    def _update_title(self, total_tokens):
        num_files = len(self.window.selection_handler.ordered_selection)
        file_text = "files" if num_files != 1 else "file"
        details_text = f"({num_files} {file_text} selected)"
        label_fg = c.TEXT_SUBTLE_COLOR
        tooltip_text = ""

        if total_tokens is not None:
            self.window.current_total_tokens = total_tokens
            if total_tokens >= 0:
                formatted_tokens = f"{total_tokens:,}".replace(',', '.')
                details_text = f"({num_files} {file_text} selected, {formatted_tokens} tokens)"

                # Check thresholds
                token_limit = self.window.app_state.config.get('token_limit', 0)
                if token_limit > 0 and total_tokens > token_limit:
                    label_fg = c.WARN
                    tooltip_text = f"Token limit exceeded! (Limit: {token_limit:,})"
            else:
                details_text = f"({num_files} {file_text} selected, token count error)"
        else:
            self.window.current_total_tokens = 0

        self.window.merge_order_details_label.config(text=details_text, fg=label_fg)
        if hasattr(self.window, 'token_count_tooltip'):
            self.window.token_count_tooltip.text = tooltip_text
```

--- End of file ---

--- File: `src/ui/file_manager/selection_data_manager.py` ---

```python
import os
from tkinter import messagebox
from ...core.utils import get_file_hash, get_token_count_for_text

class SelectionDataManager:
    def __init__(self, base_dir, token_count_enabled, parent_for_errors):
        self.base_dir = base_dir
        self.token_count_enabled = token_count_enabled
        self.parent = parent_for_errors
        self.ordered_selection = []

    def _calculate_stats_for_file(self, path):
        """Reads a file and returns its stats, or None on error."""
        full_path = os.path.join(self.base_dir, path)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            mtime = os.path.getmtime(full_path)
            file_hash = get_file_hash(full_path)

            if self.token_count_enabled:
                tokens = get_token_count_for_text(content)
                lines = content.count('\n') + 1
            else:
                tokens, lines = 0, 0

            if file_hash is not None:
                return {'path': path, 'mtime': mtime, 'hash': file_hash, 'tokens': tokens, 'lines': lines}
        except OSError:
            messagebox.showerror("Error", f"Could not access file: {path}", parent=self.parent)
        return None

    def set_initial_selection(self, selection_list):
        self.ordered_selection = list(selection_list)

    def toggle_file(self, path):
        """Adds or removes a file from the selection model"""
        current_selection_paths = {f['path'] for f in self.ordered_selection}
        if path in current_selection_paths:
            self.ordered_selection = [f for f in self.ordered_selection if f['path'] != path]
        else:
            new_entry = self._calculate_stats_for_file(path)
            if new_entry:
                self.ordered_selection.append(new_entry)

    def add_files(self, paths_to_add):
        current_selection_paths = {f['path'] for f in self.ordered_selection}
        for path in paths_to_add:
            if path not in current_selection_paths:
                new_entry = self._calculate_stats_for_file(path)
                if new_entry:
                    self.ordered_selection.append(new_entry)

    def remove_files(self, paths_to_remove):
        """Removes a list of files from the selection based on their paths."""
        paths_set = set(paths_to_remove)
        self.ordered_selection = [f for f in self.ordered_selection if f['path'] not in paths_set]

    def remove_all(self):
        self.ordered_selection.clear()

    def remove_by_indices(self, indices):
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]

    def reorder_move_to_top(self, indices):
        moved_items = [self.ordered_selection[i] for i in indices]
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]
        self.ordered_selection = moved_items + self.ordered_selection
        return range(len(moved_items))

    def reorder_move_up(self, indices):
        if not indices or indices[0] == 0:
            return None
        moved_items = [self.ordered_selection[i] for i in indices]
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]
        insert_index = indices[0] - 1
        for i, item in enumerate(moved_items):
            self.ordered_selection.insert(insert_index + i, item)
        return range(insert_index, insert_index + len(moved_items))

    def reorder_move_down(self, indices):
        if not indices or indices[-1] >= len(self.ordered_selection) - 1:
            return None
        moved_items = [self.ordered_selection[i] for i in indices]
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]
        insert_index = indices[0] + 1
        for i, item in enumerate(moved_items):
            self.ordered_selection.insert(insert_index + i, item)
        return range(insert_index, insert_index + len(moved_items))

    def reorder_move_to_bottom(self, indices):
        moved_items = [self.ordered_selection[i] for i in indices]
        for index in sorted(indices, reverse=True):
            del self.ordered_selection[index]
        new_start_index = len(self.ordered_selection)
        self.ordered_selection.extend(moved_items)
        return range(new_start_index, len(self.ordered_selection))
```

--- End of file ---

--- File: `src/ui/file_manager/file_tree_builder.py` ---

```python
import os
from ...core.utils import is_ignored
from ... import constants as c

def build_file_tree_data(base_dir, file_extensions, gitignore_patterns, filter_text="", is_extension_filter_active=True, selected_file_paths=None, is_gitignore_filter_active=True):
    """
    Scans the file system respecting .gitignore and returns a data structure
    representing the relevant files and directories for the tree view.
    Ensures that files in 'selected_file_paths' always bypass filters to remain visible.
    """
    extensions = {ext for ext in file_extensions if ext.startswith('.')}
    exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}
    filter_text_lower = filter_text.lower()

    if selected_file_paths is None:
        selected_file_paths = set()

    def is_path_or_child_selected(rel_path):
        """Checks if this path or any path deeper than it is in the Merge Order."""
        if rel_path in selected_file_paths:
            return True
        prefix = rel_path + "/"
        return any(p.startswith(prefix) for p in selected_file_paths)

    def should_be_ignored(path, rel_path):
        """Determines if a directory should be entered or ignored by gitignore."""
        if not is_gitignore_filter_active:
            return False
        # If the directory itself, or any file within it, is selected, we MUST NOT ignore it.
        if is_path_or_child_selected(rel_path):
            return False
        return is_ignored(path, base_dir, gitignore_patterns)

    def is_file_visible(rel_path, file_name):
        """Helper to determine if a file should be visible based on the filter state."""
        # Files in the Merge Order are ALWAYS visible regardless of filters.
        if rel_path in selected_file_paths:
            return True

        if is_extension_filter_active:
            file_name_lower = file_name.lower()
            file_ext = os.path.splitext(file_name_lower)[1]
            if not (file_ext in extensions or file_name_lower in exact_filenames):
                return False

        return True

    if not filter_text_lower:
        # Original, unfiltered logic for performance when not searching
        def _has_relevant_files(path, rel_path):
            try:
                for entry in os.scandir(path):
                    e_rel = os.path.relpath(entry.path, base_dir).replace('\\', '/')
                    if should_be_ignored(entry.path, e_rel) or entry.name.lower() in c.SPECIAL_FILES_TO_IGNORE:
                        continue
                    if entry.is_dir():
                        if _has_relevant_files(entry.path, e_rel): return True
                    elif entry.is_file():
                        if is_file_visible(e_rel, entry.name):
                            return True
            except OSError: return False
            return False

        def _build_nodes_unfiltered(current_path):
            nodes = []
            try: entries = sorted(os.scandir(current_path), key=lambda e: (e.is_file(), e.name.lower()))
            except OSError: return []

            for entry in entries:
                e_rel = os.path.relpath(entry.path, base_dir).replace('\\', '/')
                if should_be_ignored(entry.path, e_rel) or entry.name.lower() in c.SPECIAL_FILES_TO_IGNORE: continue

                if entry.is_dir():
                    if _has_relevant_files(entry.path, e_rel):
                        nodes.append({'name': entry.name, 'path': e_rel, 'type': 'dir', 'children': _build_nodes_unfiltered(entry.path)})
                elif entry.is_file():
                    if is_file_visible(e_rel, entry.name):
                        nodes.append({'name': entry.name, 'path': e_rel, 'type': 'file'})
            return nodes
        return _build_nodes_unfiltered(base_dir)

    # New filtered logic
    def _build_nodes_filtered(current_path):
        nodes = []
        try: entries = sorted(os.scandir(current_path), key=lambda e: (e.is_file(), e.name.lower()))
        except OSError: return [], False

        has_match_in_subtree = False
        for entry in entries:
            e_rel = os.path.relpath(entry.path, base_dir).replace('\\', '/')
            if should_be_ignored(entry.path, e_rel) or entry.name.lower() in c.SPECIAL_FILES_TO_IGNORE: continue

            name_matches_filter = filter_text_lower in entry.name.lower()

            if entry.is_dir():
                child_nodes, child_has_match = _build_nodes_filtered(entry.path)
                if name_matches_filter or child_has_match:
                    has_match_in_subtree = True
                    nodes.append({'name': entry.name, 'path': e_rel, 'type': 'dir', 'children': child_nodes})
            elif entry.is_file():
                if is_file_visible(e_rel, entry.name) and name_matches_filter:
                    has_match_in_subtree = True
                    nodes.append({'name': entry.name, 'path': e_rel, 'type': 'file'})
        return nodes, has_match_in_subtree

    result_nodes, _ = _build_nodes_filtered(base_dir)
    return result_nodes
```

--- End of file ---

--- File: `src/ui/file_manager/selection_list_ui.py` ---

```python
import os
from ... import constants as c
from ...core.utils import is_ignored

class SelectionListUI:
    def __init__(self, list_widget, token_count_enabled):
        self.listbox = list_widget
        self.token_count_enabled = token_count_enabled
        self.show_full_paths = False

    def _interpolate_color(self, color1_hex, color2_hex, factor):
        """Linearly interpolates between two hex colors based on a factor from 0.0 to 1.0."""
        r1, g1, b1 = tuple(int(color1_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(color2_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        r = int(r1 + (r2 - r1) * factor); g = int(g1 + (g2 - g1) * factor); b = int(b1 + (b2 - b1) * factor)
        return f'#{r:02x}{g:02x}{b:02x}'

    def _get_color_for_token_count(self, count, min_val, max_val):
        """Calculates a color from a 5-stop gradient based on the token count's position in the range."""
        if min_val >= max_val: return c.TEXT_SUBTLE_COLOR
        p = (count - min_val) / (max_val - min_val)
        colors = [c.TEXT_SUBTLE_COLOR, c.TEXT_SUBTLE_COLOR, c.NOTE, c.ATTENTION, c.WARN]
        if p <= 0: return colors[0]
        if p >= 1: return colors[-1]
        scaled_p = p * (len(colors) - 1)
        idx1 = int(scaled_p)
        idx2 = min(idx1 + 1, len(colors) - 1)
        local_p = scaled_p - idx1
        return self._interpolate_color(colors[idx1], colors[idx2], local_p)

    def toggle_full_path_view(self):
        """Toggles the display of full paths."""
        self.show_full_paths = not self.show_full_paths
        return self.show_full_paths

    def update_list_display(self, ordered_selection, base_dir, file_extensions, gitignore_patterns, is_reorder=False, filter_text="", animate=False):
        """Refreshes the merge order list."""
        items_to_display = ordered_selection
        if filter_text:
            items_to_display = [item for item in ordered_selection if filter_text in item['path'].lower()]

        # Prepare filter logic data
        extensions = {ext for ext in file_extensions if ext.startswith('.')}
        exact_filenames = {ext for ext in file_extensions if not ext.startswith('.')}

        min_tokens, max_tokens = 0, c.TOKEN_COLOR_RANGE_MIN_MAX
        if self.token_count_enabled:
            # Filter out ignored files when calculating the range to prevent large files from skewing the gradient
            token_counts = [
                f.get('tokens', 0) for f in items_to_display
                if f.get('tokens', -1) >= 0 and not f.get('ignore_tokens', False)
            ]
            if token_counts:
                min_tokens = min(token_counts)
                max_tokens = max(max(token_counts), c.TOKEN_COLOR_RANGE_MIN_MAX)

        display_items = []
        for file_info in items_to_display:
            path = file_info['path']
            file_name = os.path.basename(path)
            display_text = path if self.show_full_paths else file_name

            # Filter Check Logic
            file_name_lower = file_name.lower()
            file_ext = os.path.splitext(file_name_lower)[1]

            is_valid_ext = file_ext in extensions or file_name_lower in exact_filenames
            is_git_ignored = is_ignored(os.path.join(base_dir, path), base_dir, gitignore_patterns)

            # If it's ignored by Git OR has an unsupported extension, it's "filtered"
            is_filtered = is_git_ignored or (not is_valid_ext)
            left_col_color = c.TEXT_FILTERED_COLOR if is_filtered else c.TEXT_COLOR

            right_col_text, right_col_color = "", c.TEXT_SUBTLE_COLOR
            if self.token_count_enabled:
                token_count = file_info.get('tokens', -1)
                is_ignored_token = file_info.get('ignore_tokens', False)

                if token_count >= 0:
                    if is_ignored_token:
                        right_col_text = f"[{token_count}]"
                        right_col_color = "#666666"
                    else:
                        right_col_text = str(token_count)
                        right_col_color = self._get_color_for_token_count(token_count, min_tokens, max_tokens)
                else:
                    right_col_text = "?"

            display_items.append({
                'left': display_text,
                'left_fg': left_col_color,
                'right': right_col_text,
                'right_fg': right_col_color,
                'data': path
            })

        if is_reorder:
            self.listbox.reorder_and_update(display_items)
        else:
            self.listbox.set_items(display_items)

        if animate:
            self.listbox.animate_pulse()
```

--- End of file ---

--- File: `src/ui/file_manager/ui_controller.py` ---

```python
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, Toplevel, Label
from ... import constants as c
from ..assets import assets

class FileManagerUIController:
    def __init__(self, window):
        self.window = window
        self.active_folder_icon_label = None
        self.folder_tooltip_window = None
        self.folder_tooltip_label = None
        self.folder_tooltip_job = None
        self.hovered_folder_id = None

    def _is_click_in_widget(self, event):
        """Helper to check if the release event occurred inside the widget."""
        if event is None: return True
        return 0 <= event.x <= event.widget.winfo_width() and 0 <= event.y <= event.widget.winfo_height()

    def clear_filter(self, event=None):
        if not self._is_click_in_widget(event): return
        self.window.filter_text.set("")
        self.window.focus_force()

    def apply_filter(self, *args):
        filter_query = self.window.filter_text.get().lower()
        is_active = bool(filter_query)

        color = c.FILTER_ACTIVE_BORDER if is_active else c.TEXT_INPUT_BG
        self.window.filter_input_frame.config(highlightbackground=color, highlightcolor=color)

        if is_active:
            self.window.clear_filter_button.place(relx=1.0, rely=0.5, anchor='e', x=-5)
        else:
            self.window.clear_filter_button.place_forget()

        self.window.selection_handler.set_filtered_state(is_active)
        self.window.populate_tree(filter_query)
        self.window.selection_handler.filter_list(filter_query)

    def _show_icon_for_item(self, item_id):
        if not item_id:
            self.on_tree_leave()
            return

        item_info = self.window.item_map.get(item_id, {})
        if item_info.get('type') != 'file':
            self.on_tree_leave()
            return

        bbox = self.window.tree.bbox(item_id)
        if not bbox:
            self.on_tree_leave()
            return

        # Determine the correct state and select the pre-built label
        current_state = 'default'
        tags = self.window.tree.item(item_id, 'tags')
        if item_id in self.window.tree.selection():
            current_state = 'selected'
        elif 'subtle_highlight' in tags:
            current_state = 'highlight'

        label_to_show = self.window.folder_icon_labels[current_state]

        # Swap the visible label only if it has changed
        if self.active_folder_icon_label is not label_to_show:
            if self.active_folder_icon_label:
                self.active_folder_icon_label.place_forget()
            self.active_folder_icon_label = label_to_show

        # Calculate position and place the icon
        tree_width = self.window.tree.winfo_width()
        icon_width = assets.folder_reveal_icon.width()
        icon_height = assets.folder_reveal_icon.height()
        icon_x = tree_width - icon_width - 8
        icon_y = bbox[1] + (bbox[3] // 2) - (icon_height // 2)

        self.active_folder_icon_label.place(x=icon_x, y=icon_y)
        self.window.hovered_file_path = item_info['path']

    def refresh_hover_icon(self):
        if self.window.hovered_file_path:
            item_id = self.window.path_to_item_id.get(self.window.hovered_file_path)
            if item_id:
                self._show_icon_for_item(item_id)

    def on_tree_motion(self, event):
        item_id = self.window.tree.identify_row(event.y)
        self._show_icon_for_item(item_id)

        # Cancel any pending job and hide the current tooltip.
        if self.folder_tooltip_job:
            self.window.after_cancel(self.folder_tooltip_job)
            self.folder_tooltip_job = None
        self._hide_folder_tooltip()

        self.hovered_folder_id = None

        if item_id:
            item_info = self.window.item_map.get(item_id, {})

            # Special Tooltip for Normally Filtered Files
            if 'hidden_reason' in item_info:
                 self.folder_tooltip_job = self.window.after(400, lambda e=event, msg=item_info['hidden_reason']: self._show_generic_tooltip(e, msg))
            # Standard Folder Tooltip
            elif item_info.get('type') == 'dir':
                self.hovered_folder_id = item_id
                self.folder_tooltip_job = self.window.after(500, lambda e=event, iid=item_id: self._show_folder_tooltip(e, iid))

    def on_tree_leave(self, event=None):
        if self.active_folder_icon_label:
            self.active_folder_icon_label.place_forget()
            self.active_folder_icon_label = None
        self.window.hovered_file_path = None

        if self.folder_tooltip_job:
            self.window.after_cancel(self.folder_tooltip_job)
            self.folder_tooltip_job = None
        self._hide_folder_tooltip()
        self.hovered_folder_id = None

    def _get_folder_tooltip_text(self, item_id):
        """Calculates the dynamic text for the folder tooltip."""
        files_in_subtree = self.window.tree_handler._get_all_files_in_subtree(item_id)
        if not files_in_subtree:
            return None

        current_selection_paths = {f['path'] for f in self.window.selection_handler.ordered_selection}
        subtree_paths_set = set(files_in_subtree)
        is_fully_selected = subtree_paths_set.issubset(current_selection_paths)

        action_text = "remove" if is_fully_selected else "add"
        return f"Double-click to {action_text} all files in this folder"

    def _show_generic_tooltip(self, event, message):
        """Shows a simple tooltip with a custom message."""
        self._hide_folder_tooltip()
        x, y = event.x_root + 15, event.y_root + 10
        self.folder_tooltip_window = Toplevel(self.window)
        self.folder_tooltip_window.wm_overrideredirect(True)
        self.folder_tooltip_window.wm_geometry(f"+{x}+{y}")
        self.folder_tooltip_label = Label(self.folder_tooltip_window, text=message, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=c.FONT_TOOLTIP)
        self.folder_tooltip_label.pack(ipadx=4, ipady=2)

    def _show_folder_tooltip(self, event, item_id):
        self._hide_folder_tooltip()

        text = self._get_folder_tooltip_text(item_id)
        if not text:
            return

        x, y = event.x_root + 15, event.y_root + 10
        self.folder_tooltip_window = Toplevel(self.window)
        self.folder_tooltip_window.wm_overrideredirect(True)
        self.folder_tooltip_window.wm_geometry(f"+{x}+{y}")
        self.folder_tooltip_label = Label(self.folder_tooltip_window, text=text, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=c.FONT_TOOLTIP)
        self.folder_tooltip_label.pack(ipadx=4, ipady=2)

    def _hide_folder_tooltip(self):
        if self.folder_tooltip_window:
            self.folder_tooltip_window.destroy()
        self.folder_tooltip_window = None
        self.folder_tooltip_label = None

    def update_active_folder_tooltip(self):
        """Refreshes the folder tooltip text if it's currently visible."""
        if self.hovered_folder_id and self.folder_tooltip_window and self.folder_tooltip_label:
            new_text = self._get_folder_tooltip_text(self.hovered_folder_id)
            if new_text:
                self.folder_tooltip_label.config(text=new_text)
            else:
                self._hide_folder_tooltip()

    def on_folder_icon_click(self, event=None):
        if not self._is_click_in_widget(event): return
        if self.window.hovered_file_path:
            self._open_file_location(self.window.hovered_file_path)

    def _open_file_location(self, relative_path):
        full_path = os.path.join(self.window.base_dir, relative_path)
        if not os.path.exists(full_path):
            messagebox.showwarning("File Not Found", f"The file '{relative_path}' could not be found.", parent=self.window)
            return
        try:
            if sys.platform == "win32":
                subprocess.run(['explorer', '/select,', os.path.normpath(full_path)])
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", full_path])
            else:
                dir_path = os.path.dirname(full_path)
                if os.path.isdir(dir_path):
                    subprocess.run(["xdg-open", dir_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file location: {e}", parent=self.window)

    def toggle_full_path_view(self):
        self.window.full_paths_visible = not self.window.full_paths_visible
        self.window.selection_handler.toggle_full_path_view()

        def adjust_sash():
            try:
                self.window.update_idletasks()
                total_width = self.window.paned_window.winfo_width()
                if total_width <= 1: return

                if self.window.full_paths_visible:
                    self.window.sash_pos_normal = self.window.paned_window.sashpos(0)
                    sash_position = int(total_width * 0.4)
                    self.window.toggle_paths_button.config(image=assets.paths_icon_active)
                else:
                    sash_position = self.window.sash_pos_normal or (total_width // 2)
                    self.window.toggle_paths_button.config(image=assets.paths_icon)
                self.window.paned_window.sashpos(0, sash_position)
                self.window._update_sash_cover_position()
            except tk.TclError: pass
        self.window.after(10, adjust_sash)

    def toggle_gitignore_filter(self):
        """Toggles the .gitignore file filter on and off."""
        self.window.is_gitignore_filter_active = not self.window.is_gitignore_filter_active

        self.window.gitignore_button_tooltip.cancel_show()
        self.window.gitignore_button_tooltip.hide_tooltip()

        if self.window.is_gitignore_filter_active:
            self.window.toggle_gitignore_button.config(image=assets.git_files_icon)
            self.window.gitignore_button_tooltip.text = ".gitignore filter is ON. Click to show all files."
        else:
            self.window.toggle_gitignore_button.config(image=assets.git_files_icon_active)
            self.window.gitignore_button_tooltip.text = ".gitignore filter is OFF. Click to hide ignored files."

        self.window.gitignore_button_tooltip.show_tooltip()
        self.window.populate_tree(self.window.filter_text.get())

    def toggle_extension_filter(self):
        """Toggles the filetype extension filter on and off."""
        self.window.is_extension_filter_active = not self.window.is_extension_filter_active

        self.window.filter_button_tooltip.cancel_show()
        self.window.filter_button_tooltip.hide_tooltip()

        if self.window.is_extension_filter_active:
            self.window.toggle_filter_button.config(image=assets.filter_icon)
            self.window.filter_button_tooltip.text = "Filetype filter is ON. Click to show all files."
        else:
            self.window.toggle_filter_button.config(image=assets.filter_icon_active)
            self.window.filter_button_tooltip.text = "Filetype filter is OFF. Click to show only allowed filetypes."

        # Show the new tooltip immediately. It will be hidden automatically on <Leave>.
        self.window.filter_button_tooltip.show_tooltip()

        # Repopulate tree using the current text filter value
        self.window.populate_tree(self.window.filter_text.get())

    def expand_and_scroll_to_new_files(self):
        """Expands parent directories of newly detected files and scrolls to the first one."""
        if not self.window.newly_detected_files:
            return

        # Expand all parent directories for each new file.
        for file_path in self.window.newly_detected_files:
            item_id = self.window.path_to_item_id.get(file_path)
            if item_id:
                parent_id = self.window.tree.parent(item_id)
                while parent_id:
                    self.window.tree.item(parent_id, open=True)
                    parent_id = self.window.tree.parent(parent_id)

        # Scroll to the first new file alphabetically.
        first_file_path = sorted(self.window.newly_detected_files)[0]
        first_item_id = self.window.path_to_item_id.get(first_file_path)

        if first_item_id:
            # Use 'after' to give the UI time to update with the new expansions
            # before trying to scroll. This prevents a race condition.
            def scroll_if_ready():
                try:
                    self.window.tree.see(first_item_id)
                except tk.TclError:
                    # Window might have been closed during the delay
                    pass
            self.window.after(50, scroll_if_ready)
```

--- End of file ---

--- File: `src/ui/file_manager/file_tree_handler.py` ---

```python
import os
import time
from ... import constants as c
from ...core.utils import is_ignored

class FileTreeHandler:
    """
    Manages the file tree view in the List Editor, including population,
    event handling, and visual state.
    """
    def __init__(self, parent, tree_widget, action_button, item_map, path_to_item_id, is_selected_callback, on_toggle_callback):
        self.parent = parent
        self.tree = tree_widget
        self.action_button = action_button
        self.item_map = item_map
        self.path_to_item_id = path_to_item_id
        self.is_selected = is_selected_callback
        self.on_toggle = on_toggle_callback

        # Bind events
        self.tree.bind('<Button-1>', self.handle_tree_click)
        self.tree.bind('<Double-1>', self.handle_double_click)
        self.tree.bind('<Return>', self.toggle_selection_for_selected) # For accessibility
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection_change)
        self.tree.bind("<Button-1>", self.handle_tree_deselection_click, add='+')

    def get_expanded_dirs(self):
        """Returns a list of currently expanded directories"""
        return [
            info['path'] for item_id, info in self.item_map.items()
            if info.get('type') == 'dir' and self.tree.item(item_id, 'open')
        ]

    def update_item_visuals(self, item_id, current_selection_paths=None):
        """
        Updates the text (checkbox) and visual style of a tree item.
        Applies 'filtered_file_highlight' if a file is normally hidden by filters.
        Applies 'selected_grey' tag if:
        1. A file is selected OR is in the ignore list (e.g. __init__.py).
        2. A folder has all its 'relevant' files selected (ignoring files in the list).
        """
        item_info = self.item_map.get(item_id, {})
        item_type = item_info.get('type')
        if not item_type: return

        if current_selection_paths is None:
            # Create the set for O(1) lookup
            current_selection_paths = {f['path'] for f in self.parent.selection_handler.ordered_selection}

        tags = list(self.tree.item(item_id, 'tags'))

        # Clear existing visual tags to start fresh
        for t in ['selected_grey', 'filtered_file_highlight']:
            if t in tags: tags.remove(t)

        if item_type == 'file':
            path = item_info['path']
            filename = os.path.basename(path)
            is_checked = path in current_selection_paths

            check_char = "☑" if is_checked else "☐"
            self.tree.item(item_id, text=f"{check_char} {filename}")

            # Check Normal Filter Status
            hidden_reasons = []

            # Check Gitignore
            if is_ignored(os.path.join(self.parent.base_dir, path), self.parent.base_dir, self.parent.gitignore_patterns):
                hidden_reasons.append("the .gitignore filter")

            # Check Extension Filter
            file_name_lower = filename.lower()
            file_ext = os.path.splitext(file_name_lower)[1]
            extensions = {ext for ext in self.parent.file_extensions if ext.startswith('.')}
            exact_filenames = {ext for ext in self.parent.file_extensions if not ext.startswith('.')}

            if not (file_ext in extensions or file_name_lower in exact_filenames):
                hidden_reasons.append("the filetype filter")

            if hidden_reasons:
                tags.append('filtered_file_highlight')
                reason_str = " and ".join(hidden_reasons)
                item_info['hidden_reason'] = f"This file would normally be hidden by {reason_str}."
            else:
                item_info.pop('hidden_reason', None)
                # Apply grey out only if it's NOT a filtered highlight
                if is_checked or filename in c.FILES_TO_IGNORE_FOR_VISUAL_COMPLETENESS:
                    tags.append('selected_grey')

        elif item_type == 'dir':
            files_in_subtree = self._get_all_files_in_subtree(item_id)

            if not files_in_subtree:
                # Folder contains no files (empty or only dirs).
                # Consider it "complete" (grey) so it doesn't draw attention.
                tags.append('selected_grey')
            else:
                # Filter down to only files that actually matter for "completeness"
                relevant_files = [
                    p for p in files_in_subtree
                    if os.path.basename(p) not in c.FILES_TO_IGNORE_FOR_VISUAL_COMPLETENESS
                ]

                if not relevant_files:
                    # Folder contains ONLY ignored files (e.g. only __init__.py).
                    # It is visually complete.
                    tags.append('selected_grey')
                else:
                    # Folder is grey only if ALL relevant files are selected.
                    if all(p in current_selection_paths for p in relevant_files):
                        tags.append('selected_grey')

        self.tree.item(item_id, tags=tags)

    def update_all_visuals(self):
        """Iterates through all items in the tree and updates their visual state."""
        # Calculate selection set once for performance
        current_selection_paths = {f['path'] for f in self.parent.selection_handler.ordered_selection}
        for item_id in self.item_map:
            self.update_item_visuals(item_id, current_selection_paths)

    def handle_tree_deselection_click(self, event):
        """Deselects a tree item if a click occurs in an empty area"""
        if not self.tree.identify_row(event.y) and self.tree.selection():
            self.tree.selection_set("")

    def on_tree_selection_change(self, event=None):
        """Callback for when the tree selection changes"""
        self.parent.handle_tree_select(event)

    def update_action_button_state(self):
        """Updates the state and text of the button under the treeview based on multi-selection."""
        selection = self.tree.selection()
        if not selection:
            self.action_button.config(state='disabled', text="Add to List")
            return

        selected_files = [
            self.item_map.get(item_id) for item_id in selection
            if self.item_map.get(item_id, {}).get('type') == 'file'
        ]

        if not selected_files:
            self.action_button.config(state='disabled', text="Add to List")
            return

        self.action_button.config(state='normal')

        paths = [f['path'] for f in selected_files]
        selection_states = [self.is_selected(path) for path in paths]

        if all(selection_states):
            self.action_button.config(text="Remove from List")
        elif not any(selection_states):
            self.action_button.config(text="Add to List")
        else:
            self.action_button.config(text="Toggle List Status")

    def handle_tree_click(self, event):
        """Standard click handler to manage focus and manual click tracking."""
        # Selection is handled natively by the widget. We just ensure it has focus.
        self.tree.focus_set()

    def handle_double_click(self, event):
        """
        Handles native double-click event. Toggles files or folders
        and blocks the default tree expansion/collapse behavior.
        """
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self._toggle_item(item_id)
        return "break"

    def _get_all_files_in_subtree(self, parent_id):
        """Recursively collects all file paths under a given directory node in the tree."""
        files = []
        for child_id in self.tree.get_children(parent_id):
            child_info = self.item_map.get(child_id, {})
            if child_info.get('type') == 'file':
                files.append(child_info['path'])
            elif child_info.get('type') == 'dir':
                files.extend(self._get_all_files_in_subtree(child_id))
        return files

    def toggle_selection_for_selected(self, event=None):
        """Adds or removes the selected file(s) from the merge list via the callback"""
        selection = self.tree.selection()
        if not selection:
            return "break"

        for item_id in selection:
            self._toggle_item(item_id)

        return "break"

    def get_all_file_paths_in_tree_order(self):
        """Returns a flat list of all file paths in the order they appear in the tree"""
        all_tree_files = []
        def _traverse(parent_id):
            for item_id in self.tree.get_children(parent_id):
                item_info = self.item_map.get(item_id, {})
                if item_info.get('type') == 'file':
                    all_tree_files.append(item_info['path'])
                elif item_info.get('type') == 'dir':
                    _traverse(item_id)
        _traverse('')
        return all_tree_files

    def _toggle_item(self, item_id):
        """Toggles a single file or an entire folder's contents."""
        if not item_id:
            return
        item_info = self.item_map.get(item_id, {})
        item_type = item_info.get('type')

        if item_type == 'file':
            self.on_toggle(item_info['path'])
        elif item_type == 'dir':
            files_in_subtree = self._get_all_files_in_subtree(item_id)
            if not files_in_subtree:
                return

            current_selection_paths = {f['path'] for f in self.parent.selection_handler.ordered_selection}
            subtree_paths_set = set(files_in_subtree)

            # If all files in the folder are already selected, remove them. Otherwise, add them.
            if subtree_paths_set.issubset(current_selection_paths):
                self.parent.selection_handler.remove_files(files_in_subtree)
            else:
                # Only add files that are not already in the selection
                paths_to_add = [p for p in files_in_subtree if p not in current_selection_paths]
                self.parent.selection_handler.add_files(paths_to_add)
```

--- End of file ---

--- File: `src/ui/file_manager/selection_list_controller.py` ---

```python
import os
import sys
import subprocess
import pyperclip
from tkinter import messagebox, Toplevel, Label
from ... import constants as c
from .selection_data_manager import SelectionDataManager
from .selection_list_ui import SelectionListUI
from ...core.utils import is_ignored

class SelectionListController:
    """
    Orchestrates the data, UI, and user interactions for the 'Merge Order' list.
    """
    def __init__(self, parent, list_widget, buttons, base_dir, default_editor, on_change_callback, token_count_enabled):
        self.parent = parent
        self.listbox = list_widget
        self.buttons = buttons
        self.base_dir = base_dir
        self.default_editor = default_editor
        self.on_change = on_change_callback
        self.is_filtered = False
        self.tooltip_window = None
        self.tooltip_job = None

        self.data_manager = SelectionDataManager(base_dir, token_count_enabled, parent)
        self.ui_manager = SelectionListUI(list_widget, token_count_enabled)

        self._bind_events()

    @property
    def ordered_selection(self):
        return self.data_manager.ordered_selection

    def _bind_events(self):
        """Binds all widget events to their respective handlers."""
        self.listbox.bind_event('<<ListSelectionChanged>>', self.on_list_selection_change)
        self.listbox.bind_event('<Double-1>', self.open_selected_file)
        self.listbox.bind_event('<Motion>', self._schedule_tooltip)
        self.listbox.bind_event('<Leave>', self._hide_tooltip)
        self.listbox.bind_event('<MouseWheel>', self._on_scroll, add='+')
        self.listbox.bind_event('<Control-Button-1>', self._on_ctrl_click)
        self.listbox.bind_event('<Alt-Button-1>', self._on_alt_click)

    def _on_ctrl_click(self, event):
        """Handles Ctrl+Click events, specifically on the token count area."""
        if event.x > (self.listbox.winfo_width() - self.listbox.right_col_width):
            index = int(self.listbox.canvasy(event.y) // self.listbox.row_height)

            if 0 <= index < len(self.ordered_selection):
                path = self.ordered_selection[index].get('path')
                if path:
                    request_string = f"`{path}` is too big. Please help me split it up into multiple files. Be careful not to break any of the existing logic and functionality."
                    pyperclip.copy(request_string)
                    self.parent.status_var.set(f"Copied breakup request for '{os.path.basename(path)}'")
                    return "break"
        return None

    def _on_alt_click(self, event):
        """Handles Alt+Click events on the token count area to toggle ignored state."""
        if event.x > (self.listbox.winfo_width() - self.listbox.right_col_width):
            index = int(self.listbox.canvasy(event.y) // self.listbox.row_height)

            if 0 <= index < len(self.ordered_selection):
                item = self.ordered_selection[index]
                item['ignore_tokens'] = not item.get('ignore_tokens', False)
                self._update_and_notify()
                return "break"
        return None

    def set_initial_selection(self, selection_list):
        self.data_manager.set_initial_selection(selection_list)
        self._update_and_notify()

    def _update_and_notify(self, is_reorder=False):
        """Helper to refresh the UI display and invoke the parent callback."""
        self.ui_manager.update_list_display(
            self.ordered_selection,
            base_dir=self.base_dir,
            file_extensions=self.parent.file_extensions,
            gitignore_patterns=self.parent.gitignore_patterns,
            is_reorder=is_reorder
        )
        self.on_change()

    def toggle_file(self, path):
        self.data_manager.toggle_file(path)
        self._update_and_notify()

    def add_files(self, paths_to_add):
        self.data_manager.add_files(paths_to_add)
        self._update_and_notify()

    def remove_files(self, paths_to_remove):
        """Removes a list of files from the selection and updates the UI."""
        self.data_manager.remove_files(paths_to_remove)
        self._update_and_notify()

    def remove_all_files(self):
        self.data_manager.remove_all()
        self._update_and_notify()

    def move_to_top(self):
        indices = self.listbox.curselection()
        if not indices: return
        new_selection = self.data_manager.reorder_move_to_top(indices)
        self._update_and_notify(is_reorder=True)
        self.listbox.selection_set(new_selection.start, new_selection.stop - 1)
        self.listbox.see(new_selection.start)
        self.listbox.set_selection_anchor(new_selection.start)

    def move_up(self):
        indices = self.listbox.curselection()
        new_selection = self.data_manager.reorder_move_up(indices)
        if new_selection:
            self._update_and_notify(is_reorder=True)
            self.listbox.selection_set(new_selection.start, new_selection.stop - 1)
            self.listbox.see(new_selection.start)
            self.listbox.set_selection_anchor(new_selection.start)

    def move_down(self):
        indices = self.listbox.curselection()
        new_selection = self.data_manager.reorder_move_down(indices)
        if new_selection:
            self._update_and_notify(is_reorder=True)
            self.listbox.selection_set(new_selection.start, new_selection.stop - 1)
            self.listbox.see(new_selection.start)
            self.listbox.set_selection_anchor(new_selection.stop - 1)

    def move_to_bottom(self):
        indices = self.listbox.curselection()
        if not indices: return
        new_selection = self.data_manager.reorder_move_to_bottom(indices)
        self._update_and_notify(is_reorder=True)
        self.listbox.selection_set(new_selection.start, new_selection.stop - 1)
        self.listbox.see(new_selection.stop - 1)
        self.listbox.set_selection_anchor(new_selection.stop - 1)

    def remove_selected(self):
        indices = self.listbox.curselection()
        if not indices: return
        self.data_manager.remove_by_indices(indices)
        self._update_and_notify()

    def on_list_selection_change(self, event=None):
        self.parent.handle_merge_order_tree_select(event)

    def update_button_states(self):
        selection_exists = self.listbox.curselection()
        sort_buttons = [self.buttons['top'], self.buttons['up'], self.buttons['down'], self.buttons['bottom']]
        sort_button_state = 'disabled' if self.is_filtered else ('normal' if selection_exists else 'disabled')
        for btn in sort_buttons:
            btn.set_state(sort_button_state)
        self.buttons['remove'].set_state('normal' if selection_exists else 'disabled')

    def set_filtered_state(self, is_filtered):
        self.is_filtered = is_filtered
        self.update_button_states()

    def filter_list(self, filter_text):
        self.ui_manager.update_list_display(
            self.ordered_selection,
            base_dir=self.base_dir,
            file_extensions=self.parent.file_extensions,
            gitignore_patterns=self.parent.gitignore_patterns,
            is_reorder=False,
            filter_text=filter_text.lower()
        )

    def toggle_full_path_view(self):
        self.ui_manager.toggle_full_path_view()
        self._update_and_notify()

    def open_selected_file(self, event=None):
        indices = self.listbox.curselection()
        if not indices: return "break"
        relative_path = self.listbox.get_item_data(indices[0])
        if not relative_path: return "break"
        full_path = os.path.join(self.base_dir, relative_path)
        if not os.path.isfile(full_path):
            messagebox.showwarning("File Not Found", f"The file '{relative_path}' could not be found", parent=self.parent)
            return "break"
        try:
            if self.default_editor and os.path.isfile(self.default_editor):
                subprocess.Popen([self.default_editor, full_path])
            else:
                if sys.platform == "win32": os.startfile(full_path)
                elif sys.platform == "darwin": subprocess.call(['open', full_path])
                else: subprocess.call(['xdg-open', full_path])
        except (AttributeError, FileNotFoundError):
            messagebox.showinfo("Unsupported Action", "Could not open file with the system default\nPlease configure a default editor in Settings", parent=self.parent)
        except Exception as e:
            self.parent.show_error_dialog("Error", f"Could not open file: {e}")
        return "break"

    def _on_scroll(self, event=None):
        self._hide_tooltip()

    def _schedule_tooltip(self, event):
        self._hide_tooltip()
        # Immediately update info panel based on current column
        self._update_info_panel(event)
        self.tooltip_job = self.listbox.after(500, lambda e=event: self._show_tooltip(e))

    def _update_info_panel(self, event):
        """Swaps Info Panel keys based on cursor location relative to columns."""
        mgr = getattr(self.parent, 'info_mgr', None)
        if not mgr: return

        index = int(self.listbox.canvasy(event.y) // self.listbox.row_height)
        if 0 <= index < len(self.ordered_selection):
            is_over_token_area = event.x > (self.listbox.winfo_width() - self.listbox.right_col_width)
            new_key = "fm_tokens_item" if is_over_token_area else "fm_list_item"
        else:
            new_key = "fm_list"

        # Update the active documentation stack if the list is currently the top item
        if mgr._active_stack and mgr._active_stack[-1][0] == self.listbox:
            if mgr._active_stack[-1][1] != new_key:
                mgr._active_stack[-1] = (self.listbox, new_key)
                mgr._update_display()

    def _show_tooltip(self, event):
        if self.tooltip_window: self.tooltip_window.destroy(); self.tooltip_window = None
        index = int(self.listbox.canvasy(event.y) // self.listbox.row_height)
        if not (0 <= index < len(self.ordered_selection)): return

        item_info = self.ordered_selection[index]
        path = item_info.get('path')
        if not path: return

        is_over_token_area = event.x > (self.listbox.winfo_width() - self.listbox.right_col_width)
        tooltip_text = ""

        if is_over_token_area:
            # Token Stats Tooltip
            if self.ui_manager.token_count_enabled:
                tokens, lines = item_info.get('tokens', -1), item_info.get('lines', -1)
                is_ignored_token = item_info.get('ignore_tokens', False)
                if tokens >= 0:
                    tooltip_text = f"{tokens} tokens, {lines} lines"
                    if is_ignored_token:
                        tooltip_text += "\n(Ignored in coloring)"
                    tooltip_text += "\nCtrl+Click to copy breakup request\nAlt+Click to toggle ignore"
        else:
            # Filename Area
            tooltip_text = "Double-click to open in editor.\nFile path display can be toggled via the tools icon."

            # Prefix with Full Path if currently showing only basename
            if not self.ui_manager.show_full_paths:
                basename = os.path.basename(path)
                full_path_display = path.replace('/', os.sep)
                if basename != full_path_display:
                    tooltip_text = f"{full_path_display}\n\n{tooltip_text}"

            # Filter Reason Hint
            hidden_reasons = []
            if is_ignored(os.path.join(self.base_dir, path), self.base_dir, self.parent.gitignore_patterns):
                hidden_reasons.append("the .gitignore filter")

            filename = os.path.basename(path)
            file_ext = os.path.splitext(filename.lower())[1]
            extensions = {ext for ext in self.parent.file_extensions if ext.startswith('.')}
            exact_filenames = {ext for ext in self.parent.file_extensions if not ext.startswith('.')}
            if not (file_ext in extensions or filename.lower() in exact_filenames):
                hidden_reasons.append("the filetype filter")

            if hidden_reasons:
                hint = f"Normally hidden by {' and '.join(hidden_reasons)}."
                tooltip_text += f"\n\n{hint}"

        if not tooltip_text: return

        x, y = event.x_root + 15, event.y_root + 10
        self.tooltip_window = Toplevel(self.parent)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = Label(self.tooltip_window, text=tooltip_text, justify='left',
                      background=c.TOP_BAR_BG, fg=c.TEXT_COLOR, relief='solid', borderwidth=1,
                      font=c.FONT_TOOLTIP)
        label.pack(ipadx=4, ipady=2)

    def _hide_tooltip(self, event=None):
        if self.tooltip_job: self.listbox.after_cancel(self.tooltip_job); self.tooltip_job = None
        if self.tooltip_window: self.tooltip_window.destroy(); self.tooltip_window = None
```

--- End of file ---

--- File: `src/ui/file_manager/state_controller.py` ---

```python
from tkinter import messagebox
from ... import constants as c

class FileManagerStateController:
    def __init__(self, window):
        self.window = window

    def is_state_changed(self):
        if self.window.selection_handler.ordered_selection != self.window.project_config.selected_files:
            return True
        current_expanded = set(self.window.tree_handler.get_expanded_dirs())
        if current_expanded != self.window.project_config.expanded_dirs:
            return True
        return False

    def on_closing(self):
        if self.is_state_changed():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before closing?",
                parent=self.window
            )
            if response is True:
                self.save_and_close()
            elif response is False:
                self.window._close_and_save_geometry()
        else:
            self.window._close_and_save_geometry()

    def save_and_close(self):
        project = self.window.project_config
        project.selected_files = self.window.selection_handler.ordered_selection
        project.expanded_dirs = set(self.window.tree_handler.get_expanded_dirs())
        project.total_tokens = self.window.current_total_tokens
        current_paths = {f['path'] for f in project.selected_files}
        project.known_files = list(set(project.known_files) | current_paths)
        project.save()
        self.window.status_var.set("Merge list and order saved to .allcode")
        self.window._close_and_save_geometry()

    def select_all_files(self):
        all_paths = self.window.tree_handler.get_all_file_paths_in_tree_order()
        current_paths = {f['path'] for f in self.window.selection_handler.ordered_selection}
        paths_to_add = [p for p in all_paths if p not in current_paths]

        if not paths_to_add:
            self.window.status_var.set("No new files to add")
            return

        threshold = self.window.app_state.config.get('add_all_warning_threshold', c.ADD_ALL_WARNING_THRESHOLD_DEFAULT)
        if len(paths_to_add) > threshold:
            if not messagebox.askyesno(
                "Confirm Adding Files",
                f"You are about to add {len(paths_to_add)} files to the merge list.\n\nAre you sure?",
                parent=self.window
            ):
                self.window.status_var.set("Operation cancelled by user.")
                return

        self.window.selection_handler.add_files(paths_to_add)
        self.window.status_var.set(f"Added {len(paths_to_add)} file(s) to the list")

    def remove_all_files(self):
        if not self.window.selection_handler.ordered_selection:
            self.window.status_var.set("Merge list is already empty")
            return
        if messagebox.askyesno("Confirm Removal", "Remove all files from the merge list?", parent=self.window):
            count = len(self.window.selection_handler.ordered_selection)
            self.window.selection_handler.remove_all_files()
            self.window.status_var.set(f"Removed {count} file(s) from the list")
```

--- End of file ---

--- File: `src/ui/file_manager/order_request_handler.py` ---

```python
import json
import pyperclip
from tkinter import messagebox
from ...core.merger import generate_output_string
from ..multiline_input_dialog import MultilineInputDialog
from ... import constants as c

class OrderRequestHandler:
    """Handles the logic for creating and applying file order requests."""
    def __init__(self, fm_window):
        self.window = fm_window
        self.order_request_click_job = None
        self._btn_fade_job = None

    def handle_click(self, event=None):
        """Manages single, double, and ctrl-clicks for the order request button."""
        is_ctrl = event and (event.state & 0x0004)

        if is_ctrl:
            if self.order_request_click_job:
                self.window.after_cancel(self.order_request_click_job)
                self.order_request_click_job = None

            pasted_text = pyperclip.paste()
            if not pasted_text or not pasted_text.strip():
                self.window.status_var.set("Clipboard is empty.")
                return "break"

            self._apply_reorder(pasted_text)
            return "break"

        if self.order_request_click_job:
            self.window.after_cancel(self.order_request_click_job)
            self.order_request_click_job = None
            self._apply_reorder()
        else:
            self.order_request_click_job = self.window.after(300, self._copy_request)

        return "break"

    def _animate_button_press(self):
        """Flashes the button background and fades it back to normal."""
        if self._btn_fade_job:
            self.window.after_cancel(self._btn_fade_job)

        btn = self.window.order_request_button
        start_color = c.SUBTLE_HIGHLIGHT_COLOR
        end_color = c.DARK_BG

        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb

        def mix(rgb_start, rgb_end, p):
            return tuple(int(rgb_start[i] + (rgb_end[i] - rgb_start[i]) * p) for i in range(3))

        rgb_start = hex_to_rgb(start_color)
        rgb_end = hex_to_rgb(end_color)

        def step(frame, total_frames):
            if not btn.winfo_exists(): return
            progress = frame / total_frames
            current_rgb = mix(rgb_start, rgb_end, progress)
            btn.config(bg=rgb_to_hex(current_rgb))

            if frame < total_frames:
                self._btn_fade_job = self.window.after(25, step, frame + 1, total_frames)
            else:
                btn.config(bg=end_color)
                self._btn_fade_job = None

        btn.config(bg=start_color)
        self.window.after(50, step, 1, 10)

    def _copy_request(self):
        """Copies a formatted order request with full file content to the clipboard."""
        self.order_request_click_job = None
        ordered_files_info = self.window.selection_handler.ordered_selection
        if not ordered_files_info:
            self.window.status_var.set("No files in merge order to create a request for.")
            return

        temp_project_config = self.window.project_config
        temp_project_config.selected_files = ordered_files_info
        merged_code, _ = generate_output_string(
            base_dir=self.window.base_dir,
            project_config=temp_project_config,
            use_wrapper=False,
            copy_merged_prompt=""
        )
        if not merged_code:
            self.window.status_var.set("Failed to generate merged code for the request.")
            return

        paths = [f['path'] for f in ordered_files_info]
        prepend_text = "Please provide me with the optimal order in which to present these files to a language model. Only return the file list in the exact same format I will use here:\n\n"
        json_payload = json.dumps(paths, indent=2)
        content_intro = "Here's the content of the files, to help you determine the best order:"

        final_string = f"{prepend_text}{json_payload}\n\n{content_intro}\n\n{merged_code}"
        pyperclip.copy(final_string)
        self.window.status_var.set("Order request with file content copied to clipboard.")

        # Trigger the visual feedback on the button
        self._animate_button_press()

    def _apply_reorder(self, pasted_text=None):
        """Processes a new file order and updates the list."""
        current_selection = self.window.selection_handler.ordered_selection
        if not current_selection:
            self.window.status_var.set("Merge order is empty, nothing to reorder.")
            return

        if pasted_text is None:
            dialog = MultilineInputDialog(
                parent=self.window,
                title="Update Merge Order",
                prompt="Paste the language model response containing the new file order."
            )
            pasted_text = dialog.result

        if not pasted_text:
            return

        try:
            start_index = pasted_text.find('[')
            end_index = pasted_text.rfind(']') + 1
            if start_index == -1 or end_index == 0:
                raise ValueError("Could not find a JSON array (starting with '[' and ending with ']').")
            json_str = pasted_text[start_index:end_index]
            new_order_list = json.loads(json_str)
            if not isinstance(new_order_list, list):
                raise ValueError("The parsed JSON is not a list.")
        except (ValueError, json.JSONDecodeError) as e:
            self.window.show_error_dialog("Parsing Error", f"Could not parse the new file order.\n\nError: {e}")
            return

        current_paths_set = {f['path'] for f in current_selection}
        new_paths_set = set(new_order_list)
        missing_files = current_paths_set - new_paths_set
        unknown_files = new_paths_set - current_paths_set

        if missing_files or unknown_files:
            error_message = "The provided file list is invalid.\n"
            if missing_files: error_message += f"\nMissing files:\n- " + "\n- ".join(sorted(list(missing_files)))
            if unknown_files: error_message += f"\nUnknown files:\n- " + "\n- ".join(sorted(list(unknown_files)))
            self.window.show_error_dialog("Validation Error", error_message)
            return

        path_map = {f['path']: f for f in current_selection}
        new_ordered_selection = [path_map[p] for p in new_order_list]
        self.window.selection_handler.data_manager.ordered_selection = new_ordered_selection

        # Pass missing positional arguments required by SelectionListUI.update_list_display
        self.window.selection_handler.ui_manager.update_list_display(
            new_ordered_selection,
            base_dir=self.window.base_dir,
            file_extensions=self.window.file_extensions,
            gitignore_patterns=self.window.gitignore_patterns,
            is_reorder=True,
            animate=True
        )

        self.window.selection_handler.on_change()
        self.window.status_var.set("File merge order updated successfully.")
```

--- End of file ---

--- File: `src/ui/file_manager/ui_setup.py` ---

```python
from tkinter import Frame, Label, ttk, font, Button, Entry
from ..widgets.rounded_button import RoundedButton
from ..widgets.two_column_list import TwoColumnList
from ... import constants as c
from ...constants import SUBTLE_HIGHLIGHT_COLOR
from ..assets import assets
from ..tooltip import ToolTip

def setup_file_manager_ui(window, container=None, include_save_button=True, main_padding=10, main_padx=10, bottom_padding=None):
    """
    Creates and places all the UI widgets for the FileManagerWindow.
    """
    font_config = c.FONT_SMALL_BUTTON
    window.font_small = font.Font(family=font_config[0], size=font_config[1])

    # Determine the parent widget for the UI components
    parent_widget = container if container else window

    # If bottom_padding is provided by the caller (like the Project Starter), use it.
    # Otherwise, fallback to the standard top-heavy padding.
    pady_val = bottom_padding if bottom_padding is not None else (main_padding, 0)

    main_frame = Frame(parent_widget, bg=c.DARK_BG)
    main_frame.pack(fill='both', expand=True, padx=main_padx, pady=pady_val)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=0)
    main_frame.grid_columnconfigure(0, weight=1)

    # Paned Window for a truly resizable and seamless layout
    window.paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
    window.paned_window.grid(row=0, column=0, sticky='nsew')

    # Left Panel (Available Files)
    left_panel = Frame(window.paned_window, bg=c.DARK_BG)
    left_panel.grid_columnconfigure(0, weight=1)
    left_panel.grid_rowconfigure(1, weight=1)
    window.paned_window.add(left_panel, weight=1)

    # Right Panel (Merge Order)
    right_panel = Frame(window.paned_window, bg=c.DARK_BG)
    right_panel.grid_columnconfigure(0, weight=1)
    right_panel.grid_rowconfigure(1, weight=1)
    window.paned_window.add(right_panel, weight=1)
    window.sash_cover = Frame(window.paned_window, bg=c.DARK_BG, width=6, cursor="sb_h_double_arrow")

    # Bind events to the centralized methods in the main window class
    window.paned_window.bind("<<SashMoved>>", window._on_manual_sash_move)
    window.paned_window.bind("<Configure>", window._update_sash_cover_position)
    window.after(10, window._update_sash_cover_position) # Initial placement

    # ===============================
    # === WIDGETS FOR LEFT PANEL ====
    # ===============================
    available_files_title_frame = Frame(left_panel, bg=c.DARK_BG)
    available_files_title_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
    available_files_title_frame.grid_columnconfigure(1, weight=1) # Middle column expands to push sides apart.

    title_sub_frame = Frame(available_files_title_frame, bg=c.DARK_BG)
    title_sub_frame.grid(row=0, column=0, sticky='w')
    Label(title_sub_frame, text="Available Files", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(side='left')
    Label(title_sub_frame, text="(double click or enter to add/remove)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='left', padx=(5,0))

    right_buttons_frame = Frame(available_files_title_frame, bg=c.DARK_BG)
    right_buttons_frame.grid(row=0, column=2, sticky='e')

    window.toggle_gitignore_button = Button(
        right_buttons_frame,
        image=assets.git_files_icon,
        command=window.ui_controller.toggle_gitignore_filter,
        bg=c.DARK_BG,
        activebackground=c.SUBTLE_HIGHLIGHT_COLOR,
        relief='flat',
        bd=0,
        cursor='hand2'
    )
    window.toggle_gitignore_button.pack(side='left')
    window.gitignore_button_tooltip = ToolTip(window.toggle_gitignore_button, ".gitignore filter is ON. Click to show all files.")

    window.toggle_filter_button = Button(
        right_buttons_frame,
        image=assets.filter_icon,
        command=window.ui_controller.toggle_extension_filter,
        bg=c.DARK_BG,
        activebackground=c.SUBTLE_HIGHLIGHT_COLOR,
        relief='flat',
        bd=0,
        cursor='hand2'
    )
    window.toggle_filter_button.pack(side='left', padx=(5, 0))
    window.filter_button_tooltip = ToolTip(window.toggle_filter_button, "Filetype filter is ON. Click to show all files.")

    # Style configuration to ensure Treeview background is dark
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Treeview",
                    background=c.TEXT_INPUT_BG,
                    foreground=c.TEXT_COLOR,
                    fieldbackground=c.TEXT_INPUT_BG, # Explicitly fixed background
                    borderwidth=0,
                    font=c.FONT_NORMAL,
                    rowheight=25)
    style.map("Treeview", background=[('selected', c.BTN_BLUE)], foreground=[('selected', c.BTN_BLUE_TEXT)])

    window.tree = ttk.Treeview(left_panel, show='tree', selectmode='extended')
    window.tree.grid(row=1, column=0, sticky='nsew')
    tree_scroll = ttk.Scrollbar(left_panel, orient='vertical', command=window.tree.yview)
    tree_scroll.grid(row=1, column=1, sticky='ns')
    window.tree.config(yscrollcommand=tree_scroll.set)

    window.folder_icon_labels = {
        'default': Label(window.tree, image=assets.folder_reveal_icon, bg=c.TEXT_INPUT_BG, cursor="hand2"),
        'selected': Label(window.tree, image=assets.folder_reveal_icon, bg=c.BTN_BLUE, cursor="hand2"),
        'highlight': Label(window.tree, image=assets.folder_reveal_icon, bg=c.SUBTLE_HIGHLIGHT_COLOR, cursor="hand2")
    }
    for label in window.folder_icon_labels.values():
        label.bind("<ButtonRelease-1>", window.ui_controller.on_folder_icon_click)
        ToolTip(label, text="Open file in folder", delay=500)

    tree_actions_frame = Frame(left_panel, bg=c.DARK_BG)
    tree_actions_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))
    tree_actions_frame.columnconfigure(0, weight=1)
    tree_actions_frame.columnconfigure(1, weight=2)

    window.tree_action_button = RoundedButton(tree_actions_frame, text="Add to List", command=None, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, h_padding=80, cursor='hand2')
    window.tree_action_button.grid(row=0, column=0, sticky='w')
    window.tree_action_button.set_state('disabled')

    filter_container = Frame(tree_actions_frame, bg=c.DARK_BG)
    filter_container.grid(row=0, column=1, sticky='ew', padx=(10, 0))
    # Reference the Label separately for info mode registration
    window.filter_label = Label(filter_container, text="Filter:", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)
    window.filter_label.pack(side='left')
    window.filter_input_frame = Frame(filter_container, bg=c.TEXT_INPUT_BG, highlightthickness=1, highlightbackground=c.TEXT_INPUT_BG)
    window.filter_input_frame.pack(side='left', padx=(5,0), fill='x', expand=True)
    window.filter_entry = Entry(window.filter_input_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL, width=25)
    window.filter_entry.pack(side='left', fill='x', expand=True, ipady=3, padx=(5, 20))

    window.clear_filter_button = Label(window.filter_input_frame, image=assets.compact_mode_close_image, bg=c.TEXT_INPUT_BG, cursor="hand2")
    window.clear_filter_button.place(relx=1.0, rely=0.5, anchor='e', x=-5)
    window.clear_filter_button.place_forget()
    window.clear_filter_button.bind("<Enter>", lambda e: window.clear_filter_button.config(bg=c.SUBTLE_HIGHLIGHT_COLOR))
    window.clear_filter_button.bind("<Leave>", lambda e: window.clear_filter_button.config(bg=c.TEXT_INPUT_BG))
    window.clear_filter_button.bind("<ButtonRelease-1>", window.ui_controller.clear_filter)

    # "Add all" button aligned to the far right side of the available files column (row 3)
    window.add_all_btn = RoundedButton(left_panel, text="Add all", command=window.state_controller.select_all_files, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, cursor='hand2')
    window.add_all_btn.grid(row=3, column=0, columnspan=2, sticky='e', pady=10)

    window.tree.tag_configure('subtle_highlight', background=SUBTLE_HIGHLIGHT_COLOR, foreground=c.TEXT_COLOR)
    window.tree.tag_configure('new_file_highlight', foreground="#40C040")
    window.tree.tag_configure('selected_grey', foreground=c.TEXT_SUBTLE_COLOR)

    # ===============================
    # === WIDGETS FOR RIGHT PANEL ===
    # ===============================
    title_frame = Frame(right_panel, bg=c.DARK_BG)
    title_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=(10, 0))
    title_frame.columnconfigure(1, weight=1)

    Label(title_frame, text="Merge Order", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).grid(row=0, column=0, sticky='w')
    window.merge_order_details_label = Label(title_frame, text="", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)
    window.merge_order_details_label.grid(row=0, column=1, sticky='w', padx=(5,0))
    window.token_count_tooltip = ToolTip(window.merge_order_details_label, text="", delay=300)

    window.order_request_button = Button(
        title_frame,
        image=assets.order_request_icon,
        command=None,
        bg=c.DARK_BG,
        activebackground=c.SUBTLE_HIGHLIGHT_COLOR,
        relief='flat',
        bd=0,
        cursor='hand2'
    )
    window.order_request_button.grid(row=0, column=2, sticky='e', padx=(5,0))
    window.order_request_button.bind("<Button-1>", window.order_request_handler.handle_click)
    ToolTip(window.order_request_button, "Single-click: Copy order request\nDouble-click: Paste new order via dialog\nCtrl-click: Paste new order instantly")

    window.toggle_paths_button = Button(title_frame, image=assets.paths_icon, command=window.ui_controller.toggle_full_path_view, bg=c.DARK_BG, activebackground=c.SUBTLE_HIGHLIGHT_COLOR, relief='flat', bd=0, cursor='hand2')
    window.toggle_paths_button.grid(row=0, column=3, sticky='e', padx=(5,0))
    ToolTip(window.toggle_paths_button, "Toggle full path")

    list_frame = Frame(right_panel, bg=c.DARK_BG)
    list_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=(10, 0))
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)

    window.merge_order_list = TwoColumnList(list_frame, right_col_font=window.font_small, right_col_width=50)
    window.merge_order_list.grid(row=0, column=0, sticky='nsew')
    list_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=window.merge_order_list.yview)
    list_scroll.grid(row=0, column=1, sticky='ns')
    window.merge_order_list.config(yscrollcommand=list_scroll.set)
    window.merge_order_list.link_scrollbar(list_scroll)

    move_buttons_frame = Frame(right_panel, bg=c.DARK_BG)
    move_buttons_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0), padx=(10, 0))
    move_buttons_frame.grid_columnconfigure(0, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(1, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(2, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(3, weight=1, uniform="group1")
    move_buttons_frame.grid_columnconfigure(4, weight=1, uniform="group1")

    # Minimalist Reorder Buttons with Muted Borders
    btn_height = 34
    window.move_to_top_button = RoundedButton(move_buttons_frame, text="↑↑", command=None, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_FILE_MANAGER_BUTTON, width=40, height=btn_height, hollow=True, muted_border=True, cursor='hand2')
    window.move_to_top_button.grid(row=0, column=0, sticky='ew', padx=(0, 2))
    ToolTip(window.move_to_top_button, "Move Selected to Top")

    window.move_up_button = RoundedButton(move_buttons_frame, text="↑", command=None, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_FILE_MANAGER_BUTTON, width=40, height=btn_height, hollow=True, muted_border=True, cursor='hand2')
    window.move_up_button.grid(row=0, column=1, sticky='ew', padx=(2, 2))
    ToolTip(window.move_up_button, "Move Selected Up")

    # Removal button reverted to original text
    window.remove_button = RoundedButton(move_buttons_frame, text="Remove", command=None, fg=c.TEXT_COLOR, font=c.FONT_FILE_MANAGER_BUTTON, height=btn_height, hollow=True, cursor='hand2')
    window.remove_button.grid(row=0, column=2, sticky='ew', padx=2)
    ToolTip(window.remove_button, "Remove Selected from List")

    window.move_down_button = RoundedButton(move_buttons_frame, text="↓", command=None, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_FILE_MANAGER_BUTTON, width=40, height=btn_height, hollow=True, muted_border=True, cursor='hand2')
    window.move_down_button.grid(row=0, column=3, sticky='ew', padx=(2, 2))
    ToolTip(window.move_down_button, "Move Selected Down")

    window.move_to_bottom_button = RoundedButton(move_buttons_frame, text="↓↓", command=None, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_FILE_MANAGER_BUTTON, width=40, height=btn_height, hollow=True, muted_border=True, cursor='hand2')
    window.move_to_bottom_button.grid(row=0, column=4, sticky='ew', padx=(2, 0))
    ToolTip(window.move_to_bottom_button, "Move Selected to Bottom")

    for btn in [window.move_to_top_button, window.move_up_button, window.remove_button, window.move_down_button, window.move_to_bottom_button]:
        btn.set_state('disabled')

    # Combined bottom row for Right Panel (row 3)
    right_bottom_row = Frame(right_panel, bg=c.DARK_BG)
    right_bottom_row.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10, padx=(10, 0))

    # "Remove all" button aligned to the left side of the merge list column
    window.remove_all_btn = RoundedButton(right_bottom_row, text="Remove all", command=window.state_controller.remove_all_files, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_FILE_MANAGER_BUTTON, cursor='hand2')
    window.remove_all_btn.pack(side='left')

    if include_save_button:
        window.save_close_btn = RoundedButton(right_bottom_row, text="Update Project", command=window.state_controller.save_and_close, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, width=240, cursor='hand2')
        window.save_close_btn.pack(side='right')

    # Info Toggle: Managed by InfoManager.place
    window.info_toggle_btn = Label(window, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")
```

--- End of file ---

--- File: `src/ui/file_manager/file_manager_window.py` ---

```python
import tkinter as tk
import sys
import re
from tkinter import Toplevel, StringVar, Frame, Label
from ...core.utils import parse_gitignore
from .file_tree_builder import build_file_tree_data
from .file_tree_handler import FileTreeHandler
from .selection_list_controller import SelectionListController
from .ui_setup import setup_file_manager_ui
from .ui_controller import FileManagerUIController
from .data_controller import FileManagerDataController
from .state_controller import FileManagerStateController
from .order_request_handler import OrderRequestHandler
from ... import constants as c
from ...core.paths import ICON_PATH
from ..window_utils import position_window, save_window_geometry
from ..custom_error_dialog import CustomErrorDialog
from ..info_manager import attach_info_mode
from ..assets import assets

class FileManagerWindow(Toplevel):
    def __init__(self, parent, project_config, status_var, file_extensions, default_editor, app_state, newly_detected_files=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.project_config = project_config
        self.base_dir = self.project_config.base_dir
        self.status_var = status_var
        self.file_extensions = file_extensions
        self.default_editor = default_editor
        self.app_state = app_state
        self.newly_detected_files = newly_detected_files or []
        self.full_paths_visible = False
        self.token_count_enabled = self.app_state.config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT)
        self.is_extension_filter_active = True
        self.is_gitignore_filter_active = True
        self.hovered_file_path = None
        self.current_total_tokens = self.project_config.total_tokens
        self.sash_pos_normal = None
        self.window_geometries = {}

        self.title(f"Edit merge list for: {self.project_config.project_name}")
        self.iconbitmap(ICON_PATH)

        # Dynamic Geometry for Boot
        initial_geom = c.FILE_MANAGER_DEFAULT_GEOMETRY
        if self.app_state.info_mode_active:
            match = re.match(r"(\d+)x(\d+)", initial_geom)
            if match:
                w, h = map(int, match.groups())
                initial_geom = f"{w}x{h + c.INFO_PANEL_HEIGHT}"

        self.geometry(initial_geom)
        self.minsize(c.FILE_MANAGER_MIN_WIDTH, c.FILE_MANAGER_MIN_HEIGHT)
        self.grab_set()
        self.focus_force()
        self.configure(bg=c.DARK_BG)

        if self.project_config.load():
            self.status_var.set("Cleaned missing files from .allcode")

        self.gitignore_patterns = parse_gitignore(self.base_dir)
        self.ui_controller = FileManagerUIController(self)
        self.data_controller = FileManagerDataController(self)
        self.state_controller = FileManagerStateController(self)
        self.order_request_handler = OrderRequestHandler(self)

        # setup_file_manager_ui populates the window's main frame
        setup_file_manager_ui(self, include_save_button=True)
        self.create_handlers()

        # Register visual tags for the tree
        self.tree.tag_configure('filtered_file_highlight', foreground=c.TEXT_FILTERED_COLOR)
        self.tree.tag_configure('subtle_highlight', background=c.SUBTLE_HIGHLIGHT_COLOR, foreground=c.TEXT_COLOR)
        self.tree.tag_configure('new_file_highlight', foreground="#40C040")
        self.tree.tag_configure('selected_grey', foreground=c.TEXT_SUBTLE_COLOR)

        self.filter_text = StringVar()
        self.filter_entry.config(textvariable=self.filter_text)
        self.filter_text.trace_add('write', self.ui_controller.apply_filter)
        self.clear_filter_button.bind("<Button-1>", self.ui_controller.clear_filter)

        self.protocol("WM_DELETE_WINDOW", self.state_controller.on_closing)
        self.bind('<Escape>', lambda e: self.state_controller.on_closing())
        self.tree.bind("<Motion>", self.ui_controller.on_tree_motion)
        self.tree.bind("<Leave>", self.ui_controller.on_tree_leave)

        self.data_controller.validate_and_update_cache()
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.populate_tree()
        self.data_controller.run_token_recalculation()
        self.update_all_button_states()

        # Info Mode Integration
        self.info_mgr = attach_info_mode(self, self.app_state, manager_type='pack', toggle_btn=self.info_toggle_btn)
        self._register_hover_help()

        self._position_window()
        self.deiconify()

        # Disable Minimize Button (Windows Only)
        if sys.platform == "win32":
            self.after(10, self._disable_minimize_button)

        if self.newly_detected_files:
            self.ui_controller.expand_and_scroll_to_new_files()

    def _register_hover_help(self):
        """Attaches detailed help messages to the List Editor widgets."""
        mgr = self.info_mgr
        mgr.register(self.tree, "fm_tree")

        # Merge Order List default documentation
        mgr.register(self.merge_order_list, "fm_list")

        # Filtering
        mgr.register(self.filter_label, "fm_filter_text")
        mgr.register(self.filter_entry, "fm_filter_text")
        mgr.register(self.toggle_gitignore_button, "fm_filter_git")
        mgr.register(self.toggle_filter_button, "fm_filter_ext")

        # Reveal Icons (Loop through all state variants)
        for label in self.folder_icon_labels.values():
            mgr.register(label, "fm_reveal")

        # Stats and List Tools
        mgr.register(self.merge_order_details_label, "fm_tokens")
        mgr.register(self.order_request_button, "fm_order")
        mgr.register(self.toggle_paths_button, "fm_list_tools")
        mgr.register(self.tree_action_button, "fm_tree_action")

        # Sorting priority
        mgr.register(self.move_to_top_button, "fm_sort_top")
        mgr.register(self.move_up_button, "fm_sort_up")
        mgr.register(self.move_down_button, "fm_sort_down")
        mgr.register(self.move_to_bottom_button, "fm_sort_bottom")
        mgr.register(self.remove_button, "fm_sort_remove")

        # Bulk actions section
        mgr.register(self.add_all_btn, "fm_add_all")
        mgr.register(self.remove_all_btn, "fm_remove_all")
        mgr.register(self.save_close_btn, "fm_save")

        mgr.register(self.info_toggle_btn, "info_toggle")

    def _disable_minimize_button(self):
        """
        Uses Win32 API to disable the minimize button.
        Uses the wm_frame() to get the actual OS wrapper handle.
        """
        try:
            import ctypes
            # Get the handle for the window frame
            hwnd_str = self.wm_frame()
            if not hwnd_str:
                return

            # Convert hex string (e.g. '0x12345') to integer
            hwnd = int(hwnd_str, 16)

            # Win32 Constants
            GWL_STYLE = -16
            WS_MINIMIZEBOX = 0x00020000

            # Update the style to remove the minimize box bit
            user32 = ctypes.windll.user32
            current_style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            if current_style:
                new_style = current_style & ~WS_MINIMIZEBOX
                user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)

                # Force refresh of the title bar buttons
                user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)
        except (ValueError, Exception):
            pass

    def show_error_dialog(self, title, message, hint=None):
        # Instantiate the dialog with this window as the parent to keep focus.
        CustomErrorDialog(self, title, message, hint=hint)

    def _position_window(self):
        position_window(self)

    def _close_and_save_geometry(self):
        if self.state() == 'normal':
            save_window_geometry(self)
        self.destroy()

    def _update_sash_cover_position(self, event=None):
        try:
            x = self.paned_window.sashpos(0)
            self.sash_cover.place(x=x, y=0, anchor="nw", relheight=1.0)
        except Exception:
            pass

    def _on_manual_sash_move(self, event=None):
        self.sash_pos_normal = self.paned_window.sashpos(0)
        self._update_sash_cover_position()

    def create_handlers(self):
        self.item_map = {}
        self.path_to_item_id = {}
        listbox_buttons = {
            'top': self.move_to_top_button, 'up': self.move_up_button,
            'remove': self.remove_button, 'down': self.move_down_button,
            'bottom': self.move_to_bottom_button
        }
        self.selection_handler = SelectionListController(
            self, self.merge_order_list, listbox_buttons, self.base_dir, self.default_editor,
            self.on_selection_list_changed, self.token_count_enabled
        )
        self.tree_handler = FileTreeHandler(
            self, self.tree, self.tree_action_button, self.item_map, self.path_to_item_id,
            lambda path: path in [f['path'] for f in self.selection_handler.ordered_selection],
            self.on_file_toggled
        )
        self.tree_action_button.command = self.tree_handler.toggle_selection_for_selected
        self.move_to_top_button.command = self.selection_handler.move_to_top
        self.move_up_button.command = self.selection_handler.move_up
        self.move_down_button.command = self.selection_handler.move_down
        self.move_to_bottom_button.command = self.selection_handler.move_to_bottom
        self.remove_button.command = self.selection_handler.remove_selected

    def populate_tree(self, filter_text=""):
        # Get currently expanded directories before clearing the tree
        expanded_dirs_before_rebuild = set(self.tree_handler.get_expanded_dirs())

        for item in self.tree.get_children(): self.tree.delete(item)
        self.item_map.clear(); self.path_to_item_id.clear()
        selected_paths = {f['path'] for f in self.selection_handler.ordered_selection}
        tree_data = build_file_tree_data(
            self.base_dir,
            self.file_extensions,
            self.gitignore_patterns,
            filter_text,
            self.is_extension_filter_active,
            selected_paths,
            self.is_gitignore_filter_active
        )
        def _insert_nodes(parent_id, nodes):
            for node in nodes:
                tags = ()
                if node['type'] == 'file' and node['path'] in self.newly_detected_files:
                    tags += ('new_file_highlight',)

                # A directory should be open if it was already open in the current session,
                # or if it was saved as expanded from a previous session.
                is_open = node.get('path') in expanded_dirs_before_rebuild or \
                          node.get('path') in self.project_config.expanded_dirs

                item_id = self.tree.insert(parent_id, 'end', text=node['name'], open=is_open, tags=tags)
                self.item_map[item_id] = {'path': node['path'], 'type': node['type']}
                self.path_to_item_id[node['path']] = item_id

                if node['type'] == 'dir':
                    _insert_nodes(item_id, node.get('children', []))
                    self.tree_handler.update_item_visuals(item_id)
                else: # file
                    self.tree_handler.update_item_visuals(item_id)
        _insert_nodes('', tree_data)

    def on_selection_list_changed(self):
        self.tree_handler.update_all_visuals()
        self.update_all_button_states()
        self.data_controller.run_token_recalculation()
        self.ui_controller.update_active_folder_tooltip()

    def on_file_toggled(self, path):
        self.selection_handler.toggle_file(path)
        self.tree_handler.update_item_visuals(self.path_to_item_id.get(path))
        self.update_all_button_states()
        self.sync_highlights()

    def handle_tree_select(self, event):
        if self.tree.selection(): self.merge_order_list.clear_selection()
        self.sync_highlights()
        self.update_all_button_states()

    def handle_merge_order_tree_select(self, event):
        if self.merge_order_list.curselection() and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.sync_highlights()
        self.update_all_button_states()

    def update_all_button_states(self):
        self.tree_handler.update_action_button_state()
        self.selection_handler.update_button_states()

    def sync_highlights(self):
        # We target specifically the highlight tag, but preserve others like purple coloring
        for item_id in self.tree.tag_has('subtle_highlight'):
            current_tags = list(self.tree.item(item_id, 'tags'))
            if 'subtle_highlight' in current_tags:
                current_tags.remove('subtle_highlight')
            self.tree.item(item_id, tags=tuple(current_tags))

        self.merge_order_list.clear_highlights()
        selected_path, source = (None, None)
        if self.tree.selection():
            item_id = self.tree.selection()[0]
            if self.item_map.get(item_id, {}).get('type') == 'file':
                selected_path, source = (self.item_map[item_id]['path'], self.tree)
        elif self.merge_order_list.curselection():
            idx = self.merge_order_list.curselection()[0]
            selected_path, source = (self.merge_order_list.get_item_data(idx), self.merge_order_list)
        if not selected_path: return
        if source == self.tree:
            try:
                paths = [f['path'] for f in self.selection_handler.ordered_selection]
                self.merge_order_list.highlight_item(paths.index(selected_path))
            except ValueError: pass
        elif source == self.merge_order_list and selected_path in self.path_to_item_id:
            item_id = self.path_to_item_id[selected_path]
            current_tags = list(self.tree.item(item_id, 'tags'))
            if 'subtle_highlight' not in current_tags:
                current_tags.append('subtle_highlight')
            self.tree.item(item_id, tags=tuple(current_tags))
            self.tree.see(item_id)

        self.ui_controller.refresh_hover_icon()
```

--- End of file ---

--- File: `src/ui/project_starter/session_manager.py` ---

```python
import json
import os
import logging
from ...core.paths import PERSISTENT_DATA_DIR

log = logging.getLogger("CodeMerger")
SESSION_FILE = os.path.join(PERSISTENT_DATA_DIR, "project_starter_session.json")

def get_session_filepath():
    """Returns the path to the default session file."""
    return SESSION_FILE

def save_session_data(data, filepath=None):
    """Saves the project data dictionary to a JSON file."""
    target = filepath if filepath else SESSION_FILE
    try:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Failed to save session to {target}: {e}")

def load_session_data(filepath=None):
    """
    Loads project data from a JSON file.
    Returns an empty dict if the file doesn't exist or fails to load.
    """
    target = filepath if filepath else SESSION_FILE
    if not os.path.exists(target):
        return {}
    try:
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Failed to load session from {target}: {e}")
        return {}

def clear_default_session():
    """Deletes the default session file if it exists."""
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except OSError as e:
            log.error(f"Failed to delete session file: {e}")
```

--- End of file ---

--- File: `src/ui/project_starter/starter_state.py` ---

```python
import tkinter as tk
import os
from . import session_manager
from ... import constants as c
from .segment_manager import SegmentManager

class StarterState:
    """
    Manages the data and progress state of the Project Starter.
    Handles persistence via the session_manager.
    """
    def __init__(self):
        self.current_step = 1
        self.max_accessible_step = 1

        self.project_data = {
            "name": tk.StringVar(),
            "parent_folder": tk.StringVar(value=""),
            "stack": tk.StringVar(),
            "stack_experience": "", # Persistent draft of the experience text
            "goal": "",
            "concept_md": "",
            "todo_md": "",
            "base_project_path": tk.StringVar(),
            "base_project_files": [],
            "include_base_reference": tk.BooleanVar(value=True),

            # LLM Response Buffers (Persistent drafts to prevent data loss on navigation)
            "concept_llm_response": "",
            "stack_llm_response": "",
            "todo_llm_response": "",
            "generate_llm_response": "",

            "concept_segments": {},
            "concept_signoffs": {},
            "todo_phases": [],
            "todo_segments": {},
            "todo_signoffs": {},
        }

        self.project_data["name"].trace_add("write", self.save)
        self.project_data["parent_folder"].trace_add("write", self.save)
        self.project_data["stack"].trace_add("write", self.save)
        self.project_data["base_project_path"].trace_add("write", self.save)

    def get_dict(self):
        c_segs = self.project_data.get("concept_segments", {})
        t_segs = self.project_data.get("todo_segments", {})

        c_md = self.project_data.get("concept_md", "")
        t_md = self.project_data.get("todo_md", "")

        return {
            "current_step": self.current_step,
            "name": self.project_data["name"].get(),
            "parent_folder": self.project_data["parent_folder"].get(),
            "stack": self.project_data["stack"].get(),
            "stack_experience": self.project_data.get("stack_experience", ""),
            "goal": self.project_data.get("goal", ""),
            "concept_md": c_md,
            "todo_md": t_md,
            "base_project_path": self.project_data["base_project_path"].get(),
            "base_project_files": self.project_data["base_project_files"],
            "include_base_reference": self.project_data["include_base_reference"].get(),

            # Persist the raw LLM response buffers
            "concept_llm_response": self.project_data.get("concept_llm_response", ""),
            "stack_llm_response": self.project_data.get("stack_llm_response", ""),
            "todo_llm_response": self.project_data.get("todo_llm_response", ""),
            "generate_llm_response": self.project_data.get("generate_llm_response", ""),

            "concept_segments": c_segs,
            "concept_signoffs": self.project_data.get("concept_signoffs", {}),
            "todo_phases": self.project_data.get("todo_phases", []),
            "todo_segments": t_segs,
            "todo_signoffs": self.project_data.get("todo_signoffs", {})
        }

    def save(self, *args):
        self._recalc_progress()
        session_manager.save_session_data(self.get_dict())

    def load(self, filepath=None):
        loaded_data = session_manager.load_session_data(filepath)
        self.project_data["name"].set(loaded_data.get("name", ""))
        loaded_parent = loaded_data.get("parent_folder", "")
        self.project_data["parent_folder"].set(loaded_parent if loaded_parent and os.path.isdir(loaded_parent) else "")
        self.project_data["stack"].set(loaded_data.get("stack", ""))
        self.project_data["stack_experience"] = loaded_data.get("stack_experience", "")
        self.project_data["goal"] = loaded_data.get("goal", "")
        self.project_data["base_project_path"].set(loaded_data.get("base_project_path", ""))
        self.project_data["base_project_files"] = loaded_data.get("base_project_files", [])
        self.project_data["include_base_reference"].set(loaded_data.get("include_base_reference", True))

        # Restore response buffers
        self.project_data["concept_llm_response"] = loaded_data.get("concept_llm_response", "")
        self.project_data["stack_llm_response"] = loaded_data.get("stack_llm_response", "")
        self.project_data["todo_llm_response"] = loaded_data.get("todo_llm_response", "")
        self.project_data["generate_llm_response"] = loaded_data.get("generate_llm_response", "")

        # Load Concept
        self.project_data["concept_segments"] = loaded_data.get("concept_segments", {})
        self.project_data["concept_signoffs"] = loaded_data.get("concept_signoffs", {})
        self.project_data["concept_md"] = loaded_data.get("concept_md", "")

        # Load TODO
        self.project_data["todo_phases"] = loaded_data.get("todo_phases", [])
        self.project_data["todo_segments"] = loaded_data.get("todo_segments", {})
        self.project_data["todo_signoffs"] = loaded_data.get("todo_signoffs", {})
        self.project_data["todo_md"] = loaded_data.get("todo_md", "")

        # Recalc validity to set the initial accessible step
        self._recalc_progress()

        saved_step = loaded_data.get("current_step", 1)
        if saved_step <= self.max_accessible_step:
            self.current_step = saved_step
        else:
            self.current_step = self.max_accessible_step

    def reset(self):
        # Clear response buffers
        for key in ["concept_llm_response", "stack_llm_response", "todo_llm_response", "generate_llm_response"]:
            self.project_data[key] = ""

        self.project_data["name"].set("")
        self.project_data["parent_folder"].set("")
        self.project_data["stack"].set("")
        self.project_data["stack_experience"] = ""
        self.project_data["goal"] = ""
        self.project_data["concept_md"] = ""
        self.project_data["todo_md"] = ""
        self.project_data["base_project_path"].set("")
        self.project_data["base_project_files"] = []
        self.project_data["include_base_reference"].set(True)
        self.project_data["concept_segments"] = {}
        self.project_data["concept_signoffs"] = {}
        self.project_data["todo_phases"] = []
        self.project_data["todo_segments"] = {}
        self.project_data["todo_signoffs"] = {}
        session_manager.clear_default_session()
        self.current_step = 1
        self.max_accessible_step = 1

    def _recalc_progress(self):
        """Calculates logic flags and updates max_accessible_step."""
        has_details = bool(self.project_data["name"].get())

        c_segs = self.project_data.get("concept_segments", {})
        # Concept is complete ONLY if segments are cleared (merged) AND text exists
        has_concept = (not c_segs) and bool(self.project_data.get("concept_md"))

        t_segs = self.project_data.get("todo_segments", {})
        # TODO is complete ONLY if segments are cleared (merged) AND text exists
        has_todo = (not t_segs) and bool(self.project_data.get("todo_md"))

        # Determine target max based on validity
        target_max = 1
        if has_details:
            target_max = 3
            if has_concept:
                target_max = 5
                if has_todo:
                    target_max = 6

        # We only update max_accessible_step if the new calculated max is HIGHER.
        if target_max > self.max_accessible_step:
            self.max_accessible_step = target_max

    def update_from_view(self, view):
        if not view or not view.winfo_exists(): return

        if hasattr(view, 'save_state'):
             view.save_state()
        if hasattr(view, 'get_goal_content'):
            self.project_data["goal"] = view.get_goal_content()
        if hasattr(view, 'get_stack_content'):
            self.project_data["stack"].set(view.get_stack_content())
        if hasattr(view, 'get_experience_content'):
            self.project_data["stack_experience"] = view.get_experience_content()

        # Capture raw LLM responses/input from any view that provides them
        if hasattr(view, 'get_llm_response_content'):
            response_data = view.get_llm_response_content()
            for key, val in response_data.items():
                if key in self.project_data:
                    self.project_data[key] = val

        if hasattr(view, 'get_assembled_content'):
            content, segments, signoffs = view.get_assembled_content()
            view_type = str(type(view))

            # Guard against updating state with empty view initializations
            if "Concept" in view_type:
                if content or segments:
                    self.project_data["concept_md"] = content
                    self.project_data["concept_segments"] = segments
                    self.project_data["concept_signoffs"] = signoffs
            elif "Todo" in view_type:
                if content or segments:
                    self.project_data["todo_md"] = content
                    self.project_data["todo_segments"] = segments
                    self.project_data["todo_signoffs"] = signoffs

        self._recalc_progress()
```

--- End of file ---

--- File: `src/ui/project_starter/starter_validator.py` ---

```python
from pathlib import Path

def validate_step(step, state_data):
    """
    Validates the data for a specific Project Starter step.

    Args:
        step (int): The step number to validate.
        state_data (dict): The project_data dictionary from StarterState.

    Returns:
        tuple: (is_valid, error_title, error_message)
    """
    if step == 1:
        project_name = state_data["name"].get()

        if not project_name:
            return False, "Error", "Project Name is required."

    elif step == 2:
        return True, "", ""

    elif step == 3:
        # Step 3 (Concept) is valid only if merged.
        segments = state_data.get("concept_segments", {})
        if segments:
            return False, "Merge Required", "You must merge the concept segments into a final document before proceeding."

        concept = state_data.get("concept_md", "")
        if not concept:
            return False, "Error", "The concept document cannot be empty."

    elif step == 4:
        # The Stack step is optional.
        return True, "", ""

    elif step == 5:
        # Step 5 (TODO) is valid only if merged.
        segments = state_data.get("todo_segments", {})
        if segments:
            return False, "Merge Required", "You must merge the TODO plan into a final document before proceeding."

        todo = state_data.get("todo_md", "")
        if not todo:
            return False, "Error", "The TODO plan cannot be empty."

    elif step == 6:
        # Validate parent folder here, right before generation
        parent_folder = state_data["parent_folder"].get()
        if not parent_folder:
             return False, "Error", "Parent Folder is required."

        try:
            path_obj = Path(parent_folder)
            if not path_obj.exists():
                return False, "Invalid Path", f"The parent folder does not exist:\n{parent_folder}"
            if not path_obj.is_dir():
                return False, "Invalid Path", f"The path is not a directory:\n{parent_folder}"
        except Exception as e:
            return False, "Invalid Path", f"The parent folder path is invalid.\nError: {e}"

    return True, "", ""
```

--- End of file ---

--- File: `src/ui/project_starter/segment_manager.py` ---

```python
import re
from ...constants import DELIMITER_TEMPLATE

class SegmentManager:
    """
    Helper class for constructing segmented prompts, parsing LLM responses,
    and assembling the final document from segments.
    """

    @staticmethod
    def build_prompt_instructions(segment_keys, friendly_names_map):
        """
        Generates the system instructions enforcing the strict delimiter format.
        Args:
            segment_keys (list): List of keys to include in the prompt.
            friendly_names_map (dict): Mapping from key to display name.
        """
        instructions = [
            "You MUST structure your response using specific section separators.",
            "Do not add any text outside these sections.",
            "For each section, output the delimiter followed immediately by the content and close it.",
            "\nREQUIRED FORMAT:"
        ]

        for key in segment_keys:
            name = friendly_names_map.get(key, key)
            delimiter = DELIMITER_TEMPLATE.format(name=name)
            instructions.append(f"{delimiter}\n... content for {name} ...\n</SECTION>")

        return "\n".join(instructions)

    @staticmethod
    def parse_segments(text):
        """
        Parses the LLM output into a dictionary { "Section Name": "Content" }.
        Uses regex to find <SECTION name="Name"> followed by content.
        """
        # Regex to find <SECTION name="Name"> followed by content until the next section or end of string
        pattern = re.compile(r'<SECTION name="([^"]+)">\s*(.*?)(?=</SECTION>|<SECTION name=|$)', re.DOTALL | re.IGNORECASE)

        matches = pattern.findall(text)
        segments = {}

        if not matches:
            return {}

        for name, content in matches:
            segments[name.strip()] = content.strip()

        return segments

    @staticmethod
    def map_parsed_segments_to_keys(parsed_data, friendly_names_map):
        """
        Converts the dict { "Name": "Content" } to { "internal_key": "Content" }.
        Uses robust matching to handle whitespace, case sensitivity, and common variations.
        """
        def normalize(s):
            # Remove all non-alphanumeric characters for fuzzy matching
            # This handles "Problem & Audience" matching "Problem and Audience" or "ProblemAudience"
            return re.sub(r'[^a-z0-9]', '', s.lower())

        # Map of normalized labels to internal keys
        norm_label_to_key = {normalize(v): k for k, v in friendly_names_map.items()}
        # Map of normalized keys to internal keys (backup if LLM uses internal key name)
        norm_key_to_key = {normalize(k): k for k in friendly_names_map.keys()}

        keyed_data = {}
        for name, content in parsed_data.items():
            norm_name = normalize(name)

            # Match against the descriptive label
            key = norm_label_to_key.get(norm_name)

            # Match against the internal key name
            if not key:
                key = norm_key_to_key.get(norm_name)

            if key:
                keyed_data[key] = content
            else:
                # If no mapping found, keep the original name to avoid data loss
                keyed_data[name] = content
        return keyed_data

    @staticmethod
    def assemble_document(segments_dict, order_keys, friendly_names_map):
        """
        Joins segments into a single Markdown document with headers.
        """
        doc_parts = []
        for key in order_keys:
            if key in segments_dict and segments_dict[key].strip():
                friendly_name = friendly_names_map.get(key, key)
                content = segments_dict[key].strip()
                doc_parts.append(f"## {friendly_name}\n\n{content}")

        return "\n\n".join(doc_parts)
```

--- End of file ---

--- File: `src/ui/project_starter/generator.py` ---

```python
import re
import shutil
import logging
import os
from pathlib import Path
from ...core.merger import get_language_from_path

log = logging.getLogger("CodeMerger")

def sanitize_project_name(name):
    """Sanitizes the project name for use as a folder name."""
    return re.sub(r'[^a-zA-Z0-9_-]+', '-', name.lower()).strip('-')

def prepare_project_directory(parent_folder, project_name, overwrite=False):
    """
    Prepares the target directory.
    Returns: (success: bool, path: Path, message: str)
    """
    sanitized_name = sanitize_project_name(project_name)
    base_dir = Path(parent_folder)
    project_path = base_dir / sanitized_name

    if project_path.exists():
        if overwrite:
            try:
                shutil.rmtree(project_path)
            except Exception as e:
                return False, project_path, "Failed to delete existing folder: " + str(e)
        else:
            return False, project_path, "Project folder already exists."

    try:
        project_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, project_path, "Failed to create project directory: " + str(e)

    return True, project_path, ""

def parse_and_write_files(project_path, llm_output):
    """
    Parses the LLM response for file blocks and writes them to the project path.
    Uses a robust regex to handle whitespace variations and short files.
    """
    # Construct counting logic with fragments for self-processing safety
    PREFIX = "--- "
    FILE_LABEL = "File: "
    EOF_LABEL = "End of file"
    EOF_MARKER = PREFIX + EOF_LABEL + " ---"

    # Use anchored line-start counts
    start_count_pattern = r'^' + re.escape(PREFIX) + re.escape(FILE_LABEL)
    end_count_pattern = r'^' + re.escape(PREFIX) + re.escape(EOF_LABEL)

    start_count = len(re.findall(start_count_pattern, llm_output, re.MULTILINE))
    end_count = len(re.findall(end_count_pattern, llm_output, re.MULTILINE))

    if start_count != end_count:
        return False, [], f"Format Error: Marker mismatch detected ({start_count} starts, {end_count} ends). Please ask the AI to provide the full output again."

    # Pattern constructed using fragments for self-processing safety.
    file_pattern = re.compile(
        re.escape(PREFIX) + r'File: `([^\n`]+)` ---\s*[\r\n]+```[^\n]*[\r\n]+(.*?)\n?```\s*[\r\n]+' + re.escape(EOF_MARKER),
        re.DOTALL
    )

    matches = file_pattern.finditer(llm_output)

    files_created = []
    found_any = False

    for match in matches:
        found_any = True
        file_path_str, content = match.groups()

        # Cleanup potential prefixing from LLM
        clean_rel_path = file_path_str.replace("boilerplate/", "").strip().replace('\\', '/')
        relative_path = Path(clean_rel_path)
        full_path = project_path / relative_path

        try:
            # Security check: Ensure we stay within project path
            if not os.path.normpath(str(full_path)).startswith(os.path.normpath(str(project_path))):
                log.warning("Skipped file outside project: " + file_path_str)
                continue

            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Preserve original sanitization logic
            sanitized_content = "\n".join([line.rstrip() for line in content.splitlines()])

            # This overwrites any pre-copied boilerplate files if the LLM included them
            full_path.write_text(sanitized_content, encoding="utf-8")
            files_created.append(str(relative_path))
        except Exception as e:
            log.error("Failed to write file " + str(relative_path) + ": " + str(e))

    if not found_any:
        # Preserve original return error message
        return False, [], "No valid file blocks were found. Make sure each file is wrapped with '--- File: `path` ---' and '--- End of file ---', and ensure the code is wrapped in standard triple backticks."

    return True, files_created, ""

def write_base_reference_file(project_path, base_path, base_files):
    """
    Creates a project_reference.md file containing all files from the base project's merge list.
    """
    if not base_path or not base_files:
        return False

    output_blocks = []
    output_blocks.append("# Base Project Reference\n\nThis file contains the code from the base project: `" + base_path + "`\n")

    # Construct markers via fragments
    PREFIX = "--- "
    FILE_TAG = "File: "
    EOF_TAG = "End of file"

    for file_info in base_files:
        rel_path = file_info['path']
        full_path = os.path.join(base_path, rel_path)
        if not os.path.isfile(full_path):
            continue

        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()

            language = get_language_from_path(rel_path)

            # Use safe concatenation
            header = f"{PREFIX}{FILE_TAG}`{rel_path}` ---"
            footer = f"{PREFIX}{EOF_TAG} ---"

            block = [
                header,
                "```" + language,
                content,
                "```",
                footer
            ]
            output_blocks.append("\n".join(block))
        except Exception as e:
            log.error("Failed to read base file " + rel_path + " for reference: " + str(e))

    final_content = "\n\n".join(output_blocks)
    ref_file_path = project_path / "project_reference.md"

    try:
        ref_file_path.write_text(final_content, encoding="utf-8")
        return True
    except Exception as e:
        log.error("Failed to write project_reference.md: " + str(e))
        return False
```

--- End of file ---

--- File: `src/ui/project_starter/starter_prompts.py` ---

```python
import os
import tkinter as tk
from ... import constants as c
from ...core import prompts as p
from ...core.paths import REFERENCE_DIR
from .segment_manager import SegmentManager

def get_base_project_content(project_data):
    """
    Collects code from the base project's merge list for inclusion in LLM prompts.
    """
    base_path = project_data.get("base_project_path", tk.StringVar()).get()
    base_files = project_data.get("base_project_files",[])
    if not base_path or not base_files:
        return ""

    content_blocks = ["\n### Example Project Code (For Reference Only)\n"]
    for file_info in base_files:
        rel_path = file_info['path']
        full_path = os.path.join(base_path, rel_path)
        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            content_blocks.append(f"--- File: `{rel_path}` ---\n```\n{content}\n```\n")
        except Exception:
            pass
    return "\n".join(content_blocks)

def get_concept_prompt(project_data, questions_map):
    """Constructs the prompt for Step 3: Concept."""
    user_goal = project_data.get("goal", "")
    friendly_map = {k: v["label"] for k, v in questions_map.items()}
    segment_instructions = SegmentManager.build_prompt_instructions(c.CONCEPT_ORDER, friendly_map)

    parts =[
        p.STARTER_CONCEPT_PROMPT_INTRO,
        "\n### User Goal\n```\n" + user_goal.strip() + "\n```",
        get_base_project_content(project_data),
        "\n### Format Instructions",
        segment_instructions,
        p.STARTER_CONCEPT_PROMPT_CORE_INSTR
    ]
    return "\n".join(parts)

def get_stack_prompt(project_data):
    """Constructs the prompt for Step 4: Stack."""
    concept = project_data.get("concept_md", "")
    experience = project_data.get("stack_experience", "")
    parts =[
        p.STARTER_STACK_PROMPT_INTRO,
        "\n### Developer Experience\n```\n" + (experience if experience.strip() else "No specific experience listed. Recommend standard industry defaults.") + "\n```",
        "\n### Project Concept\n```markdown\n" + concept + "\n```",
        p.STARTER_STACK_PROMPT_INSTR
    ]
    return "\n".join(parts)

def get_todo_prompt(project_data, questions_map):
    """Constructs the prompt for Step 5: TODO."""
    concept_md = project_data.get("concept_md")
    if not concept_md and project_data.get("concept_segments"):
        concept_md = SegmentManager.assemble_document(project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS)

    stack = project_data["stack"].get()
    example_code = get_base_project_content(project_data)

    template_path = os.path.join(REFERENCE_DIR, "todo.md")
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            todo_template = f.read()
    except Exception:
        todo_template = "(Template not found)"

    valid_headers = [v for k, v in c.TODO_PHASES.items()]
    headers_str = ", ".join([f'"{h}"' for h in valid_headers])

    parts =[
        p.STARTER_TODO_PROMPT_INTRO,
        "\n### Tech Stack\n" + stack,
        "\n### Project Concept\n```markdown\n" + (concept_md or "No concept provided.") + "\n```",
        example_code,
        "\n### Reference Template (Standard TODO List)\n```markdown\n" + todo_template + "\n```",
        p.STARTER_TODO_PROMPT_INSTR.format(headers_str=headers_str)
    ]
    return "\n".join(parts)
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/sidebar_item.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label
from .... import constants as c
from ...assets import assets
from ...tooltip import ToolTip

class SidebarItem(Frame):
    def __init__(self, parent, text, is_overview, status_var=None, command=None):
        super().__init__(parent, bg=c.DARK_BG, cursor="hand2")
        self.command = command
        self.is_selected = False
        self.is_disabled = False
        self.is_updated = False # Indicates content was changed via sync but not viewed
        self.status_var = status_var
        self.is_overview = is_overview
        self.parent_tooltip = None

        # Alignment: Overview (Full Text) is the parent. Segments are children.
        if not is_overview:
            # Indicator for segments (Uses lock graphics)
            self.indicator = Label(self, bg=c.DARK_BG, image=assets.unlocked_icon)
            self.indicator.pack(side="left", padx=(5, 5))
            self.indicator_tooltip = ToolTip(self.indicator, "Lock segment", delay=500)
            text_padx = (0, 10)
        else:
            # No indicator for Full Text, align to far left
            self.indicator = Label(self, bg=c.DARK_BG)
            text_padx = (5, 10)

        label_text = text
        font = c.FONT_BOLD if is_overview else c.FONT_NORMAL

        self.label = Label(self, text=label_text, bg=c.DARK_BG, fg=c.TEXT_COLOR, font=font, anchor="w")
        self.label.pack(side="left", fill="x", expand=True, pady=8, padx=text_padx)

        self._bind_events()

        if self.status_var:
            self.status_var.trace_add("write", self._update_status_icon)
            self._update_status_icon()

    def _bind_events(self):
        self.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)
        if hasattr(self, 'indicator') and not self.is_overview:
            # Use dedicated toggle handler for the icon. Bind to Button-1 for instant feedback.
            self.indicator.bind("<Button-1>", self._on_indicator_click, add="+")

            # Tooltip Handoff: Suppress parent tooltip when hovering the lock icon
            self.indicator.bind("<Enter>", self._on_indicator_hover, add="+")
            self.indicator.bind("<Leave>", self._on_indicator_leave, add="+")

    def _unbind_events(self):
        self.unbind("<Button-1>")
        self.label.unbind("<Button-1>")
        if hasattr(self, 'indicator'): self.indicator.unbind("<Button-1>")

    def _on_click(self, event=None):
        if not self.is_disabled and self.command:
            self.command()

    def _on_indicator_click(self, event):
        """Toggles the locked state instantly and prevents navigation."""
        if not self.is_disabled and self.status_var:
            self.status_var.set(not self.status_var.get())
        return "break"

    def _on_indicator_hover(self, event):
        """Hides the parent navigation tooltip so only the lock tooltip shows."""
        if self.parent_tooltip:
            self.parent_tooltip.hide_tooltip()
            self.parent_tooltip.cancel_show()

    def _on_indicator_leave(self, event):
        """Allows the parent tooltip to show again when moving back to the label/frame."""
        if self.parent_tooltip:
            self.parent_tooltip.schedule_show()

    def link_parent_tooltip(self, tooltip_obj):
        """Stores a reference to the tooltip created for the whole sidebar item."""
        self.parent_tooltip = tooltip_obj

    def register_indicator_info(self, info_mgr):
        """Allows external registration of the indicator label with the Info Panel."""
        if hasattr(self, 'indicator') and not self.is_overview:
            info_mgr.register(self.indicator, "starter_seg_indicator")

    def set_selected(self, selected):
        if self.is_disabled: return
        self.is_selected = selected
        bg = c.TEXT_INPUT_BG if selected else c.DARK_BG
        self.config(bg=bg)
        self.label.config(bg=bg)
        self.indicator.config(bg=bg)

    def set_disabled(self, disabled):
        self.is_disabled = disabled

        if disabled:
            fg = "#666666" # Clearly disabled gray
            cursor = "arrow"
            self._unbind_events()
            # If item was selected, visually deselect it immediately
            if self.is_selected:
                self.is_selected = False
                self.config(bg=c.DARK_BG)
                self.label.config(bg=c.DARK_BG)
                self.indicator.config(bg=c.DARK_BG)
        else:
            fg = c.TEXT_COLOR
            cursor = "hand2"
            self._bind_events()

        self.config(cursor=cursor)
        self.label.config(fg=fg, cursor=cursor)
        self.indicator.config(cursor=cursor)

    def set_updated(self, updated):
        """Marks the item as having pending changes from a sync operation."""
        # Don't show updated status if the item is signed off or disabled
        if self.is_disabled or (self.status_var and self.status_var.get()):
            return
        self.is_updated = updated
        self._update_status_icon()

    def _update_status_icon(self, *args):
        if not self.status_var or self.is_overview: return

        is_locked = self.status_var.get()
        if is_locked:
            # Locked: Use locked icon
            self.indicator.config(image=assets.locked_icon)
            if hasattr(self, 'indicator_tooltip'):
                self.indicator_tooltip.text = "Unlock to edit"
        else:
            # Unlocked: Use unlocked icon
            self.indicator.config(image=assets.unlocked_icon)
            if hasattr(self, 'indicator_tooltip'):
                self.indicator_tooltip.text = "Lock segment"

        # Highlight color for sync updates
        if not is_locked and self.is_updated:
            self.label.config(fg=c.ATTENTION)
        else:
            self.label.config(fg=c.TEXT_COLOR if not self.is_disabled else "#666666")
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/reviewer_sidebar.py` ---

```python
import tkinter as tk
from tkinter import Frame
from .... import constants as c
from .sidebar_item import SidebarItem
from ...tooltip import ToolTip

class ReviewerSidebar(Frame):
    """
    Manages the left navigation pane of the SegmentedReviewer.
    """
    def __init__(self, parent, segment_keys, friendly_names_map, signoff_vars, on_navigate_callback, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, width=220, **kwargs)
        self.pack_propagate(False)

        self.segment_keys = segment_keys
        self.friendly_names_map = friendly_names_map
        self.signoff_vars = signoff_vars
        self.on_navigate = on_navigate_callback
        self.items = {}

        self._build_ui()

    def _build_ui(self):
        for key in self.segment_keys:
            name = self.friendly_names_map.get(key, key)
            item = SidebarItem(
                self, name, False,
                status_var=self.signoff_vars[key],
                command=lambda k=key: self.on_navigate(k)
            )
            item.pack(fill="x")

            # Create the parent ToolTip and link it to the item so the item can suppress it
            item_tooltip = ToolTip(item, f"Navigate to {name}", delay=500)
            item.link_parent_tooltip(item_tooltip)

            self.items[key] = item

    def set_active(self, active_key):
        """Updates the selection highlight in the sidebar."""
        for key, item in self.items.items():
            item.set_selected(key == active_key)

    def mark_updated(self, key, is_updated):
        """Marks a segment as having pending sync changes."""
        if key in self.items:
            self.items[key].set_updated(is_updated)

    def register_info(self, info_mgr):
        """Registers sidebar components with the Info Panel."""
        info_mgr.register(self, "starter_seg_nav")
        for item in self.items.values():
            item.register_indicator_info(info_mgr)
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/reviewer_questions.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, messagebox
from .... import constants as c
from ....core import prompts as p
from ...widgets.rounded_button import RoundedButton
from ...tooltip import ToolTip

class ReviewerQuestions(Frame):
    """
    Encapsulates the guiding questions panel and prompt generation logic.
    """
    def __init__(self, parent, questions_map, get_context_callback, **kwargs):
        super().__init__(parent, bg=c.STATUS_BG, padx=10, pady=10, **kwargs)
        self.questions_map = questions_map
        self.get_context_callback = get_context_callback

        self.current_key = None
        self.current_q_list = []
        self.current_index = 0

    def update_for_segment(self, key):
        """Rebuilds the panel content for the specified segment."""
        self.current_key = key
        for w in self.winfo_children():
            w.destroy()

        self.current_q_list = self.questions_map.get(key, {}).get("questions", [])
        self.current_index = 0

        if not self.current_q_list:
            Label(self, text="No specific questions for this segment.", bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack()
            return

        header = Frame(self, bg=c.STATUS_BG)
        header.pack(fill="x")
        Label(header, text="Review Question:", font=c.FONT_BOLD, bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack(side="left")

        nav = Frame(header, bg=c.STATUS_BG)
        nav.pack(side="right")

        self.prev_btn = RoundedButton(nav, text="<", command=lambda: self._move(-1), width=24, height=24, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2")
        self.prev_btn.pack(side="left")

        self.next_btn = RoundedButton(nav, text=">", command=lambda: self._move(1), width=24, height=24, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, cursor="hand2")
        self.next_btn.pack(side="left", padx=5)

        self.lbl_text = Label(self, text="", justify="left", anchor="w", bg=c.STATUS_BG, fg=c.TEXT_COLOR, wraplength=550, font=c.FONT_NORMAL)
        self.lbl_text.pack(fill="x", pady=(5, 10))

        btn_row = Frame(self, bg=c.STATUS_BG)
        btn_row.pack(anchor="w")

        self.copy_btn = RoundedButton(btn_row, text="Copy Context & Question", command=self._copy_q_context, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=26, cursor="hand2")
        self.copy_btn.pack(side="left")
        ToolTip(self.copy_btn, "Copy a prompt containing the current segment text and this question", delay=500)

        self._refresh_display()

    def _move(self, delta):
        self.current_index = max(0, min(self.current_index + delta, len(self.current_q_list) - 1))
        self._refresh_display()

    def _refresh_display(self):
        idx = self.current_index
        self.lbl_text.config(text=self.current_q_list[idx])
        self.prev_btn.set_state("normal" if idx > 0 else "disabled")
        self.next_btn.set_state("normal" if idx < len(self.current_q_list) - 1 else "disabled")

    def _copy_q_context(self):
        question = self.current_q_list[self.current_index]
        context_data = self.get_context_callback() # Expected to return (context_str, current_name, current_text)

        context_str, current_name, current_text = context_data

        prompt = p.STARTER_QUESTION_PROMPT_TEMPLATE.format(
            context_label="Context",
            context_content=context_str,
            focus_name=current_name,
            focus_content=current_text,
            question=question,
            instruction_suffix=f"Focus ONLY on the segment '{current_name}'. Please answer the question or provide critical feedback regarding this segment. Do NOT rewrite the text."
        )

        try:
            self.clipboard_clear()
            self.clipboard_append(prompt)
            self.copy_btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: self.copy_btn.config(text="Copy Context & Question", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if self.copy_btn.winfo_exists() else None)
        except tk.TclError:
            messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.", parent=self)
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/reviewer_footer.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...tooltip import ToolTip
from ...assets import assets

class ReviewerFooter(Frame):
    """
    Manages the action buttons at the bottom of the SegmentedReviewer.
    """
    def __init__(self, parent, on_sign_off, on_revert, on_sync, on_merge, **kwargs):
        super().__init__(parent, bg=c.DARK_BG, **kwargs)
        self.on_sign_off = on_sign_off
        self.on_revert = on_revert
        self.on_sync = on_sync
        self.on_merge = on_merge

        self._build_ui()

    def _build_ui(self):
        self.container = Frame(self, bg=c.DARK_BG)
        self.container.pack(fill='x', expand=True)

        # Sign-off Group
        self.signoff_group = Frame(self.container, bg=c.DARK_BG)
        Label(self.signoff_group, image=assets.unlocked_icon, bg=c.DARK_BG).pack(side="left", padx=(0, 10))
        self.signoff_btn = RoundedButton(
            self.signoff_group, text="Lock segment & Next",
            command=self.on_sign_off, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT,
            font=c.FONT_BUTTON, width=200, cursor="hand2"
        )
        self.signoff_btn.pack(side="left")
        ToolTip(self.signoff_btn, "Lock this section and move to the next incomplete part", delay=500)

        # Revert Group
        self.revert_group = Frame(self.container, bg=c.DARK_BG)
        self.revert_btn = RoundedButton(
            self.revert_group, text="Unlock to edit",
            command=self.on_revert, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT,
            font=c.FONT_SMALL_BUTTON, width=130, cursor="hand2"
        )
        self.revert_btn.pack(side="left")
        Label(self.revert_group, image=assets.locked_icon, bg=c.DARK_BG).pack(side="left", padx=(10, 0))
        ToolTip(self.revert_btn, "Release the lock to make further changes to this section", delay=500)

        # Utility Buttons
        self.sync_btn = RoundedButton(self.container, text="Sync Unsigned", command=self.on_sync, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_SMALL_BUTTON, width=130, cursor="hand2")
        ToolTip(self.sync_btn, "Propagates your changes to other unlocked sections to maintain consistency.", delay=500)

        self.merge_btn = RoundedButton(self.container, text="Merge Segments", command=self.on_merge, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, width=160, cursor="hand2")
        ToolTip(self.merge_btn, "Finalize all segments and merge them into a single document", delay=500)

    def update_state(self, is_signed, all_signed, has_changes, has_other_unsigned, current_text_exists):
        """Orchestrates the visibility of buttons based on the segment state."""
        self.signoff_group.pack_forget()
        self.revert_group.pack_forget()
        self.sync_btn.pack_forget()
        self.merge_btn.pack_forget()

        if all_signed:
            self.merge_btn.pack(side="right")
            self.revert_group.pack(side="left", padx=(0, 10))
            return

        if is_signed:
            self.revert_group.pack(side="left", padx=(0, 10))
        else:
            self.signoff_group.pack(side="right")
            if has_other_unsigned and has_changes and current_text_exists:
                self.sync_btn.pack(side="left")

    def register_info(self, info_mgr):
        info_mgr.register(self.signoff_btn, "starter_seg_signoff")
        info_mgr.register(self.sync_btn, "starter_seg_sync")
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/notes_dialog.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...widgets.markdown_renderer import MarkdownRenderer
from ...window_utils import position_window
from ....core.paths import ICON_PATH

class NotesDisplayDialog(tk.Toplevel):
    """
    A modal dialog to display changes/explanations from the LLM.
    """
    def __init__(self, parent, notes_text):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.title("Change Summary & Explanation")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Use grid to ensure layout is respected in smaller window sizes
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        Label(main_frame, text="Review Changes", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Explicit height for the internal text widget ensures the window doesn't request
        # too much space, while grid layout ensures the button isn't pushed off screen.
        self.renderer = MarkdownRenderer(main_frame, base_font_size=11, height=8)
        self.renderer.grid(row=1, column=0, sticky="nsew")
        self.renderer.set_markdown(notes_text)

        btn_frame = Frame(main_frame, bg=c.DARK_BG)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))

        ok_button = RoundedButton(btn_frame, text="Got it", command=self.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
        ok_button.pack(side="right")

        # position_window uses NOTES_DIALOG_DEFAULT_GEOMETRY (600x350)
        position_window(self)

        self.deiconify()
        ok_button.focus_set()
        self.wait_window(self)
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/rewrite_dialog.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, messagebox, Toplevel
import re
from .... import constants as c
from ....core import prompts as p
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...window_utils import position_window
from ..segment_manager import SegmentManager
from ...tooltip import ToolTip
from .notes_dialog import NotesDisplayDialog
from ...info_manager import attach_info_mode
from ...assets import assets

class RewriteUnsignedDialog(Toplevel):
    """
    A dialog that allows the user to input a specific instruction to rewrite
    all unsigned segments (or a full document), generates the prompt, and accepts the result.
    """
    def __init__(self, parent, app_state, segment_context_data, on_apply_callback, is_merged_mode=False):
        super().__init__(parent)
        self.parent = parent
        self.app_state = app_state
        self.segment_context = segment_context_data # Dict containing keys, names, data, signoffs
        self.on_apply_callback = on_apply_callback
        self.is_merged_mode = is_merged_mode
        self.withdraw()

        # Ensure grid is used on the Toplevel so the main frame and info panel never overlap
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title("Rewrite Content" if is_merged_mode else "Rewrite Unsigned Segments")
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

        # Dynamic Geometry for Boot
        initial_w, initial_h = 700, 750
        if self.app_state.info_mode_active:
            initial_h += c.INFO_PANEL_HEIGHT

        self.geometry(f"{initial_w}x{initial_h}")
        self.minsize(600, 600)

        # Info Mode Integration
        self.info_mgr = attach_info_mode(self, self.app_state, manager_type='grid', grid_row=1, toggle_btn=self.info_toggle_btn)
        self.info_mgr.register(self.instruction_text, "rewrite_instruction")
        self.info_mgr.register(self.copy_btn, "rewrite_copy_prompt")
        self.info_mgr.register(self.response_text, "rewrite_response")
        self.info_mgr.register(self.btn_apply, "rewrite_apply")
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")

        position_window(self)
        self.deiconify()

    def _build_ui(self):
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(5, weight=1) # Paste area expands
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        title_text = "Rewrite Document" if self.is_merged_mode else "Rewrite Unsigned Segments"
        desc_text = "Provide an instruction to modify the content. You will see a summary of changes first."

        Label(main_frame, text=title_text, font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 5))
        Label(main_frame, text=desc_text, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Section 1: Your Instruction
        Label(main_frame, text="1. Your Instruction", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.instruction_text = ScrollableText(main_frame, height=4, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.instruction_text.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.instruction_text.text_widget.bind("<KeyRelease>", self._update_copy_button_state)

        # Copy Button Container
        copy_frame = Frame(main_frame, bg=c.DARK_BG)
        copy_frame.grid(row=4, column=0, sticky="e", pady=(0, 20))

        self.copy_btn = RoundedButton(copy_frame, text="Generate & Copy Prompt", command=self._generate_and_copy, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=200, height=28, radius=4, cursor="hand2")
        self.copy_btn.pack(side="right")
        self.copy_btn.set_state("disabled") # Initially disabled
        ToolTip(self.copy_btn, "Create and copy a prompt to modify the drafts based on your instruction", delay=500)

        # Section 2: Paste Response
        Label(main_frame, text="2. Paste LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=5, column=0, sticky="nw", pady=(0, 5))

        self.response_text = ScrollableText(main_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.response_text.grid(row=6, column=0, sticky="nsew", pady=(0, 15))

        # Footer Actions
        footer_frame = Frame(main_frame, bg=c.DARK_BG)
        footer_frame.grid(row=7, column=0, sticky="ew")

        # Info Toggle: Managed by InfoManager.place
        self.info_toggle_btn = Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")

        btn_frame = Frame(footer_frame, bg=c.DARK_BG)
        btn_frame.pack(side='right')

        btn_cancel = RoundedButton(btn_frame, text="Cancel", command=self.destroy, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor="hand2")
        btn_cancel.pack(side="left", padx=(0, 10))

        self.btn_apply = RoundedButton(btn_frame, text="Apply Changes", command=self._on_apply, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=120, height=30, cursor="hand2")
        self.btn_apply.pack(side="left")
        ToolTip(self.btn_apply, "Update the project drafts with the pasted response", delay=500)

    def _update_copy_button_state(self, event=None):
        content = self.instruction_text.get("1.0", "end-1c").strip()
        if content:
            self.copy_btn.set_state("normal")
            self.copy_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.copy_btn.set_state("disabled")
            self.copy_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _generate_and_copy(self):
        instruction = self.instruction_text.get("1.0", "end-1c").strip()
        if not instruction: return

        # Unpack context
        keys = self.segment_context['keys']
        names = self.segment_context['names']
        data = self.segment_context['data']
        signoffs = self.segment_context.get('signoffs', {})

        targets = []
        references = []

        if self.is_merged_mode:
            # Treating full document as a single target block
            targets = ["full_content"]
            target_blocks = [f"{data.get('full_content', '')}"]
            reference_blocks = []
            target_instructions = "Return the complete updated Markdown document."
        else:
            for k in keys:
                if signoffs.get(k, False):
                    references.append(k)
                else:
                    targets.append(k)

            if not targets:
                messagebox.showinfo("Info", "All segments are signed off. Nothing to rewrite.")
                return

            # Build Prompt Blocks
            target_blocks = []
            for t in targets:
                name = names.get(t, t)
                content = data.get(t, "")
                target_blocks.append(f"--- Draft: {name} ---\n{content}\n")

            reference_blocks = []
            for r in references:
                name = names.get(r, r)
                content = data.get(r, "")
                reference_blocks.append(f"--- Locked Section: {name} ---\n{content}\n")

            friendly_map = {k: names.get(k, k) for k in targets}
            target_instructions = SegmentManager.build_prompt_instructions(targets, friendly_map)

        # Build dynamic references block and consistency instruction
        references_str = ""
        consistency_instr = "Ensure the rewritten content is internally consistent."
        if reference_blocks:
            references_str = "\n\n### Locked Sections (Reference Only - DO NOT CHANGE)\n" + "".join(reference_blocks)
            consistency_instr = "Ensure consistency with 'Locked Sections' (Reference Only), but do not modify them."

        prompt = p.STARTER_REWRITE_PROMPT_TEMPLATE.format(
            instruction=instruction,
            references=references_str,
            targets=''.join(target_blocks),
            consistency_instr=consistency_instr,
            target_instructions=target_instructions
        )

        try:
            self.clipboard_clear()
            self.clipboard_append(prompt)
            self.copy_btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: self._update_copy_button_state() if self.copy_btn.winfo_exists() else None)
        except tk.TclError:
            messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.", parent=self)

    def _on_apply(self):
        raw_content = self.response_text.get("1.0", "end-1c").strip()
        if not raw_content:
            messagebox.showwarning("Input Required", "Please paste the LLM response first.", parent=self)
            return

        # Extract Notes
        notes_match = re.search(r"<NOTES>(.*?)</NOTES>", raw_content, re.DOTALL | re.IGNORECASE)
        notes = notes_match.group(1).strip() if notes_match else ""

        # Extract remaining content (all content minus the notes block)
        clean_content = re.sub(r"<NOTES>.*?</NOTES>", "", raw_content, flags=re.DOTALL | re.IGNORECASE).strip()

        if notes:
            NotesDisplayDialog(self, notes)

        self.on_apply_callback(clean_content)
        self.destroy()
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/sync_dialog.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, messagebox, Toplevel
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...window_utils import position_window
from ...tooltip import ToolTip

class SyncUnsignedDialog(Toplevel):
    """
    A dialog to handle the prompt generation and response parsing for propagating changes.
    """
    def __init__(self, parent, prompt, on_apply_callback):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()
        self.prompt = prompt
        self.on_apply_callback = on_apply_callback
        self.result = None

        self.title("Sync Unsigned Segments")
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

        self.geometry("600x600")
        self.minsize(500, 500)
        position_window(self)
        self.deiconify()

    def _build_ui(self):
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        Label(main_frame, text="Propagate Changes", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 10))
        Label(main_frame, text="Update other unsigned segments to match your recent changes.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Step 1: Copy Prompt
        step1_frame = Frame(main_frame, bg=c.DARK_BG)
        step1_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        Label(step1_frame, text="1. Copy Prompt", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")
        copy_btn = RoundedButton(step1_frame, text="Copy", command=lambda: self._copy_prompt(copy_btn), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        copy_btn.pack(side="right")
        ToolTip(copy_btn, "Copy the synchronization prompt to clipboard", delay=500)

        # Step 2: Paste Response
        Label(main_frame, text="2. Paste Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=4, column=0, sticky="w", pady=(15, 5))

        self.response_text = ScrollableText(main_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.response_text.grid(row=5, column=0, sticky="nsew", pady=(0, 15))

        # Actions
        btn_frame = Frame(main_frame, bg=c.DARK_BG)
        btn_frame.grid(row=6, column=0, sticky="e")

        btn_cancel = RoundedButton(btn_frame, text="Cancel", command=self.destroy, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor="hand2")
        btn_cancel.pack(side="left", padx=(0, 10))

        btn_apply = RoundedButton(btn_frame, text="Apply Changes", command=self._on_apply, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=120, height=30, cursor="hand2")
        btn_apply.pack(side="left")
        ToolTip(btn_apply, "Apply the synced content to your unlocked segments", delay=500)

    def _copy_prompt(self, btn):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.prompt)
            btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: btn.config(text="Copy", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if btn.winfo_exists() else None)
        except tk.TclError:
            messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.", parent=self)

    def _on_apply(self):
        content = self.response_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Input Required", "Please paste the LLM response first.", parent=self)
            return

        self.on_apply_callback(content)
        self.destroy()
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/segmented_reviewer.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, messagebox
from .... import constants as c
from ....core import prompts as p
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...widgets.markdown_renderer import MarkdownRenderer
from ...tooltip import ToolTip
from ..segment_manager import SegmentManager
from ...assets import assets

# Extracted Component Imports
from .reviewer_sidebar import ReviewerSidebar
from .reviewer_questions import ReviewerQuestions
from .reviewer_footer import ReviewerFooter
from .rewrite_dialog import RewriteUnsignedDialog
from .sync_dialog import SyncUnsignedDialog

class SegmentedReviewer(Frame):
    """
    Orchestrator widget that presents content in segments with a sidebar for navigation,
    sign-off capability, and a final merge trigger.
    """
    def __init__(self, parent, segment_keys, friendly_names_map, segments_data, signoffs_data, questions_map=None, on_change_callback=None, on_merge_callback=None):
        super().__init__(parent, bg=c.DARK_BG)
        self.parent = parent
        self.segment_keys = segment_keys
        self.friendly_names_map = friendly_names_map
        self.segments_data = segments_data
        self.signoffs_data = signoffs_data
        self.questions_map = questions_map or {}
        self.on_change_callback = on_change_callback
        self.on_merge_callback = on_merge_callback

        self.active_key = None
        self.is_loading_nav = False
        self.current_segment_original_text = ""
        self.questions_visible = False
        self.info_mgr = None

        self.signoff_vars = {}
        for key in self.segment_keys:
            val = self.signoffs_data.get(key, False)
            bv = tk.BooleanVar(value=val)
            bv.trace_add("write", lambda *a, k=key, v=bv: self._on_signoff_var_change(k, v))
            self.signoff_vars[key] = bv

        self._build_ui()

        start_key = self.segment_keys[0] if self.segment_keys else None
        if start_key:
            for key in self.segment_keys:
                if not self.signoff_vars[key].get():
                    start_key = key
                    break
            self._navigate(start_key)

    def _build_ui(self):
        # Sidebar
        self.sidebar = ReviewerSidebar(
            self, self.segment_keys, self.friendly_names_map, self.signoff_vars,
            on_navigate_callback=self._navigate
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))

        # Content Container
        self.content_area = Frame(self, bg=c.DARK_BG)
        self.content_area.pack(side="left", fill="both", expand=True)

        self.header_frame = Frame(self.content_area, bg=c.DARK_BG)
        self.header_frame.pack(side="top", fill="x", pady=(0, 10))
        self.title_label = Label(self.header_frame, text="", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR)
        self.title_label.pack(side="left")

        self.header_controls = Frame(self.header_frame, bg=c.DARK_BG)
        self.header_controls.pack(side="right")

        self.main_view_container = Frame(self.content_area, bg=c.DARK_BG)
        self.main_view_container.pack(fill="both", expand=True)

        # Footer
        self.footer = ReviewerFooter(
            self.main_view_container,
            on_sign_off=self._sign_off,
            on_revert=self._revert_draft,
            on_sync=self._open_sync_dialog,
            on_merge=self._handle_final_merge
        )
        self.footer.pack(side="bottom", fill="x", pady=(10, 0))

        # Questions Panel
        self.questions_panel = ReviewerQuestions(
            self.main_view_container, self.questions_map,
            get_context_callback=self._get_question_context
        )

        # Display (Editor/Renderer)
        self.display_container = Frame(self.main_view_container, bg=c.DARK_BG)
        self.display_container.pack(side="top", fill="both", expand=True)
        self.display_container.grid_rowconfigure(0, weight=1)
        self.display_container.grid_columnconfigure(0, weight=1)

        self.editor = ScrollableText(
            self.display_container, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.parent.starter_controller.font_size),
            on_zoom=self.parent.starter_controller.adjust_font_size
        )
        self.editor.text_widget.bind("<KeyRelease>", self._on_text_change)

        self.renderer = MarkdownRenderer(
            self.display_container,
            base_font_size=self.parent.starter_controller.font_size,
            on_zoom=self.parent.starter_controller.adjust_font_size
        )
        self.renderer.text_widget.bind("<Double-Button-1>", self._on_renderer_double_click)

    def _navigate(self, key):
        if self.is_loading_nav: return
        self.is_loading_nav = True

        try:
            if self.active_key and self.active_key in self.segments_data:
                self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()

            self.active_key = None
            self.sidebar.set_active(key)
            self.sidebar.mark_updated(key, False)

            for w in self.header_controls.winfo_children(): w.destroy()

            self.questions_panel.pack_forget()
            self.editor.grid_forget()
            self.renderer.grid_forget()
            self.editor.text_widget.config(state="normal")
            self.editor.delete("1.0", "end")

            self._show_segment(key)
            self.active_key = key
        finally:
            self.is_loading_nav = False

    def _show_segment(self, key):
        name = self.friendly_names_map.get(key, key)
        self.title_label.config(text=name)
        self.current_segment_original_text = self.segments_data.get(key, "")
        self.editor.insert("1.0", self.current_segment_original_text)

        # Header Buttons
        self.q_btn = RoundedButton(self.header_controls, text="Questions", command=self._toggle_questions, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, cursor="hand2")
        self.q_btn.pack(side="left")
        ToolTip(self.q_btn, "Toggle guiding questions to help refine this section.", delay=500)

        self.rewrite_btn = RoundedButton(self.header_controls, text="Rewrite", command=self._open_rewrite_dialog, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BOLD, height=24, cursor="hand2")
        self.rewrite_btn.pack(side="left", padx=(10, 0))
        ToolTip(self.rewrite_btn, "Give an instruction to modify all unsigned segments at once.", delay=500)

        self.is_raw_mode = tk.BooleanVar(value=False)
        self.view_btn = RoundedButton(self.header_controls, text="Edit", command=self._toggle_view, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="left", padx=(10, 0))
        self.view_btn_tooltip = ToolTip(self.view_btn, "", delay=500)

        self.questions_panel.update_for_segment(key)
        self._toggle_view(force_render=True)
        self._update_footer_state(key)
        self._apply_questions_visibility()
        self._register_transient_info()

    def _on_signoff_var_change(self, key, var):
        self.signoffs_data[key] = var.get()
        if self.on_change_callback: self.on_change_callback()
        if key == self.active_key:
            self._update_footer_state()
        else:
            self._update_footer_buttons_only()

    def _update_footer_state(self, key=None):
        target_key = key or self.active_key
        if not target_key: return

        is_signed = self.signoff_vars[target_key].get()
        all_signed = all(self.signoff_vars[k].get() for k in self.segment_keys)

        if is_signed:
            self._toggle_view(force_render=True)
            self.view_btn.pack_forget()
            self.rewrite_btn.pack_forget()
            self.editor.text_widget.config(state="disabled", bg=c.DARK_BG)
        else:
            # Re-pack in specific order to maintain visual layout
            self.q_btn.pack(side="left")
            self.rewrite_btn.pack(side="left", padx=(10, 0))
            self.view_btn.pack(side="left", padx=(10, 0))
            self.editor.text_widget.config(state="normal", bg=c.TEXT_INPUT_BG)

        self._update_footer_buttons_only(target_key, is_signed, all_signed)

    def _update_footer_buttons_only(self, target_key=None, is_signed=None, all_signed=None):
        target_key = target_key or self.active_key
        if not target_key: return

        if is_signed is None:
            is_signed = self.signoff_vars[target_key].get()
        if all_signed is None:
            all_signed = all(self.signoff_vars[k].get() for k in self.segment_keys)

        current_text = self.segments_data.get(target_key, "").strip()
        has_changes = current_text != self.current_segment_original_text
        other_unsigned = any(not self.signoff_vars[k].get() for k in self.segment_keys if k != target_key)

        self.footer.update_state(
            is_signed=is_signed,
            all_signed=all_signed,
            has_changes=has_changes,
            has_other_unsigned=other_unsigned,
            current_text_exists=bool(current_text)
        )

    def _toggle_questions(self):
        self.questions_visible = not self.questions_visible
        self._apply_questions_visibility()

    def _apply_questions_visibility(self):
        if not hasattr(self, 'q_btn') or not self.q_btn.winfo_exists(): return
        if self.questions_visible:
            if not self.questions_panel.winfo_ismapped():
                self.questions_panel.pack(side="top", fill="x", before=self.display_container, pady=(0, 10))
            self.q_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.questions_panel.pack_forget()
            self.q_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _on_text_change(self, event=None):
        if self.is_loading_nav or self.active_key is None: return
        current_text = self.editor.get("1.0", "end-1c").strip()
        self.segments_data[self.active_key] = current_text
        if self.on_change_callback: self.on_change_callback()
        self._update_footer_state()

    def _get_question_context(self):
        """Callback for the questions panel to gather data for prompt creation."""
        context = ""
        for k in self.segment_keys:
            if k == self.active_key: continue
            txt = self.segments_data.get(k, "").strip()
            if txt: context += f"--- Context: {self.friendly_names_map.get(k, k)} ---\n{txt}\n\n"

        current_text = self.editor.get("1.0", "end-1c").strip()
        current_name = self.friendly_names_map.get(self.active_key, self.active_key)
        return context, current_name, current_text

    def _toggle_view(self, force_render=False):
        if force_render: self.is_raw_mode.set(False)
        else: self.is_raw_mode.set(not self.is_raw_mode.get())

        if self.is_raw_mode.get():
            self.renderer.grid_forget()
            self.editor.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Render", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.view_btn_tooltip.text = "Switch to stylized Markdown preview"
        else:
            self.editor.text_widget.tag_remove("sel", "1.0", "end")
            self.renderer.set_markdown(self.editor.get("1.0", "end-1c"))
            self.editor.grid_forget()
            self.renderer.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Edit", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            self.view_btn_tooltip.text = "Switch to raw text editor"

        if self.view_btn_tooltip.tooltip_window:
            self.view_btn_tooltip.hide_tooltip()
            self.view_btn_tooltip.show_tooltip()

    def _on_renderer_double_click(self, event):
        if self.signoff_vars[self.active_key].get(): return
        try: click_index = self.renderer.text_widget.index(f"@{event.x},{event.y}")
        except Exception: click_index = "1.0"
        self._toggle_view(force_render=False)
        self.editor.update_idletasks()
        self.editor.text_widget.mark_set("insert", click_index)
        self.editor.text_widget.see(click_index)
        self.editor.text_widget.focus_set()

    def _sign_off(self):
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        self.signoff_vars[self.active_key].set(True)
        self._update_footer_state()

        next_key = None
        current_idx = self.segment_keys.index(self.active_key)
        for i in range(current_idx + 1, len(self.segment_keys)):
            if not self.signoff_vars[self.segment_keys[i]].get():
                next_key = self.segment_keys[i]; break
        if not next_key:
            for i in range(0, current_idx):
                if not self.signoff_vars[self.segment_keys[i]].get():
                    next_key = self.segment_keys[i]; break
        if next_key: self._navigate(next_key)

    def _revert_draft(self):
        self.signoff_vars[self.active_key].set(False)
        self._update_footer_state()

    def _open_sync_dialog(self):
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        targets, references = [],[]
        for k in self.segment_keys:
            if k == self.active_key: continue
            if self.signoff_vars[k].get(): references.append(k)
            else: targets.append(k)
        if not targets: messagebox.showinfo("Nothing to Sync", "All other segments are signed off."); return

        target_context_str = "\n".join([f"--- Current Draft: {self.friendly_names_map.get(k, k)} ---\n{self.segments_data.get(k, '')}\n" for k in targets])
        ref_context_str = ""
        if references:
            ref_context_str = "\n### Locked Sections (Reference Only)\n" + "\n".join([f"--- Locked Section: {self.friendly_names_map.get(k, k)} ---\n{self.segments_data.get(k, '')}\n" for k in references])

        prompt = p.STARTER_SYNC_PROMPT_TEMPLATE.format(
            current_name=self.friendly_names_map.get(self.active_key, self.active_key),
            content=self.segments_data[self.active_key],
            ref_context=ref_context_str,
            target_context=target_context_str,
            target_instructions=SegmentManager.build_prompt_instructions(targets, self.friendly_names_map)
        )
        SyncUnsignedDialog(self, prompt, self._apply_sync_results)

    def _open_rewrite_dialog(self):
        self.segments_data[self.active_key] = self.editor.get("1.0", "end-1c").strip()
        context_data = {
            'keys': self.segment_keys, 'names': self.friendly_names_map, 'data': self.segments_data,
            'signoffs': {k: self.signoff_vars[k].get() for k in self.segment_keys}
        }
        app_state = self.parent.starter_controller.app.app_state
        RewriteUnsignedDialog(self, app_state, context_data, self._apply_sync_results)

    def _apply_sync_results(self, llm_output):
        parsed = SegmentManager.parse_segments(llm_output)
        if not parsed: messagebox.showerror("Error", "Could not parse segments."); return
        mapped = SegmentManager.map_parsed_segments_to_keys(parsed, self.friendly_names_map)
        updated_count = 0
        for key, content in mapped.items():
            if key in self.segments_data and not self.signoff_vars[key].get():
                self.segments_data[key] = content
                if key == self.active_key:
                    self.editor.text_widget.config(state="normal")
                    self.editor.delete("1.0", "end")
                    self.editor.insert("1.0", content)
                    if not self.is_raw_mode.get(): self.renderer.set_markdown(content)
                else:
                    self.sidebar.mark_updated(key, True)
                updated_count += 1
        if updated_count > 0 and self.on_change_callback: self.on_change_callback()

    def _handle_final_merge(self):
        if not self.on_merge_callback: return
        if not messagebox.askyesno("Confirm Merge", "Merge all segments into a single document?\n\nThis cannot be undone.", parent=self):
            return
        full_text = SegmentManager.assemble_document(self.segments_data, self.segment_keys, self.friendly_names_map)
        self.on_merge_callback(full_text)

    def register_info(self, info_mgr):
        self.info_mgr = info_mgr
        self.sidebar.register_info(info_mgr)
        self.footer.register_info(info_mgr)
        self._register_transient_info()

    def _register_transient_info(self):
        if not self.info_mgr: return
        if hasattr(self, 'q_btn') and self.q_btn.winfo_exists(): self.info_mgr.register(self.q_btn, "starter_seg_questions")
        if hasattr(self, 'rewrite_btn') and self.rewrite_btn.winfo_exists(): self.info_mgr.register(self.rewrite_btn, "starter_seg_rewrite")
        if hasattr(self, 'view_btn') and self.view_btn.winfo_exists(): self.info_mgr.register(self.view_btn, "starter_view_toggle")
        self.info_mgr.register(self.footer.revert_btn, "starter_seg_unlock")
        self.info_mgr.register(self.footer.merge_btn, "starter_seg_merge")

    def refresh_fonts(self, size):
        self.editor.set_font_size(size)
        self.renderer.set_font_size(size)

    def get_assembled_content(self):
        full_text = SegmentManager.assemble_document(self.segments_data, self.segment_keys, self.friendly_names_map)
        return full_text, self.segments_data, self.signoffs_data
```

--- End of file ---

--- File: `src/ui/project_starter/widgets/full_text_reviewer.py` ---

```python
import tkinter as tk
from tkinter import messagebox
import pyperclip
from .... import constants as c
from ....core import prompts as p
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...widgets.markdown_renderer import MarkdownRenderer
from ...tooltip import ToolTip

class FullTextReviewer(tk.Frame):
    """
    A reusable component for reviewing and editing large blocks of Markdown.
    Includes a guiding questions panel, edit/render toggle, and prompt generation logic.
    """
    def __init__(self, parent, title, content, questions, on_text_change_callback, on_rewrite_callback, get_prompt_context_callback, starter_controller):
        super().__init__(parent, bg=c.DARK_BG)
        self.starter_controller = starter_controller
        self.questions = questions or["Review the content for accuracy and clarity."]
        self.on_text_change = on_text_change_callback
        self.on_rewrite = on_rewrite_callback
        self.get_prompt_context = get_prompt_context_callback

        self.current_question_index = 0
        self.is_raw_mode = False
        self.questions_visible = False

        self._build_ui(title, content)

    def _build_ui(self, title, content):
        self.grid_rowconfigure(1, weight=0) # Questions Panel
        self.grid_rowconfigure(2, weight=1) # Main View
        self.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = tk.Frame(self, bg=c.DARK_BG)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(header_frame, text=title, font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        controls = tk.Frame(header_frame, bg=c.DARK_BG)
        controls.pack(side="right")

        self.q_btn = RoundedButton(controls, text="Questions", command=self._toggle_questions, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, cursor="hand2")
        self.q_btn.pack(side="left", padx=(0, 10))
        ToolTip(self.q_btn, "Toggle guiding questions to help refine this section.", delay=500)

        self.rewrite_btn = RoundedButton(controls, text="Rewrite", command=self.on_rewrite, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BOLD, height=24, cursor="hand2")
        self.rewrite_btn.pack(side="left", padx=(0, 10))
        ToolTip(self.rewrite_btn, "Instructional rewrite of the document with change notes.", delay=500)

        self.view_btn = RoundedButton(controls, text="Edit", command=self._toggle_view_mode, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=80, height=24, cursor="hand2")
        self.view_btn.pack(side="left")
        self.view_btn_tooltip = ToolTip(self.view_btn, "Switch to raw text editor", delay=500)

        # Questions Panel
        self.questions_container = tk.Frame(self, bg=c.DARK_BG)

        # Editor/Renderer
        self.view_frame = tk.Frame(self, bg=c.DARK_BG)
        self.view_frame.grid(row=2, column=0, sticky="nsew")
        self.view_frame.grid_rowconfigure(0, weight=1)
        self.view_frame.grid_columnconfigure(0, weight=1)

        self.editor = ScrollableText(
            self.view_frame, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size),
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.editor.insert("1.0", content)
        self.editor.text_widget.bind("<KeyRelease>", self._on_key_release)

        self.renderer = MarkdownRenderer(
            self.view_frame,
            base_font_size=self.starter_controller.font_size,
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.renderer.text_widget.bind("<Double-Button-1>", self._on_renderer_double_click)

        self._apply_view_mode()

    def register_info(self, info_mgr, editor_key="starter_view_toggle"):
        info_mgr.register(self.editor, editor_key)
        info_mgr.register(self.q_btn, "starter_seg_questions")
        info_mgr.register(self.rewrite_btn, "starter_seg_rewrite")
        info_mgr.register(self.view_btn, "starter_view_toggle")

    def refresh_fonts(self, size):
        self.editor.set_font_size(size)
        self.renderer.set_font_size(size)

    def set_content(self, text):
        self.editor.text_widget.config(state="normal")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)
        if not self.is_raw_mode:
            self.renderer.set_markdown(text)

    def get_content(self):
        return self.editor.get("1.0", "end-1c").strip()

    def _on_key_release(self, event=None):
        self.on_text_change(self.get_content())

    def _on_renderer_double_click(self, event):
        try:
            click_index = self.renderer.text_widget.index(f"@{event.x},{event.y}")
        except Exception:
            click_index = "1.0"
        self._toggle_view_mode()
        self.editor.update_idletasks()
        self.editor.text_widget.mark_set("insert", click_index)
        self.editor.text_widget.see(click_index)
        self.editor.text_widget.focus_set()

    def _toggle_view_mode(self):
        self.is_raw_mode = not self.is_raw_mode
        self._apply_view_mode()

    def _apply_view_mode(self):
        if self.is_raw_mode:
            self.renderer.grid_forget()
            self.editor.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Render", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.view_btn_tooltip.text = "Switch to stylized Markdown preview"
        else:
            self.renderer.set_markdown(self.editor.get("1.0", "end-1c"))
            self.editor.grid_forget()
            self.renderer.grid(row=0, column=0, sticky="nsew")
            self.view_btn.config(text="Edit", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
            self.view_btn_tooltip.text = "Switch to raw text editor"

        if self.view_btn_tooltip.tooltip_window:
             self.view_btn_tooltip.hide_tooltip()
             self.view_btn_tooltip.show_tooltip()

    def _toggle_questions(self):
        self.questions_visible = not self.questions_visible
        if self.questions_visible:
            self.questions_container.grid(row=1, column=0, sticky="ew", pady=(0, 10))
            self._create_question_prompter()
            self.q_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.questions_container.grid_remove()
            for widget in self.questions_container.winfo_children():
                widget.destroy()
            self.q_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _create_question_prompter(self):
        if self.questions_container.winfo_children():
            return

        panel = tk.Frame(self.questions_container, bg=c.STATUS_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        panel.pack(fill='x', expand=True)

        content_f = tk.Frame(panel, bg=c.STATUS_BG, padx=10, pady=10)
        content_f.pack(fill='x', expand=True)

        self.question_label = tk.Label(content_f, text="", wraplength=600, justify="left", anchor="w", font=c.FONT_NORMAL, bg=c.STATUS_BG, fg=c.TEXT_COLOR)
        self.question_label.pack(side='left', fill='x', expand=True)

        actions = tk.Frame(content_f, bg=c.STATUS_BG)
        actions.pack(side='left', padx=(10,0))

        nav = tk.Frame(actions, bg=c.STATUS_BG)
        nav.pack(anchor='e')
        self.prev_q = RoundedButton(nav, text="<", command=lambda: self._move_q(-1), width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.prev_q.pack(side="left")
        self.next_q = RoundedButton(nav, text=">", command=lambda: self._move_q(1), width=24, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        self.next_q.pack(side="left", padx=2)

        copy_btn = RoundedButton(actions, text="Copy Context & Question", command=lambda: self._copy_q_prompt(copy_btn), width=160, height=24, font=c.FONT_SMALL_BUTTON, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, cursor="hand2")
        copy_btn.pack(anchor='e', pady=(5, 0))
        ToolTip(copy_btn, "Copy the full text and this question, asking for feedback", delay=500)

        self._update_q_display()

    def _move_q(self, delta):
        self.current_question_index = max(0, min(self.current_question_index + delta, len(self.questions) - 1))
        self._update_q_display()

    def _update_q_display(self):
        if not hasattr(self, 'question_label'): return
        self.question_label.config(text=self.questions[self.current_question_index])
        self.prev_q.set_state("normal" if self.current_question_index > 0 else "disabled")
        self.next_q.set_state("normal" if self.current_question_index < len(self.questions) - 1 else "disabled")

    def _copy_q_prompt(self, btn):
        try:
            current_q = self.questions[self.current_question_index]
            context_label, context_content, focus_name, focus_content = self.get_prompt_context()

            prompt = p.STARTER_QUESTION_PROMPT_TEMPLATE.format(
                context_label=context_label,
                context_content=context_content,
                focus_name=focus_name,
                focus_content=focus_content,
                question=current_q,
                instruction_suffix="Please answer the question or provide critical feedback. Do NOT rewrite the text."
            )

            pyperclip.copy(prompt)
            btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: btn.config(text="Copy Context & Question", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if btn.winfo_exists() else None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy prompt: {e}", parent=self)
```

--- End of file ---

--- File: `src/ui/project_starter/step_details.py` ---

```python
import tkinter as tk
from tkinter import filedialog, messagebox
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..tooltip import ToolTip

class DetailsView(tk.Frame):
    def __init__(self, parent, project_data, starter_controller=None):
        super().__init__(parent, bg=c.DARK_BG)
        self.project_data = project_data
        self.starter_controller = starter_controller # Access to starter methods
        self.config(padx=10, pady=10)

        tk.Label(self, text="Project Details", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=10, anchor="w")
        tk.Label(self, text="Enter the initial details for your new project.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(pady=5, anchor="w")

        form_grid = tk.Frame(self, bg=c.DARK_BG)
        form_grid.pack(pady=20, fill="x", anchor="w")

        form_grid.grid_columnconfigure(0, minsize=150)
        form_grid.grid_columnconfigure(1, weight=1)

        # Row 0: Project Name
        self.name_label_frame = tk.Frame(form_grid, bg=c.DARK_BG)
        self.name_label_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        tk.Label(self.name_label_frame, text="Project Name:", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_NORMAL).pack(anchor="w")
        tk.Label(self.name_label_frame, text="(used for folder name)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=(c.FONT_FAMILY_PRIMARY, 8)).pack(anchor="w")

        self.name_entry = tk.Entry(form_grid, textvariable=self.project_data["name"], width=50, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief="flat", font=c.FONT_NORMAL)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, ipady=4, sticky="ew")

        # Divider
        tk.Frame(self, height=1, bg=c.WRAPPER_BORDER).pack(fill='x', pady=20)

        # Base Project Section
        base_title_frame = tk.Frame(self, bg=c.DARK_BG)
        base_title_frame.pack(anchor="w", pady=(0, 5))

        tk.Label(base_title_frame, text="Or start from an existing project ", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side="left")
        tk.Label(base_title_frame, text="(OPTIONAL):", bg=c.DARK_BG, fg=c.NOTE, font=c.FONT_BOLD).pack(side="left")

        base_frame = tk.Frame(self, bg=c.DARK_BG)
        base_frame.pack(fill='x', anchor='w')

        self.base_btn = RoundedButton(base_frame, text="Select base project", command=self._select_base_project, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.base_btn.pack(side='left')
        ToolTip(self.base_btn, "Pick an existing folder to use its merge list as a reference", delay=500)

        self.base_path_label = tk.Label(base_frame, text="No base project selected", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL)
        self.base_path_label.pack(side='left', padx=10)

        # Update label if path already exists
        self._update_base_label()

        # Tips Section at Bottom
        tips_frame = tk.Frame(self, bg=c.DARK_BG)
        tips_frame.pack(side="bottom", fill="x", anchor="w", pady=(40, 0))

        tk.Label(tips_frame, text="💡 LLM Best Practices", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.NOTE).pack(anchor="w", pady=(0, 2))
        tk.Label(tips_frame, text="- Always start a new conversation with the LLM when pasting a prompt from CodeMerger.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(anchor="w")

    def register_info(self, info_mgr):
        """Registers step-specific widgets for Info Mode."""
        if not info_mgr: return
        info_mgr.register(self.name_label_frame, "starter_details_name")
        info_mgr.register(self.name_entry, "starter_details_name")
        info_mgr.register(self.base_btn, "starter_details_base")
        info_mgr.register(self.base_path_label, "starter_details_base")

    def _select_base_project(self):
        folder_selected = filedialog.askdirectory(title="Select Base Project")
        if folder_selected:
            self.project_data["base_project_path"].set(folder_selected)
            self._update_base_label()
            if self.starter_controller:
                self.starter_controller.on_base_project_selected(folder_selected)

    def _update_base_label(self):
        path = self.project_data["base_project_path"].get()
        if path:
            self.base_path_label.config(text=path, fg=c.TEXT_COLOR)
        else:
            self.base_path_label.config(text="No base project selected", fg=c.TEXT_SUBTLE_COLOR)

    def handle_reset(self):
        """Resets the input fields for this step."""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset project details?", parent=self):
            self.project_data["name"].set("")
            self.project_data["base_project_path"].set("")
            self._update_base_label()
```

--- End of file ---

--- File: `src/ui/project_starter/step_base_files.py` ---

```python
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from ...core.project_config import ProjectConfig
from ...core.utils import parse_gitignore
from ... import constants as c
from ..file_manager.ui_setup import setup_file_manager_ui
from ..file_manager.ui_controller import FileManagerUIController
from ..file_manager.data_controller import FileManagerDataController
from ..file_manager.selection_list_controller import SelectionListController
from ..file_manager.file_tree_handler import FileTreeHandler
from ..file_manager.state_controller import FileManagerStateController
from ..file_manager.order_request_handler import OrderRequestHandler
from ..widgets.rounded_button import RoundedButton

class StepBaseFilesView(tk.Frame):
    def __init__(self, parent, starter_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.starter_controller = starter_controller
        self.project_data = project_data
        self.app = starter_controller.app
        self.base_dir = project_data["base_project_path"].get()
        self.selection_handler = None  # Initialize to None for safety

        # Check existence immediately
        if not self.base_dir or not os.path.isdir(self.base_dir):
            self._init_error_ui()
        else:
            self._init_file_manager_ui()

    def register_info(self, info_mgr):
        """
        Maps the embedded List Editor widgets to their documentation keys.
        """
        if not hasattr(self, 'tree') or not info_mgr:
            return

        # Left Panel (Available Files)
        info_mgr.register(self.tree, "fm_tree")
        info_mgr.register(self.tree_action_button, "fm_tree_action")
        info_mgr.register(self.toggle_gitignore_button, "fm_filter_git")
        info_mgr.register(self.toggle_filter_button, "fm_filter_ext")
        info_mgr.register(self.filter_entry, "fm_filter_text")

        # Reveal icons
        for label in self.folder_icon_labels.values():
            info_mgr.register(label, "fm_reveal")

        # Right Panel (Merge Order)
        info_mgr.register(self.merge_order_list, "fm_list")
        info_mgr.register(self.merge_order_details_label, "fm_tokens")
        info_mgr.register(self.order_request_button, "fm_order")
        info_mgr.register(self.toggle_paths_button, "fm_list_tools")

        # Sorting Controls
        info_mgr.register(self.move_to_top_button, "fm_sort_top")
        info_mgr.register(self.move_up_button, "fm_sort_up")
        info_mgr.register(self.remove_button, "fm_sort_remove")
        info_mgr.register(self.move_down_button, "fm_sort_down")
        info_mgr.register(self.move_to_bottom_button, "fm_sort_bottom")

        # Footer
        info_mgr.register(self.add_all_btn, "fm_add_all")
        info_mgr.register(self.remove_all_btn, "fm_remove_all")

    def _init_error_ui(self):
        """Displays a friendly error message when the base directory is missing."""
        # Clean up existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = tk.Frame(self, bg=c.DARK_BG)
        container.grid(row=0, column=0)

        tk.Label(container, text="Base files not found", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.WARN).pack(pady=(0, 10))
        tk.Label(container, text=f"The directory could not be found:\n{self.base_dir}", bg=c.DARK_BG, fg=c.TEXT_COLOR, justify="center").pack(pady=(0, 20))

        RoundedButton(container, text="Select a different folder", command=self._browse_new_folder, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor="hand2").pack()

    def _browse_new_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Base Project", parent=self)
        if folder_selected:
            self.project_data["base_project_path"].set(folder_selected)
            self.base_dir = folder_selected
            self._init_file_manager_ui()

    def _init_file_manager_ui(self):
        """Initializes the full list editor UI for a valid directory."""
        # Clean up any existing widgets (e.g., error UI)
        for widget in self.winfo_children():
            widget.destroy()

        # Mock/Proxy attributes expected by FileManager controllers
        self.status_var = tk.StringVar()
        self.file_extensions = self.app.file_extensions
        self.default_editor = self.app.app_state.default_editor
        self.app_state = self.app.app_state
        self.newly_detected_files = []
        self.full_paths_visible = False
        self.token_count_enabled = self.app_state.config.get('token_count_enabled', c.TOKEN_COUNT_ENABLED_DEFAULT)
        self.is_extension_filter_active = True
        self.is_gitignore_filter_active = True
        self.hovered_file_path = None
        self.sash_pos_normal = None
        self.current_total_tokens = 0

        # Initialize Project Config (Read-Only usage)
        self.project_config = ProjectConfig(self.base_dir)
        self.project_config.load()  # Load existing .allcode if present

        # Restore previous selection from starter state if available, else use project config
        saved_files = self.project_data["base_project_files"]
        if saved_files:
            self.project_config.selected_files = saved_files
            self.project_config.total_tokens = sum(f.get('tokens', 0) for f in saved_files)

        self.current_total_tokens = self.project_config.total_tokens

        # Setup UI
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Description
        self.grid_rowconfigure(2, weight=1)  # Main Editor
        self.grid_rowconfigure(3, weight=0)  # Status bar

        header_frame = tk.Frame(self, bg=c.DARK_BG)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(10, 5), padx=10)
        tk.Label(header_frame, text="Select Base Files", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')

        self.profile_selector_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        self.profile_selector_frame.pack(side='right')

        # Handle Profile Selection if needed
        self._check_profiles()

        tk.Label(self, text="Choose files from the existing project to use as a reference. These will be included in the context for the LLM.", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").grid(row=1, column=0, sticky='w', padx=10)

        # Main Area - The container for the list editor UI
        self.fm_frame = tk.Frame(self, bg=c.DARK_BG)
        self.fm_frame.grid(row=2, column=0, sticky='nsew')

        # Initialize Controllers
        self.gitignore_patterns = parse_gitignore(self.base_dir)
        self.ui_controller = FileManagerUIController(self)
        self.data_controller = FileManagerDataController(self)
        # We don't use the standard state controller's save logic, but we need it for "Add All" etc.
        self.state_controller = FileManagerStateController(self)
        self.order_request_handler = OrderRequestHandler(self)

        # Setup Editor UI with zero-padding overrides to prevent gaps
        setup_file_manager_ui(
            self,
            container=self.fm_frame,
            include_save_button=False,
            bottom_padding=(15, 0),
            main_padding=0,
            main_padx=0
        )

        self.create_handlers()

        # Status Bar for this view - use 'ews' to keep it tight
        self.status_label = tk.Label(self, textvariable=self.status_var, bg=c.DARK_BG, fg=c.STATUS_FG, font=c.FONT_STATUS_BAR, anchor='w')
        self.status_label.grid(row=3, column=0, sticky='ews', padx=10, pady=0)

        # Initial Population
        self.filter_text = tk.StringVar()
        self.filter_entry.config(textvariable=self.filter_text)
        self.filter_text.trace_add('write', self.ui_controller.apply_filter)
        self.clear_filter_button.bind("<Button-1>", self.ui_controller.clear_filter)

        self.tree.bind("<Motion>", self.ui_controller.on_tree_motion)
        self.tree.bind("<Leave>", self.ui_controller.on_tree_leave)

        self.data_controller.validate_and_update_cache()
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.populate_tree()
        self.data_controller.run_token_recalculation()
        self.update_all_button_states()

    def _check_profiles(self):
        profiles = self.project_config.get_profile_names()
        if len(profiles) > 1:
            tk.Label(self.profile_selector_frame, text="Load Profile:", bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left', padx=5)
            self.profile_var = tk.StringVar(value=self.project_config.active_profile_name)
            cb = ttk.Combobox(self.profile_selector_frame, textvariable=self.profile_var, values=profiles, state="readonly", width=15)
            cb.pack(side='left')
            cb.bind("<<ComboboxSelected>>", self._on_profile_change)

    def _on_profile_change(self, event):
        new_profile = self.profile_var.get()
        self.project_config.active_profile_name = new_profile
        # Reload selection from config
        self.selection_handler.set_initial_selection(self.project_config.selected_files)
        self.current_total_tokens = self.project_config.total_tokens
        self.update_all_button_states()
        self.status_var.set(f"Loaded profile: {new_profile}")

    def save_state(self):
        """Updates the starter state with the current selection."""
        # Guard against saving if in error state (selection_handler is None)
        if self.selection_handler:
            self.project_data["base_project_files"] = self.selection_handler.ordered_selection

    # Methods mimicking FileManagerWindow
    def create_handlers(self):
        self.item_map = {}
        self.path_to_item_id = {}
        listbox_buttons = {
            'top': self.move_to_top_button, 'up': self.move_up_button,
            'remove': self.remove_button, 'down': self.move_down_button,
            'bottom': self.move_to_bottom_button
        }
        # Pass self.save_state as callback to ensure state is updated on every change
        self.selection_handler = SelectionListController(
            self, self.merge_order_list, listbox_buttons, self.base_dir, self.default_editor,
            self.on_selection_list_changed, self.token_count_enabled
        )
        self.tree_handler = FileTreeHandler(
            self, self.tree, self.tree_action_button, self.item_map, self.path_to_item_id,
            lambda path: path in [f['path'] for f in self.selection_handler.ordered_selection],
            self.on_file_toggled
        )
        self.tree_action_button.command = self.tree_handler.toggle_selection_for_selected
        self.move_to_top_button.command = self.selection_handler.move_to_top
        self.move_up_button.command = self.selection_handler.move_up
        self.move_down_button.command = self.selection_handler.move_down
        self.move_to_bottom_button.command = self.selection_handler.move_to_bottom
        self.remove_button.command = self.selection_handler.remove_selected

    def populate_tree(self, filter_text=""):
        # Reuse existing logic
        from ..file_manager.file_tree_builder import build_file_tree_data

        expanded_dirs_before_rebuild = set(self.tree_handler.get_expanded_dirs())
        for item in self.tree.get_children(): self.tree.delete(item)
        self.item_map.clear(); self.path_to_item_id.clear()
        selected_paths = {f['path'] for f in self.selection_handler.ordered_selection}

        tree_data = build_file_tree_data(
            self.base_dir,
            self.file_extensions,
            self.gitignore_patterns,
            filter_text,
            self.is_extension_filter_active,
            selected_paths,
            self.is_gitignore_filter_active
        )
        def _insert_nodes(parent_id, nodes):
            for node in nodes:
                tags = ()

                # Check for expanded state in both current UI and saved project config
                is_open = (node.get('path') in expanded_dirs_before_rebuild) or \
                          (node.get('path') in self.project_config.expanded_dirs)

                item_id = self.tree.insert(parent_id, 'end', text=node['name'], open=is_open, tags=tags)
                self.item_map[item_id] = {'path': node['path'], 'type': node['type']}
                self.path_to_item_id[node['path']] = item_id
                if node['type'] == 'dir':
                    _insert_nodes(item_id, node.get('children', []))
                    self.tree_handler.update_item_visuals(item_id)
                else:
                    self.tree_handler.update_item_visuals(item_id)
        _insert_nodes('', tree_data)

    def on_selection_list_changed(self):
        self.tree_handler.update_all_visuals()
        self.update_all_button_states()
        self.data_controller.run_token_recalculation()
        self.save_state()

    def on_file_toggled(self, path):
        self.selection_handler.toggle_file(path)
        self.tree_handler.update_item_visuals(self.path_to_item_id.get(path))
        self.update_all_button_states()
        self.sync_highlights()

    def handle_tree_select(self, event):
        if self.tree.selection(): self.merge_order_list.clear_selection()
        self.sync_highlights()
        self.update_all_button_states()

    def handle_merge_order_tree_select(self, event):
        if self.merge_order_list.curselection() and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.sync_highlights()
        self.update_all_button_states()

    def update_all_button_states(self):
        self.tree_handler.update_action_button_state()
        self.selection_handler.update_button_states()

    def sync_highlights(self):
        for item_id in self.tree.tag_has('subtle_highlight'):
            self.tree.item(item_id, tags=())
        self.merge_order_list.clear_highlights()
        selected_path, source = (None, None)
        if self.tree.selection():
            item_id = self.tree.selection()[0]
            if self.item_map.get(item_id, {}).get('type') == 'file':
                selected_path, source = (self.item_map[item_id]['path'], self.tree)
        elif self.merge_order_list.curselection():
            idx = self.merge_order_list.curselection()[0]
            selected_path, source = (self.merge_order_list.get_item_data(idx), self.merge_order_list)
        if not selected_path: return
        if source == self.tree:
            try:
                paths = [f['path'] for f in self.selection_handler.ordered_selection]
                self.merge_order_list.highlight_item(paths.index(selected_path))
            except ValueError: pass
        elif source == self.merge_order_list and selected_path in self.path_to_item_id:
            item_id = self.path_to_item_id[selected_path]
            self.tree.item(item_id, tags=('subtle_highlight',))
            self.tree.see(item_id)
        self.ui_controller.refresh_hover_icon()

    def handle_reset(self):
        """Resets the file selection for this step."""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset the base file selection?", parent=self):
            if self.selection_handler:
                self.selection_handler.remove_all_files()

    # Stub methods for compatibility with controllers
    def show_error_dialog(self, title, message):
        messagebox.showerror(title, message, parent=self)

    def _close_and_save_geometry(self):
        pass # Not applicable for starter view

    def _update_sash_cover_position(self, event=None):
        try:
            x = self.paned_window.sashpos(0)
            self.sash_cover.place(x=x, y=0, anchor="nw", relheight=1.0)
        except Exception: pass

    def _on_manual_sash_move(self, event=None):
        self.sash_pos_normal = self.paned_window.sashpos(0)
        self._update_sash_cover_position()
```

--- End of file ---

--- File: `src/ui/project_starter/step_concept.py` ---

```python
import tkinter as tk
import os
import json
import pyperclip
from tkinter import messagebox
from ... import constants as c
from ...core.paths import REFERENCE_DIR
from ...core.utils import strip_markdown_wrapper
from ...core.prompts import STARTER_CONCEPT_DEFAULT_GOAL
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from .segment_manager import SegmentManager
from .widgets.segmented_reviewer import SegmentedReviewer
from .widgets.rewrite_dialog import RewriteUnsignedDialog
from .widgets.full_text_reviewer import FullTextReviewer
from ..tooltip import ToolTip
from . import starter_prompts

class ConceptView(tk.Frame):
    def __init__(self, parent, starter_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.starter_controller = starter_controller
        self.project_data = project_data

        self.questions_map = self._load_questions()
        self.has_segments = bool(self.project_data.get("concept_segments"))

        self.editor_is_active = False
        self.generation_mode_active = False

        if self.has_segments:
            self.show_editor_view()
        elif self.project_data.get("concept_md"):
            self.show_merged_view(self.project_data.get("concept_md"))
        elif self.project_data.get("concept_llm_response"):
            self.show_generation_view(starter_prompts.get_concept_prompt(self.project_data, self.questions_map))
        else:
            self.show_initial_view()

    def register_info(self, info_mgr):
        if not info_mgr: return
        if hasattr(self, 'goal_text') and self.goal_text.winfo_exists():
            info_mgr.register(self.goal_text, "starter_concept_goal")
            info_mgr.register(self.generate_btn, "starter_concept_gen")
        elif hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            info_mgr.register(self.copy_btn, "starter_concept_gen")
            info_mgr.register(self.llm_response_text, "starter_gen_response")
            info_mgr.register(self.btn_process, "starter_gen_process")
        elif hasattr(self, 'reviewer') and self.reviewer.winfo_exists():
            if isinstance(self.reviewer, FullTextReviewer):
                self.reviewer.register_info(info_mgr, "starter_concept_review")
            else:
                self.reviewer.register_info(info_mgr)

    def refresh_fonts(self):
        size = self.starter_controller.font_size
        for attr in['goal_text', 'llm_response_text', 'reviewer']:
            if hasattr(self, attr):
                widget = getattr(self, attr)
                if widget.winfo_exists():
                    if hasattr(widget, 'refresh_fonts'): widget.refresh_fonts(size)
                    else: widget.set_font_size(size)

    def _load_questions(self):
        questions_path = os.path.join(REFERENCE_DIR, "concept_questions.json")
        try:
            with open(questions_path, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def show_initial_view(self):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = False

        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        self.generate_btn = RoundedButton(btn_container, text="Generate Concept Prompt", command=self.handle_prompt_generation, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.generate_btn.pack(side='right')

        tk.Label(self, text="Describe Your Goal", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 5))
        tk.Label(self, text="Briefly describe what you want to build.", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").pack(side='top', anchor="w", pady=(0, 10))

        self.goal_text = ScrollableText(self, height=5, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size), on_zoom=self.starter_controller.adjust_font_size)
        self.goal_text.pack(side='top', fill="both", expand=True, pady=5)
        self.goal_text.insert("1.0", self.project_data.get("goal", "") or STARTER_CONCEPT_DEFAULT_GOAL)
        self.goal_text.text_widget.bind("<KeyRelease>", self._update_goal_state)
        self._update_button_state()
        self.register_info(self.starter_controller.info_mgr)

    def _update_goal_state(self, event=None):
        self.project_data["goal"] = self.goal_text.get("1.0", "end-1c").strip()
        self._update_button_state()

    def _update_button_state(self):
        content = self.project_data.get("goal", "").strip()
        self.generate_btn.set_state('normal' if content and content != STARTER_CONCEPT_DEFAULT_GOAL else 'disabled')

    def handle_prompt_generation(self):
        prompt = starter_prompts.get_concept_prompt(self.project_data, self.questions_map)
        self.show_generation_view(prompt)

    def show_generation_view(self, prompt):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = True
        self.starter_controller._update_navigation_controls()

        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        self.btn_process = RoundedButton(btn_container, text="Process & Review", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.btn_process.pack(side='right')

        tk.Label(self, text="Generate Concept", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        instr_f = tk.Frame(self, bg=c.DARK_BG)
        instr_f.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(instr_f, text="1. Copy prompt", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        self.copy_btn = RoundedButton(instr_f, text="Copy Prompt", command=lambda: self._copy_prompt(prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, radius=6, cursor="hand2")
        self.copy_btn.pack(side='left', padx=15)

        tk.Label(self, text="2. Paste LLM Response (with tags)", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 0))
        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size), on_zoom=self.starter_controller.adjust_font_size)
        self.llm_response_text.pack(side='top', fill="both", expand=True, pady=5)
        self.llm_response_text.insert("1.0", self.project_data.get("concept_llm_response", ""))
        self.llm_response_text.text_widget.bind("<KeyRelease>", self._on_response_change)

        self._update_process_btn()
        self.register_info(self.starter_controller.info_mgr)

    def _on_response_change(self, event=None):
        self.project_data["concept_llm_response"] = self.llm_response_text.get("1.0", "end-1c").strip()
        self._update_process_btn()

    def _update_process_btn(self):
        content = self.project_data.get("concept_llm_response", "").strip()
        st = 'normal' if content else 'disabled'
        self.btn_process.set_state(st)
        self.btn_process.config(bg=c.BTN_BLUE if st=='normal' else c.BTN_GRAY_BG, fg=c.BTN_BLUE_TEXT if st=='normal' else c.BTN_GRAY_TEXT)

    def _copy_prompt(self, text):
        pyperclip.copy(text)
        self.copy_btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: self.copy_btn.config(text="Copy Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if self.copy_btn.winfo_exists() else None)

    def handle_llm_response(self):
        raw = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw: return
        content = strip_markdown_wrapper(raw)
        parsed = SegmentManager.parse_segments(content)
        if not parsed:
            self.project_data["concept_md"] = content
            self.show_merged_view(content)
            return

        friendly = {k: v["label"] for k, v in self.questions_map.items()}
        mapped = SegmentManager.map_parsed_segments_to_keys(parsed, friendly)
        self.project_data["concept_segments"].clear()
        self.project_data["concept_segments"].update(mapped)
        self.project_data["concept_signoffs"].clear()
        for k in mapped: self.project_data["concept_signoffs"][k] = False
        self.project_data["concept_md"] = ""
        self.project_data["concept_llm_response"] = ""
        self.show_editor_view()

    def show_editor_view(self):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        header = tk.Frame(self, bg=c.DARK_BG)
        header.pack(side='top', fill="x", pady=(0, 5))
        tk.Label(header, text="Review Concept Segments", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        friendly = {k: v["label"] for k, v in self.questions_map.items()}
        self.reviewer = SegmentedReviewer(self, list(self.project_data["concept_segments"].keys()), friendly, self.project_data["concept_segments"], self.project_data["concept_signoffs"], self.questions_map, self.starter_controller.update_nav_state, self.handle_merge)
        self.reviewer.pack(fill="both", expand=True, pady=5)
        self.starter_controller._update_navigation_controls()
        self.register_info(self.starter_controller.info_mgr)

    def handle_merge(self, full_text):
        self.project_data["concept_segments"].clear()
        self.project_data["concept_signoffs"].clear()
        self.project_data["concept_md"] = full_text
        self.starter_controller.starter_state.update_from_view(self)
        self.starter_controller.starter_state.save()
        self.show_merged_view(full_text)

    def show_merged_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        qs =["Is this concept clearly explained?", "Did we miss anything?"]
        self.reviewer = FullTextReviewer(self, "Review Full Concept", content, qs, self._on_merged_change, self._open_rewrite, self._get_prompt_context, self.starter_controller)
        self.reviewer.pack(fill="both", expand=True)

        self.starter_controller._update_navigation_controls()
        self.register_info(self.starter_controller.info_mgr)

    def _get_prompt_context(self):
        """Provides the specific background and focus context for the LLM prompt."""
        full_text = self.project_data.get("concept_md", "")
        return (
            "Full Concept",
            "```markdown\n" + full_text + "\n```",
            "Concept",
            "(Overview above)"
        )

    def _on_merged_change(self, text):
        self.project_data["concept_md"] = text

    def _open_rewrite(self):
        ctx = {'keys': ['full_content'], 'names': {'full_content': 'Full Concept'}, 'data': {'full_content': self.project_data["concept_md"]}}
        RewriteUnsignedDialog(self, self.starter_controller.app.app_state, ctx, self._apply_rewrite, is_merged_mode=True)

    def _apply_rewrite(self, text):
        clean = strip_markdown_wrapper(text)
        self.project_data["concept_md"] = clean
        self.reviewer.set_content(clean)
        self.starter_controller.update_nav_state()

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over?", parent=self):
            self.project_data["concept_segments"].clear()
            self.project_data["concept_signoffs"].clear()
            self.project_data["concept_md"] = ""
            self.project_data["concept_llm_response"] = ""
            self.editor_is_active = False
            self.generation_mode_active = False
            self.show_initial_view()
            self.starter_controller._update_navigation_controls()

    def get_goal_content(self):
        return self.goal_text.get("1.0", "end-1c").strip() if hasattr(self, 'goal_text') and self.goal_text.winfo_exists() else self.project_data.get("goal", "")

    def get_llm_response_content(self):
        return {"concept_llm_response": self.llm_response_text.get("1.0", "end-1c").strip()} if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists() else {}

    def get_assembled_content(self):
        if not self.project_data.get("concept_segments"): return self.project_data.get("concept_md", ""), {}, {}
        friendly = {k: v["label"] for k, v in self.questions_map.items()}
        txt = SegmentManager.assemble_document(self.project_data["concept_segments"], list(self.project_data["concept_segments"].keys()), friendly)
        return txt, self.project_data["concept_segments"], self.project_data["concept_signoffs"]

    def is_editor_visible(self): return self.editor_is_active
    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active
    def _clear_frame(self):
        for w in self.winfo_children(): w.destroy()
```

--- End of file ---

--- File: `src/ui/project_starter/step_stack.py` ---

```python
import tkinter as tk
import json
import pyperclip
from tkinter import messagebox
from ... import constants as c
from ...core.utils import save_config, load_config
from ...core.prompts import STARTER_STACK_PROMPT_INTRO, STARTER_STACK_PROMPT_INSTR
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from ..tooltip import ToolTip

class StackView(tk.Frame):
    def __init__(self, parent, starter_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.starter_controller = starter_controller
        self.project_data = project_data
        self.app_config = load_config()

        # Load from state if it exists, otherwise fall back to global default
        state_exp = self.project_data.get("stack_experience", "").strip()
        self.saved_experience = state_exp if state_exp else self.app_config.get('user_experience', '')

        self.stack_content = self.project_data["stack"].get()

        self.editor_is_active = False
        self.generation_mode_active = False

        if self.stack_content:
            display_content = "\n".join([s.strip() for s in self.stack_content.split(',') if s.strip()])
            self.show_editor_view(display_content)
        elif self.project_data.get("stack_llm_response"):
            # Restore state where response was pasted but not yet processed
            self.show_generation_view(self._get_prompt())
        else:
            self.show_initial_view()

    def register_info(self, info_mgr):
        """Registers widgets for Info Mode."""
        if not info_mgr: return
        if hasattr(self, 'experience_text') and self.experience_text.winfo_exists():
            info_mgr.register(self.experience_text, "starter_stack_exp")
        if hasattr(self, 'btn_gen') and self.btn_gen.winfo_exists():
            info_mgr.register(self.btn_gen, "starter_stack_gen")
        if hasattr(self, 'stack_editor') and self.stack_editor.winfo_exists():
            info_mgr.register(self.stack_editor, "starter_stack_edit")
        if hasattr(self, 'copy_btn') and self.copy_btn.winfo_exists():
             info_mgr.register(self.copy_btn, "starter_stack_gen")
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
             info_mgr.register(self.llm_response_text, "starter_gen_response")

    def refresh_fonts(self):
        if hasattr(self, 'experience_text') and self.experience_text.winfo_exists():
            self.experience_text.set_font_size(self.starter_controller.font_size)
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            self.llm_response_text.set_font_size(self.starter_controller.font_size)
        if hasattr(self, 'stack_editor') and self.stack_editor.winfo_exists():
            self.stack_editor.set_font_size(self.starter_controller.font_size)

    def show_initial_view(self):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = False

        # ACTION BUTTON AT BOTTOM
        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill="x", pady=15)

        self.save_exp_btn = RoundedButton(btn_container, text="Save as Default", command=self._save_experience, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=30, cursor="hand2")
        ToolTip(self.save_exp_btn, "Save this text as your application-wide default for future projects", delay=500)

        self.load_exp_btn = RoundedButton(btn_container, text="Load Default", command=self._load_default_experience, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=30, cursor="hand2")
        ToolTip(self.load_exp_btn, "Replace the text below with your saved default experience", delay=500)

        self.btn_gen = RoundedButton(btn_container, text="Generate Stack Recommendation", command=self.handle_prompt_generation, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.btn_gen.pack(side='right')
        ToolTip(self.btn_gen, "Ask the LLM to recommend a technology stack based on your concept and experience", delay=500)

        # TOP CONTENT
        global_default = self.app_config.get('user_experience', '').strip()
        header_text = "Edit your known languages, frameworks, and environment details." if global_default else "List your known languages, frameworks, and environment details."
        tk.Label(self, text="Your Experience & Environment", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 5))
        tk.Label(self, text=header_text, wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, justify="left").pack(side='top', anchor="w", pady=(0, 10))

        self.experience_text = ScrollableText(
            self, height=6, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size),
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.experience_text.pack(side='top', fill="both", expand=True, pady=5)
        self.experience_text.insert("1.0", self.saved_experience)
        self.experience_text.text_widget.bind('<KeyRelease>', self._on_exp_change)
        self._on_exp_change()
        self.register_info(self.starter_controller.info_mgr)

    def _on_exp_change(self, event=None):
        current_val = self.experience_text.get("1.0", "end-1c").strip()
        global_default = self.app_config.get('user_experience', '').strip()

        # Update state variable so navigating away preserves the draft
        self.project_data["stack_experience"] = current_val

        # Toggle Save Button: Only if current text is different from global default
        if current_val != global_default:
            if not self.save_exp_btn.winfo_ismapped():
                self.save_exp_btn.pack(side='left')
        else:
            self.save_exp_btn.pack_forget()

        # Toggle Load Button: Only if there is a default AND it's different from current
        if global_default and current_val != global_default:
            if not self.load_exp_btn.winfo_ismapped():
                self.load_exp_btn.pack(side='left', padx=(10, 0))
        else:
            self.load_exp_btn.pack_forget()

    def _save_experience(self):
        """Saves current text to global config and synchronizes main app state."""
        new_exp = self.experience_text.get("1.0", "end-1c").strip()
        self.app_config['user_experience'] = new_exp
        save_config(self.app_config)

        try:
            self.starter_controller.app.app_state.reload()
        except Exception:
            pass

        self.save_exp_btn.pack_forget()
        self.load_exp_btn.pack_forget()

    def _load_default_experience(self):
        global_default = self.app_config.get('user_experience', '').strip()
        current_val = self.experience_text.get("1.0", "end-1c").strip()

        if not global_default:
            return

        if current_val:
            warning = "This will overwrite the information you have typed in.\n\nAre you sure you want to load your default stack experience?"
            if not messagebox.askyesno("Overwrite Warning", warning, parent=self):
                return

        self.experience_text.delete("1.0", "end")
        self.experience_text.insert("1.0", global_default)
        self._on_exp_change()

    def _get_prompt(self):
        concept = self.project_data.get("concept_md", "")
        experience = self.project_data.get("stack_experience", "")
        parts = [
            STARTER_STACK_PROMPT_INTRO,
            "\n### Developer Experience\n```\n" + (experience if experience.strip() else "No specific experience listed. Recommend standard industry defaults.") + "\n```",
            "\n### Project Concept\n```markdown\n" + concept + "\n```",
            STARTER_STACK_PROMPT_INSTR
        ]
        return "\n".join(parts)

    def handle_prompt_generation(self):
        prompt = self._get_prompt()
        self.show_generation_view(prompt)

    def show_generation_view(self, prompt):
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = True
        self.starter_controller._update_navigation_controls()

        # ACTION BUTTON AT BOTTOM
        btn_container = tk.Frame(self, bg=c.DARK_BG)
        btn_container.pack(side='bottom', fill='x', pady=10)
        btn_proc = RoundedButton(btn_container, text="Process Response", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        btn_proc.pack(side='right')
        ToolTip(btn_proc, "Parse the LLM's recommended stack list", delay=500)

        # TOP CONTENT
        tk.Label(self, text="Generate Stack", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 10))

        instr_frame = tk.Frame(self, bg=c.DARK_BG);
        instr_frame.pack(side='top', fill="x", pady=(0, 10))
        tk.Label(instr_frame, text="1. Copy prompt and paste it into your LLM.", bg=c.DARK_BG, fg=c.TEXT_COLOR, font=c.FONT_BOLD).pack(side='left')
        self.copy_btn = RoundedButton(instr_frame, text="Copy Prompt", command=lambda: self._copy_to_clipboard(self.copy_btn, prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, radius=6, cursor="hand2")
        self.copy_btn.pack(side='left', padx=15)
        ToolTip(self.copy_btn, "Copy the prompt to your clipboard", delay=500)

        tk.Label(self, text="2. Paste Stack Recommendation below", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(10, 5))
        self.llm_response_text = ScrollableText(
            self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size),
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.llm_response_text.pack(side='top', fill="both", expand=True, pady=5)
        self.llm_response_text.insert("1.0", self.project_data.get("stack_llm_response", ""))

        # Sync input area to state to prevent data loss on navigation
        self.llm_response_text.text_widget.bind("<KeyRelease>", lambda e: self.project_data.__setitem__("stack_llm_response", self.llm_response_text.get("1.0", "end-1c").strip()))
        self.register_info(self.starter_controller.info_mgr)

    def _copy_to_clipboard(self, button, text):
        pyperclip.copy(text)
        button.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: button.config(text="Copy Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if button.winfo_exists() else None)

    def handle_llm_response(self):
        raw_content = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw_content: return
        try:
            start_idx, end_idx = raw_content.find('['), raw_content.rfind(']')
            if start_idx == -1 or end_idx == -1: raise ValueError("No JSON list")
            json_str = raw_content[start_idx:end_idx+1].replace("'", '"')
            stack_list = json.loads(json_str)
            self.project_data["stack"].set(", ".join(stack_list))
            self.project_data["stack_llm_response"] = "" # Clear buffer on success
            self.show_editor_view("\n".join(stack_list))
        except Exception:
            tk.messagebox.showerror("Error", "Could not parse JSON list.", parent=self)

    def show_editor_view(self, content):
        self._clear_frame()
        self.editor_is_active = True
        self.generation_mode_active = False

        # HEADER & FOOTER AT EDGES
        tk.Label(self, text="Selected Code Stack", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='top', anchor="w", pady=(0, 5))
        tk.Label(self, text="Do you agree with using this stack for your project? (one subject per line)", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR, font=c.FONT_NORMAL).pack(side='bottom', anchor="w", pady=(5, 0))

        # CENTER CONTENT
        self.stack_editor = ScrollableText(
            self, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size),
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.stack_editor.pack(side='top', fill="both", expand=True, pady=5)
        self.stack_editor.insert("1.0", content)
        self.stack_editor.text_widget.bind('<KeyRelease>', self._sync_editor_to_state)

        # Trigger Starter UI Update
        self.starter_controller._update_navigation_controls()
        self.starter_controller.update_nav_state()
        self.register_info(self.starter_controller.info_mgr)

    def _sync_editor_to_state(self, event=None):
        if hasattr(self, 'stack_editor') and self.stack_editor.winfo_exists():
            raw_text = self.stack_editor.get("1.0", "end-1c")
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            self.project_data["stack"].set(", ".join(lines))
        self.starter_controller.update_nav_state()

    def handle_reset(self):
        if tk.messagebox.askyesno("Confirm", "Reset stack selection?", parent=self):
            self.project_data["stack"].set("")
            self.project_data["stack_experience"] = ""
            self.project_data["stack_llm_response"] = ""
            self.show_initial_view()
            self.starter_controller._update_navigation_controls()

    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active

    def get_stack_content(self):
        if hasattr(self, 'stack_editor') and self.stack_editor.winfo_exists():
            raw_text = self.stack_editor.get("1.0", "end-1c")
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            return ", ".join(lines)
        return self.project_data["stack"].get()

    def get_experience_content(self):
        return self.project_data.get("stack_experience", "")

    def get_llm_response_content(self):
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            return {"stack_llm_response": self.llm_response_text.get("1.0", "end-1c").strip()}
        return {}

    def _clear_frame(self):
        for widget in self.winfo_children(): widget.destroy()
```

--- End of file ---

--- File: `src/ui/project_starter/step_todo.py` ---

```python
import os
import json
import pyperclip
import tkinter as tk
from tkinter import messagebox
from ... import constants as c
from ...core.paths import REFERENCE_DIR
from ...core.utils import strip_markdown_wrapper
from ..widgets.rounded_button import RoundedButton
from ..widgets.scrollable_text import ScrollableText
from .segment_manager import SegmentManager
from .widgets.segmented_reviewer import SegmentedReviewer
from .widgets.rewrite_dialog import RewriteUnsignedDialog
from .widgets.full_text_reviewer import FullTextReviewer
from ..tooltip import ToolTip
from . import starter_prompts

class TodoView(tk.Frame):
    def __init__(self, parent, starter_controller, project_data):
        super().__init__(parent, bg=c.DARK_BG)
        self.starter_controller = starter_controller
        self.project_data = project_data

        self.questions_map = {}
        self.manual_questions = self._load_questions()

        self.editor_is_active = False
        self.generation_mode_active = False
        self.has_segments = bool(self.project_data.get("todo_segments"))

        if self.has_segments:
            self.show_editor_view()
        elif self.project_data.get("todo_md"):
            self.show_merged_view(self.project_data.get("todo_md"))
        elif self.project_data.get("todo_llm_response"):
            self.show_generation_view(starter_prompts.get_todo_prompt(self.project_data, self.questions_map))
        else:
            self.show_generation_view()

    def register_info(self, info_mgr):
        if not info_mgr: return
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            info_mgr.register(self.copy_btn, "starter_todo_gen")
            info_mgr.register(self.llm_response_text, "starter_gen_response")
            info_mgr.register(self.btn_process, "starter_gen_process")
        elif hasattr(self, 'reviewer') and self.reviewer.winfo_exists():
            if isinstance(self.reviewer, FullTextReviewer):
                self.reviewer.register_info(info_mgr, "starter_todo_review")
            else:
                self.reviewer.register_info(info_mgr)

    def refresh_fonts(self):
        size = self.starter_controller.font_size
        if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists():
            self.llm_response_text.set_font_size(size)
        if hasattr(self, 'reviewer') and self.reviewer.winfo_exists():
            self.reviewer.refresh_fonts(size)

    def _load_questions(self):
        path = os.path.join(REFERENCE_DIR, "todo_questions.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
                if isinstance(data, dict):
                    self.questions_map = data
                    return []
                return data if isinstance(data, list) else[]
        except (FileNotFoundError, json.JSONDecodeError): return[]

    def show_generation_view(self, prompt=None):
        if prompt is None: prompt = starter_prompts.get_todo_prompt(self.project_data, self.questions_map)
        self._clear_frame()
        self.editor_is_active = False
        self.generation_mode_active = True
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hdr = tk.Frame(self, bg=c.DARK_BG)
        hdr.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        tk.Label(hdr, text="1. Copy Prompt for LLM", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')
        self.copy_btn = RoundedButton(hdr, text="Copy Prompt", command=lambda: self._copy_prompt(prompt), bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
        self.copy_btn.pack(side='left', padx=15)

        tk.Label(self, text="2. Paste LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=1, column=0, pady=(10, 5), sticky="w")
        self.llm_response_text = ScrollableText(self, wrap=tk.WORD, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size), on_zoom=self.starter_controller.adjust_font_size)
        self.llm_response_text.grid(row=2, column=0, sticky='nsew')
        self.llm_response_text.insert("1.0", self.project_data.get("todo_llm_response", ""))
        self.llm_response_text.text_widget.bind("<KeyRelease>", self._on_response_change)

        self.btn_process = RoundedButton(self, text="Process & Review", command=self.handle_llm_response, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, height=30, cursor="hand2")
        self.btn_process.grid(row=3, column=0, pady=(10,0), sticky="e")
        self._update_process_btn()
        self.register_info(self.starter_controller.info_mgr)

    def _on_response_change(self, event=None):
        self.project_data["todo_llm_response"] = self.llm_response_text.get("1.0", "end-1c").strip()
        self._update_process_btn()

    def _update_process_btn(self):
        content = self.project_data.get("todo_llm_response", "").strip()
        st = 'normal' if content else 'disabled'
        self.btn_process.set_state(st)
        self.btn_process.config(bg=c.BTN_BLUE if st=='normal' else c.BTN_GRAY_BG, fg=c.BTN_BLUE_TEXT if st=='normal' else c.BTN_GRAY_TEXT)

    def _copy_prompt(self, text):
        pyperclip.copy(text)
        self.copy_btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
        self.after(2000, lambda: self.copy_btn.config(text="Copy Prompt", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT) if self.copy_btn.winfo_exists() else None)

    def handle_llm_response(self):
        raw = self.llm_response_text.get("1.0", "end-1c").strip()
        if not raw: return
        content = strip_markdown_wrapper(raw)
        parsed = SegmentManager.parse_segments(content)
        if not parsed:
            self.project_data["todo_md"] = content
            self.show_merged_view(content)
            return

        friendly = {k: v["label"] for k, v in self.questions_map.items()} if self.questions_map else c.TODO_PHASES
        mapped = SegmentManager.map_parsed_segments_to_keys(parsed, friendly)
        self.project_data["todo_segments"].clear()
        self.project_data["todo_segments"].update(mapped)
        self.project_data["todo_signoffs"].clear()
        for k in mapped: self.project_data["todo_signoffs"][k] = False
        self.project_data["todo_md"] = ""
        self.project_data["todo_llm_response"] = ""
        self.show_editor_view()

    def show_editor_view(self):
        self._clear_frame()
        self.editor_is_active, self.generation_mode_active = True, False
        header = tk.Frame(self, bg=c.DARK_BG)
        header.pack(side='top', fill="x", pady=(0, 5))
        tk.Label(header, text="Review TODO Plan", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side="left")

        friendly = {k: v["label"] for k, v in self.questions_map.items()} if self.questions_map else c.TODO_PHASES
        ordered_keys = list(self.project_data["todo_segments"].keys())
        if 'deployment' in ordered_keys:
            ordered_keys.remove('deployment'); ordered_keys.append('deployment')

        self.reviewer = SegmentedReviewer(self, ordered_keys, friendly, self.project_data["todo_segments"], self.project_data["todo_signoffs"], self.questions_map, self.starter_controller.update_nav_state, self.handle_merge)
        self.reviewer.pack(fill="both", expand=True, pady=5)
        self.starter_controller._update_navigation_controls()
        self.register_info(self.starter_controller.info_mgr)

    def handle_merge(self, full_text):
        self.project_data["todo_segments"].clear()
        self.project_data["todo_signoffs"].clear()
        self.project_data["todo_md"] = full_text
        self.starter_controller.starter_state.update_from_view(self)
        self.starter_controller.starter_state.save()
        self.show_merged_view(full_text)

    def show_merged_view(self, content):
        self._clear_frame()
        self.editor_is_active, self.generation_mode_active = True, False
        qs = self.manual_questions or["Do these TODO steps cover the concept?", "Did we miss anything?"]
        self.reviewer = FullTextReviewer(self, "Edit Your TODO Plan", content, qs, self._on_merged_change, self._open_rewrite, self._get_prompt_context, self.starter_controller)
        self.reviewer.pack(fill="both", expand=True)
        self.starter_controller._update_navigation_controls()
        self.register_info(self.starter_controller.info_mgr)

    def _get_prompt_context(self):
        """Provides the specific background and focus context for the LLM prompt."""
        concept_md = self.project_data.get("concept_md")
        if not concept_md and self.project_data.get("concept_segments"):
            concept_md = SegmentManager.assemble_document(self.project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS)
        todo_content = self.project_data.get("todo_md", "")

        return (
            "Project Concept",
            "```markdown\n" + (concept_md or "No concept provided") + "\n```",
            "Full TODO Plan",
            "```markdown\n" + todo_content + "\n```"
        )

    def _on_merged_change(self, text):
        self.project_data["todo_md"] = text

    def _open_rewrite(self):
        ctx = {'keys': ['full_content'], 'names': {'full_content': 'Full TODO Plan'}, 'data': {'full_content': self.project_data["todo_md"]}}
        RewriteUnsignedDialog(self, self.starter_controller.app.app_state, ctx, self._apply_rewrite, is_merged_mode=True)

    def _apply_rewrite(self, text):
        clean = strip_markdown_wrapper(text)
        self.project_data["todo_md"] = clean
        self.reviewer.set_content(clean)
        self.starter_controller.update_nav_state()

    def handle_reset(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to start over?", parent=self):
            self.project_data["todo_segments"].clear()
            self.project_data["todo_signoffs"].clear()
            self.project_data["todo_md"] = ""
            self.project_data["todo_llm_response"] = ""
            self.editor_is_active, self.generation_mode_active = False, False
            self.show_generation_view()
            self.starter_controller._update_navigation_controls()

    def get_llm_response_content(self):
        return {"todo_llm_response": self.llm_response_text.get("1.0", "end-1c").strip()} if hasattr(self, 'llm_response_text') and self.llm_response_text.winfo_exists() else {}

    def get_assembled_content(self):
        if not self.project_data.get("todo_segments"): return self.project_data.get("todo_md", ""), {}, {}
        keys = list(self.project_data["todo_segments"].keys())
        if 'deployment' in keys: keys.remove('deployment'); keys.append('deployment')
        friendly = {k: v["label"] for k, v in self.questions_map.items()} if self.questions_map else c.TODO_PHASES
        txt = SegmentManager.assemble_document(self.project_data["todo_segments"], keys, friendly)
        return txt, self.project_data["todo_segments"], self.project_data["todo_signoffs"]

    def is_editor_visible(self): return self.editor_is_active
    def is_step_in_progress(self): return self.editor_is_active or self.generation_mode_active
    def _clear_frame(self):
        for w in self.winfo_children(): w.destroy()
```

--- End of file ---

--- File: `src/ui/project_starter/step_generate.py` ---

```python
import os
import re
import tkinter as tk
import pyperclip
from tkinter import messagebox, ttk, filedialog
from ... import constants as c
from ...core.paths import BOILERPLATE_DIR
from ...core.utils import strip_markdown_wrapper
from ...core.prompts import STARTER_GENERATE_MASTER_INTRO, STARTER_GENERATE_MASTER_INSTR
from ..widgets.rounded_button import RoundedButton
from .segment_manager import SegmentManager
from ..tooltip import ToolTip
# // DO NOT REMOVE [index] (pattern correction)
from ..widgets.scrollable_text import ScrollableText

class GenerateView(tk.Frame):
    def __init__(self, parent, project_data, create_project_callback, starter_controller):
        super().__init__(parent, bg=c.DARK_BG)
        self.create_project_callback = create_project_callback
        self.project_data = project_data
        self.starter_controller = starter_controller
        self._trace_ids = [] # Track traces for cleanup
        self.step3_interacted = False

        self.master_prompt_content = self._generate_master_prompt(project_data)

        self.grid_columnconfigure(0, weight=1)

        # Response area is the primary expanding element
        self.grid_rowconfigure(2, weight=1)

        # Header
        tk.Label(self, text="Finalize and Generate", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, pady=(0, 10), sticky="w")

        # PROMPT COPY SECTION
        self.step1_frame = tk.Frame(self, bg=c.DARK_BG)
        self.step1_frame.grid(row=1, column=0, pady=(10, 0), sticky="ew")

        self.step1_title = tk.Label(self.step1_frame, text="1. Copy Creation Prompt", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.BTN_GREEN)
        self.step1_title.pack(side="top", anchor="w")

        self.copy_btn = RoundedButton(
            self.step1_frame, text="Copy Creation Prompt",
            command=lambda: self._copy_prompt_to_clipboard(self.copy_btn, self.master_prompt_content),
            bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON,
            height=40, width=250, radius=6, cursor="hand2",
            hover_bg=c.BTN_GREEN, # Maintain green on hover even if idle turns grey
            hover_fg="#FFFFFF"    # Maintain white text on hover
        )
        self.copy_btn.pack(side="top", anchor="w", pady=(10, 5))
        ToolTip(self.copy_btn, "Copy the final boilerplate and instructions for your AI", delay=500)

        self.hint_label = tk.Label(self.step1_frame, text="Note: it is recommended to use a smart thinking model for this step", font=(c.FONT_FAMILY_PRIMARY, 9, 'italic'), bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR)
        self.hint_label.pack(side="top", anchor="w")

        # RESPONSE SECTION (Initially Hidden)
        self.step2_frame = tk.Frame(self, bg=c.DARK_BG)

        self.step2_title = tk.Label(self.step2_frame, text="2. Paste the LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR)
        self.step2_title.pack(side="top", anchor="w", pady=(20, 5))

        self.llm_result_text = ScrollableText(
            self.step2_frame, wrap=tk.WORD, height=2, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR,
            font=(c.FONT_FAMILY_PRIMARY, self.starter_controller.font_size),
            on_zoom=self.starter_controller.adjust_font_size
        )
        self.llm_result_text.pack(side="top", fill="both", expand=True, pady=(0, 10))

        # Restore buffer if present
        saved_response = self.project_data.get("generate_llm_response", "")
        if saved_response:
            self.llm_result_text.insert("1.0", saved_response)

        self.llm_result_text.text_widget.bind('<KeyRelease>', self._validate_and_sync)
        self.llm_result_text.text_widget.bind('<<Paste>>', self._validate_and_sync)

        # DESTINATION FOLDER SECTION (Initially Hidden)
        self.step3_frame = tk.Frame(self, bg=c.DARK_BG)

        dest_label_frame = tk.Frame(self.step3_frame, bg=c.DARK_BG)
        dest_label_frame.pack(side="top", fill="x", pady=(10, 5))
        self.step3_title = tk.Label(dest_label_frame, text="3. Select Parent Folder for the project", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR)
        self.step3_title.pack(side="left")

        folder_select_frame = tk.Frame(self.step3_frame, bg=c.DARK_BG)
        folder_select_frame.pack(side="top", fill="x", pady=(0, 5))

        self.folder_entry = tk.Entry(folder_select_frame, textvariable=self.project_data["parent_folder"], bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, relief='flat', font=c.FONT_NORMAL)
        self.folder_entry.pack(side='left', fill='x', expand=True, ipady=4)

        self.browse_btn = RoundedButton(folder_select_frame, text="Browse", command=self._browse_folder, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=28, cursor='hand2')
        self.browse_btn.pack(side='left', padx=(5, 0))

        # Path Preview (Compact Single Line)
        self.preview_container = tk.Frame(self.step3_frame, bg=c.STATUS_BG, padx=10, pady=4)
        self.preview_container.pack(side="top", fill="x", pady=(5, 10))

        tk.Label(self.preview_container, text="A new folder will be created:", font=(c.FONT_FAMILY_PRIMARY, 9, 'bold'), bg=c.STATUS_BG, fg=c.TEXT_COLOR).pack(side='left')
        self.preview_path_label = tk.Label(self.preview_container, text="", font=(c.FONT_FAMILY_PRIMARY, 9), bg=c.STATUS_BG, fg=c.BTN_BLUE, justify='left')
        self.preview_path_label.pack(side='left', padx=(5, 0))

        # Interaction listeners for Step 3
        self.step3_frame.bind("<Button-1>", self._on_step3_click)
        self.folder_entry.bind("<Button-1>", self._on_step3_click)
        self.browse_btn.bind("<Button-1>", self._on_step3_click, add="+")
        self.preview_container.bind("<Button-1>", self._on_step3_click)

        # Footer
        footer_frame = tk.Frame(self, bg=c.DARK_BG)
        footer_frame.grid(row=4, column=0, sticky="ew", pady=(5, 15))

        if self.project_data["base_project_path"].get():
            ttk.Checkbutton(footer_frame, text="Include base project reference", variable=self.project_data["include_base_reference"], style='Dark.TCheckbutton').pack(side="left")

        self.create_button = RoundedButton(footer_frame, text="Create Project Files", command=self.on_create_project, bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT, font=c.FONT_BUTTON, height=40, width=250, cursor="hand2")
        self.create_button.pack(side="right")
        self.create_button.set_state('disabled')

        # Status hint label to explain why the button is disabled
        self.status_hint_label = tk.Label(footer_frame, text="", font=(c.FONT_FAMILY_PRIMARY, 9, 'italic'), bg=c.DARK_BG, fg=c.NOTE, justify='right')
        self.status_hint_label.pack(side="right", padx=15)

        # Setup preview path tracking and validation syncing
        t1 = self.project_data["parent_folder"].trace_add("write", self._update_preview_path)
        t2 = self.project_data["name"].trace_add("write", self._update_preview_path)
        t3 = self.project_data["parent_folder"].trace_add("write", self._validate_and_sync)
        t4 = self.project_data["name"].trace_add("write", self._validate_and_sync)
        t5 = self.project_data["parent_folder"].trace_add("write", self._force_backward_slashes)

        self._trace_ids = [
            ("parent_folder", t1), ("name", t2),
            ("parent_folder", t3), ("name", t4),
            ("parent_folder", t5)
        ]

        # Initial visibility check (handle session restore)
        if saved_response:
            self.step2_frame.grid(row=2, column=0, sticky="nsew")
            self._validate_and_sync()

        self._update_preview_path()
        self._validate_and_sync() # Initial state check
        self.register_info(self.starter_controller.info_mgr)

    def register_info(self, info_mgr):
        """Registers step-specific widgets for Info Mode."""
        if not info_mgr: return
        info_mgr.register(self.step1_title, "starter_gen_prompt")
        info_mgr.register(self.copy_btn, "starter_gen_prompt")
        info_mgr.register(self.step2_title, "starter_gen_response")
        info_mgr.register(self.llm_result_text, "starter_gen_response")
        info_mgr.register(self.step3_title, "starter_gen_parent")
        info_mgr.register(self.folder_entry, "starter_gen_parent")
        info_mgr.register(self.browse_btn, "starter_gen_parent")
        info_mgr.register(self.create_button, "starter_gen_create")

    def refresh_fonts(self):
        if hasattr(self, 'llm_result_text') and self.llm_result_text.winfo_exists():
            self.llm_result_text.set_font_size(self.starter_controller.font_size)

    def destroy(self):
        """Cleanup traces when the view is destroyed to prevent TclErrors."""
        for var_name, trace_id in self._trace_ids:
            try:
                self.project_data[var_name].trace_remove("write", trace_id)
            except Exception:
                pass
        super().destroy()

    def _force_backward_slashes(self, *args):
        """Ensures the parent folder path always uses backslashes."""
        val = self.project_data["parent_folder"].get()
        if '/' in val:
            self.project_data["parent_folder"].set(val.replace('/', '\\'))

    def _update_preview_path(self, *args):
        """Safely updates the preview path label if the widget still exists."""
        if not self.winfo_exists():
            return

        parent = self.project_data["parent_folder"].get().strip()
        name = self.project_data["name"].get().strip()

        if not hasattr(self, 'preview_path_label') or not self.preview_path_label.winfo_exists():
            return

        if not parent or not name:
            self.preview_path_label.config(text="[Incomplete details - please set Name and Parent Folder]", fg=c.TEXT_SUBTLE_COLOR)
            return

        from .generator import sanitize_project_name
        sanitized_name = sanitize_project_name(name)

        # Join components and normalize to backslashes for user preference
        full_path = os.path.join(parent, sanitized_name).replace('/', '\\')
        self.preview_path_label.config(text=full_path, fg=c.BTN_BLUE)

    def _browse_folder(self):
        self._on_step3_click()
        folder = filedialog.askdirectory(parent=self)
        if folder:
            # Normalize to backward slashes immediately after browsing
            normalized = folder.replace('/', '\\')
            self.project_data["parent_folder"].set(normalized)

    def _on_step3_click(self, event=None):
        """Called when user interacts with Step 3."""
        if not self.step3_interacted:
            self.step3_interacted = True
            self.step3_title.config(fg=c.TEXT_COLOR)
            self._validate_and_sync()

    def _validate_and_sync(self, *args):
        """
        Validates all inputs for the generation step and toggles button state.
        Triggered by key release in text area or changes to folder/name variables.
        Updates the status_hint_label with explanations if requirements aren't met.
        """
        if not self.winfo_exists():
            return

        content = self.llm_result_text.get("1.0", "end-1c").strip()

        # Save to buffer for persistence
        self.project_data["generate_llm_response"] = content

        # Handle title highlighting
        if content:
            self.step1_title.config(fg=c.TEXT_COLOR) # Mark Step 1 done
            self.step2_title.config(fg=c.TEXT_COLOR)
            # Reveal Step 3
            if not self.step3_frame.winfo_ismapped():
                self.step3_frame.grid(row=3, column=0, sticky="ew")
                if not self.step3_interacted:
                    self.step3_title.config(fg=c.BTN_GREEN)
        else:
            self.step3_frame.grid_forget()
            # If text is manually cleared or we are in reset, restore Step 1 focus
            self.step1_title.config(fg=c.BTN_GREEN)
            self.step2_title.config(fg=c.TEXT_COLOR)

        # Check Project Details
        project_name = self.project_data["name"].get().strip()
        if not project_name:
            self._set_ui_state("disabled", "Missing project name (Step 1)")
            return

        parent_folder = self.project_data["parent_folder"].get().strip()
        if not parent_folder:
            self._set_ui_state("disabled", "Select a destination folder")
            return

        if not os.path.isdir(parent_folder):
            self._set_ui_state("disabled", "Parent folder path is invalid")
            return

        # Check LLM Content (Files and Pitch tag)
        if not content:
             self._set_ui_state("disabled", "Paste the LLM response first")
             return

        has_files = re.search(r"--- File: `.+?` ---", content) and "--- End of file ---" in content
        if not has_files:
            self._set_ui_state("disabled", "No valid file blocks found in response")
            return

        # STRICT Check: Must find opening and closing tag
        has_pitch = re.search(r"<PITCH>.*?</PITCH>", content, re.DOTALL | re.IGNORECASE)
        if not has_pitch:
            self._set_ui_state("disabled", "Response missing <PITCH> tags")
            return

        # Check Interaction state
        if not self.step3_interacted:
            self._set_ui_state("disabled", "Verify parent folder to continue", use_gray_btn=True)
            return

        # All conditions met
        self._set_ui_state("normal", "")

    def _set_ui_state(self, state, hint_text, use_gray_btn=False):
        """Helper to sync button state and hint label."""
        self.create_button.set_state(state)
        self.status_hint_label.config(text=hint_text)

        if use_gray_btn:
            self.create_button.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        elif state == 'normal':
            self.create_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)

    def _copy_prompt_to_clipboard(self, button, text):
        pyperclip.copy(text)
        original_text = button.text
        # Change button visual state to indicate action performed
        button.config(text="Prompt Copied!", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        # Ensure that hovering always brings back the white-on-green signal
        button.hover_color = c.BTN_GREEN
        button.hover_fg = "#FFFFFF"

        # Advance focus to Step 2
        self.step1_title.config(fg=c.TEXT_COLOR)
        if not self.step2_frame.winfo_ismapped():
            self.step2_frame.grid(row=2, column=0, sticky="nsew")
            self.step2_title.config(fg=c.BTN_GREEN)
            self.llm_result_text.text_widget.focus_set()

        self.after(2000, lambda: button.config(text=original_text) if button.winfo_exists() else None)

    def _get_base_project_content(self):
        base_path = self.project_data.get("base_project_path", tk.StringVar()).get()
        base_files = self.project_data.get("base_project_files", [])
        if not base_path or not base_files: return ""

        content_blocks = ["\n### Example Project Code (For Reference Only)\n"]
        for file_info in base_files:
            rel_path = file_info['path']
            full_path = os.path.join(base_path, rel_path)
            try:
                with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    content = f.read()
                content_blocks.append(f"--- File: `{rel_path}` ---\n```\n" + content + "\n```\n")
            except Exception: pass
        return "\n".join(content_blocks)

    def _generate_master_prompt(self, project_data):
        name = project_data['name'].get()
        stack = project_data['stack'].get()

        concept = SegmentManager.assemble_document(project_data["concept_segments"], c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS) if project_data.get("concept_segments") else project_data.get("concept_md", "")
        todo = SegmentManager.assemble_document(project_data["todo_segments"], c.TODO_ORDER, c.TODO_PHASES) if project_data.get("todo_segments") else project_data.get("todo_md", "")

        # DYNAMICALLY LOAD ALL FILES IN BOILERPLATE DIRECTORY
        prompt_content = ""
        try:
            # List all files, ignoring OS-specific junk files
            files = sorted([
                f for f in os.listdir(BOILERPLATE_DIR)
                if os.path.isfile(os.path.join(BOILERPLATE_DIR, f))
                and f not in {'.DS_Store', 'Thumbs.db', '_start.txt'}
            ])

            for filename in files:
                path = os.path.join(BOILERPLATE_DIR, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        # Include the '--- End of file ---' marker for consistency
                        # This teaches the LLM the correct response format by example.
                        prompt_content += f"--- File: `boilerplate/{filename}` ---\n```\n{f.read()}\n```\n--- End of file ---\n\n"
                except Exception:
                    pass
        except Exception:
            prompt_content = "Error loading boilerplate files."

        example_code = self._get_base_project_content()

        parts = [
            STARTER_GENERATE_MASTER_INTRO.format(name=name, stack=stack),
            "\n### Provided Files\n" + prompt_content,
            "\n### Project Concept\n```markdown\n" + concept + "\n```",
            "\n### TODO Plan\n```markdown\n" + todo + "\n```",
            example_code,
            STARTER_GENERATE_MASTER_INSTR
        ]
        return "\n".join(parts)

    def on_create_project(self):
        raw = self.llm_result_text.get("1.0", "end-1c").strip()
        if not raw: return

        # Strict Regex: Will only match if closing tag exists
        pitch_match = re.search(r"<PITCH>(.*?)</PITCH>", raw, re.DOTALL | re.IGNORECASE)
        project_pitch = pitch_match.group(1).strip() if pitch_match else "a new project"

        # Now get file content
        content = strip_markdown_wrapper(raw)

        self.create_project_callback(content, self.project_data["include_base_reference"].get(), project_pitch)

    def get_llm_response_content(self):
        if hasattr(self, 'llm_result_text') and self.llm_result_text.winfo_exists():
            return {"generate_llm_response": self.llm_result_text.get("1.0", "end-1c").strip()}
        return {}

    def handle_reset(self):
        """Resets the input fields for the generate step."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the response and reset this step?", parent=self):
            # Clear text
            self.llm_result_text.text_widget.delete("1.0", "end")
            self.project_data["generate_llm_response"] = ""

            # Reset interaction flag
            self.step3_interacted = False
            self.step3_title.config(fg=c.TEXT_COLOR)

            # Hide section frames
            self.step2_frame.grid_forget()
            self.step3_frame.grid_forget()

            # Reset titles and navigation state
            self.step1_title.config(fg=c.BTN_GREEN)
            self._validate_and_sync()
            self.starter_controller._update_navigation_controls()
```

--- End of file ---

--- File: `src/ui/project_starter/success_view.py` ---

```python
import tkinter as tk
from pathlib import Path
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..tooltip import ToolTip
from ...core.project_config import _calculate_font_color

class SuccessView(tk.Frame):
    def __init__(self, parent, project_folder_name, files_created, on_start_work_callback, parent_folder, project_color=None):
        super().__init__(parent, bg=c.DARK_BG, padx=20, pady=20)

        accent_color = project_color if project_color else c.BTN_BLUE
        font_mode = _calculate_font_color(accent_color)
        text_color = "#FFFFFF" if font_mode == 'light' else "#000000"

        tk.Label(self, text="Project Created Successfully!", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=10)

        base_path = Path(parent_folder)
        project_path = base_path / project_folder_name
        tk.Label(self, text=f"Your new project is located at:", wraplength=680, bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).pack(pady=5)

        path_entry = tk.Entry(self, font=c.FONT_NORMAL, relief="flat", justify="center")
        path_entry.insert(0, str(project_path.resolve()))
        path_entry.config(
            state="readonly",
            readonlybackground=c.BTN_GRAY_BG,
            fg=c.BTN_GRAY_TEXT
        )
        path_entry.pack(fill='x', pady=5)

        tk.Label(self, text="Files Created:", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(pady=(20, 5), anchor="w")

        listbox = tk.Listbox(
            self, height=15, relief="flat",
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            selectbackground=c.BTN_BLUE, selectforeground=c.BTN_BLUE_TEXT
        )
        for f in files_created:
            listbox.insert(tk.END, f)
        listbox.pack(expand=True, fill="both", pady=5)

        btn_open = RoundedButton(
            self,
            text="Activate Project in CodeMerger",
            command=on_start_work_callback,
            bg=accent_color,
            fg=text_color,
            font=c.FONT_BUTTON,
            height=50,
            width=350,
            cursor="hand2"
        )
        btn_open.pack(pady=20)
        ToolTip(btn_open, "Activate this project and close the wizard", delay=500)
```

--- End of file ---

--- File: `src/ui/project_starter/starter_navigation.py` ---

```python
from tkinter import messagebox
from ... import constants as c
from . import starter_validator

class StarterNavigation:
    def __init__(self, dialog):
        self.dialog = dialog

    def get_active_steps(self):
        steps = [1]
        if self.dialog.starter_state.project_data["base_project_path"].get():
            steps.append(2)
        steps.extend([3, 4, 5, 6])
        return steps

    def go_to_next_step(self):
        active_steps = self.get_active_steps()
        if self.dialog.starter_state.current_step in active_steps:
            current_idx = active_steps.index(self.dialog.starter_state.current_step)
            if current_idx < len(active_steps) - 1:
                self.go_to_step(active_steps[current_idx + 1])

    def go_to_prev_step(self):
        active_steps = self.get_active_steps()
        if self.dialog.starter_state.current_step in active_steps:
            current_idx = active_steps.index(self.dialog.starter_state.current_step)
            if current_idx > 0:
                self.go_to_step(active_steps[current_idx - 1])

    def go_to_step(self, target_step_id):
        if target_step_id == self.dialog.starter_state.current_step: return
        is_accessible = (target_step_id <= self.dialog.starter_state.max_accessible_step) or (target_step_id == 2)
        if not is_accessible: return

        self.dialog.starter_state.update_from_view(self.dialog.current_view)
        self.dialog.starter_state.save()

        if target_step_id > self.dialog.starter_state.current_step:
            is_valid, err_title, err_msg = starter_validator.validate_step(self.dialog.starter_state.current_step, self.dialog.starter_state.project_data)
            if not is_valid:
                messagebox.showerror(err_title, err_msg, parent=self.dialog)
                return
            self.dialog.starter_state.max_accessible_step = max(self.dialog.starter_state.max_accessible_step, target_step_id)

        self.dialog.starter_state.current_step = target_step_id
        self.dialog._show_current_step_view()

    def update_navigation_controls(self):
        self.dialog.prev_button.pack_forget()
        self.dialog.start_over_button.pack_forget()
        self.dialog.next_button.pack_forget()

        active_steps = self.get_active_steps()
        current_idx = active_steps.index(self.dialog.starter_state.current_step)

        if current_idx < len(active_steps) - 1:
            self.dialog.next_button.pack(side="right")

        can_reset = False
        if self.dialog.current_view:
            if hasattr(self.dialog.current_view, 'is_step_in_progress'):
                can_reset = self.dialog.current_view.is_step_in_progress()
            elif hasattr(self.dialog.current_view, 'is_editor_visible'):
                can_reset = self.dialog.current_view.is_editor_visible()

        if can_reset:
            self.dialog.start_over_button.pack(side="right", padx=(0, 10))

        if current_idx > 0:
            self.dialog.prev_button.pack(side="right", padx=(0, 10))

        self.update_nav_state()

    def update_nav_state(self):
        if self.dialog.starter_state.current_step == 6: return
        self.dialog.next_button.config(text="Next >")

        if self.dialog.starter_state.current_step == 2:
            self.dialog.next_button.set_state('normal')
            self.dialog.next_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.dialog.next_tooltip.text = "Skip or confirm base files and proceed"
            return

        if self.dialog.starter_state.current_step == 4:
            stack_val = self.dialog.starter_state.project_data["stack"].get()
            if not stack_val.strip():
                self.dialog.next_button.config(text="Skip", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
                self.dialog.next_tooltip.text = "Proceed without defining a specific stack"
            else:
                self.dialog.next_button.config(text="Next >", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
                self.dialog.next_tooltip.text = "Confirm stack and proceed to TODO plan"
            self.dialog.next_button.set_state('normal')
            return

        is_valid, _, _ = starter_validator.validate_step(self.dialog.starter_state.current_step, self.dialog.starter_state.project_data)
        if is_valid:
            self.dialog.next_button.set_state('normal')
            self.dialog.next_button.config(bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.dialog.next_tooltip.text = "Move to the next step"
        else:
            self.dialog.next_button.set_state('disabled')
            self.dialog.next_button.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
            self.dialog.next_tooltip.text = "Please complete the required fields to continue"
```

--- End of file ---

--- File: `src/ui/project_starter/starter_actions.py` ---

```python
from tkinter import messagebox, filedialog
from . import session_manager

class StarterActions:
    def __init__(self, dialog):
        self.dialog = dialog

    def save_config(self):
        self.dialog.starter_state.update_from_view(self.dialog.current_view)
        project_name = self.dialog.starter_state.project_data["name"].get().strip()
        initial_file = f"{project_name}.json" if project_name else "project-config.json"
        filepath = filedialog.asksaveasfilename(title="Save Project Configuration", defaultextension=".json", initialfile=initial_file, filetypes=[("JSON files", "*.json")], parent=self.dialog)

        if not filepath: return

        session_manager.save_session_data(self.dialog.starter_state.get_dict(), filepath)
        messagebox.showinfo("Success", f"Configuration saved to:\n{filepath}", parent=self.dialog)

    def load_config(self):
        filepath = filedialog.askopenfilename(title="Load Project Configuration", filetypes=[("JSON files", "*.json")], defaultextension=".json", parent=self.dialog)
        if not filepath: return

        self.dialog.starter_state.update_from_view(self.dialog.current_view)
        self.dialog.starter_state.load(filepath)
        self.dialog.starter_state.save()
        self.dialog.starter_state.current_step = 1

        self.dialog.ui_builder.refresh_tabs()
        self.dialog._show_current_step_view()

    def start_over(self):
        if self.dialog.current_view and hasattr(self.dialog.current_view, 'handle_reset'):
            self.dialog.current_view.handle_reset()
            self.dialog.starter_state.update_from_view(self.dialog.current_view)
            self.dialog.starter_state.save()
            self.dialog.navigation.update_nav_state()

    def clear_session_data(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all project data and start fresh?", parent=self.dialog):
            # First, destroy the current view to stop traces from saving back data during the reset
            if self.dialog.current_view and self.dialog.current_view.winfo_exists():
                self.dialog.current_view.destroy()
            self.dialog.current_view = None

            self.dialog.starter_state.reset()
            self.dialog.ui_builder.refresh_tabs()
            self.dialog._show_current_step_view()
```

--- End of file ---

--- File: `src/ui/project_starter/starter_project_creator.py` ---

```python
import os
import json
import re
import logging
from pathlib import Path
from tkinter import messagebox
from ... import constants as c
from ...core import prompts as p
from ...core.utils import load_config
from . import generator
from .segment_manager import SegmentManager
from . import starter_validator

log = logging.getLogger("CodeMerger")

class StarterProjectCreator:
    def __init__(self, dialog):
        self.dialog = dialog

    def create_project(self, llm_output, include_base_reference=False, project_pitch="a new project"):
        dialog = self.dialog
        is_valid, err_title, err_msg = starter_validator.validate_step(6, dialog.starter_state.project_data)
        if not is_valid:
            messagebox.showerror(err_title, err_msg, parent=dialog)
            return

        if not llm_output.strip():
            messagebox.showerror("Error", "LLM Result text area is empty.", parent=dialog)
            return

        raw_project_name = dialog.starter_state.project_data["name"].get()
        parent_folder = dialog.starter_state.project_data["parent_folder"].get()

        color_match = re.search(r"<COLOR>(.*?)</COLOR>", llm_output, re.DOTALL | re.IGNORECASE)
        recommended_color = color_match.group(1).strip() if color_match else None
        if recommended_color and not re.match(r'^#[0-9a-fA-F]{6}$', recommended_color):
            recommended_color = None

        success, project_path, msg = generator.prepare_project_directory(parent_folder, raw_project_name)
        if not success:
            if "already exists" in msg:
                if messagebox.askyesno("Warning", f"{msg} Overwrite?", parent=dialog):
                    success, project_path, msg = generator.prepare_project_directory(parent_folder, raw_project_name, overwrite=True)
                else: return
            if not success:
                messagebox.showerror("Error", msg, parent=dialog)
                return

        success, files_created, msg = generator.parse_and_write_files(project_path, llm_output)
        if not success:
            messagebox.showerror("Error", msg, parent=dialog)
            return

        try:
            concept_segs = dialog.starter_state.project_data.get("concept_segments")
            concept_content = SegmentManager.assemble_document(concept_segs, c.CONCEPT_ORDER, c.CONCEPT_SEGMENTS) if concept_segs else dialog.starter_state.project_data.get("concept_md", "")
            if concept_content:
                (project_path / "concept.md").write_text(concept_content, encoding="utf-8")
                files_created.append("concept.md")

            todo_segs = dialog.starter_state.project_data.get("todo_segments")
            todo_content = SegmentManager.assemble_document(todo_segs, c.TODO_ORDER, c.TODO_PHASES) if todo_segs else dialog.starter_state.project_data.get("todo_md", "")
            if todo_content:
                (project_path / "todo.md").write_text(todo_content, encoding="utf-8")
                files_created.append("todo.md")
        except Exception as e:
            log.error(f"Failed to write mandatory documentation files: {e}")

        try:
            config_data = dialog.starter_state.get_dict()
            starter_json_path = project_path / "project-starter.json"
            with open(starter_json_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            files_created.append("project-starter.json")
        except Exception as e:
            log.error(f"Failed to write project-starter.json: {e}")

        if include_base_reference:
            base_path = dialog.starter_state.project_data["base_project_path"].get()
            base_files = dialog.starter_state.project_data["base_project_files"]
            if generator.write_base_reference_file(project_path, base_path, base_files):
                files_created.append("project_reference.md")

        conf = load_config()
        intro = f"We are working on {project_pitch}.\n\nContinue work on the plan laid out in `todo.md`. If a bug is reported, fix it first. ONLY output `todo.md` (in full, without omissions) when explicitly updating checkbox status."
        outro = conf.get('default_outro_prompt', p.DEFAULT_OUTRO_PROMPT)

        normalized_files = []
        merge_order_exclusion_list =['.gitignore', 'project-starter.json', '2do.txt']

        for f in files_created:
             norm = f.replace('\\', '/')
             if os.path.basename(norm) not in merge_order_exclusion_list:
                 normalized_files.append({'path': norm})

        dialog.app.project_manager.create_project_with_defaults(
            path=str(project_path),
            project_name=raw_project_name,
            intro_text=intro,
            outro_text=outro,
            initial_selected_files=normalized_files,
            project_color=recommended_color
        )

        dialog._display_success_screen(project_path.name, files_created, parent_folder, recommended_color)
```

--- End of file ---

--- File: `src/ui/project_starter/starter_ui_builder.py` ---

```python
import tkinter as tk
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..tooltip import ToolTip

class StarterUIBuilder:
    def __init__(self, dialog):
        self.dialog = dialog

    def build_ui(self):
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(1, weight=1)

        header_frame = tk.Frame(self.dialog, bg=c.DARK_BG, padx=10, pady=10)
        header_frame.grid(row=0, column=0, sticky="ew")

        self.dialog.tabs_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        self.dialog.tabs_frame.pack(side="left", fill='x', expand=True)

        right_header_frame = tk.Frame(header_frame, bg=c.DARK_BG)
        right_header_frame.pack(side="right")

        if self.dialog.app.assets.trash_icon_image:
             self.dialog.btn_clear = RoundedButton(
                right_header_frame, command=self.dialog.actions.clear_session_data,
                image=self.dialog.app.assets.trash_icon_image,
                bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, width=32, height=32, radius=6, cursor="hand2"
            )
             self.dialog.btn_clear.pack(side="right", padx=(0, 0))
             ToolTip(self.dialog.btn_clear, "Clear all starter progress and start fresh", delay=500)

        self.dialog.btn_save = RoundedButton(
            right_header_frame, text="Save Config", command=self.dialog.actions.save_config,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=32, radius=6, cursor="hand2"
        )
        self.dialog.btn_save.pack(side="right", padx=(0, 10))
        ToolTip(self.dialog.btn_save, "Save current project configuration to a file", delay=500)

        self.dialog.btn_load = RoundedButton(
            right_header_frame, text="Load Config", command=self.dialog.actions.load_config,
            bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON,
            height=32, radius=6, cursor="hand2"
        )
        self.dialog.btn_load.pack(side="right", padx=(0, 10))
        ToolTip(self.dialog.btn_load, "Load a previously saved project configuration file", delay=500)

        self.dialog.content_frame = tk.Frame(self.dialog, bg=c.DARK_BG, highlightbackground=c.WRAPPER_BORDER, highlightthickness=1)
        self.dialog.content_frame.grid(row=1, column=0, sticky="nsew", padx=10)

        self.dialog.nav_frame = tk.Frame(self.dialog, bg=c.DARK_BG, padx=10, pady=10)
        self.dialog.nav_frame.grid(row=2, column=0, sticky="ew")

        self.dialog.prev_button = RoundedButton(self.dialog.nav_frame, text="< Prev", command=self.dialog.navigation.go_to_prev_step, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        ToolTip(self.dialog.prev_button, "Go back to the previous step", delay=500)

        self.dialog.start_over_button = RoundedButton(self.dialog.nav_frame, text="Reset step", command=self.dialog.actions.start_over, height=30, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        ToolTip(self.dialog.start_over_button, "Clear the inputs for the current step", delay=500)

        self.dialog.next_button = RoundedButton(self.dialog.nav_frame, text="Next >", command=self.dialog.navigation.go_to_next_step, height=30, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BUTTON, cursor="hand2")
        self.dialog.next_tooltip = ToolTip(self.dialog.next_button, "Validate current inputs and proceed", delay=500)

    def refresh_tabs(self):
        if not self.dialog.tabs_frame: return
        for t in self.dialog.tabs: t.destroy()
        self.dialog.tabs =[]
        active_steps = self.dialog.navigation.get_active_steps()
        for i, step_id in enumerate(active_steps):
            name = self.dialog.steps_map[step_id]
            tab = RoundedButton(self.dialog.tabs_frame, command=lambda s=step_id: self.dialog.navigation.go_to_step(s), text=f"{i+1}. {name}", font=c.FONT_NORMAL, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, height=32, radius=6, hollow=True, cursor="hand2")
            tab.pack(side="left", padx=(0, 5), fill='x', expand=True)
            ToolTip(tab, f"Jump to {name} step", delay=500)
            self.dialog.tabs.append(tab)
        self.update_tab_styles()

    def update_tab_styles(self):
        active_steps = self.dialog.navigation.get_active_steps()
        for i, tab in enumerate(self.dialog.tabs):
            step_id = active_steps[i]
            is_active = (step_id == self.dialog.starter_state.current_step)
            is_accessible = (step_id <= self.dialog.starter_state.max_accessible_step) or (step_id == 2)
            tab.set_state('normal' if is_accessible else 'disabled')
            tab.config(hollow=(not is_active), bg=(c.BTN_BLUE if is_active else c.BTN_GRAY_BG), fg=(c.BTN_BLUE_TEXT if is_active else (c.TEXT_COLOR if is_accessible else c.BTN_GRAY_TEXT)))
```

--- End of file ---

--- File: `src/ui/project_starter/starter_dialog.py` ---

```python
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from ... import constants as c
from ...core.paths import ICON_PATH
from ..style_manager import apply_dark_theme
from .step_details import DetailsView
from .step_concept import ConceptView
from .step_stack import StackView
from .step_todo import TodoView
from .step_generate import GenerateView
from .step_base_files import StepBaseFilesView
from .success_view import SuccessView
from ..window_utils import get_monitor_work_area
from . import starter_state
from ..info_manager import attach_info_mode
from ..assets import assets

from .starter_ui_builder import StarterUIBuilder
from .starter_navigation import StarterNavigation
from .starter_actions import StarterActions
from .starter_project_creator import StarterProjectCreator

class ProjectStarterDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.app = app

        self.finished_successfully = False
        self.starter_state = starter_state.StarterState()
        self.font_size = c.FONT_NORMAL[1]

        self.title("Project Starter")
        self.iconbitmap(ICON_PATH)
        self.configure(bg=c.DARK_BG)
        self.grab_set()

        apply_dark_theme(self)

        self.current_view = None
        self.tabs_frame = None
        self.tabs =[]

        self.steps_map = {
            1: "Details",
            2: "Base Files",
            3: "Concept",
            4: "Stack",
            5: "TODO",
            6: "Generate"
        }

        # Sub-modules
        self.ui_builder = StarterUIBuilder(self)
        self.navigation = StarterNavigation(self)
        self.actions = StarterActions(self)
        self.project_creator = StarterProjectCreator(self)

        self.ui_builder.build_ui()

        self.starter_state.load()

        self.starter_state.project_data["name"].trace_add("write", lambda *args: self.navigation.update_nav_state())
        self.starter_state.project_data["name"].trace_add("write", self._update_window_title)
        self.starter_state.project_data["parent_folder"].trace_add("write", lambda *args: self.navigation.update_nav_state())
        self.starter_state.project_data["stack"].trace_add("write", lambda *args: self.navigation.update_nav_state())

        self.info_toggle_btn = tk.Label(self, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")
        self.info_mgr = attach_info_mode(self, self.app.app_state, manager_type='grid', grid_row=3, toggle_btn=self.info_toggle_btn)
        self._register_static_info()

        self.ui_builder.refresh_tabs()
        self._update_window_title()
        self._show_current_step_view()

        m_left, m_top, m_right, m_bottom = get_monitor_work_area(self.parent)
        self.attributes("-alpha", 0.0)
        self.geometry(f"600x400+{m_left + 50}+{m_top + 50}")
        self.deiconify()
        self.update_idletasks()
        self.state('zoomed')
        self.after(200, self._reveal_after_maximized)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Control-0>", self.reset_zoom)

    def _reveal_after_maximized(self):
        if not self.winfo_exists(): return
        self.attributes("-alpha", 1.0)
        self.focus_force()

    def _show_current_step_view(self):
        if hasattr(self, 'info_mgr'):
            self.info_mgr.clear_active_stack()

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view_frame = tk.Frame(self.content_frame, bg=c.DARK_BG)
        view_frame.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        step = self.starter_state.current_step

        if step > 3 and not self.starter_state.project_data["concept_md"]:
             messagebox.showerror("Concept Missing", "You must complete and merge the Concept document before moving to later steps.", parent=self)
             self.navigation.go_to_step(3)
             return
        if step == 6 and not self.starter_state.project_data["todo_md"]:
             messagebox.showerror("Content Missing", "You must complete and merge the TODO Plan before moving to the Generate step.", parent=self)
             self.navigation.go_to_step(5)
             return

        if step == 1: self.current_view = DetailsView(view_frame, self.starter_state.project_data, starter_controller=self)
        elif step == 2: self.current_view = StepBaseFilesView(view_frame, self, self.starter_state.project_data)
        elif step == 3: self.current_view = ConceptView(view_frame, self, self.starter_state.project_data)
        elif step == 4: self.current_view = StackView(view_frame, self, self.starter_state.project_data)
        elif step == 5: self.current_view = TodoView(view_frame, self, self.starter_state.project_data)
        elif step == 6: self.current_view = GenerateView(view_frame, self.starter_state.project_data, self.create_project, starter_controller=self)

        if self.current_view:
            self.current_view.pack(expand=True, fill="both")
            if hasattr(self.current_view, 'register_info'):
                self.current_view.register_info(self.info_mgr)

        self.ui_builder.update_tab_styles()
        self.navigation.update_navigation_controls()

    def _register_static_info(self):
        self.info_mgr.register(self.info_toggle_btn, "info_toggle")
        self.info_mgr.register(self.prev_button, "starter_nav_prev")
        self.info_mgr.register(self.next_button, "starter_nav_next")
        self.info_mgr.register(self.start_over_button, "starter_nav_reset")
        self.info_mgr.register(self.btn_save, "starter_header_save")
        self.info_mgr.register(self.btn_load, "starter_header_load")
        if hasattr(self, 'btn_clear'):
            self.info_mgr.register(self.btn_clear, "starter_header_clear")

    def _update_window_title(self, *args):
        name = self.starter_state.project_data["name"].get().strip()
        if name:
            self.title(f"Project Starter - {name}")
        else:
            self.title("Project Starter")

    def create_project(self, llm_output, include_base_reference=False, project_pitch="a new project"):
        self.project_creator.create_project(llm_output, include_base_reference, project_pitch)

    def _display_success_screen(self, project_name, files, parent_folder, project_color=None):
        self.finished_successfully = True
        for w in self.content_frame.winfo_children(): w.destroy()
        self.nav_frame.grid_forget()
        def on_start_work():
            full_path = str(Path(parent_folder) / project_name)
            self.starter_state.reset()
            self.app.ui_callbacks.on_directory_selected(full_path)
            self.destroy()
            self.app.after(100, self.app.show_and_raise)
        SuccessView(self.content_frame, project_name, files, on_start_work, parent_folder, project_color=project_color).pack(expand=True, fill="both")

    def on_base_project_selected(self, path):
        self.ui_builder.refresh_tabs()

    def on_closing(self):
        self.starter_state.update_from_view(self.current_view)
        self.starter_state.save()
        if not self.finished_successfully:
            last_path = getattr(self.app, '_last_project_path', None)
            if last_path:
                self.app.project_actions.set_active_dir_display(last_path)
        self.destroy()

    def reset_zoom(self, event=None):
        self.font_size = c.FONT_NORMAL[1]
        if self.current_view and hasattr(self.current_view, 'refresh_fonts'):
            self.current_view.refresh_fonts()

    def adjust_font_size(self, delta):
        new_size = self.font_size + delta
        self.font_size = max(8, min(new_size, 40))
        if self.current_view and hasattr(self.current_view, 'refresh_fonts'):
            self.current_view.refresh_fonts()

    def _update_navigation_controls(self):
        self.navigation.update_navigation_controls()

    def update_nav_state(self):
        self.navigation.update_nav_state()
```

--- End of file ---

--- File: `assets/reference/concept_questions.json` ---

```json
{
  "problem_statement": {
    "label": "Problem & Audience",
    "questions": [
      "Is the target audience clearly defined in terms of pain, frequency, and impact?",
      "Does the problem statement specifically address *why* this solution is needed now?",
      "Are the inputs and outputs of the core problem clearly identified?"
    ]
  },
  "core_principles": {
    "label": "Core Principles",
    "questions": [
      "Do these principles conflict with each other? If so, which one takes precedence?",
      "Are these principles actionable constraints, or just vague marketing terms?",
      "How do these principles guide the technical architecture?"
    ]
  },
  "key_features": {
    "label": "Key Features",
    "questions": [
      "Is each feature strictly necessary to solve the core problem?",
      "Are there features here that belong in a 'Phase 2' or 'Future' list instead?",
      "Is the scope of each feature defined well enough to be estimable?"
    ]
  },
  "user_flows": {
    "label": "User Actions & Flows",
    "questions": [
      "Does the primary workflow have a clear beginning, middle, and end?",
      "Are there missing transitions or decision points in the flow?",
      "How does the system handle failure states (e.g., errors, empty data) in this flow?"
    ]
  },
  "tech_constraints": {
    "label": "Data & Tech Constraints",
    "questions": [
      "Is the 'Source of Truth' clearly defined for data synchronization?",
      "Are there any implicit technical assumptions that need to be validated early?",
      "Does the conflict resolution strategy handle edge cases (e.g., offline mode)?"
    ]
  }
}
```

--- End of file ---

--- File: `assets/reference/todo_questions.json` ---

```json
{
  "setup": {
    "label": "Environment Setup",
    "questions": [
        "Does the setup include a 'Hello World' verification for the full stack?",
        "Are all necessary tools (DB, Languages, Docker) explicitly listed?"
    ]
  },
  "database": {
    "label": "Database & Schema",
    "questions": [
        "Does the schema support all Key Features defined in the Concept?",
        "Are migrations or schema management tools included in the tasks?"
    ]
  },
  "api": {
    "label": "API & Backend",
    "questions": [
        "Are the CRUD endpoints comprehensive enough for the User Flows?",
        "Is authentication and authorization included if required?"
    ]
  },
  "frontend": {
    "label": "Frontend & UI",
    "questions": [
        "Do the UI tasks cover all visual states (Loading, Error, Empty)?",
        "Is the connection to the backend explicitly tested in these tasks?"
    ]
  },
  "logic": {
    "label": "Core Logic",
    "questions": [
        "Are complex business rules broken down into testable units?",
        "Does this phase connect the UI to the real data (replacing mocks)?"
    ]
  },
  "polish": {
    "label": "Polish",
    "questions": [
        "Are there tasks for error handling and user feedback notifications?",
        "Does this include UI refinement and consistency checks?"
    ]
  },
  "deployment": {
    "label": "Deployment",
    "questions": [
        "Are build and optimization steps included?",
        "Is environment configuration (secrets, variables) handled safely?"
    ]
  }
}
```

--- End of file ---

--- File: `assets/reference/concept.md` ---

```markdown
# Project Concept Template

A lightweight, [describe your application's category, e.g., productivity, social] app for [target audience] to [solve a specific problem]. The app allows users to [core action] with [key features]. This is designed as a [web app, mobile app, desktop app] for [number or type of users].

---

## Core Principles

- **Principle 1:** Explain the foundational idea behind your app. What is the most important concept a user should understand?
- **Principle 2:** Describe another core rule or philosophy. How does the app behave in a predictable way?
- **Principle 3:** Add any other guiding principles that define the user experience.

## Key Features

### Feature A: [Name of Feature]
- Describe the feature's purpose and how it works from a user's perspective
- Detail the specific actions a user can take related to this feature

### Feature B: [Name of Feature]
- Describe this second feature, its purpose, and its mechanics
- List the user interactions involved

---

## User Actions

- **[Action 1]:** Who can perform this action and under what conditions? (e.g., The creator of an item can edit its title)
- **[Action 2]:** What is another key interaction? What are its rules?
- **[Action 3]:** Detail any other significant user capabilities

---

## Data Synchronization Strategy

- **Source of Truth:** The [backend/client] is the single source of truth for all data. The UI updates based on responses from the authoritative source
- **Data Flow:** Describe how data gets from the server to the client. Is it through polling, a push-based service (like WebSockets), or simple request-response?
- **Conflict Resolution:** Explain how the system will handle potential conflicts. For example, if two users try to edit the same resource at once, how is that resolved? Often, the "source of truth" principle is sufficient, where the first-to-arrive action wins and the second is rejected
```

--- End of file ---

--- File: `assets/reference/todo.md` ---

```markdown
# Project Bootstrap TODO

This plan outlines the phases for building out the project, from initial setup to a deployable application.

## Phase 1: Environment Setup & Core Connection
**Goal:** A working local environment is established, with confirmed communication between frontend and backend.

- [ ] **Database:** Set up the initial schema based on `concept.md`.
  - [ ] Design and implement the initial database tables (e.g., `users`, `[primary_resource]`).
  - [ ] Implement a migration tool for schema management.
  - [ ] Populate database with seed data for development (e.g., test user accounts).
- [ ] **API:** Implement the first health-check endpoint.
  - [ ] Implement a read-only endpoint (e.g., `/api/status`) to confirm server and database connectivity.
- [ ] **Frontend:** Connect to the backend.
  - [ ] Implement a basic API client to call the backend `/api/status` endpoint and log the response.
- [ ] **Testing Point 1: Verify Core Connection**
  - [ ] Run the backend server using `go.bat`.
  - [ ] Launch the frontend development server.
  - [ ] Confirm the frontend successfully fetches data from the backend status endpoint.

## Phase 2: Core Feature UI & Data Display
**Goal:** The primary user interface is built and displays static or mock data.

- [ ] **UI Development:** Implement the main application view
  - [ ] Create the primary layout and navigation components
  - [ ] Implement the UI for the core feature of your application
  - [ ] Implement any necessary routing
- [ ] **Data Display:** Render data within the UI
  - [ ] Create components to display the main data entities of your app
  - [ ] Populate UI with mock data, ensuring all visual states (loading, error, success, empty) are handled
- [ ] **Testing Point 2: Verify UI & Data Rendering**
  - [ ] Confirm the main UI populates correctly with mock data
  - [ ] Test that navigation and user flows are working as expected
  - [ ] Verify that all key visual states are represented correctly

## Phase 3: Core Logic & User Actions
**Goal:** Application logic is implemented, allowing data interaction and modification.

- [ ] **API:** Implement CRUD (Create, Read, Update, Delete) endpoints for the core features
  - [ ] Secure endpoints with authentication and authorization logic
  - [ ] Implement an endpoint to create a new resource
  - [ ] Implement an endpoint to update or delete a resource
  - [ ] Implement input validation for all endpoints
- [ ] **Frontend:** Implement user interaction flows
  - [ ] Create forms or modals for creating and editing data
  - [ ] Connect the UI elements (buttons, forms) to the corresponding backend API endpoints
  - [ ] Implement client-side state management to reflect data changes without a full page reload
- [ ] **Data & Sync Logic:** Implement data synchronization between the frontend and backend
  - [ ] Select and implement a data-fetching strategy (e.g., polling, WebSockets, or request-response)
  - [ ] Implement caching or local storage if needed to improve performance or provide offline support
- [ ] **Testing Point 3: Verify End-to-End User Actions**
  - [ ] Test the full user flow: create a new piece of data, see it appear in the UI, edit it, and then delete it
  - [ ] Verify that authentication prevents unauthorized actions
  - [ ] Ensure the UI provides feedback to the user on the status of their actions (e.g., loading indicators, success/error messages)

## Phase 4: Automation & Polishing
**Goal:** Automated processes are implemented and the user experience is polished.

- [ ] **Backend:** Implement required background jobs or scheduled tasks
  - [ ] Create scripts for tasks that need to run on a schedule (e.g., data cleanup, report generation, notifications)
  - [ ] Configure a task runner or scheduler (e.g., cron, Celery, etc)
- [ ] **Frontend/UI:** Implement secondary features and polish the user experience
  - [ ] Implement any remaining features like user profiles, settings, or help sections
  - [ ] Add simple in-app alerts or notifications
  - [ ] Refine UI with animations, improved typography, and consistent spacing
- [ ] **Testing Point 4: Verify Automation and Polish**
  - [ ] Manually trigger any background jobs to confirm they work correctly
  - [ ] Test all secondary features
  - [ ] Review the application for any UI/UX inconsistencies

## Phase 5: Deployment
**Goal:** The application is packaged and deployed to a production environment.

- [ ] **Frontend:** Package the application for production
  - [ ] Run the build process to create optimized static assets
- [ ] **Backend:** Prepare the backend for production deployment
  - [ ] Finalize environment configuration for production (e.g., database credentials, secret keys)
- [ ] **Deployment:** Deploy the services
  - [ ] Deploy backend services to the selected hosting provider
  - [ ] Deploy the frontend application
  - [ ] Verify scheduled jobs are running correctly in production
- [ ] **Post-Deployment Testing:**
  - [ ] Conduct end-to-end tests on the live production environment

## Future Enhancements
- [ ] List potential features or improvements for future versions
- [ ]
- [ ]
```

--- End of file ---

--- File: `assets/boilerplate/README.md` ---

```markdown
# [ProjectName]

[A brief, one-sentence description of your project. Explain what it does and for whom.]

See [concept.md](concept.md) for a detailed breakdown of the application's features, logic, and architecture.

## Getting Started

Follow these steps to get your development environment set up and running.

### 1. Prerequisites

Based on the **[CodeStack]** stack, you will need the following tools installed on your system:

- **Git:** For version control.
- **[Language/Runtime, e.g., Node.js v18+, Python 3.10+]:** The core runtime environment.
- **[Package Manager, e.g., npm, pip]:** For managing dependencies.
- **[Database, e.g., PostgreSQL, SQLite]:** The database system.
- **[Any other required CLI tools, e.g., Docker]:** Any other tools needed.

### 2. Clone and Initialize the Repository

First, get the code. Then, it's highly recommended to initialize it as your own Git repository and connect it to a remote like GitHub.

```bash
# If you cloned this from somewhere else, you might want to remove the old .git folder
# rm -rf .git

# Initialize a new local repository
git init
git add .
git commit -m "Initial commit from boilerplate"

# Follow instructions from your Git provider (e.g., GitHub) to create a new
# repository and connect it.
# git remote add origin <your-new-repository-url>
# git push -u origin main
```

### 3. Install Dependencies & Run

This project uses a `go.bat` script to streamline common tasks.

To install dependencies and run the application for the first time, simply execute:

```bash
go.bat
```

**What this does:**
- For **Node.js/Docker** projects, you may need to run `go i` first to install dependencies. The LLM should clarify this based on the stack.
- For **Python** projects, this script will automatically create a virtual environment (`.venv`) and install dependencies from `requirements.txt` on the first run.
- Subsequent runs of `go.bat` will just start the application.

Once running:
- The API will be available at `http://localhost:[PORT]`.
- The frontend will be available at `http://localhost:[PORT]`.

See the `go.bat` script for other available commands like `build`, `test`, or `release`.
```

--- End of file ---

--- File: `assets/boilerplate/llm.md` ---

```markdown
# Notes on project quirks for language models

**Core Directive: Act as a support programmer.**
Assume the user has full project context. Do not explain obvious code, file structures, or self-evident logic.

**The Litmus Test: The "Surprise" Factor**
Before adding a note, ask: **"Would an experienced developer be surprised by this code? Is it a workaround, a counter-intuitive performance hack, or a deviation from a standard pattern?"** If the answer is no, do not add a note.

**DO (Only if it passes the "Surprise" Test):**

- **Log Workarounds:** Document solutions that exist specifically to fix a library bug, an OS-level inconsistency, or a race condition
- **Log Atypical Choices:** Note *why* a solution was chosen when a more common or obvious one was deliberately avoided (e.g., "Used library X instead of the more popular library Y because Y has a memory leak on a specific platform")
- **Log Complex Business Logic:** If a piece of code is inherently complex due to project requirements (e.g., a complex state machine), briefly note the reason for its complexity

**DO NOT:**

- **Do not log routine bug fixes.** A fix for a common logic error is standard development, not a project quirk
- **Do not log standard implementation patterns.** Using a specific design pattern or a common programming idiom is expected
- **Do not write summaries** of the project, architecture, or individual file functions
- **Do not explain basic concepts** or write long paragraphs
- **Do not explain user-facing benefits.**

---

### Quick Examples

**Good Note (A Workaround):**

- `src/utils/image_loader.js`: Uses a two-stage load to avoid a browser-specific rendering race condition. This is intentional

**Good Note (An Atypical Choice):**
- `src/core/plugin_manager.py`: Explicitly defines all plugins in a config file instead of relying on filesystem discovery, which was found to be unreliable in a bundled executable

**Bad Note (A Routine Bug Fix):**

- `src/components/ErrorDialog.vue`: The dialog was changed to be instantiated with its own state... *(This is a standard fix for component state issues and should not be logged)*

**Bad Note (An Obvious Summary):**

- `src/main.js`: This file contains the main application class which initializes the UI...

---

## Code Quirks & Workarounds
*(Append new notes below this line)*
```

--- End of file ---

--- File: `assets/boilerplate/version.txt` ---

```text
Major=0
Minor=0
Revision=1
```

--- End of file ---

--- File: `assets/boilerplate/release.bat` ---

```batch
@echo off
setlocal enabledelayedexpansion

:: =================================================================
:: Reusable Release Script
:: Handles version checking, branch validation, and git tagging.
::
:: USAGE: call release.bat [path_to_version_file]
:: =================================================================

set "VERSION_FILE=%1"
if not defined VERSION_FILE (
    echo ERROR: Path to version file not specified.
    exit /b 1
)

:: --- 1. Get Version ---
call :GetVersion "%VERSION_FILE%"
if !errorlevel! neq 0 (
    echo Aborting: version file error.
    exit /b 1
)
set "VERSION_TAG=v!VERSION!"
echo Version found: !VERSION_TAG!

:: --- 2. Check Git Status ---
git diff-index --quiet HEAD --
if !errorlevel! neq 0 (
    echo.
    echo ERROR: Uncommitted changes detected in the working directory.
    echo Commit or stash changes before creating a release tag.
    exit /b 1
)
echo ✓ Git working directory clean.

:: --- 3. Check Branch ---
set "CURRENT_BRANCH="
for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set "CURRENT_BRANCH=%%b"
if /I not "!CURRENT_BRANCH!"=="master" if /I not "!CURRENT_BRANCH!"=="main" (
    echo.
    echo WARNING: Current branch is '!CURRENT_BRANCH!', not 'main' or 'master'.
    echo Releases should originate from a primary branch.
    exit /b 1
)
echo ✓ On primary branch ('!CURRENT_BRANCH!').

:: --- 4. Handle Existing Tag ---
echo Checking for existing remote/local tag '!VERSION_TAG!'...
git rev-parse "!VERSION_TAG!" >nul 2>&1
if !errorlevel! equ 0 (
    echo Deleting existing local tag.
    git tag -d !VERSION_TAG!
)
git ls-remote --tags origin refs/tags/!VERSION_TAG! | findstr "refs/tags/!VERSION_TAG!" > nul
if !errorlevel! equ 0 (
    echo Deleting existing remote tag.
    git push origin --delete !VERSION_TAG! >nul 2>&1
)

:: --- 5. Create and Push New Tag ---
echo.
echo Creating new annotated tag !VERSION_TAG!...
git tag -a "!VERSION_TAG!" -m "Release !VERSION_TAG!"
if !errorlevel! neq 0 (
    echo FATAL: Tag creation failed.
    exit /b 1
)

echo Pushing tag to origin...
git push origin !VERSION_TAG!
if !errorlevel! neq 0 (
    echo FATAL: Tag push to origin failed.
    exit /b 1
)

echo.
echo ### Release !VERSION_TAG! tagged and pushed successfully. ###
goto :eof

:GetVersion
    if not exist "%~1" (
        echo ERROR: Version file not found: '%~1'.
        exit /b 1
    )
    set "MAJOR_VER=" & set "MINOR_VER=" & set "REVISION_VER="
    for /f "tokens=1,2 delims==" %%a in (%~1) do (
        if /i "%%a"=="Major" set "MAJOR_VER=%%b"
        if /i "%%a"=="Minor" set "MINOR_VER=%%b"
        if /i "%%a"=="Revision" set "REVISION_VER=%%b"
    )
    if not defined MAJOR_VER ( echo ERROR: 'Major' version key not found in %~1. & exit /b 1 )
    if not defined MINOR_VER ( echo ERROR: 'Minor' version key not found in %~1. & exit /b 1 )
    if not defined REVISION_VER ( echo ERROR: 'Revision' version key not found in %~1. & exit /b 1 )
    set "VERSION=%MAJOR_VER%.%MINOR_VER%.%REVISION_VER%"
    exit /b 0
```

--- End of file ---

--- File: `assets/boilerplate/go_python.bat` ---

```batch
@echo off
setlocal enabledelayedexpansion

:: =================================================================
:: SECTION 1: CONFIGURATION
:: =================================================================
set "PROJECT_NAME=MyPythonApp"
set "VENV_DIR=.venv"
set "START_SCRIPT=src.main"
set "SPEC_FILE=%PROJECT_NAME%.spec"
set "VERSION_FILE=version.txt"
set "FLAG=%1"
set "ARG2=%2"

:: =================================================================
:: SECTION 2: COMMAND ROUTER
:: =================================================================
if /I "%FLAG%"=="" goto :DefaultAction
if /I "%FLAG%"=="cmd" goto :OpenCmd
if /I "%FLAG%"=="f" goto :FreezeReqs
if /I "%FLAG%"=="b" goto :BuildApp
if /I "%FLAG%"=="r" goto :HandleRelease
echo Unrecognized command: "%FLAG%".
goto :Usage

:DefaultAction
    call :ActivateVenv
    if !errorlevel! neq 0 goto :eof
    echo Starting %PROJECT_NAME%...
    python -m %START_SCRIPT%
    goto :eof

:OpenCmd
    call :ActivateVenv
    if !errorlevel! neq 0 goto :eof
    echo Virtual environment activated in new command prompt.
    cmd /k
    goto :eof

:FreezeReqs
    call :ActivateVenv
    if !errorlevel! neq 0 goto :eof
    echo Freezing dependencies to requirements.txt...
    pip freeze > requirements.txt
    echo Done.
    goto :eof

:BuildApp
    call :ActivateVenv
    if !errorlevel! neq 0 goto :eof
    echo.
    echo ### Starting Build Process ###
    echo.

    if /I "%ARG2%"=="cpu" (
        echo Forcing CPU-only PyTorch installation...
        pip install --force-reinstall torch torchaudio
    )

    echo Deleting old build folders...
    rmdir /s /q dist 2>nul
    rmdir /s /q build 2>nul
    echo.
    echo Running PyInstaller...
    pyinstaller %SPEC_FILE%
    if !errorlevel! neq 0 (
        echo.
        echo FATAL: PyInstaller build failed.
        goto :eof
    )
    echo.
    echo Build complete. Executable is in the 'dist' folder.
    goto :eof

:HandleRelease
    if not exist "release.bat" (
        echo ERROR: release.bat script not found.
        goto :eof
    )
    call release.bat %VERSION_FILE%
    goto :eof

:ActivateVenv
    if defined VIRTUAL_ENV exit /b 0

    if not exist "%VENV_DIR%\Scripts\activate" (
        echo.
        echo Virtual environment not found. Running one-time setup...
        python -m venv %VENV_DIR%
        if !errorlevel! neq 0 (
            echo ERROR: Failed to create venv. Verify Python installation and PATH.
            exit /b 1
        )
        call %VENV_DIR%\Scripts\activate
        echo.
        echo --- Upgrading Core Packaging Tools ---
        python -m pip install --upgrade pip setuptools wheel
        if exist requirements.txt (
            echo.
            echo --- Installing Application Requirements ---
            pip install -r requirements.txt
            if !errorlevel! neq 0 exit /b 1
        )
        echo.
        echo --- Setup complete! ---
        echo.
    ) else (
        call %VENV_DIR%\Scripts\activate
    )
    exit /b 0

:Usage
    echo.
    echo Commands:
    echo   (no flag) - Runs the main application script
    echo   cmd       - Opens a command prompt with the venv activated
    echo   f         - Freezes dependencies to requirements.txt
    echo   b         - Builds the application using PyInstaller
    echo   r         - Handles the release tagging process
    echo.
    goto :eof
```

--- End of file ---

--- File: `assets/boilerplate/go_nodejs.bat` ---

```batch
@echo off
setlocal

set "PROJECT_NAME=MyNodeProject"
set "FLAG=%1"

if "%FLAG%"=="" goto :DefaultAction
if /I "%FLAG%"=="i" goto :InstallDeps
if /I "%FLAG%"=="dev" goto :RunDev
if /I "%FLAG%"=="b" goto :RunBuild
if /I "%FLAG%"=="s" goto :RunStart
if /I "%FLAG%"=="x" goto :RunStop
if /I "%FLAG%"=="r" goto :HandleRelease
echo Unrecognized command: "%FLAG%"
goto :Usage

:DefaultAction
    echo Starting %PROJECT_NAME% in production mode...
    call :CheckNodeModules
    if errorlevel 1 goto :eof
    npm start
    goto :eof

:InstallDeps
    echo Installing node modules...
    npm install
    goto :eof

:RunDev
    echo Starting development server...
    call :CheckNodeModules
    if errorlevel 1 goto :eof
    npm run dev
    goto :eof

:RunBuild
    echo Creating a production build...
    call :CheckNodeModules
    if errorlevel 1 goto :eof
    npm run build
    goto :eof

:RunStart
    echo Starting production server via process manager (e.g., pm2)...
    call :CheckNodeModules
    if errorlevel 1 goto :eof
    npm start
    goto :eof

:RunStop
    echo Stopping server...
    npm run stop
    goto :eof

:HandleRelease
    if not exist "release.bat" (
        echo ERROR: release.bat script not found.
        goto :eof
    )
    call release.bat version.txt
    goto :eof

:CheckNodeModules
    if not exist "node_modules" (
        echo.
        echo WARNING: 'node_modules' folder not found.
        echo ACTION: Run 'go i' to install dependencies.
        echo.
        exit /b 1
    )
    exit /b 0

:Usage
    echo.
    echo Commands:
    echo   i    - Installs dependencies (npm install)
    echo   dev  - Starts the development server (npm run dev)
    echo   b    - Builds the application for production (npm run build)
    echo   s    - Starts the production application (npm start)
    echo   x    - Stops the production application (npm run stop)
    echo   r    - Handles the release tagging process
    goto :eof
```

--- End of file ---

--- File: `assets/boilerplate/go_docker.bat` ---

```batch
@echo off
setlocal

set "PROJECT_NAME=my-docker-project"
set "FLAG=%1"

if "%FLAG%"=="" goto :StartEnv
if /I "%FLAG%"=="i" goto :InstallDeps
if /I "%FLAG%"=="u" goto :UpdateDeps
if /I "%FLAG%"=="x" goto :StopEnv
if /I "%FLAG%"=="shell" goto :OpenShell
if /I "%FLAG%"=="build" goto :BuildEnv
echo Unrecognized command: "%FLAG%".
goto :Usage

:StartEnv
    echo Starting Docker environment for '%PROJECT_NAME%'...
    docker-compose -p %PROJECT_NAME% up -d
    goto :eof

:StopEnv
    echo Stopping Docker environment for '%PROJECT_NAME%'...
    docker-compose -p %PROJECT_NAME% stop
    goto :eof

:BuildEnv
    echo Building/rebuilding Docker images for '%PROJECT_NAME%'...
    docker-compose -p %PROJECT_NAME% build
    goto :eof

:InstallDeps
    echo Installing dependencies inside the container...
    REM Example for a PHP/Composer project:
    docker-compose -p %PROJECT_NAME% exec web composer install
    REM Example for a Node.js project:
    REM docker-compose -p %PROJECT_NAME% exec web npm install
    goto :eof

:UpdateDeps
    echo Updating dependencies inside the container...
    REM Example for a PHP/Composer project:
    docker-compose -p %PROJECT_NAME% exec web composer update
    REM Example for a Node.js project:
    REM docker-compose -p %PROJECT_NAME% exec web npm update
    goto :eof

:OpenShell
    echo Opening shell in 'web' container...
    docker-compose -p %PROJECT_NAME% exec web bash
    goto :eof

:Usage
    echo.
    echo Commands:
    echo   (no flag) - Starts the docker environment (up -d)
    echo   build     - Builds/rebuilds docker images
    echo   i         - Installs dependencies inside the container
    echo   u         - Updates dependencies inside the container
    echo   shell     - Opens a shell in the main 'web' container
    echo   x         - Stops the docker environment
    goto :eof
```

--- End of file ---

--- File: `go.bat` ---

```batch
@echo off
setlocal

REM Configuration
set VENV_DIR=cm-venv
set START_SCRIPT=src.codemerger
set SPEC_FILE=codemerger.spec
set FLAG=%1

REM Environment Setup
if "%VIRTUAL_ENV%"=="" (
    if not exist "%VENV_DIR%\Scripts\activate" (
        echo Virtual environment not found. Creating a new one...
        python -m venv %VENV_DIR%
        call %VENV_DIR%\Scripts\activate
        if exist requirements.txt (
            echo Installing required packages...
            pip install -r requirements.txt
        )
    ) else (
        echo Activating virtual environment...
        call %VENV_DIR%\Scripts\activate
    )
)

REM Main Command Router
if /I "%FLAG%"=="" goto :DefaultAction
if /I "%FLAG%"=="cmd" goto :OpenCmd
if /I "%FLAG%"=="f" goto :FreezeReqs
if /I "%FLAG%"=="b" goto :BuildFull
if /I "%FLAG%"=="ba" goto :BuildAppOnly
if /I "%FLAG%"=="bi" goto :BuildInstallerOnly
if /I "%FLAG%"=="r" goto :HandleRelease
echo Unrecognized command: %FLAG%
goto :eof

:DefaultAction
    echo Starting CodeMerger application...
    REM Set environment variable to disable instance detection for dev launches
    set CM_DEV_MODE=1
    python -m %START_SCRIPT%
    goto :eof

:OpenCmd
    echo Virtual environment activated. You are now in a new command prompt.
    cmd /k
    goto :eof

:FreezeReqs
    echo.
    echo Writing requirements.txt
    pip freeze > requirements.txt
    echo Done.
    goto :eof

:GetVersion
    if not exist "version.txt" (
        echo ERROR: version.txt not found.
        exit /b 1
    )
    set "MAJOR_VER="
    set "MINOR_VER="
    set "REVISION_VER="
    for /f "tokens=1,2 delims==" %%a in (version.txt) do (
        if /i "%%a"=="Major" set "MAJOR_VER=%%b"
        if /i "%%a"=="Minor" set "MINOR_VER=%%b"
        if /i "%%a"=="Revision" set "REVISION_VER=%%b"
    )
    if not defined MAJOR_VER ( echo ERROR: "Major" version not found in version.txt. & exit /b 1 )
    if not defined MINOR_VER ( echo ERROR: "Minor" version not found in version.txt. & exit /b 1 )
    if not defined REVISION_VER ( echo ERROR: "Revision" version not found in version.txt. & exit /b 1 )
    set "VERSION=%MAJOR_VER%.%MINOR_VER%.%REVISION_VER%"
    exit /b 0

:BuildFull
    call :RunPyInstaller
    if %errorlevel% neq 0 goto :eof

    call :BuildInstaller
    if %errorlevel% neq 0 (
        echo Installer build failed. See warnings above.
    )

    echo.
    echo Full Build Finished.
    goto :eof

:BuildAppOnly
    call :RunPyInstaller
    goto :eof

:RunPyInstaller
    setlocal
    echo.
    echo Starting PyInstaller Build Process
    echo Deleting old build folders...
    rmdir /s /q dist 2>nul
    rmdir /s /q build 2>nul
    rmdir /s /q dist-installer 2>nul
    echo Running PyInstaller with %SPEC_FILE%
    pyinstaller %SPEC_FILE%
    if %errorlevel% neq 0 (
        echo.
        echo FATAL: PyInstaller build failed.
        endlocal
        goto :eof
    )
    echo Executable build complete! Found in 'dist' folder.
    endlocal
    goto :eof

:BuildInstallerOnly
    call :BuildInstaller
    goto :eof

:BuildInstaller
    setlocal enabledelayedexpansion
    echo.
    echo Starting Installer Build Process

    if not exist "dist" (
        echo ERROR: 'dist' folder not found.
        echo Please run the full build ^('go b'^) first to create the application executable.
        endlocal
        exit /b 1
    )

    echo Deleting old installer folder...
    rmdir /s /q dist-installer 2>nul

    call :GetVersion
    if !errorlevel! neq 0 ( endlocal & goto :eof )

    set "INNO_SETUP_PATH="
    if exist "%ProgramFiles(x86)%\Inno Setup 6\iscc.exe" set "INNO_SETUP_PATH=%ProgramFiles(x86)%\Inno Setup 6\iscc.exe"
    if not defined INNO_SETUP_PATH if exist "%ProgramFiles%\Inno Setup 6\iscc.exe" set "INNO_SETUP_PATH=%ProgramFiles%\Inno Setup 6\iscc.exe"

    if not defined INNO_SETUP_PATH (
        echo.
        echo WARNING: Inno Setup not found. Skipping installer creation.
        echo To build an installer, download and install Inno Setup from jrsoftware.org
        endlocal
        exit /b 1
    )

    echo Compiling installer with Inno Setup for v!VERSION!...
    "!INNO_SETUP_PATH!" setup.iss /dMyAppVersion="!VERSION!"

    if !errorlevel! neq 0 (
        echo.
        echo FATAL: Inno Setup build failed.
        endlocal
        exit /b 1
    )

    echo.
    echo Installer Build Complete! Found in 'dist-installer' folder.
    endlocal
    goto :eof

:HandleRelease
    setlocal enabledelayedexpansion
    echo.
    echo Handling Release Tag

    REM Check if on master branch
    set "CURRENT_BRANCH="
    for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set "CURRENT_BRANCH=%%b"

    if not defined CURRENT_BRANCH (
        echo ERROR: Could not determine the current git branch.
        echo Make sure this is a valid git repository. Aborting.
        endlocal
        goto :eof
    )

    if /I not "!CURRENT_BRANCH!"=="master" (
        echo.
        echo WARNING: You are not on the 'master' branch.
        echo Current branch is '!CURRENT_BRANCH!'.
        echo Releases should only be made from the 'master' branch.
        echo.
        echo Aborting release process.
        endlocal
        goto :eof
    )

    REM Get version
    call :GetVersion
    if !errorlevel! neq 0 ( endlocal & goto :eof )

    set "VERSION_TAG=v!VERSION!"
    echo Found version tag: !VERSION_TAG!

    REM --- Forcefully clean up any existing tags with the same name ---
    echo Checking for existing tags to determine release comment...
    set "IS_RETRIGGER=0"
    REM Check if tag exists locally OR remotely to set the flag
    git rev-parse "!VERSION_TAG!" >nul 2>nul
    if %errorlevel% equ 0 set "IS_RETRIGGER=1"
    git ls-remote --tags origin refs/tags/!VERSION_TAG! | findstr "refs/tags/!VERSION_TAG!" > nul
    if %errorlevel% equ 0 set "IS_RETRIGGER=1"

    REM Now, unconditionally delete remote and local tags, ignoring errors
    echo Cleaning up old tags...
    git push origin --delete !VERSION_TAG! >nul 2>nul
    git tag -d !VERSION_TAG! >nul 2>nul
    echo Cleanup complete.

    REM Get optional release comment
    shift /1
    set "COMMENT="
    :ArgLoop
    if "%~1"=="" goto EndArgLoop
    if not defined COMMENT (
        set "COMMENT=%~1"
    ) else (
        set "COMMENT=!COMMENT! %~1"
    )
    shift /1
    goto ArgLoop
    :EndArgLoop

    REM Default comment if user did not provide one
    if not defined COMMENT (
        if "!IS_RETRIGGER!"=="1" (
            set "COMMENT=Re-triggering release build for !VERSION_TAG!"
        ) else (
            set "COMMENT=Initial release for !VERSION_TAG!"
        )
    )
    echo Release comment: !COMMENT!

    REM Create and push tag
    echo Creating annotated tag !VERSION_TAG!...
    git tag -a "!VERSION_TAG!" -m "!COMMENT!"
    if %errorlevel% neq 0 (
        echo FATAL: Failed to create tag. Aborting.
        endlocal
        goto :eof
    )

    echo Pushing new tag !VERSION_TAG! to origin...
    git push origin !VERSION_TAG!
    echo.
    echo Release Action Triggered!
    endlocal
    goto :eof
```

--- End of file ---

--- File: `updater_gui.py` ---

```python
# updater_gui.py
import sys
import os
import time
import requests
import subprocess
import tempfile
import threading
import tkinter as tk
import logging
from tkinter import ttk, messagebox
import shutil

# Self-Contained Constants
DARK_BG = '#2E2E2E'
TEXT_COLOR = '#FFFFFF'
TEXT_INPUT_BG = '#3C3C3C'
TEXT_SUBTLE_COLOR = '#A0A0A0'
BTN_BLUE = '#0078D4'
FONT_NORMAL = ("Segoe UI", 11)
FONT_STATUS_BAR = ("Segoe UI", 9)
FONT_BUTTON = ("Segoe UI", 12)

# Logging Setup
log_dir = tempfile.gettempdir()
log_file = os.path.join(log_dir, "codemerger_updater.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8')
    ]
)
log = logging.getLogger(__name__)

def is_pid_running(pid):
    """
    Checks if a process with the given PID is running.
    This is a dependency-free implementation for Windows using ctypes.
    """
    if sys.platform != "win32":
        # Fallback for non-windows, though this updater is windows-specific
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    import ctypes
    kernel32 = ctypes.windll.kernel32
    PROCESS_QUERY_INFORMATION = 0x0400

    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid)
    if handle == 0:
        return False

    # If we have a handle, the process exists. We must close it.
    kernel32.CloseHandle(handle)
    return True

def get_bundle_dir():
    """Gets the base path for reading bundled resources."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(".")

class UpdateGUI(tk.Tk):
    def __init__(self, pid_to_wait_for, download_url):
        super().__init__()
        self.withdraw()  # Start hidden

        try:
            bundle_dir = get_bundle_dir()
            icon_path = os.path.join(bundle_dir, 'assets', 'install.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            # Silently fail if icon cannot be set.
            pass

        self.pid_to_wait_for = pid_to_wait_for
        self.download_url = download_url
        self.installer_path = None
        self.temp_dir = None
        self.cancelled = False

        self._setup_window()

        self.update_thread = threading.Thread(target=self._update_worker)
        self.update_thread.daemon = True
        self.update_thread.start()

    def _setup_window(self):
        self.title("Updating CodeMerger")
        self.resizable(False, False)
        self.configure(bg=DARK_BG, padx=20, pady=20)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.status_label = tk.Label(self, text="Waiting for CodeMerger to close...", bg=DARK_BG, fg=TEXT_COLOR, font=FONT_NORMAL)
        self.status_label.pack(pady=(0, 10), anchor='w')

        s = ttk.Style(self)
        s.theme_use('default')
        s.configure('Update.Horizontal.TProgressbar', background=BTN_BLUE, troughcolor=TEXT_INPUT_BG, bordercolor=TEXT_INPUT_BG, lightcolor=BTN_BLUE, darkcolor=BTN_BLUE)

        self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=400, mode='determinate', style='Update.Horizontal.TProgressbar')
        self.progress_bar.pack(pady=5, fill='x', expand=True)

        self.details_label = tk.Label(self, text="", bg=DARK_BG, fg=TEXT_SUBTLE_COLOR, font=FONT_STATUS_BAR)
        self.details_label.pack(pady=(5, 15), anchor='e')

        self.cancel_button = tk.Button(self, text="Cancel", command=self._on_cancel, bg='#555', fg='white', activebackground='#666', activeforeground='white', relief='flat', padx=15, pady=5, font=FONT_BUTTON)
        self.cancel_button.pack()

        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        x = (screen_w // 2) - (win_w // 2)
        y = (screen_h // 2) - (win_h // 2)
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.lift()
        self.focus_force()

    def _update_worker(self):
        try:
            if self.pid_to_wait_for:
                log.info(f"Waiting for main process (PID: {self.pid_to_wait_for}) to exit.")
                end_time = time.time() + 10  # 10-second timeout
                while time.time() < end_time:
                    if not is_pid_running(self.pid_to_wait_for):
                        log.info(f"Main process (PID: {self.pid_to_wait_for}) has exited.")
                        break
                    time.sleep(0.2)
                else:
                    log.warning(f"Timeout waiting for main process (PID: {self.pid_to_wait_for}) to exit.")
        except Exception as e:
            log.warning(f"Error while waiting for main process to exit: {e}")

        time.sleep(0.5) # Brief pause for safety

        self.after(0, lambda: self.status_label.config(text=f"Downloading update..."))
        self.temp_dir = tempfile.mkdtemp(prefix="codemerger-update-")
        log.info(f"Created temporary directory for update: {self.temp_dir}")

        try:
            filename = self.download_url.split('/')[-1]
            self.installer_path = os.path.join(self.temp_dir, filename)
            log.info(f"Downloading from {self.download_url} to {self.installer_path}")

            with requests.get(self.download_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded_size = 0

                with open(self.installer_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if self.cancelled:
                            log.info("Download cancelled by user.")
                            self._cleanup_temp_dir()
                            return
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            self.after(0, self._on_progress, progress, downloaded_size, total_size)

            if not self.cancelled:
                self.after(0, self._on_complete)

        except Exception as e:
            log.exception(f"Download failed from URL: {self.download_url}")
            self._cleanup_temp_dir()
            self.after(0, self.show_error, f"Download failed: {e}")

    def _on_progress(self, progress, downloaded, total):
        self.progress_bar['value'] = progress
        self.details_label.config(text=f"{downloaded / 1_048_576:.2f} MB / {total / 1_048_576:.2f} MB")

    def _on_complete(self):
        self.status_label.config(text="Download complete. Launching installer...")
        self.progress_bar['value'] = 100
        self.cancel_button.config(state='disabled')
        self.after(1000, self._launch_and_exit)

    def _launch_and_exit(self):
        try:
            log.info(f"Download complete. Launching installer: {self.installer_path}")
            subprocess.Popen(f'start "" "{self.installer_path}" /SILENT', shell=True)
            self._cleanup_and_destroy()
        except Exception as e:
            log.exception("Failed to launch installer.")
            self.show_error(f"Failed to launch installer: {e}")

    def show_error(self, message):
        messagebox.showerror("Update Failed", message)
        self._cleanup_and_destroy()

    def _cleanup_temp_dir(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            log.info(f"Cleaning up temporary directory: {self.temp_dir}")
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _cleanup_and_destroy(self):
        self.destroy()
        sys.exit(0)

    def _on_cancel(self):
        log.info("Update process cancelled by user via GUI.")
        self.cancelled = True
        self.status_label.config(text="Cancelling...")
        # The worker thread will see the flag and clean up. We just close the window.
        self._cleanup_and_destroy()

def main():
    if len(sys.argv) != 3:
        log.error(f"Updater GUI launched with incorrect arguments: {sys.argv}")
        return
    try:
        pid = int(sys.argv[1])
        url = sys.argv[2]
        log.info(f"Updater GUI started. PID to wait for: {pid}, URL: {url}")
        app = UpdateGUI(pid, url)
        app.mainloop()
    except Exception as e:
        log.exception("An error occurred during updater startup.")

if __name__ == '__main__':
    main()
```

--- End of file ---

--- File: `codemerger.spec` ---

```python
# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Tcl/Tk Correct Folder Mapping
def get_tcl_tk_datas():
    """
    Finds Tcl/Tk and maps the CONTENTS of the versioned folders
    directly into _tcl_data and _tk_data to satisfy PyInstaller hooks.
    """
    prefixes = [sys.prefix, getattr(sys, 'base_prefix', sys.prefix)]
    tcl_tk_datas = []

    for prefix in prefixes:
        tcl_root = os.path.join(prefix, 'tcl')
        if os.path.exists(tcl_root):
            tcl_dir = ""
            tk_dir = ""
            for entry in os.listdir(tcl_root):
                if entry.startswith('tcl8.'): tcl_dir = entry
                if entry.startswith('tk8.'): tk_dir = entry

            if tcl_dir and tk_dir:
                tcl_path = os.path.join(tcl_root, tcl_dir)
                tk_path = os.path.join(tcl_root, tk_dir)
                tcl_tk_datas.append((tcl_path, '_tcl_data'))
                tcl_tk_datas.append((tk_path, '_tk_data'))
                os.environ['TCL_LIBRARY'] = tcl_path
                os.environ['TK_LIBRARY'] = tk_path
                return tcl_tk_datas
    return []

# Load the Tcl/Tk data once
tcl_tk_data_bundle = get_tcl_tk_datas()

# Main Application Analysis
app_data_files = [
    ('assets', 'assets'),
    ('default_filetypes.json', '.'),
    ('version.txt', '.')
]
app_data_files.extend(tcl_tk_data_bundle)

app_icon_path = 'assets/icon.ico'
install_icon_path = 'assets/install.ico'

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=app_data_files,
    hiddenimports=[
        'PIL.ImageTk',
        'tiktoken_ext.openai_public',
        'detect_secrets.plugins',
        'rich',
        'markdown2'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='CodeMerger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=app_icon_path
)

# Updater GUI Launcher Analysis
updater_datas = [(install_icon_path, 'assets')]
updater_datas.extend(tcl_tk_data_bundle)

updater_a = Analysis(
    ['updater_gui.py'],
    pathex=[],
    binaries=[],
    datas=updater_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
updater_pyz = PYZ(updater_a.pure)

updater_exe = EXE(
    updater_pyz,
    updater_a.scripts,
    [],
    name='updater_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon=install_icon_path
)

# Collection
coll = COLLECT(
    exe,
    updater_exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CodeMerger'
)
```

--- End of file ---

--- File: `setup.iss` ---

```pascal
; Inno Setup script for CodeMerger
; This script is used by the GitHub Action to build the installer.

#define MyAppName "CodeMerger"
#define MyAppPublisher "M Nugteren/2Shine"
#define MyAppURL "https://github.com/DrSiemer/codemerger"
#define MyAppExeName "CodeMerger.exe"
#define MyAppSetupName "CodeMerger_Setup"

[Setup]
AppId={{C06CFB28-1B8E-4B3B-A107-5A5C9FC92CA1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename={#MyAppSetupName}
OutputDir=.\dist-installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=assets\install.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "checkforupdates"; Description: "Enable automatic update checks"; GroupDescription: "Updates:"
Name: "addcontextmenu"; Description: "Add 'Open in CodeMerger' to folder context menu"; GroupDescription: "Integration:"

[Files]
Source: "dist\CodeMerger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: dword; ValueName: "AutomaticUpdates"; ValueData: "{code:GetCheckForUpdatesValue}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}"; ValueType: string; ValueName: ""; ValueData: "Open in CodeMerger"; Flags: uninsdeletekey; Tasks: addcontextmenu
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName},0"; Tasks: addcontextmenu
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: addcontextmenu

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall shellexec

[Code]
const
  AppGuid = '{C06CFB28-1B8E-4B3B-A107-5A5C9FC92CA1}';

var
  g_DeleteConfigData: Boolean;
  g_CleanedAppVersion: String;

// --- Helper Function for Writing Values ---
function GetCheckForUpdatesValue(Param: String): String;
begin
  if WizardIsTaskSelected('checkforupdates') then
    Result := '1'
  else
    Result := '0';
end;

// --- Split string helper ---
function SplitString(const S, Delimiter: string): TArrayOfString;
var
  P: Integer;
  Temp: string;
begin
  SetArrayLength(Result, 0);
  Temp := S;
  repeat
    P := Pos(Delimiter, Temp);
    if P > 0 then
    begin
      SetArrayLength(Result, GetArrayLength(Result)+1);
      Result[GetArrayLength(Result)-1] := Copy(Temp, 1, P-1);
      Temp := Copy(Temp, P + Length(Delimiter), MaxInt);
    end
    else
    begin
      SetArrayLength(Result, GetArrayLength(Result)+1);
      Result[GetArrayLength(Result)-1] := Temp;
      Temp := '';
    end;
  until Temp = '';
end;

// --- Compare versions (returns -1,0,1) ---
function VersionCompare(V1, V2: String): Integer;
var
  Parts1, Parts2: TArrayOfString;
  I, N1, N2, Count1, Count2, Count: Integer;
begin
  Parts1 := SplitString(V1, '.');
  Parts2 := SplitString(V2, '.');
  Count1 := GetArrayLength(Parts1);
  Count2 := GetArrayLength(Parts2);
  if Count1 > Count2 then Count := Count1 else Count := Count2;

  for I := 0 to Count-1 do
  begin
    if I < Count1 then N1 := StrToIntDef(Parts1[I],0) else N1 := 0;
    if I < Count2 then N2 := StrToIntDef(Parts2[I],0) else N2 := 0;

    if N1 < N2 then begin Result := -1; exit; end
    else if N1 > N2 then begin Result := 1; exit; end;
  end;
  Result := 0;
end;

// --- Detect installed version ---
function GetInstalledVersion(): String;
var
  S: String;
begin
  Result := '';
  if RegQueryStringValue(HKLM,
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1',
    'DisplayVersion', S) then
  begin
    Result := S;
    exit;
  end;

  if RegQueryStringValue(HKLM,
    'Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1',
    'DisplayVersion', S) then
  begin
    Result := S;
  end;
end;

// --- Check if app is running ---
function IsAppRunning(const FileName: string): Boolean;
var
  FSWbemLocator: Variant;
  FWMIService: Variant;
  FWbemObjectSet: Variant;
begin
  Result := False;
  try
    FSWbemLocator := CreateOleObject('WbemScripting.SWbemLocator');
    FWMIService := FSWbemLocator.ConnectServer('.', 'root\cimv2', '', '');
    FWbemObjectSet := FWMIService.ExecQuery('SELECT Name FROM Win32_Process WHERE Name = "' + FileName + '"');
    Result := (FWbemObjectSet.Count > 0);
  except
    // Ignore WMI errors
  end;
end;

// --- Installer initialization ---
function InitializeSetup(): Boolean;
var
  InstalledVer, NewVer: String;
  Compare: Integer;
  Msg: String;
begin
  // Clean the installer version string and store it in a global variable
  g_CleanedAppVersion := ExpandConstant('{#MyAppVersion}');
  if (Length(g_CleanedAppVersion) > 0) and (g_CleanedAppVersion[1] = 'v') then
    Delete(g_CleanedAppVersion, 1, 1);
  NewVer := g_CleanedAppVersion;

  Log('Installer version (cleaned): ' + NewVer);
  InstalledVer := GetInstalledVersion();

  if InstalledVer <> '' then
  begin
    Log('Detected installed version from registry: ' + InstalledVer);
    // Also clean the installed version string for a consistent comparison
    if (Length(InstalledVer) > 0) and (InstalledVer[1] = 'v') then
      Delete(InstalledVer, 1, 1);
    Log('Cleaned installed version for comparison: ' + InstalledVer)
  end
  else
    Log('No installed version found.');

  if InstalledVer <> '' then
  begin
    Compare := VersionCompare(NewVer, InstalledVer);
    if Compare <= 0 then
    begin
      if Compare = 0 then
        Msg := 'You are about to install the same version (v' + NewVer + '). Proceed?'
      else // Compare < 0
        Msg := 'You are about to install an older version (v' + NewVer + ' < v' + InstalledVer + '). Proceed?';

      if MsgBox(Msg, mbConfirmation, MB_YESNO) = IDNO then
      begin
        Result := False;
        exit;
      end;
    end;
  end;

  if IsAppRunning('{#MyAppExeName}') then
  begin
    MsgBox('CodeMerger is currently running. Please close all instances before proceeding.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

// --- Wizard initialization ---
procedure InitializeWizard();
var
  Value: Cardinal;
  UpdatesEnabled: Boolean;
  ContextMenuEnabled: Boolean;
  I: Integer;
begin
  WizardForm.Caption := ExpandConstant('{#MyAppName} v' + g_CleanedAppVersion + ' Setup');
  WizardForm.BringToFront;
  if not RegQueryDwordValue(HKLM, 'Software\CodeMerger', 'AutomaticUpdates', Value) then
    UpdatesEnabled := True
  else
    UpdatesEnabled := (Value = 1);

  ContextMenuEnabled := RegKeyExists(HKLM, 'Software\Classes\Directory\shell\{#MyAppName}');

  for I := 0 to WizardForm.TasksList.Items.Count - 1 do
  begin
    if WizardForm.TasksList.Name[I] = 'checkforupdates' then
      WizardForm.TasksList.Checked[I] := UpdatesEnabled;
    if WizardForm.TasksList.Name[I] = 'addcontextmenu' then
      WizardForm.TasksList.Checked[I] := ContextMenuEnabled;
  end;
end;

// Set the DisplayVersion after install
procedure CurStepChanged(CurStep: TSetupStep);
var
  UninstallKey: string;
begin
  if CurStep = ssPostInstall then
  begin
    UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1';
    RegWriteStringValue(HKLM, UninstallKey, 'DisplayVersion', g_CleanedAppVersion);
  end;
end;

// --- Uninstall steps ---
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigDir: string;
  HKCUKey, HKLMKey, ShellKey: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    if MsgBox('Do you want to remove all your CodeMerger settings and project data?', mbConfirmation, MB_YESNO) = IDYES then
      g_DeleteConfigData := True
    else
      g_DeleteConfigData := False;
  end;

  if CurUninstallStep = usPostUninstall then
  begin
    // Delete per-user config data
    if g_DeleteConfigData then
    begin
      ConfigDir := ExpandConstant('{userappdata}\CodeMerger');
      if DirExists(ConfigDir) then
        DelTree(ConfigDir, True, True, True);

      HKCUKey := 'Software\CodeMerger';
      if RegKeyExists(HKCU, HKCUKey) then
        RegDeleteKeyIncludingSubkeys(HKCU, HKCUKey);
    end;

    // Delete system-wide HKLM keys safely
    HKLMKey := 'Software\CodeMerger';
    if RegKeyExists(HKLM, HKLMKey) then
      RegDeleteKeyIncludingSubkeys(HKLM, HKLMKey);

    ShellKey := 'Software\Classes\Directory\shell\CodeMerger';
    if RegKeyExists(HKLM, ShellKey) then
      RegDeleteKeyIncludingSubkeys(HKLM, ShellKey);

    // Delete uninstall information
    HKLMKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1';
    if RegKeyExists(HKLM, HKLMKey) then
      RegDeleteKeyIncludingSubkeys(HKLM, HKLMKey);

    HKLMKey := 'Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1';
    if RegKeyExists(HKLM, HKLMKey) then
      RegDeleteKeyIncludingSubkeys(HKLM, HKLMKey);
  end;
end;
```

--- End of file ---

--- File: `.github/workflows/release.yml` ---

```yaml
name: Create Release

# Run when a new tag is pushed (format v*.*.*)
on:
  push:
    tags:
      - 'v*'

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  validate-tag:
    name: Validate Release Tag
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository with full history
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Verify tag is on the master branch
        run: |
          TAG="${{ github.ref_name }}"
          echo "Validating tag: $TAG"
          TAG_COMMIT_HASH=$(git rev-parse "$TAG")
          if ! git branch -r --contains "$TAG_COMMIT_HASH" | grep -q "origin/master"; then
            echo "::error::Tag $TAG points to a commit that is not on the 'master' branch."
            echo ""
            echo "To fix this, delete the incorrect tag and create a new one on a commit in 'master'."
            echo ""
            echo "  git push --delete origin $TAG"
            echo "  git tag -d $TAG"
            echo ""
            exit 1
          fi
          echo "Tag validation successful: $TAG is on the master branch."

  # Build for Windows
  build-windows:
    name: Build for Windows
    needs: validate-tag
    runs-on: windows-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Build with PyInstaller
        run: pyinstaller codemerger.spec
      - name: Compile Inno Setup installer
        uses: Minionguyjpro/Inno-Setup-Action@v1.2.7
        with:
          path: setup.iss
          options: /dMyAppVersion=${{ github.ref_name }}
      - name: Upload Windows artifacts
        uses: actions/upload-artifact@v4
        with:
          name: CodeMerger-windows-build
          path: |
            dist/CodeMerger.exe
            dist-installer/CodeMerger_Setup.exe

  # Create the GitHub Release
  create-release:
    name: Create a new release
    needs: [build-windows]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Download all build artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          name: CodeMerger ${{ github.ref_name }}
          draft: true
          prerelease: false
          files: |
            artifacts/CodeMerger-windows-build/dist-installer/CodeMerger_Setup.exe
```

--- End of file ---

--- File: `src/ui/widgets/diff_viewer.py` ---

```python
import tkinter as tk
from tkinter import ttk
import difflib
from ... import constants as c

class DiffViewer(tk.Frame):
    """
    A widget that displays a color-coded unified diff between two text strings.
    It grows vertically to fit its content without internal scrollbars.
    """
    def __init__(self, parent, old_text, new_text, *args, **kwargs):
        # We ignore height passed in kwargs to allow dynamic sizing
        kwargs.pop('height', None)
        super().__init__(parent, bg=c.TEXT_INPUT_BG, bd=1, relief='sunken', **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # We use wrap='word' because scrollbars are removed per request
        self.text_widget = tk.Text(
            self, wrap='word', bd=0, highlightthickness=0,
            bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR,
            font=("Consolas", 10), padx=10, pady=10,
            state='disabled'
        )
        self.text_widget.grid(row=0, column=0, sticky='nsew')

        # Tags for highlighting with optimized legibility (foreground and background)
        self.text_widget.tag_configure("add", background=c.DIFF_ADD_BG, foreground=c.DIFF_ADD_FG)
        self.text_widget.tag_configure("remove", background=c.DIFF_REMOVE_BG, foreground=c.DIFF_REMOVE_FG)
        self.text_widget.tag_configure("header", foreground=c.DIFF_HEADER_FG, font=("Consolas", 10, "bold"))

        # Binding to update height when window/container resizes (influences wrap points)
        self.text_widget.bind("<Configure>", self._adjust_height_to_content)

        self._generate_diff(old_text, new_text)

    def _adjust_height_to_content(self, event=None):
        """Calculates and sets the widget height based on visual lines to prevent internal scrolling."""
        if not self.winfo_exists():
            return
        try:
            # We use "displaylines" to account for word wrapping.
            # "end-1c" excludes the trailing newline Tkinter automatically appends.
            result = self.text_widget.count("1.0", "end-1c", "displaylines")
            if result:
                actual_lines = result[0]
                # We add +1 as a buffer to account for internal padding and prevent
                # the "one line short" scrolling artifact.
                self.text_widget.config(height=max(1, actual_lines + 1))
        except tk.TclError:
            pass

    def _generate_diff(self, old_text, new_text):
        """Calculates the diff and populates the text widget with tags."""
        # Plain view for new files (no old content)
        if not old_text:
            self.text_widget.config(state='normal')
            self.text_widget.delete("1.0", tk.END)
            if new_text:
                self.text_widget.insert(tk.END, new_text)
            else:
                self.text_widget.insert(tk.END, "(File is empty)")

            self.text_widget.config(state='disabled')
            self.after_idle(self._adjust_height_to_content)
            return

        old_lines = old_text.splitlines() if old_text else []
        new_lines = new_text.splitlines() if new_text else []

        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))

        self.text_widget.config(state='normal')
        self.text_widget.delete("1.0", tk.END)

        for line in diff:
            tag = None
            if line.startswith('+') and not line.startswith('+++'):
                tag = "add"
            elif line.startswith('-') and not line.startswith('---'):
                tag = "remove"
            elif line.startswith('@@') or line.startswith('---') or line.startswith('+++'):
                tag = "header"

            if tag:
                self.text_widget.insert(tk.END, line + "\n", tag)
            else:
                self.text_widget.insert(tk.END, line + "\n")

        if not diff:
            self.text_widget.insert(tk.END, "(No changes detected in file content)")

        self.text_widget.config(state='disabled')

        # Adjust height to fit all lines perfectly after insertion
        self.after_idle(self._adjust_height_to_content)
```

--- End of file ---

--- File: `src/ui/feedback/changes_controller.py` ---

```python
import os
import subprocess
import sys
import tkinter as tk
from tkinter import Frame, Label, Button, messagebox
from ... import constants as c
from ...core import change_applier
from ..widgets.rounded_button import RoundedButton
from ..widgets.markdown_renderer import MarkdownRenderer
from ..widgets.scrollable_frame import ScrollableFrame
from ..widgets.diff_viewer import DiffViewer
from ..tooltip import ToolTip

class FeedbackChangesController:
    """
    Manages the interactive file list in the 'Changes' tab.
    Handles row building, diff viewing, and state tracking for individual files.
    """
    def __init__(self, window):
        self.window = window
        self._diff_viewers = {}
        self._initialize_file_states()

    def register_info(self, info_mgr):
        """Binds info documentation to the changes list controls."""
        if hasattr(self.window, 'toggle_commentary_btn'):
            info_mgr.register(self.window.toggle_commentary_btn, "review_commentary")

    def _initialize_file_states(self):
        """Determines initial state (pending/skipped) for all files in the plan."""
        window = self.window
        if window.file_states: return # Already initialized for this plan

        updates = window.plan.get('updates', {})
        for path, content in updates.items():
            old_text = change_applier.get_current_file_content(window.base_dir, path)
            if old_text is not None:
                sanitized_new = change_applier._sanitize_content(os.path.join(window.base_dir, path), content)
                if old_text == sanitized_new:
                    window.file_states[path] = "skipped"
                    continue
            window.file_states[path] = "pending"

        for path in window.plan.get('creations', {}):
            window.file_states[path] = "pending"

        for path in window.plan.get('deletions_proposed', []):
            if not os.path.isfile(os.path.join(window.base_dir, path)):
                window.file_states[path] = "skipped"
                continue
            window.file_states[path] = "pending"

    def add_interactive_changes_tab(self):
        """Constructs the Change management tab."""
        window = self.window
        frame = Frame(window.notebook, bg=c.DARK_BG)
        window.notebook.add(frame, text="Changes", image=window._blue_accent, compound="left")

        header = Frame(frame, bg=c.DARK_BG, padx=20, pady=10)
        header.pack(fill='x')
        Label(header, text="Proposed Actions", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).pack(side='left')

        desc = window.plan.get('changes', "").strip()
        if desc:
            window.toggle_commentary_btn = RoundedButton(header, text="Show AI Commentary", command=self.toggle_commentary, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, height=24, radius=4, cursor="hand2")
            window.toggle_commentary_btn.pack(side='right')
            window.commentary_renderer = MarkdownRenderer(frame, base_font_size=10, auto_height=True)
            window.commentary_renderer.set_markdown(desc)

        window.file_list_scroll = ScrollableFrame(frame, bg=c.DARK_BG)
        window.file_list_scroll.pack(fill='both', expand=True, pady=(0, 10))
        self.refresh_file_list_ui()

    def toggle_commentary(self):
        window = self.window
        if not hasattr(window, 'commentary_renderer'): return
        if window.commentary_renderer.winfo_ismapped():
            window.commentary_renderer.pack_forget()
            window.toggle_commentary_btn.config(text="Show AI Commentary", bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)
        else:
            window.commentary_renderer.pack(fill='x', before=window.file_list_scroll, padx=20, pady=(0, 10))
            window.toggle_commentary_btn.config(text="Hide AI Commentary", bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)

    def refresh_file_list_ui(self):
        """Wipes and rebuilds the interactive file rows."""
        window = self.window
        container = window.file_list_scroll.scrollable_frame
        for w in container.winfo_children(): w.destroy()
        self._diff_viewers.clear()

        updates = window.plan.get('updates', {})
        creations = window.plan.get('creations', {})
        deletions = window.plan.get('deletions_proposed', [])

        if updates:
            self._create_group_header(container, "Modify Content", c.BTN_BLUE)
            for p in sorted(updates.keys()): self._create_file_row(container, p, "modify")
        if creations:
            self._create_group_header(container, "Create New File", c.BTN_GREEN)
            for p in sorted(creations.keys()): self._create_file_row(container, p, "create")
        if deletions:
            self._create_group_header(container, "Delete Obsolete File", c.WARN)
            for p in sorted(deletions): self._create_file_row(container, p, "delete")

        self.update_mass_apply_visibility()

    def _create_group_header(self, container, text, color):
        f = Frame(container, bg=c.DARK_BG, padx=20)
        f.pack(fill='x', pady=(15, 5))
        Label(f, text=text.upper(), font=(c.FONT_FAMILY_PRIMARY, 9, 'bold'), bg=c.DARK_BG, fg=color).pack(side='left')
        Frame(f, bg=color, height=1).pack(side='left', fill='x', expand=True, padx=(10, 0))

    def _create_file_row(self, parent, path, action_type):
        """Renders an individual file row with action buttons."""
        window = self.window
        row_container = Frame(parent, bg=c.DARK_BG)
        row_container.pack(fill='x', pady=2, padx=(20, 20))

        row_header = Frame(row_container, bg=c.DARK_BG)
        row_header.pack(fill='x')

        state = window.file_states.get(path, "pending")
        is_handled = state in ["applied", "deleted", "rejected"]
        is_skipped = state == "skipped"

        font_config = c.FONT_NORMAL
        if is_handled:
            font = (font_config[0], font_config[1], 'overstrike')
            fg = c.TEXT_SUBTLE_COLOR
        elif is_skipped:
            font = font_config
            fg = c.TEXT_SUBTLE_COLOR
        else:
            font = font_config
            fg = c.TEXT_COLOR

        lbl_name = Label(row_header, text=path, font=font, fg=fg, bg=c.DARK_BG, anchor='w', cursor='hand2')
        lbl_name.pack(side='left', fill='x', expand=True)

        lbl_name.bind("<Button-1>", lambda e, p=path: self.open_file_in_editor(p))
        lbl_name.bind("<Enter>", lambda e, l=lbl_name, f=font_config: self._on_link_hover(l, f, True))
        lbl_name.bind("<Leave>", lambda e, l=lbl_name, f=font: self._on_link_hover(l, f, False))

        btn_frame = Frame(row_header, bg=c.DARK_BG)
        btn_frame.pack(side='right')

        diff_container = Frame(row_container, bg=c.DARK_BG)

        btn_opts = {'font': c.FONT_SMALL_BUTTON, 'relief': 'flat', 'borderwidth': 0, 'height': 1, 'cursor': 'hand2', 'padx': 10}

        if is_skipped:
            msg = "Already deleted" if action_type == "delete" else "No changes"
            Label(btn_frame, text=msg, font=c.FONT_SMALL_BUTTON, fg=c.TEXT_SUBTLE_COLOR, bg=c.DARK_BG, padx=10).pack()
        elif is_handled:
            is_new_creation = path in window.plan.get('creations', {})
            show_undo = False
            if state == "rejected": show_undo = True
            elif is_new_creation: show_undo = True
            elif path in window.undo_buffer and window.undo_buffer[path] is not None: show_undo = True

            if show_undo:
                u_btn = Button(btn_frame, text="Undo", command=lambda: self.undo_file_action(path, action_type), bg="#666666", fg="#FFFFFF", **btn_opts)
                u_btn.pack()
                if window.info_mgr: window.info_mgr.register(u_btn, "review_file_action")
        else:
            btn_text = "View" if action_type in ["create", "delete"] else "Diff"
            d_btn = Button(btn_frame, text=btn_text, command=lambda: self.toggle_diff(path, diff_container, action_type), bg=c.BTN_BLUE, fg="#FFFFFF", **btn_opts)
            d_btn.pack(side='left', padx=(0, 2))

            tooltip_msg = "View file content" if action_type in ["create", "delete"] else "Inspect text changes"
            ToolTip(d_btn, tooltip_msg)
            if window.info_mgr: window.info_mgr.register(d_btn, "review_diff")

            if action_type == "delete":
                a_btn = Button(btn_frame, text="Accept Delete", command=lambda: self.apply_file_action(path, "delete"), bg=c.WARN, fg="#FFFFFF", **btn_opts)
                a_btn.pack(side='left', padx=(0, 2))
                k_btn = Button(btn_frame, text="Keep", command=lambda: self.discard_file_item(path), bg=c.STATUS_BG, fg=c.TEXT_COLOR, **btn_opts)
                k_btn.pack(side='left')
                if window.info_mgr:
                    window.info_mgr.register(a_btn, "review_file_action")
                    window.info_mgr.register(k_btn, "review_file_action")
            else:
                a_btn = Button(btn_frame, text="Accept", command=lambda: self.apply_file_action(path, action_type), bg=c.BTN_GREEN, fg="#FFFFFF", **btn_opts)
                a_btn.pack(side='left', padx=(0, 2))
                r_btn = Button(btn_frame, text="Discard", command=lambda: self.discard_file_item(path), bg=c.STATUS_BG, fg=c.TEXT_COLOR, **btn_opts)
                r_btn.pack(side='left')
                if window.info_mgr:
                    window.info_mgr.register(a_btn, "review_file_action")
                    window.info_mgr.register(r_btn, "review_file_action")

    def _on_link_hover(self, label, base_font, is_enter):
        if is_enter:
            st = base_font[2] + ' underline' if len(base_font) > 2 else 'underline'
            label.config(font=(base_font[0], base_font[1], st), fg=c.BTN_BLUE_TEXT)
        else:
            state = self.window.file_states.get(label.cget('text'))
            dim = state in ["applied", "deleted", "rejected", "skipped"]
            label.config(font=base_font, fg=c.TEXT_SUBTLE_COLOR if dim else c.TEXT_COLOR)

    def open_file_in_editor(self, rel_path):
        window = self.window
        full_path = os.path.join(window.base_dir, rel_path)
        if not os.path.isfile(full_path): return
        editor = window.app_state.config.get('default_editor', '')
        try:
            if editor and os.path.isfile(editor): subprocess.Popen([editor, full_path])
            else:
                if sys.platform == "win32": os.startfile(full_path)
                elif sys.platform == "darwin": subprocess.call(['open', full_path])
                else: subprocess.call(['xdg-open', full_path])
        except Exception as e: messagebox.showerror("Error", f"Could not open file: {e}", parent=window)

    def toggle_diff(self, path, container, action_type):
        if container.winfo_ismapped():
            container.pack_forget()
            return
        if path not in self._diff_viewers:
            old, new = "", ""
            if action_type == "create":
                new = self.window.plan['creations'].get(path, "")
            elif action_type == "delete":
                # For deletions, show current content as a plain view (like a new file)
                new = change_applier.get_current_file_content(self.window.base_dir, path) or ""
            else:
                old = change_applier.get_current_file_content(self.window.base_dir, path) or ""
                new = self.window.plan['updates'].get(path, "")

            v = DiffViewer(container, old, new)
            v.pack(fill='x', pady=(5, 10))
            self._diff_viewers[path] = v
        container.pack(fill='x')
        self.window.file_list_scroll._on_frame_configure()

    def apply_file_action(self, path, action_type):
        window = self.window
        original = None
        if action_type == "delete":
            if not os.path.isfile(os.path.join(window.base_dir, path)):
                window.file_states[path] = "deleted"; window.undo_buffer[path] = None
                self.refresh_file_list_ui(); return
        if action_type != "create":
            original = change_applier.get_current_file_content(window.base_dir, path)
            if original is None: return
        window.undo_buffer[path] = original
        success = False
        if action_type == "delete":
            success, _ = change_applier.delete_single_file(window.base_dir, path)
            if success: window.file_states[path] = "deleted"
        else:
            content = window.plan['updates'].get(path) or window.plan['creations'].get(path)
            success, _ = change_applier.apply_single_file(window.base_dir, path, content)
            if success:
                window.file_states[path] = "applied"
                # Automatic Addition to Merge List on individual Accept
                if hasattr(window.app, 'action_handlers'):
                    window.app.action_handlers.ensure_file_is_merged(path)

        if success:
            window.app.button_manager.update_button_states()
            self.refresh_file_list_ui()
            window.app.file_monitor.perform_new_file_check(schedule_next=False)

    def undo_file_action(self, path, action_type):
        window = self.window
        is_new = path in window.plan.get('creations', {})
        original = window.undo_buffer.get(path)
        success = False
        if window.file_states.get(path) == "rejected": success = True
        elif is_new: success, _ = change_applier.delete_single_file(window.base_dir, path)
        elif original is not None: success, _ = change_applier.apply_single_file(window.base_dir, path, original)
        if success:
            window.file_states[path] = "pending"
            window.app.button_manager.update_button_states()
            self.refresh_file_list_ui()
            window.app.file_monitor.perform_new_file_check(schedule_next=False)

    def discard_file_item(self, path):
        self.window.file_states[path] = "rejected"
        self.window.app.button_manager.update_button_states()
        self.refresh_file_list_ui()

    def update_mass_apply_visibility(self):
        window = self.window
        if not hasattr(window, 'apply_btn'): return
        has_pending = any(s == "pending" for s in window.file_states.values())
        if has_pending:
            manual = any(s in ["applied", "deleted", "rejected"] for s in window.file_states.values())
            window.apply_btn.config(text="Apply All Remaining" if manual else "Apply All")
            if not window.apply_btn.winfo_ismapped():
                window.cancel_btn.pack_forget()
                window.apply_btn.pack(side="right")
                window.cancel_btn.pack(side="right", padx=(0, 10))
        else: window.apply_btn.pack_forget()
```

--- End of file ---

--- File: `src/ui/feedback/feedback_dialog.py` ---

```python
import tkinter as tk
from tkinter import Frame
from ...core.paths import ICON_PATH
from .ui_setup import setup_feedback_ui
from .logic_controller import FeedbackLogicController
from .changes_controller import FeedbackChangesController

class FeedbackDialog(tk.Toplevel):
    """
    Orchestrator for the AI Response Review window.
    Coordinates between UI construction, state management, and file system logic.
    """
    def __init__(self, parent, plan, on_apply=None, on_refuse=None, force_verification=False):
        super().__init__(parent)
        self.parent = parent
        self.plan = plan
        self.on_apply_executor = on_apply
        self.on_refuse = on_refuse
        self.force_verification = force_verification

        # Defensive initialization to prevent AttributeErrors during widget population
        self.info_mgr = None

        # Identify root App instance
        self.app = parent
        while self.app and not hasattr(self.app, 'action_handlers'):
            self.app = getattr(self.app, 'parent', getattr(self.app, 'master', None))

        project = self.app.project_manager.get_current_project()
        self.base_dir = project.base_dir if project else ""
        self.app_state = getattr(parent, 'app_state', getattr(parent.master, 'app_state', None))

        # Shared Logic State
        if 'file_states' not in self.plan:
            self.plan['file_states'] = {}
            self.plan['undo_buffer'] = {}

        self.file_states = self.plan['file_states']
        self.undo_buffer = self.plan['undo_buffer']

        # Window Initialization
        self.withdraw()
        self.title("AI Response Review")
        self.iconbitmap(ICON_PATH)

        # Controllers
        self.logic = FeedbackLogicController(self)
        self.changes = FeedbackChangesController(self)

        # Build UI
        setup_feedback_ui(self)

        # Register Logic Components with Info Mode (if available)
        if self.info_mgr:
            self.logic.register_info(self.info_mgr)
            self.changes.register_info(self.info_mgr)
            self.info_toggle_btn.lift()

        self.logic.finalize_boot()

    def destroy(self):
        """Cleans up instance references and saves state."""
        if hasattr(self.app, 'active_feedback_dialog') and self.app.active_feedback_dialog is self:
            self.app.active_feedback_dialog = None
        self.logic.save_window_state()
        super().destroy()
```

--- End of file ---

--- File: `src/ui/feedback/logic_controller.py` ---

```python
import tkinter as tk
import pyperclip
import time
from tkinter import messagebox
from ... import constants as c
from ..window_utils import position_window, save_window_geometry
from ...core.utils import save_config
from ...core import change_applier

class FeedbackLogicController:
    """
    Handles window-level actions, settings, and high-level logic for the Feedback Dialog.
    """
    def __init__(self, window):
        self.window = window
        self._lazy_timer = None
        self._is_lazy_hiding = False
        self._last_size = (0, 0)

    def finalize_boot(self):
        """Standardizes geometry and focus after construction."""
        window = self.window

        # Position and sizing
        initial_w, initial_h = 900, 750
        if window.app_state and window.app_state.info_mode_active:
            initial_h += c.INFO_PANEL_HEIGHT
        window.geometry(f"{initial_w}x{initial_h}")
        window.minsize(600, 500)
        window.resizable(True, True)
        position_window(window)

        # Bindings
        window.bind("<Escape>", lambda e: self.handle_escape())
        window.protocol("WM_DELETE_WINDOW", self.on_close_request if window.on_apply_executor else window.destroy)
        window.bind("<Configure>", self.on_configure)

        # Tab Selection
        if window.force_verification and 'verification' in window.tab_indices:
            window.notebook.select(window.tab_indices['verification'])
        elif window.notebook.tabs():
            window.notebook.select(0)

        self.window.deiconify()

    def register_info(self, info_mgr):
        """Binds info documentation to top-level window controls."""
        window = self.window
        info_mgr.register(window.notebook, "review_tabs")
        info_mgr.register(window.auto_show_chk, "review_auto_show")
        info_mgr.register(window.info_toggle_btn, "info_toggle")

        if window.on_apply_executor:
            info_mgr.register(window.apply_btn, "review_apply")
            info_mgr.register(window.cancel_btn, "review_cancel")
        else:
            info_mgr.register(window.ok_button, "review_close")

        if hasattr(window, 'admonish_btn'):
            info_mgr.register(window.admonish_btn, "review_admonish")

        for widget, key in window.tab_widgets_for_info:
            info_mgr.register(widget, key)

    def on_configure(self, event):
        """Implements Resize Guard (Lazy Layout) to maintain UI responsiveness."""
        if event.widget != self.window: return
        new_size = (event.width, event.height)
        if self._last_size == new_size: return
        self._last_size = new_size

        if not self._is_lazy_hiding:
            self._start_lazy_layout()

        if self._lazy_timer:
            self.window.after_cancel(self._lazy_timer)
        self._lazy_timer = self.window.after(c.LAZY_LAYOUT_DELAY_MS, self._end_lazy_layout)

    def _start_lazy_layout(self):
        self._is_lazy_hiding = True
        self.window.notebook.grid_remove()

    def _end_lazy_layout(self):
        self.window.notebook.grid()
        self._is_lazy_hiding = False
        self._lazy_timer = None
        self.window.update_idletasks()

    def handle_apply_all(self):
        """Executes the batch apply logic for all pending changes."""
        window = self.window
        plan = window.plan

        pending_updates = {p: c for p, c in plan.get('updates', {}).items() if window.file_states.get(p) == "pending"}
        pending_creations = {p: c for p, c in plan.get('creations', {}).items() if window.file_states.get(p) == "pending"}
        pending_deletions = [p for p in plan.get('deletions_proposed', []) if window.file_states.get(p) == "pending"]

        if not (pending_updates or pending_creations or pending_deletions):
            return

        current_tab_text = window.notebook.tab(window.notebook.select(), "text")
        is_changes_tab = (current_tab_text == "Changes")

        # Create individual backups
        for path in list(pending_updates.keys()) + pending_deletions:
            if path not in window.undo_buffer:
                 window.undo_buffer[path] = change_applier.get_current_file_content(window.base_dir, path)

        if window.on_apply_executor(pending_updates, pending_creations, pending_deletions, is_changes_tab_active=is_changes_tab) is not False:
            for p in pending_updates: window.file_states[p] = "applied"
            for p in pending_creations: window.file_states[p] = "applied"
            for p in pending_deletions: window.file_states[p] = "deleted"

            window.changes.refresh_file_list_ui()

            if 'verification' in window.tab_indices:
                window.changes.update_mass_apply_visibility()
                window.cancel_btn.config(text="Close")
                window.notebook.select(window.tab_indices['verification'])
            else:
                window.destroy()

    def handle_cancel(self):
        """Explicitly refuses the proposed updates and closes the window."""
        if self.window.on_refuse:
            self.window.on_refuse()
        self.window.destroy()

    def handle_escape(self):
        if not self.window.on_apply_executor:
            self.window.destroy()
        else:
            self.on_close_request()

    def on_close_request(self):
        """Prompts user before discarding pending updates via manual close."""
        has_pending = any(s == "pending" for s in self.window.file_states.values())
        if has_pending:
            msg = "You are currently reviewing a proposed update. Closing this window will discard the changes.\n\nAre you sure?"
            if not messagebox.askyesno("Discard Update?", msg, parent=self.window):
                return
        self.handle_cancel()

    def copy_admonishment(self):
        """
        Copies formatting correction prompt to clipboard.
        Uses advanced fragmentation to prevent self-detection during code merging.
        """
        LT = "<"
        RT = ">"
        PRE = "--- "

        # Fragmented Tag names to ensure source file never contains a valid literal tag
        IN_T = "IN" + "TRO"
        ANS_W = "ANS" + "WERS" + " TO DIR" + "ECT USER QUE" + "STIONS"
        CHA_N = "CHA" + "NGES"
        VER_I = "VER" + "IFI" + "CATION"

        msg = (
            "Please follow the output format strictly as described in your instructions. "
            "Your previous response did not fully comply with the required formatting standards. "
            "Specifically, please ensure that:\n"
            "- ALL commentary and explanations are placed inside the mandatory XML tags ("
            f"{LT}{IN_T}{RT}, {LT}{ANS_W}{RT}, {LT}{CHA_N}{RT}, {LT}{VER_I}{RT}).\n"
            "- No text or commentary exists outside of these tags.\n"
            f"- File markers are present and correctly formatted ({PRE}File: `path` --- and {PRE}End of file ---).\n"
            "- You provide the full, complete code for modified files without using placeholders like '// ... rest of code'.\n"
            "Please re-output the response correctly."
        )
        pyperclip.copy(msg)
        self.window.admonish_btn.config(text="Copied!", bg=c.BTN_GREEN)
        self.window.after(2000, lambda: self.window.admonish_btn.config(text="Copy Correction Prompt", bg=c.ATTENTION) if self.window.admonish_btn.winfo_exists() else None)

    def adjust_font_size(self, delta):
        if not self.window.renderers: return
        new_size = max(8, min(self.window.renderers[0].base_font_size + delta, 40))
        for r in self.window.renderers: r.set_font_size(new_size)

    def save_feedback_setting(self):
        if not self.window.app_state: return
        self.window.app_state.config['show_feedback_on_paste'] = self.window.show_var.get()
        save_config(self.window.app_state.config)
        self.window.app.button_manager.refresh_paste_tooltips()

    def save_window_state(self):
        save_window_geometry(self.window)
```

--- End of file ---

--- File: `src/ui/feedback/ui_setup.py` ---

```python
import tkinter as tk
from tkinter import Frame, Label, ttk, BooleanVar
from PIL import Image, ImageDraw, ImageTk
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..widgets.markdown_renderer import MarkdownRenderer
from ..widgets.scrollable_frame import ScrollableFrame
from ..style_manager import apply_dark_theme
from ..tooltip import ToolTip
from ..info_manager import attach_info_mode
from ..assets import assets

def setup_feedback_ui(window):
    """
    Initializes the visual layout and tabbed navigation for the Feedback Dialog.
    """
    window.configure(bg=c.DARK_BG)
    apply_dark_theme(window)

    # Grid Root Configuration
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # Topmost Decoupling
    is_parent_topmost = False
    try:
        is_parent_topmost = window.parent.attributes("-topmost")
    except Exception:
        pass
    if not is_parent_topmost:
        window.transient(window.parent)

    # Accent Generation
    window._gray_accent = _create_vertical_accent(c.TEXT_SUBTLE_COLOR)
    window._cyan_accent = _create_vertical_accent("#00BCD4")
    window._blue_accent = _create_vertical_accent(c.BTN_BLUE)
    window._red_accent = _create_vertical_accent(c.WARN)
    window._green_accent = _create_vertical_accent(c.BTN_GREEN)
    window._yellow_accent = _create_vertical_accent(c.ATTENTION)

    # Main Containers
    window.main_content_frame = Frame(window, bg=c.DARK_BG, pady=20)
    window.main_content_frame.grid(row=0, column=0, sticky="nsew")
    window.main_content_frame.grid_rowconfigure(2, weight=1)
    window.main_content_frame.grid_columnconfigure(0, weight=1)

    # Header
    header_row = Frame(window.main_content_frame, bg=c.DARK_BG, padx=20)
    header_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    header_row.columnconfigure(0, weight=1)

    title_text = "Review Proposed Update" if window.on_apply_executor else "Review Last Update"
    Label(header_row, text=title_text, font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w")

    # Dynamic Alert Section
    window.alert_frame = Frame(window.main_content_frame, bg=c.DARK_BG, padx=20)

    # Notebook
    window.notebook = ttk.Notebook(window.main_content_frame)
    window.notebook.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
    window.renderers = []
    window.tab_widgets_for_info = []
    window.tab_indices = {}

    # Footer
    window.bottom_frame = Frame(window.main_content_frame, bg=c.DARK_BG, padx=20)
    window.bottom_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))

    show_val = window.app_state.config.get('show_feedback_on_paste', True) if window.app_state else True
    window.show_var = BooleanVar(value=show_val)
    window.auto_show_chk = ttk.Checkbutton(window.bottom_frame, text="Show this window automatically on paste", variable=window.show_var, style='Dark.TCheckbutton', command=window.logic.save_feedback_setting)
    window.auto_show_chk.pack(side="left")

    if window.on_apply_executor:
        window.apply_btn = RoundedButton(window.bottom_frame, text="Apply All", command=window.logic.handle_apply_all, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BOLD, width=200, height=30, cursor="hand2")
        window.cancel_btn = RoundedButton(window.bottom_frame, text="Close", command=window.logic.handle_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
        window.apply_btn.pack(side="right")
        window.cancel_btn.pack(side="right", padx=(0, 10))
    else:
        window.ok_button = RoundedButton(window.bottom_frame, text="OK", command=window.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
        window.ok_button.pack(side="right")

    # Info Toggle Integration
    # Must be initialized BEFORE populating tabs so that interactive rows can register help tips
    if window.app_state:
        window.info_toggle_btn = Label(window, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")
        window.info_mgr = attach_info_mode(window, window.app_state, manager_type='grid', grid_row=1, toggle_btn=window.info_toggle_btn)
    else:
        window.info_mgr = None

    # Build Tabs (now safe to register widgets with info_mgr)
    _populate_tabs(window)

def _create_vertical_accent(hex_color):
    """Generates a small vertical colored bar for tab identification."""
    size = (14, 22)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 1, 3, 20], radius=1, fill=hex_color)
    return ImageTk.PhotoImage(img)

def _populate_tabs(window):
    """Iterates through parsed segments and builds the notebook tabs."""
    plan = window.plan
    ordered_segments = plan.get('ordered_segments', [])
    has_unformatted = any(s['type'] == 'orphan' for s in ordered_segments)
    has_any_tags = plan.get('has_any_tags', False)
    has_file_blocks = bool(plan.get('updates') or plan.get('creations') or plan.get('deletions_proposed'))

    # Admonishment setup for unformatted outputs
    if has_unformatted and not has_any_tags:
        window.alert_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        Label(window.alert_frame, text="This text was not properly wrapped in the requested XML tags", fg=c.WARN, bg=c.DARK_BG, font=c.FONT_NORMAL).pack(side='left')
        window.admonish_btn = RoundedButton(window.alert_frame, text="Copy Correction Prompt", command=window.logic.copy_admonishment, bg=c.ATTENTION, fg="#FFFFFF", font=c.FONT_SMALL_BUTTON, width=200, height=26, cursor="hand2")
        window.admonish_btn.pack(side='right')
        ToolTip(window.admonish_btn, "Copy a prompt to tell the AI to follow the output format")

    changes_tab_added = False
    current_idx = 0

    for seg in ordered_segments:
        stype = seg['type']
        content = seg.get('content', "").strip()
        if not content and stype != 'file_placeholder': continue

        if stype == 'tag':
            tag_name = seg['tag']
            if tag_name == "DELETED FILES": continue

            if tag_name == "VERIFICATION" and not changes_tab_added and has_file_blocks:
                window.changes.add_interactive_changes_tab()
                changes_tab_added = True
                current_idx += 1

            title = tag_name.replace("ANSWERS TO DIRECT USER QUESTIONS", "Answers").title()
            icon = window._gray_accent
            info_key = "review_tab_placeholder"
            if "INTRO" in tag_name: info_key = "review_tab_intro"
            elif "CHANGES" in tag_name:
                icon = window._blue_accent; info_key = "review_tab_changes"
                changes_tab_added = True
            elif "ANSWERS" in tag_name: icon = window._cyan_accent; info_key = "review_tab_answers"
            elif "VERIFICATION" in tag_name: icon = window._green_accent; info_key = "review_tab_verification"
            elif "DELETED" in tag_name: icon = window._red_accent; info_key = "review_tab_delete"

            _add_standard_tab(window, title, content, icon=icon, info_key=info_key)
            if "VERIFICATION" in tag_name: window.tab_indices['verification'] = current_idx
            current_idx += 1
        elif stype == 'orphan':
            _add_unformatted_tab(window, "Unformatted output", content)
            current_idx += 1

    if not changes_tab_added and has_file_blocks:
        window.changes.add_interactive_changes_tab()

    if current_idx == 0:
        _add_standard_tab(window, "Response Summary", "The AI response contained only code blocks.", icon=window._gray_accent, info_key="review_tab_placeholder")

def _add_standard_tab(window, title, markdown_text, icon=None, info_key=None):
    if title == "Changes":
        window.changes.add_interactive_changes_tab()
        return

    frame = Frame(window.notebook, bg=c.DARK_BG)
    if icon: window.notebook.add(frame, text=title, image=icon, compound="left")
    else: window.notebook.add(frame, text=title)

    # Wrap the renderer in a ScrollableFrame to allow the entire content to be high enough
    scroll = ScrollableFrame(frame, bg=c.DARK_BG)
    scroll.pack(fill="both", expand=True)

    renderer = MarkdownRenderer(scroll.scrollable_frame, base_font_size=11, on_zoom=window.logic.adjust_font_size, auto_height=True)
    renderer.pack(fill="x", expand=True)
    renderer.set_markdown(markdown_text.strip())
    window.renderers.append(renderer)
    if info_key: window.tab_widgets_for_info.append((renderer, info_key))

def _add_unformatted_tab(window, title, raw_text):
    frame = Frame(window.notebook, bg=c.DARK_BG)
    window.notebook.add(frame, text=title, image=window._yellow_accent, compound="left")

    scroll = ScrollableFrame(frame, bg=c.DARK_BG)
    scroll.pack(fill="both", expand=True)

    renderer = MarkdownRenderer(scroll.scrollable_frame, base_font_size=11, on_zoom=window.logic.adjust_font_size, auto_height=True)
    renderer.pack(fill="x", expand=True)
    renderer.set_markdown(raw_text.strip())
    window.renderers.append(renderer)
    window.tab_widgets_for_info.append((renderer, "review_tab_unformatted"))
```

--- End of file ---