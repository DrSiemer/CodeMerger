import { ref, reactive } from 'vue'

export const config = ref({})
export const activeProject = reactive({
  path: null,
  name: null,
  color: null,
  fontColor: null,
  activeProfile: 'Default',
  profiles: ['Default'],
  totalTokens: 0,
  selectedFiles: [],
  expandedDirs: [],
  hasInstructions: false,
  introText: '',
  outroText: '',
  newFileCount: 0
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
export const reviewMode = ref('new') // 'new' or 'resume'
export const revertToCompactOnClose = ref(false)

// Editor Scaling State
export const DEFAULT_FONT_SIZE = 15
export const editorFontSize = ref(DEFAULT_FONT_SIZE)

// Indexing/Loading State
export const isProjectLoading = ref(false)

// Persistence for AI Review Window
export const planFileStates = ref({}) // path -> 'pending' | 'applied' | 'rejected' | 'deleted' | 'skipped'
export const planOriginalContents = ref({}) // path -> string content (for undo)

// Order Request Error Modal State
export const showOrderErrorModal = ref(false)
export const orderErrorMessage = ref('')