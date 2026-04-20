<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { X, Network, Search, Info, RefreshCw, Trash2 } from "lucide-vue-next";
import { useAppState } from "../composables/useAppState";
import { useEscapeKey } from "../composables/useEscapeKey";
import {
  enrichNodes,
  computeLayouts,
  getAllFilesUnderNode,
  extractJSON,
  getColorForDomain
} from "../utils/visualizerUtils";

import VisualizerInit from "./visualizer/VisualizerInit.vue";
import VisualizerExplorer from "./visualizer/VisualizerExplorer.vue";
import VisualizerLeafFiles from "./visualizer/VisualizerLeafFiles.vue";
import VisualizerDetails from "./visualizer/VisualizerDetails.vue";

const emit = defineEmits(["close"]);
const {
  activeProject,
  getVisualizerPrompt,
  getVisualizerUpdatePrompt,
  copyVisualizerNodeCode,
  saveVisualizerMap,
  openFile,
  resizeWindow,
  statusMessage,
  getFileContent,
} = useAppState();

const viewState = ref("init"); // 'init' | 'visualizing' | 'updating'
const navPath = ref([]);
const hoveredNode = ref(null);
const highlightedLines = ref([]);
const isCodeLoading = ref(false);
const parseError = ref("");

const searchQuery = ref("");

// Memory for partial results to allow surgical amendments
const draftTree = ref(null);
const missingPathsList = ref([]);
const duplicateEntriesList = ref([]);

const currentNavNode = computed(() => navPath.value[navPath.value.length - 1] || null);
const displayNode = computed(() => hoveredNode.value || currentNavNode.value);

const diveIntoFile = (f) => {
  navPath.value.push({
    id: 'file-' + f.path,
    isFile: true,
    name: f.path.split('/').pop(),
    path: f.path,
    description: f.description,
    domain: currentNavNode.value?.domain,
    color: currentNavNode.value?.color
  });
};

watch(currentNavNode, async (node) => {
  if (node && node.isFile) {
    isCodeLoading.value = true;
    highlightedLines.value = [];

    const content = await getFileContent(node.path);
    if (content !== null && window.pywebview) {
      highlightedLines.value = await window.pywebview.api.get_syntax_highlight(content, node.path);
    }
    isCodeLoading.value = false;
  } else {
    highlightedLines.value = [];
  }
});

// Explicitly clear hover state on navigation to prevent "sticky" UI state
watch(navPath, () => {
  if (hoveredNode.value) {
    console.log(`[Viz State] Navigation change detected. Clearing hover: "${hoveredNode.value.name}"`);
    hoveredNode.value = null;
  }
}, { deep: true });

// Contextual navigation logic: Allow copying any node except the global root or specific files, provided we aren't hovering over a preview
const canCopy = computed(() => {
  const navNode = currentNavNode.value;
  if (!navNode || navNode.isFile) return false;

  // Root check: navPath[0] is the root. Copying is allowed for any level below that.
  const isNotRoot = navPath.value.length > 1;

  // Visibility check: Only show button if we are NOT hovering over a neighbor/child (previewing)
  const result = isNotRoot && !hoveredNode.value;

  return result;
});

useEscapeKey(() => emit("close"));

const mapSyncState = computed(() => {
  if (!activeProject.visualizerMap || !activeProject.visualizerMap.file_hashes) return 'SYNCED';
  const mapHashes = activeProject.visualizerMap.file_hashes;
  const currentFiles = activeProject.selectedFiles || [];
  const mapPaths = Object.keys(mapHashes);
  const currentPaths = currentFiles.map(f => f.path);

  if (mapPaths.length !== currentPaths.length || mapPaths.some(p => !currentPaths.includes(p)) || currentPaths.some(p => !mapPaths.includes(p))) {
      return 'PATHS_CHANGED';
  }
  if (currentFiles.some(f => (f.hash || null) !== (mapHashes[f.path] || null))) {
      return 'CONTENT_CHANGED';
  }
  return 'SYNCED';
});

const syncMessage = computed(() => {
  if (mapSyncState.value === 'PATHS_CHANGED') return 'Map is out of sync (files were added or removed).';
  if (mapSyncState.value === 'CONTENT_CHANGED') return 'Map is somewhat out of sync (files were modified).';
  return '';
});

onMounted(async () => {
  await resizeWindow(1100, 800);

  // Ensure Pygments CSS is available in the modal context
  if (window.pywebview && !document.getElementById('pygments-css')) {
    const css = await window.pywebview.api.get_pygments_style();
    const style = document.createElement('style');
    style.id = 'pygments-css';
    style.innerHTML = css;
    document.head.appendChild(style);
  }

  if (activeProject.visualizerMap?.tree) {
    loadTree(activeProject.visualizerMap.tree);
    viewState.value = "visualizing";
  }
});

const moveRootFilesToMisc = (root) => {
  // Aggressively move root-level files into a standard peer-level category
  if (root.files && root.files.length > 0) {
    if (!root.children) root.children = [];

    let miscNode = root.children.find(c => c.name === 'Miscellaneous Artifacts');
    if (!miscNode) {
      miscNode = {
        name: 'Miscellaneous Artifacts',
        description: 'Project metadata, root configurations, and top-level documentation.',
        domain: 'infrastructure',
        children: [],
        files: []
      };
      // Insert at the beginning so it's easy to find
      root.children.unshift(miscNode);
    }

    miscNode.files.push(...root.files);
    // Explicitly delete the files key from the root container to ensure it only has folders
    delete root.files;
  }
};

const nukeVisualizerMap = async () => {
  if (confirm("Are you sure you want to delete all Architecture Explorer data for this profile?\n\nThis will reset the map and you will need to generate it again. This cannot be undone.")) {
    const success = await saveVisualizerMap(null);
    if (success) {
      viewState.value = "init";
      navPath.value = [];
      activeProject.visualizerMap = null;
      statusMessage.value = "Explorer data cleared.";
    }
  }
};

const loadTree = (root) => {
  const idTracker = { val: 0 };

  // Ensure root-level files are moved to a 'Miscellaneous' node for clean treemap display
  moveRootFilesToMisc(root);

  const reEnrich = (node, parentDomain = 'default') => {
    node.id = ++idTracker.val;
    node.domain = node.domain || parentDomain;
    node.color = getColorForDomain(node.domain);

    // Defensive check to ensure files list exists and items are objects
    if (!node.files) node.files = [];
    node.files = node.files.map(f => typeof f === 'string' ? { path: f, description: '' } : f);

    node.weight = node.files.length || 1;
    if (node.children?.length) {
      node.weight += node.children.reduce((acc, c) => acc + reEnrich(c, node.domain), 0);
    }
    return node.weight;
  };
  reEnrich(root);
  computeLayouts(root);
  navPath.value = [root];
};

const processRawResponse = async (raw) => {
  parseError.value = "";
  try {
    const data = extractJSON(raw);

    let root;
    // Check if this is an amendment response
    if (data.amendments) {
      const sourceTree = draftTree.value || activeProject.visualizerMap?.tree;
      if (!sourceTree) {
        throw new Error("No existing tree to amend. Please paste a full hierarchy first.");
      }
      root = JSON.parse(JSON.stringify(sourceTree));
      const { findAndAddFileToNode, removeFileFromTree } = await import("../utils/visualizerUtils");

      if (Array.isArray(data.amendments.remove)) {
        data.amendments.remove.forEach(path => {
          removeFileFromTree(root, path);
        });
      }

      const addList = Array.isArray(data.amendments.add) ? data.amendments.add : (Array.isArray(data.amendments) ? data.amendments : []);
      addList.forEach(item => {
        const added = findAndAddFileToNode(root, item.path, item.parent, item.description);
        if (!added) {
          // Dynamic Node Creation: If parent doesn't exist, create it as a new root category
          if (!root.children) root.children = [];
          let newNode = root.children.find(c => c.name.toLowerCase() === item.parent.toLowerCase());
          if (!newNode) {
            newNode = {
              name: item.parent,
              description: 'Newly categorized artifacts.',
              domain: 'default',
              children: [],
              files: []
            };
            root.children.push(newNode);
          }
          newNode.files.push({ path: item.path, description: item.description });
        }
      });
    } else {
      // Full tree response
      root = Array.isArray(data)
        ? (data.length === 1 ? data[0] : { name: 'System Architecture', description: 'Complete project structure', domain: 'default', children: data, files: [] })
        : data;
    }

    // Ensure the System root contains ONLY children (folders)
    moveRootFilesToMisc(root);

    const idTracker = { val: 0 };
    const reEnrich = (node, parentDomain = 'default') => {
      node.id = ++idTracker.val;
      node.domain = node.domain || parentDomain;
      node.color = getColorForDomain(node.domain);

      if (!node.files) node.files = [];
      node.files = node.files.map(f => typeof f === 'string' ? { path: f, description: '' } : f);

      node.weight = node.files.length || 1;
      if (node.children?.length) {
        node.weight += node.children.reduce((acc, c) => acc + reEnrich(c, node.domain), 0);
      }
      return node.weight;
    };
    reEnrich(root);

    const parsedPaths = getAllFilesUnderNode(root);
    const currentPaths = activeProject.selectedFiles.map(f => f.path);
    const missing = currentPaths.filter(p => !parsedPaths.includes(p));
    const unknown = parsedPaths.filter(p => !currentPaths.includes(p));
    const dupes = parsedPaths.filter((item, index) => parsedPaths.indexOf(item) !== index);

    if (missing.length || unknown.length || dupes.length) {
      // Save the current partial result as a draft to allow for amendments
      draftTree.value = root;
      missingPathsList.value = missing;
      duplicateEntriesList.value = [...new Set(dupes)];

      let errs = [];
      if (missing.length) errs.push(`Missing Files:\n${JSON.stringify(missing.sort(), null, 2)}`);
      if (unknown.length) errs.push(`Unknown Files:\n${JSON.stringify(unknown.sort(), null, 2)}`);
      if (dupes.length) errs.push(`Duplicate Entries Found:\n${JSON.stringify(duplicateEntriesList.value.sort(), null, 2)}`);
      throw new Error(errs.join('\n\n'));
    }

    computeLayouts(root);
    draftTree.value = null; // Clear draft on success
    const file_hashes = {};
    activeProject.selectedFiles.forEach(f => { file_hashes[f.path] = f.hash || null; });

    await saveVisualizerMap({ tree: root, file_hashes });
    loadTree(root);
    viewState.value = "visualizing";
    if (viewState.value === 'updating') statusMessage.value = "Visualizer map successfully updated.";
  } catch (err) {
    parseError.value = err.message;
  }
};

const handleCopyPrompt = async () => {
  const isUpdateMode = viewState.value === 'updating';

  if (isUpdateMode && activeProject.visualizerMap) {
    // Identify specific path diffs to request an AMENDMENT prompt
    const mapHashes = activeProject.visualizerMap.file_hashes || {};
    const mapPaths = Object.keys(mapHashes);
    const currentPaths = activeProject.selectedFiles.map(f => f.path);

    const missingPaths = currentPaths.filter(p => !mapPaths.includes(p));
    const obsoletePaths = mapPaths.filter(p => !currentPaths.includes(p));

    // Strip UI-specific properties (id, layout, etc) before sending current tree to LLM
    const prevJson = JSON.stringify(activeProject.visualizerMap.tree, (k, v) =>
      ['id', 'layout', 'color', 'weight'].includes(k) ? undefined : v, 2
    );

    const prompt = await getVisualizerUpdatePrompt(prevJson, missingPaths, obsoletePaths);
    if (prompt) {
      await navigator.clipboard.writeText(prompt);
    }
  } else {
    // Standard Full Generation for uninitialized maps or fallback
    const prompt = await getVisualizerPrompt();
    if (prompt) {
      await navigator.clipboard.writeText(prompt);
    }
  }
};

const handleCopyAmendPrompt = async () => {
  const missingList = missingPathsList.value.length > 0 ? missingPathsList.value.map(p => `- ${p}`).join('\n') : "None";
  const duplicateList = duplicateEntriesList.value.length > 0 ? duplicateEntriesList.value.map(p => `- ${p}`).join('\n') : "None";

  const prompt = `I am building an Architecture Explorer and your previous response was incomplete or contained redundancies.

**Missing Files to Categorize:**
${missingList}

**Duplicate Entries Found:**
${duplicateList}

**Instructions:**
1. Categorize the 'Missing Files' into the architectural structure we just discussed.
2. For each missing file, provide the 'parent' node name where it should be placed.
3. For 'Duplicate Entries', identify which redundant instances should be REMOVED to satisfy the 'One File, One Node' policy.
4. Provide a rich description for each added file (2-4 sentences).

**Output Format:**
Return ONLY a raw JSON object with an 'amendments' key:
{
  "amendments": {
    "add": [
      {
        "path": "path/to/missing_file.ext",
        "parent": "Existing or New Node Name",
        "description": "Detailed explanation of what this file does."
      }
    ],
    "remove": [
      "path/to/duplicate_to_delete.ext"
    ]
  }
}`;

  await navigator.clipboard.writeText(prompt);
  statusMessage.value = "Copied amend prompt to clipboard.";
};

const copyCorrectionPrompt = async () => {
  const prompt = `The JSON you provided is invalid or incomplete. You have violated the ZERO OMISSION POLICY. Your previous response was incomplete.\n\nTo fix this, you must output the COMPLETE, functional JSON object again, ensuring it contains EVERY file from the merge list.\n\nVALIDATION ERRORS TO FIX:\n${parseError.value}`;
  await navigator.clipboard.writeText(prompt);
  statusMessage.value = "Copied correction prompt to clipboard.";
};

const handleCopyNodeCode = async (node) => {
  const paths = getAllFilesUnderNode(node);
  if (paths.length) statusMessage.value = await copyVisualizerNodeCode(paths);
};
</script>

<template>
  <div id="visualizer-modal" class="absolute inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
    <div class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[90vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar shrink-0">
        <div class="flex items-center space-x-3 text-white shrink-0">
          <Network class="w-6 h-6 text-cm-blue" />
          <div class="flex items-baseline space-x-2">
            <h2 class="text-xl font-bold">Architecture Explorer</h2>
            <span class="text-gray-500 text-sm font-medium">/ {{ activeProject.name }}</span>
          </div>
        </div>

        <div class="flex items-center space-x-6 flex-grow justify-end max-w-2xl px-6">
            <div v-if="viewState === 'visualizing'" class="relative w-full max-w-sm">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input v-model="searchQuery" v-info="'viz_search'" type="text" placeholder="Search files or descriptions..." class="w-full bg-cm-input-bg border border-gray-600 rounded-full py-1.5 pl-10 pr-10 text-sm text-white focus:border-cm-blue outline-none transition-all shadow-inner" />
                <button v-if="searchQuery" @click="searchQuery = ''" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white">
                    <X class="w-4 h-4" />
                </button>
            </div>
            <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors" title="Close visualizer">
                <X class="w-6 h-6" />
            </button>
        </div>
      </div>

      <!-- Main Body -->
      <div class="flex-grow flex flex-col min-h-0 bg-cm-dark-bg">
        <VisualizerInit
          v-if="viewState === 'init' || viewState === 'updating'"
          :mode="viewState"
          :parse-error="parseError"
          @copy-prompt="handleCopyPrompt(viewState === 'updating')"
          @copy-correction="copyCorrectionPrompt"
          @copy-amend="handleCopyAmendPrompt"
          @parse="processRawResponse"
          @cancel="viewState = 'visualizing'"
        />

        <VisualizerExplorer
          v-else
          :nav-path="navPath"
          :search-query="searchQuery"
          @nav-to="(idx) => navPath.splice(idx + 1)"
          @dive-in="(node) => navPath.push(node)"
          @node-hover="(node) => hoveredNode = node"
        >
          <!-- Center Panel Code Viewer -->
          <div v-if="currentNavNode?.isFile" class="absolute inset-0 m-2 bg-[#1e1e1e] border border-gray-800 rounded-xl shadow-inner overflow-hidden flex flex-col">
            <div v-if="isCodeLoading" class="flex-grow flex items-center justify-center">
               <span class="text-gray-500 italic font-mono">Loading code...</span>
            </div>
            <div v-else class="flex-grow overflow-auto p-4 custom-scrollbar highlight">
              <table class="w-full border-collapse font-mono text-[12px] leading-relaxed selectable">
                <tbody>
                  <tr v-for="(line, idx) in highlightedLines" :key="idx" class="group">
                    <td class="w-10 pr-4 text-right text-gray-600 select-none border-r border-gray-800/50 group-hover:text-gray-400">{{ idx + 1 }}</td>
                    <td class="pl-4 whitespace-pre" v-html="line || ' '"></td>
                  </tr>
                </tbody>
              </table>
              <div v-if="highlightedLines.length === 0" class="p-6 text-gray-500 italic">File is empty or could not be read.</div>
            </div>
          </div>

          <VisualizerLeafFiles
            v-else-if="!currentNavNode?.children?.length"
            :node="currentNavNode"
            :search-query="searchQuery"
            @open-file="openFile"
            @select-file="diveIntoFile"
          />

          <template #details>
            <VisualizerDetails
              :display-node="displayNode"
              :can-copy="canCopy"
              @open-file="openFile"
              @copy-code="handleCopyNodeCode"
            />
          </template>
        </VisualizerExplorer>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-between items-center shrink-0">
        <div class="flex items-center">
            <div v-if="viewState === 'visualizing'" class="flex items-center space-x-4">
              <button @click="viewState = 'updating'" v-info="'viz_update_map'" class="bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 px-4 py-1.5 rounded text-sm font-bold shadow-sm transition-colors shrink-0 flex items-center">
                <RefreshCw class="w-4 h-4 mr-2" />
                Update Map
              </button>
              <div v-if="mapSyncState !== 'SYNCED'" class="flex items-center space-x-2 text-blue-300/80 mr-4">
                <Info class="w-4 h-4 shrink-0" />
                <span class="text-sm font-medium">{{ syncMessage }}</span>
              </div>

              <button @click="nukeVisualizerMap" class="text-gray-500 hover:text-red-400 transition-colors p-2" title="Clear all map data and start fresh">
                <Trash2 class="w-5 h-5" />
              </button>
            </div>
        </div>
        <button @click="emit('close')" class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-8 rounded transition-colors text-sm shrink-0">Close Map</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #444; border-radius: 3px; }
</style>