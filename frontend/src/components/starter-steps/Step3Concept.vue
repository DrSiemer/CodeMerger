<script setup>
import { ref, nextTick, computed, onMounted, onUnmounted, watch } from 'vue'
import { CheckCircle, HelpCircle, ChevronRight, Check, X as XIcon, CheckCheck } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'
import MarkdownRenderer from '../MarkdownRenderer.vue'
import RewriteModal from './RewriteModal.vue'
import NotesModal from './NotesModal.vue'
import ReviewerQuestions from './ReviewerQuestions.vue'
import DiffViewer from '../DiffViewer.vue'

const props = defineProps({
  pData: {
    type: Object,
    required: true
  },
  conceptQuestionsMap: {
    type: Object,
    required: true
  },
  isLookingBack: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['next'])

const CONCEPT_ORDER = ["problem_statement", "core_principles", "key_features", "user_flows", "tech_constraints"]

const {
  generateConceptPrompt,
  parseStarterSegments,
  mapParsedSegmentsToKeys,
  assembleStarterDocument,
  getStarterQuestionPrompt,
  editorFontSize,
  handleZoom,
  lockedIcon,
  unlockedIcon
} = useAppState()

const activeSegmentKey = ref(null)
const reviewerEditMode = ref(false)
const scrollRef = ref(null)
const showPasteArea = ref(!!props.pData.concept_llm_response)
const showQuestions = ref(false)

// Rewrite Modals State
const showRewriteModal = ref(false)
const rewriteContext = ref(null)
const rewriteIsMergedMode = ref(false)
const showNotesModal = ref(false)
const notesContent = ref('')

onMounted(() => {
  // If we have existing segments, find the first unlocked one to show
  if (Object.keys(props.pData.concept_segments).length) {
    const keys = CONCEPT_ORDER.filter(k => props.pData.concept_segments[k] !== undefined)
    const firstUnlocked = keys.find(k => !props.pData.concept_signoffs[k])
    activeSegmentKey.value = firstUnlocked || keys[0]
  }
})

onUnmounted(() => {
  if (acceptAllTimer) clearTimeout(acceptAllTimer)
})

// Scroll to top when switching segments
watch(activeSegmentKey, () => {
  nextTick(() => {
    if (scrollRef.value) {
      scrollRef.value.scrollTop = 0
    }
  })
})

const toggleReviewerEditMode = async (event = null, isContextual = false) => {
  let anchorText = ''
  let contentRatio = 0
  const isDoubleclick = isContextual && event

  const el = scrollRef.value
  if (el) {
    if (!reviewerEditMode.value) {
      // --- CAPTURE STATE: RENDER -> EDIT ---
      if (isDoubleclick) {
        anchorText = window.getSelection().toString().trim().split('\n')[0].substring(0, 50)
      } else {
        const rect = el.getBoundingClientRect()
        // Find visible text at the top
        const topEl = document.elementFromPoint(rect.left + 50, rect.top + 20)
        if (topEl) {
          anchorText = topEl.innerText?.trim().split('\n')[0].substring(0, 40) || ''
        }
      }
      contentRatio = el.scrollTop / el.scrollHeight
    } else {
      // --- CAPTURE STATE: EDIT -> RENDER ---
      const text = el.value
      contentRatio = el.scrollTop / el.scrollHeight
      const targetCharIdx = Math.floor(text.length * contentRatio)
      anchorText = text.substring(targetCharIdx, targetCharIdx + 60).trim().split('\n')[0]
    }
  }

  // Switch mode
  reviewerEditMode.value = !reviewerEditMode.value

  await nextTick()

  // 100ms delay allows the browser to finalize layout/wrapping in the new view
  setTimeout(() => {
    const newEl = scrollRef.value
    if (!newEl) return

    if (reviewerEditMode.value) {
      // --- APPLY SCROLL: EDIT MODE (Textarea) ---
      const fullText = newEl.value
      let foundIdx = -1

      if (anchorText) {
        // Search for snippet, prioritizing current scroll depth for duplicates
        const startSearch = Math.floor(fullText.length * contentRatio)
        foundIdx = fullText.indexOf(anchorText, Math.max(0, startSearch - 300))
        if (foundIdx === -1) foundIdx = fullText.indexOf(anchorText)
      }

      if (foundIdx !== -1) {
        const charRatio = foundIdx / fullText.length
        const offset = isDoubleclick ? 0.3 : 0.05

        // FOCUS & SELECT (Blocking native scroll jump)
        newEl.focus({ preventScroll: true })
        newEl.setSelectionRange(foundIdx, foundIdx + anchorText.length)

        // MANUAL SCROLL OVERRIDE
        // We set it twice to ensure it sticks after the browser focus event processing
        const setPos = () => {
          newEl.scrollTop = (charRatio * newEl.scrollHeight) - (newEl.clientHeight * offset)
        }
        setPos()
        requestAnimationFrame(setPos)
      } else {
        newEl.scrollTop = contentRatio * newEl.scrollHeight
      }
    } else {
      // --- APPLY SCROLL: RENDER MODE (Markdown) ---
      let scrolled = false
      if (anchorText) {
        const walker = document.createTreeWalker(newEl, NodeFilter.SHOW_TEXT, null, false)
        let node
        while (node = walker.nextNode()) {
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

const copyToClipboard = async (text, el) => {
  if (!el) return
  await navigator.clipboard.writeText(text)
  const originalText = el.innerText
  el.innerText = "Copied!"
  setTimeout(() => { if (el) el.innerText = originalText }, 2000)
}

const renderSegmentTitle = (key, map) => {
  return map[key]?.label || map[key] || key
}

const getFriendlyNames = () => {
  const friendly = {}
  for (const k in props.conceptQuestionsMap) {
    friendly[k] = props.conceptQuestionsMap[k].label || k
  }
  return friendly
}

const toggleSignoff = (key, dataRef) => {
  dataRef[key] = !dataRef[key]
  if (dataRef[key]) {
    if (activeSegmentKey.value === key) {
      reviewerEditMode.value = false
    }
    // Automatically accept diff when locking
    props.pData.concept_baselines[key] = undefined
  }
}

const handleSignoffAndNext = (key, signoffsRef, keysArray) => {
  signoffsRef[key] = true
  // Automatically accept diff when locking
  props.pData.concept_baselines[key] = undefined

  const idx = keysArray.indexOf(key)
  for (let i = idx + 1; i < keysArray.length; i++) {
    if (!signoffsRef[keysArray[i]]) {
      activeSegmentKey.value = keysArray[i]
      reviewerEditMode.value = false
      return
    }
  }
  for (let i = 0; i < idx; i++) {
    if (!signoffsRef[keysArray[i]]) {
      activeSegmentKey.value = keysArray[i]
      reviewerEditMode.value = false
      return
    }
  }
  reviewerEditMode.value = false
}

const allSigned = (signoffs) => {
  return Object.values(signoffs).every(v => v === true)
}

const isGoalFilled = computed(() => {
  return props.pData.goal.trim().length > 0
})

const generateConcept = async (e) => {
  const btn = e.currentTarget // Capture immediately before async bridge call
  const prompt = await generateConceptPrompt(props.pData, props.conceptQuestionsMap)
  await copyToClipboard(prompt, btn)
  showPasteArea.value = true
}

const processConcept = async () => {
  const content = props.pData.concept_llm_response
  const parsed = await parseStarterSegments(content)
  if (!parsed || !Object.keys(parsed).length) {
    props.pData.concept_md = content
    props.pData.concept_llm_response = ''
    return
  }

  const friendly = getFriendlyNames()
  const mapped = await mapParsedSegmentsToKeys(parsed, friendly)
  props.pData.concept_segments = mapped
  props.pData.concept_signoffs = {}
  props.pData.concept_baselines = {}
  Object.keys(mapped).forEach(k => props.pData.concept_signoffs[k] = false)
  props.pData.concept_md = ''

  const keys = CONCEPT_ORDER.filter(k => mapped[k] !== undefined)
  activeSegmentKey.value = keys[0] || Object.keys(mapped)[0]
  reviewerEditMode.value = false
}

const mergeConcept = async () => {
  if (!confirm("Merge all segments into a single document?\n\nThis cannot be undone.")) {
    return
  }

  const md = await assembleStarterDocument(props.pData.concept_segments, CONCEPT_ORDER, getFriendlyNames())
  props.pData.concept_md = md
  props.pData.concept_segments = {}
  props.pData.concept_signoffs = {}
  props.pData.concept_baselines = {}
  activeSegmentKey.value = null
}

const stripMarkdownWrapper = (text) => {
  let clean = text.trim()
  if (clean.startsWith("```") && clean.endsWith("```")) {
    const firstNewline = clean.indexOf('\n')
    if (firstNewline !== -1) {
      return clean.substring(firstNewline + 1, clean.length - 3).trim()
    }
  }
  return clean
}

// --- Rewrite Logic ---
const openRewriteModal = (isMergedMode) => {
  rewriteIsMergedMode.value = isMergedMode
  if (isMergedMode) {
    rewriteContext.value = {
      keys: ['full_content'],
      names: { full_content: 'Full Concept' },
      data: { full_content: props.pData.concept_md },
      signoffs: {}
    }
  } else {
    rewriteContext.value = {
      keys: Object.keys(props.pData.concept_segments),
      names: getFriendlyNames(),
      data: props.pData.concept_segments,
      signoffs: props.pData.concept_signoffs
    }
  }
  showRewriteModal.value = true
}

const handleRewriteApply = async ({ cleanContent, notes }) => {
  showRewriteModal.value = false

  if (notes) {
    notesContent.value = notes
    showNotesModal.value = true
  }

  if (rewriteIsMergedMode.value) {
    props.pData.concept_baselines['__merged__'] = props.pData.concept_md
    props.pData.concept_md = stripMarkdownWrapper(cleanContent)
  } else {
    const parsed = await parseStarterSegments(cleanContent)
    if (!parsed || !Object.keys(parsed).length) {
      alert("Could not parse segments.")
      return
    }

    const mapped = await mapParsedSegmentsToKeys(parsed, getFriendlyNames())

    for (const key in mapped) {
      if (props.pData.concept_segments[key] !== undefined && !props.pData.concept_signoffs[key]) {
        props.pData.concept_baselines[key] = props.pData.concept_segments[key]
        props.pData.concept_segments[key] = mapped[key]
      }
    }
  }
}

const acceptDiff = () => {
  if (props.pData.concept_md) {
    props.pData.concept_baselines['__merged__'] = undefined
  } else if (activeSegmentKey.value) {
    props.pData.concept_baselines[activeSegmentKey.value] = undefined
  }
}

const refuseDiff = () => {
  if (props.pData.concept_md && props.pData.concept_baselines['__merged__']) {
    props.pData.concept_md = props.pData.concept_baselines['__merged__']
    props.pData.concept_baselines['__merged__'] = undefined
  } else if (activeSegmentKey.value && props.pData.concept_baselines[activeSegmentKey.value]) {
    props.pData.concept_segments[activeSegmentKey.value] = props.pData.concept_baselines[activeSegmentKey.value]
    props.pData.concept_baselines[activeSegmentKey.value] = undefined
  }
}

const hasPendingDiffs = computed(() => {
  return Object.keys(props.pData.concept_baselines).some(k => k !== '__merged__' && props.pData.concept_baselines[k] !== undefined)
})

const acceptAllConfirm = ref(false)
let acceptAllTimer = null

const handleAcceptAllClick = () => {
  if (acceptAllConfirm.value) {
    for (const k in props.pData.concept_baselines) {
      if (k !== '__merged__') {
        props.pData.concept_baselines[k] = undefined
      }
    }
    acceptAllConfirm.value = false
    clearTimeout(acceptAllTimer)
  } else {
    acceptAllConfirm.value = true
    acceptAllTimer = setTimeout(() => {
      acceptAllConfirm.value = false
    }, 2500)
  }
}

// --- Questions Context Accessors ---

const getSegmentedQuestionPrompt = async (question) => {
  let context = ""
  const names = getFriendlyNames()

  for (const k of CONCEPT_ORDER) {
    if (props.pData.concept_segments[k] === undefined || k === activeSegmentKey.value) continue
    const txt = props.pData.concept_segments[k].trim()
    if (txt) context += `--- Context: ${names[k] || k} ---\n${txt}\n\n`
  }

  const name = names[activeSegmentKey.value] || activeSegmentKey.value
  const text = props.pData.concept_segments[activeSegmentKey.value]
  return await getStarterQuestionPrompt(context, name, text, question)
}

const getMergedQuestionPrompt = async (question) => {
  const context = `--- User Goal ---\n${props.pData.goal}`
  return await getStarterQuestionPrompt(context, "Full Concept", props.pData.concept_md, question)
}

const handleReset = () => {
  if (confirm("Are you sure you want to start over? This will clear current progress for the Concept step.")) {
    props.pData.concept_segments = {}
    props.pData.concept_signoffs = {}
    props.pData.concept_baselines = {}
    props.pData.concept_md = ""
    props.pData.concept_llm_response = ""
    activeSegmentKey.value = null
    reviewerEditMode.value = false
    showPasteArea.value = false
    showQuestions.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col relative" @wheel.ctrl.prevent="handleZoom">
    <template v-if="pData.concept_md">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-2xl font-bold text-white">Review Concept</h3>
        <div class="flex space-x-3">
          <button @click="handleReset" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest mr-2">Start Over</button>

          <div v-if="pData.concept_baselines['__merged__']" class="flex space-x-2">
            <button
              @click="refuseDiff"
              class="px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center space-x-2 bg-gray-700 text-red-400 hover:bg-red-900/40"
            >
              <XIcon class="w-4 h-4" />
              <span>Refuse</span>
            </button>
            <button
              @click="acceptDiff"
              class="px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center space-x-2 bg-cm-green text-white hover:brightness-110"
            >
              <Check class="w-4 h-4" />
              <span>Accept Diff</span>
            </button>
          </div>

          <template v-if="!pData.concept_baselines['__merged__']">
            <button
              @click="showQuestions = !showQuestions"
              class="px-4 py-1.5 rounded font-bold text-sm shadow transition-colors flex items-center space-x-2"
              :class="showQuestions ? 'bg-cm-blue text-white' : 'bg-gray-700 text-gray-300 hover:text-white'"
            >
              <HelpCircle class="w-4 h-4" />
              <span>Questions</span>
            </button>
            <button @click="openRewriteModal(true)" class="bg-cm-blue text-white px-4 py-1.5 rounded font-bold text-sm shadow transition-colors">Rewrite</button>
            <button @click="toggleReviewerEditMode(null, false)" class="bg-gray-700 text-white px-4 py-1.5 rounded font-bold text-sm shadow transition-colors">{{ reviewerEditMode ? 'Finish Editing' : 'Edit Markdown' }}</button>
          </template>
        </div>
      </div>

      <ReviewerQuestions
        v-if="showQuestions"
        :questions="['Is this concept clearly explained?', 'Does the target audience match the goal?', 'Are there any major omissions in the feature list?']"
        :getPrompt="getMergedQuestionPrompt"
      />

      <div class="flex-grow bg-cm-input-bg border border-gray-700 rounded overflow-hidden flex flex-col">
        <textarea v-if="reviewerEditMode" ref="scrollRef" v-model="pData.concept_md" class="w-full h-full p-6 bg-cm-input-bg text-gray-100 font-mono outline-none selectable shrink-0" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
        <div v-else ref="scrollRef" class="w-full h-full p-6 overflow-y-auto custom-scrollbar">
          <DiffViewer
            v-if="pData.concept_baselines['__merged__']"
            :oldText="pData.concept_baselines['__merged__']"
            :newText="pData.concept_md"
            :fontSize="editorFontSize"
          />
          <MarkdownRenderer v-else :content="pData.concept_md" :fontSize="editorFontSize" @dblclick="toggleReviewerEditMode($event, true)" />
        </div>
      </div>

      <div v-if="!isLookingBack" class="shrink-0 pt-6 flex justify-end">
        <button @click="$emit('next')" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-3 px-12 rounded shadow-lg transition-all flex items-center group">
          Next Step: Tech Stack
          <ChevronRight class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </template>

    <template v-else-if="Object.keys(pData.concept_segments).length">
       <div class="flex h-full min-h-0">
         <div class="w-72 shrink-0 border-r border-gray-700 pr-4 overflow-y-auto space-y-2">
           <div class="p-2 mb-4 border-b border-gray-700 flex flex-col items-center space-y-3 pb-3">
             <button @click="handleReset" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest">Start Over</button>
             <button
                v-if="hasPendingDiffs"
                @click="handleAcceptAllClick"
                class="transition-colors text-[10px] font-bold uppercase tracking-widest flex items-center px-3 py-1.5 rounded border select-none w-full justify-center"
                :class="acceptAllConfirm ? 'bg-cm-green text-white border-cm-green' : 'text-cm-green hover:text-green-400 bg-cm-green/10 border-cm-green/30 hover:bg-cm-green/20'"
                title="Accept all pending segment diffs"
              >
               <CheckCheck class="w-3.5 h-3.5 mr-1.5 shrink-0" />
               <span class="truncate">{{ acceptAllConfirm ? 'Click to confirm' : 'Accept All Diffs' }}</span>
             </button>
           </div>
           <div v-for="key in Object.keys(pData.concept_segments)" :key="key"
                @click="activeSegmentKey = key; reviewerEditMode = false"
                class="p-3 rounded cursor-pointer border transition-all flex items-center justify-between group"
                :class="activeSegmentKey === key ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'">
             <div class="flex items-center space-x-2 truncate">
                <div v-if="pData.concept_baselines[key]" class="w-1.5 h-1.5 rounded-full bg-cm-green shrink-0"></div>
                <span class="truncate pr-2">{{ renderSegmentTitle(key, conceptQuestionsMap) }}</span>
             </div>
             <button @click.stop="toggleSignoff(key, pData.concept_signoffs)" class="shrink-0 opacity-70 hover:opacity-100 transition-opacity" :title="pData.concept_signoffs[key] ? 'Unlock' : 'Lock'">
               <img v-if="pData.concept_signoffs[key] && lockedIcon" :src="lockedIcon" class="h-4 w-auto object-contain" />
               <img v-else-if="!pData.concept_signoffs[key] && unlockedIcon" :src="unlockedIcon" class="h-4 w-auto object-contain" />
             </button>
           </div>
         </div>
         <div class="flex-grow pl-6 flex flex-col min-w-0">
           <div class="flex justify-between items-center mb-4">
               <h3 class="text-xl font-bold text-white">{{ renderSegmentTitle(activeSegmentKey, conceptQuestionsMap) }}</h3>
               <div class="flex space-x-2">
                 <div v-if="pData.concept_baselines[activeSegmentKey] && !pData.concept_signoffs[activeSegmentKey]" class="flex space-x-2">
                   <button
                     @click="refuseDiff"
                     class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1 bg-gray-700 text-red-400 hover:bg-red-900/40"
                   >
                     <XIcon class="w-3 h-3" />
                     <span>Refuse</span>
                   </button>
                   <button
                     @click="acceptDiff"
                     class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1 bg-cm-green text-white hover:brightness-110"
                   >
                     <Check class="w-3 h-3" />
                     <span>Accept Diff</span>
                   </button>
                 </div>

                 <template v-if="!pData.concept_signoffs[activeSegmentKey] && !pData.concept_baselines[activeSegmentKey]">
                   <button
                      @click="showQuestions = !showQuestions"
                      class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1"
                      :class="showQuestions ? 'bg-cm-blue text-white' : 'bg-gray-700 text-gray-300 hover:text-white'"
                    >
                      <HelpCircle class="w-3 h-3" />
                      <span>Questions</span>
                    </button>
                   <button @click="openRewriteModal(false)" class="bg-cm-blue text-white px-3 py-1 rounded text-xs font-bold shadow transition-colors">Rewrite</button>
                   <button @click="toggleReviewerEditMode(null, false)" class="bg-gray-700 text-white px-3 py-1 rounded text-xs shadow">{{ reviewerEditMode ? 'Render' : 'Edit' }}</button>
                 </template>
               </div>
           </div>

           <ReviewerQuestions
              v-if="showQuestions && !pData.concept_signoffs[activeSegmentKey]"
              :questions="conceptQuestionsMap[activeSegmentKey]?.questions || []"
              :getPrompt="getSegmentedQuestionPrompt"
            />

           <div class="flex-grow border border-gray-700 rounded bg-cm-input-bg overflow-hidden">
               <textarea v-if="reviewerEditMode" ref="scrollRef" v-model="pData.concept_segments[activeSegmentKey]" class="w-full h-full bg-cm-input-bg text-white p-6 outline-none custom-scrollbar font-sans leading-relaxed selectable" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
               <div v-else ref="scrollRef" class="w-full h-full overflow-y-auto p-6 custom-scrollbar">
                 <DiffViewer
                    v-if="pData.concept_baselines[activeSegmentKey]"
                    :oldText="pData.concept_baselines[activeSegmentKey]"
                    :newText="pData.concept_segments[activeSegmentKey]"
                    :fontSize="editorFontSize"
                  />
                 <MarkdownRenderer v-else :content="pData.concept_segments[activeSegmentKey]" :fontSize="editorFontSize" @dblclick="!pData.concept_signoffs[activeSegmentKey] && toggleReviewerEditMode($event, true)" />
               </div>
           </div>
           <div class="shrink-0 pt-4 flex justify-end space-x-4">
               <button v-if="pData.concept_signoffs[activeSegmentKey]" @click="toggleSignoff(activeSegmentKey, pData.concept_signoffs)" class="bg-cm-green hover:bg-green-600 text-white px-8 py-2 rounded font-bold shadow transition-colors">Unlock</button>
               <button v-else @click="handleSignoffAndNext(activeSegmentKey, pData.concept_signoffs, Object.keys(pData.concept_segments))" class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2 rounded font-bold shadow transition-colors">Lock & Next</button>
               <button v-if="allSigned(pData.concept_signoffs)" @click="mergeConcept" class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2 rounded font-bold shadow transition-colors">Merge & Finalize</button>
           </div>
         </div>
       </div>
    </template>
    <template v-else>
      <div class="max-w-3xl mx-auto w-full space-y-6 text-gray-100">
        <h3 class="text-2xl font-bold text-white">Project Concept</h3>
        <p class="text-gray-400">Describe what you want to build in a few sentences. The LLM will use this to generate the core sections.</p>
        <textarea v-model="pData.goal" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue selectable" :style="{ fontSize: editorFontSize + 'px' }" placeholder="e.g. A desktop tool that bundles project code..."></textarea>
        <div class="bg-gray-800 p-6 rounded border border-gray-700 space-y-4">
          <button v-if="isGoalFilled" @click="generateConcept" class="w-full bg-cm-blue text-white font-bold py-3 rounded">1. Copy Prompt for LLM</button>
          <template v-if="showPasteArea">
            <textarea v-model="pData.concept_llm_response" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue" :style="{ fontSize: editorFontSize + 'px' }" placeholder="Paste LLM response here..."></textarea>
            <button @click="processConcept" :disabled="!pData.concept_llm_response" class="w-full bg-cm-green text-white font-bold py-3 rounded disabled:opacity-50">2. Process & Review</button>
          </template>
        </div>
      </div>
    </template>

    <!-- Overlay Modals -->
    <RewriteModal
      v-if="showRewriteModal"
      :contextData="rewriteContext"
      :isMergedMode="rewriteIsMergedMode"
      @close="showRewriteModal = false"
      @apply="handleRewriteApply"
    />
    <NotesModal
      v-if="showNotesModal"
      :notes="notesContent"
      @close="showNotesModal = false"
    />
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>