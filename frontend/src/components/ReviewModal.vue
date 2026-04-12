<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  X, CheckCircle, FileCode, MessageSquare,
  HelpCircle, ShieldCheck, AlertTriangle,
  ChevronDown, ChevronRight, Eye, Undo2, BookOpen,
  ClipboardPaste
} from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import MarkdownRenderer from './MarkdownRenderer.vue'
import DiffViewer from './DiffViewer.vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'new' // 'new' (pasted) or 'resume' (orange button)
  }
})

const emit = defineEmits(['close'])
const {
  lastAiResponse,
  planFileStates,
  planOriginalContents,
  getFileContent,
  applyFileChange,
  deleteFile,
  copyAdmonishment,
  resizeWindow,
  processPaste,
  editorFontSize,
  hasPendingChanges,
  handleZoom
} = useAppState()

// State management
const visibleDiffs = ref(new Set()) // paths currently showing diff
const activeTab = ref('')
const showCommentary = ref(false)
const tabContentContainer = ref(null)

// Categorize segments from the plan into dedicated tab objects
const tabs = computed(() => {
  const list = []
  if (!lastAiResponse.value) return list

  const segments = lastAiResponse.value.ordered_segments || []

  segments.forEach(seg => {
    // Filter out segments with no content or just a placeholder dash
    const hasContent = seg.content && seg.content.trim() !== '' && seg.content.trim() !== '-'

    if (seg.type === 'tag') {
      if (seg.tag === 'INTRO' && hasContent) {
        list.push({ id: 'intro', name: 'Intro', icon: MessageSquare, content: seg.content, color: 'text-cyan-400' })
      } else if (seg.tag === 'ANSWERS TO DIRECT USER QUESTIONS' && hasContent) {
        list.push({ id: 'answers', name: 'Answers', icon: HelpCircle, content: seg.content, color: 'text-purple-400' })
      } else if (seg.tag === 'CHANGES') {
        // Changes tab is special: it's added if there is commentary OR if there are file updates
        list.push({ id: 'changes', name: 'Changes', icon: FileCode, content: seg.content, color: 'text-cm-blue' })
      } else if (seg.tag === 'VERIFICATION' && hasContent) {
        list.push({ id: 'verification', name: 'Verification', icon: ShieldCheck, content: seg.content, color: 'text-cm-green' })
      }
    } else if (seg.type === 'orphan' && hasContent) {
      list.push({ id: 'unformatted', name: 'Unformatted Output', icon: AlertTriangle, content: seg.content, color: 'text-yellow-500' })
    }
  })

  // Ensure 'Changes' is present if there are file updates/creations/deletions, even if the tag was missing
  if (!list.find(t => t.id === 'changes') && (hasUpdates.value || hasCreations.value || hasDeletions.value)) {
    list.push({ id: 'changes', name: 'Changes', icon: FileCode, content: '', color: 'text-cm-blue' })
  }

  return list
})

const hasUpdates = computed(() => Object.keys(lastAiResponse.value?.updates || {}).length > 0)
const hasCreations = computed(() => Object.keys(lastAiResponse.value?.creations || {}).length > 0)
const hasDeletions = computed(() => (lastAiResponse.value?.deletions_proposed || []).length > 0)

const hasUnformatted = computed(() => tabs.value.some(t => t.id === 'unformatted'))
const hasFormattingTags = computed(() => lastAiResponse.value?.has_any_tags)

onMounted(async () => {
  await resizeWindow(1100, 850)

  // Initialization: Logic for state-aware initial tab selection
  if (tabs.value.length > 0) {
    const tabIds = tabs.value.map(t => t.id)

    if (props.mode === 'resume') {
      // Priority 1: Unaccepted changes exist -> Changes Tab
      if (hasPendingChanges.value && tabIds.includes('changes')) {
        activeTab.value = 'changes'
      }
      // Priority 2: Re-opened after acceptance -> Verification Tab
      else if (tabIds.includes('verification')) {
        activeTab.value = 'verification'
      }
      // Fallback
      else {
        activeTab.value = tabIds[0]
      }
    } else {
      // Priority 1: Default for new responses -> Intro Tab
      if (tabIds.includes('intro')) {
        activeTab.value = 'intro'
      }
      // Priority 2: If no Intro but unformatted exists -> Unformatted
      else if (hasUnformatted.value && !hasFormattingTags.value) {
        activeTab.value = 'unformatted'
      }
      // Fallback
      else {
        activeTab.value = tabIds[0]
      }
    }
  }
})

// --- Logic Actions ---

const toggleDiff = async (path) => {
  if (visibleDiffs.value.has(path)) {
    visibleDiffs.value.delete(path)
  } else {
    // Lazy load original content for diffing
    if (planOriginalContents.value[path] === undefined) {
      planOriginalContents.value[path] = await getFileContent(path)
    }
    visibleDiffs.value.add(path)
  }
}

const acceptChange = async (path, type) => {
  if (type === 'delete') {
    if (planOriginalContents.value[path] === undefined) {
      planOriginalContents.value[path] = await getFileContent(path)
    }
    const success = await deleteFile(path)
    if (success) planFileStates.value[path] = 'deleted'
  } else {
    const content = lastAiResponse.value.updates[path] || lastAiResponse.value.creations[path]
    if (type === 'modify' && planOriginalContents.value[path] === undefined) {
      planOriginalContents.value[path] = await getFileContent(path)
    }
    const success = await applyFileChange(path, content)
    if (success) planFileStates.value[path] = 'applied'
  }
}

const discardChange = (path) => {
  planFileStates.value[path] = 'rejected'
}

const undoChange = async (path, type) => {
  if (planFileStates.value[path] === 'rejected') {
    planFileStates.value[path] = 'pending'
    return
  }

  const originalText = planOriginalContents.value[path]

  if (type === 'create') {
    const success = await deleteFile(path)
    if (success) planFileStates.value[path] = 'pending'
  } else if (type === 'modify') {
    if (originalText === undefined) return
    const success = await applyFileChange(path, originalText)
    if (success) planFileStates.value[path] = 'pending'
  } else if (type === 'delete') {
    if (originalText === undefined) return
    const success = await applyFileChange(path, originalText)
    if (success) planFileStates.value[path] = 'pending'
  }
}

const applyAllPending = async () => {
  const pending = Object.entries(planFileStates.value).filter(([p, s]) => s === 'pending')
  for (const [path, state] of pending) {
    let type = 'modify'
    if (lastAiResponse.value.creations[path]) type = 'create'
    else if (lastAiResponse.value.deletions_proposed.includes(path)) type = 'delete'

    await acceptChange(path, type)
  }

  // Activating the Verification tab automatically after batch apply
  if (tabs.value.find(t => t.id === 'verification')) {
    activeTab.value = 'verification'
  }
}

const handlePasteNext = async () => {
  const success = await processPaste()
  if (success) {
    visibleDiffs.value.clear()
    showCommentary.value = false

    // Reset tab to Intro if available, matching fresh paste behavior
    if (tabs.value.length > 0) {
      const hasIntro = tabs.value.find(t => t.id === 'intro')
      activeTab.value = hasIntro ? 'intro' : tabs.value[0].id
    }

    if (tabContentContainer.value) {
      tabContentContainer.value.scrollTop = 0
    }
  }
}

// --- Helpers ---

const getPendingCount = computed(() => {
  return Object.values(planFileStates.value).filter(s => s === 'pending').length
})

// Acceptance Label Logic: transitions from Apply All to Apply All Remaining as work progresses
const applyAllLabel = computed(() => {
  const states = Object.values(planFileStates.value)
  const totalProposed = states.filter(s => s !== 'skipped').length
  if (totalProposed === 1) return 'Apply'

  const hasInteracted = states.some(s => ['applied', 'rejected', 'deleted'].includes(s))
  return hasInteracted ? 'Apply All Remaining' : 'Apply All'
})

const getSkippedMessage = (path) => {
  const isDeletion = lastAiResponse.value?.deletions_proposed?.includes(path)
  return isDeletion ? 'Already deleted' : 'No changes'
}
</script>

<template>
  <div class="absolute inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
    <div class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[92vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar">
        <h2 class="text-xl font-bold text-white">AI Response Review</h2>
        <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors">
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Format Error Alert -->
      <div v-if="hasUnformatted && !hasFormattingTags" class="bg-[#3a1e1e] px-6 py-3 border-b border-red-900/30 flex items-center justify-between">
        <div class="flex items-center text-red-300 text-sm font-medium">
          <AlertTriangle class="w-5 h-5 mr-3 text-cm-warn" />
          This response was not properly wrapped in the requested XML tags.
        </div>
        <button
          @click="copyAdmonishment"
          class="bg-[#DE6808] hover:bg-orange-500 text-white text-xs font-bold py-1.5 px-4 rounded transition-colors"
        >
          Copy Correction Prompt
        </button>
      </div>

      <!-- Tabs Navigation -->
      <div class="flex bg-cm-top-bar border-b border-gray-700 px-4 shrink-0">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-5 py-3 text-sm font-medium transition-all border-b-2 flex items-center space-x-2"
          :class="activeTab === tab.id ? 'border-cm-blue text-white bg-white/5' : 'border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/5'"
        >
          <component :is="tab.icon" class="w-4 h-4" :class="tab.color" />
          <span>{{ tab.name }}</span>
        </button>
      </div>

      <!-- Scrollable Tab Content Container -->
      <div ref="tabContentContainer" class="flex-grow overflow-y-auto custom-scrollbar bg-cm-dark-bg" @wheel.ctrl.prevent="handleZoom">
        <div v-for="tab in tabs" :key="tab.id" v-show="activeTab === tab.id" class="p-8">

          <!-- Standard Content Tabs -->
          <template v-if="tab.id !== 'changes'">
            <MarkdownRenderer :content="tab.content" :fontSize="editorFontSize" />
          </template>

          <!-- Interactive Changes Tab -->
          <template v-else>
            <div class="space-y-8 max-w-5xl mx-auto">

              <!-- AI Commentary Expandable -->
              <div v-if="tab.content" class="border border-gray-700 rounded bg-[#1A1A1A] overflow-hidden">
                <button
                  @click="showCommentary = !showCommentary"
                  class="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
                >
                  <div class="flex items-center space-x-3">
                    <BookOpen class="w-4 h-4 text-cm-blue" />
                    <span class="text-sm font-bold text-gray-200 uppercase tracking-widest">AI Commentary</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-xs text-gray-500">{{ showCommentary ? 'Hide' : 'Show' }} details</span>
                    <ChevronDown v-if="showCommentary" class="w-4 h-4 text-gray-500" />
                    <ChevronRight v-else class="w-4 h-4 text-gray-500" />
                  </div>
                </button>
                <div v-if="showCommentary" class="p-4 border-t border-gray-700 bg-cm-dark-bg">
                  <MarkdownRenderer :content="tab.content" :fontSize="editorFontSize" />
                </div>
              </div>

              <!-- Updates -->
              <div v-if="hasUpdates">
                <div class="flex items-center space-x-4 mb-4">
                  <h4 class="text-xs font-bold text-cm-blue uppercase tracking-widest shrink-0">Modify Content</h4>
                  <div class="h-px bg-cm-blue/30 flex-grow"></div>
                </div>
                <div class="space-y-3">
                  <div v-for="(content, path) in lastAiResponse.updates" :key="path" class="border border-gray-700 rounded bg-cm-input-bg/30">
                    <div class="flex items-center justify-between p-3">
                      <div class="flex items-center space-x-3 min-w-0">
                        <span
                          class="font-mono text-sm truncate"
                          :class="['pending', 'skipped'].includes(planFileStates[path]) ? (planFileStates[path] === 'skipped' ? 'text-[#888888]' : 'text-gray-200') : 'text-gray-500 line-through'"
                        >{{ path }}</span>
                      </div>

                      <div class="flex items-center space-x-2 shrink-0">
                        <template v-if="planFileStates[path] === 'skipped'">
                          <span class="text-xs font-bold text-gray-500 px-3 py-1 bg-gray-800 rounded">{{ getSkippedMessage(path) }}</span>
                        </template>
                        <template v-else-if="planFileStates[path] === 'pending'">
                          <button @click="toggleDiff(path)" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors flex items-center">
                            <Eye class="w-3.5 h-3.5 mr-1.5" />
                            Diff
                          </button>
                          <button @click="acceptChange(path, 'modify')" class="text-xs font-bold bg-cm-green hover:bg-green-600 text-white px-3 py-1 rounded transition-colors">Accept</button>
                          <button @click="discardChange(path)" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors">Discard</button>
                        </template>
                        <button v-else @click="undoChange(path, 'modify')" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center">
                          <Undo2 class="w-3.5 h-3.5 mr-1.5" />
                          Undo
                        </button>
                      </div>
                    </div>
                    <div v-if="visibleDiffs.has(path)" class="p-3 pt-0">
                      <DiffViewer :old-text="planOriginalContents[path]" :new-text="content" :fontSize="editorFontSize" :filename="path" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Creations -->
              <div v-if="hasCreations">
                <div class="flex items-center space-x-4 mb-4">
                  <h4 class="text-xs font-bold text-cm-green uppercase tracking-widest shrink-0">Create New File</h4>
                  <div class="h-px bg-cm-green/30 flex-grow"></div>
                </div>
                <div class="space-y-3">
                  <div v-for="(content, path) in lastAiResponse.creations" :key="path" class="border border-gray-700 rounded bg-cm-input-bg/30">
                    <div class="flex items-center justify-between p-3">
                      <span class="font-mono text-sm text-gray-200" :class="{'text-gray-500 line-through': planFileStates[path] === 'applied'}">{{ path }}</span>
                      <div class="flex items-center space-x-2">
                        <template v-if="planFileStates[path] === 'pending'">
                          <button @click="toggleDiff(path)" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors">View</button>
                          <button @click="acceptChange(path, 'create')" class="text-xs font-bold bg-cm-green hover:bg-green-600 text-white px-3 py-1 rounded transition-colors">Accept</button>
                          <button @click="discardChange(path)" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors">Discard</button>
                        </template>
                        <button v-else @click="undoChange(path, 'create')" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center">
                          <Undo2 class="w-3.5 h-3.5 mr-1.5" />
                          Undo
                        </button>
                      </div>
                    </div>
                    <div v-if="visibleDiffs.has(path)" class="p-3 pt-0">
                      <DiffViewer :new-text="content" :fontSize="editorFontSize" :filename="path" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Deletions -->
              <div v-if="hasDeletions">
                <div class="flex items-center space-x-4 mb-4">
                  <h4 class="text-xs font-bold text-cm-warn uppercase tracking-widest shrink-0">Delete File</h4>
                  <div class="h-px bg-cm-warn/30 flex-grow"></div>
                </div>
                <div v-for="path in lastAiResponse.deletions_proposed" :key="path" class="border border-gray-700 rounded bg-cm-input-bg/30 mb-3">
                  <div class="p-3 flex items-center justify-between">
                    <span
                      class="font-mono text-sm truncate"
                      :class="['pending', 'skipped'].includes(planFileStates[path]) ? (planFileStates[path] === 'skipped' ? 'text-[#888888]' : 'text-gray-200') : 'text-gray-500 line-through'"
                    >{{ path }}</span>
                    <div class="flex items-center space-x-2">
                      <template v-if="planFileStates[path] === 'skipped'">
                        <span class="text-xs font-bold text-gray-500 px-3 py-1 bg-gray-800 rounded">{{ getSkippedMessage(path) }}</span>
                      </template>
                      <template v-else-if="planFileStates[path] === 'pending'">
                        <button @click="toggleDiff(path)" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors">View</button>
                        <button @click="acceptChange(path, 'delete')" class="text-xs font-bold bg-cm-warn hover:bg-red-500 text-white px-3 py-1 rounded transition-colors">Accept Delete</button>
                        <button @click="discardChange(path)" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors">Keep</button>
                      </template>
                      <button v-else @click="undoChange(path, 'delete')" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center">
                        <Undo2 class="w-3.5 h-3.5 mr-1.5" />
                        Undo
                      </button>
                    </div>
                  </div>
                  <div v-if="visibleDiffs.has(path)" class="p-3 pt-0">
                    <!-- For deletions, DiffViewer shows current content as 'removed' -->
                    <DiffViewer :old-text="planOriginalContents[path]" new-text="" :fontSize="editorFontSize" :filename="path" />
                  </div>
                </div>
              </div>

            </div>
          </template>

        </div>
      </div>

      <!-- Footer Actions -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-between shrink-0">
        <div class="flex items-center">
          <button
            v-if="getPendingCount === 0"
            @click="handlePasteNext"
            class="bg-cm-green hover:bg-green-600 text-white font-bold py-2 px-8 rounded shadow-md transition-all flex items-center"
          >
            <ClipboardPaste class="w-4 h-4 mr-2" />
            Paste Next
          </button>
        </div>
        <div class="flex items-center space-x-3">
          <button
            @click="emit('close')"
            class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-8 rounded transition-colors"
          >
            {{ getPendingCount === 0 ? 'Close' : 'Cancel' }}
          </button>
          <button
            v-if="getPendingCount > 0"
            @click="applyAllPending"
            class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-2 px-12 rounded shadow-md transition-all flex items-center"
          >
            <CheckCircle class="w-4 h-4 mr-2" />
            {{ applyAllLabel }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>