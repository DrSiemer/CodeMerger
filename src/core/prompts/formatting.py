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

3. **{mode_instruction}**

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
{example_content}
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