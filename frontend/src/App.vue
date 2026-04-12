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
  toggleInfoMode
} = useAppState()
const route = useRoute()

const isCompact = computed(() => route.path === '/compact')

onMounted(() => {
  const signalReady = async () => {
    // Run core initialization logic
    await init()

    // Reduced delay to allow initial paint to stabilize before hiding splash.
    // This improves perceived startup speed.
    setTimeout(async () => {
      if (window.pywebview) {
        // Signal ready to transition from Splash to Main UI.
        // We signal regardless of route to ensure the transition completes
        // even if the router hasn't fully synchronized the initial '/' path.
        await window.pywebview.api.signal_ui_ready()
      }
    }, 50)
  }

  if (window.pywebview) {
    signalReady()
  } else {
    window.addEventListener('pywebviewready', () => {
      signalReady()
    })
  }
})
</script>

<template>
  <div class="h-screen w-screen bg-cm-dark-bg text-gray-100 flex flex-col font-sans selection:bg-cm-blue selection:text-white overflow-hidden">

    <!-- Content Area (Relative for absolute modals) -->
    <div class="flex-grow relative overflow-hidden flex flex-col">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>

    <!-- Global Layout Footer (Hidden in Compact Mode) -->
    <!-- z-50 ensures the footer area is ABOVE any backgrounds but distinct from modal absolute content -->
    <template v-if="!isCompact">
      <div class="relative z-50 flex flex-col">
        <!-- Shared Info Panel Component -->
        <InfoPanel />

        <!-- Global Status Bar -->
        <footer class="bg-cm-status-bg text-gray-300 px-6 py-2 flex items-center justify-between text-sm font-medium shrink-0 h-[36px]">
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