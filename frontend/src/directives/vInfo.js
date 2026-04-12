import { useAppState } from '../composables/useAppState'

/**
 * v-info directive
 * Usage: v-info="'key_name'"
 * Manages the global hover stack for Info Mode documentation.
 */
export default {
  mounted(el, binding) {
    const { setHoverInfo, clearHoverInfo } = useAppState()

    el._currentInfoKey = binding.value
    el._isHovered = false

    el._mouseenter = () => {
      el._isHovered = true
      if (el._currentInfoKey) {
        setHoverInfo(el._currentInfoKey)
      }
    }
    el._mouseleave = () => {
      el._isHovered = false
      if (el._currentInfoKey) {
        clearHoverInfo(el._currentInfoKey)
      }
    }

    el.addEventListener('mouseenter', el._mouseenter)
    el.addEventListener('mouseleave', el._mouseleave)
  },

  updated(el, binding) {
    const { setHoverInfo, clearHoverInfo } = useAppState()
    const newKey = binding.value
    const oldKey = el._currentInfoKey

    // If the bound documentation key changes (e.g. Close -> Cancel)
    if (newKey !== oldKey) {
      // If the user is currently hovering, we must swap the keys in the global stack
      if (el._isHovered) {
        if (oldKey) {
          clearHoverInfo(oldKey)
        }
        if (newKey) {
          setHoverInfo(newKey)
        }
      }
      // Synchronize internal reference
      el._currentInfoKey = newKey
    }
  },

  unmounted(el) {
    const { clearHoverInfo } = useAppState()

    // Ensure the info stack is cleaned up if the element is removed while hovered
    if (el._isHovered && el._currentInfoKey) {
      clearHoverInfo(el._currentInfoKey)
    }

    el.removeEventListener('mouseenter', el._mouseenter)
    el.removeEventListener('mouseleave', el._mouseleave)
  }
}