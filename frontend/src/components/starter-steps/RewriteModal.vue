<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { X, Copy } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  contextData: {
    type: Object,
    required: true
  },
  isMergedMode: {
    type: Boolean,
    default: false
  },
  // If true, the parent will have already placed the compiled prompt on the clipboard
  isPivotMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'apply'])
const { getStarterRewritePrompt } = useAppState()

const modalRef = ref(null)
const instruction = ref('')
const response = ref('')

const posX = ref(0)
const posY = ref(0)
let isDragging = false
let startMouseX = 0
let startMouseY = 0
let startPosX = 0
let startPosY = 0

const isCopyDisabled = computed(() => !instruction.value.trim())

onMounted(async () => {
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
  window.addEventListener('resize', clampToWindow)

  await nextTick()
  if (modalRef.value) {
    const rect = modalRef.value.getBoundingClientRect()
    const parent = document.getElementById('project-starter-modal')

    // Centering logic relative to the full Project Starter view (Teleport destination)
    if (parent) {
      posX.value = (parent.clientWidth - rect.width) / 2
      posY.value = (parent.clientHeight - rect.height) / 2
    } else {
      posX.value = (window.innerWidth - rect.width) / 2
      posY.value = (window.innerHeight - rect.height) / 2
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
  window.removeEventListener('resize', clampToWindow)
})

// Dragging Logic
const startDrag = (e) => {
  if (e.target.closest('button')) return

  isDragging = true
  startMouseX = e.clientX
  startMouseY = e.clientY
  startPosX = posX.value
  startPosY = posY.value

  e.preventDefault()
}

const onMouseMove = (e) => {
  if (!isDragging || !modalRef.value) return

  const deltaX = e.clientX - startMouseX
  const deltaY = e.clientY - startMouseY

  posX.value = startPosX + deltaX
  posY.value = startPosY + deltaY

  clampToWindow()
}

const onMouseUp = () => {
  isDragging = false
}

const clampToWindow = () => {
  if (!modalRef.value) return

  const rect = modalRef.value.getBoundingClientRect()
  const parent = document.getElementById('project-starter-modal')
  if (!parent) return

  if (posX.value < 0) {
    posX.value = 0
  } else if (posX.value + rect.width > parent.clientWidth) {
    posX.value = parent.clientWidth - rect.width
  }

  if (posY.value < 0) {
    posY.value = 0
  } else if (posY.value + rect.height > parent.clientHeight) {
    posY.value = parent.clientHeight - rect.height
  }
}

const generateAndCopy = async (e) => {
  const { keys, names, data, signoffs } = props.contextData
  const targets = []
  const references = []

  if (!props.isMergedMode) {
    for (const k of keys) {
      if (signoffs[k]) {
        references.push(k)
      } else {
        targets.push(k)
      }
    }

    if (targets.length === 0) {
      alert("All segments are signed off. Nothing to rewrite.")
      return
    }
  }

  const target = e.target

  if (!e.ctrlKey) {
    const prompt = await getStarterRewritePrompt(
      instruction.value.trim(),
      targets,
      references,
      names,
      data,
      props.isMergedMode
    )

    await navigator.clipboard.writeText(prompt)
  }
  const originalText = target.innerText
  target.innerText = "Copied!"
  target.classList.add("bg-cm-green", "text-white")
  target.classList.remove("bg-gray-600", "hover:bg-gray-500")

  setTimeout(() => {
    target.innerText = originalText
    target.classList.remove("bg-cm-green", "text-white")
    target.classList.add("bg-gray-600", "hover:bg-gray-500")
  }, 2000)
}

const applyChanges = () => {
  const raw = response.value.trim()
  if (!raw) return

  const notesMatch = raw.match(/<NOTES>([\s\S]*?)<\/NOTES>/i)
  const notes = notesMatch ? notesMatch[1].trim() : ""

  const cleanContent = raw.replace(/<NOTES>[\s\S]*?<\/NOTES>/i, "").trim()

  emit('apply', { cleanContent, notes })
}
</script>

<template>
  <Teleport to="#starter-teleport-anchor">
    <div class="fixed inset-0 bg-black/70 z-[100] pointer-events-auto">
      <div
        ref="modalRef"
        class="bg-cm-dark-bg w-[700px] h-[85%] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden absolute"
        :style="{ left: posX + 'px', top: posY + 'px' }"
      >

        <!-- Draggable Header -->
        <div
          @mousedown="startDrag"
          class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar shrink-0 cursor-move select-none"
        >
          <div class="min-w-0">
            <h2 class="text-xl font-bold text-white pointer-events-none truncate">
              {{ isPivotMode ? 'Apply Architectural Pivot' : (isMergedMode ? 'Rewrite Document' : 'Rewrite Unsigned Segments') }}
            </h2>
            <p class="text-gray-400 text-sm mt-1 pointer-events-none">
              {{ isPivotMode ? 'Apply the LLM response to complete the pivot.' : 'Provide an instruction to modify the content.' }}
            </p>
          </div>
          <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors shrink-0">
            <X class="w-6 h-6" />
          </button>
        </div>

        <div class="flex-grow overflow-y-auto p-6 flex flex-col space-y-6 custom-scrollbar">

          <!-- Pivot Alert (Bypasses Step 1) -->
          <div v-if="isPivotMode" class="bg-cm-blue/10 border border-cm-blue/30 rounded p-4 flex items-center space-x-3 text-blue-100">
             <Copy class="w-5 h-5 text-cm-blue shrink-0" />
             <div class="text-sm leading-relaxed">
               <span class="font-bold text-cm-blue">Pivot Prompt Copied!</span>
               Paste the generated prompt into your LLM, then paste its response below to orchestrate the architectural pivot across your project drafts.
             </div>
          </div>

          <!-- Instruction Section (Hidden in Pivot Mode) -->
          <div v-if="!isPivotMode" class="space-y-2 shrink-0">
            <label class="text-white font-bold">1. Your Instruction</label>
            <textarea
              v-model="instruction"
              v-info="'rewrite_instruction'"
              class="w-full h-24 bg-cm-input-bg border border-gray-700 text-gray-200 p-3 rounded outline-none focus:border-cm-blue custom-scrollbar text-sm"
              placeholder="e.g., Make the tone more professional, or change the primary user entity from Projects to Tasks..."
            ></textarea>
            <div class="flex justify-end pt-2">
              <button
                @click="generateAndCopy"
                :disabled="isCopyDisabled"
                v-info="'rewrite_copy_prompt'"
                class="bg-gray-600 hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-2 rounded text-sm font-bold transition-colors"
              >Generate & Copy Prompt</button>
            </div>
          </div>

          <!-- Response Section -->
          <div class="space-y-2 flex-grow flex flex-col min-h-[200px]">
            <label class="text-white font-bold">{{ isPivotMode ? 'Paste LLM Response' : '2. Paste LLM Response' }}</label>
            <textarea
              v-model="response"
              v-info="'rewrite_response'"
              class="flex-grow min-h-[150px] bg-cm-input-bg border border-gray-700 text-gray-200 p-3 rounded outline-none focus:border-cm-blue custom-scrollbar text-sm"
              placeholder="Paste the LLM's updated segments or document here..."
            ></textarea>
          </div>

        </div>

        <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end shrink-0">
          <button v-info="'rewrite_cancel'" @click="emit('close')" class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-6 rounded transition-colors text-sm mr-3">Cancel</button>
          <button @click="applyChanges" v-info="'rewrite_apply'" :disabled="!response.trim()" class="bg-cm-blue hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2 px-8 rounded transition-colors text-sm">Apply Changes</button>
        </div>

      </div>
    </div>
  </Teleport>
</template>