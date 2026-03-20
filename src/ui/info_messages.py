"""
Contains all user-facing documentation strings for Info Mode.
Explanations are based on the core application documentation.
"""

INFO_MESSAGES = {
    "default": "Info mode active: hover over any interface element to see its purpose and usage details.",

    # --- Main Window ---
    "select_project": (
        "Select a Project: Click to browse for a folder. CodeMerger will create a hidden .allcode file "
        "in that directory, that will store your file selections and project-specific instructions."
    ),
    "project_name": (
        "Project Name: This is the active project. Double-click to set a custom name. Single-click "
        "to switch to another project (same as Select Project button)."
    ),
    "color_swatch": (
        "Project Color: Pick a unique accent color for this project. This color is used in "
        "Compact Mode, to help you visually distinguish between multiple CodeMerger instances."
    ),
    "folder_icon": (
        "Folder Actions: Click to open the project in your File Explorer. Ctrl-click to copy the full "
        "path. Alt-click to open a Command Prompt (CMD) window directly in this directory."
    ),
    "manage_files": (
        "File Manager: Open the dual-panel management window. This is where you decide exactly "
        "which files are relevant to your current task and in what order the AI should read them."
    ),
    "instructions": (
        "Define Instructions: Set a project-specific Intro and Outro. This text will be wrapped "
        "around your code whenever you use 'Copy with Instructions'."
    ),
    "copy_code": (
        "Copy Prompt Only (Ctrl+Shift+C): Merges all selected files with a standard prompt header. "
        "Useful for providing updated context to an LLM without repeating project goals. "
        "Ctrl-clicking the Adaptive Copy button in Compact mode also triggers this action."
    ),
    "copy_with_instructions": (
        "Copy Prompt with Instructions (Ctrl+C): Merges code and wraps it in your custom Intro/Outro. "
        "Strictly enforces 'No Code Truncation' rules. Ctrl-click to perform 'Copy Prompt Only'."
    ),
    "paste_changes": (
        "Paste Changes (Ctrl+V): Open a review window to process AI responses. CodeMerger reads "
        "the Markdown and automatically writes changes back. Ctrl-click to instantly apply from clipboard."
    ),
    "response_review": (
        "AI Response Review: Opens the review window to see the most recently applied changes and "
        "associated AI commentary."
    ),
    "cleanup": (
        "Comment Cleanup: Copies a specialized prompt, that tells the AI to strip out it's own "
        "transient tags like [FIX] or [MODIFIED], while keeping structural logic comments."
    ),
    "settings": (
        "Application Settings: Configure application behavior."
    ),
    "filetypes": (
        "Manage Filetypes: Define which file extensions CodeMerger is allowed to index. "
        "Double-click an entry in the list to enable or disable it globally."
    ),
    "starter": (
        "Project Starter: Launch a guided workflow for starting new projects. Assists you in "
        "creating a concept, tech stack, and step-by-step implementation plan using AI."
    ),
    "info_toggle": (
        "Info Mode: Toggles help panels on all application windows. "
        "Useful for learning how to work with CodeMerger."
    ),
    "profile_nav": (
        "Profile Switcher: Swap between different configurations for the same project. Each "
        "profile has its own file selection and instruction set."
    ),
    "profile_add": (
        "Add Profile: Create a new named configuration. Useful for separating different tasks "
        "like 'Backend' or 'Feature Development' within the same project."
    ),
    "profile_delete": (
        "Delete Profile: Remove the currently active profile. The 'Default' profile cannot be deleted."
    ),

    # --- File Manager ---
    "fm_tree": (
        "Available Files: Browse your project structure. Double-click files or folders to add "
        "them to the merge list. Green text indicates newly detected files. Purple text indicates "
        "files in your merge list that would normally be ignored by the Git or extension filters."
    ),
    "fm_tree_action": (
        "Merge Toggle: Adds or removes the currently selected files from the Merge Order list. "
    ),
    "fm_list": (
        "Merge Order: This list determines in what order the code will be presented to the AI. "
        "Files are merged from top to bottom. Click a file to select it for sorting or removal."
    ),
    "fm_list_tools": (
        "List Visibility: Toggle the display of full file paths or relative filenames in the "
        "merge list."
    ),
    "fm_reveal": (
        "Open in Folder: Click this icon to open your system's file explorer and highlight "
        "this specific file."
    ),
    "fm_filter_git": "Git Filter: Toggle visibility of files listed in your .gitignore. When ON, ignored files are hidden.",
    "fm_filter_ext": "Filetype Filter: Toggle visibility of files not in your allowed extensions list. When ON, extra files are hidden.",
    "fm_filter_text": "Text Filter: Type to filter the tree and the merge list by filename.",
    "fm_tokens": (
        "Total Tokens: A real-time estimate of context usage. As the grow count grows, the color changes "
        "from gray to yellow to red to warn you about LLM context limits."
    ),
    "fm_order": (
        "Order Request: Single-click to copy a prompt asking the AI for the 'optimal' file order. "
        "Double-click to paste a new order list; Ctrl-click to directly apply a list from your clipboard."
    ),
    "fm_tokens_item": (
        "Token Stats: Shows the token count for this file. Ctrl-click to copy a breakup request for "
        "the AI. Alt-click to 'ignore' this file's tokens when calculating the color warnings."
    ),
    "fm_sort_top": "Move to Top: Place the selected files at the beginning of the merge list.",
    "fm_sort_up": "Move Up: Shift the selected files one position higher in the order.",
    "fm_sort_down": "Move Down: Shift the selected files one position lower in the order.",
    "fm_sort_bottom": "Move to Bottom: Place the selected files at the end of the merge list.",
    "fm_sort_remove": "Remove: Take the selected files out of the merge list (does not delete files from disk).",
    "fm_add_all": "Add All: Add every file matching your current filters and search text to the merge list.",
    "fm_save": "Update Project: Commit your changes to the project's .allcode file and return to the main window.",
    "fm_remove_all": "Remove All: Clear the entire merge list for the current profile.",

    # --- Settings Window ---
    "set_app": "Various settings related to application behavior.",
    "set_app_new_file": (
        "File Monitoring: Monitors your project folder for new files added since your last session. "
        "Disable this if you do not want new file warnings or do not want to spend resources on it."
    ),
    "set_app_interval": (
        "Check Interval: How frequently CodeMerger scans the disk for changes. Lower values are more "
        "responsive, but may impact performance on slow drives."
    ),
    "set_app_secrets": (
        "Secret Scanning: Uses 'detect-secrets' to look for API keys or private credentials before you copy. "
        "Enable this to prevent accidentally sharing sensitive data with the language model."
    ),
    "set_app_feedback": (
        "AI Response Review: Automatically open the response review window when wrapped sections are found."
    ),
    "set_app_compact": (
        "Compact Mode: Automatically switches to the floating Compact window when you minimize the "
        "main window. Useful for keeping CodeMerger easily accessible while working in your IDE."
    ),
    "set_app_updates": (
        "Automatic Updates: Checks GitHub for a new version once per day."
    ),
    "set_app_check_now": (
        "Check Now: Manually trigger an update check to see if a newer version of CodeMerger "
        "is available on GitHub, bypassing the automatic daily timer."
    ),

    "set_fm": "Settings that determine the behavior of the File Manager.",
    "set_fm_tokens": (
        "Token Counting: Calculates context usage based on the gpt-4 tokenizer. "
        "Disable this if you want to speed up file indexing in extremely large projects."
    ),
    "set_fm_limit": (
        "Context Limit: Set a target token count (e.g. 200000 for ChatGPT). The token count in the File Manager will "
        "turn red if you exceed this."
    ),
    "set_fm_threshold": (
        "Add All Safety: A warning threshold for the 'Add All' button. Prevents accidentally adding "
        "a large amount of files to your merge list."
    ),

    "set_prompts": "Define your default intro/outro texts.",
    "set_prompt_merged": (
        "Default Header: The text prepended when using 'Copy Prompt Only'. Best used for a short "
        "instruction, telling the AI to use the code as updated context."
    ),
    "set_prompt_intro": (
        "Global Intro: Generic greeting and mission statement. You can easily load this into a new project "
        "from the 'Instructions' window, to save time on project setup."
    ),
    "set_prompt_outro": (
        "Global Outro: Put code style instructions here. Ideal for enforcing formatting rules like "
        "'Always end your output with a clear explanation' across all your AI interactions."
    ),

    "set_starter": "Settings for the Project Starter tool.",
    "set_starter_folder": "Default Root: The parent directory where the Project Starter will create new project sub-folders by default.",

    "set_editor": "Overrule the default code editor to use when double-clicking files. Leave blank to use system defaults.",
    "set_editor_path": (
        "Editor Path: Provide the path to your code editor's executable (e.g., sublime_text.exe). "
        "When set, double-clicking files in the manager opens them directly in this application."
    ),

    # --- Instructions Window ---
    "inst_intro": "Intro Instructions: This text is placed at the very top of your merged code block. Use it to introduce your project.",
    "inst_outro": "Outro Instructions: This text is placed at the bottom. Use it for code style rules or recurring constraints.",
    "inst_defaults": "Load Defaults: Click to wipe the current fields and load the global default prompts you defined in the Settings.",
    "inst_save": "Save: Commit these instructions to the project's .allcode file. They are profile-specific.",

    # --- Filetype Manager ---
    "ft_list": "Indexed Types: Only files matching these extensions are scanned. Double-click to enable or disable.",
    "ft_action": "Active Toggle: Delete custom extensions or toggle the active status of bundled default extensions.",
    "ft_add": "Add Filetype: Type a new extension (e.g. .py or .js) and a short description to add it to the indexing list.",

    # --- Project Selector ---
    "sel_list": "Recent Projects: Quickly switch to another CodeMerger project. Hover over an entry to see the full path and Ctrl-Click to open it's folder.",
    "sel_filter": "Project Filter: Start typing to narrow down the list by folder name or display title.",
    "sel_browse": "Add Project: Open a directory browser to select a new folder for use with CodeMerger.",
    "sel_remove": "Remove Entry: Take this project off your recent list. This does not delete any files on your computer.",

    # --- Paste Changes ---
    "paste_text": "Paste Area: Paste the full Markdown response from the AI here. CodeMerger will look for '--- File: `path` ---' tags.",
    "paste_apply": "Apply Changes: CodeMerger will parse the code, validate the paths, and overwrite your local files with the new content.",

    # --- New Profile Dialog ---
    "profile_name": "Profile Name: Enter a unique label for this configuration (e.g. 'Frontend' or 'Feature Name').",
    "profile_copy_files": "Clone Selection: If checked, the new profile will start with the exact same files selected in your current merge list.",
    "profile_copy_inst": "Clone Instructions: If checked, the new profile will inherit the current custom Intro and Outro instructions.",
    "profile_create": "Create Profile: Saves the new profile. New profiles have independent tracking for 'New Files' detected on disk.",

    # --- Project Starter ---
    "starter_nav_prev": "Previous Step: Go back to review or change settings in earlier steps.",
    "starter_nav_next": "Next Step: Proceed to the next phase. Validates current input before moving.",
    "starter_nav_reset": "Reset Step: Clear the current form or editor to start this specific step over.",
    "starter_header_save": "Save Config: Export your current project configuration (concept, stack, plan) to a JSON file.",
    "starter_header_load": "Load Config: Restore a previously saved project configuration.",
    "starter_header_clear": "Clear All: Completely reset the project starter to the beginning.",

    "starter_details_name": "Project Name: The name of your application. This will be used for the folder name and the README title.",
    "starter_details_base": "Base Project: Optionally select an existing folder to use as a reference. Useful for 'v2' rewrites or analyzing existing code.",

    "starter_concept_goal": "User Goal: Briefly describe what you want to build. This is the seed for the AI to generate the full concept.",
    "starter_concept_gen": (
        "Generate Concept: Copies a structured prompt to your clipboard. You must paste this into your LLM "
        "to generate the features list and user flow, then copy the result back here (preferably as Markdown)."
    ),
    "starter_concept_review": "Concept Editor: Review the generated concept. You can edit the text directly or use the 'Rewrite' button to refine it.",

    "starter_stack_exp": "Experience: List your preferred languages and tools. The AI will recommend a stack that matches your skills.",
    "starter_stack_gen": (
        "Generate Stack: Copies a prompt to your clipboard asking the AI to recommend the best technologies. "
        "Paste the AI's response back into the input field below."
    ),
    "starter_stack_edit": "Stack List: The final list of technologies. You can manually edit this list before generating the plan.",

    "starter_todo_gen": (
        "Generate Plan: Copies a prompt to your clipboard to create an implementation plan (TODO.md). "
        "Paste the AI's response back into the input field below."
    ),
    "starter_todo_review": "Plan Editor: Review the generated tasks. Ensure no critical features are missing.",

    "starter_gen_parent": "Parent Folder: The directory where your new project folder will be created.",
    "starter_gen_prompt": (
        "Master Prompt: Copies the final boilerplate instruction to your clipboard. Paste this into your LLM "
        "to generate the initial codebase, then copy the result and paste it into the response field below."
    ),
    "starter_gen_response": "Paste Response: Paste the AI's output here. The app will parse the file blocks and create the files.",
    "starter_gen_create": "Create Files: Write the generated files to disk and initialize the project.",
    "starter_gen_process": (
        "Process Response: Analyze the pasted LLM output. CodeMerger will look for the required "
        "segment tags to populate the editor for the next phase of review."
    ),

    "starter_seg_nav": "Navigation: Jump between different segments.",
    "starter_seg_signoff": "Sign Off: Lock this segment. When all segments are signed off, you can merge them into a single document.",
    "starter_seg_rewrite": "Rewrite: Provide a specific instruction to rewrite this segment and all unsigned segments.",
    "starter_seg_sync": "Sync: Propagate manual edits from this segment to other unsigned segments to keep the document consistent.",
    "starter_seg_questions": "Questions: See guiding questions to help you verify the quality of this segment.",
    "starter_seg_unlock": "Unlock to Edit: Releases the sign-off for the current segment, allowing you to make manual edits or include it in a 'Rewrite' operation.",
    "starter_seg_merge": "Merge Segments: Finalizes the individual sections and assembles them into a single Markdown document for the next phase of the project.",

    "starter_view_toggle": (
        "View Toggle: Switch between a stylized Markdown preview and a raw text editor for manual adjustments. "
        "Be careful: manual changes could create a conflict with other segments. Use 'Rewrite' to avoid this."
    ),

    # --- Rewrite Dialog ---
    "rewrite_instruction": (
        "Modification Instruction: Tell the AI what you want to change in the project drafts. "
        "For example: 'Change the primary data entity from Projects to Tasks' or 'Use a more formal tone'."
    ),
    "rewrite_copy_prompt": (
        "Generate Prompt: Compiles your instructions with the current drafts and locked segments. "
        "Clicking this copies the prompt to your clipboard for use with an LLM."
    ),
    "rewrite_response": (
        "Paste Area: Paste the LLM's updated segments here. Ensure the tags like <<SECTION: Name>> are preserved."
    ),
    "rewrite_apply": (
        "Apply Changes: Processes the response and updates the project starter drafts. Any change notes "
        "provided by the AI in <<NOTES>> tags will be displayed for your review."
    )
}