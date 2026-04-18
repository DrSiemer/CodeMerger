export const settingsInfo = {
  // Settings Window
  "set_app": "Various settings related to application behavior.",
  "set_app_new_file": "File Monitoring: Monitors your project folder for new files added since your last session. Disable this if you do not want new file warnings or do not want to spend resources on it.",
  "set_app_interval": "Check Interval: How frequently CodeMerger scans the disk for changes. Lower values are more responsive, but may impact performance on slow drives.",
  "set_app_secrets": "Secret Scanning: Uses 'detect-secrets' to look for API keys or private credentials before you copy. Enable this to prevent accidentally sharing sensitive data with the language model.",
  "set_app_feedback": "AI Response Review: Automatically open the response review window when wrapped sections can be found.",
  "set_app_compact": "Compact Mode: Automatically switches to the compact window whenever you minimize the main window. When enabled, the minimize button in the dashboard header switches behavior to minimize the application normally to the taskbar.",
  "set_app_updates": "Automatic Updates: Checks GitHub for a new version once per day.",
  "set_app_check_now": "Check Now: Manually trigger an update check to see if a newer version of CodeMerger is available on GitHub, bypassing the automatic daily timer.",

  "set_fm": "Settings that determine the behavior of the merge list editor.",
  "set_fm_tokens": "Token Counting: Calculates context usage based on the gpt-4 tokenizer. Disable this if you want to speed up file indexing in extremely large projects.",
  "set_fm_limit": "Context Limit: Set a target token count (e.g. 200000 for ChatGPT). The token count in the merge list editor will turn red if you exceed this.",
  "set_fm_threshold": "Add All Safety: A warning threshold for the 'Add All' button. Prevents accidentally adding a large amount of files to your merge list.",
  "set_fm_alert_threshold": "New File Warning: When applying AI changes that create new files, CodeMerger will skip the confirmation dialog if the count of new files is below this number. Deletions always trigger a warning.",

  "set_prompts": "Define your default intro/outro texts.",
  "set_prompt_merged": "Default Header: The text prepended when using 'Copy Code Only'. Best used for a short instruction, telling the AI to use the code as updated context.",
  "set_prompt_intro": "Global Intro: Generic greeting and mission statement. You can easily load this into a new project from the 'Instructions' window, to save time on project setup.",
  "set_prompt_outro": "Global Outro: Put code style instructions here. Ideal for enforcing formatting rules like 'Always end your output with a clear explanation' across all your AI interactions.",

  "set_starter": "Settings for the Project Starter tool.",
  "set_starter_folder": "Default Root: The parent directory where the Project Starter will create new project sub-folders by default.",

  "set_editor": "Overrule the default code editor to use when double-clicking files. Leave blank to use system defaults.",
  "set_editor_path": "Editor Path: Provide the path to your code editor's executable (e.g., sublime_text.exe). When set, double-clicking files in the editor opens them directly in this application.",

  "settings_cancel": "Cancel: Close the settings window and discard any modifications made during this session.",
  "settings_save": "Save Changes: Persist all modifications to the application configuration and update the interface immediately.",

  "filetypes": "Manage Filetypes: Define which file extensions CodeMerger is allowed to index. Double-click an entry in the list to enable or disable it globally.",
  "ft_list": "Indexed Types: Only files matching these extensions are scanned. Double-click to enable or disable.",
  "ft_action": "Active Toggle: Delete custom extensions or toggle the active status of bundled default extensions.",
  "ft_add": "Add Filetype: Type a new extension (e.g. .py or .js) and a short description to add it to the indexing list.",

  // New Filetypes Notification
  "ft_new_ok": "OK: Acknowledge the update and close the notification."
};