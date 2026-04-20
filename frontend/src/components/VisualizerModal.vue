<script setup>
import { ref, onMounted, computed, markRaw, watch, nextTick } from "vue";
import {
  X,
  Network,
  Copy,
  Check,
  FileCode,
  ClipboardPaste,
  AlertTriangle,
  Search,
} from "lucide-vue-next";
import { useAppState } from "../composables/useAppState";
import { useEscapeKey } from "../composables/useEscapeKey";

const emit = defineEmits(["close"]);
const {
  activeProject,
  getVisualizerPrompt,
  copyVisualizerNodeCode,
  resizeWindow,
  statusMessage,
} = useAppState();

const viewState = ref("init"); // 'init' | 'visualizing'
const initContainerRef = ref(null);
const errorBlockRef = ref(null);
const promptResponse = ref("");
const treeData = ref([]);
const activeNode = ref(null);
const expandedNodes = ref(new Set());
const isPromptCopied = ref(false);
const parseError = ref("");
const searchQuery = ref("");

watch(parseError, (newVal) => {
  if (newVal) {
    nextTick(() => {
      // Small timeout ensures the element is rendered and layout is calculated in Edge/Chromium
      setTimeout(() => {
        if (errorBlockRef.value) {
          errorBlockRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 50);
    });
  }
});

const zoomPath = ref([]);
const hoveredNode = ref(null);

const currentZoomNode = computed(() => {
  if (zoomPath.length === 0) return null;
  return zoomPath.value[zoomPath.value.length - 1];
});

const displayNode = computed(() => hoveredNode.value || currentZoomNode.value);

const nodeHasMatch = (node, query) => {
  if (!query) return true;
  const q = query.toLowerCase();

  // Direct file match
  if (node.files && node.files.some(f =>
    f.path.toLowerCase().includes(q) ||
    (f.description && f.description.toLowerCase().includes(q))
  )) {
    return true;
  }

  // Recursive child match
  if (node.children) {
    return node.children.some(child => nodeHasMatch(child, query));
  }

  return false;
};

const processedLeafFiles = computed(() => {
  const node = currentZoomNode.value;
  if (!node || !node.files) return [];

  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return node.files;

  return [...node.files].sort((a, b) => {
    const aMatch = a.path.toLowerCase().includes(query) || (a.description && a.description.toLowerCase().includes(query));
    const bMatch = b.path.toLowerCase().includes(query) || (b.description && b.description.toLowerCase().includes(query));
    if (aMatch && !bMatch) return -1;
    if (!aMatch && bMatch) return 1;
    return 0;
  });
});

const highlightMatch = (text, query) => {
  if (!query || !text) return text;
  const parts = text.split(new RegExp(`(${query})`, 'gi'));
  return parts.map(part =>
    part.toLowerCase() === query.toLowerCase()
      ? `<mark class="bg-yellow-500/30 text-yellow-100 rounded px-0.5">${part}</mark>`
      : part
  ).join('');
};

useEscapeKey(() => emit("close"));

onMounted(async () => {
  await resizeWindow(1100, 800);
});

const handleCopyPrompt = async () => {
  const prompt = await getVisualizerPrompt();
  if (prompt) {
    await navigator.clipboard.writeText(prompt);
    isPromptCopied.value = true;
    setTimeout(() => {
      isPromptCopied.value = false;
    }, 2000);
  }
};

const copyCorrectionPrompt = async () => {
  const prompt = `The JSON you provided is invalid or incomplete. Please fix the following errors and output the full JSON again:\n\n${parseError.value}`;
  await navigator.clipboard.writeText(prompt);
  statusMessage.value = "Copied correction prompt to clipboard.";
};

// Layout Algorithm Core
let nodeIdCounter = 0;

const getColorForDomain = (domain) => {
  const d = (domain || '').toLowerCase();
  if (d.includes('front')) return '#0D8319'; // cm-green
  if (d.includes('back') || d.includes('api') || d.includes('server')) return '#0078D4'; // cm-blue
  if (d.includes('lib') || d.includes('util') || d.includes('core') || d.includes('shared')) return '#BB86FC'; // purple
  if (d.includes('infra') || d.includes('deploy') || d.includes('config') || d.includes('db')) return '#DE6808'; // orange
  return '#4B5563'; // gray-600 default
};

const enrichNodes = (nodes, parentDomain = 'default') => {
  let totalWeight = 0;
  nodes.forEach(node => {
    node.id = ++nodeIdCounter;
    node.domain = node.domain || parentDomain;
    node.color = getColorForDomain(node.domain);
    node.files = (node.files || []).map(f => typeof f === 'string' ? { path: f, description: '' } : f);
    node.weight = node.files.length || 1;

    if (node.children && node.children.length > 0) {
      node.weight += enrichNodes(node.children, node.domain);
    }
    totalWeight += node.weight;
  });
  return totalWeight;
};

const computeLayouts = (node) => {
  if (!node.children || node.children.length === 0) return;
  const sortedChildren = [...node.children].sort((a, b) => b.weight - a.weight);

  let cx = 0, cy = 0, cw = 100, ch = 100;
  let total = sortedChildren.reduce((s, c) => s + c.weight, 0);

  sortedChildren.forEach((child, index) => {
    let ratio = child.weight / total;
    if (index === sortedChildren.length - 1) {
      child.layout = { x: cx, y: cy, w: cw, h: ch };
    } else {
      if (cw > ch) {
        let splitW = cw * ratio;
        child.layout = { x: cx, y: cy, w: splitW, h: ch };
        cx += splitW;
        cw -= splitW;
      } else {
        let splitH = ch * ratio;
        child.layout = { x: cx, y: cy, w: cw, h: splitH };
        cy += splitH;
        ch -= splitH;
      }
    }
    total -= child.weight;
    if (child.children && child.children.length > 0) {
       computeLayouts(child);
    }
  });
};

const getRectStyle = (layout) => {
  if (!layout) return {};
  return {
    left: `calc(${layout.x}% + 4px)`,
    top: `calc(${layout.y}% + 4px)`,
    width: `calc(${layout.w}% - 8px)`,
    height: `calc(${layout.h}% - 8px)`
  };
};

const getAllFilesUnderNode = (node) => {
  let paths = [...(node.files || [])].map(f => f.path);
  if (node.children) {
    node.children.forEach((child) => {
      paths = [...paths, ...getAllFilesUnderNode(child)];
    });
  }
  return paths;
};

const parseResponse = () => {
  parseError.value = "";
  try {
    let raw = promptResponse.value.trim();
    const startIdx = raw.indexOf("[") !== -1 ? Math.min(raw.indexOf("["), raw.indexOf("{")) : raw.indexOf("{");
    const endIdx = raw.lastIndexOf("]") !== -1 ? Math.max(raw.lastIndexOf("]"), raw.lastIndexOf("}")) : raw.lastIndexOf("}");
    if (startIdx === -1 || endIdx === -1) throw new Error("JSON structure not found.");

    const jsonStr = raw.substring(startIdx, endIdx + 1);

    let data;
    try {
      data = JSON.parse(jsonStr);
    } catch (e) {
      throw new Error("Invalid JSON syntax: " + e.message);
    }

    let root;
    if (Array.isArray(data)) {
       if (data.length === 1) root = data[0];
       else root = { name: 'System Architecture', description: 'Complete project structure', domain: 'default', children: data, files: [] };
    } else {
       root = data;
    }

    nodeIdCounter = 0;
    root.id = ++nodeIdCounter;
    root.domain = root.domain || 'default';
    root.color = getColorForDomain(root.domain);
    root.files = (root.files || []).map(f => typeof f === 'string' ? { path: f, description: '' } : f);
    root.weight = root.files.length || 1;

    if (root.children && root.children.length > 0) {
      root.weight += enrichNodes(root.children, root.domain);
    }

    // STRICT FILE VALIDATION
    const parsedPaths = getAllFilesUnderNode(root);
    const currentPaths = activeProject.selectedFiles.map(f => f.path);

    const currentPathsSet = new Set(currentPaths);
    const parsedPathsSet = new Set(parsedPaths);

    const missingFiles = [...currentPathsSet].filter(p => !parsedPathsSet.has(p));
    const unknownFiles = [...parsedPathsSet].filter(p => !currentPathsSet.has(p));
    const duplicates = parsedPaths.filter((item, index) => parsedPaths.indexOf(item) !== index);

    if (missingFiles.length || unknownFiles.length || duplicates.length) {
      let errorParts = [];
      if (missingFiles.length) {
        errorParts.push(`Missing Files:\n${JSON.stringify(missingFiles.sort(), null, 2)}`);
      }
      if (unknownFiles.length) {
        errorParts.push(`Unknown Files:\n${JSON.stringify(unknownFiles.sort(), null, 2)}`);
      }
      if (duplicates.length) {
        errorParts.push(`Duplicate Entries Found:\n${JSON.stringify([...new Set(duplicates)].sort(), null, 2)}`);
      }
      throw new Error(errorParts.join('\n\n'));
    }

    computeLayouts(root);

    zoomPath.value = [root];
    viewState.value = "visualizing";
  } catch (err) {
    parseError.value = err.message;
    promptResponse.value = "";
  }
};

const handleCopyNodeCode = async (node) => {
  const paths = getAllFilesUnderNode(node);
  if (paths.length === 0) {
    statusMessage.value = "No files attached to this node or its children.";
    return;
  }
  const result = await copyVisualizerNodeCode(paths);
  statusMessage.value = result;
};
</script>

<template>
  <div
    id="visualizer-modal"
    class="absolute inset-0 bg-black/70 flex items-center justify-center z-50 p-6"
  >
    <div
      class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[90vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden"
    >
      <!-- Header -->
      <div
        class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar"
      >
        <div class="flex items-center space-x-3 text-white shrink-0">
          <Network class="w-6 h-6 text-cm-blue" />
          <h2 class="text-xl font-bold">Architecture Explorer</h2>
          <span class="text-gray-500 text-sm font-medium"
            >/ {{ activeProject.name }}</span
          >
        </div>

        <div class="flex items-center space-x-6 flex-grow justify-end max-w-2xl px-6">
            <!-- Search Bar -->
            <div v-if="viewState === 'visualizing'" class="relative w-full max-w-sm">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Search files or descriptions..."
                    class="w-full bg-cm-input-bg border border-gray-600 rounded-full py-1.5 pl-10 pr-10 text-sm text-white focus:border-cm-blue outline-none transition-all shadow-inner"
                />
                <button
                    v-if="searchQuery"
                    @click="searchQuery = ''"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                >
                    <X class="w-4 h-4" />
                </button>
            </div>

            <button
                @click="emit('close')"
                class="text-gray-400 hover:text-white transition-colors"
                title="Close visualizer"
            >
                <X class="w-6 h-6" />
            </button>
        </div>
      </div>

      <!-- Main Body -->
      <div class="flex-grow flex flex-col min-h-0 bg-cm-dark-bg">
        <!-- STEP 1: Initialization -->
        <div
          v-if="viewState === 'init'"
          ref="initContainerRef"
          class="flex-grow flex flex-col items-center p-12 max-w-2xl mx-auto space-y-8 overflow-y-auto custom-scrollbar"
        >
          <div class="text-center space-y-4">
            <h3 class="text-2xl font-bold text-white">
              Initialize Architectural View
            </h3>
            <p class="text-gray-400 leading-relaxed">
              This tool organizes your <strong>Merge List</strong> into a
              zoomable 2D semantic map. To begin, ask an LLM to categorize your
              files into structural layers.
            </p>
          </div>

          <div
            class="w-full space-y-6 bg-gray-800/50 p-8 rounded-xl border border-gray-700"
          >
            <!-- Parse Error Validation Block -->
            <div
              v-if="parseError"
              ref="errorBlockRef"
              class="w-full bg-red-900/30 border border-red-700 p-4 rounded-xl space-y-3"
            >
              <div class="flex items-center space-x-2 text-red-400 font-bold">
                <AlertTriangle class="w-5 h-5" />
                <span>Validation Error</span>
              </div>
              <div
                class="text-sm text-gray-300 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto custom-scrollbar"
              >
                {{ parseError }}
              </div>
              <button
                @click="copyCorrectionPrompt"
                class="bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-4 rounded text-sm transition-colors flex items-center shadow-lg"
              >
                <Copy class="w-4 h-4 mr-2" /> Copy Correction Prompt
              </button>
            </div>

            <button
              @click="handleCopyPrompt"
              class="w-full py-4 rounded-lg font-bold text-lg transition-all flex items-center justify-center space-x-3 shadow-lg"
              :class="
                isPromptCopied
                  ? 'bg-cm-green text-white'
                  : 'bg-cm-blue hover:bg-blue-500 text-white'
              "
            >
              <Check v-if="isPromptCopied" class="w-6 h-6" />
              <Copy v-else class="w-6 h-6" />
              <span>{{
                isPromptCopied ? "Prompt Copied!" : "1. Copy Generation Prompt"
              }}</span>
            </button>

            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <label
                  class="text-sm font-bold text-gray-300 uppercase tracking-widest"
                  >2. Paste LLM Response (JSON)</label
                >
              </div>
              <textarea
                v-model="promptResponse"
                class="w-full h-40 bg-cm-input-bg border border-gray-600 text-gray-200 p-4 rounded outline-none focus:border-cm-blue custom-scrollbar font-mono text-xs"
                placeholder="Paste the JSON object or array of nodes here..."
              ></textarea>
            </div>

            <button
              @click="parseResponse"
              :disabled="!promptResponse.trim()"
              class="w-full py-3 bg-cm-green hover:bg-green-600 disabled:opacity-30 text-white font-bold rounded shadow transition-all flex items-center justify-center space-x-2"
            >
              <Network class="w-4 h-4" />
              <span>Visualize Hierarchy</span>
            </button>
          </div>
        </div>

        <!-- STEP 2: The Architecture Explorer -->
        <div v-else class="flex-grow flex flex-col min-h-0">
          <!-- Breadcrumbs -->
          <div
            class="flex items-center space-x-1 text-sm px-6 py-3 bg-gray-800 border-b border-gray-700 shrink-0"
          >
            <div v-for="(b, idx) in zoomPath" :key="b.id" class="flex items-center">
              <span v-if="idx > 0" class="mx-2 text-gray-500">/</span>
              <button
                @click="zoomPath.splice(idx + 1)"
                class="hover:text-white transition-colors"
                :class="
                  idx === zoomPath.length - 1 ? 'text-white font-bold' : 'text-gray-400'
                "
              >
                {{ b.name }}
              </button>
            </div>
          </div>

          <div class="flex-grow flex min-h-0">
            <!-- Left Pane: 2D Map -->
            <div
              class="w-2/3 border-r border-gray-700 relative bg-[#1A1A1A] overflow-hidden p-2"
            >
              <div
                v-if="
                  currentZoomNode &&
                  currentZoomNode.children &&
                  currentZoomNode.children.length > 0
                "
                class="absolute inset-0 m-2"
              >
                <div
                  v-for="child in currentZoomNode.children"
                  :key="child.id"
                  class="absolute border border-gray-900 rounded-xl overflow-hidden cursor-pointer transition-all duration-300 hover:brightness-125 shadow-lg group"
                  :class="{ 'opacity-20 grayscale': searchQuery && !nodeHasMatch(child, searchQuery) }"
                  :style="getRectStyle(child.layout)"
                  @click="zoomPath.push(child)"
                  @mouseenter="hoveredNode = child"
                  @mouseleave="hoveredNode = null"
                >
                  <!-- Background Node Color -->
                  <div
                    class="absolute inset-0 opacity-25 group-hover:opacity-40 transition-opacity"
                    :style="{ backgroundColor: child.color }"
                  ></div>

                  <!-- Level 2 Previews (Children's children) -->
                  <div
                    v-if="child.children && child.children.length > 0"
                    class="absolute inset-0 opacity-30"
                  >
                    <div
                      v-for="grandchild in child.children"
                      :key="grandchild.id"
                      class="absolute border border-gray-900 rounded-lg"
                      :style="[
                        getRectStyle(grandchild.layout),
                        { backgroundColor: grandchild.color },
                      ]"
                    ></div>
                  </div>

                  <!-- Labels -->
                  <div
                    class="absolute inset-0 p-4 flex flex-col justify-start pointer-events-none"
                  >
                    <div class="font-bold text-white text-xl drop-shadow-md truncate">
                      {{ child.name }}
                    </div>
                    <div class="text-sm text-gray-300 drop-shadow-md font-medium">
                      {{ child.weight }} items
                    </div>
                  </div>
                </div>
              </div>
              <!-- Detailed File List for Leaf Nodes -->
              <div
                v-else-if="
                  currentZoomNode &&
                  currentZoomNode.files &&
                  currentZoomNode.files.length > 0
                "
                class="absolute inset-0 m-2 overflow-y-auto custom-scrollbar bg-[#222222] rounded-xl border border-gray-800 p-6 space-y-4"
              >
                <h4 class="text-lg font-bold text-white mb-4 flex items-center">
                  <FileCode class="w-5 h-5 mr-2 text-cm-blue" />
                  Implementation Files
                </h4>
                <div
                  v-for="file in processedLeafFiles"
                  :key="file.path"
                  class="bg-[#2a2a2a] border rounded-lg p-5 shadow-sm hover:border-gray-500 transition-all duration-300"
                  :class="[
                      searchQuery && (file.path.toLowerCase().includes(searchQuery.toLowerCase()) || (file.description && file.description.toLowerCase().includes(searchQuery.toLowerCase())))
                        ? 'border-cm-blue ring-1 ring-cm-blue/30 scale-[1.01]'
                        : 'border-gray-700'
                  ]"
                >
                  <div class="flex items-center space-x-2 mb-3">
                    <span class="text-cm-blue font-mono font-bold text-sm break-all" v-html="highlightMatch(file.path, searchQuery)"></span>
                  </div>
                  <p class="text-gray-300 text-[15px] leading-relaxed" v-html="highlightMatch(file.description, searchQuery)"></p>
                </div>
              </div>
              <div v-else class="flex items-center justify-center h-full text-gray-500">
                <div class="text-center">
                  <FileCode class="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p class="text-2xl font-bold text-gray-400">
                    {{ currentZoomNode?.name }}
                  </p>
                  <p class="text-sm mt-2">Empty Leaf Node</p>
                </div>
              </div>
            </div>

            <!-- Right Pane: Details & Copy -->
            <div
              class="w-1/3 flex flex-col p-8 bg-black/20 overflow-y-auto custom-scrollbar"
            >
              <div v-if="displayNode" class="space-y-8 animate-in fade-in duration-300">
                <div class="space-y-2">
                  <div class="flex items-center justify-between">
                    <h3 class="text-3xl font-extralight text-white leading-tight truncate pr-4">
                      {{ displayNode.name }}
                    </h3>
                    <span
                      v-if="displayNode.domain"
                      class="text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded"
                      :style="{
                        backgroundColor: displayNode.color + '40',
                        color: displayNode.color,
                      }"
                    >
                      {{ displayNode.domain }}
                    </span>
                  </div>
                  <div
                    class="h-1 w-20 rounded"
                    :style="{ backgroundColor: displayNode.color }"
                  ></div>
                </div>

                <div class="space-y-4">
                  <div class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]">
                    Architectural Description
                  </div>
                  <p class="text-gray-200 text-lg leading-relaxed italic">
                    "{{
                      displayNode.description || "No description provided for this node."
                    }}"
                  </p>
                </div>

                <div
                  v-if="zoomPath.length > 0 && displayNode.id !== zoomPath[0].id"
                  class="space-y-4 pt-6 border-t border-gray-700/50"
                >
                  <div class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]">
                    Actions
                  </div>
                  <button
                    @click="handleCopyNodeCode(displayNode)"
                    class="hover:brightness-110 text-white w-full py-4 rounded-xl font-bold text-lg shadow-xl transition-all flex items-center justify-center space-x-3 active:scale-[0.98]"
                    :style="{ backgroundColor: displayNode.color }"
                    title="Copy all merged code for this node and its children"
                  >
                    <ClipboardPaste class="w-6 h-6" />
                    <span>Copy Merged Code</span>
                  </button>
                </div>

                <div
                  v-if="displayNode.files && displayNode.files.length > 0"
                  class="space-y-4 pt-6"
                >
                  <div class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]">
                    Direct Files ({{ displayNode.files.length }})
                  </div>
                  <div class="space-y-1">
                    <div
                      v-for="file in displayNode.files"
                      :key="file.path"
                      class="flex items-center space-x-2 text-gray-400 group"
                    >
                      <FileCode class="w-3 h-3 text-gray-600 shrink-0" />
                      <span class="text-xs font-mono truncate text-gray-300">{{
                        file.path
                      }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div
                v-else
                class="h-full flex items-center justify-center text-gray-600 italic"
              >
                Select a node to view details
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Simple Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end">
        <button
          @click="emit('close')"
          class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-8 rounded transition-colors text-sm"
        >
          Close Map
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 3px;
}
</style>