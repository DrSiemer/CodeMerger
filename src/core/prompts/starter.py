# Project Starter Prompt Templates

STARTER_CONCEPT_DEFAULT_GOAL = "The plan is to build a..."

STARTER_CONCEPT_PROMPT_INTRO = "Based on the following user goal, generate a full project concept document."

STARTER_CONCEPT_PROMPT_CORE_INSTR = """
### Core Instructions
1. Fill in every section with specific details relevant to the user's goal.
2. Ensure the 'User Flows' section covers the complete lifecycle of the main data entity.
3. **Readability & Formatting:** Use frequent line breaks and short paragraphs to avoid dense blocks of text. Utilize Markdown elements (bullet points, bolding) to ensure the document is highly readable and visually structured.
4. **Technical Alignment:** If a 'Reference Project' is provided, use it as a technical guide. Your concept should describe a new project that follows the architectural patterns and logic style found in that reference code.
"""

STARTER_STACK_PROMPT_INTRO = "Act as a Senior Software Architect. Your goal is to determine the optimal stack for the new project below, ensuring technical continuity with the core ecosystem of the Reference Project (if provided)."

STARTER_STACK_PROMPT_INSTR = """
### Constraints
1. **Ecosystem Continuity:** If a 'Reference Project' is provided, you MUST stick to its primary language and framework (e.g., if the reference is PHP/CodeIgniter, the new stack must be PHP/CodeIgniter). Do NOT suggest a different primary ecosystem simply because it appears in the Competency Profile.
2. **Requirement-First Flexibility:** While you must maintain the core ecosystem, you are FREE to pick the supporting technologies (databases, caching, utilities, frontend libraries) that work best for the *new* project goal. Do not feel obligated to use a specific library or database from the Reference Project if it is not the best fit for the new requirements.
3. **Discard Irrelevant Legacy:** If the Reference Project contains technologies, patterns, or integrations that do not relate to the NEW project goal, DISCARD them. Your priority is a lean, goal-focused stack.
4. **Competency Profile:** Treat the 'USER COMPETENCY PROFILE' as a background skills profile. Use it to verify the user is comfortable with your recommendations.
5. **Deep Rationale:** For every choice, provide a technical rationale explaining why it is the optimal fit for this specific project and how it aligns with the core ecosystem.
6. **The "Why Not Delete" Warning:** For every technology, generate a one-sentence "warning" explaining exactly what would be lost or what significant technical hurdle would be introduced if this item were removed.
7. **Format:** Return ONLY a raw JSON array of objects.
   - Format: [{"tech": "Name", "rationale": "Reasoning", "warning": "Consequence of removal"}]
   - Example: [{"tech": "PostgreSQL", "rationale": "Relational handling for user data", "warning": "Switching to NoSQL would require a total rewrite of our complex analytical queries."}]
"""

STARTER_DESIGN_PROMPT_INTRO = "You are a Senior Systems Architect. Based on the following Project Concept and Tech Stack, create a comprehensive System Design document."

STARTER_DESIGN_PROMPT_INSTR = """
### Instructions
1. **Be Specific:** Do not write generic advice. Define actual table names, component hierarchies, state management strategies, and data payloads based on the concept and chosen stack.
2. **Present Alternatives (CRITICAL):** Whenever you make a significant architectural decision that has a viable alternative (e.g., SQLite vs Postgres, SPA vs SSR, REST vs GraphQL, Context API vs Redux), you MUST wrap your chosen path in `<SELECTEDPATH>` and `</SELECTEDPATH>` tags.
3. **Alternative JSON Block:** Immediately after the closing `</SELECTEDPATH>` tag, provide a JSON array of valid options wrapped in `<ALTERNATIVES>` and `</ALTERNATIVES>` tags.
   - **Lateral Engineering Pivots:** Do NOT provide 'discarded' or 'rejected' ideas. Instead, identify high-quality, defensible architectural paths that reflect legitimate engineering trade-offs.
   - **Contextual Superiority:** Each alternative must be presented as a choice that becomes the **superior path** under different strategic priorities (e.g., prioritizing extreme horizontal scale vs. low infrastructure complexity).
   - **Format:** Format the JSON strictly as:
<ALTERNATIVES>
[
  {{ "title": "Pivot to [Option Name]", "description": "A high-level technical description of this path and the specific scenario or priority where this choice would be superior to the current selection." }}
]
</ALTERNATIVES>
4. **Format & Custom Phases:** You MUST output the plan using `<SECTION name="Phase Name">` followed by content and closing with `</SECTION>`.
   - Required Phase Names: {headers_str}.
5. **Architectural Consistency:** If a 'Reference Project' is provided, your design MUST respect the established architectural patterns (e.g., MVC, Hexagonal, etc.) found in that code to ensure the new features are a natural fit for the existing system.
"""

STARTER_PIVOT_PROMPT_TEMPLATE = """You are a Project Editor. The user has elected to pivot the system design.
In the segment **{active_key}**, locate the following selected path:
```
{selected_path_text}
```
Replace this path with the following alternative: **{alt_title} - {alt_desc}**.

### Content to Update
{targets}

{references}

### Instructions
1. Rewrite the '{active_key}' segment to fully integrate this new direction. Remove the `<ALTERNATIVES>` block for this specific choice once applied. You may leave the `<SELECTEDPATH>` wrapper or remove it, but integrate the new text smoothly.
2. Review all other unlocked draft segments (Content to Update). If this architectural pivot affects them, update them to remain perfectly consistent.
3. Ensure consistency with 'Locked Sections' (Reference Only), but do not modify them.
4. Keep any other `<SELECTEDPATH>` and `<ALTERNATIVES>` blocks in the document exactly as they are, unless this new pivot makes them logically impossible.
5. Return the COMPLETE updated text for all modified segments using the `<SECTION name="...">` format.
6. Start your response with a brief summary wrapped in `<NOTES>...</NOTES>` explaining what you changed across the system design."""

STARTER_TODO_PROMPT_INTRO = """You are a Technical Project Manager.
Based on the following project Concept, Tech Stack, and System Design, create a detailed TODO plan."""

STARTER_TODO_PROMPT_INSTR = """
### Instructions
1. **Analyze Relevance:** Compare the Reference Template against the Concept and System Design. **SKIP** any phase from the template that is not appropriate for this specific project (e.g., remove 'Database' for a static site, remove 'API' for a CLI tool).
2. **Adapt Tasks:** For the phases you keep, adapt the tasks to be highly specific to the provided System Design (e.g., instead of 'Create tables', write 'Create `users` and `products` tables as defined in Data Models').
3. **Format & Custom Phases:** You MUST output the plan using `<SECTION name="Phase Name">` followed by content and closing with `</SECTION>`.
   - Suggested Phase Names: {headers_str}.
   - **ADDITIONAL PHASES:** You are encouraged to add project-specific phases if the suggested list is insufficient. Simply create a descriptive name for any new section.
   - **DO NOT** output sections for phases you decided to skip.
4. **THE DEPLOYMENT ANCHOR (CRITICAL):** Regardless of how many custom phases you add, the "Deployment" phase MUST be the final section of your response. All other phases (suggested or custom) must be placed before it.
5. **Base Code Integration:** If a 'Reference Project' is provided, ensure your tasks account for it (e.g., 'Migrate data models from legacy reference' or 'Replace utility patterns found in example code').
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

STARTER_DEFAULT_SCAFFOLD_INTRO_TEMPLATE = """We are working on {project_pitch}.

Continue work on the plan laid out in `todo.md`. If a bug is reported, fix it first. ONLY output `todo.md` (in full, without omissions) when explicitly updating checkbox status."""

STARTER_SECTION_INSTRUCTIONS_TEMPLATE = """You MUST structure your response using specific section separators.
Do not add any text outside these sections.
For each section, output the delimiter followed immediately by the content and close it.

REQUIRED FORMAT:
{delimiters}"""

STARTER_REFERENCE_PROJECT_HEADER = """
### REFERENCE PROJECT (TECHNICAL REFERENCE GUIDE)
--- IMPORTANT: The code provided below is a strong guide for the technology stack, architectural patterns, and coding standards intended for this project. Use these files to determine the framework (e.g., CodeIgniter, React) and libraries to use. Note that you are designing a NEW project from scratch; do NOT assume a pre-prepared environment exists. ---
"""

STARTER_NAME_SUGGESTIONS_PROMPT_TEMPLATE = """Act as a branding expert and creative consultant. Based on the project details provided below, suggest 10 unique and catchy project names.

### Project Concept
{concept}

### Tech Stack
{stack}

Provide a diverse list of suggestions (ranging from literal and professional to creative and abstract) and include a one-sentence rationale for each."""