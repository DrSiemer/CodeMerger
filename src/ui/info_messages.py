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
        "Copy Code Only (Ctrl+Shift+C): Merges all selected files with a standard prompt header. "
        "Useful for providing updated context to an LLM without repeating project goals."
    ),
    "copy_with_instructions": (
        "Copy with Instructions (Ctrl+C): Merges code and wraps it in your custom Intro/Outro. "
        "Strictly enforces 'No Code Truncation' rules, to ensure the AI returns full file updates."
    ),
    "paste_changes": (
        "Paste Changes (Ctrl+V): Open a review window to process AI responses. CodeMerger reads "
        "the Markdown and automatically writes suggested changes back to your local files."
    ),
    "cleanup": (
        "Comment Cleanup: Copies a specialized prompt, that tells the AI to strip out it's own "
        "transient tags like [FIX] or [MODIFIED], while keeping structural logic comments."
    ),
    "settings": (
        "Global Settings: Configure secret scanning, application updates, default text editor "
        "paths, and file monitoring intervals."
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
        "Total Tokens: A real-time estimate of context usage. As the count grows, the color changes "
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
    "fm_save": "Save and Close: Commit your changes to the project's .allcode file and return to the main window.",
    "fm_remove_all": "Remove All: Clear the entire merge list for the current profile.",

    # --- Settings Window ---
    "set_app": "Application Behavior: Toggle automatic updates, compact mode on minimize, and file system monitoring intervals.",
    "set_fm": "File Manager Settings: Configure the token counting engine and set thresholds for bulk 'Add All' operations.",
    "set_prompts": "Default Prompts: Define reusable intro/outro texts that you can quickly load into any project via 'Instructions'.",
    "set_starter": "Project Starter Config: Set a default root directory where the starter wizard will propose creating new projects.",
    "set_editor": "Default Editor: Choose a specific code editor to use when double-clicking files. Leave blank to use system defaults.",

    # --- Instructions Window ---
    "inst_intro": "Intro Instructions: This text is placed at the very top of your merged code block. Use it to set the immediate goal.",
    "inst_outro": "Outro Instructions: This text is placed at the bottom. Use it for stylistic rules or recurring constraints.",
    "inst_defaults": "Load Defaults: Click to wipe the current fields and load the global default prompts you defined in Settings.",
    "inst_save": "Save: Commit these instructions to the project's .allcode file. They are profile-specific.",

    # --- Filetype Manager ---
    "ft_list": "Indexed Types: Only files matching these extensions are scanned. Double-click an entry to enable or disable it.",
    "ft_action": "Contextual Action: Delete custom extensions or toggle the active status of bundled default extensions.",
    "ft_add": "Add Filetype: Type a new extension (e.g. .py or .js) and a short description to add it to the indexing list.",

    # --- Project Selector ---
    "sel_list": "Recent Projects: Quickly switch to a previous folder. Hover over an entry to see the full path or Ctrl-Click to open folder.",
    "sel_filter": "Project Filter: Start typing to narrow down the list by folder name or display title.",
    "sel_browse": "Add Project: Open a directory browser to select a new folder for use with CodeMerger.",
    "sel_remove": "Remove Entry: Take this project off your recent list. This does not delete any files on your computer.",

    # --- Paste Changes ---
    "paste_text": "Paste Area: Paste the full Markdown response from the AI here. CodeMerger will look for '--- File: `path` ---' tags.",
    "paste_apply": "Apply Changes: CodeMerger will parse the code, validate the paths, and overwrite your local files with the new content.",

    # --- New Profile Dialog ---
    "profile_name": "Profile Name: Enter a unique label for this configuration (e.g. 'Frontend' or 'Refactoring').",
    "profile_copy_files": "Clone Selection: If checked, the new profile will start with the exact same files selected in your current merge list.",
    "profile_copy_inst": "Clone Instructions: If checked, the new profile will inherit the current custom Intro and Outro instructions.",
    "profile_create": "Create Profile: Saves the new profile. New profiles have independent tracking for 'New Files' detected on disk."
}