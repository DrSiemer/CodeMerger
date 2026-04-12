<script setup>
import { useAppState, currentInfoText, infoModeActive } from '../composables/useAppState'
import { INFO_MESSAGES } from '../utils/infoMessages'

/**
 * Singleton Refs imported directly from useAppState.js module scope.
 * This hard-links reactivity between the modals and footer.
 */
</script>

<template>
  <div v-if="infoModeActive" id="info-panel" class="bg-[#1A1A1A] border-t border-gray-700 h-[80px] shrink-0 flex items-center px-6 z-40">
    <p :class="currentInfoText === INFO_MESSAGES.default ? 'text-gray-500' : 'text-gray-300'" class="text-[13px] leading-relaxed">
      {{ currentInfoText }}
    </p>
  </div>
</template>