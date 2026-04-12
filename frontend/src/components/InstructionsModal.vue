<script setup>
import { ref, onMounted } from 'vue'
import { X, BookOpen, RotateCcw, Save } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'

const emit = defineEmits(['close'])
const { activeProject, config, saveInstructions, resizeWindow } = useAppState()

const localIntro = ref('')
const localOutro = ref('')

onMounted(async () => {
  // Grow window to provide a comfortable text area footprint
  await resizeWindow(800, 650)

  localIntro.value = activeProject.introText || ''
  localOutro.value = activeProject.outroText || ''
})

const loadDefaults = () => {
  const isCurrentlyEmpty = !localIntro.value.trim() && !localOutro.value.trim()

  if (isCurrentlyEmpty || confirm('This will replace your current instructions with the global defaults. Continue?')) {
    localIntro.value = config.value.default_intro_prompt || ''
    localOutro.value = config.value.default_outro_prompt || ''
  }
}

const handleSave = async () => {
  const success = await saveInstructions(localIntro.value, localOutro.value)
  if (success) {
    emit('close')
  }
}
</script>

<template>
  <div class="absolute inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
    <div class="bg-cm-dark-bg w-full max-w-[700px] h-[600px] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar shrink-0">
        <div class="flex items-center space-x-3 text-white">
          <BookOpen class="w-5 h-5 text-cm-blue" />
          <h2 class="text-xl font-bold">Set Instructions</h2>
          <span class="text-gray-500 text-sm font-medium">/ {{ activeProject.name }}</span>
        </div>
        <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors">
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Body -->
      <div class="flex-grow overflow-y-auto p-6 flex flex-col space-y-6 custom-scrollbar">

        <!-- Intro -->
        <div class="flex flex-col space-y-2">
          <div class="flex items-baseline space-x-2">
            <span class="text-white font-bold">Intro Instructions</span>
            <span class="text-gray-500 text-sm">(prepended to the final output)</span>
          </div>
          <textarea
            v-model="localIntro"
            class="flex-grow min-h-[140px] bg-cm-input-bg border border-gray-700 text-gray-200 p-3 rounded outline-none focus:border-cm-blue custom-scrollbar text-sm leading-relaxed font-sans selectable"
            placeholder="Introduce your project and goals here..."
          ></textarea>
        </div>

        <!-- Outro -->
        <div class="flex flex-col space-y-2">
          <div class="flex items-baseline space-x-2">
            <span class="text-white font-bold">Outro Instructions</span>
            <span class="text-gray-500 text-sm">(appended to the final output)</span>
          </div>
          <textarea
            v-model="localOutro"
            class="flex-grow min-h-[140px] bg-cm-input-bg border border-gray-700 text-gray-200 p-3 rounded outline-none focus:border-cm-blue custom-scrollbar text-sm leading-relaxed font-sans selectable"
            placeholder="Add style guidelines or recurring constraints here..."
          ></textarea>
        </div>

      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex items-center justify-between shrink-0">
        <button
          @click="loadDefaults"
          class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors text-sm font-medium"
          title="Wipe current fields and load global default prompts from Settings"
        >
          <RotateCcw class="w-4 h-4" />
          <span>Load Defaults</span>
        </button>

        <div class="flex items-center space-x-3">
          <button
            @click="emit('close')"
            class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-6 rounded transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            @click="handleSave"
            class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-2 px-10 rounded shadow-md transition-all flex items-center text-sm"
          >
            <Save class="w-4 h-4 mr-2" />
            Save and Close
          </button>
        </div>
      </div>

    </div>
  </div>
</template>