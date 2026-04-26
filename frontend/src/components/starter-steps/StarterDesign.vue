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
  designQuestionsMap: {
    type: Object,
    required: true
  },
  isLookingBack: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['next'])

// Sync with Backend DESIGN_ORDER and DESIGN_SEGMENTS constants
const DESIGN_ORDER = ["arch_overview", "data_models", "component_breakdown"]
const DESIGN_SEGMENTS = {
    "arch_overview": "Architecture Overview",
    "data_models": "Data Models & State",
    "component_breakdown": "Component Breakdown"
}

const {
  generateDesignPrompt,
  parseStarterSegments,
  mapParsedSegmentsToKeys,
  assembleStarterDocument,
  getStarterQuestionPrompt,
  getStarterPivotPrompt,
  editorFontSize,
  handleZoom,
  copyText
} = useAppState()

const showPasteArea = ref(!!props.pData.design_llm_response)
const showQuestions = ref(false)
const showRewriteModal = ref(false)
const rewriteContext = ref(null)
const rewriteIsMergedMode = ref(false)
const rewriteIsPivotMode = ref(false)
const showNotesModal = ref(false)
const notesContent = ref('')

const getFriendlyNames = () => {
  const friendly = {}
  for (const k in props.designQuestionsMap) {
    friendly[k] = props.designQuestionsMap[k].label || k
  }
  if (Object.keys(friendly).length === 0) return DESIGN_SEGMENTS
  return friendly
}

const generateDesign = async (e) => {
  const btn = e.currentTarget
  if (!e.ctrlKey) {
    const prompt = await generateDesignPrompt(props.pData, props.designQuestionsMap)
    await copyText(prompt)
    const originalText = btn.innerText
    btn.innerText = "Copied!"
    setTimeout(() => { if (btn) btn.innerText = originalText }, 2000)
  }
  showPasteArea.value = true
}

const processDesign = async () => {
  const content = props.pData.design_llm_response
  const parsed = await parseStarterSegments(content)
  if (!parsed || !Object.keys(parsed).length) {
    props.pData.design_md = content
    props.pData.design_llm_response = ''
    return
  }

  const mapped = await mapParsedSegmentsToKeys(parsed, getFriendlyNames())

  Object.keys(props.pData.design_segments).forEach(k => delete props.pData.design_segments[k])
  Object.keys(props.pData.design_signoffs).forEach(k => delete props.pData.design_signoffs[k])
  Object.keys(props.pData.design_baselines).forEach(k => delete props.pData.design_baselines[k])

  Object.assign(props.pData.design_segments, mapped)
  Object.keys(mapped).forEach(k => props.pData.design_signoffs[k] = false)
  props.pData.design_llm_response = ''
}

const mergeDesign = async () => {
  if (!confirm("Merge all segments into a single document?\n\nThis cannot be undone.")) {
    return
  }

  const md = await assembleStarterDocument(props.pData.design_segments, DESIGN_ORDER, getFriendlyNames())
  props.pData.design_md = md

  Object.keys(props.pData.design_segments).forEach(k => delete props.pData.design_segments[k])
  Object.keys(props.pData.design_signoffs).forEach(k => delete props.pData.design_signoffs[k])
  Object.keys(props.pData.design_baselines).forEach(k => delete props.pData.design_baselines[k])
}

// --- Rewrite Logic ---
const openRewriteModal = (isMergedMode, isPivotMode = false) => {
  rewriteIsMergedMode.value = isMergedMode
  rewriteIsPivotMode.value = isPivotMode
  if (isMergedMode) {
    rewriteContext.value = {
      keys: ['full_content'],
      names: { full_content: 'Full System Design' },
      data: { full_content: props.pData.design_md },
      signoffs: {}
    }
  } else {
    rewriteContext.value = {
      keys: Object.keys(props.pData.design_segments),
      names: getFriendlyNames(),
      data: props.pData.design_segments,
      signoffs: props.pData.design_signoffs
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
    if (props.pData.design_md !== cleanContent) {
      props.pData.design_baselines['__merged__'] = props.pData.design_md
      props.pData.design_md = cleanContent
    }
  } else {
    const parsed = await parseStarterSegments(cleanContent)
    if (!parsed || !Object.keys(parsed).length) {
      alert("Could not parse segments.")
      return
    }

    const mapped = await mapParsedSegmentsToKeys(parsed, getFriendlyNames())

    for (const key in mapped) {
      const oldVal = props.pData.design_segments[key]
      const newVal = mapped[key]

      if (oldVal !== undefined && !props.pData.design_signoffs[key]) {
        if (oldVal !== newVal) {
          props.pData.design_baselines[key] = oldVal
          props.pData.design_segments[key] = newVal
        }
      }
    }
  }
}

// --- Pivot Execution Flow ---
const handlePivot = async (alternative, selectedText, activeKey = 'full_content') => {
  const isMergedMode = !!props.pData.design_md;
  const targets = [];
  const references = [];
  const names = isMergedMode ? { full_content: 'Full System Design' } : getFriendlyNames();
  const data = isMergedMode ? { full_content: props.pData.design_md } : props.pData.design_segments;

  if (!isMergedMode) {
    for (const k of Object.keys(props.pData.design_segments)) {
      if (props.pData.design_signoffs[k]) {
        references.push(k);
      } else {
        targets.push(k);
      }
    }
  }

  // 1. Ask Backend to generate the highly contextual pivot prompt
  const prompt = await getStarterPivotPrompt(
    alternative,
    selectedText,
    activeKey,
    targets,
    references,
    names,
    data,
    isMergedMode
  );

  // 2. Put it on clipboard automatically
  await copyText(prompt);

  // 3. Open Rewrite Modal in Pivot mode (skips manual instruction step)
  openRewriteModal(isMergedMode, true);
}

// --- Questions Context Accessors ---
const getSegmentedQuestionPrompt = async (question, activeKey) => {
  let context = ""
  const names = getFriendlyNames()

  for (const k of DESIGN_ORDER) {
    if (props.pData.design_segments[k] === undefined || k === activeKey) continue
    const txt = props.pData.design_segments[k].trim()
    if (txt) context += `--- Context: ${names[k] || k} ---\n${txt}\n\n`
  }

  const name = names[activeKey] || activeKey
  const text = props.pData.design_segments[activeKey]
  return await getStarterQuestionPrompt(context, name, text, question)
}

const getMergedQuestionPrompt = async (question) => {
  const context = `--- Project Concept ---\n${props.pData.concept_md}`
  return await getStarterQuestionPrompt(context, "System Design", props.pData.design_md, question)
}

const handleReset = () => {
  if (confirm("Are you sure you want to start over? This will clear current progress for the Design step.")) {
    Object.keys(props.pData.design_segments).forEach(k => delete props.pData.design_segments[k])
    Object.keys(props.pData.design_signoffs).forEach(k => delete props.pData.design_signoffs[k])
    Object.keys(props.pData.design_baselines).forEach(k => delete props.pData.design_baselines[k])
    props.pData.design_md = ""
    props.pData.design_llm_response = ""
    showPasteArea.value = false
    showQuestions.value = false
  }
}
</script>

    <template>
      <div class="h-full flex flex-col relative" @wheel.ctrl.prevent="handleZoom">
        <template v-if="pData.design_md">
          <FullTextReviewer
            title="Review System Design"
            :content="pData.design_md"
            @update:content="val => pData.design_md = val"
            v-model:showQuestions="showQuestions"
            :baselines="pData.design_baselines"
            :questions="['Are the data models normalized correctly?', 'Does the component breakdown cover all user flows?']"
            :getQuestionPrompt="getMergedQuestionPrompt"
            :isLookingBack="isLookingBack"
            reviewInfoKey="starter_design_review"
            nextButtonText="Next Step: TODO Plan"
            @reset="handleReset"
            @rewrite="openRewriteModal(true)"
            @pivot="handlePivot"
            @next="$emit('next')"
          />
        </template>

        <template v-else-if="Object.keys(pData.design_segments).length">
          <SegmentedReviewer
            :segments="pData.design_segments"
            :signoffs="pData.design_signoffs"
            :baselines="pData.design_baselines"
            v-model:showQuestions="showQuestions"
            :orderedKeys="DESIGN_ORDER"
            :friendlyNames="getFriendlyNames()"
            :questionsMap="designQuestionsMap"
            :getQuestionPrompt="getSegmentedQuestionPrompt"
            @reset="handleReset"
            @rewrite="openRewriteModal(false)"
            @pivot="handlePivot"
            @merge="mergeDesign"
          />
        </template>

        <template v-else>
          <div class="max-w-3xl mx-auto w-full space-y-6 text-gray-100 pb-12">
            <h3 class="text-2xl font-bold text-white">Generate System Design</h3>

            <div class="flex justify-between items-center bg-gray-800 p-6 rounded border border-gray-700 shadow-lg">
              <div class="text-gray-300"><span class="font-bold text-white">1.</span> Copy prompt for LLM</div>
              <button @click="generateDesign" v-info="'starter_design_gen'" class="bg-cm-blue hover:bg-blue-500 text-white px-6 py-2.5 rounded shadow transition-colors font-bold">Copy Design Prompt</button>
            </div>

            <div v-if="showPasteArea" class="bg-gray-800 p-6 rounded border border-gray-700 shadow-lg space-y-4">
              <div class="text-gray-300"><span class="font-bold text-white">2.</span> Paste LLM Response (with tags)</div>
              <textarea v-model="pData.design_llm_response" class="w-full h-96 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar selectable" :style="{ fontSize: editorFontSize + 'px' }" placeholder="Paste response here..."></textarea>
              <div class="flex justify-end">
                <button @click="processDesign" :disabled="!pData.design_llm_response" class="bg-cm-green hover:bg-green-600 text-white px-10 py-3 rounded shadow-lg transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed active:scale-95">Process & Review</button>
              </div>
            </div>
          </div>
        </template>

    <RewriteModal
      v-if="showRewriteModal"
      :contextData="rewriteContext"
      :isMergedMode="rewriteIsMergedMode"
      :isPivotMode="rewriteIsPivotMode"
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