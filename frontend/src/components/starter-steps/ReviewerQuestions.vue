<script setup>
import { ref, computed, watch } from 'vue'
import { ChevronLeft, ChevronRight, Copy, Check } from 'lucide-vue-next'

const props = defineProps({
  questions: {
    type: Array,
    default: () => []
  },
  getPrompt: {
    type: Function,
    required: true
  }
})

const currentIndex = ref(0)
const isCopied = ref(false)

// Reset index when question list changes (e.g. switching segments)
watch(() => props.questions, () => {
  currentIndex.value = 0
}, { deep: true })

const currentQuestion = computed(() => props.questions[currentIndex.value] || 'No questions available for this section.')

const prev = () => {
  if (currentIndex.value > 0) currentIndex.value--
}

const next = () => {
  if (currentIndex.value < props.questions.length - 1) currentIndex.value++
}

const handleCopy = async () => {
  if (!props.questions.length) return

  const prompt = await props.getPrompt(currentQuestion.value)
  if (prompt) {
    await navigator.clipboard.writeText(prompt)
    isCopied.value = true
    setTimeout(() => { isCopied.value = false }, 2000)
  }
}
</script>

<template>
  <div class="bg-cm-status-bg border border-gray-700 rounded-lg p-5 mb-4 shadow-inner" v-info="'starter_questions_panel'">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center space-x-2">
        <span class="text-[10px] font-black text-cm-blue uppercase tracking-[0.2em]">Review Question</span>
        <span class="text-[10px] text-gray-500 font-mono" v-if="questions.length > 0">
          ({{ currentIndex + 1 }} / {{ questions.length }})
        </span>
      </div>

      <div class="flex items-center space-x-1" v-if="questions.length > 1">
        <button
          @click="prev"
          :disabled="currentIndex === 0"
          class="p-1 hover:bg-gray-700 text-gray-400 disabled:opacity-20 rounded transition-colors"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <button
          @click="next"
          :disabled="currentIndex === questions.length - 1"
          class="p-1 hover:bg-gray-700 text-gray-400 disabled:opacity-20 rounded transition-colors"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <p class="text-gray-200 text-[15px] leading-relaxed mb-5 min-h-[40px]">
      {{ currentQuestion }}
    </p>

    <div class="flex justify-start">
      <button
        @click="handleCopy"
        :disabled="!questions.length"
        v-info="'starter_questions_copy'"
        class="flex items-center space-x-2 px-4 py-2 rounded text-xs font-bold transition-all active:scale-95 disabled:opacity-50"
        :class="isCopied ? 'bg-cm-green text-white' : 'bg-gray-700 hover:bg-gray-600 text-gray-200'"
      >
        <Check v-if="isCopied" class="w-3.5 h-3.5" />
        <Copy v-else class="w-3.5 h-3.5" />
        <span>{{ isCopied ? 'Prompt Copied!' : 'Copy Context & Question' }}</span>
      </button>
    </div>
  </div>
</template>