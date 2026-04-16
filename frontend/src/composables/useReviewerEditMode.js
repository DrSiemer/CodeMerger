import { ref, nextTick } from 'vue'

export function useReviewerEditMode(scrollRef) {
  const reviewerEditMode = ref(false)

  const toggleReviewerEditMode = async (event = null, isContextual = false) => {
    let anchorText = ''
    let contentRatio = 0
    const isDoubleclick = isContextual && event

    const el = scrollRef.value
    if (el) {
      if (!reviewerEditMode.value) {
        if (isDoubleclick) {
          anchorText = window.getSelection().toString().trim().split('\n')[0].substring(0, 50)
        } else {
          const rect = el.getBoundingClientRect()
          const topEl = document.elementFromPoint(rect.left + 50, rect.top + 20)
          if (topEl) {
            anchorText = topEl.innerText?.trim().split('\n')[0].substring(0, 40) || ''
          }
        }
        contentRatio = el.scrollTop / el.scrollHeight
      } else {
        const text = el.value
        contentRatio = el.scrollTop / el.scrollHeight
        const targetCharIdx = Math.floor(text.length * contentRatio)
        anchorText = text.substring(targetCharIdx, targetCharIdx + 60).trim().split('\n')[0]
      }
    }

    reviewerEditMode.value = !reviewerEditMode.value
    await nextTick()

    setTimeout(() => {
      const newEl = scrollRef.value
      if (!newEl) return

      if (reviewerEditMode.value) {
        const fullText = newEl.value
        let foundIdx = -1

        if (anchorText) {
          const startSearch = Math.floor(fullText.length * contentRatio)
          foundIdx = fullText.indexOf(anchorText, Math.max(0, startSearch - 300))
          if (foundIdx === -1) foundIdx = fullText.indexOf(anchorText)
        }

        if (foundIdx !== -1) {
          const charRatio = foundIdx / fullText.length
          const offset = isDoubleclick ? 0.3 : 0.05
          newEl.focus({ preventScroll: true })
          newEl.setSelectionRange(foundIdx, foundIdx + anchorText.length)
          const setPos = () => { newEl.scrollTop = (charRatio * newEl.scrollHeight) - (newEl.clientHeight * offset) }
          setPos()
          requestAnimationFrame(setPos)
        } else {
          newEl.scrollTop = contentRatio * newEl.scrollHeight
        }
      } else {
        let scrolled = false
        if (anchorText) {
          const walker = document.createTreeWalker(newEl, NodeFilter.SHOW_TEXT, null, false)
          let node
          while ((node = walker.nextNode())) {
            if (node.textContent.includes(anchorText)) {
              node.parentElement.scrollIntoView({ block: 'start', behavior: 'instant' })
              newEl.scrollTop -= (newEl.clientHeight * 0.05)
              scrolled = true
              break
            }
          }
        }
        if (!scrolled) {
          newEl.scrollTop = contentRatio * newEl.scrollHeight
        }
      }
    }, 100)
  }

  return {
    reviewerEditMode,
    toggleReviewerEditMode
  }
}