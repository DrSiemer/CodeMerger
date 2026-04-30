# Surgical Diff Instruction Fragments
INSTR_FAST_APPLY = """SURGICAL DIFFS (FAST APPLY):
   - Only output the specific changes using ORIGINAL/UPDATED blocks.
   - **Baseline Awareness (STRICT REQUIREMENT):** Your reference for the ORIGINAL block MUST be the *current* state of the code as it exists *now*. If we have been editing a file throughout this session, the ORIGINAL block must reflect the code *after* your most recent modification.
   - **EVOLUTIONARY CONTEXT:** Do NOT use the initial source code from the start of the conversation as a reference if it has since been modified. The evolved state is your new and only baseline.
   - **REPLACE ALL POLICY:** If any single segment you want to replace in this file is more than 50 lines of code, or if you are replacing the ENTIRE content of a file, you MUST use the Replace All shortcut.
   - **Replace All Shortcut:** Put `--==[ REPLACE ALL ]==--` inside the ORIGINAL block instead of repeating code verbatim.
   - The ORIGINAL section must match the current state of the code exactly (including indentation).
   - **UNIQUENESS REQUIREMENT:** Every ORIGINAL block MUST be unique within the file. If the code you are replacing appears multiple times, include enough surrounding context (lines before/after) to make the block unique and non-ambiguous.
   - You can provide multiple blocks per file.
   - **NEW FILES:** If you are creating a file that does not yet exist in the project, do NOT use ORIGINAL/UPDATED blocks. Simply provide the full content of the file."""

EXAMPLE_FAST_APPLY = """<<<<<<< ORIGINAL
[existing code to replace]
=======
[new code]
>>>>>>> UPDATED

OR for total rewrites / NEW files:

<<<<<<< ORIGINAL
--==[ REPLACE ALL ]==--
=======
[entirely new file content]
>>>>>>> UPDATED"""

SURGICAL_AMBIGUOUS_PROMPT_TEMPLATE = """Ambiguous ORIGINAL Block: The ORIGINAL code blocks provided for the following files appear multiple times in my current local source:
{paths_str}

This creates an ambiguous match, making it impossible to apply the patch safely. Please provide additional context lines (above or below) in your ORIGINAL block to ensure it uniquely identifies the specific segment you intend to modify."""

SURGICAL_MISMATCH_PROMPT_TEMPLATE = """Surgical Patch Mismatch: The ORIGINAL code blocks provided for the following files do not match my current local source:
{paths_str}

This error occurred because your baseline reference is out of sync with the current evolved state of the project. To resolve this, I am providing the *actual* up-to-date source code for the affected files below. Please use this code as your new baseline and return a CORRECTED surgical diff using ORIGINAL/UPDATED blocks.

CRITICAL: Do NOT return the full file content. Only provide corrected surgical blocks.

{blocks_str}"""

SURGICAL_UNIQUENESS_INSTRUCTION = "Please ensure your new ORIGINAL blocks are a byte-for-byte match to my source and are UNIQUE within the file (provide context if needed to disambiguate)."