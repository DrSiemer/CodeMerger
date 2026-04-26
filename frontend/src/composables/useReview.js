import { computed } from 'vue'
import { lastAiResponse, planFileStates, planOriginalContents, activeProject, statusMessage, showFormatErrorModal, formatErrorMessage, verificationHistory, hasAcceptedChanges } from './globalState'
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

  const addToVerificationHistory = (content) => {
    if (!content || content === '-' || content.trim().length === 0) return

    const history = verificationHistory.value
    const lastEntry = history.length > 0 ? history[history.length - 1] : null

    // Ignore identical verification in succession
    if (!lastEntry || lastEntry.content !== content) {
      const now = new Date()

      const displayTimestamp = now.toLocaleString([], {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      })

      history.push({
        content: content,
        timestamp: displayTimestamp,
        rawTime: now.getTime()
      })
    }
  }

  // Helper to archive the verification section of the interaction that just ended
  const archivePreviousVerification = () => {
    const prevPlan = lastAiResponse.value
    if (!prevPlan || !hasAcceptedChanges.value) return

    addToVerificationHistory(prevPlan.verification)

    // Reset the modification flag for the next response
    hasAcceptedChanges.value = false
  }

  const processPaste = async () => {
    if (!window.pywebview) return false

    // OVERWRITE CHECK
    if (hasPendingChanges.value) {
      if (!confirm("An AI response is already in memory with changes that have not been applied yet.\n\nDo you want to overwrite it with the new response from your clipboard?")) {
        return false
      }
    }

    try {
      // Use Python backend to access system clipboard to bypass browser prompts
      const text = await getClipboardText()

      if (!text || !text.trim()) {
        statusMessage.value = "Clipboard is empty."
        return false
      }

      const plan = await window.pywebview.api.parse_markdown_response(text)

      archivePreviousVerification()
      lastAiResponse.value = plan

      planFileStates.value = {}
      planOriginalContents.value = {}

      const updates = plan.updates || {}
      const creations = plan.creations || {}
      const deletions = plan.deletions_proposed || []
      const skipped = plan.skipped_files || []

      // Initialize states including the new 'skipped' status for NO-OP files
      Object.keys(updates).forEach(p => planFileStates.value[p] = skipped.includes(p) ? 'skipped' : 'pending')
      Object.keys(creations).forEach(p => planFileStates.value[p] = 'pending')
      deletions.forEach(p => planFileStates.value[p] = skipped.includes(p) ? 'skipped' : 'pending')

      if (plan.status === 'ERROR') {
        formatErrorMessage.value = plan.message
        showFormatErrorModal.value = true
        return false
      }

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
    hasAcceptedChanges.value = false
    statusMessage.value = "AI response cleared from memory."
  }

  const getFileContent = async (relPath) => {
    if (window.pywebview) {
      return await window.pywebview.api.get_file_content(relPath)
    }
    return null
  }

  const applyFileChange = async (rel_path, content) => {
    if (window.pywebview) {
      const [success, error] = await window.pywebview.api.apply_single_file_change(rel_path, content)
      if (success) {
        hasAcceptedChanges.value = true
        statusMessage.value = `Applied changes to ${rel_path}`
        const proj = await window.pywebview.api.get_current_project()
        project.applyProjectData(proj)
      } else {
        alert(`Error applying change: ${error}`)
      }
      return success
    }
    return false
  }

  const deleteFile = async (rel_path) => {
    if (window.pywebview) {
      const [success, error] = await window.pywebview.api.delete_file(rel_path)
      if (success) {
        hasAcceptedChanges.value = true
        statusMessage.value = `Deleted ${rel_path}`
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

  const copyCode = async (use_wrapper) => {
    if (!activeProject.path) return
    statusMessage.value = 'Merging and copying...'
    const msg = await window.pywebview.api.copy_code(use_wrapper)
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
  const applyFullPlan = async (plan) => {
    if (window.pywebview) {
      const res = await window.pywebview.api.apply_full_plan(plan)
      if (res && res[0]) {
        hasAcceptedChanges.value = true
      }
      return res
    }
    return [false, ""]
  }

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
    applyFullPlan,
    addToVerificationHistory,
    archivePreviousVerification
  }
}