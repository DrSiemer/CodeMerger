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
- **Info Mode Key-Sync Requirement (CRITICAL):** When porting Info Mode features from Python to Web UI, a 1:1 mapping between `info_messages.py` (Python) and `infoMessages.js` (JavaScript) is MANDATORY. If a key is used in `v-info` but is missing from `infoMessages.js`, the system silently falls back to the default message. Since the text doesn't change, Vue's reactivity system will not trigger an update, resulting in the footer appearing "broken" or "frozen" even if events are firing. ALWAYS verify the frontend key dictionary exists before implementing hovers.
- **Dots in batch files:** NEVER use triple dots (`...`) in Batch scripts (`.bat`), as they cannot handle it and you will break the scripts by doing that.

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

- **Strict Whitespace Sanitization**: To prevent "phantom diffs" (where the system detects changes that are invisible to the eye), CodeMerger enforces an aggressive sanitization pipeline. ALL file content (extracted from LLM responses or read from disk) is normalized to LF line endings and has every line's trailing whitespace stripped. This occurs inside the parser (`src/core/change_applier.py`) before any comparison or write operation. LLMs should avoid generating trailing whitespace entirely.
- **Global UI Changes**: Component variations must be implemented via optional parameters to avoid creating visual side effects in other parts of the UI.
- **Marker Fragment Strategy (Self-Hosting)**: To allow CodeMerger to bundle its own source code without the parser tripping over its own definitions, all marker string constants and regex patterns (e.g., `--- File:`) are constructed using string fragments (concatenation). Marker counting logic also uses line-start anchors (`^`) and `re.MULTILINE` to avoid matching substrings inside code blocks.
- **Automatic Deletion Prohibition**: CodeMerger never allows automatic deletion of files. Even during "Auto-Apply" (Ctrl-click) workflows, the application must detect proposed deletions in the LLM response and force a blocking confirmation dialog that explicitly lists the files targeted for removal.
- **PyWebView DPI Scaling Matrix (Windows)**: When DPI awareness is enabled on Windows, PyWebView 5.3+ operates in a non-standard "Hybrid" unit system. The `create_window` constructor requires **Physical Pixels** for position (`x`, `y`) but **Logical Pixels** for dimensions (`width`, `height`). Property getters like `win.x` and `win.width` return **Physical Pixels**. However, runtime execution methods follow a "Unit Split" quirk: `win.move()` requires **Logical Units** (OS-scaled), while `win.resize()` requires **Physical Units** (1:1 pixels). High-DPI growth logic must perform math in Physical space and apply these specific conversions per-method to avoid cropping or growth failure.
- **Hard-Wired Info Reactivity**: Documentation updates across view boundaries (e.g., from an absolute-positioned modal to the global footer) must bypass destructured hooks. The `InfoPanel.vue` footer must import the `DOC_STATE` singleton **directly** as a module-level constant from `useAppState.js`. Updates to the hover stack must use the **Spread-Operator Replacement** pattern (`activeInfoStack.value = [...stack]`) to create a new array reference, forcing Vue 3 to trigger watchers regardless of stacking context.
- **Explicit Paste Routing**: To maintain strict control over clipboard data and bypass browser security/permission dialogs, the standard browser `paste` event is globally blocked (`preventDefault`) in the main application window. ALL paste operations must be initiated via keyboard shortcuts or UI buttons that call the Python backend's `pyperclip` wrapper. This ensures consistent data handling across different OS environments and WebView versions.
- **Cross-Window Clipboard Access**: The application explicitly bypasses the `navigator.clipboard` API in favor of the Python `pyperclip` bridge. This avoids browser permission popups and "User Activation" requirements that would otherwise block programmatic clipboard access, especially when triggering paste operations from the Compact window into the Main window's review logic.

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
- **Development Updater Search (Quirk)**: When running in non-frozen (source) mode, the `Updater` checks `dist/CodeMerger/updater_gui.exe` as a secondary path. This allows testing the update system without a full installation, provided the developer has run `go ba` to generate the build artifacts first.
- **Forceful Update Shutdown (Quirk)**: The main application uses `os._exit(0)` to terminate immediately after launching the update GUI. This bypasses the standard PyWebView/Chromium graceful shutdown, which can be slow or hang due to COM object teardown. Immediate exit is required so the `updater_gui.exe` can see the PID has vanished and begin the download/install cycle without a timeout.

### PyWebView & Web UI

- **Smart Growth Mechanism**: To prevent "stuck" states where complex modals (like Settings or File Manager) are clipped due to a small main window size, components use a `resizeWindow` hook on mount. This calls the backend `ensure_window_size` API, which grows the window to `max(current, requested)` dimensions. It never shrinks the window, respecting user-defined larger layouts.
- **Base64 Asset Pipeline**: Local images are served to the frontend via a `get_image_base64` API method. This bypasses security restrictions and path inconsistencies associated with serving local filesystem files directly in a WebView environment.
- **API Bridge Protection**: Properties in the Python `Api` class prefixed with an underscore (e.g., `self._window`) are ignored by PyWebView during JS API generation. This is used to store internal references without triggering premature DOM evaluation or crashes during the startup handshake.
- **Graceful Shutdown & Multi-Window Teardown (Workaround)**: Avoid `os._exit(0)` inside the `window.events.closed` handler on Windows. Abruptly killing the process prevents Chromium (WebView2) from cleanly unregistering its window classes, resulting in `Failed to unregister class Chrome_WidgetWin_0. Error = 1411`. Additionally, when managing multiple windows where a secondary window intercepts its `closing` event (returning `False`), you must use an `_is_shutting_down` flag to bypass the intercept during app exit. The secondary window MUST be explicitly destroyed inside the main window's `closing` event (not `closed`) to ensure clean COM object teardown before the primary window finishes closing. Cleanup logic (stopping background threads) is placed immediately after the blocking `webview.start()` call to ensure the UI loop has fully exited first.
- **Strict Window Mutual Exclusion**: The main application window and the Compact window must NEVER be visible at the same time. Because the OS can force a window restoration (e.g., via a taskbar click), the `WindowManager` must subscribe to `shown`, `restored`, and `maximized` events on the main window to explicitly hide the Compact window whenever the main dashboard is displayed.
- **Window Restore Artifact Fix**: To prevent intermittent visual glitches where the main window animates from an oversized (often screen-sized) state when exiting Compact Mode, the window's last known good dimensions and coordinates must be explicitly re-applied via `move()` and `resize()` immediately before calling `show()` and `restore()`. This ensures the OS window manager anchors the restoration animation to the correct dashboard bounds rather than defaulting to the full desktop workspace.
- **High-DPI Hybrid Growth Strategy**: To solve "cropped growth" on High-DPI displays (e.g., 150% scaling), CodeMerger uses an **Absolute Physical Arithmetic** pipeline. Centering and boundary checks are performed in raw physical pixels against the monitor's work area. **Hybrid-Domain Execution** is then applied: `win.resize()` is called with raw physical pixels (for standard windows), while `win.move()` is called with logical pixels (physical / scale). This overcomes PyWebView's inconsistent unit handling. Calls are **sequenced** (move then resize) with a 20ms delay to prevent OS-level geometry drops.
- **Overlay-Isolated Global Layout**: To ensure the Info footer remains visible and accessible even when modals are open, the app uses a split-level layout in `App.vue`. The main content area is a `relative` container, while the footer is a sibling to that container. Modals use `absolute inset-0` positioning to anchor strictly to the content area. This ensures that the transparent black backdrop used by modals physically cannot cover the Info Panel or Status Bar.
- **Reference-Replacement Reactivity**: Vue 3 reactivity for module-level `ref` arrays (like the `activeInfoStack` used for hovers) can fail to notify components across view boundaries if updated via mutation methods like `.push()`. Global state updates for Info Mode must use the spread operator (`activeInfoStack.value = [...activeInfoStack.value, key]`) to replace the array reference, forcing a reliable DOM update.

### Build, Installation, & CI/CD

- `.github/workflows/release.yml`: A dedicated `validate-tag` job runs before the build to enforce that release tags are created only on the `master` branch, preventing accidental releases from feature branches.
- `go.bat`: The `go r` release command automatically cleans up existing local and remote git tags matching the new version. This allows re-triggering a release build on GitHub Actions without manual git intervention.
- `setup.iss`: The Inno Setup script reads existing registry settings during `InitializeWizard` to preserve user choices on upgrade. The uninstaller documentation includes notes on removing configuration data. The `[Run]` section uses the `shellexec` flag to run the app in a separate process, fixing post-update launch failures caused by an inherited installer environment.
- **EdgeChromium Initialization (Installer Note)**: In `setup.iss`, the `[Run]` section MUST use the `shellexec` flag. Without this, the application inherits the installer's environment (often elevated or with limited DLL access), which can cause PyWebView's underlying `WebView2` loader to fail to find the Edge runtime, resulting in a blank window or crash on the first launch after update.
- **Local Update Mocking (Testing)**: To verify the update logic without a live GitHub release, redirect `GITHUB_API_URL` to `http://127.0.0.1:8000/release.json` and serve a mock JSON file alongside the setup executable from the local `dist-installer` folder. Set `version.txt` to `0.0.0` to force detection.
- **Dev vs Debug Mode (CLI)**: Use `go dev` for active UI development (hot-reloading Vite frontend). Use `go debug` to test the production bundle (`frontend/dist`) with DevTools enabled. This is critical for debugging backend-to-frontend handshakes or bundling issues before release.