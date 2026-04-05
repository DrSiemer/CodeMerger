# CodeMerger UI Rewrite Plan (Vue 3 + PyWebView)

## Phase 1: Environment Setup & API Bridge
*Goal: Establish the Vue frontend, the Python backend, and the communication layer between them.*

- [x] **Frontend Init:** Run `npm create vite@latest frontend -- --template vue` in the project root.
- [x] **Dependencies:** Install Tailwind CSS (for rapid layout), `vue-router` (if needed for wizard/settings), and `lucide-vue-next` (or similar, for SVG icons to replace image assets).
- [x] **Python API Class:** Create `src/api.py`. This class will contain all methods exposed to JavaScript (e.g., `select_directory()`, `get_config()`, `save_config()`, `open_url()`).
- [x] **PyWebView Entry Point:** Create `run_webview.py` to replace `run.py`.
    - Set it to load `http://localhost:5173` if a `--dev` flag is passed.
    - Set it to load `frontend/dist/index.html` for production.
    - Bind the `Api` class to `webview.create_window(..., js_api=api)`.
- [x] **Native Dialogs:** Implement OS dialogs in `api.py` using `webview.windows[0].create_file_dialog()` for folder/file selection.

> **🛑 Human Verification Checkpoint 1:**
> - Does running the Python script successfully open a PyWebView window showing the default Vue welcome screen?
> - Can a Vue button call a Python method (e.g., `window.pywebview.api.test()`) and receive a response?
> - Does the native OS folder selection dialog open when triggered from Vue?

---

## Phase 2: Core Layout, State & Settings
*Goal: Rebuild the main dashboard structure and connect it to the `App_State` and `Project_Config` logic.*

- [ ] **State Management:** Set up a Vue composable (e.g., `useAppState.js`) to fetch the initial config from Python on mount and sync changes back.
- [ ] **Main Layout:** Build the Top Bar (Project selector, title, folder icon), Main Content Area, and Status Bar.
- [ ] **Project Loading:** Implement the "Select Project" flow. Vue calls `api.select_project()` -> Python utilizes `ProjectManager` -> returns `ProjectConfig` dict -> Vue updates UI.
- [ ] **Modals:** Implement basic Vue modals for:
    - Settings (Application, File Manager, Prompts, Editor, Starter).
    - Filetypes Manager (Simple list with toggles).
    - Project Selector (Recent projects list with filtering).
- [ ] **Actions:** Connect the "Copy Code Only" and "Copy with Instructions" buttons to call `api.copy_merged_code()` (which utilizes `src/core/clipboard.py`).
- [ ] **Tooltips:** Implement standard HTML `title` attributes or a lightweight Vue tooltip plugin.

> **🛑 Human Verification Checkpoint 2:**
> - Can you select a project and see the UI update with the project name?
> - Do the Settings and Filetypes modals open, successfully save data to `config.json` via Python, and close?
> - Does clicking the "Copy" buttons successfully put the merged code into the Windows clipboard?

---

## Phase 3: File Manager & Drag-and-Drop
*Goal: Rebuild the dual-pane file selection interface.*

- [ ] **Layout:** Create a split-pane layout (Left: Available Files, Right: Merge Order).
- [ ] **File Tree (Left):**
    - Create a recursive Vue component `<FileTreeNode>` to render the nested directory structure returned by `api.get_file_tree()`.
    - Implement double-click to add files to the merge list.
    - Implement visual indicators (text color) for filtered or new files.
- [ ] **Merge Order (Right):**
    - Install `vuedraggable` (or `@formkit/drag-and-drop`) to handle the sortable list.
    - Bind the list to the selected files array. When reordered in Vue, send the new array to Python to update `ProjectConfig`.
- [ ] **Token Counting:** Expose `get_token_count_for_text` to the API. Have Vue request token counts for selected files and display them, changing text color if the limit is exceeded.
- [ ] **File Monitor:** Convert `FileMonitor` to use a Python background thread. When new files are detected, use `webview.windows[0].evaluate_js()` to trigger a Vue event that shows the "New Files" warning icon.

> **🛑 Human Verification Checkpoint 3:**
> - Does the file tree accurately reflect the project folder and respect `.gitignore`?
> - Can you add files, drag them to reorder, and remove them?
> - Do token counts calculate and display correctly?
> - Does clicking "Update Project" save the `.allcode` file correctly?

---

## Phase 4: AI Feedback & Diff Viewer
*Goal: Rebuild the Markdown rendering and interactive diff comparison.*

- [ ] **Markdown Rendering:** Install `markdown-it` in Vue. Create a `<MarkdownRenderer>` component to display AI commentary safely.
- [ ] **Paste Logic:** Connect the "Paste Changes" button. Vue sends clipboard text to Python -> Python parses it -> returns the structured JSON plan.
- [ ] **Review Modal (Tabs):** Create a tabbed modal (Intro, Changes, Answers, Verification).
- [ ] **Diff Viewer:**
    - Expose original and new file content to Vue.
    - Use a library like `diff2html` or a simple custom Vue component that compares the two strings and renders green/red highlighted lines.
- [ ] **Interactive File List:** Rebuild the file list where users can click "Accept", "Discard", or "Undo" on individual files, triggering the respective Python file-system actions.

> **🛑 Human Verification Checkpoint 4:**
> - When pasting an AI response, does the Review Modal appear?
> - Does the Diff Viewer accurately show added/removed lines?
> - Does clicking "Accept" physically write the new file to the disk via Python?
> - Does clicking "Undo" revert the file to its previous state?

---

## Phase 5: Project Starter Wizard
*Goal: Rebuild the multi-step form and the Segmented Markdown Reviewer.*

- [ ] **Stepper UI:** Build a tabbed/stepper component for navigation (Details -> Base Files -> Concept -> Stack -> TODO -> Generate).
- [ ] **State Syncing:** Ensure Vue maintains the draft state (Goal, Experience, LLM responses) and syncs with Python's `session_manager.py` on step changes.
- [ ] **Segmented Reviewer:**
    - Build a layout with a Sidebar (Segments) and Main Area (Editor/Renderer).
    - Implement the Lock/Unlock (Sign-off) toggles.
    - Implement the "Edit/Render" toggle switching between a `<textarea>` and the `<MarkdownRenderer>`.
- [ ] **Prompt Generation:** Connect Vue buttons to Python to generate prompts and automatically copy them to the clipboard.
- [ ] **Generation Step:** Connect the final "Create Project Files" button to trigger `StarterProjectCreator` in Python, followed by displaying the Success view.

> **🛑 Human Verification Checkpoint 5:**
> - Can you navigate through the wizard steps without losing drafted text?
> - Do the LLM prompt copy buttons work?
> - Can you lock/unlock segments in the Reviewer?
> - Does the final "Create Project" button successfully scaffold the boilerplate folder on disk?

---

## Phase 6: Compact Mode & Window Management
*Goal: Replicate the always-on-top, draggable mini-window integration.*

- [ ] **Window State Handling:** In Python, subscribe to the `events.minimized` event on the main PyWebView window.
- [ ] **Compact Window Creation:** When minimized, Python should hide the main window and create a *second* PyWebView window (`frameless=True`, `on_top=True`, `width=250`, `height=100`) pointing to a specific Vue route (e.g., `/#/compact`).
- [ ] **Compact UI:** Build the minimal Vue view containing the title, Adaptive Copy button, and Paste button.
- [ ] **OS Dragging:** Add CSS `--webkit-app-region: drag` (or PyWebView equivalent) to the compact window header to allow native OS dragging.
- [ ] **Restoration:** Double-clicking the header or clicking close should trigger an API call that destroys the compact window and restores the main window.

> **🛑 Human Verification Checkpoint 6:**
> - Does minimizing the main app instantly spawn the compact widget?
> - Is the widget always on top of other applications?
> - Can you drag the widget around the screen?
> - Does restoring the main window work seamlessly?

---

## Phase 7: Build Pipeline & Clean Up
*Goal: Finalize the single-executable build process and remove Tkinter.*

- [ ] **Delete Tkinter:** Remove the entire `src/ui/` directory (excluding assets/reference files). Remove Tkinter imports from `codemerger.py`.
- [ ] **Refactor Updater:** Update `src/core/updater.py`. Instead of Tkinter `messagebox`, have it return states to Vue to trigger HTML-based update alerts.
- [ ] **Update `go.bat`:**
    - Add a step to run `npm run build` in the `frontend/` directory before running PyInstaller.
- [ ] **Update `codemerger.spec`:**
    - Remove `get_tcl_tk_datas()`.
    - Add `('frontend/dist', 'frontend/dist')` to the `datas` array.
    - Add `webview` and `webview.platforms.edgechromium` to `hiddenimports`.
- [ ] **Compile:** Run `go b` to test the full PyInstaller and Inno Setup build.

> **🛑 Human Verification Checkpoint 7:**
> - Does `go b` successfully build `CodeMerger_Setup.exe`?
> - When installing and running the executable, does it launch perfectly without opening a background console window?
> - Are there no leftover Tkinter dependencies causing errors?