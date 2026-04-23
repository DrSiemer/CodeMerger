export const mainInfo = {
  // Main Window
  "select_project": "Select a Project: Click to browse for a folder. CodeMerger will create a hidden .codemerger folder in that directory, that will store your file selections and project-specific instructions.",
  "project_name": "Project Name: This is the active project. Hover here to reveal the pen icon or double-click to set a custom title. Single-click to switch to another project (same as Select Project button).",
  "color_swatch": "Project Color: Pick a unique accent color for this project. This color is used in Compact Mode, to help you visually distinguish between multiple CodeMerger instances.",
  "minimize_to_taskbar": "Minimize without showing Compact Mode: Click to minimize the application to the taskbar. This action ignores your global 'Compact Mode' setting for this click.",
  "minimize_to_compact": "Minimize to Compact Mode: Click to minimize the application and show the Compact Mode panel. This action ignores your global 'Compact Mode' setting for this click.",
  "folder_icon": "Folder Actions: Click to open the project in your File Explorer. Ctrl-click to copy the full path. Alt-click to open a Command Prompt (CMD) window directly in this directory.",
  "manage_files": "Edit Merge List: Open the dual-panel management window. This is where you decide exactly which files are relevant to your current task and in what order the AI should read them.",
  "instructions": "Define Instructions: Set a project-specific Intro and Outro. This text will be wrapped around your code whenever you use 'Copy with Instructions'.",
  "copy_code": "Copy Code Only (Ctrl+Shift+C): Merges all selected files with a standard prompt header. Useful for providing updated context to an LLM without repeating project goals. Ctrl-clicking the Adaptive Copy button in Compact mode also triggers this action.",
  "copy_with_instructions": "Copy Prompt with Instructions (Ctrl+C): Merges code and wraps it in your custom Intro/Outro. Strictly enforces 'No Code Truncation' rules. Ctrl-click to perform 'Copy Code Only'.",
  "paste_changes": "Paste Changes (Ctrl+V): Instantly applies code from your clipboard. Depending on your settings, this opens a review window or writes directly to disk. Ctrl-click to toggle the review behavior. Alt-click to open the manual paste window for raw text input.",
  "response_review": "AI Response Review: Opens the review window to see the most recently applied changes and associated AI commentary.",
  "useful_prompts": "Useful Prompts: Access a menu of specialized prompts for your LLM, such as Comment Cleanup, finding Dead Weight, or DRYing up your code.",
  "fast_apply_toggle": "Fast Apply: Toggles Surgical Diff mode. When ON, the AI is instructed to output only specific ORIGINAL/UPDATED blocks rather than full files, saving tokens and speed. Turn OFF if using weaker models that struggle with patching.",
  "settings": "Application Settings: Configure application behavior.",
  "starter": "Project Starter: Launch a guided workflow for starting new projects. Assists you in creating a concept, tech stack, and step-by-step implementation plan using AI.",
  "visualizer": "Architecture Explorer: Explore a semantic map of your project. This tool uses AI to organize your Merge List into logical layers, making it easier to navigate complex codebases and copy code for specific features.",
  "info_toggle": "Info Mode: Toggles help panels on all application windows. Useful for learning how to work with CodeMerger.",
  "profile_nav": "Profile Switcher: Swap between different configurations for the same project. Each profile has its own file selection and instruction set.",
  "profile_add": "Add Profile: Create a new named configuration. Useful for separating different tasks like 'Backend' or 'Feature Development' within the same project.",
  "profile_delete": "Delete Profile: Remove the currently active profile. The 'Default' profile cannot be deleted.",

  // New Profile Dialog
  "profile_name": "Profile Name: Enter a unique label for this configuration (e.g. 'Frontend' or 'Feature Name').",
  "profile_copy_files": "Clone Selection: If checked, the new profile will start with the exact same files selected in your current merge list.",
  "profile_copy_inst": "Clone Instructions: If checked, the new profile will inherit the current custom Intro and Outro instructions.",
  "profile_create": "Create Profile: Saves the new profile. New profiles have independent tracking for 'New Files' detected on disk.",
  "profile_cancel": "Cancel: Discard the new profile details and return to the main dashboard without making any changes.",

  // Project Selector
  "sel_list": "Recent Projects: Quickly switch to another CodeMerger project. Hover over an entry to see the full path and Ctrl-Click to open it's folder.",
  "sel_filter": "Project Filter: Start typing to narrow down the list by folder name or display title.",
  "sel_browse": "Add Project: Open a directory browser to select a new folder for use with CodeMerger.",
  "sel_remove": "Remove Entry: Take this project off your recent list. This does not delete any files on your computer.",

  // Instructions Window
  "inst_intro": "Intro Instructions: This text is placed at the very top of your merged code block. Use it to introduce your project.",
  "inst_outro": "Outro Instructions: This text is placed at the bottom. Use it for code style rules or recurring constraints.",
  "inst_defaults": "Load Defaults: Click to wipe the current fields and load the global default prompts you defined in the Settings.",
  "inst_save": "Save: Commit these instructions to the project's .codemerger configuration. They are profile-specific."
};