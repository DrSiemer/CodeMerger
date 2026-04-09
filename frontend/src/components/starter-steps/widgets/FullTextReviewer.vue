<script setup>
import { ref, nextTick, computed } from 'vue'
import { HelpCircle, ChevronRight, Check, X as XIcon } from 'lucide-vue-next'
import MarkdownRenderer from '../../MarkdownRenderer.vue'
import ReviewerQuestions from '../ReviewerQuestions.vue'
import DiffViewer from '../../DiffViewer.vue'
import { useAppState } from '../../../composables/useAppState'

const props = defineProps({
  title: String,
  content: String,
  baselines: Object,
  questions: Array,
  getQuestionPrompt: Function,
  isLookingBack: Boolean,
  nextButtonText: String
})

const emit = defineEmits(['update:content', 'reset', 'rewrite', 'next'])

const { editorFontSize, handleZoom } = useAppState()
const reviewerEditMode = ref(false)
const showQuestions = ref(false)
const scrollRef = ref(null)

const localContent = computed({
  get: () => props.content,
  set: (val) => emit('update:content', val)
})

const toggleReviewerEditMode = async (event = null, isContextual = false) => {
  let anchorText = ''
  let contentRatio = 0
  const isDoubleclick = isContextual && event

  const el = scrollRef.value
  if (el) {
    if (!reviewerEditMode.value) {
      if (isDoubleclick) {
        anchorText = window.getSelection().toString().trim().split('\n')[0].substring(0, 50)
      } else {
        const rect = el.getBoundingClientRect()
        const topEl = document.elementFromPoint(rect.left + 50, rect.top + 20)
        if (topEl) {
          anchorText = topEl.innerText?.trim().split('\n')[0].substring(0, 40) || ''
        }
      }
      contentRatio = el.scrollTop / el.scrollHeight
    } else {
      const text = el.value
      contentRatio = el.scrollTop / el.scrollHeight
      const targetCharIdx = Math.floor(text.length * contentRatio)
      anchorText = text.substring(targetCharIdx, targetCharIdx + 60).trim().split('\n')[0]
    }
  }

  reviewerEditMode.value = !reviewerEditMode.value
  await nextTick()

  setTimeout(() => {
    const newEl = scrollRef.value
    if (!newEl) return

    if (reviewerEditMode.value) {
      const fullText = newEl.value
      let foundIdx = -1

      if (anchorText) {
        const startSearch = Math.floor(fullText.length * contentRatio)
        foundIdx = fullText.indexOf(anchorText, Math.max(0, startSearch - 300))
        if (foundIdx === -1) foundIdx = fullText.indexOf(anchorText)
      }

      if (foundIdx !== -1) {
        const charRatio = foundIdx / fullText.length
        const offset = isDoubleclick ? 0.3 : 0.05
        newEl.focus({ preventScroll: true })
        newEl.setSelectionRange(foundIdx, foundIdx + anchorText.length)
        const setPos = () => { newEl.scrollTop = (charRatio * newEl.scrollHeight) - (newEl.clientHeight * offset) }
        setPos()
        requestAnimationFrame(setPos)
      } else {
        newEl.scrollTop = contentRatio * newEl.scrollHeight
      }
    } else {
      let scrolled = false
      if (anchorText) {
        const walker = document.createTreeWalker(newEl, NodeFilter.SHOW_TEXT, null, false)
        let node
        while ((node = walker.nextNode())) {
          if (node.textContent.includes(anchorText)) {
            node.parentElement.scrollIntoView({ block: 'start', behavior: 'instant' })
            newEl.scrollTop -= (newEl.clientHeight * 0.05)
            scrolled = true
            break
          }
        }
      }
      if (!scrolled) {
        newEl.scrollTop = contentRatio * newEl.scrollHeight
      }
    }
  }, 100)
}

const refuseDiff = () => {
  if (props.baselines && props.baselines['__merged__']) {
    emit('update:content', props.baselines['__merged__'])
    props.baselines['__merged__'] = undefined
  }
}

const acceptDiff = () => {
  if (props.baselines) {
    props.baselines['__merged__'] = undefined
  }
}
</script>

<template>
  <div class="h-full flex flex-col relative" @wheel.ctrl.prevent="handleZoom">
    <div class="flex items-center justify-between mb-4 shrink-0">
      <h3 class="text-2xl font-bold text-white">{{ title }}</h3>
      <div class="flex space-x-3">
        <button @click="$emit('reset')" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest mr-2">Start Over</button>

        <div v-if="baselines && baselines['__merged__']" class="flex space-x-2">
          <button
            @click="refuseDiff"
            class="px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center space-x-2 bg-gray-700 text-red-400 hover:bg-red-900/40"
          >
            <XIcon class="w-4 h-4" /><span>Refuse</span>
          </button>
          <button
            @click="acceptDiff"
            class="px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center space-x-2 bg-cm-green text-white hover:brightness-110"
          >
            <Check class="w-4 h-4" /><span>Accept Diff</span>
          </button>
        </div>

        <template v-if="!(baselines && baselines['__merged__'])">
          <button
            @click="showQuestions = !showQuestions"
            class="px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center space-x-2"
            :class="showQuestions ? 'bg-cm-blue text-white' : 'bg-gray-700 text-gray-300 hover:text-white'"
          >
            <HelpCircle class="w-4 h-4" /><span>Questions</span>
          </button>
          <button @click="$emit('rewrite')" class="bg-cm-blue text-white px-4 py-1.5 rounded font-bold text-sm shadow transition-colors">Rewrite</button>
          <button @click="toggleReviewerEditMode(null, false)" class="bg-gray-700 text-white px-4 py-1.5 rounded font-bold text-sm shadow transition-colors">{{ reviewerEditMode ? 'Finish Editing' : 'Edit Markdown' }}</button>
        </template>
      </div>
    </div>

    <ReviewerQuestions v-if="showQuestions" :questions="questions" :getPrompt="getQuestionPrompt" />

    <div class="flex-grow bg-cm-input-bg border border-gray-700 rounded overflow-hidden flex flex-col min-h-0">
      <textarea v-if="reviewerEditMode" ref="scrollRef" v-model="localContent" class="w-full h-full p-6 bg-cm-input-bg text-gray-100 font-mono outline-none selectable shrink-0" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
      <div v-else ref="scrollRef" class="w-full h-full overflow-y-auto p-6 custom-scrollbar">
        <DiffViewer v-if="baselines && baselines['__merged__']" :oldText="baselines['__merged__']" :newText="localContent" :fontSize="editorFontSize" />
        <MarkdownRenderer v-else :content="localContent" :fontSize="editorFontSize" @dblclick="toggleReviewerEditMode($event, true)" />
      </div>
    </div>

    <div v-if="!isLookingBack" class="shrink-0 pt-6 flex justify-end">
      <button @click="$emit('next')" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-3 px-12 rounded shadow-lg transition-all flex items-center group">
        {{ nextButtonText }}
        <ChevronRight class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #555; }
</style>