<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  HelpCircle, Check, X as XIcon, CheckCheck,
  LockKeyhole, LockKeyholeOpen, PencilLine, Waypoints,
  ChevronDown, ChevronUp, Trash2
} from 'lucide-vue-next'
import MarkdownRenderer from '../../MarkdownRenderer.vue'
import ReviewerQuestions from '../ReviewerQuestions.vue'
import DiffViewer from '../../DiffViewer.vue'
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

const acceptAllConfirm = ref(false)
let acceptAllTimer = null

// --- Interactive Pivot State ---
const openPivotIndex = ref(null)

const togglePivot = (idx) => {
  if (openPivotIndex.value === idx) openPivotIndex.value = null
  else openPivotIndex.value = idx
}

watch(activeSegmentKey, () => { openPivotIndex.value = null })

// --- Fragmented Rendering Engine ---
const activeSegmentContent = computed(() => {
  if (!activeSegmentKey.value) return '';
  return props.segments[activeSegmentKey.value] || '';
});

const contentChunks = computed(() => {
  const chunks = []
  const txt = activeSegmentContent.value
  const regex = /<SELECTEDPATH>([\s\S]*?)<\/SELECTEDPATH>\s*<ALTERNATIVES>([\s\S]*?)<\/ALTERNATIVES>/gi

  let lastIdx = 0
  let match
  let pivotIdx = 0

  while ((match = regex.exec(txt)) !== null) {
    if (match.index > lastIdx) {
      chunks.push({ type: 'text', content: txt.substring(lastIdx, match.index) })
    }
    try {
      const selectedText = match[1].trim()
      const alternatives = JSON.parse(match[2].trim())
      chunks.push({ type: 'pivot', id: pivotIdx++, selectedText, alternatives })
    } catch (e) {
      chunks.push({ type: 'text', content: match[0] })
    }
    lastIdx = regex.lastIndex
  }
  if (lastIdx < txt.length) {
    chunks.push({ type: 'text', content: txt.substring(lastIdx) })
  }
  return chunks
})

const discardPivot = (chunk) => {
  if (!confirm("Accept this path and discard all alternatives?")) return
  const escapedText = chunk.selectedText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const pattern = new RegExp(`<SELECTEDPATH>\\s*${escapedText}\\s*<\/SELECTEDPATH>\\s*<ALTERNATIVES>[\\s\\S]*?<\/ALTERNATIVES>`, 'gi')
  const newContent = activeSegmentContent.value.replace(pattern, chunk.selectedText)
  props.segments[activeSegmentKey.value] = newContent
  openPivotIndex.value = null
}

onMounted(() => {
  if (props.orderedKeys.length) {
    const firstUnlocked = props.orderedKeys.find(k => !props.signoffs[k])
    activeSegmentKey.value = firstUnlocked || props.orderedKeys[0]
  }
})

onUnmounted(() => { if (acceptAllTimer) clearTimeout(acceptAllTimer) })

watch(() => props.orderedKeys, (newKeys) => {
  if (newKeys.length > 0 && !newKeys.includes(activeSegmentKey.value)) {
    activeSegmentKey.value = newKeys[0]
  }
}, { deep: true })

watch(activeSegmentKey, () => {
  nextTick(() => {
    if (scrollRef.value) {
      scrollRef.value.scrollTop = 0

      // If the newly selected segment has a diff, automatically scroll to the first changed line
      if (props.baselines[activeSegmentKey.value]) {
        setTimeout(() => {
          const el = scrollRef.value
          if (!el) return
          const firstDiff = el.querySelector('.bg-\\[\\#1e301e\\], .bg-\\[\\#3a1e1e\\]')
          if (firstDiff) {
            firstDiff.scrollIntoView({ behavior: 'smooth', block: 'center' })
          }
        }, 200)
      }
    }
  })
})

// Automatically switch to the first segment containing a diff after a Rewrite is applied
watch(() => props.baselines, (newB) => {
  if (!newB) return
  const keysWithDiffs = props.orderedKeys.filter(k => newB[k] !== undefined)
  if (keysWithDiffs.length > 0) {
    // If the currently viewed segment doesn't have a diff, jump to the first one that does
    if (!activeSegmentKey.value || newB[activeSegmentKey.value] === undefined) {
      activeSegmentKey.value = keysWithDiffs[0]
    }
  }
}, { deep: true })

const hasPendingDiffs = computed(() => {
  return Object.keys(props.baselines).some(k => k !== '__merged__' && props.baselines[k] !== undefined)
})

const renderSegmentTitle = (key) => props.friendlyNames[key] || key

const getPromptForCurrentSegment = async (question) => {
  return props.getQuestionPrompt(question, activeSegmentKey.value)
}

const toggleSignoff = (key) => {
  if (!props.signoffs[key]) {
      // Locking attempt
      const content = props.segments[key] || ''
      if (/<ALTERNATIVES>[\s\S]*?<\/ALTERNATIVES>/gi.test(content)) {
          alert("You must resolve all architectural alternatives (Pivot or Discard) in this segment before locking it.")
          return
      }
  }

  props.signoffs[key] = !props.signoffs[key]
  if (props.signoffs[key]) {
    if (activeSegmentKey.value === key) reviewerEditMode.value = false
    props.baselines[key] = undefined
  }
}

const handleSignoffAndNext = () => {
  const key = activeSegmentKey.value
  const content = props.segments[key] || ''

  if (/<ALTERNATIVES>[\s\S]*?<\/ALTERNATIVES>/gi.test(content)) {
      alert("You must resolve all architectural alternatives (Pivot or Discard) in this segment before locking it.")
      return
  }

  props.signoffs[key] = true
  props.baselines[key] = undefined

  const idx = props.orderedKeys.indexOf(key)
  for (let i = idx + 1; i < props.orderedKeys.length; i++) {
    if (!props.signoffs[props.orderedKeys[i]]) {
      activeSegmentKey.value = props.orderedKeys[i]; reviewerEditMode.value = false; return
    }
  }
  for (let i = 0; i < idx; i++) {
    if (!props.signoffs[props.orderedKeys[i]]) {
      activeSegmentKey.value = props.orderedKeys[i]; reviewerEditMode.value = false; return
    }
  }
  reviewerEditMode.value = false
}

const allSigned = computed(() => Object.values(props.signoffs).every(v => v === true))

const refuseDiff = () => {
  if (activeSegmentKey.value && props.baselines[activeSegmentKey.value]) {
    props.segments[activeSegmentKey.value] = props.baselines[activeSegmentKey.value]
    props.baselines[activeSegmentKey.value] = undefined
  }
}

const acceptDiff = () => { if (activeSegmentKey.value) props.baselines[activeSegmentKey.value] = undefined }

const handleAcceptAllClick = () => {
  if (acceptAllConfirm.value) {
    for (const k in props.baselines) if (k !== '__merged__') props.baselines[k] = undefined
    acceptAllConfirm.value = false; clearTimeout(acceptAllTimer)
  } else {
    acceptAllConfirm.value = true; acceptAllTimer = setTimeout(() => { acceptAllConfirm.value = false }, 2500)
  }
}
</script>

<template>
  <div class="flex h-full min-h-0 text-gray-100" @wheel.ctrl.prevent="handleZoom">
    <div class="w-72 shrink-0 border-r border-gray-700 pr-4 overflow-y-auto space-y-2" v-info="'starter_seg_nav'">
      <div class="p-2 mb-4 border-b border-gray-700 flex flex-col items-center space-y-3 pb-3">
        <button @click="$emit('reset')" v-info="'starter_nav_reset'" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest">Start Over</button>
        <button
          v-if="hasPendingDiffs"
          @click="handleAcceptAllClick"
          class="transition-colors text-[10px] font-bold uppercase tracking-widest flex items-center px-3 py-1.5 rounded border select-none w-full justify-center"
          :class="acceptAllConfirm ? 'bg-cm-green text-white border-cm-green' : 'text-cm-green hover:text-green-400 bg-cm-green/10 border-cm-green/30 hover:bg-cm-green/20'"
        >
          <CheckCheck class="w-3.5 h-3.5 mr-1.5 shrink-0" />
          <span class="truncate">{{ acceptAllConfirm ? 'Click to confirm' : 'Accept All Diffs' }}</span>
        </button>
      </div>
      <div v-for="key in orderedKeys" :key="key"
           @click="activeSegmentKey = key; reviewerEditMode = false"
           class="p-3 rounded cursor-pointer border transition-all flex items-center justify-between group"
           :class="activeSegmentKey === key ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'">
        <div class="flex items-center space-x-2 truncate">
          <div v-if="baselines[key]" class="w-1.5 h-1.5 rounded-full bg-cm-green shrink-0"></div>
          <span class="truncate pr-2">{{ renderSegmentTitle(key) }}</span>
        </div>
        <button @click.stop="toggleSignoff(key)" v-info="'starter_seg_indicator'" class="shrink-0 opacity-70 hover:opacity-100 transition-opacity" :title="signoffs[key] ? 'Unlock' : 'Lock'">
          <LockKeyhole v-if="signoffs[key]" class="w-4 h-4 text-cm-green" :stroke-width="2.5" />
          <LockKeyholeOpen v-else class="w-4 h-4 text-gray-500" :stroke-width="2.5" />
        </button>
      </div>
    </div>
    <div class="flex-grow pl-6 flex flex-col min-w-0" v-if="activeSegmentKey">
      <div class="flex justify-between items-center mb-4 shrink-0">
          <h3 class="text-xl font-bold text-white">{{ renderSegmentTitle(activeSegmentKey) }}</h3>
          <div class="flex space-x-2">
            <div v-if="baselines[activeSegmentKey] && !signoffs[activeSegmentKey]" class="flex space-x-2">
              <button @click="refuseDiff" class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1 bg-gray-700 text-red-400 hover:bg-red-900/40">
                <XIcon class="w-3 h-3" /><span>Refuse</span>
              </button>
              <button @click="acceptDiff" class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1 bg-cm-green text-white hover:brightness-110">
                <Check class="w-3 h-3" /><span>Accept Diff</span>
              </button>
            </div>

            <template v-if="!signoffs[activeSegmentKey] && !baselines[activeSegmentKey]">
              <button
                 @click="$emit('update:showQuestions', !showQuestions)"
                 v-info="'starter_seg_questions'"
                 class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1"
                 :class="showQuestions ? 'bg-cm-blue text-white' : 'bg-gray-800 border-gray-600 text-gray-300 hover:text-white'"
               >
                 <HelpCircle class="w-3 h-3" /><span>Questions</span>
               </button>
              <button @click="$emit('rewrite')" v-info="'starter_seg_rewrite'" class="bg-cm-blue text-white px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center">
                <PencilLine class="w-3 h-3 mr-1" />
                <span>Rewrite</span>
              </button>
              <button @click="toggleReviewerEditMode(null, false)" v-info="'starter_view_toggle'" class="bg-gray-700 text-white px-3 py-1 rounded text-xs shadow transition-colors">{{ reviewerEditMode ? 'Render' : 'Edit' }}</button>
            </template>
          </div>
      </div>

      <ReviewerQuestions
        v-if="showQuestions && !signoffs[activeSegmentKey]"
        :questions="questionsMap[activeSegmentKey]?.questions || []"
        :getPrompt="getPromptForCurrentSegment"
      />

      <div class="flex-grow border border-gray-700 rounded bg-cm-input-bg overflow-hidden flex flex-col min-h-0" v-info="'starter_view_toggle'">
          <textarea v-if="reviewerEditMode" ref="scrollRef" v-model="segments[activeSegmentKey]" class="w-full h-full bg-cm-input-bg text-white p-6 outline-none custom-scrollbar font-sans leading-relaxed selectable shrink-0" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
          <div v-else ref="scrollRef" class="w-full h-full overflow-y-auto p-6 custom-scrollbar">
            <DiffViewer v-if="baselines[activeSegmentKey]" :oldText="baselines[activeSegmentKey]" :newText="segments[activeSegmentKey]" :fontSize="editorFontSize" :fullContext="true" />

            <div v-else class="space-y-4">
               <template v-for="chunk in contentChunks" :key="chunk.id || chunk.content">
                  <MarkdownRenderer
                    v-if="chunk.type === 'text'"
                    :content="chunk.content"
                    :fontSize="editorFontSize"
                    class="fragmented-md"
                    @dblclick="!signoffs[activeSegmentKey] && toggleReviewerEditMode($event, true)"
                  />

                  <!-- Interactive Pivot Zones -->
                  <div v-else class="pt-6 mb-0">
                    <div
                      @click="!signoffs[activeSegmentKey] && togglePivot(chunk.id)"
                      class="border-l-4 border-cm-blue pl-6 pt-8 pb-1 bg-blue-900/10 rounded-r-lg text-gray-200 shadow-md relative group transition-all mb-0"
                      :class="!signoffs[activeSegmentKey] ? 'cursor-pointer hover:bg-blue-900/20' : 'cursor-default'"
                    >
                      <!-- Decision Header (Anchored to Top) -->
                      <div class="absolute -top-3.5 left-3 right-4 flex items-center justify-between">
                        <div class="flex items-center space-x-2 pointer-events-none">
                          <span class="bg-cm-blue text-white text-[10px] font-black px-2 py-1 rounded shadow tracking-widest uppercase">Selected Path</span>
                          <div v-if="!signoffs[activeSegmentKey]" class="bg-gray-800 text-cm-blue text-[10px] font-bold px-2 py-1 rounded shadow border border-cm-blue/30 group-hover:border-cm-blue transition-colors">Click to see alternatives</div>
                        </div>

                        <div v-if="!signoffs[activeSegmentKey]" class="flex items-center space-x-3">
                          <!-- Integrated Accept Button -->
                          <button
                            @click.stop="discardPivot(chunk)"
                            class="bg-cm-top-bar border border-gray-600 text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-cm-green hover:border-cm-green/50 flex items-center px-3 py-1 rounded shadow-lg transition-all active:scale-95 pointer-events-auto"
                            title="Finalize this choice and remove alternatives"
                          >
                            <Check class="w-3.5 h-3.5 mr-1.5" />
                            Accept Path
                          </button>

                          <div class="text-cm-blue/60 group-hover:text-cm-blue transition-colors bg-cm-top-bar p-1 rounded-full border border-gray-600 shadow-md pointer-events-none">
                             <ChevronDown v-if="openPivotIndex !== chunk.id" class="w-5 h-5" />
                             <ChevronUp v-else class="w-5 h-5" />
                          </div>
                        </div>
                      </div>

                      <MarkdownRenderer :content="chunk.selectedText" :fontSize="editorFontSize" />
                    </div>

                    <!-- Alternatives Grid -->
                    <transition name="pivot-slide">
                      <div v-if="openPivotIndex === chunk.id && !signoffs[activeSegmentKey]" class="pl-4 border-l-2 border-dashed border-gray-700 space-y-2 pt-7 pb-2">
                        <div class="flex items-center justify-between ml-2">
                          <div class="flex items-center text-gray-500">
                            <Waypoints class="w-4 h-4 mr-2" />
                            <span class="text-[10px] font-black uppercase tracking-widest">Architectural Alternatives</span>
                          </div>
                        </div>
                        <div class="grid grid-cols-1 gap-3">
                          <button
                            v-for="alt in chunk.alternatives"
                            :key="alt.title"
                            @click="$emit('pivot', alt, chunk.selectedText, activeSegmentKey)"
                            class="bg-gray-800 border border-gray-700 hover:border-cm-blue hover:bg-gray-700 p-4 rounded-lg text-left transition-all group flex flex-col shadow-sm relative overflow-hidden"
                          >
                            <div class="absolute top-0 right-0 w-1 h-full bg-cm-blue transform translate-x-full group-hover:translate-x-0 transition-transform"></div>
                            <div class="font-bold text-cm-blue mb-1 text-base group-hover:text-blue-400">{{ alt.title }}</div>
                            <div class="text-sm text-gray-400 group-hover:text-gray-300 leading-relaxed">{{ alt.description }}</div>
                          </button>
                        </div>
                      </div>
                    </transition>
                  </div>
               </template>
            </div>
          </div>
      </div>
      <div class="shrink-0 pt-4 flex justify-end space-x-4">
          <button v-if="signoffs[activeSegmentKey]" @click="toggleSignoff(activeSegmentKey)" v-info="'starter_seg_unlock'" class="bg-cm-green hover:bg-green-600 text-white px-8 py-2 rounded font-bold shadow transition-colors flex items-center">
            <LockKeyholeOpen class="w-4 h-4 mr-2" :stroke-width="2.5" />
            <span>Unlock</span>
          </button>
          <button v-else @click="handleSignoffAndNext" v-info="'starter_seg_signoff'" class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2 rounded font-bold shadow transition-colors flex items-center">
            <LockKeyhole class="w-4 h-4 mr-2" :stroke-width="2.5" />
            <span>Lock & Next</span>
          </button>
          <button v-if="allSigned" @click="$emit('merge')" v-info="'starter_seg_merge'" class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2 rounded font-bold shadow transition-colors">Merge & Finalize</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pivot-slide-enter-active, .pivot-slide-leave-active { transition: all 0.3s ease-out; max-height: 800px; }
.pivot-slide-enter-from, .pivot-slide-leave-to { opacity: 0; max-height: 0; transform: translateY(-10px); }
:deep(.fragmented-md .prose) { margin-top: 0 !important; margin-bottom: 0 !important; }
</style>