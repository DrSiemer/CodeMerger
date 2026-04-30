import { ref, reactive, watch } from 'vue'
import { useAppState } from '../useAppState'

export function useStarterState() {
  const {
    config,
    getStarterSession,
    saveStarterSession,
    clearStarterSession,
    exportStarterConfig,
    loadStarterConfig,
    getConceptQuestions,
    getDesignQuestions,
    getTodoQuestions
  } = useAppState()

  const isLoading = ref(true)
  const isResetting = ref(false)
  const toastMessage = ref('')
  const showToast = ref(false)
  let toastTimer = null

  const pData = reactive({
    name: '',
    starting_mode: null,
    parent_folder: '',
    stack: [],
    stack_experience: '',
    goal: '',
    concept_md: '',
    design_md: '',
    todo_md: '',
    base_project_path: '',
    base_project_files: [],
    include_base_reference: true,

    concept_llm_response: '',
    stack_llm_response: '',
    design_llm_response: '',
    todo_llm_response: '',
    generate_llm_response: '',

    concept_segments: {},
    concept_signoffs: {},
    concept_baselines: {},
    design_segments: {},
    design_signoffs: {},
    design_baselines: {},
    todo_phases: [],
    todo_segments: {},
    todo_signoffs: {},
    todo_baselines: {}
  })

  const conceptQuestionsMap = ref({})
  const designQuestionsMap = ref({})
  const todoQuestionsMap = ref({})

  const showToastNotification = (msg) => {
    toastMessage.value = msg
    showToast.value = true
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { showToast.value = false }, 3000)
  }

  const saveState = async (currentStep) => {
    if (isLoading.value || isResetting.value) return
    await saveStarterSession({ current_step: currentStep, ...pData })
  }

  const loadSession = async () => {
    conceptQuestionsMap.value = await getConceptQuestions()
    designQuestionsMap.value = await getDesignQuestions()
    todoQuestionsMap.value = await getTodoQuestions()

    const saved = await getStarterSession()
    if (saved && Object.keys(saved).length > 0) {
      if (typeof saved.stack === 'string' && saved.stack.trim()) {
        saved.stack = saved.stack.split('\n').filter(s => s.trim()).map(s => ({ tech: s, rationale: 'Imported from previous version' }))
      } else if (!saved.stack) {
        saved.stack = []
      }
      Object.assign(pData, saved)
      isLoading.value = false
      return saved.current_step || 1
    } else {
      pData.parent_folder = config.value?.default_parent_folder || ''
      pData.stack_experience = config.value?.user_experience || ''
      isLoading.value = false
      return 1
    }
  }

  const performReset = async () => {
    isResetting.value = true
    await clearStarterSession()

    Object.assign(pData, {
      name: '',
      starting_mode: null,
      parent_folder: config.value?.default_parent_folder || '',
      stack: [],
      stack_experience: config.value?.user_experience || '',
      goal: '',
      concept_md: '',
      design_md: '',
      todo_md: '',
      base_project_path: '',
      base_project_files: [],
      include_base_reference: true,
      concept_llm_response: '',
      stack_llm_response: '',
      design_llm_response: '',
      todo_llm_response: '',
      generate_llm_response: '',
      concept_segments: {},
      concept_signoffs: {},
      concept_baselines: {},
      design_segments: {},
      design_signoffs: {},
      design_baselines: {},
      todo_phases: [],
      todo_segments: {},
      todo_signoffs: {},
      todo_baselines: {}
    })
    isResetting.value = false
  }

  const handleExport = async (currentStep) => {
    const success = await exportStarterConfig({ current_step: currentStep, ...pData })
    if (success) showToastNotification("Config saved successfully.")
  }

  const handleImport = async () => {
    const loadedData = await loadStarterConfig()
    if (loadedData) {
      Object.assign(pData, loadedData)
      showToastNotification("Config loaded successfully.")
      return loadedData.current_step || 1
    }
    return null
  }

  return {
    pData,
    isLoading,
    isResetting,
    toastMessage,
    showToast,
    conceptQuestionsMap,
    designQuestionsMap,
    todoQuestionsMap,
    loadSession,
    saveState,
    performReset,
    handleExport,
    handleImport
  }
}