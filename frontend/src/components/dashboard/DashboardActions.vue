<script setup>
import { ref, computed } from 'vue'
import { Settings, Copy, ClipboardPaste, BookOpen, Eye, Loader2, Trash2, Zap } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const emit = defineEmits(['open-settings', 'open-instructions-modal', 'open-review-modal'])

const {
  activeProject,
  isProjectLoading,
  lastAiResponse,
  hasPendingChanges,
  copyCleanupPrompt,
  copyCode,
  processPaste,
  clearPasteData,
  config,
  toggleFastApply
} = useAppState()

const cleanupPulse = ref(false)

const isCopyingInstructions = ref(false)
const isCopyingOnly = ref(false)

const handleCleanup = async () => {
  cleanupPulse.value = true
  await copyCleanupPrompt()
  setTimeout(() => {
    cleanupPulse.value = false
  }, 450)
}

const handleCopy = async (useWrapper, event) => {
  const finalUseWrapper = useWrapper && !event.ctrlKey

  if (useWrapper) {
    isCopyingInstructions.value = true
  } else {
    isCopyingOnly.value = true
  }

  try {
    await copyCode(finalUseWrapper)
  } finally {
    isCopyingInstructions.value = false
    isCopyingOnly.value = false
  }
}

const handlePasteChanges = async () => {
  const success = await processPaste()
  if (success) {
    emit('open-review-modal', 'new')
  }
}

const openExistingReview = () => {
  emit('open-review-modal', 'resume')
}

const pasteTooltipText = computed(() => {
  const showReview = config.value.show_feedback_on_paste ?? true
  const base = showReview ? "Paste and Review changes (Ctrl+V)" : "Paste and Apply changes immediately (Ctrl+V)"
  const override = showReview ? "Apply immediately" : "Apply with Review"
  return `${base}\n(Ctrl-Click: ${override}, Alt-Click: open manual paste window)`
})
</script>

<template>
  <main id="dashboard-main" class="flex-grow flex flex-col relative bg-cm-dark-bg min-h-0 overflow-y-auto">
    <div class="absolute bottom-4 left-6 flex flex-col">
      <button id="btn-settings" @click="emit('open-settings', 'application')" class="text-gray-400 hover:text-white transition-colors" title="Application settings" v-info="'settings'">
        <Settings class="w-7 h-7" />
      </button>
    </div>

    <div class="flex-grow flex items-center justify-center pb-4">
      <div v-if="activeProject.path" id="dashboard-action-card" class="w-full max-w-[620px] border border-gray-600 rounded bg-cm-dark-bg p-6 flex flex-col shadow-sm">
        <div class="flex justify-between items-center mb-5">
          <h2 class="text-[17px] font-medium text-white">Actions</h2>

          <div class="flex items-center space-x-3">
            <!-- Mini Fast Apply Toggle -->
            <button
              @click="toggleFastApply"
              v-info="'fast_apply_toggle'"
              class="transition-all duration-300 p-1 rounded hover:bg-white/5"
              :class="(config.enable_fast_apply ?? true) ? 'text-cm-blue' : 'text-gray-600'"
              title="Toggle Fast Apply (Surgical Diffs)"
            >
              <Zap class="w-4 h-4" :fill="(config.enable_fast_apply ?? true) ? 'currentColor' : 'none'" />
            </button>

            <button
              id="btn-comment-cleanup"
              @click="handleCleanup"
              class="text-gray-500 hover:text-gray-300 text-sm font-mono font-bold transition-colors relative"
              :class="{ 'click-pulse': cleanupPulse }"
              :style="cleanupPulse ? { '--click-color': 'rgba(255, 255, 255, 0.2)' } : {}"
              title="Copy comment cleanup prompt"
              v-info="'cleanup'"
            >
              //
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <!-- Conditional Copy Button Layout -->
          <template v-if="activeProject.hasInstructions">
            <button
              id="btn-copy-with-instructions"
              @click="handleCopy(true, $event)"
              :disabled="isCopyingInstructions || isCopyingOnly || isProjectLoading"
              class="bg-cm-blue hover:bg-blue-500 text-white font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex flex-col items-center justify-center space-y-1 leading-tight disabled:opacity-50 disabled:cursor-not-allowed"
              title="Copy Prompt with Instructions (Ctrl+C). Ctrl-Click to copy code only."
              v-info="'copy_with_instructions'"
            >
              <Loader2 v-if="isCopyingInstructions" class="w-6 h-6 animate-spin" />
              <span v-else>Copy with Instructions</span>
            </button>
            <button
              id="btn-copy-code"
              @click="handleCopy(false, $event)"
              :disabled="isCopyingInstructions || isCopyingOnly || isProjectLoading"
              class="bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex flex-col items-center justify-center space-y-1 leading-tight disabled:opacity-50 disabled:cursor-not-allowed"
              title="Copy Code Only (Ctrl+Shift+C)"
              v-info="'copy_code'"
            >
              <Loader2 v-if="isCopyingOnly" class="w-6 h-6 animate-spin" />
              <span v-else>Copy Code Only</span>
            </button>
          </template>

          <template v-else>
            <button
              id="btn-copy-code"
              @click="handleCopy(false, $event)"
              :disabled="isCopyingInstructions || isCopyingOnly || isProjectLoading"
              class="col-span-2 bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Copy Code Only (Ctrl+Shift+C)"
              v-info="'copy_code'"
            >
              <Loader2 v-if="isCopyingOnly" class="w-6 h-6 animate-spin" />
              <template v-else>
                <Copy class="w-5 h-5" />
                <span>Copy Code Only</span>
              </template>
            </button>
          </template>

          <button
            id="btn-define-instructions"
            @click="emit('open-instructions-modal')"
            :disabled="isProjectLoading"
            class="self-start w-full bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-2.5 rounded shadow-sm flex items-center justify-center space-x-2 transition-colors text-[15px] disabled:opacity-50"
            title="Define project-specific instructions"
            v-info="'instructions'"
          >
            <BookOpen class="w-4 h-4" />
            <span>Define Instructions</span>
          </button>

          <div class="flex flex-col space-y-4">
            <!-- Orange Attention styling when changes are pending in memory (Requirement) -->
            <div class="relative w-full">
              <button
                id="btn-paste-changes"
                @click="handlePasteChanges"
                :disabled="isProjectLoading"
                class="relative w-full text-white font-semibold py-2.5 rounded shadow-sm flex items-center justify-center space-x-2 transition-colors text-[15px] disabled:opacity-50"
                :class="hasPendingChanges ? 'bg-[#DE6808] hover:bg-orange-500' : 'bg-cm-green hover:bg-green-600'"
                :title="pasteTooltipText"
                v-info="'paste_changes'"
              >
                <ClipboardPaste class="w-4 h-4" />
                <span>Paste Changes</span>
              </button>
              <!-- Clear Recycle Bin -->
              <button
                v-if="hasPendingChanges"
                @click.stop="clearPasteData"
                class="absolute top-1 right-1 p-1 text-white/50 hover:text-white transition-colors"
                title="Clear unapplied response from memory"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>

            <button
              id="btn-response-review"
              v-if="lastAiResponse"
              @click="openExistingReview"
              :disabled="isProjectLoading"
              class="w-full bg-gray-600 hover:bg-gray-500 text-white font-semibold py-2.5 rounded shadow-sm flex items-center justify-center space-x-2 transition-colors text-[15px] disabled:opacity-50"
              title="Review latest AI response"
              v-info="'response_review'"
            >
              <Eye class="w-4 h-4" :class="hasPendingChanges ? 'text-[#DE6808]' : 'text-white'" />
              <span>AI Response Review</span>
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="!isProjectLoading" class="mb-4 text-gray-500 text-[17px]">
        Select a project to get started
      </div>
    </div>
  </main>
</template>