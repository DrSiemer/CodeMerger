<script setup>
import { ref, watch, nextTick } from 'vue'
import { Network, Copy, Check, AlertTriangle, RefreshCw } from 'lucide-vue-next'

const props = defineProps({
  mode: String, // 'init' | 'updating'
  parseError: String
})

const emit = defineEmits(['copy-prompt', 'parse', 'cancel', 'copy-correction'])

const promptResponse = ref('')
const isPromptCopied = ref(false)
const errorBlockRef = ref(null)

watch(() => props.parseError, (newVal) => {
  if (newVal) {
    nextTick(() => {
      setTimeout(() => {
        if (errorBlockRef.value) {
          errorBlockRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 50);
    });
  }
})

const handleCopy = () => {
  emit('copy-prompt')
  isPromptCopied.value = true
  setTimeout(() => { isPromptCopied.value = false }, 2000)
}
</script>

<template>
  <div class="flex-grow flex flex-col items-center p-12 max-w-2xl mx-auto space-y-8 overflow-y-auto custom-scrollbar">
    <div class="text-center space-y-4">
      <h3 class="text-2xl font-bold text-white">
        {{ mode === 'init' ? 'Initialize Architectural View' : 'Update Architectural View' }}
      </h3>
      <p class="text-gray-400 leading-relaxed">
        {{ mode === 'init'
          ? 'This tool organizes your Merge List into a semantic map. To begin, ask an LLM to categorize your files into structural layers.'
          : 'Your merge list has changed. Pass the latest context to the LLM to update the map while preserving your existing structure.'
        }}
      </p>
    </div>

    <div class="w-full space-y-6 bg-gray-800/50 p-8 rounded-xl border border-gray-700">
      <!-- Error Block -->
      <div v-if="parseError" ref="errorBlockRef" class="w-full bg-red-900/30 border border-red-700 p-4 rounded-xl space-y-3">
        <div class="flex items-center space-x-2 text-red-400 font-bold">
          <AlertTriangle class="w-5 h-5" />
          <span>Validation Error</span>
        </div>
        <div class="text-sm text-gray-300 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto custom-scrollbar">
          {{ parseError }}
        </div>
        <button
          @click="emit('copy-correction')"
          class="bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-4 rounded text-sm transition-colors flex items-center shadow-lg"
        >
          <Copy class="w-4 h-4 mr-2" /> Copy Correction Prompt
        </button>
      </div>

      <!-- Copy Prompt Button -->
      <button
        @click="handleCopy"
        v-info="'viz_init_copy'"
        class="w-full py-4 rounded-lg font-bold text-lg transition-all flex items-center justify-center space-x-3 shadow-lg"
        :class="isPromptCopied ? 'bg-cm-green text-white' : 'bg-cm-blue hover:bg-blue-500 text-white'"
      >
        <Check v-if="isPromptCopied" class="w-6 h-6" />
        <Copy v-else class="w-6 h-6" />
        <span>{{ isPromptCopied ? "Prompt Copied!" : (mode === 'init' ? "1. Copy Generation Prompt" : "1. Copy Update Prompt") }}</span>
      </button>

      <!-- Paste Area -->
      <div class="space-y-2" v-info="'viz_init_paste'">
        <label class="text-sm font-bold text-gray-300 uppercase tracking-widest">
          2. Paste {{ mode === 'updating' ? 'Updated ' : '' }}LLM Response (JSON)
        </label>
        <textarea
          v-model="promptResponse"
          class="w-full h-40 bg-cm-input-bg border border-gray-600 text-gray-200 p-4 rounded outline-none focus:border-cm-blue custom-scrollbar font-mono text-xs"
          :placeholder="`Paste the ${mode === 'updating' ? 'updated ' : ''}JSON response here...`"
        ></textarea>
      </div>

      <!-- Action Footer -->
      <div class="flex space-x-3">
        <button
          v-if="mode === 'updating'"
          @click="emit('cancel')"
          class="w-1/3 py-3 bg-gray-600 hover:bg-gray-500 text-white font-bold rounded shadow transition-all"
        >
          Cancel
        </button>
        <button
          @click="emit('parse', promptResponse)"
          v-info="'viz_init_visualize'"
          :disabled="!promptResponse.trim()"
          class="flex-grow py-3 bg-cm-green hover:bg-green-600 disabled:opacity-30 text-white font-bold rounded shadow transition-all flex items-center justify-center space-x-2"
        >
          <Network v-if="mode === 'init'" class="w-4 h-4" />
          <RefreshCw v-else class="w-4 h-4" />
          <span>{{ mode === 'init' ? 'Visualize Hierarchy' : 'Update Map' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>