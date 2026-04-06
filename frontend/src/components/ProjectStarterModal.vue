<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { Play, Save, Upload, Trash2, X } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'

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
const successScreenData = ref(null)

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

  isLoading.value = false
})

watch(() => pData, () => {
  recalcProgress()
  saveState()
}, { deep: true })

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

const onProjectCreated = (res) => {
  successScreenData.value = res
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
</script>

<template>
  <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 font-sans">
    <div class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[92vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden text-gray-100">

      <StepSuccess v-if="successScreenData" :successScreenData="successScreenData" @close="emit('close')" />

      <template v-else>
        <!-- Header -->
        <div class="bg-cm-top-bar border-b border-gray-700 px-6 py-4 flex items-center justify-between shrink-0">
          <div class="flex items-center space-x-4">
            <Play class="w-6 h-6 text-cm-blue" />
            <h2 class="text-xl font-bold text-white">Project Starter <span v-if="pData.name" class="text-gray-500 font-medium">/ {{ pData.name }}</span></h2>
          </div>

          <div class="flex items-center space-x-3">
            <button @click="exportConfig" class="p-2 text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800" title="Save Configuration">
              <Save class="w-4 h-4"/>
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
          <Step1Details v-if="currentStep === 1" :pData="pData" />
          <Step2BaseFiles v-if="currentStep === 2" :pData="pData" />
          <Step3Concept v-if="currentStep === 3" :pData="pData" :conceptQuestionsMap="conceptQuestionsMap" />
          <Step4Stack v-if="currentStep === 4" :pData="pData" />
          <Step5Todo v-if="currentStep === 5" :pData="pData" :todoQuestionsMap="todoQuestionsMap" />
          <Step6Generate v-if="currentStep === 6" :pData="pData" @projectCreated="onProjectCreated" />
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