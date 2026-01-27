# Segmented Wizard Implementation TODO

## Phase 1: Foundation & Data Structures
- [ ] **Define Constants:**
  - [ ] Create `src/ui/project_starter/constants.py`.
  - [ ] Define `CONCEPT_SEGMENTS` (ordered list of keys: problem, principles, features, etc.).
  - [ ] Define `TODO_PHASES` (standard keys: setup, db, api, frontend, polish, deploy).
  - [ ] Define `DELIMITER_TEMPLATE` (e.g., `<<SECTION: {name}>>`).
- [ ] **Update Assets:**
  - [ ] Refactor `assets/reference/concept_questions.json` to a dictionary format mapping segment keys to question lists and display labels.
  - [ ] Refactor `assets/reference/todo_questions.json` to map generic phase keys to question lists.
- [ ] **Create Logic Helper:**
  - [ ] Create `src/ui/project_starter/segment_manager.py`.
  - [ ] Implement `parse_segments(text)`: Returns dict `{key: content}`.
  - [ ] Implement `assemble_document(segments_dict)`: Joins content with headers.
  - [ ] Implement `build_prompt_instructions(segment_keys)`: Generates the strict system instructions for the LLM.

## Phase 2: UI Components (SegmentedReviewer)
- [ ] **Create Component Skeleton:**
  - [ ] Create `src/ui/project_starter/widgets/segmented_reviewer.py`.
  - [ ] Setup standard layout: Left Sidebar (Frame) + Main Content (Frame).
- [ ] **Implement Sidebar:**
  - [ ] Create `SidebarItem` class: Button + Status Icon (Pending/SignedOff).
  - [ ] Implement selection logic (highlight active item).
  - [ ] Add "Full Overview" item at the top.
- [ ] **Implement Content Area - Segment Mode:**
  - [ ] Add `QuestionsPanel`: Reuse existing logic but make it collapsible (hidden by default).
  - [ ] Add `SegmentEditor`: `ScrollableText` bound to the current segment's data.
  - [ ] Add `Footer`: "Sign Off" button (updates state, moves next) and "Revert to Draft".
- [ ] **Implement Content Area - Full Overview Mode:**
  - [ ] Add `ViewSwitcher`: Toggle between Rendered Markdown and Raw Text.
  - [ ] **Rendered View:** Use `MarkdownRenderer` to show `segment_manager.assemble_document()`.
  - [ ] **Raw View:** `ScrollableText` showing the full assembled text.
  - [ ] *Optional/Stretch:* Implement basic re-parsing if the user edits the Raw View.

## Phase 3: Refactor Concept Step (Step 3)
- [ ] **Update State (`wizard_state.py`):**
  - [ ] Add `concept_segments` (Dict) to project data.
  - [ ] Add `concept_signoffs` (Dict or Set) to track status.
- [ ] **Update Prompt Generation (`step2_concept.py`):**
  - [ ] Update `_get_prompt` to include the `build_prompt_instructions` from Phase 1.
- [ ] **Update View (`step2_concept.py`):**
  - [ ] Replace the simple `show_editor_view` with the new `SegmentedReviewer` widget.
  - [ ] Pass the new `concept_questions.json` data to the reviewer.
  - [ ] Update `get_concept_content` to return the assembled document from the segments.

## Phase 4: Refactor TODO Step (Step 5)
- [ ] **Update State (`wizard_state.py`):**
  - [ ] Add `todo_phases` (List) to store selected phases.
  - [ ] Add `todo_segments` (Dict) and `todo_signoffs`.
- [ ] **Create Configuration View:**
  - [ ] In `step4_todo.py`, create a "Phase Selector" screen (Checkboxes).
  - [ ] Default checks: Setup, DB, API, Frontend.
  - [ ] "Generate Prompt" button moves to Generation View.
- [ ] **Update Prompt Generation:**
  - [ ] Construct prompt to ask *only* for the selected phases.
  - [ ] Inject strict delimiters for those phases.
- [ ] **Update Editor View:**
  - [ ] Replace editor with `SegmentedReviewer`.
  - [ ] Pass `todo_questions.json` mapped to the specific phases.

## Phase 5: Integration & Cleanup
- [ ] **Update Master Generator (`step5_generate.py`):**
  - [ ] Ensure it uses the *assembled* versions of Concept and TODO (via `segment_manager.assemble_document`) when building the final request.
- [ ] **Persistence:**
  - [ ] Ensure `session_manager.py` correctly saves/loads the new dictionary structures (`segments` and `signoffs`).
- [ ] **Testing:**
  - [ ] Verify parsing robustness (what if LLM misses a tag?).
  - [ ] Verify "Sign Off" visual feedback works.
  - [ ] Verify "Full Overview" accurately reflects segment changes.