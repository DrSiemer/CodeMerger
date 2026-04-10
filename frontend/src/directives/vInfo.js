import { useAppState } from '../composables/useAppState'

/**
 * v-info directive
 * Usage: v-info="'key_name'"
 * Manages the global hover stack for Info Mode documentation.
 */
export default {
  mounted(el, binding) {
    const { setHoverInfo, clearHoverInfo } = useAppState()

    el._mouseenter = () => {
      if (binding.value) {
        setHoverInfo(binding.value)
      }
    }
    el._mouseleave = () => {
      if (binding.value) {
        clearHoverInfo(binding.value)
      }
    }

    el.addEventListener('mouseenter', el._mouseenter)
    el.addEventListener('mouseleave', el._mouseleave)
  },
  unmounted(el, binding) {
    const { clearHoverInfo } = useAppState()
    if (binding.value) {
      clearHoverInfo(binding.value)
    }
    el.removeEventListener('mouseenter', el._mouseenter)
    el.removeEventListener('mouseleave', el._mouseleave)
  }
}