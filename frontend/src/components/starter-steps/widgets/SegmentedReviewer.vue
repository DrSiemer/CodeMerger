<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { HelpCircle, Check, X as XIcon, CheckCheck } from 'lucide-vue-next'
import MarkdownRenderer from '../../MarkdownRenderer.vue'
import ReviewerQuestions from '../ReviewerQuestions.vue'
import DiffViewer from '../../DiffViewer.vue'
import { useAppState } from '../../../composables/useAppState'

const props = defineProps({
  segments: Object,
  signoffs: Object,
  baselines: Object,
  orderedKeys: Array,
  friendlyNames: Object,
  questionsMap: Object,
  getQuestionPrompt: Function
})

const emit = defineEmits(['reset', 'rewrite', 'merge'])

const { editorFontSize, handleZoom, lockedIcon, unlockedIcon } = useAppState()

const activeSegmentKey = ref(null)
const reviewerEditMode = ref(false)
const showQuestions = ref(false)
const scrollRef = ref(null)

const acceptAllConfirm = ref(false)
let acceptAllTimer = null

onMounted(() => {
  if (props.orderedKeys.length) {
    const firstUnlocked = props.orderedKeys.find(k => !props.signoffs[k])
    activeSegmentKey.value = firstUnlocked || props.orderedKeys[0]
  }
})

onUnmounted(() => {
  if (acceptAllTimer) clearTimeout(acceptAllTimer)
})

watch(() => props.orderedKeys, (newKeys) => {
  if (newKeys.length > 0 && !newKeys.includes(activeSegmentKey.value)) {
    activeSegmentKey.value = newKeys[0]
  }
}, { deep: true })

watch(activeSegmentKey, () => {
  nextTick(() => { if (scrollRef.value) scrollRef.value.scrollTop = 0 })
})

const hasPendingDiffs = computed(() => {
  return Object.keys(props.baselines).some(k => k !== '__merged__' && props.baselines[k] !== undefined)
})

const renderSegmentTitle = (key) => props.friendlyNames[key] || key

const getPromptForCurrentSegment = async (question) => {
  return props.getQuestionPrompt(question, activeSegmentKey.value)
}

const toggleSignoff = (key) => {
  props.signoffs[key] = !props.signoffs[key]
  if (props.signoffs[key]) {
    if (activeSegmentKey.value === key) reviewerEditMode.value = false
    props.baselines[key] = undefined
  }
}

const handleSignoffAndNext = () => {
  const key = activeSegmentKey.value
  props.signoffs[key] = true
  props.baselines[key] = undefined

  const idx = props.orderedKeys.indexOf(key)
  for (let i = idx + 1; i < props.orderedKeys.length; i++) {
    if (!props.signoffs[props.orderedKeys[i]]) {
      activeSegmentKey.value = props.orderedKeys[i]; reviewerEditMode.value = false; return
    }
  }
  for (let i = 0; i < idx; i++) {
    if (!props.signoffs[props.orderedKeys[i]]) {
      activeSegmentKey.value = props.orderedKeys[i]; reviewerEditMode.value = false; return
    }
  }
  reviewerEditMode.value = false
}

const allSigned = computed(() => Object.values(props.signoffs).every(v => v === true))

const refuseDiff = () => {
  if (activeSegmentKey.value && props.baselines[activeSegmentKey.value]) {
    props.segments[activeSegmentKey.value] = props.baselines[activeSegmentKey.value]
    props.baselines[activeSegmentKey.value] = undefined
  }
}

const acceptDiff = () => {
  if (activeSegmentKey.value) props.baselines[activeSegmentKey.value] = undefined
}

const handleAcceptAllClick = () => {
  if (acceptAllConfirm.value) {
    for (const k in props.baselines) {
      if (k !== '__merged__') props.baselines[k] = undefined
    }
    acceptAllConfirm.value = false
    clearTimeout(acceptAllTimer)
  } else {
    acceptAllConfirm.value = true
    acceptAllTimer = setTimeout(() => { acceptAllConfirm.value = false }, 2500)
  }
}

const toggleReviewerEditMode = async (event = null, isContextual = false) => {
  let anchorText = ''
  let contentRatio = 0
  const isDoubleclick = isContextual && event

  const el = scrollRef.value
  if (el) {
    if (!reviewerEditMode.value) {
      if (isDoubleclick) {
        anchorText = window.getSelection().toString().trim().split('\n')[0].substring(0, 50)
      } else {
        const rect = el.getBoundingClientRect()
        const topEl = document.elementFromPoint(rect.left + 50, rect.top + 20)
        if (topEl) anchorText = topEl.innerText?.trim().split('\n')[0].substring(0, 40) || ''
      }
      contentRatio = el.scrollTop / el.scrollHeight
    } else {
      const text = el.value
      contentRatio = el.scrollTop / el.scrollHeight
      const targetCharIdx = Math.floor(text.length * contentRatio)
      anchorText = text.substring(targetCharIdx, targetCharIdx + 60).trim().split('\n')[0]
    }
  }

  reviewerEditMode.value = !reviewerEditMode.value
  await nextTick()

  setTimeout(() => {
    const newEl = scrollRef.value
    if (!newEl) return

    if (reviewerEditMode.value) {
      const fullText = newEl.value
      let foundIdx = -1

      if (anchorText) {
        const startSearch = Math.floor(fullText.length * contentRatio)
        foundIdx = fullText.indexOf(anchorText, Math.max(0, startSearch - 300))
        if (foundIdx === -1) foundIdx = fullText.indexOf(anchorText)
      }

      if (foundIdx !== -1) {
        const charRatio = foundIdx / fullText.length
        const offset = isDoubleclick ? 0.3 : 0.05
        newEl.focus({ preventScroll: true })
        newEl.setSelectionRange(foundIdx, foundIdx + anchorText.length)
        const setPos = () => { newEl.scrollTop = (charRatio * newEl.scrollHeight) - (newEl.clientHeight * offset) }
        setPos()
        requestAnimationFrame(setPos)
      } else {
        newEl.scrollTop = contentRatio * newEl.scrollHeight
      }
    } else {
      let scrolled = false
      if (anchorText) {
        const walker = document.createTreeWalker(newEl, NodeFilter.SHOW_TEXT, null, false)
        let node
        while ((node = walker.nextNode())) {
          if (node.textContent.includes(anchorText)) {
            node.parentElement.scrollIntoView({ block: 'start', behavior: 'instant' })
            newEl.scrollTop -= (newEl.clientHeight * 0.05)
            scrolled = true
            break
          }
        }
      }
      if (!scrolled) {
        newEl.scrollTop = contentRatio * newEl.scrollHeight
      }
    }
  }, 100)
}
</script>

<template>
  <div class="flex h-full min-h-0 text-gray-100" @wheel.ctrl.prevent="handleZoom">
    <div class="w-72 shrink-0 border-r border-gray-700 pr-4 overflow-y-auto space-y-2">
      <div class="p-2 mb-4 border-b border-gray-700 flex flex-col items-center space-y-3 pb-3">
        <button @click="$emit('reset')" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest">Start Over</button>
        <button
          v-if="hasPendingDiffs"
          @click="handleAcceptAllClick"
          class="transition-colors text-[10px] font-bold uppercase tracking-widest flex items-center px-3 py-1.5 rounded border select-none w-full justify-center"
          :class="acceptAllConfirm ? 'bg-cm-green text-white border-cm-green' : 'text-cm-green hover:text-green-400 bg-cm-green/10 border-cm-green/30 hover:bg-cm-green/20'"
        >
          <CheckCheck class="w-3.5 h-3.5 mr-1.5 shrink-0" />
          <span class="truncate">{{ acceptAllConfirm ? 'Click to confirm' : 'Accept All Diffs' }}</span>
        </button>
      </div>
      <div v-for="key in orderedKeys" :key="key"
           @click="activeSegmentKey = key; reviewerEditMode = false"
           class="p-3 rounded cursor-pointer border transition-all flex items-center justify-between group"
           :class="activeSegmentKey === key ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'">
        <div class="flex items-center space-x-2 truncate">
          <div v-if="baselines[key]" class="w-1.5 h-1.5 rounded-full bg-cm-green shrink-0"></div>
          <span class="truncate pr-2">{{ renderSegmentTitle(key) }}</span>
        </div>
        <button @click.stop="toggleSignoff(key)" class="shrink-0 opacity-70 hover:opacity-100 transition-opacity" :title="signoffs[key] ? 'Unlock' : 'Lock'">
          <img v-if="signoffs[key] && lockedIcon" :src="lockedIcon" class="h-4 w-auto object-contain" />
          <img v-else-if="!signoffs[key] && unlockedIcon" :src="unlockedIcon" class="h-4 w-auto object-contain" />
        </button>
      </div>
    </div>
    <div class="flex-grow pl-6 flex flex-col min-w-0" v-if="activeSegmentKey">
      <div class="flex justify-between items-center mb-4 shrink-0">
          <h3 class="text-xl font-bold text-white">{{ renderSegmentTitle(activeSegmentKey) }}</h3>
          <div class="flex space-x-2">
            <div v-if="baselines[activeSegmentKey] && !signoffs[activeSegmentKey]" class="flex space-x-2">
              <button @click="refuseDiff" class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1 bg-gray-700 text-red-400 hover:bg-red-900/40">
                <XIcon class="w-3 h-3" /><span>Refuse</span>
              </button>
              <button @click="acceptDiff" class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1 bg-cm-green text-white hover:brightness-110">
                <Check class="w-3 h-3" /><span>Accept Diff</span>
              </button>
            </div>

            <template v-if="!signoffs[activeSegmentKey] && !baselines[activeSegmentKey]">
              <button
                 @click="showQuestions = !showQuestions"
                 class="px-3 py-1 rounded text-xs font-bold shadow transition-colors flex items-center space-x-1"
                 :class="showQuestions ? 'bg-cm-blue text-white' : 'bg-gray-700 text-gray-300 hover:text-white'"
               >
                 <HelpCircle class="w-3 h-3" /><span>Questions</span>
               </button>
              <button @click="$emit('rewrite')" class="bg-cm-blue text-white px-3 py-1 rounded text-xs font-bold shadow transition-colors">Rewrite</button>
              <button @click="toggleReviewerEditMode(null, false)" class="bg-gray-700 text-white px-3 py-1 rounded text-xs shadow transition-colors">{{ reviewerEditMode ? 'Render' : 'Edit' }}</button>
            </template>
          </div>
      </div>

      <ReviewerQuestions
        v-if="showQuestions && !signoffs[activeSegmentKey]"
        :questions="questionsMap[activeSegmentKey]?.questions || []"
        :getPrompt="getPromptForCurrentSegment"
      />

      <div class="flex-grow border border-gray-700 rounded bg-cm-input-bg overflow-hidden">
          <textarea v-if="reviewerEditMode" ref="scrollRef" v-model="segments[activeSegmentKey]" class="w-full h-full bg-cm-input-bg text-white p-6 outline-none custom-scrollbar font-sans leading-relaxed selectable" :style="{ fontSize: editorFontSize + 'px' }"></textarea>
          <div v-else ref="scrollRef" class="w-full h-full overflow-y-auto p-6 custom-scrollbar">
            <DiffViewer v-if="baselines[activeSegmentKey]" :oldText="baselines[activeSegmentKey]" :newText="segments[activeSegmentKey]" :fontSize="editorFontSize" />
            <MarkdownRenderer v-else :content="segments[activeSegmentKey]" :fontSize="editorFontSize" @dblclick="!signoffs[activeSegmentKey] && toggleReviewerEditMode($event, true)" />
          </div>
      </div>
      <div class="shrink-0 pt-4 flex justify-end space-x-4">
          <button v-if="signoffs[activeSegmentKey]" @click="toggleSignoff(activeSegmentKey)" class="bg-cm-green hover:bg-green-600 text-white px-8 py-2 rounded font-bold shadow transition-colors">Unlock</button>
          <button v-else @click="handleSignoffAndNext" class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2 rounded font-bold shadow transition-colors">Lock & Next</button>
          <button v-if="allSigned" @click="$emit('merge')" class="bg-cm-blue hover:bg-blue-500 text-white px-8 py-2 rounded font-bold shadow transition-colors">Merge & Finalize</button>
      </div>
    </div>
  </div>
</template>