import { ref, reactive, computed } from 'vue'

export const config = ref({})
export const activeProject = reactive({
  path: null,
  name: null,
  color: null,
  fontColor: null,
  activeProfile: 'default',
  profiles: [{ id: 'default', name: 'Default' }],
  totalTokens: 0,
  selectedFiles: [],
  expandedDirs: [],
  hasInstructions: false,
  introText: '',
  outroText: '',
  newFileCount: 0,
  visualizerMap: null
})
export const statusMessage = ref('')
export const statusVisible = ref(false)
export const lastAiResponse = ref(null)
export const newlyAddedFiletypes = ref([])

// Global Shared Assets
export const appIcon = ref('')
export const logoMask = ref('')
export const logoMaskSmall = ref('')

// AI Review State
export const showReviewModal = ref(false)
export const reviewMode = ref('new')
export const revertToCompactOnClose = ref(false)

// Dashboard Tool Modals Visibility
export const showProjectModal = ref(false)
export const showSettingsModal = ref(false)
export const showFileManagerModal = ref(false)
export const showInstructionsModal = ref(false)
export const showStarterModal = ref(false)
export const showVisualizerModal = ref(false)
export const showNewProfileModal = ref(false)
export const showPromptsModal = ref(false)

// A tool modal is "blocking" if it covers the dashboard and handles its own input/shortcuts
export const isBlockingModalActive = computed(() => {
  return showProjectModal.value ||
         showSettingsModal.value ||
         showFileManagerModal.value ||
         showInstructionsModal.value ||
         showStarterModal.value ||
         showVisualizerModal.value ||
         showNewProfileModal.value ||
         showPromptsModal.value ||
         showColorPicker.value ||
         showFormatErrorModal.value
})

// Color Picker State
export const showColorPicker = ref(false)
export const originalProjectColor = ref(null)

// Editor Scaling State
export const DEFAULT_FONT_SIZE = 15
export const editorFontSize = ref(DEFAULT_FONT_SIZE)

// Indexing/Loading State
export const isProjectLoading = ref(false)

// Persistence for AI Review Window
// path -> 'pending' | 'applied' | 'rejected' | 'deleted' | 'skipped'
export const planFileStates = ref({})
// path -> string content (for undo)
export const planOriginalContents = ref({})

// Order Request Error Modal State
export const showOrderErrorModal = ref(false)
export const orderErrorMessage = ref('')

// Format Error Modal State
export const showFormatErrorModal = ref(false)
export const formatErrorMessage = ref('')

// Verification History (Session-only)
export const verificationHistory = ref([])
export const hasAcceptedChanges = ref(false)