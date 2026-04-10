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
  "profile_delete": "Delete Profile: Remove the currently active profile. The 'Default' profile cannot be deleted."
};