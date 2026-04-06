<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import {
  X, FolderPlus, Play, CheckCircle, Save, Download,
  RotateCcw, Trash2, Edit2, Key, Code, HelpCircle, FileText, Upload,
  Search, GitBranch, Filter, Milestone, ArrowDownUp
} from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import MarkdownRenderer from './MarkdownRenderer.vue'
import FileTreeNode from './FileTreeNode.vue'

const emit = defineEmits(['close'])
const {
  config,
  resizeWindow,
  statusMessage,
  getStarterSession,
  saveStarterSession,
  clearStarterSession,
  exportStarterConfig,
  loadStarterConfig,
  getConceptQuestions,
  getTodoQuestions,
  getBaseProjectData,
  getBaseFileTree,
  getTokenCountForPath,
  generateConceptPrompt,
  generateStackPrompt,
  generateTodoPrompt,
  generateMasterPrompt,
  parseStarterSegments,
  assembleStarterDocument,
  mapParsedSegmentsToKeys,
  createStarterProject,
  createStarterProjectOverwrite,
  selectDirectory,
  loadProject
} = useAppState()

// State
const currentStep = ref(1)
const maxAccessibleStep = ref(1)
const isLoading = ref(true)

const pData = reactive({
  name: '',
  parent_folder: '',
  stack: '',
  stack_experience: '',
  goal: '',
  concept_md: '',
  todo_md: '',
  base_project_path: '',
  base_project_files: [],
  include_base_reference: true,

  concept_llm_response: '',
  stack_llm_response: '',
  todo_llm_response: '',
  generate_llm_response: '',

  concept_segments: {},
  concept_signoffs: {},
  todo_phases: [],
  todo_segments: {},
  todo_signoffs: {}
})

const conceptQuestionsMap = ref({})
const todoQuestionsMap = ref({})

// Constants mapping
const CONCEPT_ORDER = ["problem_statement", "core_principles", "key_features", "user_flows", "tech_constraints"]
const TODO_ORDER = ["setup", "database", "api", "frontend", "logic", "polish", "deployment"]
const TODO_PHASES = {
    "setup": "Environment Setup",
    "database": "Database & Schema",
    "api": "API & Backend",
    "frontend": "Frontend & UI",
    "logic": "Core Logic & Actions",
    "polish": "Automation & Polish",
    "deployment": "Deployment"
}

// Segment Reviewer State
const activeSegmentKey = ref(null)
const reviewerEditMode = ref(false)

// Step 2 File Manager State
const baseFileTree = ref([])
const baseFilterText = ref('')
const baseIsExtFilter = ref(true)
const baseIsGitFilter = ref(true)
const baseShowFullPaths = ref(false)

onMounted(async () => {
  await resizeWindow(1100, 850)

  conceptQuestionsMap.value = await getConceptQuestions()
  todoQuestionsMap.value = await getTodoQuestions()

  const saved = await getStarterSession()
  if (saved && Object.keys(saved).length > 0) {
    Object.assign(pData, saved)
    recalcProgress()
    if (saved.current_step && saved.current_step <= maxAccessibleStep.value) {
      currentStep.value = saved.current_step
    } else {
      currentStep.value = maxAccessibleStep.value
    }
  } else {
    pData.parent_folder = config.value?.default_parent_folder || ''
    pData.stack_experience = config.value?.user_experience || ''
  }

  if (currentStep.value === 2 && pData.base_project_path) {
    refreshBaseTree()
  }

  isLoading.value = false
})

watch(() => pData, () => {
  recalcProgress()
  saveState()
}, { deep: true })

watch(currentStep, (newStep) => {
  if (newStep === 2 && pData.base_project_path) {
    refreshBaseTree()
  }
})

const recalcProgress = () => {
  const hasDetails = !!pData.name
  const hasConcept = (!Object.keys(pData.concept_segments).length) && !!pData.concept_md
  const hasTodo = (!Object.keys(pData.todo_segments).length) && !!pData.todo_md

  let targetMax = 1
  if (hasDetails) {
    targetMax = 3
    if (hasConcept) {
      targetMax = 5
      if (hasTodo) {
        targetMax = 6
      }
    }
  }
  if (targetMax > maxAccessibleStep.value) maxAccessibleStep.value = targetMax
}

const saveState = async () => {
  if (isLoading.value) return
  await saveStarterSession({ current_step: currentStep.value, ...pData })
}

const exportConfig = async () => {
  const exportData = { current_step: currentStep.value, ...pData }
  await exportStarterConfig(exportData)
}

const importConfig = async () => {
  const loadedData = await loadStarterConfig()
  if (loadedData) {
    Object.assign(pData, loadedData)
    recalcProgress()
    if (loadedData.current_step && loadedData.current_step <= maxAccessibleStep.value) {
      currentStep.value = loadedData.current_step
    } else {
      currentStep.value = maxAccessibleStep.value
    }
    saveState()
  }
}

const clearAll = async () => {
  if (confirm("Are you sure you want to clear all project data and start fresh?")) {
    await clearStarterSession()
    location.reload()
  }
}

// --- Navigation ---
const activeStepsList = computed(() => {
  const steps = [1]
  if (pData.base_project_path) steps.push(2)
  steps.push(3, 4, 5, 6)
  return steps
})

const goToStep = (step) => {
  if (step <= maxAccessibleStep.value || step === 2) {
    currentStep.value = step
    saveState()
  }
}

const prevStep = () => {
  const idx = activeStepsList.value.indexOf(currentStep.value)
  if (idx > 0) goToStep(activeStepsList.value[idx - 1])
}

const nextStep = () => {
  const idx = activeStepsList.value.indexOf(currentStep.value)
  if (idx < activeStepsList.value.length - 1) goToStep(activeStepsList.value[idx + 1])
}

// --- Step 2 File Manager Logic ---
const refreshBaseTree = async () => {
  baseFileTree.value = await getBaseFileTree(
    pData.base_project_path,
    baseFilterText.value,
    baseIsExtFilter.value,
    baseIsGitFilter.value,
    pData.base_project_files
  )
}

const toggleBaseFile = async (path) => {
  const idx = pData.base_project_files.findIndex(f => f.path === path)
  if (idx !== -1) {
    pData.base_project_files.splice(idx, 1)
  } else {
    const tokens = await getTokenCountForPath(pData.base_project_path, path)
    pData.base_project_files.push({ path, tokens, ignoreTokens: false })
  }
}

const baseTotalTokens = computed(() => {
  return pData.base_project_files.reduce((acc, f) => acc + (f.tokens || 0), 0)
})

// --- Step 1 Details ---
const browseBaseProject = async () => {
  const folder = await selectDirectory()
  if (folder) {
    pData.base_project_path = folder
    const existingData = await getBaseProjectData(folder)
    if (existingData && existingData.selected_files?.length) {
      pData.base_project_files = existingData.selected_files
    } else {
      pData.base_project_files = []
    }
  }
}

const browseParentFolder = async () => {
  const folder = await selectDirectory()
  if (folder) pData.parent_folder = folder
}

// --- Step 3 Concept ---
const generateConcept = async (e) => {
  const prompt = await generateConceptPrompt(pData, conceptQuestionsMap.value)
  await copyToClipboard(prompt, e)
}

const processConcept = async () => {
  const content = pData.concept_llm_response
  const parsed = await parseStarterSegments(content)
  if (!parsed || !Object.keys(parsed).length) {
    pData.concept_md = content
    pData.concept_llm_response = ''
    return
  }

  const friendly = {}
  for (const k in conceptQuestionsMap.value) friendly[k] = conceptQuestionsMap.value[k].label || k

  const mapped = await mapParsedSegmentsToKeys(parsed, friendly)
  pData.concept_segments = mapped
  pData.concept_signoffs = {}
  Object.keys(mapped).forEach(k => pData.concept_signoffs[k] = false)
  pData.concept_llm_response = ''
  activeSegmentKey.value = Object.keys(mapped)[0]
  reviewerEditMode.value = false
}

const mergeConcept = async () => {
  const friendly = {}
  for (const k in conceptQuestionsMap.value) friendly[k] = conceptQuestionsMap.value[k].label || k
  const md = await assembleStarterDocument(pData.concept_segments, CONCEPT_ORDER, friendly)
  pData.concept_md = md
  pData.concept_segments = {}
  pData.concept_signoffs = {}
  activeSegmentKey.value = null
}

// --- Step 4 Stack ---
const generateStack = async (e) => {
  const prompt = await generateStackPrompt(pData)
  await copyToClipboard(prompt, e)
}

const processStack = () => {
  const raw = pData.stack_llm_response
  try {
    const startIdx = raw.indexOf('[')
    const endIdx = raw.lastIndexOf(']')
    if (startIdx === -1 || endIdx === -1) throw new Error("No JSON")
    const jsonStr = raw.substring(startIdx, endIdx + 1).replace(/'/g, '"')
    const list = JSON.parse(jsonStr)
    pData.stack = list.join(', ')
    pData.stack_llm_response = ''
  } catch (err) {
    alert("Could not parse JSON list.")
  }
}

// --- Step 5 TODO ---
const generateTodo = async (e) => {
  const prompt = await generateTodoPrompt(pData, todoQuestionsMap.value)
  await copyToClipboard(prompt, e)
}

const processTodo = async () => {
  const content = pData.todo_llm_response
  const parsed = await parseStarterSegments(content)
  if (!parsed || !Object.keys(parsed).length) {
    pData.todo_md = content
    pData.todo_llm_response = ''
    return
  }

  const friendly = {}
  for (const k in todoQuestionsMap.value) friendly[k] = todoQuestionsMap.value[k].label || k

  const mapped = await mapParsedSegmentsToKeys(parsed, friendly)
  pData.todo_segments = mapped
  pData.todo_signoffs = {}
  Object.keys(pData.todo_segments).forEach(k => pData.todo_signoffs[k] = false)
  pData.todo_llm_response = ''

  const keys = Object.keys(mapped)
  if (keys.includes('deployment')) {
    keys.splice(keys.indexOf('deployment'), 1)
    keys.push('deployment')
  }
  activeSegmentKey.value = keys[0]
  reviewerEditMode.value = false
}

const mergeTodo = async () => {
  const friendly = {}
  for (const k in todoQuestionsMap.value) friendly[k] = todoQuestionsMap.value[k].label || k

  const keys = Object.keys(pData.todo_segments)
  if (keys.includes('deployment')) {
    keys.splice(keys.indexOf('deployment'), 1)
    keys.push('deployment')
  }

  const md = await assembleStarterDocument(pData.todo_segments, keys, friendly)
  pData.todo_md = md
  pData.todo_segments = {}
  pData.todo_signoffs = {}
  activeSegmentKey.value = null
}

// --- Step 6 Generate ---
const copyMasterPrompt = async (e) => {
  const prompt = await generateMasterPrompt(pData)
  await copyToClipboard(prompt, e)
}

const isGenerateReady = computed(() => {
  if (!pData.name || !pData.parent_folder || !pData.generate_llm_response) return false
  const content = pData.generate_llm_response
  if (!content.includes('--- File: ') || !content.includes('--- End of file ---')) return false
  if (!content.includes('<PITCH>') || !content.includes('</PITCH>')) return false
  return true
})

// --- Logic for Success ---
const successScreenData = ref(null)
const createProject = async () => {
  const pitchMatch = pData.generate_llm_response.match(/<PITCH>(.*?)<\/PITCH>/i)
  const pitch = pitchMatch ? pitchMatch[1].trim() : "a new project"
  let res = await createStarterProject(pData.generate_llm_response, pData.include_base_reference, pitch, pData)
  if (res.status === 'EXISTS' && confirm("Project folder already exists. Overwrite?")) {
    res = await createStarterProjectOverwrite(pData.generate_llm_response, pData.include_base_reference, pitch, pData)
  }
  if (res.status === 'SUCCESS') successScreenData.value = res
  else if (res.message) alert(res.message)
}

const copyToClipboard = async (text, buttonEvent) => {
  await navigator.clipboard.writeText(text)
  const target = buttonEvent.target
  const originalText = target.innerText
  target.innerText = "Copied!"
  setTimeout(() => { target.innerText = originalText }, 2000)
}

const renderSegmentTitle = (key, map) => {
  return map[key]?.label || map[key] || key
}

const toggleSignoff = (key, dataRef) => {
  dataRef[key] = !dataRef[key]
}

const handleSignoffAndNext = (key, signoffsRef, keysArray) => {
  signoffsRef[key] = true
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
}

const allSigned = (signoffs) => {
  return Object.values(signoffs).every(v => v === true)
}
</script>

<template>
  <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 font-sans">
    <div class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[92vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden text-gray-100">

      <template v-if="successScreenData">
        <div class="flex-grow flex flex-col items-center justify-center p-8 space-y-6">
          <h2 class="text-3xl font-bold text-white">Project Created Successfully!</h2>
          <div class="text-gray-400 text-lg">Your new project is located at:</div>
          <div class="bg-cm-input-bg border border-gray-600 text-gray-300 px-6 py-3 rounded font-mono text-lg w-full max-w-2xl text-center">{{ successScreenData.project_path }}</div>
          <button @click="loadProject(successScreenData.project_path); emit('close')" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-3 px-8 rounded shadow-md transition-colors mt-8 text-lg">Activate Project in CodeMerger</button>
        </div>
      </template>

      <template v-else>
        <!-- Header -->
        <div class="bg-cm-top-bar border-b border-gray-700 px-6 py-4 flex items-center justify-between shrink-0">
          <div class="flex items-center space-x-4">
            <Play class="w-6 h-6 text-cm-blue" />
            <h2 class="text-xl font-bold text-white">Project Starter <span v-if="pData.name" class="text-gray-500 font-medium">/ {{ pData.name }}</span></h2>
          </div>

          <div class="flex items-center space-x-3">
            <button @click="exportConfig" class="p-2 text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800" title="Export Configuration">
              <Download class="w-4 h-4"/>
            </button>
            <button @click="importConfig" class="p-2 text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800" title="Load Configuration">
              <Upload class="w-4 h-4"/>
            </button>
            <button @click="clearAll" class="p-2 text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800" title="Clear and restart">
              <Trash2 class="w-4 h-4"/>
            </button>
            <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors ml-4"><X class="w-6 h-6" /></button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex bg-gray-800 border-b border-gray-700 px-4 shrink-0 overflow-x-auto">
          <button
            v-for="(stepName, idx) in ['Details', 'Base Files', 'Concept', 'Stack', 'TODO', 'Generate']"
            :key="idx"
            @click="goToStep(idx+1)"
            class="px-5 py-3 text-sm font-medium transition-all border-b-2 whitespace-nowrap"
            :class="[
              currentStep === idx+1 ? 'border-cm-blue text-white bg-white/10' : 'border-transparent',
              (idx+1 <= maxAccessibleStep || idx+1 === 2) ? 'text-white font-bold hover:bg-white/5' : 'text-gray-500 cursor-not-allowed'
            ]"
            :disabled="idx+1 > maxAccessibleStep && idx+1 !== 2"
          >
            {{ idx+1 }}. {{ stepName }}
          </button>
        </div>

        <!-- Body -->
        <div class="flex-grow overflow-hidden flex flex-col p-8 bg-cm-dark-bg">

          <!-- STEP 1: Details -->
          <div v-if="currentStep === 1" class="max-w-3xl mx-auto space-y-8 w-full">
            <h3 class="text-2xl font-bold text-white">Project Details</h3>
            <div class="space-y-4">
              <p class="text-gray-400 text-lg">Enter the initial details for your new project.</p>
            </div>

            <div class="space-y-6">
              <div>
                <label class="block text-gray-200 font-bold mb-2 uppercase tracking-wider text-xs">Project Name</label>
                <input v-model="pData.name" type="text" class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 focus:border-cm-blue outline-none text-lg" placeholder="e.g. My Next Big Idea">
              </div>

              <div class="pt-6 border-t border-gray-700">
                <label class="block text-gray-200 font-bold mb-2 uppercase tracking-wider text-xs">Start from an existing project <span class="text-[#DE6808]">(OPTIONAL)</span></label>
                <div class="flex items-center space-x-4 mt-3">
                  <button @click="browseBaseProject" class="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded font-semibold transition-colors flex items-center shrink-0">
                    <FolderPlus class="w-5 h-5 mr-2" />
                    Select base project
                  </button>
                  <span class="text-gray-400 font-mono text-sm break-all">{{ pData.base_project_path || 'No base project selected' }}</span>
                </div>
              </div>

              <br>
              <div class="bg-cm-blue/10 border border-cm-blue/30 rounded p-4 text-sm text-blue-100 leading-relaxed italic shadow-inner">
                Tip: It is highly recommended to start a fresh chat with your LLM before pasting prompts from this starter.
              </div>
            </div>
          </div>

          <!-- STEP 2: Base Files -->
          <div v-if="currentStep === 2" class="flex flex-col h-full overflow-hidden">
            <div class="flex items-center justify-between mb-4 shrink-0">
              <div>
                <h3 class="text-2xl font-bold text-white">Select Base Files</h3>
                <p class="text-gray-400 text-sm">Choose files from <span class="text-cm-blue font-mono">{{ pData.base_project_path }}</span> as reference context.</p>
              </div>
              <div class="text-right">
                <div class="text-xs font-bold text-gray-500 uppercase">Starter Selection</div>
                <div class="text-cm-blue font-mono font-bold">{{ pData.base_project_files.length }} files / {{ baseTotalTokens.toLocaleString() }} tokens</div>
              </div>
            </div>

            <div class="flex-grow flex min-h-0 border border-gray-700 rounded overflow-hidden">
              <div class="w-1/2 flex flex-col bg-gray-900 border-r border-gray-700 p-4">
                <div class="relative mb-4">
                  <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input v-model="baseFilterText" @input="refreshBaseTree" type="text" placeholder="Filter base project..." class="w-full bg-cm-input-bg text-white pl-10 pr-4 py-2 rounded border border-gray-700 outline-none text-sm">
                </div>
                <div class="flex-grow overflow-y-auto custom-scrollbar">
                  <FileTreeNode
                    v-for="node in baseFileTree"
                    :key="node.path"
                    :node="node"
                    :selected-paths="pData.base_project_files.map(f => f.path)"
                    @toggle-select="toggleBaseFile"
                  />
                </div>
              </div>
              <div class="w-1/2 flex flex-col bg-cm-dark-bg p-4">
                <div class="flex items-center justify-between mb-4">
                  <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">Merge Order</span>
                </div>
                <div class="flex-grow overflow-y-auto custom-scrollbar space-y-1 pr-1">
                  <div v-for="(file, idx) in pData.base_project_files" :key="file.path" class="flex items-center justify-between bg-cm-input-bg p-2 rounded border border-gray-700 group transition-colors hover:border-gray-500">
                    <span class="text-sm text-gray-300 truncate pr-4">{{ file.path }}</span>
                    <button @click="pData.base_project_files.splice(idx, 1)" class="text-gray-500 hover:text-red-400 p-1 transition-colors"><X class="w-4 h-4"/></button>
                  </div>
                  <div v-if="!pData.base_project_files.length" class="h-full flex items-center justify-center text-gray-600 italic">No files selected.</div>
                </div>
              </div>
            </div>
          </div>

          <!-- STEP 3: Concept -->
          <div v-if="currentStep === 3" class="h-full flex flex-col">
             <template v-if="pData.concept_md">
               <div class="flex items-center justify-between mb-4">
                 <h3 class="text-2xl font-bold text-white">Review Concept</h3>
                 <button @click="reviewerEditMode = !reviewerEditMode" class="bg-cm-blue text-white px-4 py-1.5 rounded font-bold text-sm">{{ reviewerEditMode ? 'Finish Editing' : 'Edit Markdown' }}</button>
               </div>
               <div class="flex-grow bg-cm-input-bg border border-gray-700 rounded overflow-hidden">
                 <textarea v-if="reviewerEditMode" v-model="pData.concept_md" class="w-full h-full p-6 bg-cm-input-bg text-gray-100 font-mono outline-none"></textarea>
                 <div v-else class="w-full h-full p-6 overflow-y-auto custom-scrollbar"><MarkdownRenderer :content="pData.concept_md" /></div>
               </div>
             </template>
             <template v-else-if="Object.keys(pData.concept_segments).length">
                <div class="flex h-full min-h-0">
                  <div class="w-64 border-r border-gray-700 pr-4 overflow-y-auto space-y-2">
                    <div v-for="key in Object.keys(pData.concept_segments)" :key="key" @click="activeSegmentKey = key; reviewerEditMode = false" class="p-3 rounded cursor-pointer border transition-all" :class="activeSegmentKey === key ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'">
                      {{ renderSegmentTitle(key, conceptQuestionsMap) }}
                    </div>
                  </div>
                  <div class="flex-grow pl-6 flex flex-col">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-xl font-bold text-white">{{ renderSegmentTitle(activeSegmentKey, conceptQuestionsMap) }}</h3>
                        <button @click="reviewerEditMode = !reviewerEditMode" class="bg-gray-700 text-white px-3 py-1 rounded text-xs">{{ reviewerEditMode ? 'Render' : 'Edit' }}</button>
                    </div>
                    <div class="flex-grow border border-gray-700 rounded bg-cm-input-bg overflow-hidden">
                        <textarea v-if="reviewerEditMode" v-model="pData.concept_segments[activeSegmentKey]" class="w-full h-full bg-cm-input-bg text-white p-6 outline-none custom-scrollbar font-sans text-sm leading-relaxed"></textarea>
                        <div v-else class="w-full h-full overflow-y-auto p-6 custom-scrollbar"><MarkdownRenderer :content="pData.concept_segments[activeSegmentKey]" /></div>
                    </div>
                    <div class="shrink-0 pt-4 flex justify-between">
                        <button @click="toggleSignoff(activeSegmentKey, pData.concept_signoffs)" class="flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors">
                            <CheckCircle class="w-5 h-5" :class="pData.concept_signoffs[activeSegmentKey] ? 'text-cm-green' : 'text-gray-600'"/>
                            <span>{{ pData.concept_signoffs[activeSegmentKey] ? 'Locked' : 'Lock for Merge' }}</span>
                        </button>
                        <button v-if="allSigned(pData.concept_signoffs)" @click="mergeConcept" class="bg-cm-green text-white px-8 py-2 rounded font-bold shadow">Merge & Finalize</button>
                        <button v-else @click="handleSignoffAndNext(activeSegmentKey, pData.concept_signoffs, Object.keys(pData.concept_segments))" class="bg-cm-blue text-white px-8 py-2 rounded font-bold shadow">Lock & Next</button>
                    </div>
                  </div>
                </div>
             </template>
             <template v-else>
               <div class="max-w-3xl mx-auto w-full space-y-6">
                 <h3 class="text-2xl font-bold text-white">Project Concept</h3>
                 <p class="text-gray-400">Describe what you want to build in a few sentences. The LLM will use this to generate the core sections.</p>
                 <textarea v-model="pData.goal" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue" placeholder="e.g. A desktop tool that bundles project code..."></textarea>
                 <div class="bg-gray-800 p-6 rounded border border-gray-700 space-y-4">
                   <button @click="generateConcept" class="w-full bg-cm-blue text-white font-bold py-3 rounded">1. Copy Prompt for LLM</button>
                   <textarea v-model="pData.concept_llm_response" class="w-full h-40 bg-cm-input-bg border border-gray-700 text-white rounded p-4 outline-none focus:border-cm-blue" placeholder="Paste LLM response here..."></textarea>
                   <button @click="processConcept" :disabled="!pData.concept_llm_response" class="w-full bg-cm-green text-white font-bold py-3 rounded disabled:opacity-50">2. Process & Review</button>
                 </div>
               </div>
             </template>
          </div>

          <!-- STEP 4: Stack -->
          <div v-if="currentStep === 4" class="max-w-3xl mx-auto space-y-6 w-full text-gray-100">
             <h3 class="text-2xl font-bold text-white">Tech Stack</h3>
             <textarea v-model="pData.stack_experience" class="w-full h-24 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar" placeholder="List your known languages, frameworks, and environment details..."></textarea>

             <div class="flex justify-between items-center bg-gray-800 p-4 rounded border border-gray-700 mt-4">
                <div class="text-gray-300"><span class="font-bold text-white">1.</span> Copy prompt for LLM</div>
                <button @click="generateStack" class="bg-cm-blue hover:bg-blue-500 text-white px-4 py-2 rounded shadow transition-colors font-bold">Copy Stack Prompt</button>
             </div>

             <div class="bg-gray-800 p-4 rounded border border-gray-700">
                <div class="text-gray-300 mb-2"><span class="font-bold text-white">2.</span> Paste LLM Response or Type Stack</div>
                <textarea v-model="pData.stack_llm_response" class="w-full h-24 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar" placeholder='["Vue", "Python"]'></textarea>
                <div class="flex justify-end mt-3">
                  <button @click="processStack" :disabled="!pData.stack_llm_response" class="bg-cm-green hover:bg-green-600 text-white px-6 py-2 rounded shadow transition-colors disabled:opacity-50 font-bold">Process List</button>
                </div>
             </div>

             <div v-if="pData.stack" class="mt-8 p-4 border border-cm-blue rounded bg-cm-blue/10">
                <div class="font-bold text-white mb-2">Final Selected Stack:</div>
                <div class="text-cm-blue font-mono">{{ pData.stack }}</div>
             </div>
          </div>

          <!-- STEP 5: TODO -->
          <div v-if="currentStep === 5" class="h-full flex flex-col">
            <template v-if="pData.todo_md">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-2xl font-bold text-white">Review TODO Plan</h3>
                <button @click="reviewerEditMode = !reviewerEditMode" class="bg-cm-blue text-white px-4 py-1.5 rounded font-bold text-sm">{{ reviewerEditMode ? 'Finish Editing' : 'Edit Markdown' }}</button>
              </div>
              <div class="flex-grow bg-cm-input-bg border border-gray-700 rounded overflow-hidden text-gray-100">
                <textarea v-if="reviewerEditMode" v-model="pData.todo_md" class="w-full h-full p-6 bg-cm-input-bg text-gray-100 font-mono outline-none"></textarea>
                <div v-else class="w-full h-full p-6 overflow-y-auto custom-scrollbar"><MarkdownRenderer :content="pData.todo_md" /></div>
              </div>
            </template>

            <template v-else-if="Object.keys(pData.todo_segments).length">
               <div class="flex h-full min-h-0 text-gray-100">
                  <div class="w-64 border-r border-gray-700 pr-4 overflow-y-auto space-y-2">
                    <div v-for="key in Object.keys(pData.todo_segments)" :key="key" @click="activeSegmentKey = key; reviewerEditMode = false" class="p-3 rounded cursor-pointer border transition-all" :class="activeSegmentKey === key ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'">
                      {{ TODO_PHASES[key] || key }}
                    </div>
                  </div>
                  <div class="flex-grow pl-6 flex flex-col min-w-0">
                    <div class="flex justify-between items-center mb-4 shrink-0">
                        <h3 class="text-xl font-bold text-white">{{ TODO_PHASES[activeSegmentKey] || activeSegmentKey }}</h3>
                        <button @click="reviewerEditMode = !reviewerEditMode" class="bg-gray-700 text-white px-3 py-1 rounded text-xs">{{ reviewerEditMode ? 'Render' : 'Edit' }}</button>
                    </div>
                    <div class="flex-grow border border-gray-700 rounded bg-cm-input-bg overflow-hidden">
                        <textarea v-if="reviewerEditMode" v-model="pData.todo_segments[activeSegmentKey]" class="w-full h-full bg-cm-input-bg text-white p-6 outline-none custom-scrollbar font-sans text-sm leading-relaxed"></textarea>
                        <div v-else class="w-full h-full overflow-y-auto p-6 custom-scrollbar"><MarkdownRenderer :content="pData.todo_segments[activeSegmentKey]" /></div>
                    </div>
                    <div class="shrink-0 pt-4 flex justify-between">
                        <button @click="toggleSignoff(activeSegmentKey, pData.todo_signoffs)" class="flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors">
                            <CheckCircle class="w-5 h-5" :class="pData.todo_signoffs[activeSegmentKey] ? 'text-cm-green' : 'text-gray-600'"/>
                            <span>{{ pData.todo_signoffs[activeSegmentKey] ? 'Locked' : 'Lock for Merge' }}</span>
                        </button>
                        <button v-if="allSigned(pData.todo_signoffs)" @click="mergeTodo" class="bg-cm-green text-white px-8 py-2 rounded font-bold shadow">Merge & Finalize</button>
                        <button v-else @click="handleSignoffAndNext(activeSegmentKey, pData.todo_signoffs, Object.keys(pData.todo_segments))" class="bg-cm-blue text-white px-8 py-2 rounded font-bold shadow">Lock & Next</button>
                    </div>
                  </div>
                </div>
            </template>

            <template v-else>
              <div class="max-w-3xl mx-auto space-y-6 w-full text-gray-100">
                <h3 class="text-2xl font-bold text-white">Generate TODO Plan</h3>

                <div class="flex justify-between items-center bg-gray-800 p-4 rounded border border-gray-700 mt-4">
                  <div class="text-gray-300"><span class="font-bold text-white">1.</span> Copy prompt for LLM</div>
                  <button @click="generateTodo" class="bg-cm-blue hover:bg-blue-500 text-white px-4 py-2 rounded shadow transition-colors font-bold">Copy TODO Prompt</button>
                </div>

                <div class="bg-gray-800 p-4 rounded border border-gray-700">
                  <div class="text-gray-300 mb-2"><span class="font-bold text-white">2.</span> Paste LLM Response (with tags)</div>
                  <textarea v-model="pData.todo_llm_response" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar" placeholder="Paste response here..."></textarea>
                  <div class="flex justify-end mt-3">
                    <button @click="processTodo" :disabled="!pData.todo_llm_response" class="bg-cm-green hover:bg-green-600 text-white px-6 py-2 rounded shadow transition-colors disabled:opacity-50 font-bold">Process & Review</button>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <!-- STEP 6: Generate -->
          <div v-if="currentStep === 6" class="max-w-3xl mx-auto w-full space-y-8 text-gray-100 pb-8">
            <h3 class="text-2xl font-bold text-white">Finalize & Generate</h3>
            <div class="bg-gray-800 p-8 rounded border border-gray-700 space-y-6">
              <div class="space-y-3">
                <label class="block text-gray-300 font-bold text-sm uppercase">1. Destination Folder</label>
                <div class="flex space-x-3">
                  <input v-model="pData.parent_folder" type="text" class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-2 text-sm outline-none focus:border-cm-blue">
                  <button @click="browseParentFolder" class="bg-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-600 font-bold">Browse</button>
                </div>
                <div v-if="pData.name && pData.parent_folder" class="text-cm-blue text-xs font-mono">Full path: {{ pData.parent_folder }}\{{ pData.name.replace(/\s+/g, '-') }}</div>
              </div>
              <div class="pt-6 border-t border-gray-700 flex flex-col space-y-4">
                <label class="block text-gray-300 font-bold text-sm uppercase">2. Creation Prompt</label>
                <button @click="copyMasterPrompt" class="bg-cm-blue text-white font-bold py-4 rounded text-lg shadow-lg hover:bg-blue-500 transition-colors">Copy Final Creation Prompt</button>
                <textarea v-model="pData.generate_llm_response" class="w-full h-48 bg-cm-input-bg border border-gray-700 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar" placeholder="Paste generated code blocks here..."></textarea>
              </div>
            </div>
            <div class="flex justify-end mt-4">
              <button @click="createProject" :disabled="!isGenerateReady" class="bg-cm-green hover:bg-green-600 disabled:bg-gray-700 disabled:opacity-50 text-white font-bold px-12 py-4 rounded-lg shadow-xl text-xl flex items-center transition-all">
                <Upload class="w-6 h-6 mr-3" />
                Create Project Files
              </button>
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="bg-cm-top-bar border-t border-gray-700 px-6 py-4 flex items-center justify-between shrink-0">
          <button v-if="currentStep > 1" @click="prevStep" class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-8 rounded transition-colors text-sm">&lt; Back</button>
          <div v-else></div>
          <button
            v-if="currentStep < 6"
            @click="nextStep"
            class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-2 px-10 rounded shadow-md transition-all text-sm disabled:opacity-40 disabled:cursor-not-allowed"
            :disabled="currentStep > maxAccessibleStep && currentStep !== 2"
          >
            Next &gt;
          </button>
        </div>
      </template>

    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.custom-scrollbar::-webkit-scrollbar { width: 8px; height: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #555; }
</style>