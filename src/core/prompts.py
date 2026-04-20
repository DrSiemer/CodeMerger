"""
Contains all large text blocks used as prompts for Language Models.
Separating these from logic improves maintainability and readability.
"""

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
3. **Formatting:** Do not use numbering. Prefer single-line comments for single sentences.
4. **Punctuation:** Remove dots from the end of single-line comments.
5. **Tense:** Remove historical/past-tense commentary (e.g., change "Fixed crash" to "Prevents crash"). Do not alter the grammar of existing present-tense or CLI-standard comments.
6. **Spaces:** Do not delete spaces inside the code itself (e.g., do not turn `a = []` into `a =[]`).

Note: If your cleanup removes almost ALL comments in a file, re-verify that you are preserving structural headers and the 'why' context for complex logic blocks."""

# Surgical Diff Instruction Fragments
INSTR_FULL_FILE = """NO CODE TRUNCATION (STRICT REQUIREMENT):
   - You MUST provide the FULL, COMPLETE content for EVERY file you modify.
   - DO NOT use comments like `// ... rest of code`.
   - ZERO OMISSION POLICY: Every single line must be mirrored exactly."""

INSTR_FAST_APPLY = """SURGICAL DIFFS (FAST APPLY):
   - Only output the specific changes using ORIGINAL/UPDATED blocks.
   - **Baseline Awareness (STRICT REQUIREMENT):** Your reference for the ORIGINAL block MUST be the *current* state of the code as it exists *now*. If we have been editing a file throughout this session, the ORIGINAL block must reflect the code *after* your most recent modification.
   - **EVOLUTIONARY CONTEXT:** Do NOT use the initial source code from the start of the conversation as a reference if it has since been modified. The evolved state is your new and only baseline.
   - **Replace All Shortcut:** If you are replacing the ENTIRE content of a file, you may put `==ALL==` inside the ORIGINAL block instead of repeating the whole file verbatim.
   - The ORIGINAL section must match the current state of the code exactly (including indentation).
   - You can provide multiple blocks per file.
   - **NEW FILES:** If you are creating a file that does not yet exist in the project, do NOT use ORIGINAL/UPDATED blocks. Simply provide the full content of the file."""

EXAMPLE_FULL_FILE = "[full unabridged code here]"

EXAMPLE_FAST_APPLY = """<<<<<<< ORIGINAL
[existing code to replace]
=======
[new code]
>>>>>>> UPDATED

OR for total rewrites / NEW files:

<<<<<<< ORIGINAL
==ALL==
=======
[entirely new file content]
>>>>>>> UPDATED"""

# Project Starter Prompt Templates

STARTER_CONCEPT_DEFAULT_GOAL = "The plan is to build a..."

STARTER_CONCEPT_PROMPT_INTRO = "Based on the following user goal, generate a full project concept document."

STARTER_CONCEPT_PROMPT_CORE_INSTR = """
### Core Instructions
1. Fill in every section with specific details relevant to the user's goal.
2. Ensure the 'User Flows' section covers the complete lifecycle of the main data entity.
3. **Readability & Formatting:** Use frequent line breaks and short paragraphs to avoid dense blocks of text. Utilize Markdown elements (bullet points, bolding) to ensure the document is highly readable and visually structured.
"""

STARTER_STACK_PROMPT_INTRO = "Act as a Senior Software Architect. Your goal is to select the leanest, most performant technical stack for the project below."

STARTER_STACK_PROMPT_INSTR = """
### Constraints
1. **Requirement-First Selection:** Analyze the Project Concept first. Suggest technologies that are objectively the best fit for the problem, regardless of what's in the Developer Experience list.
2. **Experience-Second Filtering:** Use the "Developer Experience" list ONLY to choose between technically equal paths. Do not default to Python or other listed languages if they are inappropriate for the project concept.
3. **Deep Rationale:** For every choice, provide a technical rationale explaining why it is the optimal fit for this specific project.
4. **The "Why Not Delete" Warning:** For every technology, generate a one-sentence "warning" explaining exactly what would be lost or what significant technical hurdle would be introduced if this item were removed from the stack.
5. **Format:** Return ONLY a raw JSON array of objects.
   - Format: [{"tech": "Name", "rationale": "Reasoning", "warning": "Consequence of removal"}]
   - Example: [{"tech": "PostgreSQL", "rationale": "Relational handling for user data", "warning": "Switching to NoSQL would require a total rewrite of our complex analytical queries."}]
"""

STARTER_TODO_PROMPT_INTRO = """You are a Technical Project Manager.
Based on the following project Concept and Tech Stack, create a detailed TODO plan."""

STARTER_TODO_PROMPT_INSTR = """
### Instructions
1. **Analyze Relevance:** Compare the Reference Template against the Concept. **SKIP** any phase from the template that is not appropriate for this specific project (e.g., remove 'Database' for a static site, remove 'API' for a CLI tool).
2. **Adapt Tasks:** For the phases you keep, adapt the tasks to be specific to this project (e.g., change 'Create tables' to 'Create `users` and `products` tables').
3. **Format & Custom Phases:** You MUST output the plan using `<SECTION name="Phase Name">` followed by content and closing with `</SECTION>`.
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
4. **Short Description:** At the start of your response, provide a short, one-sentence description (noun phrase) of exactly what this project is (e.g., 'a Python-based CLI tool for image processing'). This description must grammatically fit into the sentence 'We are working on [PITCH].' Wrap this description in `<PITCH>` tags. **You MUST close the tag with `</PITCH>`. Example: `<PITCH>a new CLI tool</PITCH>`.**
5. **Project Color:** Choose a single accent hex color code (e.g. #4A90E2) that fits the brand or technology of this project. Wrap it in `<COLOR>` tags. Example: `<COLOR>#4A90E2</COLOR>`.
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
Wrap this summary in `<NOTES>` tags.
Example: <NOTES>I updated the database schema to include a 'status' field and revised the user flow accordingly.</NOTES>

### User Instruction
{instruction}{references}

### Content to Update
{targets}

### Instructions
1. Review the User Instruction.
2. Rewrite the content in the 'Content to Update' section to incorporate this instruction.
3. {consistency_instr}
4. {target_instructions}
5. Output the summary in `<NOTES>`, followed by the updated content."""

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

# Project Visualizer Prompt
VISUALIZER_GENERATION_PROMPT = """Analyze the following project code from my Merge List.
Create a hierarchical Architecture Explorer to help me visualize the project's structure based on logic, dependencies, and roles.

**Goal:** Provide a deep, expert-level architectural breakdown. I want sophisticated insights into how these files interact and why they exist.

**Constraints:**
1. Structure the system into explicit conceptual layers: High-level Domains -> Functional Features -> Structural Components -> Implementation Details.
2. At every level, group elements so NO NODE HAS MORE THAN 6 CHILDREN. Create semantic "Aggregation Nodes" (e.g., "Core Utilities", "Auth Modules") to group smaller parts if necessary.
3. Assign a "domain" to top-level nodes (e.g., "frontend", "backend", "libraries", "infrastructure").
4. CRITICAL ZERO OMISSION POLICY: You are provided with an explicit list of {file_count} "Files to Categorize" below.
   - You MUST assign EVERY SINGLE FILE from this list to exactly one leaf node.
   - Do not drop, skip, or ignore any files, even if they seem minor or redundant.
   - **MANDATORY COUNT:** Your final JSON MUST contain exactly {file_count} file entries.
   - **Handling Uncertainty:** If a file's semantic role is unclear, place it in a catch-all node like "Project Infrastructure" or "Supporting Artifacts" rather than omitting it.
5. **Quality over Brevity:** For each file, provide a rich, detailed description (2-4 sentences) explaining its specific role, core logic, and its importance to the overall architecture. Avoid generic filler; be specific to the code provided.
6. Each node (category) MUST have a short, insightful description of the role that part of the system plays.

**Self-Correction Strategy (Before Responding):**
- Count the files in your generated JSON.
- Compare this count against the expected total ({file_count}).
- If you are short, find the missing files in the "Files to Categorize" list and add them.
- If you run out of output tokens, I will ask you to continue, but you must not start by omitting files.

**Output Format:**
Return ONLY a raw JSON object (or array of objects) with the following structure:
[
  {{
    "name": "Node Name",
    "description": "Role of this part of the system.",
    "domain": "frontend",
    "children": [ ... recursively ],
    "files": [
      {{
        "path": "path/to/file1.ext",
        "description": "Detailed explanation of what this file does, its core logic, and why it is important."
      }}
    ]
  }}
]

**Files to Categorize:**
{file_list}
{previous_map_context}
**Project Code Content:**
{merged_content}"""