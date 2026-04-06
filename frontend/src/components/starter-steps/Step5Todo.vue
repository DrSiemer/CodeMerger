<script setup>
import { ref } from 'vue'
import { CheckCircle } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'
import MarkdownRenderer from '../MarkdownRenderer.vue'

const props = defineProps({
  pData: {
    type: Object,
    required: true
  },
  todoQuestionsMap: {
    type: Object,
    required: true
  }
})

const TODO_PHASES = {
    "setup": "Environment Setup",
    "database": "Database & Schema",
    "api": "API & Backend",
    "frontend": "Frontend & UI",
    "logic": "Core Logic & Actions",
    "polish": "Automation & Polish",
    "deployment": "Deployment"
}

const {
  generateTodoPrompt,
  parseStarterSegments,
  mapParsedSegmentsToKeys,
  assembleStarterDocument
} = useAppState()

const activeSegmentKey = ref(null)
const reviewerEditMode = ref(false)

const copyToClipboard = async (text, buttonEvent) => {
  await navigator.clipboard.writeText(text)
  const target = buttonEvent.target
  const originalText = target.innerText
  target.innerText = "Copied!"
  setTimeout(() => { target.innerText = originalText }, 2000)
}

const toggleSignoff = (key, dataRef) => dataRef[key] = !dataRef[key]

const handleSignoffAndNext = (key, signoffsRef, keysArray) => {
  signoffsRef[key] = true
  const idx = keysArray.indexOf(key)
  for (let i = idx + 1; i < keysArray.length; i++) {
    if (!signoffsRef[keysArray[i]]) {
      activeSegmentKey.value = keysArray[i]
      reviewerEditMode.value = false
      return
    }
  }
  for (let i = 0; i < idx; i++) {
    if (!signoffsRef[keysArray[i]]) {
      activeSegmentKey.value = keysArray[i]
      reviewerEditMode.value = false
      return
    }
  }
}

const allSigned = (signoffs) => Object.values(signoffs).every(v => v === true)

const generateTodo = async (e) => {
  const prompt = await generateTodoPrompt(props.pData, props.todoQuestionsMap)
  await copyToClipboard(prompt, e)
}

const processTodo = async () => {
  const content = props.pData.todo_llm_response
  const parsed = await parseStarterSegments(content)
  if (!parsed || !Object.keys(parsed).length) {
    props.pData.todo_md = content
    props.pData.todo_llm_response = ''
    return
  }

  const friendly = {}
  for (const k in props.todoQuestionsMap) friendly[k] = props.todoQuestionsMap[k].label || k

  const mapped = await mapParsedSegmentsToKeys(parsed, friendly)
  props.pData.todo_segments = mapped
  props.pData.todo_signoffs = {}
  Object.keys(props.pData.todo_segments).forEach(k => props.pData.todo_signoffs[k] = false)
  props.pData.todo_llm_response = ''

  const keys = Object.keys(mapped)
  if (keys.includes('deployment')) {
    keys.splice(keys.indexOf('deployment'), 1)
    keys.push('deployment')
  }
  activeSegmentKey.value = keys[0]
  reviewerEditMode.value = false
}

const mergeTodo = async () => {
  const friendly = {}
  for (const k in props.todoQuestionsMap) friendly[k] = props.todoQuestionsMap[k].label || k

  const keys = Object.keys(props.pData.todo_segments)
  if (keys.includes('deployment')) {
    keys.splice(keys.indexOf('deployment'), 1)
    keys.push('deployment')
  }

  const md = await assembleStarterDocument(props.pData.todo_segments, keys, friendly)
  props.pData.todo_md = md
  props.pData.todo_segments = {}
  props.pData.todo_signoffs = {}
  activeSegmentKey.value = null
}
</script>

<template>
  <div class="h-full flex flex-col">
    <template v-if="pData.todo_md">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-2xl font-bold text-white">Review TODO Plan</h3>
        <button @click="reviewerEditMode = !reviewerEditMode" class="bg-cm-blue text-white px-4 py-1.5 rounded font-bold text-sm">{{ reviewerEditMode ? 'Finish Editing' : 'Edit Markdown' }}</button>
      </div>
      <div class="flex-grow bg-cm-input-bg border border-gray-700 rounded overflow-hidden text-gray-100">
        <textarea v-if="reviewerEditMode" v-model="pData.todo_md" class="w-full h-full p-6 bg-cm-input-bg text-gray-100 font-mono outline-none"></textarea>
        <div v-else class="w-full h-full p-6 overflow-y-auto custom-scrollbar"><MarkdownRenderer :content="pData.todo_md" /></div>
      </div>
    </template>

    <template v-else-if="Object.keys(pData.todo_segments).length">
       <div class="flex h-full min-h-0 text-gray-100">
          <div class="w-64 border-r border-gray-700 pr-4 overflow-y-auto space-y-2">
            <div v-for="key in Object.keys(pData.todo_segments)" :key="key" @click="activeSegmentKey = key; reviewerEditMode = false" class="p-3 rounded cursor-pointer border transition-all" :class="activeSegmentKey === key ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'">
              {{ TODO_PHASES[key] || key }}
            </div>
          </div>
          <div class="flex-grow pl-6 flex flex-col min-w-0">
            <div class="flex justify-between items-center mb-4 shrink-0">
                <h3 class="text-xl font-bold text-white">{{ TODO_PHASES[activeSegmentKey] || activeSegmentKey }}</h3>
                <button @click="reviewerEditMode = !reviewerEditMode" class="bg-gray-700 text-white px-3 py-1 rounded text-xs">{{ reviewerEditMode ? 'Render' : 'Edit' }}</button>
            </div>
            <div class="flex-grow border border-gray-700 rounded bg-cm-input-bg overflow-hidden">
                <textarea v-if="reviewerEditMode" v-model="pData.todo_segments[activeSegmentKey]" class="w-full h-full bg-cm-input-bg text-white p-6 outline-none custom-scrollbar font-sans text-sm leading-relaxed"></textarea>
                <div v-else class="w-full h-full overflow-y-auto p-6 custom-scrollbar"><MarkdownRenderer :content="pData.todo_segments[activeSegmentKey]" /></div>
            </div>
            <div class="shrink-0 pt-4 flex justify-between">
                <button @click="toggleSignoff(activeSegmentKey, pData.todo_signoffs)" class="flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors">
                    <CheckCircle class="w-5 h-5" :class="pData.todo_signoffs[activeSegmentKey] ? 'text-cm-green' : 'text-gray-600'"/>
                    <span>{{ pData.todo_signoffs[activeSegmentKey] ? 'Locked' : 'Lock for Merge' }}</span>
                </button>
                <button v-if="allSigned(pData.todo_signoffs)" @click="mergeTodo" class="bg-cm-green text-white px-8 py-2 rounded font-bold shadow">Merge & Finalize</button>
                <button v-else @click="handleSignoffAndNext(activeSegmentKey, pData.todo_signoffs, Object.keys(pData.todo_segments))" class="bg-cm-blue text-white px-8 py-2 rounded font-bold shadow">Lock & Next</button>
            </div>
          </div>
        </div>
    </template>

    <template v-else>
      <div class="max-w-3xl mx-auto space-y-6 w-full text-gray-100">
        <h3 class="text-2xl font-bold text-white">Generate TODO Plan</h3>

        <div class="flex justify-between items-center bg-gray-800 p-4 rounded border border-gray-700 mt-4">
          <div class="text-gray-300"><span class="font-bold text-white">1.</span> Copy prompt for LLM</div>
          <button @click="generateTodo" class="bg-cm-blue hover:bg-blue-500 text-white px-4 py-2 rounded shadow transition-colors font-bold">Copy TODO Prompt</button>
        </div>

        <div class="bg-gray-800 p-4 rounded border border-gray-700">
          <div class="text-gray-300 mb-2"><span class="font-bold text-white">2.</span> Paste LLM Response (with tags)</div>
          <textarea v-model="pData.todo_llm_response" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue custom-scrollbar" placeholder="Paste response here..."></textarea>
          <div class="flex justify-end mt-3">
            <button @click="processTodo" :disabled="!pData.todo_llm_response" class="bg-cm-green hover:bg-green-600 text-white px-6 py-2 rounded shadow transition-colors disabled:opacity-50 font-bold">Process & Review</button>
          </div>
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