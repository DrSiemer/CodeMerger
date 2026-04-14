<script setup>
import { onMounted, onUnmounted } from 'vue'
import { X, AlertTriangle, Copy } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'

const props = defineProps({
  message: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])
const { statusMessage, copyAdmonishment } = useAppState()

const handleEscape = (e) => {
  if (e.key === 'Escape') emit('close')
}

const copyCorrectionPrompt = async () => {
  await copyAdmonishment()
  emit('close')
}

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <div id="format-error-modal" class="absolute inset-0 bg-black/90 flex items-center justify-center z-[100] p-6">
    <div class="bg-cm-dark-bg w-full max-w-[700px] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar">
        <div class="flex items-center text-cm-warn space-x-2">
          <AlertTriangle class="w-5 h-5" />
          <h2 class="text-lg font-bold">Format Error</h2>
        </div>
        <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors" title="Close error dialog">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6">
        <p class="text-gray-300 text-sm font-bold mb-3 uppercase tracking-tight">Validation Details:</p>
        <div class="bg-black/30 border border-gray-800 rounded p-4 max-h-[300px] overflow-y-auto custom-scrollbar">
          <p class="text-gray-200 text-xs font-mono leading-relaxed whitespace-pre-wrap">
            {{ message }}
          </p>
        </div>
        <p class="mt-4 text-gray-500 text-xs italic">
          The response from the LLM is invalid or could not be parsed. Copy the correction prompt below to ask the model to re-output the response correctly.
        </p>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end space-x-3">
        <button
          @click="emit('close')"
          class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-6 rounded transition-colors text-sm"
          title="Dismiss the error message"
        >
          Close
        </button>
        <button
          id="btn-format-error-copy"
          @click="copyCorrectionPrompt"
          class="bg-[#DE6808] hover:bg-orange-500 text-white font-bold py-2 px-6 rounded shadow-md transition-all text-sm flex items-center"
          title="Copy the formatting correction prompt for the LLM"
        >
          <Copy class="w-4 h-4 mr-2" />
          Copy Correction Prompt
        </button>
      </div>
    </div>
  </div>
</template>