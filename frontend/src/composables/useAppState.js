import { watch } from 'vue'
import * as globalState from './globalState'
import * as infoMode from './infoMode'
import { useSystem } from './useSystem'
import { useProject } from './useProject'
import { useReview } from './useReview'
import { useStarter } from './useStarter'

// Re-export state and infoMode modules to maintain backwards compatibility
// with components directly importing these variables from useAppState.js
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
    // Watcher to handle status message auto-clear and fading
    watch(globalState.statusMessage, (newVal) => {
      if (statusTimeout) clearTimeout(statusTimeout)
      if (statusFadeTimeout) clearTimeout(statusFadeTimeout)

      if (newVal) {
        globalState.statusVisible.value = true

        // Step 1: Start fading after 5 seconds (to finish at 6s)
        statusFadeTimeout = setTimeout(() => {
          globalState.statusVisible.value = false
        }, 5000)

        // Step 2: Fully clear text after transition is complete
        statusTimeout = setTimeout(() => {
          globalState.statusMessage.value = ''
        }, 6100)
      }
    })

    // Sync Plan States to backend whenever they change.
    // This is critical for Compact Mode orange indicator and Overwrite warnings.
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

      // Load migration metadata
      globalState.newlyAddedFiletypes.value = await window.pywebview.api.get_newly_added_filetypes()

      // Load all shared assets into global store once the bridge is available
      globalState.appIcon.value = await window.pywebview.api.get_image_base64('icon.ico')
      globalState.logoMask.value = await window.pywebview.api.get_image_base64('logo_mask.png')
      globalState.logoMaskSmall.value = await window.pywebview.api.get_image_base64('logo_mask_small.png')

      const proj = await window.pywebview.api.get_current_project()
      project.applyProjectData(proj)

      // Background Monitor Listeners
      window.addEventListener('cm-new-files', (e) => {
        globalState.activeProject.newFileCount = e.detail.count
      })
      window.addEventListener('cm-project-reloaded', () => {
        init() // Re-fetch all data on external config change
      })

      // Cross-window Event Listener: Close review modal when entering compact mode
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