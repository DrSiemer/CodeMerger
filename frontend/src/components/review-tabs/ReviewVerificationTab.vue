<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ChevronLeft, ChevronRight, ArrowUpRight, FolderOpen } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'
import MarkdownRenderer from '../MarkdownRenderer.vue'

const {
  lastAiResponse,
  editorFontSize,
  verificationHistory,
  openProjectFolder,
  activeProject
} = useAppState()

const selectedHistoryIndex = ref(0)

const currentPlanHasVerification = computed(() => {
  const v = lastAiResponse.value?.verification
  return !!(v && v !== '-' && v.trim().length > 0)
})

// Combine history and staged verification into one navigable sequence
const allVerifications = computed(() => {
  const combined = [...verificationHistory.value.map(h => ({ ...h, isArchive: true }))]
  const currentV = lastAiResponse.value?.verification || ''

  if (currentPlanHasVerification.value) {
    combined.push({
      content: currentV,
      timestamp: 'Current',
      isArchive: false
    })
  }
  return combined
})

const currentVerificationView = computed(() => {
  const list = allVerifications.value
  if (list.length === 0) return null
  const idx = Math.min(selectedHistoryIndex.value, list.length - 1)
  return list[idx]
})

const isHistorical = computed(() => {
  const view = currentVerificationView.value
  return view && view.isArchive
})

const isLatest = computed(() => selectedHistoryIndex.value === allVerifications.value.length - 1)

onMounted(() => {
  if (allVerifications.value.length > 0) {
    selectedHistoryIndex.value = allVerifications.value.length - 1
  }
})

// Reset navigation index whenever a new AI response is pasted
watch(lastAiResponse, () => {
  if (allVerifications.value.length > 0) {
    selectedHistoryIndex.value = allVerifications.value.length - 1
  }
})
</script>

<template>
  <div class="relative min-h-full review-verification-container">
    <!-- Floating Toolbar (History & Folder Access) -->
    <div
      class="relative z-20 float-right ml-6 mb-2 flex flex-col items-end space-y-2 select-none pointer-events-auto"
      :class="isHistorical || allVerifications.length <= 1 ? 'opacity-100' : 'opacity-40 hover:opacity-100 transition-opacity'"
    >
      <!-- Quick Folder Access -->
      <button
        v-if="activeProject.path"
        @click="openProjectFolder($event)"
        v-info="'folder_icon'"
        class="p-2 text-gray-400 hover:text-white bg-black/40 border border-gray-700 rounded-md shadow-sm transition-colors"
        title="Open project folder (Ctrl-Click: Copy Path, Alt-Click: Open Command Prompt)"
      >
        <FolderOpen class="w-5 h-5" />
      </button>

      <!-- Verification History Navigation -->
      <div
        v-if="allVerifications.length > 1"
        v-info="'review_verification_history'"
        class="flex items-center space-x-1 bg-black/40 border border-gray-700 rounded-md p-1 shadow-sm"
      >
        <button
          @click="selectedHistoryIndex--"
          :disabled="selectedHistoryIndex <= 0"
          class="p-1 text-gray-400 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
          title="Previous verification"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <div class="px-2 text-[10px] font-mono text-gray-400 tracking-tighter">
          {{ selectedHistoryIndex + 1 }} / {{ allVerifications.length }}
        </div>
        <button
          @click="selectedHistoryIndex++"
          :disabled="selectedHistoryIndex >= allVerifications.length - 1"
          class="p-1 text-gray-400 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
          title="Next verification"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>

      <button
        v-if="!isLatest"
        @click="selectedHistoryIndex = allVerifications.length - 1"
        v-info="'review_verification_current'"
        class="flex items-center space-x-1 px-2 py-1 text-[9px] font-black uppercase tracking-[0.15em] text-cm-blue hover:text-blue-300 transition-colors bg-blue-500/5 rounded border border-cm-blue/20"
        title="Jump to current verification"
      >
        <ArrowUpRight class="w-3 h-3" />
        <span>Current</span>
      </button>
    </div>

    <!-- Content Body -->
    <div :class="{'opacity-80 grayscale-[0.3] border-l-4 border-yellow-700/40 pl-6 py-1': isHistorical}">
      <!-- Consolidated History Badge -->
      <div v-if="isHistorical" class="mb-4">
        <div class="inline-flex items-center px-2 py-0.5 rounded bg-yellow-900/30 text-yellow-500 text-[10px] font-black uppercase tracking-[0.2em] border border-yellow-700/50">
          Verification from {{ currentVerificationView?.timestamp }}
        </div>
      </div>

      <MarkdownRenderer v-if="currentVerificationView" :content="currentVerificationView.content" :fontSize="editorFontSize" />
      <div v-else class="text-gray-500 italic py-10 text-center">
        No verification steps provided.
      </div>
    </div>

    <div class="clear-both"></div>
  </div>
</template>

<style scoped>
:deep(.cm-verification-note) {
  margin-top: 1rem;
  opacity: 0.9;
}
</style>