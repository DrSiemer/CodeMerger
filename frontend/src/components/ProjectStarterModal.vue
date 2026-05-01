<script setup>
import { onMounted, onUnmounted, ref, watch, computed } from 'vue'
import { Leaf, Save, Upload, Trash2, LogOut } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { useEscapeKey } from '../composables/useEscapeKey'
import { useStarterState } from '../composables/starter/useStarterState'
import { useStarterNavigation } from '../composables/starter/useStarterNavigation'
import { WINDOW_SIZES } from '../utils/constants'

import StarterDetails from './starter-steps/StarterDetails.vue'
import StarterBaseFiles from './starter-steps/StarterBaseFiles.vue'
import StarterConcept from './starter-steps/StarterConcept.vue'
import StarterStack from './starter-steps/StarterStack.vue'
import StarterDesign from './starter-steps/StarterDesign.vue'
import StarterTodo from './starter-steps/StarterTodo.vue'
import StarterGenerate from './starter-steps/StarterGenerate.vue'
import StepSuccess from './starter-steps/StepSuccess.vue'

const emit = defineEmits(['close'])
const { showStarterModal, resizeWindow } = useAppState()

const {
  pData, isLoading, isResetting, toastMessage, showToast,
  conceptQuestionsMap, designQuestionsMap, todoQuestionsMap,
  loadSession, saveState, performReset, handleExport, handleImport
} = useStarterState()

const {
  currentStep, maxAccessibleStep, stepNames, activeStepsList,
  isLookingBack, isNextDisabled, recalcProgress, goToStep, prevStep, nextStep
} = useStarterNavigation(pData)

const successScreenData = ref(null)

const handleClose = async (wasCreated = false) => {
  if (window.pywebview) await window.pywebview.api.on_starter_close(wasCreated)
  showStarterModal.value = false
}

useEscapeKey(() => handleClose())

onMounted(async () => {
  await resizeWindow(WINDOW_SIZES.PROJECT_STARTER.width, WINDOW_SIZES.PROJECT_STARTER.height)
  if (window.pywebview) await window.pywebview.api.on_starter_open()

  const startStep = await loadSession()
  recalcProgress()
  currentStep.value = maxAccessibleStep.value || startStep
})

onUnmounted(() => {
  pData.concept_baselines = {}; pData.design_baselines = {}; pData.todo_baselines = {}
})

watch(pData, () => {
  if (isResetting.value) return
  recalcProgress()
  saveState(currentStep.value)
}, { deep: true })

const onProjectCreated = async (res) => {
  await performReset()
  if (window.pywebview) await window.pywebview.api.on_starter_close(true)
  successScreenData.value = res
}

const clearAll = async () => {
  if (confirm("Are you sure you want to clear all project data and start fresh?")) {
    await performReset()
    currentStep.value = 1
    maxAccessibleStep.value = 1
  }
}

const isStarterEmpty = computed(() => {
  return !pData.name.trim() && !pData.goal.trim() && !pData.base_project_path && !pData.concept_md && !pData.design_md && !pData.todo_md && !pData.concept_llm_response && !pData.stack_llm_response && !pData.design_llm_response && !pData.todo_llm_response && !pData.generate_llm_response
})

const triggerImport = async () => {
  const step = await handleImport()
  if (step) {
    recalcProgress()
    currentStep.value = maxAccessibleStep.value
    saveState(currentStep.value)
  }
}
</script>

<template>
  <div id="project-starter-modal" class="absolute inset-0 bg-cm-dark-bg z-50 flex flex-col overflow-hidden text-gray-100 font-sans">
    <StepSuccess v-if="successScreenData" :successScreenData="successScreenData" @close="emit('close')" />

    <div v-else class="flex-grow flex flex-col min-h-0">
      <div id="starter-header" class="bg-cm-top-bar border-b border-gray-700 px-6 py-4 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-4">
          <Leaf class="w-6 h-6 text-cm-blue" />
          <h2 class="text-xl font-bold text-white">Project Starter <span v-if="pData.name" class="text-gray-500 font-medium">/ {{ pData.name }}</span></h2>
        </div>

        <div class="flex items-center space-x-2">
          <span class="text-cm-green text-sm font-bold transition-opacity duration-500 mr-2" :class="showToast ? 'opacity-100' : 'opacity-0 pointer-events-none'">{{ toastMessage }}</span>
          <button @click="triggerImport" v-info="'starter_header_load'" class="px-3 py-1.5 text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800 flex items-center font-bold shadow-sm">
            <Upload class="w-4 h-4 mr-0 lg:mr-2"/><span class="hidden lg:inline text-xs">Import</span>
          </button>
          <template v-if="!isStarterEmpty">
            <button @click="handleExport(currentStep)" v-info="'starter_header_save'" class="px-3 py-1.5 text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800 flex items-center font-bold shadow-sm">
              <Save class="w-4 h-4 mr-0 lg:mr-2"/><span class="hidden lg:inline text-xs">Export</span>
            </button>
            <button @click="clearAll" v-info="'starter_header_clear'" class="px-3 py-1.5 text-gray-400 hover:text-red-400 transition-colors border border-gray-600 rounded bg-gray-800 flex items-center font-bold shadow-sm">
              <Trash2 class="w-4 h-4 mr-0 lg:mr-2"/><span class="hidden lg:inline text-xs">Reset</span>
            </button>
            <div class="w-px h-6 bg-gray-600 mx-1"></div>
          </template>
          <button @click="handleClose(false)" v-info="'starter_header_exit'" class="flex items-center text-gray-400 hover:text-white transition-colors border border-gray-600 rounded bg-gray-800 hover:bg-gray-700 px-3 py-1.5 shadow-sm">
            <LogOut class="w-4 h-4 mr-2" /><span class="text-xs font-bold">{{ isStarterEmpty ? 'Exit' : 'Save and Exit' }}</span>
          </button>
        </div>
      </div>

      <div id="starter-tabs" class="flex bg-gray-800 border-b border-gray-700 px-4 shrink-0 overflow-x-auto justify-start">
        <button v-for="(stepId, index) in activeStepsList" :key="stepId" @click="goToStep(stepId)" class="px-5 py-3 text-sm font-medium transition-all border-b-2 whitespace-nowrap" :class="[currentStep === stepId ? 'border-cm-blue text-white bg-white/10' : 'border-transparent', (stepId <= maxAccessibleStep || stepId === 2) ? 'text-white font-bold hover:bg-white/5' : 'text-gray-500 cursor-not-allowed']" :disabled="stepId > maxAccessibleStep && stepId !== 2">
          {{ index + 1 }}. {{ stepNames[stepId] }}
        </button>
      </div>

      <div id="starter-step-container" class="flex-grow overflow-y-auto custom-scrollbar bg-cm-dark-bg flex flex-col items-center h-0 min-h-0">
        <div class="w-full max-w-6xl flex-grow flex flex-col p-8 min-h-0">
          <StarterDetails v-if="currentStep === 1" :pData="pData" :isLookingBack="isLookingBack" @next="nextStep" />
          <StarterBaseFiles v-if="currentStep === 2" :pData="pData" :isLookingBack="isLookingBack" />
          <StarterConcept v-if="currentStep === 3" :pData="pData" :isLookingBack="isLookingBack" :conceptQuestionsMap="conceptQuestionsMap" @next="nextStep" />
          <StarterStack v-if="currentStep === 4" :pData="pData" :isLookingBack="isLookingBack" @next="nextStep" />
          <StarterDesign v-if="currentStep === 5" :pData="pData" :isLookingBack="isLookingBack" :designQuestionsMap="designQuestionsMap" @next="nextStep" />
          <StarterTodo v-if="currentStep === 6" :pData="pData" :isLookingBack="isLookingBack" :todoQuestionsMap="todoQuestionsMap" @next="nextStep" />
          <StarterGenerate v-if="currentStep === 7" :pData="pData" @projectCreated="onProjectCreated" />
        </div>
      </div>
    </div>

    <div v-if="!successScreenData" id="starter-footer" class="bg-cm-top-bar border-t border-gray-700 px-6 py-4 flex items-center justify-between shrink-0 relative z-10">
      <button v-if="currentStep > 1" @click="prevStep" v-info="'starter_nav_prev'" class="bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded font-bold transition-all flex items-center">&lt; Previous Step</button>
      <div v-else></div>
      <button v-if="activeStepsList.indexOf(currentStep) < activeStepsList.length - 1" @click="nextStep" :disabled="isNextDisabled" v-info="'starter_nav_next'" class="bg-cm-blue hover:bg-blue-500 disabled:bg-gray-700 disabled:opacity-50 text-white px-10 py-2 rounded font-bold shadow-lg transition-all flex items-center">
        {{ currentStep === 4 && (Array.isArray(pData.stack) ? !pData.stack.length : !pData.stack.trim()) ? 'Skip Stack' : 'Next Step >' }}
      </button>
    </div>
    <div id="starter-teleport-anchor"></div>
  </div>
</template>