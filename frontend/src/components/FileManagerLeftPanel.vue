<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Filter, GitBranch, CheckSquare, Loader2, Eye, X } from 'lucide-vue-next'
import FileTreeNode from './FileTreeNode.vue'

const props = defineProps({
  fileTree: Array,
  isExtFilter: Boolean,
  isGitFilter: Boolean,
  selectedPaths: Array,
  expandedDirs: Object,
  highlightedPath: String,
  isLoading: Boolean
})

const emit = defineEmits([
  'update:isExtFilter',
  'update:isGitFilter',
  'toggle-select',
  'toggle-directory',
  'file-click',
  'toggle-expand',
  'add-all'
])

const showVisibilityOptions = ref(false)
const windowWidth = ref(window.innerWidth)

const updateWidth = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', updateWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})

const isNarrow = computed(() => windowWidth.value < 1000)

const scrollToPath = (path) => {
  const id = `node-${path.replace(/[\\/.]/g, '-')}`
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}

defineExpose({ scrollToPath })
</script>

<template>
  <div id="fm-available-files" class="flex flex-col border-r border-gray-700 p-5 bg-cm-dark-bg transition-all duration-300">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-gray-200">Available Files</h3>
      <div class="flex items-center space-x-2">
        <button
          v-if="!showVisibilityOptions"
          @click="showVisibilityOptions = true"
          class="flex items-center px-3 py-1.5 rounded border border-gray-600 bg-gray-800 text-gray-400 hover:text-white transition-colors text-xs font-bold uppercase tracking-wider"
          v-info="'fm_visibility_toggle'"
        >
          <Eye class="w-4 h-4 mr-2" />
          <span>File visibility</span>
        </button>

        <template v-else>
          <button
            @click="emit('update:isGitFilter', !isGitFilter)"
            class="flex items-center px-3 py-1.5 rounded border transition-colors text-xs font-bold uppercase tracking-wider"
            :class="isGitFilter ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-400'"
            v-info="'fm_filter_git'"
            :title="isNarrow ? 'Toggle Gitignore Filter' : ''"
          >
            <GitBranch class="w-4 h-4" :class="{'mr-2': !isNarrow}" />
            <span v-if="!isNarrow">Git ignored</span>
          </button>
          <button
            @click="emit('update:isExtFilter', !isExtFilter)"
            class="flex items-center px-3 py-1.5 rounded border transition-colors text-xs font-bold uppercase tracking-wider"
            :class="isExtFilter ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-400'"
            v-info="'fm_filter_ext'"
            :title="isNarrow ? 'Toggle Extension Filter' : ''"
          >
            <Filter class="w-4 h-4" :class="{'mr-2': !isNarrow}" />
            <span v-if="!isNarrow">Extensions</span>
          </button>
          <button
            @click="showVisibilityOptions = false"
            class="p-1.5 text-gray-500 hover:text-white transition-colors"
          >
            <X class="w-4 h-4" />
          </button>
        </template>
      </div>
    </div>

    <!-- Tree / Loading Area -->
    <div class="flex-grow overflow-y-auto custom-scrollbar pr-2 mb-2 relative" v-info="'fm_tree'">
      <div v-if="isLoading" class="absolute inset-0 flex flex-col items-center justify-center space-y-4 bg-cm-dark-bg/80 z-10">
        <Loader2 class="w-10 h-10 text-cm-blue animate-spin" />
        <span class="text-sm font-bold text-gray-400 uppercase tracking-widest">Scanning Files...</span>
      </div>

      <div v-else>
        <FileTreeNode
          v-for="node in fileTree"
          :key="node.path"
          :node="node"
          :selected-paths="selectedPaths"
          :initial-expanded-paths="Array.from(expandedDirs)"
          :highlightedPath="highlightedPath"
          @toggle-select="(p) => emit('toggle-select', p)"
          @toggle-directory="(node) => emit('toggle-directory', node)"
          @file-click="(p) => emit('file-click', p)"
          @toggle-expand="(data) => emit('toggle-expand', data)"
        />
      </div>
    </div>

    <div class="flex justify-end pt-2">
      <button
        id="btn-fm-add-all"
        @click="emit('add-all')"
        :disabled="isLoading"
        class="bg-gray-700 hover:bg-gray-600 disabled:opacity-30 disabled:cursor-not-allowed text-white font-medium py-1.5 px-4 rounded text-sm transition-colors flex items-center"
        v-info="'fm_add_all'"
      >
        <CheckSquare class="w-4 h-4 mr-2" />
        Add all
      </button>
    </div>
  </div>
</template>