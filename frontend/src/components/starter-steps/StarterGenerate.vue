<script setup>
import { ref, computed } from 'vue'
import { Upload, Copy, Check, Sparkles } from 'lucide-vue-next'
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
  generateNameSuggestionsPrompt,
  createStarterProject,
  createStarterProjectOverwrite,
  selectDirectory,
  editorFontSize,
  handleZoom,
  copyText
} = useAppState()

const showPasteArea = ref(!!props.pData.generate_llm_response)
const isPathCopied = ref(false)
const isSuggestionsCopied = ref(false)

const isFolderValid = computed(() => {
  return props.pData.parent_folder && props.pData.parent_folder.trim() !== ''
})

const fullPathPreview = computed(() => {
  if (!props.pData.name || !props.pData.parent_folder) return ''

  // Mirror Python sanitize_project_name logic
  const sanitizedName = props.pData.name
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, '-')
    .replace(/^-+|-+$/g, '')

  const parent = props.pData.parent_folder.replace(/\//g, '\\')
  return `${parent}\\${sanitizedName}`
})

const copyToClipboard = async (text, el) => {
  if (!el) return
  await copyText(text)
  const originalText = el.innerText
  el.innerText = "Copied!"
  setTimeout(() => { if (el) el.innerText = originalText }, 2000)
}

const copyPathToClipboard = async () => {
  if (!fullPathPreview.value) return
  await copyText(fullPathPreview.value)
  isPathCopied.value = true
  setTimeout(() => { isPathCopied.value = false }, 2000)
}

const copyNameSuggestionsPrompt = async () => {
  const prompt = await generateNameSuggestionsPrompt(props.pData)
  if (prompt) {
    await copyText(prompt)
    isSuggestionsCopied.value = true
    setTimeout(() => { isSuggestionsCopied.value = false }, 2000)
  }
}

const browseParentFolder = async () => {
  const folder = await selectDirectory()
  if (folder) {
    const normalized = folder.replace(/\//g, '\\')
    props.pData.parent_folder = normalized
  }
}

const copyMasterPrompt = async (e) => {
  const btn = e.currentTarget
  if (!e.ctrlKey) {
    const prompt = await generateMasterPrompt(props.pData)
    await copyToClipboard(prompt, btn)
  }
  showPasteArea.value = true
}

const isGenerateReady = computed(() => {
  if (!props.pData.name.trim() || !props.pData.parent_folder || !props.pData.generate_llm_response) return false
  const content = props.pData.generate_llm_response
  if (!content.includes('--- File: ') || !content.includes('--- End of file ---')) return false
  if (!content.includes('<PITCH>') || !content.includes('</PITCH>')) return false
  return true
})

const createProject = async () => {
  const pitchMatch = props.pData.generate_llm_response.match(/<PITCH>(.*?)<\/PITCH>/i)
  const pitch = pitchMatch ? pitchMatch[1].trim() : "a new project"

  let res = await createStarterProject(props.pData.generate_llm_response, props.pData.include_base_reference, pitch)

  if (res?.status === 'EXISTS' && confirm("Project folder already exists. Overwrite?")) {
    res = await createStarterProjectOverwrite(props.pData.generate_llm_response, props.pData.include_base_reference, pitch)
  }

  if (res?.status === 'SUCCESS') {
    emit('projectCreated', res)
  } else if (res?.message) {
    alert(res.message)
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto w-full space-y-8 text-gray-100 flex flex-col flex-grow min-h-0" @wheel.ctrl.prevent="handleZoom">
    <h3 class="text-2xl font-bold text-white">Finalize and Generate</h3>
    <div class="bg-gray-800 p-8 rounded border border-gray-700 space-y-6 shadow-xl">

      <div class="space-y-3 border-b border-gray-700 pb-6" v-info="'starter_details_name'">
        <div class="flex items-center justify-between">
          <label class="block text-gray-300 font-bold text-sm uppercase">1. Project Name</label>
          <button
            @click="copyNameSuggestionsPrompt"
            class="flex items-center space-x-1.5 text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded border transition-all active:scale-95"
            :class="isSuggestionsCopied ? 'bg-cm-green text-white border-cm-green' : 'bg-gray-700 text-gray-400 border-gray-600 hover:text-white hover:border-gray-500'"
            title="Ask the AI for name suggestions based on your project context"
          >
            <Sparkles class="w-3 h-3" />
            <span>{{ isSuggestionsCopied ? 'Prompt Copied!' : 'Suggest Names' }}</span>
          </button>
        </div>
        <input v-model="pData.name" type="text" class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 focus:border-cm-blue outline-none text-lg" placeholder="Enter a name for your project...">
      </div>

      <div class="space-y-3 pt-2" v-info="'starter_gen_parent'">
        <label class="block text-gray-300 font-bold text-sm uppercase">2. Destination Folder</label>
        <div class="flex space-x-3">
          <input v-model="pData.parent_folder" type="text" class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-2 text-sm outline-none focus:border-cm-blue">
          <button @click="browseParentFolder" class="bg-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-600 font-bold">Browse</button>
        </div>

        <div
          v-if="fullPathPreview"
          class="bg-black/20 border border-cm-blue/20 rounded p-2 flex items-center justify-between group cursor-pointer hover:bg-black/30 transition-colors"
          @click="copyPathToClipboard"
          title="Click to copy full path"
        >
          <div class="flex flex-col min-w-0">
            <span class="text-[10px] text-gray-500 font-bold uppercase tracking-tight select-none">Full Project path (sanitized)</span>
            <span class="text-cm-blue text-xs font-mono truncate select-none">{{ fullPathPreview }}</span>
          </div>
          <div class="shrink-0 ml-4 opacity-40 group-hover:opacity-100 transition-opacity">
            <Check v-if="isPathCopied" class="w-4 h-4 text-cm-green" />
            <Copy v-else class="w-4 h-4 text-cm-blue" />
          </div>
        </div>
      </div>

      <div v-if="isFolderValid" class="pt-6 border-t border-gray-700 space-y-6">
        <div class="space-y-3">
          <label class="block text-gray-300 font-bold text-sm uppercase">3. Creation Prompt</label>
          <button @click="copyMasterPrompt" v-info="'starter_gen_prompt'" class="w-full bg-cm-blue text-white font-bold py-4 rounded text-lg shadow-lg hover:bg-blue-500 transition-colors">Copy Final Creation Prompt</button>
        </div>

        <div v-if="showPasteArea" class="pt-4 space-y-3 flex flex-col flex-grow min-h-[250px]">
          <label class="block text-gray-300 font-bold text-sm uppercase shrink-0">4. Paste the LLM Output</label>
          <textarea v-model="pData.generate_llm_response" v-info="'starter_gen_response'" class="w-full flex-grow min-h-[150px] bg-cm-input-bg border border-gray-700 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar font-mono" :style="{ fontSize: editorFontSize + 'px' }" placeholder="Paste generated code blocks here..."></textarea>
        </div>
      </div>
    </div>

    <div class="flex justify-end pt-4">
      <button @click="createProject" v-info="'starter_gen_create'" :disabled="!isGenerateReady" class="bg-cm-green hover:bg-green-600 disabled:bg-gray-700 disabled:opacity-50 text-white font-bold px-12 py-4 rounded-lg shadow-xl text-xl flex items-center transition-all active:scale-95">
        <Upload class="w-6 h-6 mr-3" />
        Create Project Files
      </button>
    </div>
  </div>
</template>