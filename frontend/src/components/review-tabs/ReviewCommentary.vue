<script setup>
import { ref } from 'vue'
import { BookOpen, ChevronDown, ChevronRight, ChevronUp } from 'lucide-vue-next'
import MarkdownRenderer from '../MarkdownRenderer.vue'
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  commentary: {
    type: String,
    required: true
  }
})

const { editorFontSize } = useAppState()
const showCommentary = ref(false)

const collapseCommentary = () => {
  showCommentary.value = false
  setTimeout(() => {
    const el = document.getElementById('commentary-header')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 50)
}
</script>

<template>
  <div class="border border-gray-700 rounded bg-[#1A1A1A] overflow-hidden">
    <button
      id="commentary-header"
      @click="showCommentary = !showCommentary"
      v-info="'review_commentary'"
      class="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
      title="Read technical explanations for these changes"
    >
      <div class="flex items-center space-x-3">
        <BookOpen class="w-4 h-4 text-cm-blue" />
        <span class="text-sm font-bold text-gray-200 uppercase tracking-widest">AI Commentary</span>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-xs text-gray-500">{{ showCommentary ? 'Hide' : 'Show' }} details</span>
        <ChevronDown v-if="showCommentary" class="w-4 h-4 text-gray-500" />
        <ChevronRight v-else class="w-4 h-4 text-gray-500" />
      </div>
    </button>
    <div v-if="showCommentary" class="p-4 border-t border-gray-700 bg-cm-dark-bg">
      <MarkdownRenderer :content="commentary" :fontSize="editorFontSize" />
      <div class="flex justify-end mt-3">
        <button @click="collapseCommentary" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-1.5 rounded transition-colors flex items-center">
          <ChevronUp class="w-3.5 h-3.5 mr-1" />
          Collapse
        </button>
      </div>
    </div>
  </div>
</template>