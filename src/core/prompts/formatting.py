# LLM Output Formatting and Automation Instruction Templates

FORMATTING_INSTRUCTION_TEMPLATE = """**CRITICAL INSTRUCTIONS FOR CODE GENERATION - READ CAREFULLY:**

1. **MANDATORY TAGGING & CLOSING POLICY:**
   Every section of your response (Answers, Intro, Changes, Delete, Verification) MUST be explicitly wrapped in tags.
   **CRITICAL:** Every opening tag MUST have an identical closing tag.
   Format: `<INTRO>[content]</INTRO>`

2. **INTRO, ANSWERS & CHANGES (PRE-CODE):**
   Immediately before the code blocks, provide these sections in this order:
   - **<INTRO>**: Use this to provide a technical implementation plan or architectural summary.
   - **<ANSWERS TO DIRECT USER QUESTIONS>**: If the user asked a specific question (usually ending with a '?'), answer it here. If there is no question mark in the prompt, there is no question. In that case, this block MUST remain empty (use a single dash `-`). Do NOT fill it with filler text like "None" or "No questions".
   - **<CHANGES>**: List of behavioral, algorithmic, or visual changes.

3. **SURGICAL DIFFS (FAST APPLY):**
   - Only output the specific changes using ORIGINAL/UPDATED blocks.
   - **Baseline Awareness (STRICT REQUIREMENT):** Your reference for the ORIGINAL block MUST be the *current* state of the code as it exists *now*. If we have been editing a file throughout this session, the ORIGINAL block must reflect the code *after* your most recent modification.
   - **EVOLUTIONARY CONTEXT:** Do NOT use the initial source code from the start of the conversation as a reference if it has since been modified. The evolved state is your new and only baseline.
   - **REPLACE ALL POLICY:** If any single segment you want to replace in this file is more than 50 lines of code, or if you are replacing the ENTIRE content of a file, you MUST use the Replace All shortcut.
   - **Replace All Shortcut:** Put `--==[ REPLACE ALL ]==--` inside the ORIGINAL block instead of repeating code verbatim.
   - The ORIGINAL section must match the current state of the code exactly (including indentation).
   - **UNIQUENESS REQUIREMENT:** Every ORIGINAL block MUST be unique within the file. If the code you are replacing appears multiple times, include enough surrounding context (lines before/after) to make the block unique and non-ambiguous.
   - You can provide multiple blocks per file.
   - **NEW FILES:** If you are creating a file that does not yet exist in the project, do NOT use ORIGINAL/UPDATED blocks. Simply provide the full content of the file.

4. **EVOLVED BASELINE AWARENESS (SESSION CONTEXT):**
   - You must acknowledge that the codebase evolves. If a file has been modified in previous turns of this conversation, that modified version is your only valid baseline for the ORIGINAL block.
   - NEVER reference the initial code blocks from the start of the chat if they have been superceded by your own subsequent changes.

5. **FUNCTIONAL PRESERVATION:**
   - Do not remove or break any existing functionality.
   - NO SILENT REFACTORING: Do not "improve," "clean up," or "simplify" any code that is not directly related to the requested change. Leave unrelated logic and comments untouched.
   - IMPORTANT: Try to preserve the original code and the logic of the original code as much as possible, unless explicitly instructed to change something.

6. **STRICT CHANGE DETECTION & OUTPUT MINIMIZATION:**
   - ONLY output files that have actually been modified.
   - If a file's final code is **byte-for-byte identical** to the current state of the project, **DO NOT** include it in your output.
   - **UNCHANGED FILES (LAST RESORT ONLY):** If you feel a strict compulsion to acknowledge files you didn't modify, use the optional `<UNCHANGED>` block at the very end of your response. DO NOT output this block if you can simply stop yourself from outputting unchanged files. It is only here to prevent you from wasting tokens on unmodified code blocks.

7. **MANDATORY OUTPUT FORMAT (PARSER COMPATIBILITY):**
   - Every modified file MUST be wrapped exactly like this template, including the trailing marker:

{marker_prefix}{marker_file}`path/to/file.ext` ---
```[language_id]
<<<<<<< ORIGINAL
[existing code to replace]
=======
[new code]
>>>>>>> UPDATED

OR for total rewrites / NEW files:

<<<<<<< ORIGINAL
--==[ REPLACE ALL ]==--
=======
[entirely new file content]
>>>>>>> UPDATED
```
{marker_prefix}{marker_eof} ---

   - **CRITICAL:** The `{marker_prefix}{marker_eof} ---` marker is a machine-parseable sentinel. It MUST be present after every file block.

8. **DELETE, VERIFICATION & UNCHANGED (POST-CODE):**
   Immediately following the final "--- End of file ---" marker, provide these sections:

   <DELETED FILES>
   STRICT FILE PATHS ONLY.
   FORMAT: DELETE FILE: path/to/obsolete_file.ext
   PROHIBITION: Do NOT describe code-level removals, logic deletions, or "cleanup."
   If no files were deleted from the filesystem, this section should ONLY contain a single dash (`-`). Do NOT write "None" or any other text.
   </DELETED FILES>

   <VERIFICATION>
   - Steps to test the changes.
   </VERIFICATION>

   <UNCHANGED>
   (OPTIONAL: You may list the names of unchanged files here to satisfy any compulsion to acknowledge them without outputting their code. Omit this block entirely if possible.)
   </UNCHANGED>

9. **ASSUMPTION OF APPLICATION:** You MUST assume that I have successfully applied your previous output to my local files unless I explicitly state that an issue occurred (e.g., a surgical diff mismatch or incorrectly formatted output). Do not repeat changes from previous turns unless providing a requested correction.

==========

You MUST format your EXACT output using this skeleton. Do not deviate from this structure:

<INTRO>
(Implementation plan)
</INTRO>

<ANSWERS TO DIRECT USER QUESTIONS>
(Answer any direct questions here, otherwise `-`)
</ANSWERS TO DIRECT USER QUESTIONS>

<CHANGES>
(List of changes)
</CHANGES>

{marker_prefix}{marker_file}`path/to/file.ext` ---
```language
(Full unabridged file code or surgical blocks as instructed)
```
{marker_prefix}{marker_eof} ---

<DELETED FILES>
(Files to delete, or `-`)
</DELETED FILES>

<VERIFICATION>
(Testing steps)
</VERIFICATION>"""

AUTOMATION_WARNING_TEMPLATE = "CRITICAL: I am using an automated parser. Please begin your response directly with the <INTRO> tag. You MUST use the exact XML tags and {marker_prefix}{marker_file} wrappers shown in the template. If you use `// ...` or `[rest of code]`, the parser will crash and your response will be useless. You must mirror every single line of the file (or the exact surgical blocks) without omitting lines within the block."

FORMAT_CORRECTION_PROMPT_TEMPLATE = """Please follow the output format strictly as described in your instructions. Your previous response did not fully comply with the required formatting standards. Specifically, please ensure that:
- ALL commentary and explanations must be placed inside one of the allowed XML tags ({LT}{IN_T}{RT}, {LT}{ANS_W}{RT}, {LT}{CHA_N}{RT}, {LT}{VER_I}{RT}, {LT}{UNC_H}{RT}).
- No text or commentary exists outside of these tags.
- File markers are present and correctly formatted ({PRE}File: `path` --- and {PRE}End of file ---).
- You provide the full, complete code for modified files without using placeholders like '// ... rest of code'.
Please re-output the response correctly."""

ORDER_CORRECTION_PROMPT_TEMPLATE = """The file list you provided for the merge order is invalid. Please provide only the JSON array of strings in the exact same format as requested. Ensure you do not omit any files from the current selection and do not add files that were not requested.

Validation Errors:
{error_msg}"""