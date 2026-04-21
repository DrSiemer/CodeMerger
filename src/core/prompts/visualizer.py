# Project Visualizer Prompt
VISUALIZER_GENERATION_PROMPT = """Analyze the following project code from my Merge List.
Create a hierarchical Architecture Explorer to help me visualize the project's structure based on logic, dependencies, and roles.

**Goal:** Provide a deep, expert-level architectural breakdown. I want sophisticated insights into how these files interact and why they exist.

**Constraints:**
1. Structure the system into explicit conceptual layers: High-level Domains -> Functional Features -> Structural Components -> Implementation Details.
2. At every level, group elements so NO NODE HAS MORE THAN 6 CHILDREN. Create semantic "Aggregation Nodes" (e.g., "Core Utilities", "Auth Modules") to group smaller parts if necessary.
3. Provide a high-level summary at the root level that serves as an intro to the code structure and explains the main division of logic.
4. Assign a "domain" to top-level nodes (e.g., "frontend", "backend", "libraries", "infrastructure").
5. CRITICAL ZERO OMISSION POLICY: You are provided with an explicit list of {file_count} "Files to Categorize" below.
   - You MUST assign EVERY SINGLE FILE from this list to exactly one leaf node.
   - **ROOT LEVEL PROHIBITION:** Do NOT attach files directly to the global root node. Every file must be inside a functional or semantic grouping node.
   - Do not drop, skip, or ignore any files, even if they seem minor or redundant.
   - **MANDATORY COUNT:** Your final JSON MUST contain exactly {file_count} file entries.
   - **Handling Uncertainty:** If a file's semantic role is unclear (e.g., top-level config, build scripts, README), place it in a catch-all aggregation node like "Miscellaneous Artifacts" or "Project Infrastructure" rather than omitting it or leaving it at the root.
5. **Quality over Brevity:** For each file, provide a rich, detailed description (2-4 sentences) explaining its specific role, core logic, and its importance to the overall architecture. Avoid generic filler; be specific to the code provided.
6. Each node (category) MUST have a short, insightful description of the role that part of the system plays.

**Self-Correction Strategy (Before Responding):**
- Count the files in your generated JSON.
- Compare this count against the expected total ({file_count}).
- If you are short, find the missing files in the "Files to Categorize" list and add them.
- If you run out of output tokens, I will ask you to continue, but you must not start by omitting files.

**Quality & Formatting Requirements:**
1. For each file, provide a rich, detailed description (2-4 sentences) explaining its specific role, core logic, and importance.
2. **Use Markdown formatting** in all description fields.
3. Ensure every description contains **at least one bold segment** to highlight the most critical aspect of that file or node.

**Output Format:**
Return ONLY a raw JSON object representing the system root. The root-level "description" must contain the high-level intro to the code structure.
{{
  "name": "System Architecture",
  "description": "A comprehensive intro to the code structure, explaining the main division of logic across domains.",
  "children": [
    {{
      "name": "Category Name",
      "description": "High-level role of this grouping.",
      "domain": "frontend",
      "children": [ ... sub-categories recursively ... ],
      "files": [
        {{
          "path": "path/to/file.ext",
          "description": "Rich 2-4 sentence explanation of the file's logic and purpose."
        }}
      ]
    }}
  ]
}}

**Files to Categorize:**
{file_list}
{previous_map_context}
**Project Code Content:**
{merged_content}"""

# Project Visualizer Amend Prompt
VISUALIZER_AMEND_PROMPT = """I am building an Architecture Explorer and your previous response was incomplete or contained redundancies.

**Missing Files to Categorize:**
{missing_list}

**Duplicate Entries Found:**
{duplicate_list}

**Instructions:**
1. Categorize the 'Missing Files' into the architectural structure we just discussed.
2. For each missing file, provide the 'parent' node name where it should be placed.
   - **Semantic Grouping:** If a file doesn't fit into an existing node, suggest a NEW semantic parent name that describes its role (e.g., "Documentation Assets", "Utility Hooks").
3. For 'Duplicate Entries', identify which redundant instances should be REMOVED to satisfy the 'One File, One Node' policy.
4. Provide a rich description for each added file (2-4 sentences). **Use Markdown formatting and make at least one segment of each description bold to indicate the most important part.**

**Output Format:**
Return ONLY a raw JSON object with an 'amendments' key:
{{
  "amendments": {{
    "add": [
      {{
        "path": "path/to/missing_file.ext",
        "parent": "Existing or New Node Name",
        "description": "Detailed explanation of what this file does."
      }}
    ],
    "remove": [
      "path/to/duplicate_to_delete.ext"
    ]
  }}
}}"""

# Project Visualizer Update Prompt
VISUALIZER_UPDATE_PROMPT = """I am updating my Architecture Explorer. The project structure has evolved, and I need you to provide an AMENDMENT to the existing hierarchy.

**Current Architecture Tree:**
```json
{current_tree}
```

**Files to REMOVE (Obsolete):**
{obsolete_list}

**New Files to ADD (Categorize These):**
{new_files_content}

**Instructions:**
1. Analyze the 'New Files' and determine their semantic placement within the 'Current Architecture Tree'.
2. Identify existing nodes that should be the 'parent' for these files, or suggest new semantic grouping nodes if appropriate.
3. For 'Files to REMOVE', identify their paths in the amendment JSON to ensure they are purged from the hierarchy.
4. Provide a rich, detailed description (2-4 sentences) for each new file added. **Use Markdown formatting and make at least one segment of each description bold to indicate the most important part.** Avoid filler; be specific to the code provided.
5. Ensure the final architecture respects the policy: NO NODE HAS MORE THAN 6 CHILDREN. Create grouping nodes if necessary.

**Output Format:**
Return ONLY a raw JSON object with an 'amendments' key:
{{
  "amendments": {{
    "add": [
      {{
        "path": "path/to/new_file.ext",
        "parent": "Existing or New Node Name",
        "description": "Detailed explanation of what this file does, its core logic, and why it is important."
      }}
    ],
    "remove": [
      "path/to/obsolete_file.ext"
    ]
  }}
}}"""