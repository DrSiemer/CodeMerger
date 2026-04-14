import { activeProject, statusMessage, isProjectLoading, showColorPicker, originalProjectColor } from './globalState'

export function useProject() {
  const applyProjectData = (projData) => {
    if (projData && projData.path) {
      activeProject.path = projData.path
      activeProject.name = projData.project_name
      activeProject.color = projData.project_color
      activeProject.fontColor = projData.project_font_color
      activeProject.activeProfile = projData.active_profile || 'Default'
      activeProject.profiles = projData.profiles || ['Default']
      activeProject.totalTokens = projData.total_tokens
      activeProject.selectedFiles = projData.selected_files || []
      activeProject.expandedDirs = projData.expanded_dirs || []
      activeProject.hasInstructions = projData.has_instructions
      activeProject.introText = projData.intro_text || ''
      activeProject.outroText = projData.outro_text || ''
      activeProject.newFileCount = projData.new_file_count || 0
      if (projData.status_msg) {
        statusMessage.value = projData.status_msg
      }
    } else {
      // Logic for cancelled, deactivated, or invalid loads
      activeProject.path = null
      activeProject.name = null
      activeProject.color = null
      activeProject.fontColor = null
      activeProject.activeProfile = 'Default'
      activeProject.profiles = ['Default']
      activeProject.totalTokens = 0
      activeProject.selectedFiles = []
      activeProject.expandedDirs = []
      activeProject.hasInstructions = false
      activeProject.introText = ''
      activeProject.outroText = ''
      activeProject.newFileCount = 0

      if (projData && projData.status_msg) {
        statusMessage.value = projData.status_msg
      } else {
        statusMessage.value = 'No project active'
      }
    }
  }

  const selectProject = async () => {
    statusMessage.value = 'Waiting for selection...'
    if (window.pywebview) {
      const path = await window.pywebview.api.select_project()
      return path
    }
    return null
  }

  const selectColor = () => {
    if (!activeProject.path) return
    originalProjectColor.value = activeProject.color
    showColorPicker.value = true
  }

  const saveProjectColor = async (hex) => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.save_project_color(hex)
      if (proj) applyProjectData(proj)
    }
  }

  const loadProject = async (path) => {
    if (!path) return
    statusMessage.value = 'Loading project...'
    isProjectLoading.value = true
    try {
      const proj = await window.pywebview.api.load_project(path)
      if (proj && proj.path) {
        applyProjectData(proj)
      } else if (proj && proj.status_msg) {
        statusMessage.value = proj.status_msg
      }
    } finally {
      isProjectLoading.value = false
    }
  }

  const cancelLoadProject = async () => {
    if (window.pywebview && isProjectLoading.value) {
      await window.pywebview.api.cancel_load_project()
    }
  }

  const renameProject = async (newName) => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.rename_project(newName)
      if (proj) applyProjectData(proj)
    }
  }

  const removeRecentProject = async (path) => {
    if (window.pywebview) {
      const result = await window.pywebview.api.remove_recent_project(path)
      if (path === activeProject.path) applyProjectData(null)
      return Array.isArray(result) ? result : []
    }
    return []
  }

  const switchProfile = async (name) => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.switch_profile(name)
      if (proj) applyProjectData(proj)
    }
  }

  const createProfile = async (name, copyFiles, copyInstructions) => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.create_profile(name, copyFiles, copyInstructions)
      if (proj) {
        applyProjectData(proj)
        return true
      }
    }
    return false
  }

  const deleteProfile = async (name) => {
    if (window.pywebview) {
      const proj = await window.pywebview.api.delete_profile(name)
      if (proj) applyProjectData(proj)
    }
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

  const getFileTree = async (filterText, isExtFilter, isGitFilter, currentSelectedPaths) => {
    if (window.pywebview) {
      return await window.pywebview.api.get_file_tree(filterText, isExtFilter, isGitFilter, currentSelectedPaths)
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

  const openFile = async (relPath) => {
    if (window.pywebview) {
      return await window.pywebview.api.open_file(relPath)
    }
    return false
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

  const getRecentProjects = async () => window.pywebview ? await window.pywebview.api.get_recent_projects() : []

  return {
    applyProjectData,
    selectProject,
    selectColor,
    saveProjectColor,
    loadProject,
    cancelLoadProject,
    renameProject,
    removeRecentProject,
    switchProfile,
    createProfile,
    deleteProfile,
    openProjectFolder,
    clearUnknownFiles,
    addAllNewFiles,
    getFileTree,
    updateProjectFiles,
    copyOrderRequest,
    openFile,
    saveInstructions,
    getRecentProjects
  }
}