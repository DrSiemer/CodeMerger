<script setup>
import { ref, computed, watch } from 'vue'
import { ChevronLeft, ChevronRight, Copy, Check, MessageSquarePlus, BookOpen } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const { copyText } = useAppState()

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
const isCustom = ref(true)
const customText = ref('')

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

const handleCopy = async (e) => {
  const questionToCopy = isCustom.value ? customText.value.trim() : currentQuestion.value

  if (!questionToCopy) return

  if (!e.ctrlKey) {
    const prompt = await props.getPrompt(questionToCopy)
    if (prompt) {
      await copyText(prompt)
      isCopied.value = true
      setTimeout(() => { isCopied.value = false }, 2000)
    }
  } else {
    isCopied.value = true
    setTimeout(() => { isCopied.value = false }, 2000)
  }
}

const isCopyDisabled = computed(() => {
  if (isCustom.value) return !customText.value.trim()
  return props.questions.length === 0
})
</script>

<template>
  <div class="bg-cm-status-bg border border-gray-700 rounded-lg p-5 mb-4 shadow-inner" v-info="'starter_questions_panel'">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <span class="text-[10px] font-black text-cm-blue uppercase tracking-[0.2em]">Review Mode</span>
        </div>

        <div class="flex bg-gray-800 rounded p-0.5 border border-gray-700">
          <button
            @click="isCustom = true"
            class="px-2 py-1 rounded text-[10px] font-bold uppercase transition-colors flex items-center space-x-1"
            :class="isCustom ? 'bg-cm-blue text-white' : 'text-gray-500 hover:text-gray-300'"
            title="Ask your own specific question"
          >
            <MessageSquarePlus class="w-3 h-3" />
            <span>Custom</span>
          </button>
          <button
            @click="isCustom = false"
            class="px-2 py-1 rounded text-[10px] font-bold uppercase transition-colors flex items-center space-x-1"
            :class="!isCustom ? 'bg-cm-blue text-white' : 'text-gray-500 hover:text-gray-300'"
            title="Use prewritten guiding questions"
          >
            <BookOpen class="w-3 h-3" />
            <span>Guiding</span>
          </button>
        </div>
      </div>

      <div class="flex items-center space-x-1" v-if="!isCustom && questions.length > 1">
        <span class="text-[10px] text-gray-500 font-mono mr-2">
          ({{ currentIndex + 1 }} / {{ questions.length }})
        </span>
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

    <div class="mb-5 min-h-[40px]">
      <p v-if="!isCustom" class="text-gray-200 text-[15px] leading-relaxed">
        {{ currentQuestion }}
      </p>
      <textarea
        v-else
        v-model="customText"
        v-info="'starter_questions_custom'"
        class="w-full h-20 bg-cm-input-bg border border-gray-600 text-gray-200 p-3 rounded text-sm outline-none focus:border-cm-blue custom-scrollbar font-sans selectable"
        placeholder="Type your own question or instruction for the AI..."
      ></textarea>
    </div>

    <div class="flex justify-start">
      <button
        @click="handleCopy($event)"
        :disabled="isCopyDisabled"
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