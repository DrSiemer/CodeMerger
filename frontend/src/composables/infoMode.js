import { ref } from 'vue'
import { INFO_MESSAGES } from '../utils/infoMessages'

export const infoModeActive = ref(true)
export const activeInfoStack = ref([])
export const currentInfoText = ref(INFO_MESSAGES['default'])

const _resolveInfoText = () => {
  const stack = activeInfoStack.value;
  if (stack.length > 0) {
    const topKey = stack[stack.length - 1];
    currentInfoText.value = INFO_MESSAGES[topKey] || INFO_MESSAGES['default'];
  } else {
    currentInfoText.value = INFO_MESSAGES['default'];
  }
}

export const setHoverInfo = (key) => {
  if (!activeInfoStack.value.includes(key)) {
    // We use the spread operator to create a new array reference, forcing Vue 3 to trigger reactivity across view boundaries that mutation would miss
    activeInfoStack.value = [...activeInfoStack.value, key];
    _resolveInfoText();
  }
}

export const clearHoverInfo = (key) => {
  if (activeInfoStack.value.includes(key)) {
    activeInfoStack.value = activeInfoStack.value.filter(k => k !== key);
    _resolveInfoText();
  }
}