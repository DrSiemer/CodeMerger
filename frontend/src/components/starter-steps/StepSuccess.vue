<script setup>
import { computed } from 'vue'
import { FolderOpen } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  successScreenData: {
    type: Object,
    required: true
  }
})
const emit = defineEmits(['close'])

const { loadProject, openPath } = useAppState()

const handleActivate = () => {
  loadProject(props.successScreenData.project_path)
  emit('close')
}

const handleOpenFolder = async () => {
  await openPath(props.successScreenData.project_path)
}

const buttonFontColor = computed(() => {
  const hex = props.successScreenData.project_color
  if (!hex) return '#FFFFFF'

  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)

  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b)
  return luminance > 150 ? '#000000' : '#FFFFFF'
})
</script>

<template>
  <div class="flex-grow flex flex-col items-center justify-center p-8 space-y-6">
    <h2 class="text-3xl font-bold text-white">Project Created Successfully!</h2>
    <div class="text-gray-400 text-lg">Your new project is located at:</div>

    <div class="flex items-center space-x-3 w-full max-w-2xl" v-info="'starter_success_path'">
      <div class="bg-cm-input-bg border border-gray-600 text-gray-300 px-6 py-3 rounded font-mono text-lg flex-grow text-center overflow-hidden truncate">
        {{ successScreenData.project_path }}
      </div>
      <button
        @click="handleOpenFolder"
        v-info="'starter_success_open'"
        class="bg-gray-700 hover:bg-gray-600 p-3.5 rounded border border-gray-600 transition-colors shrink-0"
        title="Open in File Explorer"
      >
        <FolderOpen class="w-6 h-6 text-white" />
      </button>
    </div>

    <div class="flex flex-col items-center space-y-4 pt-8 w-full">
      <button
        @click="handleActivate"
        v-info="'starter_success_activate'"
        class="hover:brightness-110 text-white font-bold py-4 px-12 rounded shadow-xl transition-all text-xl flex items-center"
        :style="{
          backgroundColor: successScreenData.project_color || '#0078D4',
          color: buttonFontColor
        }"
      >
        Activate Project in CodeMerger
      </button>

      <button
        @click="emit('close')"
        v-info="'starter_success_exit'"
        class="text-gray-500 hover:text-white font-bold text-sm uppercase tracking-widest transition-colors"
      >
        Exit
      </button>
    </div>
  </div>
</template>