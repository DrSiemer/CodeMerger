import { onMounted, onUnmounted } from 'vue'

export function useEscapeKey(callback) {
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') callback(e)
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
  })
}