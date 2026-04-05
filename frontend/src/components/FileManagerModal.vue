<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import {
  X, Search, Filter, GitBranch, Milestone,
  Trash2, ArrowUpToLine, ArrowUp, ArrowDown, ArrowDownToLine,
  RotateCcw, Save, CheckSquare
} from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import FileTreeNode from './FileTreeNode.vue'
import { useDragAndDrop } from '@formkit/drag-and-drop/vue'

const emit = defineEmits(['close'])
const { activeProject, getFileTree, resizeWindow, updateProjectFiles } = useAppState()

// Reorderable list setup
const [mergeListRef, listItems] = useDragAndDrop(
  JSON.parse(JSON.stringify(activeProject.selectedFiles)),
  { handle: '.drag-handle' }
)

// State
const fileTree = ref([])
const filterText = ref('')
const isExtFilter = ref(true)
const isGitFilter = ref(true)
const showFullPaths = ref(false)
const selectedIndices = ref(new Set())
const lastSelectedIndex = ref(null)
const currentExpandedDirs = ref(new Set(activeProject.expandedDirs))
const isLoaded = ref(false)

const TOKEN_COLOR_RANGE_MAX = 2500

onMounted(async () => {
  await resizeWindow(1100, 800)
  await refreshTree()
  isLoaded.value = true
})

const refreshTree = async () => {
  fileTree.value = await getFileTree(filterText.value, isExtFilter.value, isGitFilter.value)
}

watch([filterText, isExtFilter, isGitFilter], () => {
  refreshTree()
})

const totalTokens = computed(() => {
  return listItems.value.reduce((acc, f) => acc + (f.tokens || 0), 0)
})

const tokenColorClass = computed(() => {
  const limit = activeProject.tokenLimit || 0
  if (limit > 0 && totalTokens.value > limit) return 'text-cm-warn'
  return 'text-gray-400'
})

const getTokenColor = (count) => {
  if (!count || count < 0) return 'text-gray-500'
  const maxInList = Math.max(...listItems.value.map(f => f.tokens || 0), TOKEN_COLOR_RANGE_MAX)
  const p = count / maxInList
  if (p < 0.2) return 'text-gray-500'
  if (p < 0.4) return 'text-gray-400'
  if (p < 0.6) return 'text-[#B77B06]'
  if (p < 0.8) return 'text-[#DE6808]'
  return 'text-[#DF2622]'
}

// --- Enhanced Selection Logic ---

const handleFileClick = (index, event) => {
  if (event.shiftKey && lastSelectedIndex.value !== null) {
    // Shift-Select: Range
    const start = Math.min(lastSelectedIndex.value, index)
    const end = Math.max(lastSelectedIndex.value, index)
    selectedIndices.value.clear()
    for (let i = start; i <= end; i++) {
      selectedIndices.value.add(i)
    }
  } else if (event.ctrlKey) {
    // Ctrl-Select: Discrete
    if (selectedIndices.value.has(index)) {
      selectedIndices.value.delete(index)
    } else {
      selectedIndices.value.add(index)
      lastSelectedIndex.value = index
    }
  } else {
    // Single Click: Reset
    selectedIndices.value.clear()
    selectedIndices.value.add(index)
    lastSelectedIndex.value = index
  }
}

// --- Actions from Tree ---

const toggleFileSelect = (path) => {
  const idx = listItems.value.findIndex(f => f.path === path)
  if (idx !== -1) {
    listItems.value.splice(idx, 1)
    selectedIndices.value.clear()
    lastSelectedIndex.value = null
  } else {
    window.pywebview.api.get_token_count(path).then(tokens => {
      listItems.value.push({ path, tokens })
    })
  }
}

const toggleFolderExpand = ({ path, expanded }) => {
  if (expanded) currentExpandedDirs.value.add(path)
  else currentExpandedDirs.value.delete(path)
}

const addAll = () => {
  const allFiles = []
  const traverse = (nodes) => {
    for (const node of nodes) {
      if (node.type === 'file') allFiles.push(node.path)
      if (node.children) traverse(node.children)
    }
  }
  traverse(fileTree.value)
  const currentPaths = new Set(listItems.value.map(f => f.path))
  const toAdd = allFiles.filter(p => !currentPaths.has(p))
  if (toAdd.length > 50 && !confirm(`Add ${toAdd.length} files to list?`)) return
  toAdd.forEach(path => {
    window.pywebview.api.get_token_count(path).then(tokens => {
      listItems.value.push({ path, tokens })
    })
  })
}

// --- Navigation Helpers ---

const scrollToSelection = (alignToTop = false) => {
  nextTick(() => {
    const selectedEl = mergeListRef.value?.querySelector('.bg-cm-blue')
    if (selectedEl) {
      selectedEl.scrollIntoView({
        behavior: 'smooth',
        block: alignToTop ? 'start' : 'nearest'
      })
    }
  })
}

// --- Reorder Logic ---

const moveSelectionToTop = () => {
  if (selectedIndices.value.size === 0) return
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => a - b)
  const itemsToMove = sortedIndices.map(i => listItems.value[i])
  for (let i = sortedIndices.length - 1; i >= 0; i--) listItems.value.splice(sortedIndices[i], 1)
  listItems.value.unshift(...itemsToMove)
  selectedIndices.value.clear()
  for (let i = 0; i < itemsToMove.length; i++) selectedIndices.value.add(i)
  lastSelectedIndex.value = 0
  scrollToSelection(true)
}

const moveSelectionUp = () => {
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => a - b)
  if (sortedIndices.length === 0 || sortedIndices[0] === 0) return
  const newIndices = new Set()
  sortedIndices.forEach(i => {
    const item = listItems.value.splice(i, 1)[0]
    listItems.value.splice(i - 1, 0, item)
    newIndices.add(i - 1)
  })
  selectedIndices.value = newIndices
  lastSelectedIndex.value = Array.from(newIndices)[0]
  scrollToSelection()
}

const moveSelectionDown = () => {
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => b - a)
  if (sortedIndices.length === 0 || sortedIndices[0] === listItems.value.length - 1) return
  const newIndices = new Set()
  sortedIndices.forEach(i => {
    const item = listItems.value.splice(i, 1)[0]
    listItems.value.splice(i + 1, 0, item)
    newIndices.add(i + 1)
  })
  selectedIndices.value = newIndices
  lastSelectedIndex.value = Array.from(newIndices)[0]
  scrollToSelection()
}

const moveSelectionToBottom = () => {
  if (selectedIndices.value.size === 0) return
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => a - b)
  const itemsToMove = sortedIndices.map(i => listItems.value[i])
  for (let i = sortedIndices.length - 1; i >= 0; i--) listItems.value.splice(sortedIndices[i], 1)
  listItems.value.push(...itemsToMove)
  selectedIndices.value.clear()
  const startIdx = listItems.value.length - itemsToMove.length
  for (let i = 0; i < itemsToMove.length; i++) selectedIndices.value.add(startIdx + i)
  lastSelectedIndex.value = startIdx
  scrollToSelection(true)
}

const removeSelected = () => {
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => b - a)
  sortedIndices.forEach(i => listItems.value.splice(i, 1))
  selectedIndices.value.clear()
  lastSelectedIndex.value = null
}

const clearAll = () => {
  if (confirm('Are you sure you want to clear the entire merge list?')) {
    listItems.value.splice(0, listItems.value.length)
    selectedIndices.value.clear()
    lastSelectedIndex.value = null
  }
}

// --- Save & Close Logic ---

const hasUnsavedChanges = computed(() => {
  if (listItems.value.length !== activeProject.selectedFiles.length) return true
  for (let i = 0; i < listItems.value.length; i++) {
    if (listItems.value[i].path !== activeProject.selectedFiles[i].path) return true
  }
  if (currentExpandedDirs.value.size !== activeProject.expandedDirs.length) return true
  for (const path of activeProject.expandedDirs) {
    if (!currentExpandedDirs.value.has(path)) return true
  }
  return false
})

const handleCancel = () => {
  if (hasUnsavedChanges.value && !confirm('You have unsaved changes. Discard them?')) return
  emit('close')
}

const handleSave = async () => {
  await updateProjectFiles(listItems.value, totalTokens.value, Array.from(currentExpandedDirs.value))
  emit('close')
}
</script>

<template>
  <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
    <div class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[90vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar">
        <div class="flex items-center space-x-3">
          <h2 class="text-xl font-bold text-white">Edit Merge List</h2>
          <span class="text-gray-500 text-sm font-medium">/ {{ activeProject.name }}</span>
        </div>
        <button @click="handleCancel" class="text-gray-400 hover:text-white transition-colors">
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Main Content Split -->
      <div class="flex-grow flex min-h-0 overflow-hidden">

        <!-- Left Panel: Available Files -->
        <div class="w-1/2 flex flex-col border-r border-gray-700 p-5 bg-cm-dark-bg">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-gray-200">Available Files</h3>
            <div class="flex items-center space-x-2">
              <button
                @click="isGitFilter = !isGitFilter"
                class="p-1.5 rounded border transition-colors"
                :class="isGitFilter ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-500'"
                title="Toggle Gitignore Filter"
              >
                <GitBranch class="w-4 h-4" />
              </button>
              <button
                @click="isExtFilter = !isExtFilter"
                class="p-1.5 rounded border transition-colors"
                :class="isExtFilter ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-500'"
                title="Toggle Extension Filter"
              >
                <Filter class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Filter Search -->
          <div class="relative mb-4">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              v-model="filterText"
              type="text"
              placeholder="Filter tree..."
              class="w-full bg-cm-input-bg text-white pl-10 pr-4 py-2 rounded border border-gray-600 focus:border-cm-blue outline-none text-sm"
            >
          </div>

          <!-- File Tree -->
          <div class="flex-grow overflow-y-auto custom-scrollbar pr-2 mb-2">
            <FileTreeNode
              v-for="node in fileTree"
              :key="node.path"
              :node="node"
              :selected-paths="listItems.map(f => f.path)"
              :initial-expanded-paths="activeProject.expandedDirs"
              @toggle-select="toggleFileSelect"
              @toggle-expand="toggleFolderExpand"
            />
          </div>

          <div class="flex justify-end pt-2">
            <button
              @click="addAll"
              class="bg-gray-700 hover:bg-gray-600 text-white font-medium py-1.5 px-4 rounded text-sm transition-colors flex items-center"
            >
              <CheckSquare class="w-4 h-4 mr-2" />
              Add all
            </button>
          </div>
        </div>

        <!-- Right Panel: Merge Order -->
        <div class="w-1/2 flex flex-col p-5 bg-cm-dark-bg">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <h3 class="font-semibold text-gray-200">Merge Order</h3>
              <span :class="tokenColorClass" class="text-sm font-mono pt-0.5">
                ({{ listItems.length }} files, {{ totalTokens.toLocaleString() }} tokens)
              </span>
            </div>
            <button
              @click="showFullPaths = !showFullPaths"
              class="p-1.5 rounded border transition-colors"
              :class="showFullPaths ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-500'"
              title="Toggle Path Visibility"
            >
              <Milestone class="w-4 h-4" />
            </button>
          </div>

          <!-- Merge List -->
          <div class="flex-grow overflow-y-auto custom-scrollbar mb-2 pr-2">
            <ul ref="mergeListRef" class="space-y-1">
              <li
                v-for="(file, index) in listItems"
                :key="file.path"
                class="group flex items-center border rounded p-2 text-sm transition-colors"
                :class="selectedIndices.has(index) ? 'bg-cm-blue border-cm-blue' : 'bg-cm-input-bg border-gray-700 hover:border-gray-500'"
                @click="handleFileClick(index, $event)"
              >
                <div class="drag-handle cursor-grab active:cursor-grabbing mr-3 text-gray-600 group-hover:text-gray-400" @click.stop>
                  <div class="grid grid-cols-2 gap-0.5 w-3">
                    <div v-for="n in 6" :key="n" class="w-1 h-1 bg-current rounded-full"></div>
                  </div>
                </div>

                <span class="flex-grow truncate pr-4" :class="selectedIndices.has(index) ? 'text-white font-medium' : 'text-gray-200'">
                  {{ showFullPaths ? file.path : file.path.split('/').pop() }}
                </span>

                <div class="flex items-center space-x-3 shrink-0">
                  <span class="text-xs font-mono" :class="selectedIndices.has(index) ? 'text-blue-100 font-bold' : getTokenColor(file.tokens)">
                    {{ file.tokens?.toLocaleString() || '?' }}
                  </span>
                </div>
              </li>
            </ul>
            <div v-if="listItems.length === 0" class="h-full flex items-center justify-center text-gray-600 italic">
              No files selected to merge.
            </div>
          </div>

          <!-- Reorder Toolbar (No border, reduced padding) -->
          <div class="flex items-center justify-center space-x-2 pt-2">
            <button @click="moveSelectionToTop" class="p-2 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="selectedIndices.size === 0" title="Move Selected to Top"><ArrowUpToLine class="w-4 h-4" /></button>
            <button @click="moveSelectionUp" class="p-2 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="selectedIndices.size === 0" title="Move Selected Up"><ArrowUp class="w-4 h-4" /></button>
            <button @click="removeSelected" class="px-5 py-2 bg-gray-800 border border-gray-700 rounded hover:bg-red-900/50 hover:text-red-400 text-gray-400 disabled:opacity-30 text-sm font-medium transition-colors" :disabled="selectedIndices.size === 0" title="Remove Selected">Remove</button>
            <button @click="moveSelectionDown" class="p-2 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="selectedIndices.size === 0" title="Move Selected Down"><ArrowDown class="w-4 h-4" /></button>
            <button @click="moveSelectionToBottom" class="p-2 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="selectedIndices.size === 0" title="Move Selected to Bottom"><ArrowDownToLine class="w-4 h-4" /></button>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="px-6 py-2 border-t border-gray-700 bg-cm-top-bar flex justify-between shrink-0">
        <button
          @click="clearAll"
          class="bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium py-1.5 px-6 rounded transition-colors flex items-center text-sm"
        >
          <RotateCcw class="w-3.5 h-3.5 mr-2" />
          Clear List
        </button>

        <div class="flex items-center space-x-3">
          <button
            @click="handleCancel"
            class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-1.5 px-6 rounded transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            @click="handleSave"
            class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-1.5 px-10 rounded shadow-md transition-all flex items-center text-sm"
          >
            <Save class="w-4 h-4 mr-2" />
            Update Project
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>