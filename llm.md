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
- `src/core/change_applier.py`: Implements a placeholder-bypass in `get_section` to treat a single dash (`-`) or standard keywords (none, n/a) as an empty string. This is a workaround for LLMs that struggle to leave XML-tagged segments completely empty when instructed.

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