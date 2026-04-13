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
  cancelLoadProject
} = useAppState()
const route = useRoute()
const router = useRouter()

const isCompact = computed(() => {
  // Use router state if available, but fallback to raw location hash for initial production render
  return route.path === '/compact' || window.location.hash.toLowerCase().includes('compact')
})

onMounted(() => {
  const signalReady = async () => {
    const waitForBridgeAndSignal = async (attempts = 0) => {
      // PyWebView injection can be slow on localhost, so we check specifically for the api object
      if (window.pywebview && window.pywebview.api) {
        try {
          // Ensure Router is fully synchronized with the window URL before signaling ready
          await router.isReady()

          // Ensure initial hash navigation is picked up in production WebView
          if (window.location.hash.toLowerCase().includes('compact') && route.path !== '/compact') {
            await router.push('/compact')
          }

          await window.pywebview.api.signal_ui_ready()
          init()
        } catch (err) {
          console.error("Ready signal error:", err)
        }
      } else if (attempts < 200) { // Support slow dev startup (approx 4s total polling)
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

  window.addEventListener('paste', (e) => {
    e.preventDefault()
  }, true)

  window.addEventListener('keydown', async (e) => {
    const isCtrl = e.ctrlKey || e.metaKey
    const isShift = e.shiftKey
    const key = e.key.toLowerCase()

    if (isCtrl && key === 'v') {
      e.preventDefault()

      // Text Input Routing (Project Starter / Modals)
      const activeEl = document.activeElement
      const isInput = activeEl && (activeEl.tagName === 'TEXTAREA' || (activeEl.tagName === 'INPUT' && activeEl.type === 'text'))

      if (isInput) {
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

      // Feature Routing
      if (isCompact.value) {
        // Notify Compact view to trigger its specific cross-window paste request
        window.dispatchEvent(new CustomEvent('cm-compact-paste', { detail: { isAuto: isShift } }))
      } else if (activeProject.path) {
        // Notify Dashboard to trigger response review or auto-apply
        window.dispatchEvent(new CustomEvent('cm-shortcut-paste', { detail: { toggleReview: isShift } }))
      }
    }

    if (isCtrl && key === 'c') {
      // Feature routing for Prompts (if no text is currently selected in UI)
      const selection = window.getSelection().toString()
      if (!selection && activeProject.path) {
        e.preventDefault()
        if (isCompact.value) {
          window.dispatchEvent(new CustomEvent('cm-compact-copy', { detail: { codeOnly: isShift } }))
        } else {
          // Dashboard copy: Ctrl+C = with instructions, Ctrl+Shift+C = code only
          await copyCode(!isShift)
        }
      }
    }

    if (isCtrl && key === '0') {
      e.preventDefault()
      resetEditorFontSize()
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
        <div class="bg-cm-top-bar border border-gray-600 rounded-2xl p-10 shadow-2xl flex flex-col items-center space-y-5">
          <Loader2 class="w-16 h-16 text-cm-blue animate-spin" />
          <div class="text-xl font-bold tracking-widest text-white uppercase">Scanning Project</div>

          <!-- Subtle Cancel Button -->
          <button
            @click="cancelLoadProject"
            class="text-gray-500 hover:text-gray-300 text-xs font-bold uppercase tracking-tighter transition-colors border-b border-transparent hover:border-gray-500 pt-2"
          >
            Cancel
          </button>
        </div>
      </div>
    </transition>

    <!-- Content Area (Relative for absolute modals) -->
    <div id="content-area" class="flex-grow relative overflow-hidden flex flex-col">
      <router-view />
    </div>

    <!-- Modal Layers -->
    <NewFiletypesModal v-if="newlyAddedFiletypes.length > 0" />

    <!-- Global Layout Footer (Hidden in Compact Mode) -->
    <template v-if="!isCompact">
      <div id="global-footer" class="relative z-50 flex flex-col">
        <!-- Shared Info Panel Component -->
        <InfoPanel />

        <!-- Global Status Bar -->
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