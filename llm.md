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

- Be careful making global visual changes. Component variations must be implemented via optional parameters, to avoid side effects in other parts of the UI.
- `src/core/paths.py`: Distinguishes between `get_bundle_dir()` for read-only assets bundled with PyInstaller and `get_persistent_data_dir()` for user configuration (`%APPDATA%` on Windows), ensuring portability and correct data storage.
- `src/core/registry.py`: Settings are read with a fallback system: it first checks for a user-specific setting in `HKEY_CURRENT_USER` and, if not found, falls back to the system-wide default in `HKEY_LOCAL_MACHINE` that is set by the installer.
- `src/core/secret_scanner.py`: Uses `detect_secrets.settings.transient_settings` to explicitly define and enable all scanner plugins. This is necessary to ensure plugins are correctly loaded in a packaged PyInstaller environment where filesystem-based plugin discovery might fail.
- `src.core/updater.py`: The automatic update check compares only the date part of the `last_update_check` timestamp to ensure it runs only once per day, not every time the app is started.
- `src/ui/app_window.py`: When the `status_var` is updated, it cancels any pending fade animation and resets the text color to full visibility. After a 4.5-second delay, it kicks off a 0.5-second animation that interpolates the text color from its default (`#D3D3D3`) to the status bar's background color (`#3A3A3A`), creating a smooth fade-out effect. Once faded, the text is cleared. It also tracks its last move time via the `<Configure>` event. This allows the `ViewManager` to decide whether to use a saved compact mode position or calculate a new one. When moved to a new display, only saved *child* window positions (`window_geometries`) are cleared, as the compact mode position is now handled by the timestamp logic.
- `src/ui/assets.py`: Uses a two-stage load (PIL then `PhotoImage`) to avoid a Tkinter race condition where `PhotoImage` requires a root window to exist before it can be instantiated.
- `src/ui/compact_mode.py`: The new files warning icon is composited onto the button's base PIL images at runtime. This avoids needing separate asset files for every button state. Dragging is implemented manually by tracking mouse offsets on a dedicated move bar and triggers a callback on release to record its move time.
- `src/ui/custom_widgets.py`: The `RoundedButton` is drawn using Pillow with 4x supersampling for anti-aliasing. Font selection is OS-aware to find `segoeui.ttf` on Windows for better rendering. It redraws on the `<Configure>` event to support responsive layouts (e.g., `sticky='ew'`).
- `src/ui/file_manager/file_manager_window.py`: Token recalculation is debounced using `after(250, ...)` to prevent performance issues when rapidly adding or removing many files from the selection. The file filter functionality is coordinated here, tracing a `StringVar` to trigger filtering in both the file tree and the selection list, and to manage the UI state (e.g., disabling sorting buttons).
- `src/ui/file_manager/file_tree_handler.py`: Double-click is detected manually using `time.time()` because the standard `<Double-Button-1>` event behavior was inconsistent across different widget states and focus conditions.
- `src/ui/file_monitor.py`: The `start()` method triggers an immediate file scan upon project activation and uses `app.after()` for periodic file checks.
- `src/ui/view_manager.py`: Implements a state machine (`NORMAL`, `SHRINKING`, `COMPACT`, `GROWING`) and custom animation logic to override the OS's default minimize/restore behavior. It now uses a timestamp-based system to decide whether to use the last known compact window position or to calculate a new one. The default position is now calculated using the work area of the main window's *current* monitor (via a new helper in `window_utils.py`), ensuring the compact window appears on the correct screen, even in multi-monitor setups.
- `src/ui/widgets/scrollable_text.py`: The `_manage_scrollbar` method calls `update_idletasks()` before checking `yview()` to prevent a race condition during layout calculation. The overflow detection logic was also corrected to `top_fraction > 0.0 or bottom_fraction < 1.0`, which robustly handles all scroll positions and correctly identifies when content exceeds the visible area.
- `src/ui/window_utils.py`: Added a new helper, `get_monitor_work_area`, which uses Windows-specific APIs to find the exact work area of the monitor a given window is currently on. The existing `position_window` logic was also updated to ensure popups are kept fully visible on their intended screen.
- `go.bat`: The `go r` release command automatically cleans up existing local and remote git tags matching the new version. This allows re-triggering a release build on GitHub Actions without manual git intervention.
- `setup.iss`: The Inno Setup script reads existing registry settings during `InitializeWizard` to preserve user choices (like "Enable automatic updates") when upgrading. The uninstaller explicitly asks the user if they want to remove their configuration data in `%APPDATA%`.
- `.github/workflows/release.yml`: A dedicated `validate-tag` job runs before the build to enforce that release tags are created only on the `master` branch, preventing accidental releases from feature branches.