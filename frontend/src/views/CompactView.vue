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
  statusMessage
} = useAppState()

const isCopying = ref(false)
const appIcon = ref('')

// Manual Window Dragging State
let isDragging = false
let startMouseX = 0
let startMouseY = 0
let startWinX = 0
let startWinY = 0

const onBlur = () => {
  // Critical Failsafe: if the window loses focus, drop any dragging state
  // to prevent the "cursor capture" bug.
  isDragging = false
}

onMounted(async () => {
  appIcon.value = await getImage('icon.ico')
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
  window.addEventListener('blur', onBlur)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
  window.removeEventListener('blur', onBlur)
})

const startDrag = async (e) => {
  // Guard: ensure button clicks don't trigger dragging
  if (e.target.closest('button')) return

  // Alt-click: Open console in project folder
  if (e.altKey) {
    openProjectFolder({ ctrlKey: false, altKey: true })
    return
  }

  // Capture screen position of the mouse
  startMouseX = e.screenX
  startMouseY = e.screenY

  // Fetch actual window coordinates from Python bridge (Compact specific API)
  const pos = await window.pywebview.api.get_compact_window_pos()
  startWinX = pos.x
  startWinY = pos.y

  // Set dragging state only after data is ready to prevent jump artifacts
  isDragging = true
}

const onMouseMove = (e) => {
  if (!isDragging) return

  const deltaX = e.screenX - startMouseX
  const deltaY = e.screenY - startMouseY

  const newX = startWinX + deltaX
  const newY = startWinY + deltaY

  // Move the compact window specifically
  window.pywebview.api.move_compact_window(newX, newY)
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
    // We call a special remote-paste method that targets the main window's browser context.
    // Holding Ctrl triggers 'Auto-Apply' (matching Tkinter behavior).
    const result = await window.pywebview.api.request_remote_paste(true, !!event.ctrlKey)

    // Display returned status messages (e.g. "Already up to date")
    if (typeof result === 'string') {
      statusMessage.value = result
    }
  }
}

const handleClose = (event) => {
  if (event.ctrlKey) {
    closeApp()
  } else {
    restoreMainWindow()
  }
}

/**
 * Logic for project name abbreviation - EXACT port from Tkinter version.
 * Prioritizes capital letters, then fills remaining 8 slots with lowercase from the start.
 */
const titleAbbr = computed(() => {
  const name = activeProject.name || 'CodeMerger'
  const maxLen = 8
  const chars = [...name]

  // Identify uppercase indices
  const capitalIndices = []
  for (let i = 0; i < chars.length; i++) {
    if (chars[i] >= 'A' && chars[i] <= 'Z') {
      capitalIndices.push(i)
    }
  }

  if (capitalIndices.length > 1) {
    // Identify lowercase indices
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

    // Sort to maintain relative character positions
    indicesToKeep.sort((a, b) => a - b)
    return indicesToKeep.map(i => chars[i]).join('')
  } else {
    // Fallback for single-case or short names
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
    <!-- Manual Drag Header -->
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
        <!-- Alert icon if new files -->
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

    <!-- Content Stack - Tightened Spacing -->
    <div class="flex-grow flex flex-col p-1.5 space-y-1.5 justify-center">

      <!-- Adaptive Copy Button -->
      <button
        @click="handleCopy"
        :disabled="isCopying"
        class="w-full text-[11px] font-bold py-2.5 rounded shadow transition-all flex items-center justify-center space-x-2 disabled:opacity-50 active:scale-95 leading-tight h-8"
        :class="activeProject.hasInstructions ? 'bg-cm-blue hover:bg-blue-500 text-white' : 'bg-gray-300 hover:bg-gray-200 text-gray-900'"
        title="Copy Prompt (Ctrl+Click for Code Only)"
      >
        <Loader2 v-if="isCopying" class="w-3.5 h-3.5 animate-spin" />
        <span v-else class="truncate px-1">{{ copyButtonText }}</span>
      </button>

      <!-- Paste & Review Bar -->
      <div class="w-full flex items-center space-x-1.5">
        <button
          @click="handlePaste"
          class="flex-grow bg-cm-green hover:bg-green-600 text-white font-bold py-2.5 rounded text-[11px] transition-all active:scale-95 shadow"
          title="Paste response from AI (Ctrl+Click to auto-apply)"
        >
          Paste
        </button>

        <button
          v-if="lastAiResponse"
          @click="restoreMainWindow"
          class="bg-orange-600 hover:bg-orange-500 text-white w-4 py-2.5 rounded flex items-center justify-center transition-all active:scale-95 shadow shrink-0"
          title="View response review"
        >
          <!-- Small vertical orange bar matching original UI -->
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Ensure dragging doesn't interfere with child interactions */
button {
  -webkit-app-region: no-drag;
}
</style>