<script setup>
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppState } from './composables/useAppState'
import InfoPanel from './components/InfoPanel.vue'
import { Info } from 'lucide-vue-next'

const {
  init,
  statusMessage,
  statusVisible,
  infoModeActive,
  toggleInfoMode,
  getClipboardText,
  copyCode,
  activeProject
} = useAppState()
const route = useRoute()

const isCompact = computed(() => route.path === '/compact')

onMounted(() => {
  const signalReady = async () => {
    await init()

    const waitForBridgeAndSignal = async (attempts = 0) => {
      if (window.pywebview && window.pywebview.api) {
        await window.pywebview.api.signal_ui_ready()
      } else if (attempts < 150) {
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
  })
})
</script>

<template>
  <div id="app-wrapper" class="h-screen w-screen bg-cm-dark-bg text-gray-100 flex flex-col font-sans selection:bg-cm-blue selection:text-white overflow-hidden">

    <!-- Content Area (Relative for absolute modals) -->
    <div id="content-area" class="flex-grow relative overflow-hidden flex flex-col">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>

    <!-- Global Layout Footer (Hidden in Compact Mode) -->
    <!-- z-50 ensures the footer area is ABOVE any backgrounds but distinct from modal absolute content -->
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