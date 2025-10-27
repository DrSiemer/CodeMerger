# LLM Project Log

**Core Directive: Act as a Peer Programmer.**
Assume I have full project context. Do not explain obvious code, file structures, or self-evident logic. Focus on the *'why'* behind non-obvious code.

**DO:**

- **Log Exceptions & Decisions:** Note *why* a solution is unusual (e.g., "Workaround for library bug X," "Chose Y library for performance reasons").
- **Log Corrections:** If I correct your behavior, add a note so you don't repeat the mistake.
- **Consolidate Comments:** You may move verbose comments from the source code into this log to improve code readability.
- **Merge Updates:** When updating an existing note, merge new information with the old. Do not remove valid existing details.
- **Be Concise:** Focus on the technical implementation and its direct technical reason.

**DO NOT:**

- **Do not write summaries** of the project, architecture, or individual file functions.
- **Do not explain basic concepts** or write long paragraphs.
- **Do not explain user-facing benefits.** Stick to the "how" and "why" of the code itself.

---

### Quick Examples

**Good Note:**

- `src/ui/assets.py`: Uses a two-stage load (PIL then `PhotoImage`) to avoid a Tkinter race condition with the root window. This is intentional.

**Bad Note:**

- `src/ui/app_window.py`: This file contains the main `App` class which initializes the UI... *(This is an obvious summary)*.

---

## Notes
*(Append new notes below this line)*

### Architectural

- **Global UI Changes**: Component variations must be implemented via optional parameters to avoid creating visual side effects in other parts of the UI.

### Core Logic (`src/core`)

- `src/core/paths.py`: Distinguishes between `get_bundle_dir()` for read-only assets bundled with PyInstaller and `get_persistent_data_dir()` for user configuration (`%APPDATA%` on Windows), ensuring portability and correct data storage.
- `src/core/registry.py`: Settings are read with a fallback system: it first checks for a user-specific setting in `HKEY_CURRENT_USER` and, if not found, falls back to the system-wide default in `HKEY_LOCAL_MACHINE` set by the installer.
- `src/core/secret_scanner.py`: Uses `detect_secrets.settings.transient_settings` to explicitly define and enable all scanner plugins. This is necessary to ensure plugins are correctly loaded in a packaged PyInstaller environment where filesystem-based plugin discovery might fail.
- `src.core/updater.py`: The automatic update check compares only the date part of the `last_update_check` timestamp to ensure it runs only once per day, not every time the app is started.

### User Interface (`src/ui`)

- `src/ui/app_window.py`: On startup, `_run_update_cleanup()` safely removes temporary installer files from any previous update. It then calls `lift()` and `focus_force()` to ensure the main window gets focus, which is particularly important when relaunched by the installer.
- `src/ui/app_window.py`: Tracks its last move time via the `<Configure>` event. This allows the `ViewManager` to decide whether to use a saved compact mode position or calculate a new one. When moved to a new display, only saved child window positions (`window_geometries`) are cleared.
- `src/ui/assets.py`: Uses a two-stage load (PIL then `PhotoImage`) to avoid a Tkinter race condition where `PhotoImage` requires a root window to exist before it can be instantiated.
- `src/ui/compact_mode.py`: The new files warning icon is composited onto the button's base PIL images at runtime to avoid needing separate asset files for every state. Dragging is implemented manually by tracking mouse offsets on a dedicated move bar.
- `src/ui/custom_widgets.py`: The `RoundedButton` is drawn using Pillow with 4x supersampling for anti-aliasing. Font selection is OS-aware to find `segoeui.ttf` on Windows. It redraws on `<Configure>` to support responsive layouts.
- `src/ui/file_manager/file_manager_window.py`: Token recalculation is debounced using `after(250, ...)` to prevent performance issues when rapidly adding/removing many files.
- `src/ui/file_manager/file_tree_handler.py`: Double-click is detected manually using `time.time()` because the standard `<Double-Button-1>` event behavior was inconsistent across different widget states.
- `src/ui/file_monitor.py`: The `start()` method triggers an immediate file scan upon project activation and then uses `app.after()` for subsequent periodic checks.
- `src/ui/status_bar_manager.py`: When the status is updated, it cancels any pending fade animation. After a 4.5-second delay, it kicks off a 0.5-second animation that interpolates the text color to the background color, creating a smooth fade-out.
- `src/ui/update_window.py`: Implements the in-app updater as a modal `Toplevel` window that performs the download in a separate thread. After download, it calls `sys.exit()` to terminate the current app and launches the installer.
- `updater_gui.py`: On startup, the update progress window calls `lift()` and `focus_force()` to ensure it gets focus when it appears.
- `src/ui/view_manager.py`: Implements a state machine (`NORMAL`, `SHRINKING`, `COMPACT`, `GROWING`) and custom animation logic to override the OS's default minimize/restore behavior. It uses a timestamp-based system to decide whether to use the last known compact window position or calculate a new one on the current monitor.
- `src/ui/widgets/scrollable_text.py`: The `_manage_scrollbar` method calls `update_idletasks()` before checking `yview()` to prevent a race condition during layout calculation. The overflow detection logic was corrected to `top_fraction > 0.0 or bottom_fraction < 1.0` for robustness.
- `src/ui/window_utils.py`: `get_monitor_work_area` uses Windows-specific APIs to find the correct work area of the monitor a given window is on, ensuring popups and the compact window appear fully visible, even in multi-monitor setups.

### Build, Installation, & CI/CD

- `.github/workflows/release.yml`: A dedicated `validate-tag` job runs before the build to enforce that release tags are created only on the `master` branch, preventing accidental releases from feature branches.
- `go.bat`: The `go r` release command automatically cleans up existing local and remote git tags matching the new version. This allows re-triggering a release build on GitHub Actions without manual git intervention.
- `setup.iss`: The Inno Setup script reads existing registry settings during `InitializeWizard` to preserve user choices on upgrade. The uninstaller prompts the user before removing configuration data. The `[Run]` section uses the `shellexec` flag to run the app in a separate process, fixing post-update launch failures caused by an inherited installer environment.