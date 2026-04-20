export const visualizerInfo = {
  // Architecture Explorer
  "viz_search": "Search Explorer: Filter the map to highlight specific files or architectural nodes based on their name or AI-generated description.",
  "viz_update_map": "Update Hierarchy: Regenerates the prompt to include your latest Merge List changes while instructing the LLM to preserve the existing architectural structure.",
  "viz_init_copy": "Copy Instructions: Get the prompt for your LLM. This includes your source code and a strict JSON output schema to ensure a valid architectural tree is generated.",
  "viz_init_paste": "Paste JSON response: Insert the raw output from the language model here. CodeMerger will validate the structure and file list before rendering.",
  "viz_init_visualize": "Initialize View: Parses the pasted JSON and constructs the interactive treemap layout.",
  "viz_explorer_tree": "Interactive Treemap: Visual representation of your system. Larger boxes represent more complex components. Click a node to dive deeper; use breadcrumbs to navigate back up.",
  "viz_leaf_list": "Component Files: Every file assigned to this specific architectural focused area. Click a file card to open it in your editor.",
  "viz_details": "Node Context: View the AI's explanation of this layer's role and logic. This sidebar updates dynamically based on your selection or hover.",
  "viz_details_copy": "Copy Subtree Code: Merges and copies the source code for all files contained within the currently selected architectural node."
};