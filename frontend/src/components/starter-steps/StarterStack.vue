<script setup>
import { ref } from 'vue'
import { useAppState } from '../../composables/useAppState'
import StackDeleteModal from './stack/StackDeleteModal.vue'
import StackExperienceInput from './stack/StackExperienceInput.vue'
import StackPasteResponse from './stack/StackPasteResponse.vue'
import StackReviewList from './stack/StackReviewList.vue'

const props = defineProps({
  pData: {
    type: Object,
    required: true
  },
  isLookingBack: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['next'])

const { generateStackPrompt, handleZoom, copyText } = useAppState()

// Sub-states: 'input' | 'pasting' | 'review'
const viewState = ref((Array.isArray(props.pData.stack) && props.pData.stack.length > 0) ? 'review' : (props.pData.stack_llm_response ? 'pasting' : 'input'))

const showConfirmDelete = ref(false)
const deleteTargetIndex = ref(null)
const listRef = ref(null)

const requestDelete = (idx) => {
  deleteTargetIndex.value = idx
  showConfirmDelete.value = true
}

const abortDelete = () => {
  deleteTargetIndex.value = null
  showConfirmDelete.value = false
}

const confirmDelete = () => {
  if (deleteTargetIndex.value !== null) {
    props.pData.stack.splice(deleteTargetIndex.value, 1)
    if (listRef.value) listRef.value.expandedIndices.delete(deleteTargetIndex.value)
  }
  abortDelete()
}

const handleGeneratePrompt = async (e) => {
  const btn = e.currentTarget
  if (!e.ctrlKey) {
    const prompt = await generateStackPrompt(props.pData)
    await copyText(prompt)
    const originalText = btn.innerText
    btn.innerText = "Copied!"
    setTimeout(() => { if (btn) btn.innerText = originalText }, 2000)
  }
  viewState.value = 'pasting'
}

const handleReset = () => {
  if (confirm("Reset tech stack selection and return to input?")) {
    props.pData.stack = []
    props.pData.stack_llm_response = ''
    if (listRef.value) listRef.value.expandedIndices.clear()
    viewState.value = 'input'
  }
}
</script>

<template>
  <div class="h-full flex flex-col text-gray-100 relative" @wheel.ctrl.prevent="handleZoom">

    <StackDeleteModal
      v-if="showConfirmDelete"
      :target="pData.stack[deleteTargetIndex]"
      @confirm="confirmDelete"
      @abort="abortDelete"
    />

    <StackExperienceInput
      v-if="viewState === 'input'"
      :pData="pData"
      @generate="handleGeneratePrompt"
    />

    <StackPasteResponse
      v-else-if="viewState === 'pasting'"
      :pData="pData"
      @processed="viewState = 'review'"
      @back="viewState = 'input'"
      @generate="handleGeneratePrompt"
    />

    <StackReviewList
      v-else-if="viewState === 'review'"
      ref="listRef"
      :pData="pData"
      :isLookingBack="isLookingBack"
      @reset="handleReset"
      @request-delete="requestDelete"
      @next="$emit('next')"
    />

  </div>
</template>