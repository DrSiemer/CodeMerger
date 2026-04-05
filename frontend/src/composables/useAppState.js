import { ref, reactive } from 'vue'

export function useAppState() {
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

  const getRecentProjects = async () => {
    if (window.pywebview) {
      return await window.pywebview.api.get_recent_projects()
    }
    return []
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
    selectProject,
    loadProject,
    getRecentProjects,
    removeRecentProject,
    copyCode
  }
}