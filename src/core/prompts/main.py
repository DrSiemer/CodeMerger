# Default Project Instructions
DEFAULT_COPY_MERGED_PROMPT = "Here is the most recent code, please use this when making changes:\n"

DEFAULT_INTRO_PROMPT = "We are working on REPLACE_ME.\n\nQUESTION\n\n"

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