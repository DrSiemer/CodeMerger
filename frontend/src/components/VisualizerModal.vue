<script setup>
import { ref, onMounted, computed, markRaw } from "vue";
import {
  X,
  Network,
  Copy,
  Check,
  FileCode,
  ClipboardPaste,
} from "lucide-vue-next";
import { useAppState } from "../composables/useAppState";
import { useEscapeKey } from "../composables/useEscapeKey";
import VisualizerTreeNode from "./VisualizerTreeNode.vue";

const emit = defineEmits(["close"]);
const {
  activeProject,
  getVisualizerPrompt,
  copyVisualizerNodeCode,
  resizeWindow,
  statusMessage,
} = useAppState();

const viewState = ref("init"); // 'init' | 'visualizing'
const promptResponse = ref("");
const treeData = ref([]);
const activeNode = ref(null);
const expandedNodes = ref(new Set());
const isPromptCopied = ref(false);

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

const parseResponse = () => {
  try {
    let raw = promptResponse.value.trim();
    const startIdx = raw.indexOf("[");
    const endIdx = raw.lastIndexOf("]");
    if (startIdx === -1 || endIdx === -1)
      throw new Error("JSON structure not found.");

    const jsonStr = raw.substring(startIdx, endIdx + 1);
    const data = JSON.parse(jsonStr);

    if (!Array.isArray(data)) throw new Error("Root must be an array.");

    // Recursively assign IDs
    let idCounter = 0;
    const processNodes = (nodes) => {
      nodes.forEach((node) => {
        node.id = ++idCounter;
        if (node.children) processNodes(node.children);
      });
    };
    processNodes(data);

    treeData.value = data;
    viewState.value = "visualizing";
    if (data.length > 0) activeNode.value = data[0];
  } catch (err) {
    alert(`Could not parse architectural tree.\n\nError: ${err.message}`);
  }
};

const getAllFilesUnderNode = (node) => {
  let paths = [...(node.files || [])];
  if (node.children) {
    node.children.forEach((child) => {
      paths = [...paths, ...getAllFilesUnderNode(child)];
    });
  }
  return paths;
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

const toggleNode = (node) => {
  if (expandedNodes.value.has(node.id)) expandedNodes.value.delete(node.id);
  else expandedNodes.value.add(node.id);
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
        <div class="flex items-center space-x-3 text-white">
          <Network class="w-6 h-6 text-cm-blue" />
          <h2 class="text-xl font-bold">Project Node Visualizer</h2>
          <span class="text-gray-500 text-sm font-medium"
            >/ {{ activeProject.name }}</span
          >
        </div>
        <button
          @click="emit('close')"
          class="text-gray-400 hover:text-white transition-colors"
          title="Close visualizer"
        >
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Main Body -->
      <div class="flex-grow flex flex-col min-h-0 bg-cm-dark-bg">
        <!-- STEP 1: Initialization -->
        <div
          v-if="viewState === 'init'"
          class="flex-grow flex flex-col items-center justify-center p-12 max-w-2xl mx-auto space-y-8"
        >
          <div class="text-center space-y-4">
            <h3 class="text-2xl font-bold text-white">
              Initialize Architectural View
            </h3>
            <p class="text-gray-400 leading-relaxed">
              This tool organizes your <strong>Merge List</strong> into a
              logical hierarchy. To begin, ask an LLM to categorize your files
              by feature, layer, or role.
            </p>
          </div>

          <div
            class="w-full space-y-6 bg-gray-800/50 p-8 rounded-xl border border-gray-700"
          >
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
                placeholder="Paste the JSON array of nodes here..."
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

        <!-- STEP 2: The Visualizer Tree -->
        <div v-else class="flex-grow flex min-h-0">
          <!-- Left Pane: Tree View -->
          <div
            class="w-1/2 border-r border-gray-700 flex flex-col p-6 overflow-hidden"
          >
            <div class="flex items-center justify-between mb-6">
              <h3
                class="font-bold text-gray-300 uppercase tracking-widest text-sm"
              >
                System Hierarchy
              </h3>
              <button
                @click="viewState = 'init'"
                class="text-xs font-bold text-gray-500 hover:text-gray-300 uppercase tracking-tight"
              >
                Re-initialize
              </button>
            </div>

            <div
              class="flex-grow overflow-y-auto custom-scrollbar pr-2 space-y-1"
            >
              <VisualizerTreeNode
                v-for="node in treeData"
                :key="node.id"
                :node="node"
                :active-id="activeNode?.id"
                :expanded-nodes="expandedNodes"
                @activate="activeNode = $event"
                @toggle="toggleNode"
              />
            </div>
          </div>

          <!-- Right Pane: Details & Copy -->
          <div
            class="w-1/2 flex flex-col p-8 bg-black/20 overflow-y-auto custom-scrollbar"
          >
            <div
              v-if="activeNode"
              class="space-y-8 animate-in fade-in duration-300"
            >
              <div class="space-y-2">
                <h3 class="text-4xl font-extralight text-cm-blue leading-tight">
                  {{ activeNode.name }}
                </h3>
                <div class="h-1 w-20 bg-cm-blue/30 rounded"></div>
              </div>

              <div class="space-y-4">
                <div
                  class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]"
                >
                  Architectural Description
                </div>
                <p class="text-gray-200 text-lg leading-relaxed italic">
                  "{{
                    activeNode.description ||
                    "No description provided for this node."
                  }}"
                </p>
              </div>

              <div class="space-y-4 pt-6">
                <div
                  class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]"
                >
                  Actions
                </div>
                <button
                  @click="handleCopyNodeCode(activeNode)"
                  class="bg-cm-blue hover:bg-blue-500 text-white w-full py-4 rounded-xl font-bold text-lg shadow-xl transition-all flex items-center justify-center space-x-3 active:scale-[0.98]"
                  title="Copy all merged code for this node and its children"
                >
                  <ClipboardPaste class="w-6 h-6" />
                  <span>Copy Merged Code for Node</span>
                </button>
              </div>

              <div
                v-if="activeNode.files && activeNode.files.length > 0"
                class="space-y-4 pt-6"
              >
                <div
                  class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]"
                >
                  Direct Files ({{ activeNode.files.length }})
                </div>
                <div class="space-y-1">
                  <div
                    v-for="file in activeNode.files"
                    :key="file"
                    class="flex items-center space-x-2 text-gray-400 group"
                  >
                    <FileCode class="w-3 h-3 text-gray-600" />
                    <span class="text-xs font-mono truncate">{{ file }}</span>
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

      <!-- Simple Footer -->
      <div
        class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end"
      >
        <button
          @click="emit('close')"
          class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-8 rounded transition-colors text-sm"
        >
          Close Visualizer
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
