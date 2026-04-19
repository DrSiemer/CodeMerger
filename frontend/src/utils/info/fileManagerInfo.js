export const fileManagerInfo = {
  // File Manager
  "fm_tree": "Available Files: Browse your project structure. Click a checkbox to toggle selection, or Ctrl+Click a filename to open the file in your editor. Green text indicates newly detected files.",
  "fm_tree_action": "Merge Toggle: Adds or removes the currently selected files from the list.",
  "fm_list": "Merge Order: This list determines in what order the code will be presented to the AI. Files are merged from top to bottom. Click a file to select it for sorting or removal.",
  "fm_list_tools": "List Visibility: Toggle the display of full file paths or relative filenames in the merge list.",
  "fm_visibility_toggle": "File Visibility: Click to manage filters for hidden files (Git ignored) and allowed file extensions.",
  "fm_filter_git": "Git Filter: Toggle visibility of files listed in your .gitignore. When ON, ignored files are hidden.",
  "fm_filter_ext": "Filetype Filter: Toggle visibility of files not in your allowed extensions list. When ON, extra files are hidden.",
  "fm_filter_text": "Text Filter: Type to filter the tree and the merge list by filename.",
  "fm_tokens": "Total Tokens: A real-time estimate of context usage. As the grow count grows, the color changes from gray to yellow to red to warn you about LLM context limits.",
  "fm_order": "Order Request: Click to copy a prompt asking for the optimal file order. Ctrl-click to directly apply a new order list from your clipboard.",
  "fm_tokens_item": "Token Stats: Shows the token count for this file. Text color shifts from gray to red as a file grows larger. Ctrl-click to copy a breakup request. Alt-click to 'ignore' this file's tokens in coloring warnings.",
  "fm_list_item": "Merge Item: Double-click to open this file in your editor. Click to select for sorting, which also scrolls the Available Files tree to this item with a subtle highlight.",
  "fm_sort_top": "Move to Top: Place the selected files at the beginning of the merge list.",
  "fm_sort_up": "Move Up: Shift the selected files one position higher in the order.",
  "fm_sort_down": "Move Down: Shift the selected files one position lower in the order.",
  "fm_sort_bottom": "Move to Bottom: Place the selected files at the end of the merge list.",
  "fm_sort_remove": "Delete: Take the selected files out of the merge list (does not delete files from disk).",
  "fm_add_all": "Add All: Add every file matching your current filters and search text to the merge list.",
  "fm_save": "Save Merge List: Commit your changes to the project's .allcode file and return to the main window.",
  "fm_cancel": "Cancel: Exit the merge list editor without saving. Any additions, removals, or reordering performed since opening this window will be discarded.",
  "fm_close": "Close: Exit the merge list editor. No changes have been detected."
};