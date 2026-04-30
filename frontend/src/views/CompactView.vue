<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAppState } from '../composables/useAppState'
import { Expand } from 'lucide-vue-next'
import { COMPACT_TITLE_MAX_LEN } from '../utils/constants'
import CompactFeedbackOverlay from '../components/compact/CompactFeedbackOverlay.vue'
import CompactActionsStandard from '../components/compact/CompactActionsStandard.vue'
import CompactActionsUltra from '../components/compact/CompactActionsUltra.vue'

const app = useAppState()
const {
  activeProject, lastAiResponse, appIcon, copyCode, restoreMainWindow,
  closeApp, openProjectFolder, checkPendingChanges, clearPasteData, init, config, claimLastPlan,
  addAllNewFiles
} = app

const isCopying = ref(false)
const hasPendingChangesInternal = ref(false)
const feedback = reactive({ active: false, mode: 'none', msg: '', type: '' })
const titleOverride = ref(null)

// Handlers and variables remain in-view to ensure zero-latency window dragging
const localWinX = ref(0), localWinY = ref(0)
let isDragging = false, ticking = false
let startMouseX = 0, startMouseY = 0, startWinX = 0, startWinY = 0, lastClickTime = 0

const onBlur = () => { isDragging = false }
const onMouseUp = () => { isDragging = false }

const startDrag = (e) => {
  if (e.target.closest('button')) return
  const now = Date.now()
  if (now - lastClickTime < 300) { isDragging = false; restoreMainWindow(); return }
  lastClickTime = now
  if (e.altKey || e.ctrlKey) {
    openProjectFolder({ ctrlKey: e.ctrlKey, altKey: e.altKey }).then(res => {
      if (res && res.includes('Error')) {
        triggerTitleError(e.altKey ? 'CMD FAIL' : 'COPY FAIL')
      } else if (e.ctrlKey) {
        triggerFeedback('success', 'Path copied', 'copy-path')
      }
    })
    return
  }
  startMouseX = e.screenX; startMouseY = e.screenY
  startWinX = localWinX.value; startWinY = localWinY.value
  isDragging = true
}

const onMouseMove = (e) => {
  if (!isDragging || ticking) return
  ticking = true
  requestAnimationFrame(() => {
    if (!isDragging) { ticking = false; return }
    const deltaXLogical = e.screenX - startMouseX
    const deltaYLogical = e.screenY - startMouseY
    const newX = startWinX + deltaXLogical
    const newY = startWinY + deltaYLogical
    localWinX.value = newX; localWinY.value = newY
    window.pywebview.api.move_compact_window(newX, newY)
    ticking = false
  })
}

// --- Logic Handlers ---
let statusCheckInterval = null, feedbackTimer = null, titleTimer = null

const updatePendingStatus = async () => {
  if (!window.pywebview || !window.pywebview.api) return

  // Synchronizes local coordinates with the backend to prevent drag offsets
  const pos = await window.pywebview.api.get_compact_window_pos()
  if (pos) {
    localWinX.value = pos.x
    localWinY.value = pos.y
  }

  const status = await checkPendingChanges()
  hasPendingChangesInternal.value = status.has_pending
  if (status.exists && !lastAiResponse.value) lastAiResponse.value = await claimLastPlan()
  else if (!status.exists && lastAiResponse.value) lastAiResponse.value = null
}

const triggerFeedback = (mode, msg, type = '', duration = 1500) => {
  if (feedbackTimer) clearTimeout(feedbackTimer)
  feedback.mode = mode; feedback.msg = msg; feedback.type = type; feedback.active = true
  if (mode !== 'confirm') feedbackTimer = setTimeout(() => { feedback.active = false }, duration)
}

const triggerTitleError = (msg) => {
  if (titleTimer) clearTimeout(titleTimer)
  titleOverride.value = msg
  titleTimer = setTimeout(() => { titleOverride.value = null }, 2000)
}

const handleCopy = async (event, bypassSecrets = null) => {
  if (!activeProject.path) return
  isCopying.value = true
  try {
    const isCtrl = event.ctrlKey
    const useWrapper = activeProject.hasInstructions && !isCtrl
    const result = await window.pywebview.api.copy_code(useWrapper, bypassSecrets || false)
    if (result && typeof result === 'object' && result.status === 'SECRETS_DETECTED') {
      triggerFeedback('confirm', 'Secrets found!', 'secrets'); return
    }
    if (typeof result === 'string') {
      if (result.includes('Error') || result.includes('cancelled')) triggerFeedback('error', result, 'copy', 3000)
      else triggerFeedback('success', 'COPIED', isCtrl ? 'copy-only' : 'copy')
    }
  } catch (err) { triggerFeedback('error', 'Copy Failed', 'copy', 3000)
  } finally { isCopying.value = false }
}

const handlePaste = async (event, forceOverwrite = false) => {
  if (!window.pywebview) return
  const force = (event.altKey && hasPendingChangesInternal.value) || forceOverwrite
  if (hasPendingChangesInternal.value && !force) { triggerFeedback('confirm', 'Overwrite memory?', 'overwrite'); return }
  try {
    const result = await window.pywebview.api.request_remote_paste(true, !!event.ctrlKey, force)
    if (result === true || typeof result === 'string') lastAiResponse.value = await claimLastPlan()
    await updatePendingStatus()
    if (typeof result === 'string') triggerFeedback(result.includes('Error') || result.includes('empty') ? 'error' : 'success', result.includes('Error') || result.includes('empty') ? result : 'PASTED', 'paste', 3000)
    else if (result === true) triggerFeedback('success', 'PASTED', 'paste')
  } catch (err) { triggerFeedback('error', 'Paste Failed', 'paste', 3000) }
}

const handleClear = async () => { await clearPasteData(); await updatePendingStatus() }

const handleOpenReview = async () => {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.request_remote_review(true)
    await updatePendingStatus()
  }
}

const handleRestore = (e) => {
  if (e.ctrlKey) closeApp()
  else restoreMainWindow()
}

const handleManage = async (event) => {
  if (event?.ctrlKey) {
    await addAllNewFiles()
    triggerFeedback('success', 'Files Added', 'add-files')
    return
  }
  if (window.pywebview && window.pywebview.api) await window.pywebview.api.restore_main_window_and_trigger_fm()
}

const handleCancelFeedback = () => {
  if (feedbackTimer) clearTimeout(feedbackTimer)
  feedback.active = false
}

const handleConfirmChoice = async () => {
  const type = feedback.type
  handleCancelFeedback()
  if (type === 'secrets') await handleCopy({ ctrlKey: false }, true)
  else if (type === 'overwrite') await handlePaste({ ctrlKey: false }, true)
}

onMounted(async () => {
  await init()
  if (window.pywebview && window.pywebview.api) {
    const pos = await window.pywebview.api.get_compact_window_pos()
    localWinX.value = pos.x; localWinY.value = pos.y
  }
  await updatePendingStatus()
  window.addEventListener('mousemove', onMouseMove); window.addEventListener('mouseup', onMouseUp)
  window.addEventListener('blur', onBlur)
  window.addEventListener('cm-compact-paste', (e) => handlePaste({ ctrlKey: e.detail.isAuto }))
  window.addEventListener('cm-compact-copy', (e) => handleCopy({ ctrlKey: e.detail.codeOnly }))
  window.addEventListener('cm-shortcut-path-copy', () => triggerFeedback('success', 'Path copied', 'copy-path'))
  window.addEventListener('cm-project-reloaded', updatePendingStatus)
  statusCheckInterval = setInterval(updatePendingStatus, 2000)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove); window.removeEventListener('mouseup', onMouseUp)
  window.removeEventListener('blur', onBlur)
  if (statusCheckInterval) clearInterval(statusCheckInterval)
  if (feedbackTimer) clearTimeout(feedbackTimer)
  if (titleTimer) clearTimeout(titleTimer)
})

const isUltra = computed(() => config.value.enable_ultra_compact_mode ?? false)
const titleAbbr = computed(() => {
  if (titleOverride.value) return titleOverride.value
  const name = activeProject.name || 'CodeMerger'
  if (isUltra.value) return name.charAt(0).toUpperCase()
  const maxLen = COMPACT_TITLE_MAX_LEN, chars = [...name], capIdx = []
  for (let i = 0; i < chars.length; i++) if (chars[i] >= 'A' && chars[i] <= 'Z') capIdx.push(i)
  if (capIdx.length > 1) {
    const lowIdx = []
    for (let i = 0; i < chars.length; i++) if (chars[i] >= 'a' && chars[i] <= 'z') lowIdx.push(i)
    const needed = maxLen - capIdx.length
    let indices = needed > 0 ? [...capIdx, ...lowIdx.slice(0, needed)] : capIdx.slice(0, maxLen)
    indices.sort((a, b) => a - b)
    return indices.map(i => chars[i]).join('')
  }
  return name.replace(/\s/g, '').slice(0, maxLen)
})

const pasteTooltipText = computed(() => {
  const showReview = config.value.show_feedback_on_paste ?? true
  return `${showReview ? "Paste and Review changes" : "Paste and Apply changes immediately"}\n(Ctrl-Click: ${showReview ? "Apply immediately" : "Apply with Review"}, Alt-Click: overwrite existing response)`
})
</script>

<template>
  <div id="compact-view" class="h-full flex flex-col bg-cm-dark-bg border border-gray-600 select-none overflow-hidden font-sans">
    <!-- Header (Draggable Zone) -->
    <div v-if="!isUltra" id="compact-move-bar" @mousedown="startDrag" class="h-7 bg-cm-top-bar flex items-center justify-between px-2 shrink-0 border-b border-gray-700 cursor-move" title="Double-click: Restore | Ctrl-Click: Copy Path | Alt-Click: CMD">
      <div class="flex items-center space-x-2 min-w-0 pointer-events-none h-full">
        <img v-if="appIcon" :src="appIcon" class="w-4 h-4 shrink-0" />
        <span class="text-[11px] font-mono font-bold tracking-widest px-1 rounded whitespace-nowrap overflow-hidden h-[18px] flex items-center pt-[1px] antialiased shrink-0 transition-colors duration-300" :style="{ color: activeProject.fontColor === 'dark' || titleOverride ? '#000000' : '#FFFFFF', backgroundColor: titleOverride ? '#DF2622' : (activeProject.color || '#666666') }">{{ titleAbbr }}</span>
      </div>
      <div class="flex items-center space-x-1.5 shrink-0 h-full">
        <button @mousedown.stop @click="handleRestore" class="text-gray-400 hover:text-white transition-colors flex items-center justify-center" title="Restore dashboard (Ctrl-Click: Exit)"><Expand class="w-4 h-4" /></button>
      </div>
    </div>

    <div id="compact-content-root" class="relative flex-grow">
      <div id="compact-actions" class="flex flex-col transition-opacity duration-200" :class="{ 'opacity-0 pointer-events-none': feedback.active }">
        <div v-if="isUltra" class="flex flex-col w-full pt-0.5">
          <div class="h-6 flex items-center px-1 cursor-move" @mousedown="startDrag" title="Drag to move. Double-click: Restore | Ctrl-Click: Copy Path | Alt-Click: CMD">
            <img v-if="appIcon" :src="appIcon" class="w-4 h-4 shrink-0 pointer-events-none mr-1" />
            <div class="flex-grow flex justify-center pointer-events-none">
              <span class="text-[11px] font-mono font-bold w-5 rounded h-[18px] flex items-center justify-center antialiased shrink-0 transition-colors duration-300" :style="{ color: activeProject.fontColor === 'dark' || titleOverride ? '#000000' : '#FFFFFF', backgroundColor: titleOverride ? '#DF2622' : (activeProject.color || '#666666') }">{{ titleAbbr }}</span>
            </div>
            <button @mousedown.stop @click="handleRestore" class="text-gray-500 hover:text-white transition-colors flex items-center justify-center h-5 w-5 shrink-0"><Expand class="w-3.5 h-3.5" /></button>
          </div>
          <CompactActionsUltra
            :is-copying="isCopying" :new-file-count="activeProject.newFileCount" :has-pending="hasPendingChangesInternal" :has-last-response="!!lastAiResponse" :paste-tooltip="pasteTooltipText"
            @copy="handleCopy" @paste="handlePaste" @clear="handleClear" @review="handleOpenReview" @manage="handleManage"
          />
        </div>

        <CompactActionsStandard v-else
          :is-copying="isCopying" :has-instructions="activeProject.hasInstructions" :new-file-count="activeProject.newFileCount" :has-pending="hasPendingChangesInternal" :has-last-response="!!lastAiResponse" :paste-tooltip="pasteTooltipText"
          @copy="handleCopy" @paste="handlePaste" @clear="handleClear" @review="handleOpenReview" @manage="handleManage"
        />
      </div>

      <CompactFeedbackOverlay :feedback="feedback" :is-ultra="isUltra" @confirm="handleConfirmChoice" @cancel="handleCancelFeedback" />
    </div>
  </div>
</template>

<style scoped>
button { -webkit-app-region: no-drag; }
</style>