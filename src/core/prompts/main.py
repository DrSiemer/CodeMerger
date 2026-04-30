# Default Project Instructions
DEFAULT_COPY_MERGED_PROMPT = "Here is the most recent code, please use this when making changes:\n"

DEFAULT_INTRO_PROMPT = """We are working on REPLACE_ME.

QUESTION

"""

DEFAULT_OUTRO_PROMPT = """Stylistic Guidelines (The Harness Standard)

DO:
- make sure empty lines are actually empty: avoid generating lines of spaces or tabs
- use only concise, single-sentence, unnumbered comments without trailing punctuation or XML tags
- always place closing triple backticks (```) on their own, new line
- Present Tense: All rationale in comments must be in the present tense (e.g., 'Checks for null' instead of 'Checked for null')
- Layout Preservation: Mirror the original line-wrapping and structural layout exactly.

Do NOT:
- remove my original comments
- shorten code with comments like `... Unchanged` or `Same as before`
- call something "final" or "definitive"; it usually isn't
- use double newlines between code
- add comments if the code itself makes it pretty clear what it does
- remove logs when you think you have solved a problem; wait for confirmation that the issue is resolved
- use !important to solve HTML styling issues
- no history: do not add comments describing previous states, fixed bugs, or renames. Git handles history; the source should only describe the current state.

Use the following format if you want to add temporary notification comments: // [KEYWORD] Comment (e.g., [FIX] Now using correct value, [MODIFIED] Improved algorithm). These comments are transient and exist only to show the user what you've changed. If you find them in code you are reviewing, remove these comments as the user will have already seen them."""

MAGIC_NUMBER_PROMPT = """Let's hunt down "magic numbers" in this codebase.

**CRITICAL CONSTRAINTS:**
- **No Behavior Changes:** Logic must remain functionally identical. Do not alter the mathematical outcome, visual dimensions, or conditional logic.
- **Centralized Definition:** Extract hardcoded numbers (e.g., dimensions, timeouts, thresholds) and define them as named constants. If a constants or config file already exists in the provided context, you MUST use it. Otherwise, create a new centralized file (e.g., `constants.py`, `constants.js`).
- **Meaningful Names:** Give the extracted numbers descriptive, uppercase names (e.g., `MAX_RETRIES = 5` instead of `FIVE = 5`).
- **Provide Reasoning:** In your `<CHANGES>` section, clearly list which numbers were extracted, what they represent, and where they were moved.

**1. Identify Magic Numbers:**
- Scan the provided code for hardcoded numerical values embedded directly within logic, layout, or calculations (excluding obvious context-free numbers like 0 or 1 in loops).

**2. Extraction & Refactoring:**
- Move these values into the existing project-wide constants file if one is present, or create a logically placed new one.
- Replace the original hardcoded values with references to the extracted constants.
- Ensure all necessary imports are added to the affected files so the project remains functional."""

COMMENT_CLEANUP_PROMPT = """Let's clean up the comments in this project.

**CRITICAL CONSTRAINTS:**
- **Do not output files where nothing is changed.**
- **CODE MUST REMAIN BYTE-FOR-BYTE IDENTICAL.** Do NOT modify code, indentation, spacing, or logic in ANY way! When you delete or move an inline comment, you must preserve the exact whitespace of the remaining code.
- **Sparingly add new comments**, only in places where the code lacks necessary context for a new developer.
- Preserve linter/compiler directives (e.g., eslint-disable, @ts-ignore).

**Directive:** Optimize for a programmer who has never seen the code. Remove all LLM tags, transient feedback, and changelogs. Git handles history; the code shouldn't.

**The "Surprise Factor" Test:**
Only keep a comment if an experienced developer would be surprised by the code.
- **KEEP** comments for workarounds (fixing library bugs, race conditions, or OS quirks).
- **KEEP** comments for atypical choices (why library X was used instead of Y).
- **KEEP** comments for complex business logic (the "why," not the "how").
- **KEEP** structural headers (e.g., "Navigation", "API Logic") that aid file scanning.
- **DELETE everything else.**

**Intelligent Tag Handling (e.g., [FIX], [MODIFIED], [TAG]):**
1. **Strip the Tag:** Mentally remove the [TAG] prefix.
2. **Evaluate the Residue:**
   - If the remaining text describes a **change/history** (e.g., "Renamed function", "Fixed bug in loop"), **DELETE the entire comment**.
   - If the remaining text explains **permanent logic or a "why"** (e.g., "Safari fails to parse this date format without the Z offset"), **KEEP the text but REMOVE the [TAG]**.

**Stylistic Rules:**
1. **Remove Redundancy:** Delete comments that explain the obvious or restate code in English.
2. **Placement:** Move comments from the end of a line to the line *above* the code.
3. **Formatting:** Do not use numbering. Prefer single-line sentences.
4. **Punctuation:** Remove dots from the end of single-line comments.
5. **Tense:** Remove historical/past-tense commentary (e.g., change "Fixed crash" to "Prevents crash"). Do not alter the grammar of existing present-tense or CLI-standard comments.
6. **Spaces:** Do not delete spaces inside the code itself (e.g., do not turn `a = []` into `a =[]`).

Note: If your cleanup removes almost ALL comments in a file, re-verify that you are preserving structural headers and the 'why' context for complex logic blocks."""

DEAD_WEIGHT_PROMPT = """Let's audit this project for unused "dead weight."

**CRITICAL CONSTRAINTS:**
- **No Logic Changes:** Do NOT refactor, "improve," or simplify any logic. Your only job is to excise what isn't being used.
- **Conservative Deletion:** If a file or function appears unused but might be an entry point or required by a file NOT in the current context, LEAVE IT ALONE.
- **Provide Reasoning:** In your `<CHANGES>` section, provide a clear explanation for every file deleted and every block of code removed, justifying why it was deemed unused.

**1. Unused Files (Orphans):**
- Identify files that are never imported, required, or referenced by any other file in this context.
- List these strictly in the `<DELETED FILES>` section using the format: `DELETE FILE: path/to/file.ext`.

**2. Unused Code (Dead Branches):**
- Identify and remove functions, classes, variables, or imports that are defined but never called or referenced.
- Remove unreachable code (e.g., logic following a `return` or `break`).

**3. Cleanup Directive:**
- If a removal leaves behind empty brackets or dangling commas, clean them up to ensure the code remains valid and syntactically correct.
- If a file becomes completely empty after removing unused code, move it to the `<DELETED FILES>` section instead of outputting an empty file."""

DRY_UP_PROMPT = """Let's DRY up this project (Don't Repeat Yourself).

**CRITICAL CONSTRAINTS:**
- **No Behavior Changes:** Logic must remain functionally identical. Do not add new features or change how the code currently handles inputs/outputs.
- **Clarity Over Abstraction:** Do not over-engineer. Only abstract code if it truly reduces the maintenance burden. Avoid deep nesting or overly complex "generic" functions that make the code harder to read.
- **Provide Reasoning:** In your `<CHANGES>` section, clearly explain what logic was consolidated and why the new shared structure was chosen.

**1. Identify Redundancy:**
- Scan for duplicated logic blocks, repeated string/numeric constants, or functions that perform nearly identical tasks with minor variations.

**2. Consolidation:**
- Abstract shared patterns into reusable functions, constants, or components.
- If logic is shared across multiple files, move it to a centralized utility file (e.g., `utils.py`, `helpers.js`) or a relevant core module.
- If this consolidation makes a file obsolete, list it in the `<DELETED FILES>` section.

**3. Update References:**
- Replace the original redundant code with calls to your new abstracted logic.
- Ensure all necessary imports/exports are added to the affected files so the project remains functional."""

BRUTAL_REVIEW_PROMPT = """You are a senior code reviewer in a terrible mood. You have zero patience for over-engineering, sloppy logic, or pointless fluff. Review the provided code and give brutally honest, direct, and short feedback.

**CRITICAL CONSTRAINTS:**
- DO NOT sugarcoat anything.
- DO NOT give compliments.
- Identify the absolute worst offenses immediately.
- Keep it brief. Bullet points only."""

ORDER_REQUEST_PROMPT_TEMPLATE = """Please provide me with the optimal order in which to present these files to a language model. Only return the file list in the exact same format I will use here:

{json_payload}

Here's the content of the files, to help you determine the best order:

{merged_code}"""

SPLIT_FILE_PROMPT_TEMPLATE = """The file `{path}` exceeds optimal token limits for efficient processing and needs to be refactored into smaller, modular components.

**Objective:** Deconstruct this file into a set of smaller, logically separated files. The goal is to achieve a low token count per module while ensuring the system remains 100% functional.

**Refactoring Framework & Best Practices:**
- **Avoid "Container Creep":** Do not simply move the entire contents into one new file with a different name. Aim for true functional decomposition.
- **Single Responsibility:** Extract logic into focused modules (e.g., separate UI components from business logic, or isolate API methods from data parsers).
- **Utility Extraction:** Identify repetitive helper functions or standalone logic and move them into shared utility files (e.g., `utils.js` or `helpers.py`).
- **Functional Preservation:** Maintain all existing logic and external interfaces. Ensure all imports and exports are correctly updated in every affected file.
- **Token Efficiency:** Smaller files are easier to maintain and lead to more reliable AI outputs. Aim for high modularity.

**Proposed Strategy:**
1. **Analyze Dependencies:** Identify logic blocks that can exist independently with minimal cross-references.
2. **Extract Constants & Types:** Move hardcoded values, configuration, or type definitions to centralized files.
3. **Decompose:** Split the core functionality of `{path}` into smaller units.
4. **Integrate:** Update the original file `{path}` (or create a new entry point) to orchestrate these new modules.

**Output Requirement:**
Provide the updated code for `{path}` and all newly created modules. Use the surgical diff format (ORIGINAL/UPDATED) for existing files and provide full content for new ones."""