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

### Core Logic (`src/core`)

- `src/core/paths.py`: Distinguishes between `get_bundle_dir()` for read-only assets bundled with PyInstaller and `get_persistent_data_dir()` for user configuration (`%APPDATA%` on Windows), ensuring portability and correct data storage.
- `src/core/registry.py`: Settings are read with a fallback system: it first checks for a user-specific setting in `HKEY_CURRENT_USER` and, if not found, falls back to the system-wide default in `HKEY_LOCAL_MACHINE` set by the installer.
- `src/core/secret_scanner.py`: Uses `detect_secrets.settings.transient_settings` to explicitly define and enable all scanner plugins. This is necessary to ensure plugins are correctly loaded in a packaged PyInstaller environment where filesystem-based plugin discovery might fail.
- `src.core/updater.py`: The automatic update check compares only the date part of the `last_update_check` timestamp to ensure it runs only once per day, not every time the app is started.
- `src/core/change_applier.py`: A persistent generative flaw was identified where the model repeatedly produced `lines.strip()` instead of the correct `lines[1].strip()`, causing an `AttributeError`. This is a form of pattern-matching failure where a high-probability (but incorrect) code pattern overrides the specific analytical correction. The fix is to embed explicit, high-priority comments (e.g., `// DO NOT REMOVE [index]`) directly in the code to act as a hard constraint during generation.
- `src/core/logger.py`: Centralizes application logging using the `rich` library for formatted console output and a `RotatingFileHandler` for persistent log files. It also sets a global exception hook to ensure all unhandled exceptions are logged.
- `src/core/utils.py`: `parse_gitignore` modifies the `dirs` list of `os.walk` in-place using `is_ignored`. This prevents the walker from traversing into ignored directories (like `node_modules`), drastically improving load times.

### User Interface (`src/ui`)

- **General Dialog Focus**: In several dialog windows (`PasteChangesDialog`, `NewProfileDialog`, etc.), the call to `.focus_set()` on an input widget was moved to *after* the `.deiconify()` call. Setting focus before the window is visible is unreliable and was causing input fields to not receive focus on launch. Adding `.lift()` and `.focus_force()` to the `PasteChangesDialog` was also done for extra robustness.
- `src/ui/app_window.py`: In `apply_changes_from_clipboard()`, the project's base directory for creating new file paths must be accessed via `project_manager.get_current_project().base_dir`. Accessing it directly on the `App` instance (`self.base_dir`) causes an `AttributeError` because the `App` class does not store this state directly.
- `src/ui/app_window.py`: On startup, `_run_update_cleanup()` safely removes temporary installer files from any previous update. It then calls `lift()` and `focus_force()` to ensure the main window gets focus, which is particularly important when relaunched by the installer.
- `src/ui/app_window.py`: Tracks its last move time via the `<Configure>` event. This allows the `ViewManager` to decide whether to use a saved compact mode position or calculate a new one. When moved to a new display, only saved child window positions (`window_geometries`) are cleared.
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
- `src/ui/view_manager.py`: Implements a state machine (`NORMAL`, `SHRINKING`, `COMPACT`, `GROWING`) and custom animation logic to override the OS's default minimize/restore behavior. It uses a timestamp-based system to decide whether to use the last known compact window position or calculate a new one on the current monitor.
- `src/ui/view_manager.py`: In `_on_animation_complete`, the main window restoration logic forces `alpha` to `0.01` and calls `update()` before minimizing. This workaround forces the Windows DWM to update the taskbar thumbnail with the full-sized window buffer instead of a black or shrunken artifact.
- `src/ui/widgets/scrollable_text.py`: The `_manage_scrollbar` method calls `update_idletasks()` before checking `yview()` to prevent a race condition during layout calculation. The overflow detection logic was corrected to `top_fraction > 0.0 or bottom_fraction < 1.0` for robustness.
- `src/ui/window_utils.py`: `get_monitor_work_area` uses Windows-specific APIs to find the correct work area of the monitor a given window is on, ensuring popups and the compact window appear fully visible, even in multi-monitor setups.

### Build, Installation, & CI/CD

- `.github/workflows/release.yml`: A dedicated `validate-tag` job runs before the build to enforce that release tags are created only on the `master` branch, preventing accidental releases from feature branches.
- `go.bat`: The `go r` release command automatically cleans up existing local and remote git tags matching the new version. This allows re-triggering a release build on GitHub Actions without manual git intervention.
- `setup.iss`: The Inno Setup script reads existing registry settings during `InitializeWizard` to preserve user choices on upgrade. The uninstaller prompts the user before removing configuration data. The `[Run]` section uses the `shellexec` flag to run the app in a separate process, fixing post-update launch failures caused by an inherited installer environment.