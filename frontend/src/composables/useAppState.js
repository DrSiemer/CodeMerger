import { watch } from 'vue'
import * as globalState from './globalState'
import * as infoMode from './infoMode'
import { useSystem } from './useSystem'
import { useProject } from './useProject'
import { useReview } from './useReview'
import { useStarter } from './useStarter'

// Maintain backwards compatibility for module scope imports
export * from './globalState'
export * from './infoMode'

let statusTimeout = null
let statusFadeTimeout = null
let isInitialized = false
let isAppSetup = false
let initPromise = null

export function useAppState() {
  const system = useSystem()
  const project = useProject()
  const review = useReview()
  const starter = useStarter()

  if (!isInitialized) {
    watch(globalState.statusMessage, (newVal) => {
      if (statusTimeout) clearTimeout(statusTimeout)
      if (statusFadeTimeout) clearTimeout(statusFadeTimeout)

      if (newVal) {
        globalState.statusVisible.value = true

        statusFadeTimeout = setTimeout(() => {
          globalState.statusVisible.value = false
        }, 5000)

        statusTimeout = setTimeout(() => {
          globalState.statusMessage.value = ''
        }, 6100)
      }
    })

    // Synchronizes file states to backend for Compact Mode orange indicator and Overwrite warnings
    watch(globalState.planFileStates, (newStates) => {
      if (window.pywebview && Object.keys(newStates).length > 0) {
        window.pywebview.api.sync_plan_states(JSON.parse(JSON.stringify(newStates)))
      }
    }, { deep: true })

    isInitialized = true
  }

  const refreshProject = async (data = null) => {
    if (data) {
      project.applyProjectData(data)
    } else if (window.pywebview) {
      const proj = await window.pywebview.api.get_current_project()
      project.applyProjectData(proj)
    }

    if (window.pywebview) {
      const status = await review.checkPendingChanges()
      if (!status.exists && globalState.lastAiResponse.value) {
        globalState.lastAiResponse.value = null
        globalState.planFileStates.value = {}
        globalState.planOriginalContents.value = {}
        globalState.showReviewModal.value = false
        globalState.revertToCompactOnClose.value = false
      }
    }
  }

  const init = async () => {
    if (!window.pywebview) return
    if (isAppSetup) return await refreshProject()
    if (initPromise) return await initPromise

    initPromise = (async () => {
      globalState.config.value = await window.pywebview.api.get_app_config()
      infoMode.infoModeActive.value = globalState.config.value.info_mode_active ?? true
      globalState.newlyAddedFiletypes.value = await window.pywebview.api.get_newly_added_filetypes()
      globalState.appIcon.value = await window.pywebview.api.get_image_base64('icon.ico')
      globalState.logoMask.value = await window.pywebview.api.get_image_base64('logo_mask.png')
      globalState.logoMaskSmall.value = await window.pywebview.api.get_image_base64('logo_mask_small.png')

      window.addEventListener('cm-new-files', (e) => { globalState.activeProject.newFileCount = e.detail.count })
      window.addEventListener('cm-project-reloaded', (e) => { refreshProject(e.detail) })
      window.addEventListener('cm-config-updated', (e) => { globalState.config.value = e.detail })
      window.addEventListener('cm-close-review', () => {
        globalState.showReviewModal.value = false
        globalState.revertToCompactOnClose.value = false
      })
      window.addEventListener('cm-archive-verification', (e) => { review.addToVerificationHistory(e.detail.content) })
      window.addEventListener('cm-plan-cleared', () => {
        globalState.lastAiResponse.value = null
        globalState.planFileStates.value = {}
        globalState.planOriginalContents.value = {}
        globalState.showReviewModal.value = false
        globalState.revertToCompactOnClose.value = false
      })

      isAppSetup = true
      await refreshProject()
      initPromise = null
    })()

    return await initPromise
  }

  return {
    ...globalState,
    ...infoMode,
    ...system,
    ...project,
    ...review,
    ...starter,
    init,
    refreshProject
  }
}