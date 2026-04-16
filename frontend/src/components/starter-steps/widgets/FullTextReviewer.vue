<script setup>
import { computed, ref } from 'vue'
import { HelpCircle, ChevronRight, Check, X as XIcon, PencilLine } from 'lucide-vue-next'
import MarkdownRenderer from '../../MarkdownRenderer.vue'
import ReviewerQuestions from '../ReviewerQuestions.vue'
import DiffViewer from '../../DiffViewer.vue'
import { useAppState } from '../../../composables/useAppState'
import { useReviewerEditMode } from '../../../composables/useReviewerEditMode'

const props = defineProps({
  title: String,
  content: String,
  baselines: Object,
  questions: Array,
  getQuestionPrompt: Function,
  isLookingBack: Boolean,
  reviewInfoKey: String,
  nextButtonText: String
})

const emit = defineEmits(['update:content', 'reset', 'rewrite', 'next'])

const { editorFontSize, handleZoom } = useAppState()
const showQuestions = ref(false)
const scrollRef = ref(null)

const { reviewerEditMode, toggleReviewerEditMode } = useReviewerEditMode(scrollRef)

const localContent = computed({
  get: () => props.content,
  set: (val) => emit('update:content', val)
})

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
            v-info="'starter_seg_questions'"
            class="px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center space-x-2"
            :class="showQuestions ? 'bg-cm-blue text-white' : 'bg-gray-700 text-gray-300 hover:text-white'"
          >
            <HelpCircle class="w-4 h-4" /><span>Questions</span>
          </button>
          <button @click="$emit('rewrite')" v-info="'starter_seg_rewrite'" class="bg-cm-blue text-white px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center">
            <PencilLine class="w-4 h-4 mr-2" />
            <span>Rewrite</span>
          </button>
          <button @click="toggleReviewerEditMode(null, false)" v-info="'starter_view_toggle'" class="bg-gray-700 text-white px-4 py-1.5 rounded font-bold text-sm shadow transition-colors">{{ reviewerEditMode ? 'Finish Editing' : 'Edit Markdown' }}</button>
        </template>
      </div>
    </div>

    <ReviewerQuestions v-if="showQuestions" :questions="questions" :getPrompt="getQuestionPrompt" />

    <div class="flex-grow bg-cm-input-bg border border-gray-700 rounded overflow-hidden flex flex-col min-h-0">
      <textarea v-if="reviewerEditMode" v-info="reviewInfoKey || 'starter_view_toggle'" ref="scrollRef" v-model="localContent" class="w-full h-full p-6 bg-cm-input-bg text-gray-100 font-mono outline-none selectable shrink-0" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
      <div v-else ref="scrollRef" v-info="reviewInfoKey || 'starter_view_toggle'" class="w-full h-full overflow-y-auto p-6 custom-scrollbar">
        <DiffViewer v-if="baselines && baselines['__merged__']" :oldText="baselines['__merged__']" :newText="localContent" :fontSize="editorFontSize" :fullContext="true" />
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