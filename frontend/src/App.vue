<script setup>
import { onMounted } from 'vue'
import { useAppState } from './composables/useAppState'

const { init } = useAppState()

onMounted(() => {
  if (window.pywebview) {
    init()
  } else {
    window.addEventListener('pywebviewready', () => {
      init()
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