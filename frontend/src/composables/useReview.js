import { computed } from 'vue'
import { lastAiResponse, planFileStates, planOriginalContents, activeProject, statusMessage } from './globalState'
import { useProject } from './useProject'

export function useReview() {
  const project = useProject()

  const hasPendingChanges = computed(() => {
    if (!lastAiResponse.value) return false
    const states = Object.values(planFileStates.value)
    if (states.length === 0) return false
    return states.some(s => s === 'pending')
  })

  const getClipboardText = async () => {
    if (window.pywebview) {
      return await window.pywebview.api.get_clipboard_text()
    }
    return ""
  }

  const processPaste = async () => {
    if (!window.pywebview) return false

    // OVERWRITE CHECK (Main Dashboard flow)
    if (hasPendingChanges.value) {
      if (!confirm("An AI response is already in memory with changes that have not been applied yet.\n\nDo you want to overwrite it with the new response from your clipboard?")) {
        return false
      }
    }

    try {
      // Use Python backend to access system clipboard bypassing browser prompts
      const text = await getClipboardText()

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
      const skipped = plan.skipped_files || []

      // CRITICAL: Initialize states including the new 'skipped' status for NO-OP files
      Object.keys(updates).forEach(p => planFileStates.value[p] = skipped.includes(p) ? 'skipped' : 'pending')
      Object.keys(creations).forEach(p => planFileStates.value[p] = 'pending')
      deletions.forEach(p => planFileStates.value[p] = skipped.includes(p) ? 'skipped' : 'pending')

      return true
    } catch (err) {
      statusMessage.value = "Failed to access clipboard."
      return false
    }
  }

  const clearPasteData = async () => {
    if (window.pywebview) {
      await window.pywebview.api.clear_parsed_plan()
    }
    lastAiResponse.value = null
    planFileStates.value = {}
    planOriginalContents.value = {}
    statusMessage.value = "AI response cleared from memory."
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
        project.applyProjectData(proj)
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
        project.applyProjectData(proj)
      } else {
        alert(`Error deleting file: ${error}`)
      }
      return success
    }
    return false
  }

  const copyAdmonishment = async () => {
    if (window.pywebview) {
      const msg = await window.pywebview.api.copy_admonishment()
      statusMessage.value = msg
    }
  }

  const copyCode = async (useWrapper) => {
    if (!activeProject.path) return
    statusMessage.value = 'Merging and copying...'
    const msg = await window.pywebview.api.copy_code(useWrapper)
    statusMessage.value = msg
  }

  const claimLastPlan = async () => window.pywebview ? await window.pywebview.api.claim_last_plan() : null

  const checkPendingChanges = async () => {
    if (window.pywebview) {
      return await window.pywebview.api.check_for_pending_changes()
    }
    return { exists: false, has_pending: false }
  }

  const syncPlanStates = async (states) => window.pywebview ? await window.pywebview.api.sync_plan_states(states) : false
  const applyFullPlan = async (plan) => window.pywebview ? await window.pywebview.api.apply_full_plan(plan) : [false, ""]

  return {
    hasPendingChanges,
    getClipboardText,
    processPaste,
    clearPasteData,
    getFileContent,
    applyFileChange,
    deleteFile,
    copyAdmonishment,
    copyCode,
    claimLastPlan,
    checkPendingChanges,
    syncPlanStates,
    applyFullPlan
  }
}