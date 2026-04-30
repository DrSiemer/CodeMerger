<script setup>
import { ChevronRight, Save, RotateCcw } from 'lucide-vue-next'
import { useAppState } from '../../../composables/useAppState'

const props = defineProps({
  pData: Object
})

const emit = defineEmits(['generate'])

const { config, saveConfig, editorFontSize, copyText } = useAppState()

const loadDefaultExperience = () => {
  const defaultExp = config.value.user_experience || ''
  if (!defaultExp) {
    alert("No default experience has been saved yet.")
    return
  }

  if (props.pData.stack_experience.trim() && !confirm("This will overwrite your current input with your saved default experience. Continue?")) {
    return
  }

  props.pData.stack_experience = defaultExp
}

const saveDefaultExperience = async () => {
  const currentExp = props.pData.stack_experience.trim()

  if (!currentExp && !confirm("You are about to save an empty string as your default. This will clear your saved experience profile. Continue?")) {
    return
  }

  const newConfig = { ...config.value, user_experience: currentExp }
  await saveConfig(newConfig)
}
</script>

<template>
  <div class="flex flex-col h-full space-y-4">
    <div class="shrink-0">
      <h3 class="text-2xl font-bold text-white">Your Experience & Environment</h3>
      <p class="text-gray-400 mt-1">List your known languages, frameworks, and environment details. This context helps the LLM suggest a compatible stack.</p>
    </div>

    <textarea
      v-model="pData.stack_experience"
      v-info="'starter_stack_exp'"
      class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-6 outline-none focus:border-cm-blue custom-scrollbar text-lg leading-relaxed selectable"
      :style="{ fontSize: editorFontSize + 'px' }"
      placeholder="e.g. I am a senior Python developer comfortable with Flask. I use Windows 11 and want to build a lightweight desktop app..."
    ></textarea>

    <div class="shrink-0 flex items-center justify-between bg-gray-800/50 p-4 rounded border border-gray-700">
      <div class="flex items-center space-x-3 text-sm">
        <button
          v-if="pData.stack_experience !== (config.user_experience || '')"
          @click="loadDefaultExperience"
          class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded hover:bg-gray-700 font-bold"
          title="Load saved experience from settings"
        >
          <RotateCcw class="w-4 h-4" />
          <span>Load Default</span>
        </button>
        <button
          v-if="pData.stack_experience !== (config.user_experience || '')"
          @click="saveDefaultExperience"
          class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded hover:bg-gray-700 font-bold"
          title="Save current text as your app-wide default"
        >
          <Save class="w-4 h-4" />
          <span>Save as Default</span>
        </button>
      </div>

      <button
        @click="$emit('generate', $event)"
        v-info="'starter_stack_gen'"
        class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2.5 rounded shadow-lg transition-all font-bold flex items-center"
      >
        Copy Stack Prompt
        <ChevronRight class="w-4 h-4 ml-2" />
      </button>
    </div>
  </div>
</template>