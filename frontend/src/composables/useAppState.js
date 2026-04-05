import { ref, reactive } from 'vue'

export function useAppState() {
  const config = ref({})
  const activeProject = reactive({
    path: null,
    name: null,
    color: null,
    fontColor: null,
    totalTokens: 0
  })
  const statusMessage = ref('Initializing...')

  const applyProjectData = (projData) => {
    if (projData) {
      activeProject.path = projData.path
      activeProject.name = projData.project_name
      activeProject.color = projData.project_color
      activeProject.fontColor = projData.project_font_color
      activeProject.totalTokens = projData.total_tokens
      if (projData.status_msg) {
        statusMessage.value = projData.status_msg
      }
    } else {
      activeProject.path = null
      activeProject.name = null
      activeProject.color = null
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
      // If the user didn't cancel the dialog, apply the loaded project
      applyProjectData(proj)
    } else {
      statusMessage.value = 'Selection cancelled'
    }
  }

  return {
    config,
    activeProject,
    statusMessage,
    init,
    selectProject
  }
}