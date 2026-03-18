"""
Contains all large text blocks used as prompts for Language Models.
Separating these from logic improves maintainability and readability.
"""

# --- Default Project Instructions ---
DEFAULT_COPY_MERGED_PROMPT = "Here is the most recent code, please use this when making changes:\n"

DEFAULT_INTRO_PROMPT = "Hi! I am working on REPLACE_ME.\n\nQUESTION\n\n"

DEFAULT_OUTRO_PROMPT = """Stylistic Guidelines

DO:
- end your output with clear instructions on how to check if the code you proposed works
- make sure empty lines are actually empty: avoid generating lines of spaces or tabs
- always place closing triple backticks (```) on their own, new line

Do NOT:
- remove my original comments
- shorten code with comments like `... Unchanged` or `Same as before`
- use numbered steps (e.g., "1.") in comments
- use <summary> tags
- end comments with dots (unless you are using multiple sentences)
- call something "final" or "definitive"; it usually isn't
- use double newlines between code
- add comments if the code itself makes it pretty clear what it does
- remove logs when you think you have solved a problem; wait for confirmation that the issue is resolved
- use !important to solve HTML styling issues

Use the following format if you want to add temporary notification comments: // [KEYWORD] Comment (e.g., [FIX] Now using correct value, [MODIFIED] Improved algorithm). These comments are transient and exist only to show the user what you've changed. If you find them in code you are reviewing, remove these comments as the user will have already seen them."""

COMMENT_CLEANUP_PROMPT = """Let's clean up the comments. Remove all LLM tags (e.g., [MODIFIED], [FIX]), transient feedback, and changelogs. Git handles history; the code shouldn't.

Directive: Optimize the code for a programmer that has never seen this code before. Assume they understand standard syntax; do not explain what the code is doing, only why it is the way it is, if it is non-obvious.

1. Remove Redundancy: Delete comments that explain the obvious or simply restate the code in English (e.g., "Submit button" above a <button>, or "No clicks" next to pointer-events: none)
2. Keep Structure: Retain section headers (e.g., "Navigation", "API Logic") that help file navigation
3. Keep Context: Retain comments that explain the "why" behind complex business logic or workarounds for browser bugs, but clean up the wording
4. Clean Tags: Remove the [TAG] prefix. If the comment remains useful without the tag, keep it; otherwise, delete it
5. Avoid comments directly behind code
6. Do not use numbering in comments
7. Remove dots from the end of single line comments
8. Single line comments for single sentences are preferred, even if that makes them long
9. No History: Delete comments describing changes, fixes, or renames (e.g., "Removed X", "Fixed Y", "Renamed Z"). If a comment refers to the code's past state, delete it
10. Present Tense: All rationale must be in the present tense. If a rationale explains a choice (e.g., "Named pose_recorder to avoid shadowing"), ensure it describes the current state, not the act of changing it

Do not change code, only comments."""

# --- Project Starter Prompt Templates ---

STARTER_CONCEPT_DEFAULT_GOAL = "The plan is to build a..."

STARTER_CONCEPT_PROMPT_INTRO = "Based on the following user goal, generate a full project concept document."

STARTER_CONCEPT_PROMPT_CORE_INSTR = """
### Core Instructions
1. Fill in every section with specific details relevant to the user's goal.
2. Ensure the 'User Flows' section covers the complete lifecycle of the main data entity.
3. **Readability & Formatting:** Use frequent line breaks and short paragraphs to avoid dense blocks of text. Utilize Markdown elements (bullet points, bolding) to ensure the document is highly readable and visually structured.
"""

STARTER_STACK_PROMPT_INTRO = "Based on the project concept and the developer's experience, recommend the best technical stack for this project."

STARTER_STACK_PROMPT_INSTR = """
### Instructions
1. Analyze requirements against known skills.
2. Return the recommended stack as a raw JSON list of strings.
   - Example: ["Python 3.10", "Flask"]
3. Return ONLY the JSON.
"""

STARTER_TODO_PROMPT_INTRO = """You are a Technical Project Manager.
Based on the following project Concept and Tech Stack, create a detailed TODO plan."""

STARTER_TODO_PROMPT_INSTR = """
### Instructions
1. **Analyze Relevance:** Compare the Reference Template against the Concept. **SKIP** any phase from the template that is not appropriate for this specific project (e.g., remove 'Database' for a static site, remove 'API' for a CLI tool).
2. **Adapt Tasks:** For the phases you keep, adapt the tasks to be specific to this project (e.g., change 'Create tables' to 'Create `users` and `products` tables').
3. **Format & Custom Phases:** You MUST output the plan using `<<SECTION: Phase Name>>` followed by content.
   - Suggested Phase Names: {headers_str}.
   - **ADDITIONAL PHASES:** You are encouraged to add project-specific phases if the suggested list is insufficient. Simply create a descriptive name for any new section.
   - **DO NOT** output sections for phases you decided to skip.
4. **THE DEPLOYMENT ANCHOR (CRITICAL):** Regardless of how many custom phases you add, the "Deployment" phase MUST be the final section of your response. All other phases (suggested or custom) must be placed before it.
"""

STARTER_GENERATE_MASTER_INTRO = "You are a senior developer creating a boilerplate for: {name}\nStack: {stack}"

STARTER_GENERATE_MASTER_INSTR = """
### Core Instructions
1. **Select & Rename:** Select the appropriate `go_*.bat` script for the stack and rename it to `go.bat`.
2. **Mandatory README:** You MUST output the `README.md` file. Populate it (or create it) with the project title, the pitch, and specific setup steps derived from the stack.
3. **BOILERPLATE ONLY:** DO NOT implement any of the actual tasks, code, or features described in the TODO plan yet. Your job is ONLY to set up the skeleton/infrastructure (README, batch scripts, config files). Do NOT create source files (like *.js, *.py, *.css) unless they are explicitly part of the standard boilerplate provided above.
4. **Short Description:** At the start of your response, provide a short, one-sentence description (noun phrase) of exactly what this project is (e.g., 'a Python-based CLI tool for image processing'). This description must grammatically fit into the sentence 'We are working on [PITCH].' Wrap this description in `<<PITCH>>` tags. **You MUST close the tag with `<<PITCH>>`. Example: `<<PITCH>>a new CLI tool<<PITCH>>`.**
5. **Project Color:** Choose a single accent hex color code (e.g. #4A90E2) that fits the brand or technology of this project. Wrap it in `<<COLOR>>` tags. Example: `<<COLOR>>#4A90E2<<COLOR>>`.
6. **Output Format:** Return the complete source code for every file you are modifying or creating using this exact format:
--- File: `path/to/file.ext` ---
```language
[content]
```
--- End of file ---

CRITICAL: Do NOT omit the '--- End of file ---' marker for any block.
"""

STARTER_REWRITE_PROMPT_TEMPLATE = """You are a Project Editor.
The user has provided a global instruction to modify the project plan.
Your task is to update the drafts listed below to comply with this instruction.

### Summary Requirement
You MUST start your response with a brief summary and explanation of what you changed and why.
Wrap this summary in `<<NOTES>>` tags.
Example: <<NOTES>>I updated the database schema to include a 'status' field and revised the user flow accordingly.<<NOTES>>

### User Instruction
{instruction}

### Locked Sections (Reference Only - DO NOT CHANGE)
{references}

### Content to Update
{targets}

### Instructions
1. Review the User Instruction.
2. Rewrite the content in the 'Content to Update' section to incorporate this instruction.
3. Ensure consistency with 'Locked Sections' (if any), but do not modify them.
4. {target_instructions}
5. Output the summary in `<<NOTES>>`, followed by the updated content."""

STARTER_SYNC_PROMPT_TEMPLATE = """You are a Consistency Engine. The user has modified section **{current_name}**.
Update *unsigned* drafts to match these changes, respecting *locked* sections.

### New Source of Truth: {current_name}
```
{content}
```
{ref_context}
### Drafts to Update
{target_context}

### Instructions
1. {target_instructions}"""

STARTER_QUESTION_PROMPT_TEMPLATE = """### {context_label}
{context_content}

### Focus: {focus_name}
{focus_content}

### Question
{question}

Instruction: {instruction_suffix}"""