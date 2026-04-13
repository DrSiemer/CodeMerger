<script setup>
import { Search, Filter, GitBranch, CheckSquare } from 'lucide-vue-next'
import FileTreeNode from './FileTreeNode.vue'

const props = defineProps({
  fileTree: Array,
  filterText: String,
  isExtFilter: Boolean,
  isGitFilter: Boolean,
  selectedPaths: Array,
  expandedDirs: Object, // Set
  highlightedPath: String
})

const emit = defineEmits([
  'update:filterText',
  'update:isExtFilter',
  'update:isGitFilter',
  'toggle-select',
  'toggle-directory',
  'file-click',
  'toggle-expand',
  'add-all'
])

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
  <div id="fm-available-files" class="w-1/2 flex flex-col border-r border-gray-700 p-5 bg-cm-dark-bg">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-gray-200">Available Files</h3>
      <div class="flex items-center space-x-2">
        <button
          @click="emit('update:isGitFilter', !isGitFilter)"
          class="p-1.5 rounded border transition-colors"
          :class="isGitFilter ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-500'"
          title="Toggle Gitignore Filter"
          v-info="'fm_filter_git'"
        >
          <GitBranch class="w-4 h-4" />
        </button>
        <button
          @click="emit('update:isExtFilter', !isExtFilter)"
          class="p-1.5 rounded border transition-colors"
          :class="isExtFilter ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-500'"
          title="Toggle Extension Filter"
          v-info="'fm_filter_ext'"
        >
          <Filter class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Filter Search -->
    <div class="relative mb-4">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
      <input
        id="fm-filter-input"
        :value="filterText"
        @input="emit('update:filterText', $event.target.value)"
        type="text"
        placeholder="Filter tree..."
        class="w-full bg-cm-input-bg text-white pl-10 pr-4 py-2 rounded border border-gray-600 focus:border-cm-blue outline-none text-sm"
        v-info="'fm_filter_text'"
      >
    </div>

    <!-- File Tree -->
    <div class="flex-grow overflow-y-auto custom-scrollbar pr-2 mb-2" v-info="'fm_tree'">
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

    <div class="flex justify-end pt-2">
      <button
        id="btn-fm-add-all"
        @click="emit('add-all')"
        class="bg-gray-700 hover:bg-gray-600 text-white font-medium py-1.5 px-4 rounded text-sm transition-colors flex items-center"
        v-info="'fm_add_all'"
      >
        <CheckSquare class="w-4 h-4 mr-2" />
        Add all
      </button>
    </div>
  </div>
</template>