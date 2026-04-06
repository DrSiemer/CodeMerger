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
  conceptQuestionsMap: {
    type: Object,
    required: true
  }
})

const CONCEPT_ORDER = ["problem_statement", "core_principles", "key_features", "user_flows", "tech_constraints"]

const {
  generateConceptPrompt,
  parseStarterSegments,
  mapParsedSegmentsToKeys,
  assembleStarterDocument,
  editorFontSize,
  handleZoom
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

const renderSegmentTitle = (key, map) => {
  return map[key]?.label || map[key] || key
}

const toggleSignoff = (key, dataRef) => {
  dataRef[key] = !dataRef[key]
}

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

const allSigned = (signoffs) => {
  return Object.values(signoffs).every(v => v === true)
}

const generateConcept = async (e) => {
  const prompt = await generateConceptPrompt(props.pData, props.conceptQuestionsMap)
  await copyToClipboard(prompt, e)
}

const processConcept = async () => {
  const content = props.pData.concept_llm_response
  const parsed = await parseStarterSegments(content)
  if (!parsed || !Object.keys(parsed).length) {
    props.pData.concept_md = content
    props.pData.concept_llm_response = ''
    return
  }

  const friendly = {}
  for (const k in props.conceptQuestionsMap) friendly[k] = props.conceptQuestionsMap[k].label || k

  const mapped = await mapParsedSegmentsToKeys(parsed, friendly)
  props.pData.concept_segments = mapped
  props.pData.concept_signoffs = {}
  Object.keys(mapped).forEach(k => props.pData.concept_signoffs[k] = false)
  props.pData.concept_llm_response = ''
  activeSegmentKey.value = Object.keys(mapped)[0]
  reviewerEditMode.value = false
}

const mergeConcept = async () => {
  const friendly = {}
  for (const k in props.conceptQuestionsMap) friendly[k] = props.conceptQuestionsMap[k].label || k
  const md = await assembleStarterDocument(props.pData.concept_segments, CONCEPT_ORDER, friendly)
  props.pData.concept_md = md
  props.pData.concept_segments = {}
  props.pData.concept_signoffs = {}
  activeSegmentKey.value = null
}
</script>

<template>
  <div class="h-full flex flex-col" @wheel.ctrl.prevent="handleZoom">
    <template v-if="pData.concept_md">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-2xl font-bold text-white">Review Concept</h3>
        <button @click="reviewerEditMode = !reviewerEditMode" class="bg-cm-blue text-white px-4 py-1.5 rounded font-bold text-sm">{{ reviewerEditMode ? 'Finish Editing' : 'Edit Markdown' }}</button>
      </div>
      <div class="flex-grow bg-cm-input-bg border border-gray-700 rounded overflow-hidden">
        <textarea v-if="reviewerEditMode" v-model="pData.concept_md" class="w-full h-full p-6 bg-cm-input-bg text-gray-100 font-mono outline-none" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
        <div v-else class="w-full h-full p-6 overflow-y-auto custom-scrollbar"><MarkdownRenderer :content="pData.concept_md" :fontSize="editorFontSize" /></div>
      </div>
    </template>
    <template v-else-if="Object.keys(pData.concept_segments).length">
       <div class="flex h-full min-h-0">
         <div class="w-64 border-r border-gray-700 pr-4 overflow-y-auto space-y-2">
           <div v-for="key in Object.keys(pData.concept_segments)" :key="key" @click="activeSegmentKey = key; reviewerEditMode = false" class="p-3 rounded cursor-pointer border transition-all" :class="activeSegmentKey === key ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'">
             {{ renderSegmentTitle(key, conceptQuestionsMap) }}
           </div>
         </div>
         <div class="flex-grow pl-6 flex flex-col">
           <div class="flex justify-between items-center mb-4">
               <h3 class="text-xl font-bold text-white">{{ renderSegmentTitle(activeSegmentKey, conceptQuestionsMap) }}</h3>
               <button @click="reviewerEditMode = !reviewerEditMode" class="bg-gray-700 text-white px-3 py-1 rounded text-xs">{{ reviewerEditMode ? 'Render' : 'Edit' }}</button>
           </div>
           <div class="flex-grow border border-gray-700 rounded bg-cm-input-bg overflow-hidden">
               <textarea v-if="reviewerEditMode" v-model="pData.concept_segments[activeSegmentKey]" class="w-full h-full bg-cm-input-bg text-white p-6 outline-none custom-scrollbar font-sans leading-relaxed" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
               <div v-else class="w-full h-full overflow-y-auto p-6 custom-scrollbar"><MarkdownRenderer :content="pData.concept_segments[activeSegmentKey]" :fontSize="editorFontSize" /></div>
           </div>
           <div class="shrink-0 pt-4 flex justify-between">
               <button @click="toggleSignoff(activeSegmentKey, pData.concept_signoffs)" class="flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors">
                   <CheckCircle class="w-5 h-5" :class="pData.concept_signoffs[activeSegmentKey] ? 'text-cm-green' : 'text-gray-600'"/>
                   <span>{{ pData.concept_signoffs[activeSegmentKey] ? 'Locked' : 'Lock for Merge' }}</span>
               </button>
               <button v-if="allSigned(pData.concept_signoffs)" @click="mergeConcept" class="bg-cm-green text-white px-8 py-2 rounded font-bold shadow">Merge & Finalize</button>
               <button v-else @click="handleSignoffAndNext(activeSegmentKey, pData.concept_signoffs, Object.keys(pData.concept_segments))" class="bg-cm-blue text-white px-8 py-2 rounded font-bold shadow">Lock & Next</button>
           </div>
         </div>
       </div>
    </template>
    <template v-else>
      <div class="max-w-3xl mx-auto w-full space-y-6">
        <h3 class="text-2xl font-bold text-white">Project Concept</h3>
        <p class="text-gray-400">Describe what you want to build in a few sentences. The LLM will use this to generate the core sections.</p>
        <textarea v-model="pData.goal" class="w-full h-40 bg-cm-input-bg border border-gray-600 text-white rounded p-4 outline-none focus:border-cm-blue" :style="{ fontSize: editorFontSize + 'px' }" placeholder="e.g. A desktop tool that bundles project code..."></textarea>
        <div class="bg-gray-800 p-6 rounded border border-gray-700 space-y-4">
          <button @click="generateConcept" class="w-full bg-cm-blue text-white font-bold py-3 rounded">1. Copy Prompt for LLM</button>
          <textarea v-model="pData.concept_llm_response" class="w-full h-40 bg-cm-input-bg border border-gray-700 text-white rounded p-4 outline-none focus:border-cm-blue" :style="{ fontSize: editorFontSize + 'px' }" placeholder="Paste LLM response here..."></textarea>
          <button @click="processConcept" :disabled="!pData.concept_llm_response" class="w-full bg-cm-green text-white font-bold py-3 rounded disabled:opacity-50">2. Process & Review</button>
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