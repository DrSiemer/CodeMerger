<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAppState } from '../composables/useAppState'
import {
  ClipboardPaste, Eye, Expand, AlertTriangle, Loader2, Trash2,
  Check, AlertCircle, HelpCircle
} from 'lucide-vue-next'

const app = useAppState()

const {
  activeProject,
  lastAiResponse,
  appIcon,
  getImage,
  copyCode,
  restoreMainWindow,
  closeApp,
  openProjectFolder,
  checkPendingChanges,
  clearPasteData,
  statusMessage,
  init,
  config,
  claimLastPlan
} = app

const isCopying = ref(false)
const hasPendingChangesInternal = ref(false)

// Feedback Banner State
const feedback = reactive({
  active: false,
  mode: 'none', // 'success' | 'error' | 'confirm'
  msg: '',
  type: '' // 'copy' | 'paste' | 'secrets' | 'overwrite'
})

const titleOverride = ref(null)

// Manual Window Dragging State
let isDragging = false
let startMouseX = 0
let startMouseY = 0
let startWinX = 0
let startWinY = 0
let lastClickTime = 0

// Interval for updating the notification status locally
let statusCheckInterval = null
let feedbackTimer = null
let titleTimer = null

const onBlur = () => {
  isDragging = false
}

const updatePendingStatus = async () => {
  if (!window.pywebview) return

  const status = await checkPendingChanges()
  hasPendingChangesInternal.value = status.has_pending

  // Cross-Window Synchronization
  if (status.exists && !lastAiResponse.value) {
    lastAiResponse.value = await claimLastPlan()
  } else if (!status.exists && lastAiResponse.value) {
    lastAiResponse.value = null
  }
}

const triggerFeedback = (mode, msg, type = '', duration = 1500) => {
  if (feedbackTimer) clearTimeout(feedbackTimer)

  feedback.mode = mode
  feedback.msg = msg
  feedback.type = type
  feedback.active = true

  if (mode !== 'confirm') {
    feedbackTimer = setTimeout(() => {
      feedback.active = false
    }, duration)
  }
}

const triggerTitleError = (msg) => {
  if (titleTimer) clearTimeout(titleTimer)
  titleOverride.value = msg
  titleTimer = setTimeout(() => {
    titleOverride.value = null
  }, 2000)
}

// Handle global shortcuts dispatched from App.vue while in Compact mode
const onShortcutPaste = (e) => {
  handlePaste({ ctrlKey: e.detail.isAuto })
}

const onShortcutCopy = (e) => {
  handleCopy({ ctrlKey: e.detail.codeOnly })
}

onMounted(async () => {
  // Ensure app state is loaded if compact mode is entry point
  await init()

  await updatePendingStatus()

  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
  window.addEventListener('blur', onBlur)

  window.addEventListener('cm-compact-paste', onShortcutPaste)
  window.addEventListener('cm-compact-copy', onShortcutCopy)

  statusCheckInterval = setInterval(updatePendingStatus, 2000)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
  window.removeEventListener('blur', onBlur)
  window.removeEventListener('cm-compact-paste', onShortcutPaste)
  window.removeEventListener('cm-compact-copy', onShortcutCopy)
  if (statusCheckInterval) clearInterval(statusCheckInterval)
  if (feedbackTimer) clearTimeout(feedbackTimer)
  if (titleTimer) clearTimeout(titleTimer)
})

const startDrag = async (e) => {
  if (e.target.closest('button')) return

  const now = Date.now()
  const isDblClick = (now - lastClickTime < 300)
  lastClickTime = now

  if (isDblClick) {
    isDragging = false
    restoreMainWindow()
    return
  }

  if (e.altKey) {
    const res = await openProjectFolder({ ctrlKey: false, altKey: true })
    if (res && res.includes('Error')) {
      triggerTitleError('CMD FAIL')
    }
    return
  }

  // Store pure logical mouse coordinates
  startMouseX = e.screenX
  startMouseY = e.screenY

  const pos = await window.pywebview.api.get_compact_window_pos()
  startWinX = pos.x
  startWinY = pos.y

  isDragging = true
}

const onMouseMove = (e) => {
  if (!isDragging) return

  // Calculate deltas in pure logical pixels and maps 1:1 to the backend
  const deltaXLogical = e.screenX - startMouseX
  const deltaYLogical = e.screenY - startMouseY

  window.pywebview.api.move_compact_window(startWinX + deltaXLogical, startWinY + deltaYLogical)
}

const onMouseUp = () => {
  isDragging = false
}

const handleCopy = async (event, bypassSecrets = null) => {
  if (!activeProject.path) return
  isCopying.value = true

  try {
    const useWrapper = activeProject.hasInstructions && !event.ctrlKey

    // Non-blocking secrets check: False means "check only"
    const result = await window.pywebview.api.copy_code(useWrapper, bypassSecrets || false)

    if (result && typeof result === 'object' && result.status === 'SECRETS_DETECTED') {
      triggerFeedback('confirm', 'Secrets found!', 'secrets')
      return
    }

    if (typeof result === 'string') {
      if (result.includes('Error') || result.includes('cancelled')) {
        triggerFeedback('error', result, 'copy', 3000)
      } else {
        triggerFeedback('success', 'COPIED', 'copy')
      }
    }
  } catch (err) {
    triggerFeedback('error', 'Copy Failed', 'copy', 3000)
  } finally {
    isCopying.value = false
  }
}

const handlePaste = async (event, forceOverwrite = false) => {
  if (!window.pywebview) return

  // Local check for pending changes to trigger inline confirmation instead of backend dialog
  if (hasPendingChangesInternal.value && !forceOverwrite) {
    triggerFeedback('confirm', 'Overwrite memory?', 'overwrite')
    return
  }

  try {
    const result = await window.pywebview.api.request_remote_paste(true, !!event.ctrlKey, forceOverwrite)

    if (result === true || typeof result === 'string') {
      lastAiResponse.value = await claimLastPlan()
    }

    await updatePendingStatus()

    if (typeof result === 'string') {
      if (result.includes('Error') || result.includes('empty')) {
        triggerFeedback('error', result, 'paste', 3000)
      } else {
        triggerFeedback('success', 'PASTED', 'paste')
      }
    } else if (result === true) {
      triggerFeedback('success', 'PASTED', 'paste')
    }
  } catch (err) {
    triggerFeedback('error', 'Paste Failed', 'paste', 3000)
  }
}

const handleConfirmChoice = async () => {
  const type = feedback.type
  feedback.active = false

  if (type === 'secrets') {
    // True means "bypass secrets check"
    await handleCopy({ ctrlKey: false }, true)
  } else if (type === 'overwrite') {
    await handlePaste({ ctrlKey: false }, true)
  }
}

const handleOpenReview = async () => {
  if (window.pywebview) {
    await window.pywebview.api.request_remote_review(true)
    await updatePendingStatus()
  }
}

const handleClear = async () => {
  await clearPasteData()
  await updatePendingStatus()
}

const handleClose = (event) => {
  if (event.ctrlKey) closeApp()
  else restoreMainWindow()
}

const handleNewFilesClick = async () => {
  if (window.pywebview) {
    await window.pywebview.api.restore_main_window_and_trigger_fm()
  }
}

const isUltra = computed(() => config.value.enable_ultra_compact_mode ?? false)

const titleAbbr = computed(() => {
  if (titleOverride.value) return titleOverride.value

  const name = activeProject.name || 'CodeMerger'

  if (isUltra.value) {
    return name.charAt(0).toUpperCase()
  }

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

const pasteTooltipText = computed(() => {
  const showReview = config.value.show_feedback_on_paste ?? true
  const base = showReview ? "Paste and Review changes" : "Paste and Apply changes immediately"
  const override = showReview ? "Apply immediately" : "Apply with Review"
  return `${base}\n(Ctrl-Click: ${override}, Alt-Click: manual window)`
})
</script>

<template>
  <div id="compact-view" class="h-full flex flex-col bg-cm-dark-bg border border-gray-600 select-none overflow-hidden font-sans">
    <!-- Header Draggable Bar -->
    <div
      v-if="!isUltra"
      id="compact-move-bar"
      class="h-7 bg-cm-top-bar flex items-center justify-between px-2 shrink-0 border-b border-gray-700 cursor-move"
      @mousedown="startDrag"
      title="Double-click to restore. Alt-Click to open Command Prompt."
    >
      <div class="flex items-center space-x-2 min-w-0 pointer-events-none h-full">
        <img v-if="appIcon" :src="appIcon" class="w-4 h-4 shrink-0" />
        <span
          class="text-[11px] font-mono font-bold tracking-widest px-1 rounded whitespace-nowrap overflow-hidden h-[18px] flex items-center pt-[1px] antialiased shrink-0 transition-colors duration-300"
          :style="{
            color: activeProject.fontColor === 'dark' || titleOverride ? '#000000' : '#FFFFFF',
            backgroundColor: titleOverride ? '#DF2622' : (activeProject.color || '#666666')
          }"
        >
          {{ titleAbbr }}
        </span>
      </div>

      <div class="flex items-center space-x-1.5 shrink-0 h-full">
        <button
          @mousedown.stop
          @click="handleClose"
          class="text-gray-400 hover:text-white transition-colors flex items-center justify-center"
          title="Restore dashboard (Ctrl-Click: Exit application)"
        >
          <Expand class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Actions & Feedback Area -->
    <div id="compact-content-root" class="relative flex-grow">

      <!-- Action Buttons Layer -->
      <div id="compact-actions" class="flex flex-col transition-opacity duration-200" :class="{ 'opacity-0 pointer-events-none': feedback.active, 'p-1.5 space-y-1.5': !isUltra, 'p-1 pb-0 items-center space-y-1': isUltra }">

        <!-- ULTRA COMPACT BLOCK -->
        <div v-if="isUltra" class="flex flex-col w-full">
          <!-- Draggable Header -->
          <div class="h-6 flex items-center px-1 cursor-move mb-0.5" @mousedown="startDrag">
            <img v-if="appIcon" :src="appIcon" class="w-4 h-4 shrink-0 pointer-events-none mr-1" />

            <div class="flex-grow flex justify-center pointer-events-none">
              <span
                class="text-[11px] font-mono font-bold w-5 rounded h-[18px] flex items-center justify-center antialiased shrink-0 transition-colors duration-300"
                :style="{
                  color: activeProject.fontColor === 'dark' || titleOverride ? '#000000' : '#FFFFFF',
                  backgroundColor: titleOverride ? '#DF2622' : (activeProject.color || '#666666')
                }"
              >
                {{ titleAbbr }}
              </span>
            </div>

            <button
              @mousedown.stop
              @click="handleClose"
              class="text-gray-500 hover:text-white transition-colors flex items-center justify-center h-5 w-5 shrink-0"
              title="Restore dashboard"
            >
              <Expand class="w-3.5 h-3.5" />
            </button>
          </div>

          <!-- Action Rows -->
          <div class="flex flex-col items-center space-y-1 w-full px-0.5">
            <!-- Row C -->
            <div class="flex items-center gap-1 w-full max-w-[64px]">
              <div class="relative flex-grow">
                <button
                  @click="handleCopy($event)"
                  @mousedown.stop
                  :disabled="isCopying"
                  class="w-full bg-cm-blue hover:bg-blue-500 text-white h-6 rounded flex items-center justify-center transition-all active:scale-95 disabled:opacity-50 text-[11px] font-black leading-none"
                  title="Copy Prompt with Instructions (Ctrl-Click: Code Only)"
                >
                  <Loader2 v-if="isCopying" class="w-3 h-3 animate-spin" />
                  <span v-else>C</span>
                </button>
              </div>
              <button
                v-if="activeProject.newFileCount > 0"
                @click="handleNewFilesClick"
                @mousedown.stop
                class="bg-gray-800 hover:bg-gray-700 text-cm-green w-6 h-6 rounded flex items-center justify-center transition-all active:scale-95 shadow shrink-0"
                title="New files detected! Click to manage."
              >
                <AlertTriangle class="w-3.5 h-3.5 animate-pulse" />
              </button>
            </div>

            <!-- Row P -->
            <div class="flex items-center gap-1 w-full max-w-[64px]">
              <div class="relative flex-grow">
                <button
                  @click="handlePaste($event)"
                  @mousedown.stop
                  class="w-full text-white h-6 rounded flex items-center justify-center transition-all active:scale-95 text-[11px] font-black leading-none"
                  :class="hasPendingChangesInternal ? 'bg-[#DE6808]' : 'bg-cm-green hover:bg-green-600'"
                  :title="pasteTooltipText"
                >
                  <span>P</span>
                </button>
                <button
                  v-if="hasPendingChangesInternal"
                  @click.stop="handleClear"
                  @mousedown.stop
                  class="absolute -top-1 -right-1 p-0.5 bg-gray-900 rounded-full text-white/70 hover:text-white shadow-sm border border-gray-700 transition-colors"
                  title="Clear unapplied response"
                >
                  <Trash2 class="w-2 h-2" />
                </button>
              </div>
              <button
                v-if="lastAiResponse"
                @click="handleOpenReview"
                @mousedown.stop
                class="w-6 h-6 rounded flex items-center justify-center transition-all active:scale-95 bg-gray-800 text-gray-400 hover:text-white shrink-0"
                title="View response review"
              >
                <Eye class="w-3.5 h-3.5" :class="hasPendingChangesInternal ? 'text-[#DE6808]' : 'text-gray-400'" />
              </button>
            </div>
          </div>
        </div>

        <!-- STANDARD COMPACT LAYOUT -->
        <template v-else>
          <!-- Copy/New Files Button Group -->
          <div class="flex items-center space-x-1.5 h-8">
            <button
              id="btn-compact-copy"
              @click="handleCopy($event)"
              :disabled="isCopying"
              class="flex-grow text-[11px] font-bold py-1.5 rounded shadow transition-all flex items-center justify-center space-x-2 disabled:opacity-50 active:scale-95 leading-tight h-8"
              :class="activeProject.hasInstructions ? 'bg-cm-blue hover:bg-blue-500 text-white' : 'bg-gray-300 hover:bg-gray-200 text-gray-900'"
              title="Copy with Instructions (Ctrl-Click: Code Only)"
            >
              <Loader2 v-if="isCopying" class="w-3.5 h-3.5 animate-spin" />
              <span v-else class="truncate px-1">Copy Prompt</span>
            </button>

            <!-- New Files Indicator -->
            <button
              v-if="activeProject.newFileCount > 0"
              @click="handleNewFilesClick"
              class="bg-gray-800 hover:bg-gray-700 text-cm-green w-6 py-1.5 rounded flex items-center justify-center transition-all active:scale-95 shadow shrink-0 h-8"
              title="New files detected! Click to manage."
            >
              <AlertTriangle class="w-4 h-4 animate-pulse" />
            </button>
          </div>

          <!-- Paste & Review Logic Row -->
          <div class="w-full flex items-center space-x-1.5">
            <div class="relative flex-grow flex h-8">
              <button
                id="btn-compact-paste"
                @click="handlePaste($event)"
                class="w-full text-white font-bold py-1.5 rounded text-[11px] transition-all active:scale-95 shadow h-full"
                :class="hasPendingChangesInternal ? 'bg-[#DE6808]' : 'bg-cm-green hover:bg-green-600'"
                :title="pasteTooltipText"
              >
                <span>Paste</span>
              </button>
              <button
                v-if="hasPendingChangesInternal"
                @click.stop="handleClear"
                class="absolute top-0.5 right-0.5 p-0.5 text-white/50 hover:text-white transition-colors"
                title="Clear unapplied response"
              >
                <Trash2 class="w-3 h-3" />
              </button>
            </div>

            <button
              id="btn-compact-review"
              v-if="lastAiResponse"
              @click="handleOpenReview"
              class="bg-gray-800 hover:bg-gray-700 text-white w-6 py-1.5 rounded flex items-center justify-center transition-all active:scale-95 shadow shrink-0 h-8"
              title="View response review"
            >
              <Eye class="w-3.5 h-3.5" :class="hasPendingChangesInternal ? 'text-[#DE6808]' : 'text-gray-400'" />
            </button>
          </div>
        </template>
      </div>

      <!-- Transient Feedback Layer -->
      <transition name="feedback-slide">
        <div
          v-if="feedback.active"
          class="absolute inset-0 z-50 p-1.5 flex flex-col"
        >
          <!-- Success/Error Banner -->
          <div
            v-if="feedback.mode !== 'confirm'"
            class="w-full h-full rounded shadow-lg flex items-center justify-center px-2 py-1 overflow-hidden"
            :class="feedback.mode === 'success' ? 'bg-cm-green' : 'bg-cm-warn'"
          >
             <div class="flex flex-col items-center justify-center text-center">
                <Check v-if="feedback.mode === 'success'" class="w-3.5 h-3.5 text-white mb-0.5 shrink-0" />
                <AlertCircle v-else class="w-3.5 h-3.5 text-white mb-0.5 shrink-0" />
                <span class="text-[9px] font-black text-white uppercase tracking-wider leading-tight whitespace-normal max-w-full px-1">
                   {{ feedback.msg }}
                </span>
             </div>
          </div>

          <!-- Choice/Confirmation Banner -->
          <div
            v-else
            class="w-full h-full rounded shadow-lg bg-[#DE6808] flex flex-col overflow-hidden"
          >
            <div class="flex-grow flex items-center justify-center px-2 py-1">
               <HelpCircle class="w-3.5 h-3.5 text-white mr-1.5 shrink-0" />
               <span class="text-[10px] font-bold text-white uppercase tracking-tighter leading-tight text-center whitespace-normal">
                  {{ feedback.msg }}
               </span>
            </div>
            <div class="flex h-8 border-t border-white/20">
              <button
                @click="handleConfirmChoice"
                class="flex-1 bg-white/10 hover:bg-white/20 text-white text-[9px] font-black uppercase tracking-widest transition-colors"
              >Confirm</button>
              <button
                @click="feedback.active = false"
                class="flex-1 bg-black/10 hover:bg-black/20 text-white/80 text-[9px] font-black uppercase tracking-widest transition-colors border-l border-white/20"
              >Abort</button>
            </div>
          </div>
        </div>
      </transition>

    </div>
  </div>
</template>

<style scoped>
button { -webkit-app-region: no-drag; }

.feedback-slide-enter-active,
.feedback-slide-leave-active {
  transition: transform 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67), opacity 0.2s ease;
}

.feedback-slide-enter-from {
  transform: translateY(10px);
  opacity: 0;
}

.feedback-slide-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>