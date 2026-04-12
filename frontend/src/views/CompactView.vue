<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAppState } from '../composables/useAppState'
import {
  ClipboardPaste, Eye, Minimize2, AlertTriangle, Loader2
} from 'lucide-vue-next'

const {
  activeProject,
  lastAiResponse,
  getImage,
  copyCode,
  restoreMainWindow,
  closeApp,
  openProjectFolder,
  checkPendingChanges,
  statusMessage,
  init
} = useAppState()

const isCopying = ref(false)
const appIcon = ref('')
const hasPendingChangesInternal = ref(false)

// Manual Window Dragging State
let isDragging = false
let startMouseX = 0
let startMouseY = 0
let startWinX = 0
let startWinY = 0

// Interval for updating the notification status locally
let statusCheckInterval = null

const onBlur = () => {
  isDragging = false
}

const updatePendingStatus = async () => {
  hasPendingChangesInternal.value = await checkPendingChanges()
}

/**
 * Handles global shortcuts dispatched from App.vue while in Compact mode
 */
const onShortcutPaste = (e) => {
  handlePaste({ ctrlKey: e.detail.isAuto })
}

const onShortcutCopy = (e) => {
  handleCopy({ ctrlKey: e.detail.codeOnly })
}

onMounted(async () => {
  // Ensure app state is loaded if compact mode is entry point
  await init()

  appIcon.value = await getImage('icon.ico')
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
  window.addEventListener('blur', onBlur)

  // Listen for redirected shortcuts
  window.addEventListener('cm-compact-paste', onShortcutPaste)
  window.addEventListener('cm-compact-copy', onShortcutCopy)

  await updatePendingStatus()
  statusCheckInterval = setInterval(updatePendingStatus, 2000)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
  window.removeEventListener('blur', onBlur)
  window.removeEventListener('cm-compact-paste', onShortcutPaste)
  window.removeEventListener('cm-compact-copy', onShortcutCopy)
  if (statusCheckInterval) clearInterval(statusCheckInterval)
})

const startDrag = async (e) => {
  if (e.target.closest('button')) return

  if (e.altKey) {
    openProjectFolder({ ctrlKey: false, altKey: true })
    return
  }

  // Mouse coordinates (pure logical)
  startMouseX = e.screenX
  startMouseY = e.screenY

  // Get current logical window coordinates from bridge
  const pos = await window.pywebview.api.get_compact_window_pos()
  startWinX = pos.x
  startWinY = pos.y

  isDragging = true
}

const onMouseMove = (e) => {
  if (!isDragging) return

  // Calculate deltas in pure logical pixels and map 1:1 to the backend
  const deltaXLogical = e.screenX - startMouseX
  const deltaYLogical = e.screenY - startMouseY

  window.pywebview.api.move_compact_window(startWinX + deltaXLogical, startWinY + deltaYLogical)
}

const onMouseUp = () => {
  isDragging = false
}

const handleCopy = async (event) => {
  isCopying.value = true
  try {
    const useWrapper = activeProject.hasInstructions && !event.ctrlKey
    await copyCode(useWrapper)
  } finally {
    isCopying.value = false
  }
}

const handlePaste = async (event) => {
  if (window.pywebview) {
    const result = await window.pywebview.api.request_remote_paste(true, !!event.ctrlKey)
    await updatePendingStatus()
    if (typeof result === 'string') {
      statusMessage.value = result
    }
  }
}

const handleClose = (event) => {
  if (event.ctrlKey) closeApp()
  else restoreMainWindow()
}

const titleAbbr = computed(() => {
  const name = activeProject.name || 'CodeMerger'
  const maxLen = 8
  const chars = [...name]

  const capitalIndices = []
  for (let i = 0; i < chars.length; i++) {
    if (chars[i] >= 'A' && chars[i] <= 'Z') {
      capitalIndices.push(i)
    }
  }

  if (capitalIndices.length > 1) {
    const lowercaseIndices = []
    for (let i = 0; i < chars.length; i++) {
      if (chars[i] >= 'a' && chars[i] <= 'z') {
        lowercaseIndices.push(i)
      }
    }

    const lowercaseNeeded = maxLen - capitalIndices.length
    let indicesToKeep = []

    if (lowercaseNeeded > 0) {
      indicesToKeep = [...capitalIndices, ...lowercaseIndices.slice(0, lowercaseNeeded)]
    } else {
      indicesToKeep = capitalIndices.slice(0, maxLen)
    }

    indicesToKeep.sort((a, b) => a - b)
    return indicesToKeep.map(i => chars[i]).join('')
  } else {
    const noSpaceTitle = name.replace(/\s/g, '')
    return noSpaceTitle.slice(0, maxLen)
  }
})

const copyButtonText = computed(() => {
  return activeProject.hasInstructions ? 'Copy Prompt (i)' : 'Copy Prompt'
})
</script>

<template>
  <div class="h-full flex flex-col bg-cm-dark-bg border border-gray-600 select-none overflow-hidden font-sans">
    <!-- Header Draggable Bar -->
    <div
      class="h-7 bg-cm-top-bar flex items-center justify-between px-2 shrink-0 border-b border-gray-700 cursor-move"
      @mousedown="startDrag"
      @dblclick="restoreMainWindow"
      title="Double-click to restore"
    >
      <div class="flex items-center space-x-2 min-w-0 pointer-events-none">
        <img v-if="appIcon" :src="appIcon" class="w-4 h-4" />
        <span
          class="text-[9px] font-black tracking-widest px-1 py-0.5 rounded leading-none whitespace-nowrap overflow-hidden"
          :style="{ color: activeProject.fontColor === 'dark' ? '#000000' : '#FFFFFF', backgroundColor: activeProject.color || '#666666' }"
        >
          {{ titleAbbr }}
        </span>
      </div>

      <div class="flex items-center space-x-1.5 shrink-0">
        <!-- New Files Alert (Blinks green) -->
        <AlertTriangle
          v-if="activeProject.newFileCount > 0"
          class="w-3.5 h-3.5 text-cm-green animate-pulse"
          title="New files detected!"
        />
        <button
          @mousedown.stop
          @click="handleClose"
          class="text-gray-400 hover:text-white transition-colors"
          title="Restore dashboard (Ctrl+Click to exit)"
        >
          <Minimize2 class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Actions Area -->
    <div class="flex flex-col p-1.5 space-y-1.5">
      <!-- Adaptive Copy Button (Switches logic based on project instructions) -->
      <button
        @click="handleCopy"
        :disabled="isCopying"
        class="w-full text-[11px] font-bold py-1.5 rounded shadow transition-all flex items-center justify-center space-x-2 disabled:opacity-50 active:scale-95 leading-tight h-8"
        :class="activeProject.hasInstructions ? 'bg-cm-blue hover:bg-blue-500 text-white' : 'bg-gray-300 hover:bg-gray-200 text-gray-900'"
        title="Copy Prompt (Ctrl+Click for Code Only)"
      >
        <Loader2 v-if="isCopying" class="w-3.5 h-3.5 animate-spin" />
        <span v-else class="truncate px-1">{{ copyButtonText }}</span>
      </button>

      <!-- Paste & Review Logic Row -->
      <div class="w-full flex items-center space-x-1.5">
        <!-- Orange styling when changes are pending in memory -->
        <button
          @click="handlePaste"
          class="relative flex-grow text-white font-bold py-1.5 rounded text-[11px] transition-all active:scale-95 shadow h-8"
          :class="hasPendingChangesInternal ? 'bg-[#DE6808] hover:bg-orange-500' : 'bg-cm-green hover:bg-green-600'"
          title="Paste response from AI (Ctrl+Click to auto-apply)"
        >
          <span>Paste</span>
        </button>

        <button
          v-if="lastAiResponse"
          @click="restoreMainWindow"
          class="bg-gray-800 hover:bg-gray-700 text-white w-8 py-1.5 rounded flex items-center justify-center transition-all active:scale-95 shadow shrink-0 h-8"
          title="View response review"
        >
          <!-- Eye icon color mirrors the pending changes state -->
          <Eye class="w-3.5 h-3.5" :class="hasPendingChangesInternal ? 'text-[#DE6808]' : 'text-gray-400'" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Standard PyWebView override to allow button interaction inside draggable areas */
button { -webkit-app-region: no-drag; }
</style>