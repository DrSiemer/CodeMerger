<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Filter, GitBranch, CheckSquare, Loader2, Eye, X } from 'lucide-vue-next'
import FileTreeNode from './FileTreeNode.vue'

const props = defineProps({
  fileTree: { type: Array, default: () => [] },
  isExtFilter: Boolean,
  isGitFilter: Boolean,
  selectedPaths: { type: Array, default: () => [] },
  expandedDirs: { type: Object, default: () => new Set() },
  highlightedPath: String,
  isLoading: Boolean
})

const emit = defineEmits([
  'update:isExtFilter',
  'update:isGitFilter',
  'toggle-select',
  'toggle-directory',
  'remove-select',
  'file-click',
  'toggle-expand',
  'add-all'
])

const showVisibilityOptions = ref(false)
const multiSelectedPaths = ref(new Set())
const lastClickedPath = ref(null)
const windowWidth = ref(window.innerWidth)

const clearSelection = () => {
  multiSelectedPaths.value = new Set()
  lastClickedPath.value = null
}

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

// Smart Button Logic: Analyze highlighted items vs merge list
const selectionAnalysis = computed(() => {
  const result = { toAdd: [], toRemove: [] }
  try {
    if (!multiSelectedPaths.value || multiSelectedPaths.value.size === 0) return result

    const highlighted = Array.from(multiSelectedPaths.value)
    const merged = new Set(props.selectedPaths || [])
    const toAddSet = new Set()
    const toRemoveSet = new Set()

    const pathToNode = {}
    const traverseBuildMap = (nodes) => {
      if (!nodes || !Array.isArray(nodes)) return
      for (const n of nodes) {
        if (!n) continue
        pathToNode[n.path] = n
        if (n.children) traverseBuildMap(n.children)
      }
    }
    traverseBuildMap(props.fileTree)

    const IGNORED_FOR_COMPLETENESS = ['__init__.py']

    for (const path of highlighted) {
      const node = pathToNode[path]
      if (!node) continue

      const processFileNode = (fNode) => {
        if (!fNode || IGNORED_FOR_COMPLETENESS.includes(fNode.name)) return
        if (merged.has(fNode.path)) toRemoveSet.add(fNode.path)
        else toAddSet.add(fNode.path)
      }

      if (node.type === 'file') {
        processFileNode(node)
      } else {
        const traverseSubtree = (n) => {
          if (!n) return
          if (n.type === 'file') {
            processFileNode(n)
          } else if (n.children && Array.isArray(n.children)) {
            for (const child of n.children) traverseSubtree(child)
          }
        }
        traverseSubtree(node)
      }
    }

    result.toAdd = Array.from(toAddSet)
    result.toRemove = Array.from(toRemoveSet)
  } catch (err) {
    console.error("[FileManagerLeftPanel] Selection analysis crash:", err)
  }
  return result
})

const scrollToPath = (path) => {
  const id = `node-${path.replace(/[\\/.]/g, '-')}`
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}

// Logic for Multi-selection and Range selection
const handleNodeClick = ({ node, event }) => {
  if (!node || !node.path) return
  const path = node.path
  const isShift = event.shiftKey
  const isCtrl = event.ctrlKey || event.metaKey

  if (isShift && lastClickedPath.value) {
    // Range Selection logic
    const flattened = []
    const traverse = (nodes) => {
      if (!nodes || !Array.isArray(nodes)) return
      for (const n of nodes) {
        if (!n) continue
        flattened.push(n.path)
        if (n.type === 'dir' && props.expandedDirs?.has?.(n.path)) {
          traverse(n.children || [])
        }
      }
    }
    traverse(props.fileTree)

    const idxA = flattened.indexOf(lastClickedPath.value)
    const idxB = flattened.indexOf(path)

    if (idxA !== -1 && idxB !== -1) {
      const start = Math.min(idxA, idxB)
      const end = Math.max(idxA, idxB)

      const newSelection = isCtrl ? new Set(multiSelectedPaths.value) : new Set()

      for (let i = start; i <= end; i++) {
        newSelection.add(flattened[i])
      }
      multiSelectedPaths.value = newSelection
    }
  } else if (isCtrl) {
    // Toggle individual highlight
    const newSelection = new Set(multiSelectedPaths.value)
    if (newSelection.has(path)) {
      newSelection.delete(path)
    } else {
      newSelection.add(path)
    }
    multiSelectedPaths.value = newSelection
    lastClickedPath.value = path
  } else {
    // Single selection (reset)
    multiSelectedPaths.value = new Set([path])
    lastClickedPath.value = path
  }
}

const addSelected = async () => {
  const analysis = selectionAnalysis.value
  const paths = analysis.toAdd
  if (!paths || paths.length === 0) return

  const isMixed = analysis.toRemove.length > 0

  for (const path of paths) {
    emit('toggle-select', path)
  }

  if (!isMixed) {
    multiSelectedPaths.value = new Set()
    lastClickedPath.value = null
  }
}

const removeSelected = async () => {
  const analysis = selectionAnalysis.value
  const paths = analysis.toRemove
  if (!paths || paths.length === 0) return

  const isMixed = analysis.toAdd.length > 0

  for (const path of paths) {
    emit('remove-select', path)
  }

  if (!isMixed) {
    multiSelectedPaths.value = new Set()
    lastClickedPath.value = null
  }
}

defineExpose({ scrollToPath, clearSelection })
</script>

<template>
  <div
    id="fm-available-files"
    class="flex flex-col border-r border-gray-700 p-5 bg-cm-dark-bg transition-all duration-300"
    @click.self="clearSelection"
  >
    <div class="flex items-center justify-between mb-4" @click.self="clearSelection">
      <h3 class="font-semibold text-gray-200 cursor-default" @click="clearSelection">Available Files</h3>
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
    <div
      class="flex-grow overflow-y-auto custom-scrollbar pr-2 mb-2 relative"
      v-info="'fm_tree'"
      @click.self="clearSelection"
    >
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
          :multi-selected-paths="multiSelectedPaths"
          :initial-expanded-paths="Array.from(expandedDirs)"
          :highlightedPath="highlightedPath"
          @toggle-select="(p) => emit('toggle-select', p)"
          @toggle-directory="(node) => emit('toggle-directory', node)"
          @file-click="(p) => emit('file-click', p)"
          @node-click="handleNodeClick"
          @toggle-expand="(data) => emit('toggle-expand', data)"
        />
      </div>
    </div>

    <div class="flex justify-end items-center space-x-3 pt-2">
      <!-- Smart Batch Actions -->
      <template v-if="multiSelectedPaths && multiSelectedPaths.size > 0">
        <button
          id="btn-fm-remove-selected"
          @click="removeSelected"
          :disabled="!selectionAnalysis.toRemove || selectionAnalysis.toRemove.length === 0"
          class="bg-gray-700 hover:bg-red-900/50 hover:text-red-400 disabled:opacity-30 disabled:hover:bg-gray-700 disabled:hover:text-gray-400 text-gray-300 font-bold py-1.5 px-4 rounded text-sm transition-all flex items-center"
        >
          {{ isNarrow ? 'Remove' : 'Remove Selected' }} ({{ selectionAnalysis.toRemove ? selectionAnalysis.toRemove.length : 0 }})
        </button>

        <button
          id="btn-fm-add-selected"
          @click="addSelected"
          :disabled="!selectionAnalysis.toAdd || selectionAnalysis.toAdd.length === 0"
          class="bg-cm-blue hover:bg-blue-500 disabled:opacity-30 text-white font-bold py-1.5 px-6 rounded text-sm shadow-md transition-all flex items-center"
        >
          {{ isNarrow ? 'Add' : 'Add Selected' }} ({{ selectionAnalysis.toAdd ? selectionAnalysis.toAdd.length : 0 }})
        </button>
      </template>

      <button
        v-else-if="selectedPaths.length === 0"
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