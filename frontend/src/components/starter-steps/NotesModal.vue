<script setup>
import MarkdownRenderer from '../MarkdownRenderer.vue'

const props = defineProps({
  notes: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])
</script>

<template>
  <div class="fixed inset-0 bg-black/60 flex items-center justify-center z-[70] p-4">
    <div class="bg-cm-dark-bg w-full max-w-[600px] max-h-[80vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">

      <div class="px-6 py-4 border-b border-gray-700 bg-cm-top-bar shrink-0">
        <h2 class="text-xl font-bold text-white">Change Summary & Explanation</h2>
      </div>

      <div class="flex-grow overflow-y-auto p-6 custom-scrollbar bg-cm-input-bg">
        <MarkdownRenderer :content="notes" :fontSize="14" />
      </div>

      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end shrink-0">
        <button @click="emit('close')" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-2 px-8 rounded transition-colors text-sm shadow">Got it</button>
      </div>

    </div>
  </div>
</template>