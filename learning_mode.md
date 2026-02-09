Notes

- Keep this code as separated from the main application code as possible; not everybody will want to use it
- The process should offer an easy way to converse about a particular segment to help them understand (similar to how asking questions is set up in the Project Wizard)



# Feature Concept: Guided Implementation Mode ("Learning Mode")

## 1. The Core Concept
The "Learning Mode" transforms CodeMerger from a pure utility into a mentoring tool. Instead of dumping a complete solution into the codebase at once, it forces the language model to break the solution down into logical, verifiable steps.

This addresses the "hollowing out" of junior developer skills by shifting the focus from **syntax** (which the AI handles) to **architecture and validation** (where human judgment is required).

### The Workflow
1.  **Opt-In:** The user toggles "Learning Mode" on the main application window.
2.  **Prompting:** When copying code, CodeMerger appends a strict protocol to the system prompt, instructing the LLM to format its response as a series of segmented, verifiable steps.
3.  **Parsing & Validation:** When the user pastes the response, CodeMerger validates the format. If valid, it launches the **Guided Paste Wizard**.
4.  **Guided Application:**
    *   The wizard presents the solution one step at a time.
    *   **Auto-Apply:** As soon as a step is displayed, the code changes for that specific step are automatically applied to the project.
    *   **Context & Verification:** The user sees the *Explanation* (Architectural reasoning) and the *Verification Instructions* (How to test this specific change).
    *   **Progression:** The user must explicitly confirm they have verified the step before proceeding to the next one.

## 2. The Protocol (LLM Output Format)

To enable the parser to function correctly, the LLM must adhere to a strict separator format.

**Proposed Structure:**

```text
# Introduction
[High-level summary of the architectural approach]

## --- STEP 1: [Step Title] ---
### Explanation
[Why we are doing this. Focus on architecture/design patterns.]

### Verification
[Specific instructions: e.g., "Run `npm test`, you should see Error X disappear."]

### Code
--- File: `path/to/file.py` ---
```
[Code content]
```
--- End of file ---

## --- STEP 2: [Step Title] ---
... (Repeat structure)

## --- END STEPS ---
[Final summary]
```

## 3. Implementation Plan

### Phase 1: Configuration & UI Toggle
*   [ ] **Update `src/constants.py`**:
    *   Define `LEARNING_MODE_PROMPT`: A prompt template instructing the LLM on the specific separator format and the requirement for verification steps.
    *   Define `STEP_SEPARATOR_PATTERN`: Regex or string constant for identifying steps (e.g., `## --- STEP \d+: .+ ---`).
*   [ ] **Update `src/app_state.py`**:
    *   Add `learning_mode_enabled` boolean to the state model.
*   [ ] **Update `src/ui/ui_builder.py`**:
    *   Add a toggle button (e.g., a "Hat" icon or `SwitchButton`) to the main window (likely near the Copy buttons) to toggle the mode.
*   [ ] **Update `src/core/clipboard.py`**:
    *   Modify `copy_project_to_clipboard` to check the toggle state. If enabled, append the `LEARNING_MODE_PROMPT` to the final clipboard output.

### Phase 2: Parser Logic
*   [ ] **Create `src/core/guided_parser.py`**:
    *   Implement `validate_guided_response(text)`: Scans the text to ensure it contains at least one valid step separator and that the structure is intact (no broken code blocks). Returns a boolean and an error message if invalid.
    *   Implement `parse_guided_response(text)`: Splits the text into a list of "Step Objects".
        *   *Step Object Structure:* `{ "title": str, "explanation": str, "verification": str, "code_blocks": str }`

### Phase 3: The Guided Paste Wizard
*   [ ] **Create `src/ui/guided_paste_dialog.py`**:
    *   This is a new `Toplevel` window, distinct from `PasteChangesDialog`.
    *   **Layout:**
        *   **Header:** Step Progress (e.g., "Step 1 of 4: Database Setup").
        *   **Left Panel:** Scrollable text area for "Explanation" and "Verification".
        *   **Right Panel:** Read-only view of the code changes applied in this step.
        *   **Footer:**
            *   "Verification Checklist" (Checkbox: "I have verified this step works").
            *   Navigation Buttons: "Previous" (Disabled), "Next Step" (Disabled until checked).
    *   **Logic:**
        *   On `__init__`: Parse the content. If invalid, fall back to standard error/paste dialog.
        *   On `show_step(index)`:
            1.  Call `change_applier.execute_plan()` for the code in the *current* step immediately.
            2.  Update the UI text areas.
            3.  Update the status bar to say "Changes for Step X applied."

### Phase 4: Integration
*   [ ] **Update `src/ui/app_window_parts/action_handlers.py`**:
    *   Modify `apply_changes_from_clipboard` and `open_paste_changes_dialog`.
    *   Before opening the standard dialog, run a quick check: `guided_parser.is_guided_format(clipboard_content)`.
    *   If true, validate fully.
        *   If valid: Open `GuidedPasteDialog`.
        *   If invalid format but looks like an attempt: Show warning ("Guided format detected but broken").
        *   Else: Open standard `PasteChangesDialog`.