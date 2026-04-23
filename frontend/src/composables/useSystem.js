import { config, statusMessage, editorFontSize, DEFAULT_FONT_SIZE, newlyAddedFiletypes } from './globalState'
import { infoModeActive } from './infoMode'

export function useSystem() {
  const resetEditorFontSize = () => {
    editorFontSize.value = DEFAULT_FONT_SIZE
  }

  const handleZoom = (e) => {
    const delta = e.deltaY > 0 ? -1 : 1
    editorFontSize.value = Math.max(8, Math.min(editorFontSize.value + delta, 40))
  }

  const getImage = async (filename) => {
    if (window.pywebview) {
      return await window.pywebview.api.get_image_base64(filename)
    }
    return ""
  }

  const resizeWindow = async (width, height) => {
    if (window.pywebview) {
      const footerHeight = infoModeActive.value ? 116 : 36
      await window.pywebview.api.ensure_window_size(width, height + footerHeight)
    }
  }

  const toggleInfoMode = async () => {
    infoModeActive.value = !infoModeActive.value
    if (window.pywebview) {
      const newConfig = { ...config.value, info_mode_active: infoModeActive.value }
      await window.pywebview.api.save_app_config(newConfig)

      // Grow window immediately to prevent dashboard content overlap when enabling info mode
      if (infoModeActive.value) {
        await resizeWindow(window.innerWidth, window.innerHeight - 36)
      }
    }
  }

  const toggleFastApply = async () => {
    if (window.pywebview) {
      const newVal = !(config.value.enable_fast_apply ?? true)
      const newConfig = { ...config.value, enable_fast_apply: newVal }
      await saveConfig(newConfig)
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

  const clearNewlyAddedFiletypes = () => {
    newlyAddedFiletypes.value = []
  }

  const restoreMainWindow = async () => {
    if (window.pywebview) {
      await window.pywebview.api.restore_main_window()
    }
  }

  const minimizeWindow = async (toggle = false) => {
    if (window.pywebview) {
      await window.pywebview.api.minimize_window(toggle)
    }
  }

  const closeApp = async () => {
    if (window.pywebview) {
      await window.pywebview.api.close_app()
    }
  }

  const selectEditorExecutable = async () => {
    if (window.pywebview) {
      return await window.pywebview.api.select_editor_executable()
    }
    return null
  }

  const copyUsefulPrompt = async (promptType) => {
    if (window.pywebview) {
      const msg = await window.pywebview.api.copy_useful_prompt(promptType)
      statusMessage.value = msg
    }
  }

  const checkForUpdatesManual = async () => {
    if (window.pywebview) {
      return await window.pywebview.api.check_for_updates_manual()
    }
    return false
  }

  return {
    resetEditorFontSize,
    handleZoom,
    getImage,
    resizeWindow,
    toggleInfoMode,
    toggleFastApply,
    saveConfig,
    getFiletypes,
    saveFiletypes,
    clearNewlyAddedFiletypes,
    restoreMainWindow,
    minimizeWindow,
    closeApp,
    selectEditorExecutable,
    copyUsefulPrompt,
    checkForUpdatesManual
  }
}