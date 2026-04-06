<script setup>
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  successScreenData: {
    type: Object,
    required: true
  }
})
const emit = defineEmits(['close'])

const { loadProject } = useAppState()

const handleActivate = () => {
  loadProject(props.successScreenData.project_path)
  emit('close')
}
</script>

<template>
  <div class="flex-grow flex flex-col items-center justify-center p-8 space-y-6">
    <h2 class="text-3xl font-bold text-white">Project Created Successfully!</h2>
    <div class="text-gray-400 text-lg">Your new project is located at:</div>
    <div class="bg-cm-input-bg border border-gray-600 text-gray-300 px-6 py-3 rounded font-mono text-lg w-full max-w-2xl text-center">{{ successScreenData.project_path }}</div>
    <button @click="handleActivate" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-3 px-8 rounded shadow-md transition-colors mt-8 text-lg">Activate Project in CodeMerger</button>
  </div>
</template>