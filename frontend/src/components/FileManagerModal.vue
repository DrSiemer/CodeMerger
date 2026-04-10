<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { X, RotateCcw, Save, Info } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { useDragAndDrop } from '@formkit/drag-and-drop/vue'
import FileManagerLeftPanel from './FileManagerLeftPanel.vue'
import FileManagerRightPanel from './FileManagerRightPanel.vue'
import InfoPanel from './InfoPanel.vue'

const emit = defineEmits(['close'])
const {
  activeProject, getFileTree, resizeWindow, updateProjectFiles,
  copyOrderRequest, clearUnknownFiles, statusMessage,
  infoModeActive, toggleInfoMode
} = useAppState()

// Reorderable list setup
const [mergeListRef, listItems] = useDragAndDrop(
  JSON.parse(JSON.stringify(activeProject.selectedFiles)),
  { handle: '.drag-handle' }
)

// State
const rightPanelRef = ref(null)
const fileTree = ref([])
const filterText = ref('')
const isExtFilter = ref(true)
const isGitFilter = ref(true)
const showFullPaths = ref(false)
const currentExpandedDirs = ref(new Set(activeProject.expandedDirs))
const isLoaded = ref(false)
const isOrderPulseActive = ref(false)

onMounted(async () => {
  await resizeWindow(1100, 800)
  await refreshTree()
  await autoHandleNewFiles()
  await clearUnknownFiles()
  isLoaded.value = true
})

const refreshTree = async () => {
  fileTree.value = await getFileTree(filterText.value, isExtFilter.value, isGitFilter.value)
}

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

watch([filterText, isExtFilter, isGitFilter], () => refreshTree())

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
  const idx = listItems.value.findIndex(f => f.path === path)
  if (idx !== -1) {
    listItems.value.splice(idx, 1)
    rightPanelRef.value?.clearSelection()
  } else {
    window.pywebview.api.get_token_count(path).then(tokens => {
      listItems.value.push({ path, tokens, ignoreTokens: false })
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
      listItems.value.push({ path, tokens, ignoreTokens: false })
    })
  })
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
        <FileManagerLeftPanel
          :fileTree="fileTree"
          v-model:filterText="filterText"
          v-model:isExtFilter="isExtFilter"
          v-model:isGitFilter="isGitFilter"
          :selectedPaths="listItems.map(f => f.path)"
          :expandedDirs="currentExpandedDirs"
          @toggle-select="toggleFileSelect"
          @toggle-expand="toggleFolderExpand"
          @add-all="addAll"
        />

        <FileManagerRightPanel
          ref="rightPanelRef"
          :listItems="listItems"
          :mergeListRef="mergeListRef"
          :totalTokens="totalTokens"
          :tokenColorClass="tokenColorClass"
          v-model:showFullPaths="showFullPaths"
          :isOrderPulseActive="isOrderPulseActive"
          @token-interaction="handleTokenInteraction"
          @order-request="handleOrderRequest"
        />
      </div>

      <!-- Shared Info Panel Component -->
      <InfoPanel />

      <!-- Footer Actions -->
      <div class="px-6 py-3 border-t border-gray-700 bg-cm-top-bar flex justify-between items-center shrink-0">
        <button
          @click="listItems.splice(0, listItems.length)"
          class="bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium py-1.5 px-6 rounded transition-colors flex items-center text-sm"
          v-info="'fm_remove_all'"
        >
          <RotateCcw class="w-3.5 h-3.5 mr-2" />
          Clear List
        </button>

        <div class="flex items-center space-x-6">
          <div class="flex items-center space-x-3">
            <button @click="handleCancel" class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-6 rounded transition-colors text-sm" v-info="'fm_cancel'">
              Cancel
            </button>
            <button @click="handleSave" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-1.5 px-10 rounded shadow-md transition-all flex items-center text-sm" v-info="'fm_save'">
              <Save class="w-4 h-4 mr-2" />
              Update Project
            </button>
          </div>

          <button @click="toggleInfoMode" v-info="'info_toggle'" class="transition-colors shrink-0" :class="infoModeActive ? 'text-cm-blue hover:text-blue-400' : 'text-gray-400 hover:text-white'" title="Toggle Info Mode">
            <Info class="w-5 h-5" />
          </button>
        </div>
      </div>

    </div>
  </div>
</template>