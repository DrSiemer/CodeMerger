<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { X, Save, Search } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { useEscapeKey } from '../composables/useEscapeKey'
import { useDragAndDrop } from '@formkit/drag-and-drop/vue'
import { WINDOW_SIZES } from '../utils/constants'
import FileManagerLeftPanel from './FileManagerLeftPanel.vue'
import FileManagerRightPanel from './FileManagerRightPanel.vue'
import OrderErrorModal from './OrderErrorModal.vue'

const emit = defineEmits(['close'])
const {
  activeProject, getFileTree, resizeWindow, updateProjectFiles,
  copyOrderRequest, clearUnknownFiles, statusMessage, config,
  showOrderErrorModal, orderErrorMessage
} = useAppState()

const IGNORED_FOR_COMPLETENESS = ['__init__.py']

const [mergeListRef, listItems] = useDragAndDrop(
  JSON.parse(JSON.stringify(activeProject.selectedFiles)),
  { handle: '.drag-handle' }
)

const leftPanelRef = ref(null)
const rightPanelRef = ref(null)
const fileTree = ref([])
const filterText = ref('')
const isExtFilter = ref(true)
const isGitFilter = ref(true)
const showFullPaths = ref(false)
const currentExpandedDirs = ref(new Set(activeProject.expandedDirs))
const isLoaded = ref(false)
const isTreeLoading = ref(false)
const isOrderPulseActive = ref(false)

// Sequence tracker to prevent async race conditions where old search results overwrite newer ones
const lastRequestId = ref(0)

const highlightedPath = ref(null)

useEscapeKey(() => {
  if (showOrderErrorModal.value) {
    showOrderErrorModal.value = false
    return
  }
  handleCancel()
})

const debounce = (fn, delay) => {
  let timeout
  return (...args) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn(...args), delay)
  }
}

onMounted(async () => {
  console.log("[FileManager] Mounted. Current newFileCount:", activeProject.newFileCount);
  await resizeWindow(WINDOW_SIZES.FILE_MANAGER.width, WINDOW_SIZES.FILE_MANAGER.height)
  await refreshTree()
  await autoHandleNewFiles()
  // Triggered on mount to clear UI alert immediately upon entry
  console.log("[FileManager] Clearing unknown files...");
  await clearUnknownFiles()
  isLoaded.value = true
})

const refreshTree = async () => {
  const requestId = ++lastRequestId.value
  if (!fileTree.value.length) isTreeLoading.value = true

  try {
    const currentPaths = listItems.value.map(f => f.path)
    const result = await getFileTree(filterText.value, isExtFilter.value, isGitFilter.value, currentPaths)
    if (requestId !== lastRequestId.value) return
    fileTree.value = result
  } finally {
    if (requestId === lastRequestId.value) isTreeLoading.value = false
  }
}

const debouncedRefresh = debounce(refreshTree, 200)

const autoHandleNewFiles = async () => {
  const newFiles = []
  const traverse = (nodes) => {
    nodes.forEach(node => {
      if (node.type === 'file' && node.is_new) {
        newFiles.push(node.path)
        const parts = node.path.split('/')
        let currentPath = ''
        for (let i = 0; i < parts.length - 1; i++) {
          currentPath += (i === 0 ? '' : '/') + parts[i]
          currentExpandedDirs.value.add(currentPath)
        }
      }
      if (node.children) traverse(node.children)
    })
  }
  traverse(fileTree.value)
  if (newFiles.length > 0) {
    newFiles.sort()
    const firstTargetId = `node-${newFiles[0].replace(/[\\/.]/g, '-')}`
    await nextTick()
    setTimeout(() => {
      const el = document.getElementById(firstTargetId)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 100)
  }
}

watch(filterText, () => {
  highlightedPath.value = null
  debouncedRefresh()
})

watch([isExtFilter, isGitFilter], () => {
  highlightedPath.value = null
  refreshTree()
})

const totalTokens = computed(() => {
  return listItems.value.reduce((acc, f) => {
    if (!f || f.ignoreTokens) return acc
    return acc + (f.tokens || 0)
  }, 0)
})

const tokenColorClass = computed(() => {
  const limit = activeProject.tokenLimit || 0
  if (limit > 0 && totalTokens.value > limit) return 'text-cm-warn'
  return 'text-gray-400'
})

const handleTokenInteraction = (index, event) => {
  event.stopPropagation()
  const item = listItems.value[index]
  if (!item) return

  if (event.altKey) {
    item.ignoreTokens = !item.ignoreTokens
  } else if (event.ctrlKey) {
    const path = item.path
    const breakupMsg = `\`${path}\` is too big. Please help me split it up into multiple files. Be careful not to break any of the existing logic and functionality.`
    navigator.clipboard.writeText(breakupMsg)
    statusMessage.value = `Copied breakup request for ${path.split('/').pop()}`
  }
}

const toggleFileSelect = (path) => {
  highlightedPath.value = null
  const existingIdx = listItems.value.findIndex(f => f.path === path)

  if (existingIdx !== -1) {
    listItems.value.splice(existingIdx, 1)
    rightPanelRef.value?.clearSelection()
  } else {
    window.pywebview.api.get_token_count(path).then(tokens => {
      const doubleCheckIdx = listItems.value.findIndex(f => f.path === path)
      if (doubleCheckIdx === -1) {
        listItems.value.push({ path, tokens, ignoreTokens: false })

        nextTick(() => {
          rightPanelRef.value?.scrollToPath(path)
        })
      }
    })
  }
}

const toggleDirectorySelect = async (node) => {
  highlightedPath.value = null
  const subtreeFiles = []
  const traverse = (n) => {
    if (n.type === 'file') {
      if (!IGNORED_FOR_COMPLETENESS.includes(n.name)) {
        subtreeFiles.push(n.path)
      }
    }
    if (n.children) n.children.forEach(traverse)
  }
  traverse(node)

  if (subtreeFiles.length === 0) return

  const currentPaths = new Set(listItems.value.map(f => f.path))
  const isFullySelected = subtreeFiles.every(p => currentPaths.has(p))

  if (isFullySelected) {
    const pathsToRemove = new Set(subtreeFiles)
    for (let i = listItems.value.length - 1; i >= 0; i--) {
      if (pathsToRemove.has(listItems.value[i].path)) {
        listItems.value.splice(i, 1)
      }
    }
    rightPanelRef.value?.clearSelection()
  } else {
    const toAdd = subtreeFiles.filter(p => !currentPaths.has(p))
    for (const path of toAdd) {
      const tokens = await window.pywebview.api.get_token_count(path)
      if (listItems.value.findIndex(f => f.path === path) === -1) {
        listItems.value.push({ path, tokens, ignoreTokens: false })
      }
    }

    if (toAdd.length > 0) {
      const lastPath = toAdd[toAdd.length - 1]
      nextTick(() => {
        rightPanelRef.value?.scrollToPath(lastPath)
      })
    }
  }
}

const removeFileFromList = (path) => {
  const idx = listItems.value.findIndex(f => f.path === path)
  if (idx !== -1) {
    listItems.value.splice(idx, 1)
    rightPanelRef.value?.clearSelection()
  }
}

const onLeftFileClick = (path) => {
  highlightedPath.value = null
  rightPanelRef.value?.scrollToPath(path)
}

const onRightFileClick = (path) => {
  highlightedPath.value = path
  leftPanelRef.value?.scrollToPath(path)
}

const toggleFolderExpand = ({ path, expanded }) => {
  highlightedPath.value = null
  if (expanded) currentExpandedDirs.value.add(path)
  else currentExpandedDirs.value.delete(path)
}

const addAll = async () => {
  highlightedPath.value = null
  const allFiles = []
  const traverse = (nodes) => {
    for (const node of nodes) {
      if (node.type === 'file') {
        if (!IGNORED_FOR_COMPLETENESS.includes(node.name)) {
          allFiles.push(node.path)
        }
      }
      if (node.children) traverse(node.children)
    }
  }
  traverse(fileTree.value)
  const currentPaths = new Set(listItems.value.map(f => f.path))
  const toAdd = allFiles.filter(p => !currentPaths.has(p))
  const threshold = config.value.add_all_warning_threshold || 50
  if (toAdd.length > threshold && !confirm(`Add ${toAdd.length} files to list?`)) return

  for (const path of toAdd) {
    const tokens = await window.pywebview.api.get_token_count(path)
    if (listItems.value.findIndex(f => f.path === path) === -1) {
      listItems.value.push({ path, tokens, ignoreTokens: false })
    }
  }

  if (toAdd.length > 0) {
    const lastPath = toAdd[toAdd.length - 1]
    nextTick(() => {
      rightPanelRef.value?.scrollToPath(lastPath)
    })
  }
}

const handleOrderRequest = async () => {
  if (listItems.value.length === 0) return
  const cleanList = JSON.parse(JSON.stringify(listItems.value))
  const success = await copyOrderRequest(cleanList)
  if (success) {
    isOrderPulseActive.value = true
    setTimeout(() => { isOrderPulseActive.value = false }, 450)
  }
}

const hasUnsavedChanges = computed(() => {
  if (listItems.value.length !== activeProject.selectedFiles.length) return true
  for (let i = 0; i < listItems.value.length; i++) {
    const cur = listItems.value[i]
    const orig = activeProject.selectedFiles[i]
    if (cur.path !== orig.path || cur.ignoreTokens !== orig.ignoreTokens) return true
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
  <div id="file-manager-modal" class="absolute inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
    <div class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[90vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden relative">

      <!-- Error Layer -->
      <OrderErrorModal v-if="showOrderErrorModal" :message="orderErrorMessage" @close="showOrderErrorModal = false" />

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar">
        <div class="flex items-center space-x-3">
          <h2 class="text-xl font-bold text-white">Edit Merge List</h2>
          <span class="text-gray-500 text-sm font-medium">/ {{ activeProject.name }}</span>
        </div>
        <button @click="handleCancel" class="text-gray-400 hover:text-white transition-colors" title="Close merge list editor">
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Main Content Split -->
      <div class="flex-grow flex min-0 overflow-hidden">
        <FileManagerLeftPanel
          id="fm-available-files"
          ref="leftPanelRef"
          :class="showFullPaths ? 'w-2/5' : 'w-1/2'"
          :fileTree="fileTree"
          v-model:isExtFilter="isExtFilter"
          v-model:isGitFilter="isGitFilter"
          :selectedPaths="listItems.map(f => f.path)"
          :expandedDirs="currentExpandedDirs"
          :highlightedPath="highlightedPath"
          :isLoading="isTreeLoading"
          @toggle-select="toggleFileSelect"
          @toggle-directory="toggleDirectorySelect"
          @remove-select="removeFileFromList"
          @file-click="onLeftFileClick"
          @toggle-expand="toggleFolderExpand"
          @add-all="addAll"
        />

        <FileManagerRightPanel
          id="fm-merge-order"
          ref="rightPanelRef"
          :class="showFullPaths ? 'w-3/5' : 'w-1/2'"
          :listItems="listItems"
          :filterText="filterText"
          :mergeListRef="mergeListRef"
          :totalTokens="totalTokens"
          :tokenColorClass="tokenColorClass"
          v-model:showFullPaths="showFullPaths"
          :isOrderPulseActive="isOrderPulseActive"
          @file-click="onRightFileClick"
          @token-interaction="handleTokenInteraction"
          @order-request="handleOrderRequest"
        />
      </div>

      <!-- Footer Actions -->
      <div
        id="fm-footer"
        class="px-6 py-3 border-t border-gray-700 bg-cm-top-bar flex items-center justify-between shrink-0"
        :class="{'has-changes': hasUnsavedChanges}"
      >

        <!-- Left Column: Spacer (Symmetry) -->
        <div class="footer-col-side flex justify-start"></div>

        <!-- Center Column: Filter Search -->
        <div class="footer-search-col mx-4">
          <div class="relative w-full">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              id="fm-filter-input"
              v-model="filterText"
              type="text"
              placeholder="Filter both lists..."
              class="w-full bg-cm-input-bg text-white pl-10 pr-10 py-1.5 rounded border border-gray-600 focus:border-cm-blue outline-none text-sm transition-all"
            >
            <button
              v-if="filterText"
              @click="filterText = ''"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
              title="Clear filter"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Right Column: Navigation Actions -->
        <div class="footer-col-side flex justify-end items-center space-x-3">
          <button
            @click="handleCancel"
            class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-1.5 px-6 rounded transition-colors text-sm shrink-0"
            :title="hasUnsavedChanges ? 'Discard modifications and exit' : 'Exit merge list editor'"
          >
            {{ hasUnsavedChanges ? 'Cancel' : 'Close' }}
          </button>
          <button
            id="btn-fm-save"
            v-if="hasUnsavedChanges"
            @click="handleSave"
            class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-1.5 px-10 rounded shadow-md transition-all flex items-center text-sm shrink-0"
            title="Commit changes and update the project merge list"
          >
            <Save class="w-4 h-4 mr-2" />
            Save Merge List
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.footer-col-side, .footer-search-col {
  transition: all 0.4s ease-in-out 0.1s;
}

.has-changes .footer-col-side,
.has-changes .footer-search-col {
  transition: all 0.4s ease-in-out;
}

.footer-col-side {
  flex: 1 1 0px;
  min-width: 90px;
}

.footer-search-col {
  flex: 1 1 auto;
  max-width: 448px;
  min-width: 180px;
  display: flex;
  justify-content: center;
}

.has-changes .footer-col-side:last-child {
  min-width: 240px;
  flex: 0 0 auto;
}

.has-changes .footer-search-col {
  flex-grow: 0;
  flex-basis: 320px;
  max-width: 320px;
}
</style>