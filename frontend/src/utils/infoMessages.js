/**
 * User-facing documentation strings for Info Mode.
 */
export const INFO_MESSAGES = {
  "default": "Info mode active: hover over any interface element to see its purpose and usage details.",

  // Main Window
  "select_project": "Select a Project: Click to browse for a folder. CodeMerger will create a hidden .allcode file in that directory, that will store your file selections and project-specific instructions.",
  "project_name": "Project Name: This is the active project. Hover here to reveal the pen icon or double-click to set a custom title. Single-click to switch to another project (same as Select Project button).",
  "color_swatch": "Project Color: Pick a unique accent color for this project. This color is used in Compact Mode, to help you visually distinguish between multiple CodeMerger instances.",
  "folder_icon": "Folder Actions: Click to open the project in your File Explorer. Ctrl-click to copy the full path. Alt-click to open a Command Prompt (CMD) window directly in this directory.",
  "manage_files": "Edit Merge List: Open the dual-panel management window. This is where you decide exactly which files are relevant to your current task and in what order the AI should read them.",
  "instructions": "Define Instructions: Set a project-specific Intro and Outro. This text will be wrapped around your code whenever you use 'Copy with Instructions'.",
  "copy_code": "Copy Code Only (Ctrl+Shift+C): Merges all selected files with a standard prompt header. Useful for providing updated context to an LLM without repeating project goals. Ctrl-clicking the Adaptive Copy button in Compact mode also triggers this action.",
  "copy_with_instructions": "Copy Prompt with Instructions (Ctrl+C): Merges code and wraps it in your custom Intro/Outro. Strictly enforces 'No Code Truncation' rules. Ctrl-click to perform 'Copy Code Only'.",
  "paste_changes": "Paste Changes (Ctrl+V): Instantly applies code from your clipboard. Depending on your settings, this opens a review window or writes directly to disk. Ctrl-click to toggle the review behavior. Alt-click to open the manual paste window for raw text input.",
  "response_review": "AI Response Review: Opens the review window to see the most recently applied changes and associated AI commentary.",
  "cleanup": "Comment Cleanup: Copies a specialized prompt, that tells the AI to strip out it's own transient tags like [FIX] or [MODIFIED], while keeping structural logic comments.",
  "settings": "Application Settings: Configure application behavior.",
  "starter": "Project Starter: Launch a guided workflow for starting new projects. Assists you in creating a concept, tech stack, and step-by-step implementation plan using AI.",
  "info_toggle": "Info Mode: Toggles help panels on all application windows. Useful for learning how to work with CodeMerger.",
  "profile_nav": "Profile Switcher: Swap between different configurations for the same project. Each profile has its own file selection and instruction set.",
  "profile_add": "Add Profile: Create a new named configuration. Useful for separating different tasks like 'Backend' or 'Feature Development' within the same project.",
  "profile_delete": "Delete Profile: Remove the currently active profile. The 'Default' profile cannot be deleted.",

  // File Manager
  "fm_tree": "Available Files: Browse your project structure. Double-click files or folders to add them to the merge list. Green text indicates newly detected files. Purple text indicates files in your merge list that would normally be ignored by the Git or extension filters.",
  "fm_tree_action": "Merge Toggle: Adds or removes the currently selected files from the list.",
  "fm_list": "Merge Order: This list determines in what order the code will be presented to the AI. Files are merged from top to bottom. Click a file to select it for sorting or removal.",
  "fm_list_tools": "List Visibility: Toggle the display of full file paths or relative filenames in the merge list.",
  "fm_filter_git": "Git Filter: Toggle visibility of files listed in your .gitignore. When ON, ignored files are hidden.",
  "fm_filter_ext": "Filetype Filter: Toggle visibility of files not in your allowed extensions list. When ON, extra files are hidden.",
  "fm_filter_text": "Text Filter: Type to filter the tree and the merge list by filename.",
  "fm_tokens": "Total Tokens: A real-time estimate of context usage. As the grow count grows, the color changes from gray to yellow to red to warn you about LLM context limits.",
  "fm_order": "Order Request: Click to copy a prompt asking the AI for the 'optimal' file order.",
  "fm_tokens_item": "Token Stats: Shows the token count for this file. Text color shifts from gray to red as a file grows larger, helping you identify potential context bottlenecks. Ctrl-click to copy a breakup request (asking the AI to split the file). Alt-click to 'ignore' this file's tokens when calculating total context warnings.",
  "fm_sort_top": "Move to Top: Place the selected files at the beginning of the merge list.",
  "fm_sort_up": "Move Up: Shift the selected files one position higher in the order.",
  "fm_sort_down": "Move Down: Shift the selected files one position lower in the order.",
  "fm_sort_bottom": "Move to Bottom: Place the selected files at the end of the merge list.",
  "fm_sort_remove": "Remove: Take the selected files out of the merge list (does not delete files from disk).",
  "fm_add_all": "Add All: Add every file matching your current filters and search text to the merge list.",
  "fm_save": "Save Merge List: Commit your changes to the project's .allcode file and return to the main window.",
  "fm_remove_all": "Remove All: Clear the entire merge list for the current profile.",
  "fm_cancel": "Cancel: Exit the merge list editor without saving. Any additions, removals, or reordering performed since opening this window will be discarded.",
  "fm_close": "Close: Exit the merge list editor. No changes have been detected."
};