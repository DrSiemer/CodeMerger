<script setup>
import { ref, computed, nextTick } from 'vue'
import {
  ChevronRight, Save, RotateCcw, Plus, Trash2,
  ChevronDown, ChevronUp, PencilLine,
  ChevronDownSquare, ChevronUpSquare
} from 'lucide-vue-next'
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

const { config, saveConfig, generateStackPrompt, editorFontSize, handleZoom, copyText } = useAppState()

// Sub-states: 'input' | 'pasting' | 'review'
const viewState = ref((Array.isArray(props.pData.stack) && props.pData.stack.length > 0) ? 'review' : (props.pData.stack_llm_response ? 'pasting' : 'input'))

const expandedIndices = ref(new Set())
const editingNameIndex = ref(null)
const nameInputRef = ref(null)

const toggleExpand = (idx) => {
  // Manual items or items without rationale are not expandable
  if (!props.pData.stack[idx].rationale) return

  if (expandedIndices.value.has(idx)) expandedIndices.value.delete(idx)
  else expandedIndices.value.add(idx)
}

const startEditingName = (idx) => {
  editingNameIndex.value = idx
  nextTick(() => {
    if (nameInputRef.value && nameInputRef.value[0]) {
      nameInputRef.value[0].focus()
      nameInputRef.value[0].select()
    }
  })
}

const stopEditingName = () => {
  editingNameIndex.value = null
}

const isAllExpanded = computed(() => {
  const expandable = props.pData.stack.filter(item => !!item.rationale)
  if (expandable.length === 0) return false
  return expandable.every(item => {
    const idx = props.pData.stack.indexOf(item)
    return expandedIndices.value.has(idx)
  })
})

const toggleAll = () => {
  if (isAllExpanded.value) {
    expandedIndices.value.clear()
  } else {
    props.pData.stack.forEach((item, idx) => {
      if (item.rationale) expandedIndices.value.add(idx)
    })
  }
}

// Deletion Confirmation State
const showConfirmDelete = ref(false)
const deleteTargetIndex = ref(null)

// --- Deletion Flow ---

const requestDelete = (idx) => {
  deleteTargetIndex.value = idx
  showConfirmDelete.value = true
}

const abortDelete = () => {
  deleteTargetIndex.value = null
  showConfirmDelete.value = false
}

const confirmDelete = () => {
  if (deleteTargetIndex.value !== null) {
    props.pData.stack.splice(deleteTargetIndex.value, 1)
    expandedIndices.value.delete(deleteTargetIndex.value)
  }
  abortDelete()
}

const deleteTarget = computed(() => {
  if (deleteTargetIndex.value === null) return null
  return props.pData.stack[deleteTargetIndex.value]
})

const hasVisibleWarning = computed(() => {
  const t = deleteTarget.value
  if (!t || t.isManual || !t.warning) return false
  // Filter out common generic placeholders
  const low = t.warning.toLowerCase()
  return !(low.includes('manually added') || low.trim() === '');
})

// --- Logic & Processing ---

const copyToClipboard = async (text, el) => {
  if (!el) return
  await copyText(text)
  const originalText = el.innerText
  el.innerText = "Copied!"
  setTimeout(() => { if (el) el.innerText = originalText }, 2000)
}

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

  const newConfig = { ...config.value, user_experience: currentExp }
  await saveConfig(newConfig)
}

const goToPasting = async (e) => {
  const btn = e.currentTarget
  if (!e.ctrlKey) {
    const prompt = await generateStackPrompt(props.pData)
    await copyToClipboard(prompt, btn)
  }
  viewState.value = 'pasting'
}

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
    viewState.value = 'review'
  } catch (err) {
    alert(`Could not parse the technology stack.\n\nError: ${err.message}\n\nPlease ensure the LLM provided a valid JSON array of objects.`)
  }
}

const addManualSubject = () => {
  const newIdx = props.pData.stack.length
  props.pData.stack.push({
    tech: '',
    rationale: '',
    warning: '',
    isManual: true
  })
  startEditingName(newIdx)
}

const handleReset = () => {
  if (confirm("Reset tech stack selection and return to input?")) {
    props.pData.stack = []
    props.pData.stack_llm_response = ''
    expandedIndices.value.clear()
    viewState.value = 'input'
  }
}
</script>

<template>
  <div class="h-full flex flex-col text-gray-100 relative" @wheel.ctrl.prevent="handleZoom">

    <!-- DELETION CONFIRM MODAL -->
    <Teleport to="#project-starter-modal">
      <div v-if="showConfirmDelete" class="absolute inset-0 bg-black/85 flex items-center justify-center z-[110] p-4">
        <div class="bg-cm-dark-bg w-full max-w-lg rounded-xl shadow-2xl border border-gray-700 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          <div class="bg-cm-top-bar px-6 py-5 border-b border-gray-700 flex items-center space-x-3">
             <Trash2 class="w-5 h-5 text-gray-400" />
             <h3 class="text-xl font-bold text-white">Remove Subject?</h3>
          </div>

          <div class="p-8 space-y-6">
            <p class="text-gray-200 text-lg leading-snug">Are you sure you want to remove <span class="font-black text-cm-blue">{{ deleteTarget?.tech || 'this item' }}</span> from the project stack?</p>

            <div v-if="hasVisibleWarning" class="bg-black/30 border border-gray-800 rounded-lg p-5">
               <span class="block text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] mb-2">Architectural Warning</span>
               <p v-info="'starter_stack_delete_warning'" class="text-gray-300 leading-relaxed">{{ deleteTarget?.warning }}</p>
            </div>
          </div>

          <div class="px-6 py-5 bg-cm-top-bar border-t border-gray-800 flex justify-end space-x-3">
            <button @click="abortDelete" class="px-6 py-2 rounded font-bold text-gray-400 hover:text-white transition-colors">Cancel</button>
            <button @click="confirmDelete" class="bg-cm-warn hover:bg-red-600 text-white font-bold px-10 py-2 rounded shadow-lg transition-all">Remove</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- PHASE 1: EXPERIENCE INPUT -->
    <template v-if="viewState === 'input'">
      <div class="flex flex-col h-full space-y-4">
        <div class="shrink-0">
          <h3 class="text-2xl font-bold text-white">Your Experience & Environment</h3>
          <p class="text-gray-400 mt-1">List your known languages, frameworks, and environment details. This context helps the LLM suggest a compatible stack.</p>
        </div>

        <textarea
          v-model="pData.stack_experience"
          v-info="'starter_stack_exp'"
          class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded p-6 outline-none focus:border-cm-blue custom-scrollbar text-lg leading-relaxed selectable"
          :style="{ fontSize: editorFontSize + 'px' }"
          placeholder="e.g. I am a senior Python developer comfortable with Flask. I use Windows 11 and want to build a lightweight desktop app..."
        ></textarea>

        <div class="shrink-0 flex items-center justify-between bg-gray-800/50 p-4 rounded border border-gray-700">
          <div class="flex items-center space-x-3 text-sm">
            <button
              v-if="pData.stack_experience !== (config.user_experience || '')"
              @click="loadDefaultExperience"
              class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded hover:bg-gray-700 font-bold"
              title="Load saved experience from settings"
            >
              <RotateCcw class="w-4 h-4" />
              <span>Load Default</span>
            </button>
            <button
              v-if="pData.stack_experience !== (config.user_experience || '')"
              @click="saveDefaultExperience"
              class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded hover:bg-gray-700 font-bold"
              title="Save current text as your app-wide default"
            >
              <Save class="w-4 h-4" />
              <span>Save as Default</span>
            </button>
          </div>

          <button
            @click="goToPasting"
            v-info="'starter_stack_gen'"
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
          <button @click="viewState = 'input'" class="text-gray-500 hover:text-gray-300 font-bold text-sm">Back to Experience</button>
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

    <!-- PHASE 3: REVIEW & EDIT -->
    <template v-else-if="viewState === 'review'">
      <div class="flex flex-col h-full space-y-4">
        <div class="shrink-0 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-bold text-white">Selected Code Stack</h3>
            <p class="text-gray-400 mt-1">Review the chosen technologies. Click a subject to reveal its architectural rationale.</p>
          </div>
          <button @click="handleReset" v-info="'starter_nav_reset'" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest">Start Over</button>
        </div>

        <div v-if="pData.stack.some(i => !!i.rationale)" class="flex justify-end items-center shrink-0">
          <button
            @click="toggleAll"
            class="text-[10px] font-bold text-gray-500 hover:text-white flex items-center space-x-2 transition-colors uppercase tracking-widest"
            :title="isAllExpanded ? 'Collapse all rationales' : 'Expand all rationales'"
          >
            <component :is="isAllExpanded ? ChevronUpSquare : ChevronDownSquare" class="w-3.5 h-3.5" />
            <span>{{ isAllExpanded ? 'Collapse All' : 'Expand All' }}</span>
          </button>
        </div>

        <div class="flex-grow overflow-y-auto custom-scrollbar space-y-2 pr-2" v-info="'starter_stack_edit'">
          <div v-for="(item, idx) in pData.stack" :key="idx" class="border border-gray-700 rounded-lg overflow-hidden transition-all duration-200">
            <!-- Header Row -->
            <div
              class="flex items-center justify-between p-4 cursor-pointer transition-colors group"
              :class="[
                expandedIndices.has(idx) ? 'bg-cm-blue/10' : 'bg-gray-800/40 hover:bg-gray-800/60',
                !item.rationale ? 'cursor-default' : 'cursor-pointer'
              ]"
              @click="toggleExpand(idx)"
              v-info="'starter_stack_item'"
            >
              <div class="flex items-center space-x-4 min-w-0 flex-grow">
                 <component
                   v-if="item.rationale"
                   :is="expandedIndices.has(idx) ? ChevronUp : ChevronDown"
                   class="w-5 h-5 text-gray-500 shrink-0"
                 />
                 <div v-else class="w-5 h-5 shrink-0"></div>

                 <div class="flex-grow min-w-0 flex items-center">
                    <input
                      v-if="editingNameIndex === idx"
                      ref="nameInputRef"
                      v-model="item.tech"
                      @click.stop
                      @blur="stopEditingName"
                      @keyup.enter="stopEditingName"
                      v-info="'starter_stack_edit_name'"
                      class="bg-black/30 border border-cm-blue text-white font-bold text-lg py-1 px-2 rounded w-full outline-none"
                      placeholder="Technology Name"
                    >
                    <div v-else class="flex items-center space-x-2 truncate">
                      <span class="text-white font-bold text-lg truncate">{{ item.tech || '(unnamed)' }}</span>
                      <button
                        @click.stop="startEditingName(idx)"
                        v-info="'starter_stack_edit_name'"
                        class="text-gray-500 hover:text-white p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Edit name"
                      >
                        <PencilLine class="w-4 h-4" />
                      </button>
                    </div>
                 </div>
              </div>

              <button @click.stop="requestDelete(idx)" v-info="'starter_stack_delete'" class="ml-4 text-gray-600 hover:text-red-400 transition-colors p-2 shrink-0">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>

            <!-- Expanded Content -->
            <div v-if="expandedIndices.has(idx) && item.rationale" class="bg-black/20 p-6 border-t border-gray-700/50 animate-in slide-in-from-top-1 duration-200">
              <div class="space-y-3">
                <span class="block text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">Technical Rationale</span>
                <p v-info="'starter_stack_rationale'" class="text-gray-200 text-[15px] leading-relaxed whitespace-pre-wrap">{{ item.rationale }}</p>
              </div>
            </div>
          </div>

          <!-- Add Button -->
          <button @click="addManualSubject" v-info="'starter_stack_add'" class="w-full py-3 border border-dashed border-gray-700 rounded-lg text-gray-500 hover:text-gray-300 hover:border-gray-500 transition-all flex items-center justify-center space-x-2 bg-black/10">
            <Plus class="w-4 h-4" />
            <span class="font-bold text-sm">Add Subject</span>
          </button>
        </div>

        <div v-if="!isLookingBack" class="shrink-0 pt-6 flex justify-end">
          <button @click="$emit('next')" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-3 px-12 rounded shadow-lg transition-all flex items-center group">
            Next Step: System Design
            <ChevronRight class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </template>

  </div>
</template>

<style scoped>
/* Standardize font scaling for plain text previews */
p {
  font-family: inherit;
}
</style>