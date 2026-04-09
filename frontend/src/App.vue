<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppState } from './composables/useAppState'

const { init } = useAppState()
const route = useRoute()

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

    <!-- View Slot -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

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