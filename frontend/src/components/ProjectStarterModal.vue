<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { Leaf, Save, Upload, Trash2, LogOut } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { useEscapeKey } from '../composables/useEscapeKey'

import Step1Details from './starter-steps/Step1Details.vue'
import Step2BaseFiles from './starter-steps/Step2BaseFiles.vue'
import Step3Concept from './starter-steps/Step3Concept.vue'
import Step4Stack from './starter-steps/Step4Stack.vue'
import Step5Todo from './starter-steps/Step5Todo.vue'
import Step6Generate from './starter-steps/Step6Generate.vue'
import StepSuccess from './starter-steps/StepSuccess.vue'

const emit = defineEmits(['close'])
const {
  config,
  resizeWindow,
  getStarterSession,
  saveStarterSession,
  clearStarterSession,
  exportStarterConfig,
  loadStarterConfig,
  getConceptQuestions,
  getTodoQuestions
} = useAppState()

const currentStep = ref(1)
const maxAccessibleStep = ref(1)
const isLoading = ref(true)
const isResetting = ref(false)

const toastMessage = ref('')
const showToast = ref(false)
let toastTimer = null

const pData = reactive({
  name: '',
  parent_folder: '',
  stack: [],
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
  concept_baselines: {},
  todo_phases: [],
  todo_segments: {},
  todo_signoffs: {},
  todo_baselines: {}
})

const conceptQuestionsMap = ref({})
const todoQuestionsMap = ref({})
const successScreenData = ref(null)

const stepNames = {
  1: 'Details',
  2: 'Base Files',
  3: 'Concept',
  4: 'Stack',
  5: 'TODO',
  6: 'Generate'
}

const handleClose = async (wasCreated = false) => {
  if (window.pywebview) {
    await window.pywebview.api.on_starter_close(wasCreated)
  }
  emit('close')
}

useEscapeKey(() => handleClose())

onMounted(async () => {
  await resizeWindow(1100, 850)

  // Requirement: Deactivate current model and disable compact mode
  if (window.pywebview) {
    await window.pywebview.api.on_starter_open()
  }

  conceptQuestionsMap.value = await getConceptQuestions()
  todoQuestionsMap.value = await getTodoQuestions()

  const saved = await getStarterSession()
  if (saved && Object.keys(saved).length > 0) {
    // Migration logic for stack string to array of objects
    if (typeof saved.stack === 'string' && saved.stack.trim()) {
      saved.stack = saved.stack.split('\n').filter(s => s.trim()).map(s => ({ tech: s, rationale: 'Imported from previous version' }))
    } else if (!saved.stack) {
      saved.stack = []
    }

    Object.assign(pData, saved)
    recalcProgress()
    currentStep.value = maxAccessibleStep.value
  } else {
    pData.parent_folder = config.value?.default_parent_folder || ''
    pData.stack_experience = config.value?.user_experience || ''
  }

  isLoading.value = false
})

onUnmounted(() => {
  // Automatic acceptance of all pending diffs on exit
  pData.concept_baselines = {}
  pData.todo_baselines = {}
})

watch(() => pData, () => {
  if (isResetting.value) return
  recalcProgress()
  saveState()
}, { deep: true })

const recalcProgress = () => {
  const hasDetails = !!pData.name
  const hasConcept = (!Object.keys(pData.concept_segments).length) && !!pData.concept_md
  const hasStack = pData.stack && pData.stack.length > 0
  const hasTodo = (!Object.keys(pData.todo_segments).length) && !!pData.todo_md

  let targetMax = 1
  if (hasDetails) {
    targetMax = 3 // Move to Concept
    if (hasConcept) {
      targetMax = 4 // Move to Stack
      if (hasStack) {
        targetMax = 5 // Move to TODO
        if (hasTodo) {
          targetMax = 6 // Move to Generate
        }
      }
    }
  }

  if (targetMax > maxAccessibleStep.value) {
      maxAccessibleStep.value = targetMax
  }
}

const saveState = async () => {
  if (isLoading.value || isResetting.value) return
  await saveStarterSession({ current_step: currentStep.value, ...pData })
}

const showToastNotification = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const exportConfig = async () => {
  const exportData = { current_step: currentStep.value, ...pData }
  const success = await exportStarterConfig(exportData)
  if (success) {
    showToastNotification("Config saved successfully.")
  }
}

const importConfig = async () => {
  const loadedData = await loadStarterConfig()
  if (loadedData) {
    Object.assign(pData, loadedData)
    recalcProgress()
    currentStep.value = maxAccessibleStep.value
    saveState()
    showToastNotification("Config loaded successfully.")
  }
}

// Resets all reactive data and deletes the session file from disk
const performReset = async () => {
  isResetting.value = true

  await clearStarterSession()

  pData.name = ''
  pData.parent_folder = config.value?.default_parent_folder || ''
  pData.stack = []
  pData.stack_experience = config.value?.user_experience || ''
  pData.goal = ''
  pData.concept_md = ''
  pData.todo_md = ''
  pData.base_project_path = ''
  pData.base_project_files = []
  pData.include_base_reference = true

  pData.concept_llm_response = ''
  pData.stack_llm_response = ''
  pData.todo_llm_response = ''
  pData.generate_llm_response = ''

  pData.concept_segments = {}
  pData.concept_signoffs = {}
  pData.concept_baselines = {}
  pData.todo_phases = []
  pData.todo_segments = {}
  pData.todo_signoffs = {}
  pData.todo_baselines = {}

  currentStep.value = 1
  maxAccessibleStep.value = 1

  isResetting.value = false
}

const clearAll = async () => {
  if (confirm("Are you sure you want to clear all project data and start fresh?")) {
    await performReset()
  }
}

const onProjectCreated = async (res) => {
  await performReset()
  // Call API to signify project was created (Requirement: don't restore previous)
  if (window.pywebview) {
    await window.pywebview.api.on_starter_close(true)
  }
  successScreenData.value = res
}

// --- Navigation ---
const activeStepsList = computed(() => {
  const steps = [1]
  if (pData.base_project_path) steps.push(2)
  steps.push(3, 4, 5, 6)
  return steps
})

const isLookingBack = computed(() => currentStep.value < maxAccessibleStep.value)

const isNextDisabled = computed(() => {
  // Step 1: Name is mandatory
  if (currentStep.value === 1) {
    return !pData.name.trim()
  }

  // Step 3 (Concept): Can only proceed if document is merged and segments are cleared
  if (currentStep.value === 3) {
    const hasMergedDoc = !!pData.concept_md.trim()
    const hasActiveSegments = Object.keys(pData.concept_segments).length > 0
    return !hasMergedDoc || hasActiveSegments
  }

  // Step 5 (TODO): Can only proceed if plan is merged and segments are cleared
  if (currentStep.value === 5) {
    const hasMergedDoc = !!pData.todo_md.trim()
    const hasActiveSegments = Object.keys(pData.todo_segments).length > 0
    return !hasMergedDoc || hasActiveSegments
  }

  return false
})

const isStarterEmpty = computed(() => {
  return !pData.name.trim() &&
         !pData.goal.trim() &&
         !pData.base_project_path &&
         !pData.concept_md &&
         !pData.todo_md &&
         !pData.concept_llm_response &&
         !pData.stack_llm_response &&
         !pData.todo_llm_response &&
         !pData.generate_llm_response
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
  if (idx < activeStepsList.value.length - 1) {
    const targetStep = activeStepsList.value[idx + 1]

    if (currentStep.value === 3) {
      if (Object.keys(pData.concept_segments).length > 0) {
        alert("You must merge the concept segments into a final document before proceeding.")
        return
      }
      if (!pData.concept_md) {
        alert("The concept document cannot be empty.")
        return
      }
    }
    if (currentStep.value === 5) {
      if (Object.keys(pData.todo_segments).length > 0) {
        alert("You must merge the TODO plan into a final document before proceeding.")
        return
      }
      if (!pData.todo_md) {
        alert("The TODO plan cannot be empty.")
        return
      }
    }

    if (targetStep > maxAccessibleStep.value) {
      maxAccessibleStep.value = targetStep
    }

    goToStep(targetStep)
  }
}
</script>

<template>
  <div id="project-starter-modal" class="absolute inset-0 bg-cm-dark-bg z-50 flex flex-col overflow-hidden text-gray-100 font-sans">

    <StepSuccess v-if="successScreenData" :successScreenData="successScreenData" @close="emit('close')" />

    <template v-else>
      <!-- Header -->
      <div id="starter-header" class="bg-cm-top-bar border-b border-gray-700 px-6 py-4 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-4">
          <Leaf class="w-6 h-6 text-cm-blue" />
          <h2 class="text-xl font-bold text-white">Project Starter <span v-if="pData.name" class="text-gray-500 font-medium">/ {{ pData.name }}</span></h2>
        </div>

        <div class="flex items-center space-x-2">
          <span
            class="text-cm-green text-sm font-bold transition-opacity duration-500 mr-2"
            :class="showToast ? 'opacity-100' : 'opacity-0 pointer-events-none'"
          >
            {{ toastMessage }}
          </span>

          <template v-if="!isStarterEmpty">
            <button id="btn-starter-export" @click="exportConfig" v-info="'starter_header_save'" class="px-3 py-1.5 text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800 flex items-center font-bold shadow-sm" title="Export configuration to JSON file">
              <Save class="w-4 h-4 mr-0 lg:mr-2"/>
              <span class="hidden lg:inline text-xs">Export</span>
            </button>
            <button id="btn-starter-import" @click="importConfig" v-info="'starter_header_load'" class="px-3 py-1.5 text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800 flex items-center font-bold shadow-sm" title="Restore project configuration from JSON">
              <Upload class="w-4 h-4 mr-0 lg:mr-2"/>
              <span class="hidden lg:inline text-xs">Import</span>
            </button>
            <button id="btn-starter-reset" @click="clearAll" v-info="'starter_header_clear'" class="px-3 py-1.5 text-gray-400 hover:text-red-400 transition-colors border border-gray-600 rounded bg-gray-800 flex items-center font-bold shadow-sm" title="Wipe all progress and start fresh">
              <Trash2 class="w-4 h-4 mr-0 lg:mr-2"/>
              <span class="hidden lg:inline text-xs">Reset</span>
            </button>

            <div class="w-px h-6 bg-gray-600 mx-1"></div>
          </template>

          <button id="btn-starter-exit" @click="handleClose(false)" v-info="'starter_header_exit'" class="flex items-center text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800 hover:bg-gray-700 px-3 py-1.5 shadow-sm" :title="isStarterEmpty ? 'Exit' : 'Save and Exit'">
            <LogOut class="w-4 h-4 mr-2" />
            <span class="text-xs font-bold">{{ isStarterEmpty ? 'Exit' : 'Save and Exit' }}</span>
          </button>
        </div>
      </div>

      <!-- Tabs (Left aligned) -->
      <div id="starter-tabs" class="flex bg-gray-800 border-b border-gray-700 px-4 shrink-0 overflow-x-auto justify-start">
        <button
          v-for="(stepId, index) in activeStepsList"
          :key="stepId"
          @click="goToStep(stepId)"
          class="px-5 py-3 text-sm font-medium transition-all border-b-2 whitespace-nowrap"
          :class="[
            currentStep === stepId ? 'border-cm-blue text-white bg-white/10' : 'border-transparent',
            (stepId <= maxAccessibleStep || stepId === 2) ? 'text-white font-bold hover:bg-white/5' : 'text-gray-500 cursor-not-allowed'
          ]"
          :disabled="stepId > maxAccessibleStep && stepId !== 2"
          :title="`Jump to ${stepNames[stepId]} step`"
        >
          {{ index + 1 }}. {{ stepNames[stepId] }}
        </button>
      </div>

      <!-- Body: Full scrollable region for all content below the tabs -->
      <div id="starter-step-container" class="flex-grow overflow-y-auto custom-scrollbar bg-cm-dark-bg flex flex-col items-center h-0 min-h-0">
        <div class="w-full max-w-6xl flex-grow flex flex-col p-8 min-h-0">
          <Step1Details v-if="currentStep === 1" :pData="pData" :isLookingBack="isLookingBack" @next="nextStep" />
          <Step2BaseFiles v-if="currentStep === 2" :pData="pData" :isLookingBack="isLookingBack" />
          <Step3Concept v-if="currentStep === 3" :pData="pData" :isLookingBack="isLookingBack" :conceptQuestionsMap="conceptQuestionsMap" @next="nextStep" />
          <Step4Stack v-if="currentStep === 4" :pData="pData" :isLookingBack="isLookingBack" @next="nextStep" />
          <Step5Todo v-if="currentStep === 5" :pData="pData" :isLookingBack="isLookingBack" :todoQuestionsMap="todoQuestionsMap" @next="nextStep" />
          <Step6Generate v-if="currentStep === 6" :pData="pData" @projectCreated="onProjectCreated" />
        </div>
      </div>
    </template>

    <!-- Navigation Bar at Bottom -->
    <div v-if="!successScreenData" id="starter-footer" class="bg-cm-top-bar border-t border-gray-700 px-6 py-4 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-3">
             <button
                id="btn-starter-prev"
                v-if="currentStep > 1"
                @click="prevStep"
                v-info="'starter_nav_prev'"
                class="bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded font-bold transition-all flex items-center"
                title="Return to the previous phase"
             >
                &lt; Previous Step
             </button>
        </div>

        <div class="flex items-center space-x-3">
             <button
                id="btn-starter-next"
                v-if="activeStepsList.indexOf(currentStep) < activeStepsList.length - 1"
                @click="nextStep"
                :disabled="isNextDisabled"
                v-info="'starter_nav_next'"
                class="bg-cm-blue hover:bg-blue-500 disabled:bg-gray-700 disabled:opacity-50 text-white px-10 py-2 rounded font-bold shadow-lg transition-all flex items-center"
                title="Proceed to the next phase"
             >
                {{ currentStep === 4 && (!Array.isArray(pData.stack) ? !pData.stack.trim() : !pData.stack.length) ? 'Skip Stack' : 'Next Step >' }}
             </button>
        </div>
    </div>

  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>