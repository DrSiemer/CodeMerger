<script setup>
import { useAppState } from '../../../composables/useAppState'

const props = defineProps({
  pData: Object
})

const emit = defineEmits(['processed', 'back', 'generate'])

const { editorFontSize } = useAppState()

const processStack = () => {
  const raw = props.pData.stack_llm_response
  try {
    const startIdx = raw.indexOf('[')
    const endIdx = raw.lastIndexOf(']')
    if (startIdx === -1 || endIdx === -1) throw new Error("JSON array markers ([ ]) not found.")

    const jsonStr = raw.substring(startIdx, endIdx + 1)
    const list = JSON.parse(jsonStr)

    if (!Array.isArray(list)) throw new Error("The content is not a list/array.")

    props.pData.stack = list.map(item => {
      if (typeof item === 'string') {
        return {
          tech: item,
          rationale: 'Suggested by AI during initial scan.',
          warning: '',
          isManual: false
        }
      }
      return {
        tech: item.tech || 'Unnamed Subject',
        rationale: item.rationale || '',
        warning: item.warning || '',
        isManual: false
      }
    })

    props.pData.stack_llm_response = ''
    emit('processed')
  } catch (err) {
    alert(`Could not parse the technology stack.\n\nError: ${err.message}\n\nPlease ensure the LLM provided a valid JSON array of objects.`)
  }
}
</script>

<template>
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
        @click="$emit('generate', $event)"
        v-info="'starter_stack_gen'"
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
        v-info="'starter_gen_response'"
        class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-6 outline-none focus:border-cm-blue custom-scrollbar font-mono text-base selectable"
        :style="{ fontSize: editorFontSize + 'px' }"
        placeholder='Example response: [{"tech": "Node.js", "rationale": "High concurrency...", "warning": "..."}]'
      ></textarea>
    </div>

    <div class="shrink-0 flex items-center justify-between pt-2">
      <button @click="$emit('back')" class="text-gray-500 hover:text-gray-300 font-bold text-sm">Back to Experience</button>
      <button
        @click="processStack"
        v-info="'starter_gen_process'"
        :disabled="!pData.stack_llm_response.trim()"
        class="bg-cm-green hover:bg-green-600 text-white px-10 py-3 rounded shadow-lg transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Process & Review Stack
      </button>
    </div>
  </div>
</template>