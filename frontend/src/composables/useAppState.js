import { ref, reactive } from 'vue'

// Define state variables OUTSIDE the composable function to create a global singleton.
// This ensures all components (App, Settings, Modals) share the exact same data.
const config = ref({})
const activeProject = reactive({
  path: null,
  name: null,
  color: null,
  fontColor: null,
  totalTokens: 0,
  hasInstructions: false
})
const statusMessage = ref('Initializing...')

export function useAppState() {
  const applyProjectData = (projData) => {
    if (projData) {
      activeProject.path = projData.path
      activeProject.name = projData.project_name
      activeProject.color = projData.project_color
      activeProject.fontColor = projData.project_font_color
      activeProject.totalTokens = projData.total_tokens
      activeProject.hasInstructions = projData.has_instructions
      if (projData.status_msg) {
        statusMessage.value = projData.status_msg
      }
    } else {
      activeProject.path = null
      activeProject.name = null
      activeProject.color = null
      activeProject.hasInstructions = false
      statusMessage.value = 'No project selected'
    }
  }

  const init = async () => {
    if (window.pywebview) {
      config.value = await window.pywebview.api.get_app_config()
      const proj = await window.pywebview.api.get_current_project()
      applyProjectData(proj)
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

  return {
    config,
    activeProject,
    statusMessage,
    init,
    getImage,
    resizeWindow,
    saveConfig,
    getFiletypes,
    saveFiletypes,
    selectProject,
    loadProject,
    renameProject,
    getRecentProjects: async () => window.pywebview ? await window.pywebview.api.get_recent_projects() : [],
    removeRecentProject,
    copyCode
  }
}