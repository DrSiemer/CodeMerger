<script setup>
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  pData: {
    type: Object,
    required: true
  }
})

const { generateStackPrompt } = useAppState()

const copyToClipboard = async (text, buttonEvent) => {
  await navigator.clipboard.writeText(text)
  const target = buttonEvent.target
  const originalText = target.innerText
  target.innerText = "Copied!"
  setTimeout(() => { target.innerText = originalText }, 2000)
}

const generateStack = async (e) => {
  const prompt = await generateStackPrompt(props.pData)
  await copyToClipboard(prompt, e)
}

const processStack = () => {
  const raw = props.pData.stack_llm_response
  try {
    const startIdx = raw.indexOf('[')
    const endIdx = raw.lastIndexOf(']')
    if (startIdx === -1 || endIdx === -1) throw new Error("No JSON")
    const jsonStr = raw.substring(startIdx, endIdx + 1).replace(/'/g, '"')
    const list = JSON.parse(jsonStr)
    props.pData.stack = list.join(', ')
    props.pData.stack_llm_response = ''
  } catch (err) {
    alert("Could not parse JSON list.")
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-6 w-full text-gray-100">
    <h3 class="text-2xl font-bold text-white">Tech Stack</h3>
    <textarea v-model="pData.stack_experience" class="w-full h-24 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar" placeholder="List your known languages, frameworks, and environment details..."></textarea>

    <div class="flex justify-between items-center bg-gray-800 p-4 rounded border border-gray-700 mt-4">
       <div class="text-gray-300"><span class="font-bold text-white">1.</span> Copy prompt for LLM</div>
       <button @click="generateStack" class="bg-cm-blue hover:bg-blue-500 text-white px-4 py-2 rounded shadow transition-colors font-bold">Copy Stack Prompt</button>
    </div>

    <div class="bg-gray-800 p-4 rounded border border-gray-700">
       <div class="text-gray-300 mb-2"><span class="font-bold text-white">2.</span> Paste LLM Response or Type Stack</div>
       <textarea v-model="pData.stack_llm_response" class="w-full h-24 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar" placeholder='["Vue", "Python"]'></textarea>
       <div class="flex justify-end mt-3">
         <button @click="processStack" :disabled="!pData.stack_llm_response" class="bg-cm-green hover:bg-green-600 text-white px-6 py-2 rounded shadow transition-colors disabled:opacity-50 font-bold">Process List</button>
       </div>
    </div>

    <div v-if="pData.stack" class="mt-8 p-4 border border-cm-blue rounded bg-cm-blue/10">
       <div class="font-bold text-white mb-2">Final Selected Stack:</div>
       <div class="text-cm-blue font-mono">{{ pData.stack }}</div>
    </div>
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