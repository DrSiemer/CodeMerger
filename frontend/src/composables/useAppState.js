import { watch } from 'vue'
import * as globalState from './globalState'
import * as infoMode from './infoMode'
import { useSystem } from './useSystem'
import { useProject } from './useProject'
import { useReview } from './useReview'
import { useStarter } from './useStarter'

// Maintenance of backwards compatibility for module scope imports
export * from './globalState'
export * from './infoMode'

let statusTimeout = null
let statusFadeTimeout = null
let isInitialized = false

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

    // Critical for Compact Mode orange indicator and Overwrite warnings
    watch(globalState.planFileStates, (newStates) => {
      if (window.pywebview && Object.keys(newStates).length > 0) {
        window.pywebview.api.sync_plan_states(JSON.parse(JSON.stringify(newStates)))
      }
    }, { deep: true })

    isInitialized = true
  }

  const init = async () => {
    if (window.pywebview) {
      globalState.config.value = await window.pywebview.api.get_app_config()
      infoMode.infoModeActive.value = globalState.config.value.info_mode_active ?? true

      globalState.newlyAddedFiletypes.value = await window.pywebview.api.get_newly_added_filetypes()

      globalState.appIcon.value = await window.pywebview.api.get_image_base64('icon.ico')
      globalState.logoMask.value = await window.pywebview.api.get_image_base64('logo_mask.png')
      globalState.logoMaskSmall.value = await window.pywebview.api.get_image_base64('logo_mask_small.png')

      const proj = await window.pywebview.api.get_current_project()
      project.applyProjectData(proj)

      window.addEventListener('cm-new-files', (e) => {
        globalState.activeProject.newFileCount = e.detail.count
      })
      window.addEventListener('cm-project-reloaded', () => {
        init()
      })

      window.addEventListener('cm-close-review', () => {
        globalState.showReviewModal.value = false
        globalState.revertToCompactOnClose.value = false
      })
    }
  }

  return {
    ...globalState,
    ...infoMode,
    ...system,
    ...project,
    ...review,
    ...starter,
    init
  }
}