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

### Meta-Log: Notes on My Behavior

*(Use this section to log corrections to my own behavior, so I don't repeat mistakes. This is separate from code logic.)*

- **Logging Threshold:** Do not log standard bug fixes or common implementation patterns. The bar for a "quirk" is high: it must be a workaround, a non-standard choice, or an otherwise surprising piece of code.
- **Info Mode Key-Sync Requirement (CRITICAL):** When porting Info Mode features from Python to Web UI, a 1:1 mapping between `info_messages.py` (Python) and `infoMessages.js` (JavaScript) is MANDATORY. If a key is used in `v-info` but is missing from `infoMessages.js`, the system silently falls back to the default message. Since the text doesn't change, Vue's reactivity system will not trigger an update, resulting in the footer appearing "broken" or "frozen" even if events are firing. ALWAYS verify the frontend key dictionary exists before implementing hovers.
- **Dots in batch files:** NEVER use triple dots (`...`) in Batch scripts (`.bat`), as they cannot handle it and you will break the scripts by doing that.

---

## Code Quirks & Workarounds

### Architectural

- **Strict Whitespace & Line Normalization**: To prevent "phantom diffs," CodeMerger enforces a strict sanitization pipeline in `src/core/change_applier.py`. ALL file content (LLM output or disk) is normalized to LF endings and has trailing whitespace stripped. Comparisons and writes occur only on this sanitized data.
- **Marker Fragment Strategy (Self-Hosting)**: To allow CodeMerger to bundle its own source, all marker constants (e.g., `--- File:`) are constructed using string fragments (concatenation). Logic in `merger.py` and `change_applier.py` uses line-start anchors (`^`) and `re.MULTILINE` to prevent false matches within code blocks.
- **PyWebView DPI "Hybrid" Coordination (Windows)**: PyWebView 5.3+ handles units inconsistently. The `create_window` constructor and `win.resize()` require **Physical Pixels**, but `win.move()` requires **Logical Units** (OS-scaled). Property getters (`win.x`, `win.width`) always return **Physical Pixels**. Calculation pipelines in `window_geometry.py` and `window_manager.py` perform math in Physical space and apply per-method conversion to avoid geometry drops.
- **Explicit Python-Bridged Clipboard**: Standard browser `paste` events are globally blocked in `App.vue`. All clipboard operations route through the Python `pyperclip` bridge. This bypasses "User Activation" security restrictions and permission popups, which is essential for programmatic paste operations between the Compact window and the Main window's review logic.
- **Taskbar Continuity (Windows)**: To prevent the taskbar icon from jumping to the "back of the line" during mode switches, the Main window is never hidden; it remains in a `minimized` state to anchor the taskbar presence. The Compact window is flagged as a `WS_EX_TOOLWINDOW` via Win32 API to suppress its own taskbar button, creating the illusion of a single stable application icon.
- **Inventory-First UI Stack**: To support 12,000+ files, `FileMonitorThread` maintains a flat memory inventory (paths + gitignore status). The `FileApi` reconstructs the UI Tree on-demand using a non-recursive Trie builder. This avoids Disk IO during filtering, searching, and sorting.
- **Visibility Bypass (Purple Logic)**: Selected files (Merge Order) are immune to Extension and Gitignore filters. If a file is visible *only* because of this bypass, it is flagged as `is_filtered`, triggering a purple visual style to alert the user that settings would normally hide it.

### Backend Logic (`src/core`, `src/api_parts`)

- **Atomic Configuration Persistence**: `src/core/project_config.py` uses `tempfile.mkstemp` and `os.replace` for atomic writes. The `load` method includes defensive checks to ignore transiently empty files created during write collisions, preventing the initialization of empty default profiles.
- **Permissive Section Parsing**: The `change_applier.py` parser is permissive with the `ANSWERS TO DIRECT USER QUESTIONS` tag, accepting either the full closing tag or a truncated `</ANSWERS>` to handle LLM output cutoffs. It also filters out common AI hallucinations (e.g., "No conceptual questions were asked") to keep segments clean.
- **Forceful Update Shutdown**: CodeMerger uses `os._exit(0)` immediately after launching `updater_gui.exe`. This bypasses PyWebView/Chromium COM object teardown, which can hang and block the external updater from accessing the locked process ID.
- **Named Mutex Single-Instance Detection**: `src/core/utils.py` uses a Named Mutex (Windows) and `fcntl` (POSIX) for instance detection instead of process scanning, avoiding the high startup cost of iterating the system process table.
- **Adaptive Monitor Throttling**: `FileMonitorThread` scales sleep time based on scan duration ($T \times 4$). If a scan takes 3s, it sleeps for 12s. On Windows, it also calls `THREAD_MODE_BACKGROUND_BEGIN` to lower IO/CPU priority during massive project walks.
- **API Bridge Protection**: Attributes in the `Api` class prefixed with an underscore (e.g., `self._window_manager`) are ignored by PyWebView during JS API generation, preventing premature DOM evaluation or crashes during the startup handshake.

### Frontend & Web UI (`frontend/src`)

- **Spread-Operator Reactivity Replacement**: Vue 3 reactivity for module-level array refs (like `activeInfoStack` in `infoMode.js`) can fail to trigger watchers across view boundaries if updated via `.push()`. Global state updates MUST use the spread-operator replacement pattern (`activeInfoStack.value = [...stack]`) to force array reference changes.
- **Split-Level Layout Isolation**: To ensure the Info footer remains visible over modals, `App.vue` uses a split layout where the main content is a `relative` container and the footer is a sibling. Modals use `absolute inset-0` to anchor to the content area, preventing the modal backdrop from covering the Info Panel.
- **Async Search Request Sequencing**: `FileManagerModal.vue` uses a `lastRequestId` tracker. Responses from the Python backend are discarded if their ID is older than the current session query, preventing "reverting" UI results if a fast simple search finishes after a slow complex one.
- **Windows MIME Type Overrides**: `run_webview.py` explicitly registers MIME types for `.js`, `.mjs`, and `.css` in the Python `mimetypes` module. This bypasses a common Windows registry bug where `.js` is mapped to `text/plain`, which would otherwise cause Chromium to refuse ES modules.
- **Compact Mode Transient State**: Coordinates for the Compact Mode window are strictly transient. They must reset to `None` on every application startup. If `None`, the window centers on the main dashboard using Physical Pixel arithmetic.
- **Single-Change Auto-Verification**: If an AI response proposes only a single file change (modification, creation, or deletion), accepting that change via the file list buttons will automatically switch the review window to the Verification tab. THIS IS BY DESIGN. For responses containing multiple files, the view remains on the Changes tab after individual accepts to allow for further review, unless the 'Apply All' button is used.
- **Visualizer Context Copying**: The "Copy Merged Code" action in the Architecture Explorer is available for any navigated node except the global root. This allows for copying entire subtrees (domains/components) or specific leaf components. To ensure intentional context sharing, the button only appears when actively navigated *into* a node and is hidden during hover previews.

### Build & Environment

- **EdgeChromium Installer Flags**: In `setup.iss`, the `[Run]` section MUST use the `shellexec` flag. Without it, the app inherits the installer's elevated environment, which often causes the `WebView2` loader to fail to locate the Edge runtime, resulting in a blank window.
- **Release Tag Validation**: `.github/workflows/release.yml` includes a `validate-tag` job that enforces tags are created only on the `master` branch to prevent accidental releases from feature branches.
- **Local Update Mocking**: Update logic can be verified by pointing `GITHUB_API_URL` to `localhost:8000/release.json` and serving a mock JSON from the `dist-installer` folder.