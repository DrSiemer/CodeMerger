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