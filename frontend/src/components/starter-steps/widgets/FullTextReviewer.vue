<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { HelpCircle, ChevronRight, Check, X as XIcon, PencilLine, Waypoints, ChevronDown, ChevronUp } from 'lucide-vue-next'
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
  nextButtonText: String,
  showQuestions: Boolean
})

const emit = defineEmits(['update:content', 'reset', 'rewrite', 'next', 'update:showQuestions', 'pivot'])

const { editorFontSize, handleZoom } = useAppState()
const scrollRef = ref(null)

const { reviewerEditMode, toggleReviewerEditMode } = useReviewerEditMode(scrollRef)

const localContent = computed({
  get: () => props.content,
  set: (val) => emit('update:content', val)
})

// --- Interactive Pivot State ---
const openPivotIndex = ref(null)

const togglePivot = (idx) => {
  if (openPivotIndex.value === idx) openPivotIndex.value = null
  else openPivotIndex.value = idx
}

// --- Resolution Check ---
const hasUnresolvedPivots = computed(() => {
  return /<ALTERNATIVES>[\s\S]*?<\/ALTERNATIVES>/gi.test(localContent.value)
})

const handleNext = () => {
  if (props.baselines && props.baselines['__merged__'] !== undefined) {
    alert("You must accept or refuse the pending changes before proceeding.")
    return
  }
  if (hasUnresolvedPivots.value) {
    alert("You must resolve all architectural alternatives (either Pivot or Discard) before proceeding to the next step.")
    return
  }
  emit('next')
}

const discardPivot = (chunk) => {
  // Regex to target this specific selected path + alternatives block
  // We use escaping on the text to ensure the match is precise
  const escapedText = chunk.selectedText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const pattern = new RegExp(`<SELECTEDPATH>\\s*${escapedText}\\s*<\/SELECTEDPATH>\\s*<ALTERNATIVES>[\\s\\S]*?<\/ALTERNATIVES>`, 'gi')

  const newContent = localContent.value.replace(pattern, chunk.selectedText)
  emit('update:content', newContent)
  openPivotIndex.value = null
}

// --- Fragmented Rendering Engine ---
const contentChunks = computed(() => {
  const chunks = []
  const txt = localContent.value || ''
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

// Automatically scroll to the first diff line when the diff view is activated after a rewrite
watch(() => props.baselines?.['__merged__'], (newVal) => {
  if (newVal !== undefined) {
    reviewerEditMode.value = false
    nextTick(() => {
      // Small delay to allow DiffViewer to fetch highlighted lines via IPC and mount them in DOM
      setTimeout(() => {
        const container = scrollRef.value
        if (!container) return

        // Look for the first line with an 'add' or 'remove' background color (Tailwind escaped brackets)
        const firstDiff = container.querySelector('.bg-\\[\\#1e301e\\], .bg-\\[\\#3a1e1e\\]')
        if (firstDiff) {
          firstDiff.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 200)
    })
  }
})
</script>

<template>
  <div class="h-full flex flex-col relative" @wheel.ctrl.prevent="handleZoom">
    <div class="flex items-center justify-between mb-4 shrink-0">
      <h3 class="text-2xl font-bold text-white">{{ title }}</h3>
      <div class="flex space-x-3">
        <button @click="$emit('reset')" v-info="'starter_nav_reset'" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest mr-2">Start Over</button>

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
            @click="$emit('update:showQuestions', !showQuestions)"
            v-info="'starter_seg_questions'"
            class="px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center space-x-2"
            :class="showQuestions ? 'bg-cm-blue text-white' : 'bg-gray-800 border-gray-600 text-gray-300 hover:text-white'"
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

        <div v-else class="space-y-4">
          <template v-for="chunk in contentChunks" :key="chunk.id || chunk.content">
            <MarkdownRenderer
              v-if="chunk.type === 'text'"
              :content="chunk.content"
              :fontSize="editorFontSize"
              class="fragmented-md"
              @dblclick="toggleReviewerEditMode($event, true)"
            />

            <!-- Interactive Pivot Zones -->
            <div v-else class="pt-6 mb-0">
              <div
                @click="togglePivot(chunk.id)"
                class="border-l-4 border-cm-blue pl-6 pt-8 pb-1 bg-blue-900/10 rounded-r-lg text-gray-200 shadow-md relative cursor-pointer hover:bg-blue-900/20 transition-all group mb-0"
              >
                <!-- Decision Header (Anchored to Top) -->
                <div class="absolute -top-3.5 left-3 right-4 flex items-center justify-between">
                  <div class="flex items-center space-x-2 pointer-events-none">
                    <span class="bg-cm-blue text-white text-[10px] font-black px-2 py-1 rounded shadow tracking-widest uppercase">Selected Path</span>
                    <div class="bg-gray-800 text-cm-blue text-[10px] font-bold px-2 py-1 rounded shadow border border-cm-blue/30 group-hover:border-cm-blue transition-colors">Click to see alternatives</div>
                  </div>

                  <div class="flex items-center space-x-3">
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
                <div v-if="openPivotIndex === chunk.id" class="pl-4 border-l-2 border-dashed border-gray-700 space-y-2 pt-7 pb-2">
                  <div class="flex items-center justify-between ml-2">
                    <div class="flex items-center text-gray-500">
                      <Waypoints class="w-4 h-4 mr-2" />
                      <span class="text-[10px] font-black uppercase tracking-widest">Architectural Alternatives</span>
                    </div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <button
                      v-for="alt in chunk.alternatives"
                      :key="alt.title"
                      @click="$emit('pivot', alt, chunk.selectedText)"
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

    <div v-if="!isLookingBack" class="shrink-0 pt-6 flex justify-end">
      <button
        @click="handleNext"
        :disabled="baselines && baselines['__merged__'] !== undefined"
        class="bg-cm-blue hover:bg-blue-500 disabled:opacity-50 disabled:bg-gray-700 text-white font-bold py-3 px-12 rounded shadow-lg transition-all flex items-center group"
      >
        {{ nextButtonText }}
        <ChevronRight class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.pivot-slide-enter-active, .pivot-slide-leave-active { transition: all 0.3s ease-out; max-height: 500px; }
.pivot-slide-enter-from, .pivot-slide-leave-to { opacity: 0; max-height: 0; transform: translateY(-10px); }
:deep(.fragmented-md .prose) { margin-top: 0 !important; margin-bottom: 0 !important; }
</style>