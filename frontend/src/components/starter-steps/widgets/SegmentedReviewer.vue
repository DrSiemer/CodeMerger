<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { HelpCircle, Check, X as XIcon, LockKeyhole, LockKeyholeOpen, PencilLine } from 'lucide-vue-next'
import MarkdownRenderer from '../../MarkdownRenderer.vue'
import ReviewerQuestions from '../ReviewerQuestions.vue'
import DiffViewer from '../../DiffViewer.vue'
import SegmentedSidebar from './SegmentedSidebar.vue'
import InteractivePivot from './InteractivePivot.vue'
import { useAppState } from '../../../composables/useAppState'
import { useReviewerEditMode } from '../../../composables/useReviewerEditMode'

const props = defineProps({
  segments: Object,
  signoffs: Object,
  baselines: Object,
  orderedKeys: Array,
  friendlyNames: Object,
  questionsMap: Object,
  getQuestionPrompt: Function,
  showQuestions: Boolean
})

const emit = defineEmits(['reset', 'rewrite', 'merge', 'update:showQuestions', 'pivot'])

const { editorFontSize, handleZoom } = useAppState()
const activeSegmentKey = ref(null)
const scrollRef = ref(null)

const { reviewerEditMode, toggleReviewerEditMode } = useReviewerEditMode(scrollRef)

const activeSegmentContent = computed(() => {
  if (!activeSegmentKey.value) return ''
  return props.segments[activeSegmentKey.value] || ''
})

const contentChunks = computed(() => {
  const chunks = []
  const txt = activeSegmentContent.value
  const regex = /<SELECTEDPATH>([\s\S]*?)<\/SELECTEDPATH>\s*<ALTERNATIVES>([\s\S]*?)<\/ALTERNATIVES>/gi
  let lastIdx = 0, match, pivotIdx = 0

  while ((match = regex.exec(txt)) !== null) {
    if (match.index > lastIdx) chunks.push({ type: 'text', content: txt.substring(lastIdx, match.index) })
    try {
      const selectedText = match[1].trim()
      const alternatives = JSON.parse(match[2].trim())
      chunks.push({ type: 'pivot', id: pivotIdx++, selectedText, alternatives })
    } catch (e) { chunks.push({ type: 'text', content: match[0] }) }
    lastIdx = regex.lastIndex
  }
  if (lastIdx < txt.length) chunks.push({ type: 'text', content: txt.substring(lastIdx) })
  return chunks
})

const discardPivot = (chunk) => {
  const escapedText = chunk.selectedText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const pattern = new RegExp(`<SELECTEDPATH>\\s*${escapedText}\\s*<\/SELECTEDPATH>\\s*<ALTERNATIVES>[\\s\\S]*?<\/ALTERNATIVES>`, 'gi')
  props.segments[activeSegmentKey.value] = activeSegmentContent.value.replace(pattern, chunk.selectedText)
}

onMounted(() => {
  if (props.orderedKeys.length) {
    const firstUnlocked = props.orderedKeys.find(k => !props.signoffs[k])
    activeSegmentKey.value = firstUnlocked || props.orderedKeys[0]
  }
})

watch(activeSegmentKey, () => {
  reviewerEditMode.value = false
  nextTick(() => {
    if (scrollRef.value) {
      scrollRef.value.scrollTop = 0
      if (props.baselines[activeSegmentKey.value]) {
        setTimeout(() => {
          const el = scrollRef.value
          if (!el) return
          const firstDiff = el.querySelector('.bg-\\[\\#1e301e\\], .bg-\\[\\#3a1e1e\\]')
          if (firstDiff) firstDiff.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }, 200)
      }
    }
  })
})

watch(() => props.baselines, (newB) => {
  if (!newB) return
  const keysWithDiffs = props.orderedKeys.filter(k => newB[k] !== undefined)
  if (keysWithDiffs.length > 0) {
    reviewerEditMode.value = false
    if (!activeSegmentKey.value || newB[activeSegmentKey.value] === undefined) activeSegmentKey.value = keysWithDiffs[0]
  }
}, { deep: true })

const toggleSignoff = (key) => {
  props.signoffs[key] = !props.signoffs[key]
  if (props.signoffs[key]) {
    if (activeSegmentKey.value === key) reviewerEditMode.value = false
    props.baselines[key] = undefined
  }
}

const handleSignoffAndNext = () => {
  const key = activeSegmentKey.value
  if (/<ALTERNATIVES>[\s\S]*?<\/ALTERNATIVES>/gi.test(props.segments[key] || '')) {
    alert("You must resolve all architectural alternatives in this segment before locking it.")
    return
  }
  props.signoffs[key] = true
  props.baselines[key] = undefined
  const idx = props.orderedKeys.indexOf(key)
  for (let i = idx + 1; i < props.orderedKeys.length; i++) {
    if (!props.signoffs[props.orderedKeys[i]]) { activeSegmentKey.value = props.orderedKeys[i]; return }
  }
  for (let i = 0; i < idx; i++) {
    if (!props.signoffs[props.orderedKeys[i]]) { activeSegmentKey.value = props.orderedKeys[i]; return }
  }
}

const acceptAllDiffs = () => {
  for (const k in props.baselines) if (k !== '__merged__') props.baselines[k] = undefined
}

const allSigned = computed(() => props.orderedKeys.every(k => props.signoffs[k]))
const hasPendingDiffs = computed(() => Object.keys(props.baselines).some(k => k !== '__merged__' && props.baselines[k] !== undefined))
</script>

<template>
  <div class="flex h-full min-h-0 text-gray-100" @wheel.ctrl.prevent="handleZoom">
    <SegmentedSidebar
      :orderedKeys="orderedKeys"
      :friendlyNames="friendlyNames"
      :signoffs="signoffs"
      :baselines="baselines"
      :activeSegmentKey="activeSegmentKey"
      :segments="segments"
      @select="k => activeSegmentKey = k"
      @reset="$emit('reset')"
      @toggle-signoff="toggleSignoff"
      @accept-all="acceptAllDiffs"
    />

    <div class="flex-grow pl-6 flex flex-col min-w-0" v-if="activeSegmentKey">
      <div class="flex justify-between items-center mb-4 shrink-0">
        <h3 class="text-xl font-bold text-white">{{ friendlyNames[activeSegmentKey] || activeSegmentKey }}</h3>
        <div class="flex space-x-2">
          <div v-if="baselines[activeSegmentKey] && !signoffs[activeSegmentKey]" class="flex space-x-2">
            <button @click="props.segments[activeSegmentKey] = props.baselines[activeSegmentKey]; props.baselines[activeSegmentKey] = undefined" class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1 bg-gray-700 text-red-400 hover:bg-red-900/40">
              <XIcon class="w-3 h-3" /><span>Refuse</span>
            </button>
            <button @click="props.baselines[activeSegmentKey] = undefined" class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1 bg-cm-green text-white hover:brightness-110">
              <Check class="w-3 h-3" /><span>Accept Diff</span>
            </button>
          </div>
          <template v-if="!signoffs[activeSegmentKey] && !baselines[activeSegmentKey]">
            <button @click="$emit('update:showQuestions', !showQuestions)" v-info="'starter_seg_questions'" class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1" :class="showQuestions ? 'bg-cm-blue text-white' : 'bg-gray-800 border-gray-600 text-gray-300 hover:text-white'">
              <HelpCircle class="w-3 h-3" /><span>Questions</span>
            </button>
            <button @click="$emit('rewrite')" v-info="'starter_seg_rewrite'" class="bg-cm-blue text-white px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center">
              <PencilLine class="w-3 h-3 mr-1" /><span>Rewrite</span>
            </button>
            <button @click="toggleReviewerEditMode(null, false)" v-info="'starter_view_toggle'" class="bg-gray-700 text-white px-3 py-1 rounded text-xs shadow transition-colors">{{ reviewerEditMode ? 'Render' : 'Edit' }}</button>
          </template>
        </div>
      </div>

      <ReviewerQuestions
        v-if="showQuestions && !signoffs[activeSegmentKey]"
        :questions="questionsMap[activeSegmentKey]?.questions || []"
        :getPrompt="q => getQuestionPrompt(q, activeSegmentKey)"
      />

      <div class="flex-grow border border-gray-700 rounded bg-cm-input-bg overflow-hidden flex flex-col min-h-0" v-info="'starter_view_toggle'">
        <textarea v-if="reviewerEditMode" ref="scrollRef" v-model="segments[activeSegmentKey]" class="w-full h-full bg-cm-input-bg text-white p-6 outline-none custom-scrollbar font-sans leading-relaxed selectable shrink-0" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
        <div v-else ref="scrollRef" class="w-full h-full overflow-y-auto p-6 custom-scrollbar">
          <DiffViewer v-if="baselines[activeSegmentKey]" :oldText="baselines[activeSegmentKey]" :newText="segments[activeSegmentKey]" :fontSize="editorFontSize" :fullContext="true" />
          <div v-else class="space-y-4">
            <template v-for="chunk in contentChunks" :key="chunk.id || chunk.content">
              <MarkdownRenderer v-if="chunk.type === 'text'" :content="chunk.content" :fontSize="editorFontSize" class="fragmented-md" @dblclick="!signoffs[activeSegmentKey] && toggleReviewerEditMode($event, true)" />
              <InteractivePivot v-else :chunk="chunk" :isLocked="signoffs[activeSegmentKey]" :fontSize="editorFontSize" @discard="discardPivot" @pivot="(alt, txt) => $emit('pivot', alt, txt, activeSegmentKey)" />
            </template>
          </div>
        </div>
      </div>

      <div class="shrink-0 pt-4 flex justify-end space-x-4">
        <button v-if="signoffs[activeSegmentKey]" @click="toggleSignoff(activeSegmentKey)" v-info="'starter_seg_unlock'" class="bg-cm-green hover:bg-green-600 text-white px-8 py-2 rounded font-bold shadow transition-colors flex items-center">
          <LockKeyholeOpen class="w-4 h-4 mr-2" :stroke-width="2.5" /><span>Unlock</span>
        </button>
        <button v-else @click="handleSignoffAndNext" v-info="'starter_seg_signoff'" class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2 rounded font-bold shadow transition-colors flex items-center">
          <LockKeyhole class="w-4 h-4 mr-2" :stroke-width="2.5" /><span>Lock & Next</span>
        </button>
        <button v-if="allSigned" :disabled="hasPendingDiffs" @click="$emit('merge')" v-info="'starter_seg_merge'" class="bg-cm-blue hover:bg-blue-500 disabled:opacity-50 disabled:bg-gray-700 text-white px-8 py-2 rounded font-bold shadow transition-colors">Merge & Finalize</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.fragmented-md .prose) { margin-top: 0 !important; margin-bottom: 0 !important; }
</style>