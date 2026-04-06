import { ref, reactive, watch } from 'vue'

// Define state variables OUTSIDE the composable function to create a global singleton.
const config = ref({})
const activeProject = reactive({
  path: null,
  name: null,
  color: null,
  fontColor: null,
  totalTokens: 0,
  selectedFiles: [],
  expandedDirs: [],
  hasInstructions: false,
  introText: '',
  outroText: '',
  newFileCount: 0
})
const statusMessage = ref('')
const statusVisible = ref(false)
const lastAiResponse = ref(null)

// Assets
const logoMask = ref('')
const logoMaskSmall = ref('')

// AI Review State
const showReviewModal = ref(false)
const reviewMode = ref('new') // 'new' or 'resume'
const revertToCompactOnClose = ref(false)

// Persistence for AI Review Window
const planFileStates = ref({}) // path -> 'pending' | 'applied' | 'rejected' | 'deleted'
const planOriginalContents = ref({}) // path -> string content (for undo)

let statusTimeout = null
let statusFadeTimeout = null

// Watcher to handle status message auto-clear and fading
watch(statusMessage, (newVal) => {
  // Clear any existing timers when a new message arrives
  if (statusTimeout) clearTimeout(statusTimeout)
  if (statusFadeTimeout) clearTimeout(statusFadeTimeout)

  if (newVal) {
    // Show immediately
    statusVisible.value = true

    // Step 1: Start fading after 5 seconds (to finish at 6s)
    statusFadeTimeout = setTimeout(() => {
      statusVisible.value = false
    }, 5000)

    // Step 2: Fully clear text after transition is complete
    statusTimeout = setTimeout(() => {
      statusMessage.value = ''
    }, 6100)
  }
})

export function useAppState() {
  const applyProjectData = (projData) => {
    if (projData) {
      activeProject.path = projData.path
      activeProject.name = projData.project_name
      activeProject.color = projData.project_color
      activeProject.fontColor = projData.project_font_color
      activeProject.totalTokens = projData.total_tokens
      activeProject.selectedFiles = projData.selected_files || []
      activeProject.expandedDirs = projData.expanded_dirs || []
      activeProject.hasInstructions = projData.has_instructions
      activeProject.introText = projData.intro_text || ''
      activeProject.outroText = projData.outro_text || ''
      if (projData.status_msg) {
        statusMessage.value = projData.status_msg
      }
    } else {
      activeProject.path = null
      activeProject.name = null
      activeProject.color = null
      activeProject.selectedFiles = []
      activeProject.expandedDirs = []
      activeProject.hasInstructions = false
      activeProject.introText = ''
      activeProject.outroText = ''
      statusMessage.value = 'No project selected'
    }
  }

  const init = async () => {
    if (window.pywebview) {
      config.value = await window.pywebview.api.get_app_config()

      // Load static assets into global store immediately
      logoMask.value = await window.pywebview.api.get_image_base64('logo_mask.png')
      logoMaskSmall.value = await window.pywebview.api.get_image_base64('logo_mask_small.png')

      const proj = await window.pywebview.api.get_current_project()
      applyProjectData(proj)

      // Background Monitor Listeners
      window.addEventListener('cm-new-files', (e) => {
        activeProject.newFileCount = e.detail.count
      })
      window.addEventListener('cm-project-reloaded', () => {
        init() // Re-fetch all data on external config change
      })
    }
  }

  const getImage = async (filename) => {
    if (window.pywebview) {
      return await window.pywebview.api.get_image_base64(filename)
    }
    return ""
  }

  const resizeWindow = async (width, height) => {
    if (window.pywebview) {
      await window.pywebview.api.ensure_window_size(width, height)
    }
  }

  const saveConfig = async (newConfig) => {
    if (window.pywebview) {
      const success = await window.pywebview.api.save_app_config(newConfig)
      if (success) {
        config.value = newConfig
        statusMessage.value = "Settings updated successfully."
      } else {
        statusMessage.value = "Failed to save settings."
      }
    }
  }

  const getFiletypes = async () => {
    if (window.pywebview) {
      return await window.pywebview.api.get_filetypes()
    }
    return []
  }

  const saveFiletypes = async (types) => {
    if (window.pywebview) {
      const success = await window.pywebview.api.save_filetypes(types)
      if (success) {
        statusMessage.value = "Filetypes updated successfully."
      } else {
        statusMessage.value = "Failed to save filetypes."
      }
    }
  }

  const selectProject = async () => {
    statusMessage.value = 'Waiting for selection...'
    const proj = await window.pywebview.api.select_project()
    if (proj !== undefined) {
      applyProjectData(proj)
      return proj
    } else {
      statusMessage.value = 'Selection cancelled'
      return null
    }
  }

  const selectColor = async () => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.select_color()
      if (proj) {
        applyProjectData(proj)
      }
    }
  }

  const loadProject = async (path) => {
    statusMessage.value = 'Loading project...'
    const proj = await window.pywebview.api.load_project(path)
    if (proj) {
      applyProjectData(proj)
    }
  }

  const renameProject = async (newName) => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.rename_project(newName)
      if (proj) {
        applyProjectData(proj)
      }
    }
  }

  const removeRecentProject = async (path) => {
    if (window.pywebview) {
      return await window.pywebview.api.remove_recent_project(path)
    }
    return []
  }

  const copyCode = async (useWrapper) => {
    if (!activeProject.path) return
    statusMessage.value = 'Merging and copying...'
    const msg = await window.pywebview.api.copy_code(useWrapper)
    statusMessage.value = msg
  }

  const openProjectFolder = async (event) => {
    if (!activeProject.path) return
    const msg = await window.pywebview.api.open_project_folder(event.ctrlKey, event.altKey)
    statusMessage.value = msg
  }

  const clearUnknownFiles = async () => {
    if (window.pywebview) {
      await window.pywebview.api.clear_unknown_files()
      activeProject.newFileCount = 0
    }
  }

  const addAllNewFiles = async () => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.add_all_new_files()
      if (proj) {
        applyProjectData(proj)
        activeProject.newFileCount = 0
      }
    }
  }

  const saveInstructions = async (intro, outro) => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.save_project_instructions(intro, outro)
      if (proj) {
        applyProjectData(proj)
        return true
      }
    }
    return false
  }

  const copyCleanupPrompt = async () => {
    if (window.pywebview) {
      const msg = await window.pywebview.api.copy_comment_cleanup_prompt()
      statusMessage.value = msg
    }
  }

  const restoreMainWindow = async () => {
    if (window.pywebview) {
      await window.pywebview.api.restore_main_window()
    }
  }

  const minimizeWindow = async () => {
    if (window.pywebview) {
      await window.pywebview.api.minimize_window()
    }
  }

  const closeApp = async () => {
    if (window.pywebview) {
      await window.pywebview.api.close_app()
    }
  }

  // --- AI Feedback & Change Applier ---

  const processPaste = async () => {
    if (!window.pywebview) return false
    try {
      // Use Python backend to access system clipboard bypassing browser prompts
      const text = await window.pywebview.api.get_clipboard_text()

      if (!text || !text.trim()) {
        statusMessage.value = "Clipboard is empty."
        return false
      }

      const plan = await window.pywebview.api.parse_markdown_response(text)
      if (plan.status === 'ERROR') {
        alert(plan.message)
        return false
      }

      lastAiResponse.value = plan

      // Reset Review State for new plan
      planFileStates.value = {}
      planOriginalContents.value = {}

      const updates = plan.updates || {}
      const creations = plan.creations || {}
      const deletions = plan.deletions_proposed || []

      Object.keys(updates).forEach(p => planFileStates.value[p] = 'pending')
      Object.keys(creations).forEach(p => planFileStates.value[p] = 'pending')
      deletions.forEach(p => planFileStates.value[p] = 'pending')

      return true
    } catch (err) {
      statusMessage.value = "Failed to access clipboard."
      return false
    }
  }

  const getFileContent = async (relPath) => {
    if (window.pywebview) {
      return await window.pywebview.api.get_file_content(relPath)
    }
    return null
  }

  const applyFileChange = async (relPath, content) => {
    if (window.pywebview) {
      const [success, error] = await window.pywebview.api.apply_single_file_change(relPath, content)
      if (success) {
        statusMessage.value = `Applied changes to ${relPath}`
        // Trigger a reload of current project to update token counts and selection list
        const proj = await window.pywebview.api.get_current_project()
        applyProjectData(proj)
      } else {
        alert(`Error applying change: ${error}`)
      }
      return success
    }
    return false
  }

  const deleteFile = async (relPath) => {
    if (window.pywebview) {
      const [success, error] = await window.pywebview.api.delete_file(relPath)
      if (success) {
        statusMessage.value = `Deleted ${relPath}`
        const proj = await window.pywebview.api.get_current_project()
        applyProjectData(proj)
      } else {
        alert(`Error deleting file: ${error}`)
      }
      return success
    }
    return false
  }

  const copyAdmonishment = async () => {
    if (window.pywebview) {
      const prompt = await window.pywebview.api.get_admonishment_prompt()
      await navigator.clipboard.writeText(prompt)
      statusMessage.value = "Copied format correction prompt."
    }
  }

  // --- File Management ---

  const getFileTree = async (filterText, isExtFilter, isGitFilter) => {
    if (window.pywebview) {
      return await window.pywebview.api.get_file_tree(filterText, isExtFilter, isGitFilter)
    }
    return []
  }

  const updateProjectFiles = async (newList, tokenCount, expandedDirs) => {
    if (window.pywebview) {
      const success = await window.pywebview.api.update_project_files(newList, tokenCount, expandedDirs)
      if (success) {
        activeProject.selectedFiles = newList
        activeProject.totalTokens = tokenCount
        activeProject.expandedDirs = expandedDirs
        statusMessage.value = "Merge order updated."
      }
    }
  }

  const copyOrderRequest = async (selectedFiles) => {
    if (window.pywebview) {
      const msg = await window.pywebview.api.generate_order_request(selectedFiles)
      if (msg) {
        statusMessage.value = msg
        return true
      }
    }
    return false
  }

  return {
    config,
    activeProject,
    statusMessage,
    statusVisible,
    lastAiResponse,
    showReviewModal,
    reviewMode,
    revertToCompactOnClose,
    planFileStates,
    planOriginalContents,
    logoMask,
    logoMaskSmall,
    init,
    getImage,
    resizeWindow,
    saveConfig,
    getFiletypes,
    saveFiletypes,
    selectProject,
    selectColor,
    loadProject,
    renameProject,
    getRecentProjects: async () => window.pywebview ? await window.pywebview.api.get_recent_projects() : [],
    removeRecentProject,
    copyCode,
    openProjectFolder,
    clearUnknownFiles,
    addAllNewFiles,
    getFileTree,
    updateProjectFiles,
    copyOrderRequest,
    processPaste,
    getFileContent,
    applyFileChange,
    deleteFile,
    copyAdmonishment,
    saveInstructions,
    copyCleanupPrompt,
    restoreMainWindow,
    minimizeWindow,
    closeApp
  }
}