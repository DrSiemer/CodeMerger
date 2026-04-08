<script setup>
import { ref, computed } from 'vue'
import { ChevronRight, Save, RotateCcw } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

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

const { config, saveConfig, generateStackPrompt, editorFontSize, handleZoom } = useAppState()

// Sub-states: 'input' | 'pasting' | 'review'
const viewState = ref(props.pData.stack ? 'review' : (props.pData.stack_llm_response ? 'pasting' : 'input'))

/**
 * Robust copy helper that handles async text generation and UI feedback.
 */
const copyToClipboard = async (text, el) => {
  if (!el) return
  await navigator.clipboard.writeText(text)
  const originalText = el.innerText
  el.innerText = "Copied!"
  setTimeout(() => { if (el) el.innerText = originalText }, 2000)
}

// --- Default Experience Management ---

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

  // Update global config via API
  const newConfig = { ...config.value, user_experience: currentExp }
  await saveConfig(newConfig)
}

// --- Navigation & Processing ---

const goToPasting = async (e) => {
  const btn = e.currentTarget // Capture immediately
  const prompt = await generateStackPrompt(props.pData)
  await copyToClipboard(prompt, btn)
  viewState.value = 'pasting'
}

const processStack = () => {
  const raw = props.pData.stack_llm_response
  try {
    const startIdx = raw.indexOf('[')
    const endIdx = raw.lastIndexOf(']')
    if (startIdx === -1 || endIdx === -1) throw new Error("No JSON")
    const jsonStr = raw.substring(startIdx, endIdx + 1).replace(/'/g, '"')
    const list = JSON.parse(jsonStr)
    // PRESENTATION: Join with newlines for the editor instead of commas
    props.pData.stack = list.join('\n')
    props.pData.stack_llm_response = ''
    viewState.value = 'review'
  } catch (err) {
    alert("Could not parse JSON list. Please ensure the LLM returned a valid array format.")
  }
}

const handleReset = () => {
  if (confirm("Reset tech stack selection and return to input?")) {
    props.pData.stack = ''
    props.pData.stack_llm_response = ''
    viewState.value = 'input'
  }
}
</script>

<template>
  <div class="h-full flex flex-col text-gray-100" @wheel.ctrl.prevent="handleZoom">

    <!-- PHASE 1: EXPERIENCE INPUT -->
    <template v-if="viewState === 'input'">
      <div class="flex flex-col h-full space-y-4">
        <div class="shrink-0">
          <h3 class="text-2xl font-bold text-white">Your Experience & Environment</h3>
          <p class="text-gray-400 mt-1">List your known languages, frameworks, and environment details. This context helps the LLM suggest a compatible stack.</p>
        </div>

        <textarea
          v-model="pData.stack_experience"
          class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-6 outline-none focus:border-cm-blue custom-scrollbar text-lg leading-relaxed selectable"
          :style="{ fontSize: editorFontSize + 'px' }"
          placeholder="e.g. I am a senior Python developer comfortable with Flask. I use Windows 11 and want to build a lightweight desktop app..."
        ></textarea>

        <div class="shrink-0 flex items-center justify-between bg-gray-800/50 p-4 rounded border border-gray-700">
          <div class="flex items-center space-x-3">
            <button
              @click="loadDefaultExperience"
              class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded hover:bg-gray-700 text-sm font-bold"
              title="Load saved experience from settings"
            >
              <RotateCcw class="w-4 h-4" />
              <span>Load Default</span>
            </button>
            <button
              @click="saveDefaultExperience"
              class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded hover:bg-gray-700 text-sm font-bold"
              title="Save current text as your app-wide default"
            >
              <Save class="w-4 h-4" />
              <span>Save as Default</span>
            </button>
          </div>

          <button
            @click="goToPasting"
            class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2.5 rounded shadow-lg transition-all font-bold flex items-center"
          >
            Copy Stack Prompt
            <ChevronRight class="w-4 h-4 ml-2" />
          </button>
        </div>
      </div>
    </template>

    <!-- PHASE 2: PASTE RESPONSE -->
    <template v-else-if="viewState === 'pasting'">
      <div class="flex flex-col h-full space-y-4">
        <div class="shrink-0">
          <h3 class="text-2xl font-bold text-white">Generate Stack</h3>
          <p class="text-gray-400 mt-1">Paste the JSON recommendation from the LLM below to extract your code stack.</p>
        </div>

        <div class="shrink-0 flex items-center justify-between bg-cm-blue/10 border border-cm-blue/30 p-4 rounded text-sm">
          <div class="flex items-center space-x-3 text-blue-100">
            <span class="font-bold text-cm-blue">Step 1:</span>
            <span>Paste the prompt into your LLM and copy its JSON response.</span>
          </div>
          <button
            @click="goToPasting"
            class="bg-cm-blue hover:bg-blue-500 text-white px-4 py-1.5 rounded text-xs font-bold transition-colors"
          >
            Re-copy Prompt
          </button>
        </div>

        <div class="flex flex-col flex-grow min-h-0">
          <div class="flex items-center space-x-2 text-gray-200 font-bold mb-2 text-sm">
            <span class="text-cm-blue">Step 2:</span>
            <span>Paste LLM Response</span>
          </div>
          <textarea
            v-model="pData.stack_llm_response"
            class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-6 outline-none focus:border-cm-blue custom-scrollbar font-mono text-base selectable"
            :style="{ fontSize: editorFontSize + 'px' }"
            placeholder='Example response: ["Python 3.10", "FastAPI", "SQLite"]'
          ></textarea>
        </div>

        <div class="shrink-0 flex items-center justify-between pt-2">
          <button @click="viewState = 'input'" class="text-gray-500 hover:text-gray-300 font-bold text-sm">Back to Experience</button>
          <button
            @click="processStack"
            :disabled="!pData.stack_llm_response.trim()"
            class="bg-cm-green hover:bg-green-600 text-white px-10 py-3 rounded shadow-lg transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Process & Review Stack
          </button>
        </div>
      </div>
    </template>

    <!-- PHASE 3: REVIEW & EDIT -->
    <template v-else-if="viewState === 'review'">
      <div class="flex flex-col h-full space-y-4">
        <div class="shrink-0 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-bold text-white">Final Code Stack</h3>
            <p class="text-gray-400 mt-1">Review and manually adjust the technologies. Use one line per subject.</p>
          </div>
          <button @click="handleReset" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest">Start Over</button>
        </div>

        <textarea
          v-model="pData.stack"
          class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-6 outline-none focus:border-cm-blue custom-scrollbar text-xl font-mono leading-relaxed selectable shrink-0"
          :style="{ fontSize: editorFontSize + 'px' }"
          placeholder="Python 3.10&#10;FastAPI&#10;Tailwind CSS"
        ></textarea>

        <div v-if="!isLookingBack" class="shrink-0 pt-6 flex justify-end">
          <button @click="$emit('next')" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-3 px-12 rounded shadow-lg transition-all flex items-center group">
            Next Step: TODO Plan
            <ChevronRight class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </template>

  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>