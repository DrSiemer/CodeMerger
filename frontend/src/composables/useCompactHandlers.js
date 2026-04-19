import { ref, reactive, computed } from 'vue'

export function useCompactHandlers(app) {
  const {
    activeProject,
    copyCode,
    checkPendingChanges,
    claimLastPlan,
    lastAiResponse,
    config
  } = app

  const isCopying = ref(false)
  const hasPendingChangesInternal = ref(false)
  const titleOverride = ref(null)

  const feedback = reactive({
    active: false,
    mode: 'none',
    msg: '',
    type: ''
  })

  let feedbackTimer = null
  let titleTimer = null

  const triggerFeedback = (mode, msg, type = '', duration = 1500) => {
    if (feedbackTimer) clearTimeout(feedbackTimer)
    feedback.mode = mode
    feedback.msg = msg
    feedback.type = type
    feedback.active = true
    if (mode !== 'confirm') {
      feedbackTimer = setTimeout(() => { feedback.active = false }, duration)
    }
  }

  const triggerTitleError = (msg) => {
    if (titleTimer) clearTimeout(titleTimer)
    titleOverride.value = msg
    titleTimer = setTimeout(() => { titleOverride.value = null }, 2000)
  }

  const updatePendingStatus = async () => {
    if (!window.pywebview) return
    const status = await checkPendingChanges()
    hasPendingChangesInternal.value = status.has_pending
    if (status.exists && !lastAiResponse.value) {
      lastAiResponse.value = await claimLastPlan()
    } else if (!status.exists && lastAiResponse.value) {
      lastAiResponse.value = null
    }
  }

  const handleCopy = async (event, bypassSecrets = null) => {
    if (!activeProject.path) return
    isCopying.value = true
    try {
      const useWrapper = activeProject.hasInstructions && !event.ctrlKey
      const result = await window.pywebview.api.copy_code(useWrapper, bypassSecrets || false)
      if (result && typeof result === 'object' && result.status === 'SECRETS_DETECTED') {
        triggerFeedback('confirm', 'Secrets found!', 'secrets')
        return
      }
      if (typeof result === 'string') {
        if (result.includes('Error') || result.includes('cancelled')) {
          triggerFeedback('error', result, 'copy', 3000)
        } else {
          triggerFeedback('success', 'COPIED', 'copy')
        }
      }
    } catch (err) {
      triggerFeedback('error', 'Copy Failed', 'copy', 3000)
    } finally {
      isCopying.value = false
    }
  }

  const handlePaste = async (event, forceOverwrite = false) => {
    if (!window.pywebview) return
    if (hasPendingChangesInternal.value && !forceOverwrite) {
      triggerFeedback('confirm', 'Overwrite memory?', 'overwrite')
      return
    }
    try {
      const result = await window.pywebview.api.request_remote_paste(true, !!event.ctrlKey, forceOverwrite)
      if (result === true || typeof result === 'string') {
        lastAiResponse.value = await claimLastPlan()
      }
      await updatePendingStatus()
      if (typeof result === 'string') {
        if (result.includes('Error') || result.includes('empty')) {
          triggerFeedback('error', result, 'paste', 3000)
        } else {
          triggerFeedback('success', 'PASTED', 'paste')
        }
      } else if (result === true) {
        triggerFeedback('success', 'PASTED', 'paste')
      }
    } catch (err) {
      triggerFeedback('error', 'Paste Failed', 'paste', 3000)
    }
  }

  const handleConfirmChoice = async () => {
    const type = feedback.type
    feedback.active = false
    if (type === 'secrets') {
      await handleCopy({ ctrlKey: false }, true)
    } else if (type === 'overwrite') {
      await handlePaste({ ctrlKey: false }, true)
    }
  }

  const isUltra = computed(() => config.value.enable_ultra_compact_mode ?? false)

  const titleAbbr = computed(() => {
    if (titleOverride.value) return titleOverride.value
    const name = activeProject.name || 'CodeMerger'
    if (isUltra.value) return name.charAt(0).toUpperCase()
    const maxLen = 8
    const chars = [...name]
    const capitalIndices = []
    for (let i = 0; i < chars.length; i++) {
      if (chars[i] >= 'A' && chars[i] <= 'Z') capitalIndices.push(i)
    }
    if (capitalIndices.length > 1) {
      const lowercaseIndices = []
      for (let i = 0; i < chars.length; i++) {
        if (chars[i] >= 'a' && chars[i] <= 'z') lowercaseIndices.push(i)
      }
      const lowercaseNeeded = maxLen - capitalIndices.length
      let indicesToKeep = lowercaseNeeded > 0
        ? [...capitalIndices, ...lowercaseIndices.slice(0, lowercaseNeeded)]
        : capitalIndices.slice(0, maxLen)
      indicesToKeep.sort((a, b) => a - b)
      return indicesToKeep.map(i => chars[i]).join('')
    } else {
      return name.replace(/\s/g, '').slice(0, maxLen)
    }
  })

  return {
    isCopying,
    hasPendingChangesInternal,
    feedback,
    titleOverride,
    updatePendingStatus,
    triggerFeedback,
    triggerTitleError,
    handleCopy,
    handlePaste,
    handleConfirmChoice,
    titleAbbr,
    isUltra
  }
}