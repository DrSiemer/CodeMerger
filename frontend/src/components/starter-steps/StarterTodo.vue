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
  todoQuestionsMap: {
    type: Object,
    required: true
  },
  isLookingBack: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['next'])

const TODO_PHASES = {
  "setup": "Environment Setup",
  "database": "Database & Schema",
  "api": "API & Backend",
  "frontend": "Frontend & UI",
  "logic": "Core Logic & Actions",
  "polish": "Automation & Polish",
  "deployment": "Deployment"
}

const {
  generateTodoPrompt,
  parseStarterSegments,
  mapParsedSegmentsToKeys,
  assembleStarterDocument,
  getStarterQuestionPrompt,
  editorFontSize,
  handleZoom
} = useAppState()

const showPasteArea = ref(!!props.pData.todo_llm_response)
const showQuestions = ref(false)
const showRewriteModal = ref(false)
const rewriteContext = ref(null)
const rewriteIsMergedMode = ref(false)
const showNotesModal = ref(false)
const notesContent = ref('')

const getFriendlyNames = () => {
  const friendly = {}
  for (const k in props.todoQuestionsMap) {
    friendly[k] = props.todoQuestionsMap[k].label || k
  }
  if (Object.keys(friendly).length === 0) return TODO_PHASES
  return friendly
}

const orderedTodoKeys = computed(() => {
  const keys = Object.keys(props.pData.todo_segments)
  if (keys.includes('deployment')) {
    keys.splice(keys.indexOf('deployment'), 1)
    keys.push('deployment')
  }
  return keys
})

const generateTodo = async (e) => {
  const btn = e.currentTarget
  const prompt = await generateTodoPrompt(props.pData, props.todoQuestionsMap)
  await navigator.clipboard.writeText(prompt)
  const originalText = btn.innerText
  btn.innerText = "Copied!"
  setTimeout(() => { if (btn) btn.innerText = originalText }, 2000)
  showPasteArea.value = true
}

const processTodo = async () => {
  const content = props.pData.todo_llm_response
  const parsed = await parseStarterSegments(content)
  if (!parsed || !Object.keys(parsed).length) {
    props.pData.todo_md = content
    props.pData.todo_llm_response = ''
    return
  }

  const mapped = await mapParsedSegmentsToKeys(parsed, getFriendlyNames())

  for (const k in props.pData.todo_segments) delete props.pData.todo_segments[k]
  for (const k in props.pData.todo_signoffs) delete props.pData.todo_signoffs[k]
  for (const k in props.pData.todo_baselines) delete props.pData.todo_baselines[k]

  Object.assign(props.pData.todo_segments, mapped)
  Object.keys(mapped).forEach(k => props.pData.todo_signoffs[k] = false)
  props.pData.todo_llm_response = ''
}

const mergeTodo = async () => {
  if (!confirm("Merge all segments into a single document?\n\nThis cannot be undone.")) {
    return
  }

  const md = await assembleStarterDocument(props.pData.todo_segments, orderedTodoKeys.value, getFriendlyNames())
  props.pData.todo_md = md

  for (const k in props.pData.todo_segments) delete props.pData.todo_segments[k]
  for (const k in props.pData.todo_signoffs) delete props.pData.todo_signoffs[k]
  for (const k in props.pData.todo_baselines) delete props.pData.todo_baselines[k]
}

// --- Rewrite Logic ---
const openRewriteModal = (isMergedMode) => {
  rewriteIsMergedMode.value = isMergedMode
  if (isMergedMode) {
    rewriteContext.value = {
      keys: ['full_content'],
      names: { full_content: 'Full TODO Plan' },
      data: { full_content: props.pData.todo_md },
      signoffs: {}
    }
  } else {
    rewriteContext.value = {
      keys: Object.keys(props.pData.todo_segments),
      names: getFriendlyNames(),
      data: props.pData.todo_segments,
      signoffs: props.pData.todo_signoffs
    }
  }
  showRewriteModal.value = true
}

const handleRewriteApply = async ({ cleanContent, notes }) => {
  showRewriteModal.value = false
  showQuestions.value = false

  if (notes) {
    notesContent.value = notes
    showNotesModal.value = true
  }

  if (rewriteIsMergedMode.value) {
    if (props.pData.todo_md !== cleanContent) {
      props.pData.todo_baselines['__merged__'] = props.pData.todo_md
      props.pData.todo_md = cleanContent
    }
  } else {
    const parsed = await parseStarterSegments(cleanContent)
    if (!parsed || !Object.keys(parsed).length) {
      alert("Could not parse segments.")
      return
    }

    const mapped = await mapParsedSegmentsToKeys(parsed, getFriendlyNames())

    for (const key in mapped) {
      const oldVal = props.pData.todo_segments[key]
      const newVal = mapped[key]

      if (oldVal !== undefined && !props.pData.todo_signoffs[key]) {
        if (oldVal !== newVal) {
          props.pData.todo_baselines[key] = oldVal
          props.pData.todo_segments[key] = newVal
        }
      }
    }
  }
}

// --- Questions Context Accessors ---
const getSegmentedQuestionPrompt = async (question, activeKey) => {
  let context = ""
  const names = getFriendlyNames()

  for (const k of orderedTodoKeys.value) {
    if (props.pData.todo_segments[k] === undefined || k === activeKey) continue
    const txt = props.pData.todo_segments[k].trim()
    if (txt) context += `--- Context: ${names[k] || k} ---\n${txt}\n\n`
  }

  const name = names[activeKey] || activeKey
  const text = props.pData.todo_segments[activeKey]
  return await getStarterQuestionPrompt(context, name, text, question)
}

const getMergedQuestionPrompt = async (question) => {
  const context = `--- Project Concept ---\n${props.pData.concept_md}`
  return await getStarterQuestionPrompt(context, "TODO Plan", props.pData.todo_md, question)
}

const handleReset = () => {
  if (confirm("Are you sure you want to start over? This will clear current progress for the TODO step.")) {
    for (const k in props.pData.todo_segments) delete props.pData.todo_segments[k]
    for (const k in props.pData.todo_signoffs) delete props.pData.todo_signoffs[k]
    for (const k in props.pData.todo_baselines) delete props.pData.todo_baselines[k]
    props.pData.todo_md = ""
    props.pData.todo_llm_response = ""
    showPasteArea.value = false
    showQuestions.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col relative" @wheel.ctrl.prevent="handleZoom">
    <template v-if="pData.todo_md">
      <FullTextReviewer
        title="Review TODO Plan"
        :content="pData.todo_md"
        @update:content="val => pData.todo_md = val"
        v-model:showQuestions="showQuestions"
        :baselines="pData.todo_baselines"
        :questions="['Does this plan accurately reflect the project concept?', 'Are the steps actionable and well-sequenced?', 'Is anything critical missing from the environment setup?']"
        :getQuestionPrompt="getMergedQuestionPrompt"
        :isLookingBack="isLookingBack"
        reviewInfoKey="starter_todo_review"
        nextButtonText="Next Step: Generate Files"
        @reset="handleReset"
        @rewrite="openRewriteModal(true)"
        @next="$emit('next')"
      />
    </template>

    <template v-else-if="Object.keys(pData.todo_segments).length">
      <SegmentedReviewer
        :segments="pData.todo_segments"
        :signoffs="pData.todo_signoffs"
        :baselines="pData.todo_baselines"
        v-model:showQuestions="showQuestions"
        :orderedKeys="orderedTodoKeys"
        :friendlyNames="getFriendlyNames()"
        :questionsMap="todoQuestionsMap"
        :getQuestionPrompt="getSegmentedQuestionPrompt"
        @reset="handleReset"
        @rewrite="openRewriteModal(false)"
        @merge="mergeTodo"
      />
    </template>

    <template v-else>
      <div class="max-w-3xl mx-auto w-full space-y-6 text-gray-100">
        <h3 class="text-2xl font-bold text-white">Generate TODO Plan</h3>

        <div class="flex justify-between items-center bg-gray-800 p-4 rounded border border-gray-700 mt-4">
          <div class="text-gray-300"><span class="font-bold text-white">1.</span> Copy prompt for LLM</div>
          <button @click="generateTodo" v-info="'starter_todo_gen'" class="bg-cm-blue hover:bg-blue-500 text-white px-4 py-2 rounded shadow transition-colors font-bold">Copy TODO Prompt</button>
        </div>

        <div v-if="showPasteArea" class="bg-gray-800 p-4 rounded border border-gray-700 mt-4">
          <div class="text-gray-300 mb-2"><span class="font-bold text-white">2.</span> Paste LLM Response (with tags)</div>
          <textarea v-model="pData.todo_llm_response" v-info="'starter_gen_response'" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar selectable" :style="{ fontSize: editorFontSize + 'px' }" placeholder="Paste response here..."></textarea>
          <div class="flex justify-end mt-3">
            <button @click="processTodo" v-info="'starter_gen_process'" :disabled="!pData.todo_llm_response" class="bg-cm-green hover:bg-green-600 text-white px-6 py-2 rounded shadow transition-colors disabled:opacity-50 font-bold">Process & Review</button>
          </div>
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