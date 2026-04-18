<script setup>
import { ref, computed } from 'vue'
import { useAppState } from '../../composables/useAppState'
import RewriteModal from './RewriteModal.vue'
import NotesModal from './NotesModal.vue'
import FullTextReviewer from './widgets/FullTextReviewer.vue'
import SegmentedReviewer from './widgets/SegmentedReviewer.vue'

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
  handleZoom
} = useAppState()

const showPasteArea = ref(!!props.pData.concept_llm_response)
const showRewriteModal = ref(false)
const rewriteContext = ref(null)
const rewriteIsMergedMode = ref(false)
const showNotesModal = ref(false)
const notesContent = ref('')

const getFriendlyNames = () => {
  const friendly = {}
  for (const k in props.conceptQuestionsMap) {
    friendly[k] = props.conceptQuestionsMap[k].label || k
  }
  return friendly
}

const isGoalFilled = computed(() => {
  return props.pData.goal.trim().length > 0
})

const generateConcept = async (e) => {
  const btn = e.currentTarget
  const prompt = await generateConceptPrompt(props.pData, props.conceptQuestionsMap)
  await navigator.clipboard.writeText(prompt)
  const originalText = btn.innerText
  btn.innerText = "Copied!"
  setTimeout(() => { if (btn) btn.innerText = originalText }, 2000)
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

  const mapped = await mapParsedSegmentsToKeys(parsed, getFriendlyNames())

  for (const k in props.pData.concept_segments) delete props.pData.concept_segments[k]
  for (const k in props.pData.concept_signoffs) delete props.pData.concept_signoffs[k]
  for (const k in props.pData.concept_baselines) delete props.pData.concept_baselines[k]

  Object.assign(props.pData.concept_segments, mapped)
  Object.keys(mapped).forEach(k => props.pData.concept_signoffs[k] = false)
  props.pData.concept_md = ''
}

const mergeConcept = async () => {
  if (!confirm("Merge all segments into a single document?\n\nThis cannot be undone.")) {
    return
  }

  const md = await assembleStarterDocument(props.pData.concept_segments, CONCEPT_ORDER, getFriendlyNames())
  props.pData.concept_md = md

  for (const k in props.pData.concept_segments) delete props.pData.concept_segments[k]
  for (const k in props.pData.concept_signoffs) delete props.pData.concept_signoffs[k]
  for (const k in props.pData.concept_baselines) delete props.pData.concept_baselines[k]
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
    if (props.pData.concept_md !== cleanContent) {
      props.pData.concept_baselines['__merged__'] = props.pData.concept_md
      props.pData.concept_md = cleanContent
    }
  } else {
    const parsed = await parseStarterSegments(cleanContent)
    if (!parsed || !Object.keys(parsed).length) {
      alert("Could not parse segments.")
      return
    }

    const mapped = await mapParsedSegmentsToKeys(parsed, getFriendlyNames())

    for (const key in mapped) {
      const oldVal = props.pData.concept_segments[key]
      const newVal = mapped[key]

      if (oldVal !== undefined && !props.pData.concept_signoffs[key]) {
        if (oldVal !== newVal) {
          props.pData.concept_baselines[key] = oldVal
          props.pData.concept_segments[key] = newVal
        }
      }
    }
  }
}

// --- Questions Context Accessors ---
const getSegmentedQuestionPrompt = async (question, activeKey) => {
  let context = ""
  const names = getFriendlyNames()

  for (const k of CONCEPT_ORDER) {
    if (props.pData.concept_segments[k] === undefined || k === activeKey) continue
    const txt = props.pData.concept_segments[k].trim()
    if (txt) context += `--- Context: ${names[k] || k} ---\n${txt}\n\n`
  }

  const name = names[activeKey] || activeKey
  const text = props.pData.concept_segments[activeKey]
  return await getStarterQuestionPrompt(context, name, text, question)
}

const getMergedQuestionPrompt = async (question) => {
  const context = `--- User Goal ---\n${props.pData.goal}`
  return await getStarterQuestionPrompt(context, "Full Concept", props.pData.concept_md, question)
}

const handleReset = () => {
  if (confirm("Are you sure you want to start over? This will clear current progress for the Concept step.")) {
    for (const k in props.pData.concept_segments) delete props.pData.concept_segments[k]
    for (const k in props.pData.concept_signoffs) delete props.pData.concept_signoffs[k]
    for (const k in props.pData.concept_baselines) delete props.pData.concept_baselines[k]
    props.pData.concept_md = ""
    props.pData.concept_llm_response = ""
    showPasteArea.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col relative" @wheel.ctrl.prevent="handleZoom">
    <template v-if="pData.concept_md">
      <FullTextReviewer
        title="Review Concept"
        :content="pData.concept_md"
        @update:content="val => pData.concept_md = val"
        :baselines="pData.concept_baselines"
        :questions="['Is this concept clearly explained?', 'Does the target audience match the goal?', 'Are there any major omissions in the feature list?']"
        :getQuestionPrompt="getMergedQuestionPrompt"
        :isLookingBack="isLookingBack"
        reviewInfoKey="starter_concept_review"
        nextButtonText="Next Step: Tech Stack"
        @reset="handleReset"
        @rewrite="openRewriteModal(true)"
        @next="$emit('next')"
      />
    </template>

    <template v-else-if="Object.keys(pData.concept_segments).length">
      <SegmentedReviewer
        :segments="pData.concept_segments"
        :signoffs="pData.concept_signoffs"
        :baselines="pData.concept_baselines"
        :orderedKeys="Object.keys(pData.concept_segments)"
        :friendlyNames="getFriendlyNames()"
        :questionsMap="conceptQuestionsMap"
        :getQuestionPrompt="getSegmentedQuestionPrompt"
        @reset="handleReset"
        @rewrite="openRewriteModal(false)"
        @merge="mergeConcept"
      />
    </template>

    <template v-else>
      <div class="max-w-3xl mx-auto w-full space-y-6 text-gray-100">
        <h3 class="text-2xl font-bold text-white">Project Concept</h3>
        <p class="text-gray-400">Describe what you want to build in a few sentences. The LLM will use this to generate the core sections.</p>
        <textarea v-model="pData.goal" v-info="'starter_concept_goal'" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue selectable" :style="{ fontSize: editorFontSize + 'px' }" placeholder="e.g. A desktop tool that bundles project code..."></textarea>
        <div v-if="isGoalFilled || showPasteArea" class="bg-gray-800 p-6 rounded border border-gray-700 space-y-4">
          <button v-if="isGoalFilled" @click="generateConcept" v-info="'starter_concept_gen'" class="w-full bg-cm-blue text-white font-bold py-3 rounded">1. Copy Prompt for LLM</button>
          <template v-if="showPasteArea">
            <textarea v-model="pData.concept_llm_response" v-info="'starter_gen_response'" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue" :style="{ fontSize: editorFontSize + 'px' }" placeholder="Paste LLM response here..."></textarea>
            <button @click="processConcept" v-info="'starter_gen_process'" :disabled="!pData.concept_llm_response" class="w-full bg-cm-green text-white font-bold py-3 rounded disabled:opacity-50">2. Process & Review</button>
          </template>
        </div>
      </div>
    </template>

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