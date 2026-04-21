<script setup>
import { ref, onMounted, computed } from "vue";
import { X, Network, Search, Info, RefreshCw, Trash2 } from "lucide-vue-next";
import { useAppState } from "../composables/useAppState";
import { useEscapeKey } from "../composables/useEscapeKey";
import { useVisualizer } from "../composables/useVisualizer";

import VisualizerInit from "./visualizer/VisualizerInit.vue";
import VisualizerExplorer from "./visualizer/VisualizerExplorer.vue";
import VisualizerLeafFiles from "./visualizer/VisualizerLeafFiles.vue";
import VisualizerDetails from "./visualizer/VisualizerDetails.vue";
import VisualizerCodeViewer from "./visualizer/VisualizerCodeViewer.vue";

const emit = defineEmits(["close"]);
const { activeProject, openFile, resizeWindow } = useAppState();

const {
  viewState, navPath, hoveredNode, targetScrollPath, parseError, currentNavNode, displayNode,
  rankedMtimeMap, canCopy, mapSyncState, syncMessage,
  highlightedLines, isCodeLoading,
  processRawResponse, handleCopyPrompt, handleCopyAmendPrompt,
  copyCorrectionPrompt, handleCopyNodeCode, nukeVisualizerMap,
  diveIntoFile, scrollToAndHighlight
} = useVisualizer();

const searchQuery = ref("");

useEscapeKey(() => emit("close"));

onMounted(async () => {
  await resizeWindow(1100, 800);
});
</script>

<template>
  <div id="visualizer-modal" class="absolute inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
    <div class="bg-cm-dark-bg w-full h-full max-h-[92vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">
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
          @copy-prompt="handleCopyPrompt"
          @copy-correction="copyCorrectionPrompt"
          @copy-amend="handleCopyAmendPrompt"
          @parse="processRawResponse"
          @cancel="viewState = 'visualizing'"
        />

        <VisualizerExplorer
          :nav-path="navPath"
          :search-query="searchQuery"
          :ranked-mtime-map="rankedMtimeMap"
          @nav-to="(idx) => navPath.splice(idx + 1)"
          @dive-in="(node) => navPath.push(node)"
          @node-hover="(node) => hoveredNode = node"
        >
          <!-- Center Panel Code Viewer -->
          <VisualizerCodeViewer
            v-if="currentNavNode?.isFile"
            :is-code-loading="isCodeLoading"
            :highlighted-lines="highlightedLines"
          />

          <VisualizerLeafFiles
            v-else-if="!currentNavNode?.children?.length"
            :node="currentNavNode"
            :search-query="searchQuery"
            :ranked-mtime-map="rankedMtimeMap"
            :target-scroll-path="targetScrollPath"
            @open-file="openFile"
            @open-code="diveIntoFile"
          />

          <template #details="{ rankedMtimeMap }">
            <VisualizerDetails
              :display-node="displayNode"
              :can-copy="canCopy"
              :ranked-mtime-map="rankedMtimeMap"
              :search-query="searchQuery"
              @open-file="openFile"
              @scroll-to-file="(f) => scrollToAndHighlight(f.path)"
              @copy-code="handleCopyNodeCode"
            />
          </template>
        </VisualizerExplorer>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-between items-center shrink-0">
        <div class="flex items-center">
            <div v-if="viewState === 'visualizing'" class="flex items-center space-x-4">
              <button v-if="mapSyncState !== 'SYNCED'" @click="viewState = 'updating'" v-info="'viz_update_map'" class="bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 px-4 py-1.5 rounded text-sm font-bold shadow-sm transition-colors shrink-0 flex items-center">
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