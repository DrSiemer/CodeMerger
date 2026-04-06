<script setup>
import { computed } from 'vue'
import { Upload } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  pData: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['projectCreated'])

const {
  generateMasterPrompt,
  createStarterProject,
  createStarterProjectOverwrite,
  selectDirectory,
  editorFontSize,
  handleZoom
} = useAppState()

const copyToClipboard = async (text, buttonEvent) => {
  await navigator.clipboard.writeText(text)
  const target = buttonEvent.target
  const originalText = target.innerText
  target.innerText = "Copied!"
  setTimeout(() => { target.innerText = originalText }, 2000)
}

const browseParentFolder = async () => {
  const folder = await selectDirectory()
  if (folder) {
    // Normalization logic
    const normalized = folder.replace(/\//g, '\\')
    props.pData.parent_folder = normalized
  }
}

const copyMasterPrompt = async (e) => {
  const prompt = await generateMasterPrompt(props.pData)
  await copyToClipboard(prompt, e)
}

const isGenerateReady = computed(() => {
  if (!props.pData.name || !props.pData.parent_folder || !props.pData.generate_llm_response) return false
  const content = props.pData.generate_llm_response
  if (!content.includes('--- File: ') || !content.includes('--- End of file ---')) return false
  if (!content.includes('<PITCH>') || !content.includes('</PITCH>')) return false
  return true
})

const createProject = async () => {
  const pitchMatch = props.pData.generate_llm_response.match(/<PITCH>(.*?)<\/PITCH>/i)
  const pitch = pitchMatch ? pitchMatch[1].trim() : "a new project"
  let res = await createStarterProject(props.pData.generate_llm_response, props.pData.include_base_reference, pitch, props.pData)

  if (res?.status === 'EXISTS' && confirm("Project folder already exists. Overwrite?")) {
    res = await createStarterProjectOverwrite(props.pData.generate_llm_response, props.pData.include_base_reference, pitch, props.pData)
  }

  if (res?.status === 'SUCCESS') {
    emit('projectCreated', res)
  } else if (res?.message) {
    alert(res.message)
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto w-full space-y-8 text-gray-100 pb-8" @wheel.ctrl.prevent="handleZoom">
    <h3 class="text-2xl font-bold text-white">Finalize & Generate</h3>
    <div class="bg-gray-800 p-8 rounded border border-gray-700 space-y-6">
      <div class="space-y-3">
        <label class="block text-gray-300 font-bold text-sm uppercase">1. Destination Folder</label>
        <div class="flex space-x-3">
          <input v-model="pData.parent_folder" type="text" class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-2 text-sm outline-none focus:border-cm-blue">
          <button @click="browseParentFolder" class="bg-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-600 font-bold">Browse</button>
        </div>
        <div v-if="pData.name && pData.parent_folder" class="text-cm-blue text-xs font-mono">Full path: {{ pData.parent_folder }}\{{ pData.name.replace(/\s+/g, '-') }}</div>
      </div>
      <div class="pt-6 border-t border-gray-700 flex flex-col space-y-4">
        <label class="block text-gray-300 font-bold text-sm uppercase">2. Creation Prompt</label>
        <button @click="copyMasterPrompt" class="bg-cm-blue text-white font-bold py-4 rounded text-lg shadow-lg hover:bg-blue-500 transition-colors">Copy Final Creation Prompt</button>
        <textarea v-model="pData.generate_llm_response" class="w-full h-48 bg-cm-input-bg border border-gray-700 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar" :style="{ fontSize: editorFontSize + 'px' }" placeholder="Paste generated code blocks here..."></textarea>
      </div>
    </div>
    <div class="flex justify-end mt-4">
      <button @click="createProject" :disabled="!isGenerateReady" class="bg-cm-green hover:bg-green-600 disabled:bg-gray-700 disabled:opacity-50 text-white font-bold px-12 py-4 rounded-lg shadow-xl text-xl flex items-center transition-all">
        <Upload class="w-6 h-6 mr-3" />
        Create Project Files
      </button>
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