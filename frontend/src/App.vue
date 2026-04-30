<script setup>
import { onMounted, computed, watch, nextTick, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppState } from './composables/useAppState'
import InfoPanel from './components/InfoPanel.vue'
import NewFiletypesModal from './components/NewFiletypesModal.vue'
import { Info, Loader2 } from 'lucide-vue-next'

const {
  init,
  statusMessage,
  statusVisible,
  infoModeActive,
  toggleInfoMode,
  getClipboardText,
  copyCode,
  activeProject,
  newlyAddedFiletypes,
  resetEditorFontSize,
  isProjectLoading,
  cancelLoadProject,
  openProjectFolder
} = useAppState()
const route = useRoute()
const router = useRouter()

const isCompact = computed(() => {
  // Use location hash fallback for initial production render
  return route.path === '/compact' || window.location.hash.toLowerCase().includes('compact')
})

onMounted(() => {
  const signalReady = async () => {
    const waitForBridgeAndSignal = async (attempts = 0) => {
      if (window.pywebview && window.pywebview.api) {
        try {
          await router.isReady()

          if (window.location.hash.toLowerCase().includes('compact') && route.path !== '/compact') {
            await router.push('/compact')
          }

          await window.pywebview.api.signal_ui_ready()
          init()
        } catch (err) {
          console.error("Ready signal error:", err)
        }
      } else if (attempts < 1000) {
        setTimeout(() => waitForBridgeAndSignal(attempts + 1), 20)
      }
    }

    await waitForBridgeAndSignal()
  }

  if (window.pywebview) {
    signalReady()
  } else {
    window.addEventListener('pywebviewready', () => {
      signalReady()
    })
  }

  // Globally intercepting and preventing the browser paste event bypasses security popups and routes clipboard access exclusively through our Python pyperclip bridge
  window.addEventListener('paste', (e) => {
    e.preventDefault()
  }, true)

  window.addEventListener('keydown', async (e) => {
    if (isProjectLoading.value) return

    const isCtrl = e.ctrlKey || e.metaKey
    const isShift = e.shiftKey
    const key = e.key.toLowerCase()
    const activeEl = document.activeElement
    const isInput = activeEl && (activeEl.tagName === 'TEXTAREA' || (activeEl.tagName === 'INPUT' && activeEl.type === 'text') || activeEl.isContentEditable)

    if (isCtrl && key === 'v') {
      if (isInput) {
        e.preventDefault()
        const text = await getClipboardText()
        if (text) {
          const start = activeEl.selectionStart
          const end = activeEl.selectionEnd
          const val = activeEl.value
          activeEl.value = val.substring(0, start) + text + val.substring(end)
          activeEl.selectionStart = activeEl.selectionEnd = start + text.length
          activeEl.dispatchEvent(new Event('input', { bubbles: true }))
        }
        return
      }

      // Requirement: Block AI response pasting unless on the Main Screen or in Compact Mode
      if (isBlockingModalActive.value) return

      e.preventDefault()

      if (isCompact.value) {
        window.dispatchEvent(new CustomEvent('cm-compact-paste', { detail: { isAuto: isShift } }))
      } else if (activeProject.path) {
        window.dispatchEvent(new CustomEvent('cm-shortcut-paste', { detail: { toggleReview: isShift } }))
      }
    }

    if (isCtrl && key === 'c') {
      const selection = window.getSelection().toString()
      if (!selection && activeProject.path) {
        e.preventDefault()
        if (isCompact.value) {
          window.dispatchEvent(new CustomEvent('cm-compact-copy', { detail: { codeOnly: isShift } }))
        } else {
          await copyCode(!isShift)
        }
      }
    }

    if (isCtrl && key === '0') {
      e.preventDefault()
      resetEditorFontSize()
    }

    // Global Action Shortcuts (c: Console, f: Folder, p: Path)
    // Protected by isInput check to ensure they only fire when the window is focused but no input is active
    if (!isInput && !isCtrl && !e.metaKey && !e.altKey && !isShift && activeProject.path) {
      if (key === 'c') {
        e.preventDefault()
        await openProjectFolder({ ctrlKey: false, altKey: true })
      } else if (key === 'f') {
        e.preventDefault()
        await openProjectFolder({ ctrlKey: false, altKey: false })
      } else if (key === 'p') {
        e.preventDefault()
        await openProjectFolder({ ctrlKey: true, altKey: false })
        window.dispatchEvent(new CustomEvent('cm-shortcut-path-copy'))
      }
    }
  })
})
</script>

<template>
  <div id="app-wrapper" class="h-screen w-full bg-cm-dark-bg text-gray-100 flex flex-col font-sans selection:bg-cm-blue selection:text-white overflow-hidden">

    <!-- Global Loading Overlay -->
    <transition name="fade">
      <div
        v-if="isProjectLoading"
        id="loading-overlay"
        class="fixed inset-0 bg-black/60 z-[100] flex flex-col items-center justify-center pointer-events-auto"
      >
        <div class="bg-cm-top-bar border border-gray-600 rounded-2xl p-10 shadow-2xl flex flex-col items-center space-y-5 min-w-[320px]">
          <div class="flex justify-center items-center w-full">
            <Loader2 class="w-16 h-16 text-cm-blue animate-spin" />
          </div>
          <div class="text-xl font-bold tracking-widest text-white uppercase text-center w-full">Scanning Project</div>

          <button
            @click="cancelLoadProject"
            class="text-gray-500 hover:text-gray-300 text-xs font-bold uppercase tracking-tighter transition-colors border-b border-transparent hover:border-gray-500 pt-2"
          >
            Cancel
          </button>
        </div>
      </div>
    </transition>

    <div id="content-area" class="flex-grow relative overflow-hidden flex flex-col">
      <router-view />
    </div>

    <NewFiletypesModal v-if="newlyAddedFiletypes.length > 0" />

    <template v-if="!isCompact">
      <div id="global-footer" class="relative z-50 flex flex-col">
        <InfoPanel />

        <footer id="status-bar" class="bg-cm-status-bg text-gray-300 px-6 py-2 flex items-center justify-between text-sm font-medium shrink-0 h-[36px]">
          <div
            class="tracking-wide truncate pr-4"
            :class="statusVisible ? 'opacity-100' : 'opacity-0 transition-opacity duration-1000'"
          >
            {{ statusMessage }}
          </div>
          <button @click="toggleInfoMode" v-info="'info_toggle'" class="transition-colors shrink-0" :class="infoModeActive ? 'text-cm-blue hover:text-blue-400' : 'text-gray-400 hover:text-white'" title="Toggle Info Mode">
            <Info class="w-5 h-5" />
          </button>
        </footer>
      </div>
    </template>

  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>