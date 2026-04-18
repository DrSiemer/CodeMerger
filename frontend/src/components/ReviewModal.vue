<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  X, CheckCircle, FileCode, MessageSquare,
  HelpCircle, ShieldCheck, AlertTriangle,
  ClipboardPaste
} from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { useEscapeKey } from '../composables/useEscapeKey'
import MarkdownRenderer from './MarkdownRenderer.vue'
import ReviewChangesTab from './review-tabs/ReviewChangesTab.vue'

// default is 'new' (pasted) or 'resume' (orange button)
const props = defineProps({
  mode: {
    type: String,
    default: 'new'
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
  handleZoom,
  statusMessage
} = useAppState()

const visibleDiffs = ref(new Set())
const activeTab = ref('')
const tabContentContainer = ref(null)

const hasUpdates = computed(() => Object.keys(lastAiResponse.value?.updates || {}).length > 0)
const hasCreations = computed(() => Object.keys(lastAiResponse.value?.creations || {}).length > 0)
const hasDeletions = computed(() => (lastAiResponse.value?.deletions_proposed || []).length > 0)

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
        list.push({ id: 'intro', name: 'Intro', icon: MessageSquare, content: seg.content, color: 'text-cyan-400', tooltip: 'Review technical plan and summary' })
      } else if (seg.tag === 'ANSWERS TO DIRECT USER QUESTIONS' && hasContent) {
        list.push({ id: 'answers', name: 'Answers', icon: HelpCircle, content: seg.content, color: 'text-purple-400', tooltip: 'Review answers to your specific questions' })
      } else if (seg.tag === 'CHANGES') {
        // Changes tab is special: it's added if there is commentary OR if there are file updates
        list.push({ id: 'changes', name: 'Changes', icon: FileCode, content: seg.content, color: 'text-cm-blue', tooltip: 'Review and apply file modifications' })
      } else if (seg.tag === 'VERIFICATION' && hasContent) {
        list.push({ id: 'verification', name: 'Verification', icon: ShieldCheck, content: seg.content, color: 'text-cm-green', tooltip: 'Read verification steps and tests' })
      }
    } else if (seg.type === 'orphan' && hasContent) {
      list.push({ id: 'unformatted', name: 'Unformatted Output', icon: AlertTriangle, content: seg.content, color: 'text-yellow-500', tooltip: 'AI commentary that failed tag formatting' })
    }
  })

  // Ensure 'Changes' is present if there are file updates/creations/deletions, even if the tag was missing
  if (!list.find(t => t.id === 'changes') && (hasUpdates.value || hasCreations.value || hasDeletions.value)) {
    list.push({ id: 'changes', name: 'Changes', icon: FileCode, content: '', color: 'text-cm-blue', tooltip: 'Review and apply file modifications' })
  }

  return list
})

const hasUnformatted = computed(() => tabs.value.some(t => t.id === 'unformatted'))
const hasFormattingTags = computed(() => lastAiResponse.value?.has_any_tags)

useEscapeKey(() => {
  if (getPendingCount.value > 0) {
    if (confirm('You have pending changes in the review. Discard them?')) emit('close')
  } else {
    emit('close')
  }
})

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

const allReviewPaths = computed(() => {
  const response = lastAiResponse.value
  if (!response) return []
  return [
    ...Object.keys(response.updates || {}),
    ...Object.keys(response.creations || {}),
    ...(response.deletions_proposed || [])
  ]
})

const expandablePaths = computed(() => {
  return allReviewPaths.value.filter(p => planFileStates.value[p] === 'pending')
})

const isAllExpanded = computed(() => {
  const paths = expandablePaths.value
  if (paths.length === 0) return visibleDiffs.value.size > 0
  return paths.every(p => visibleDiffs.value.has(p))
})

const toggleAllDiffs = async () => {
  if (isAllExpanded.value) {
    visibleDiffs.value.clear()
  } else {
    const paths = expandablePaths.value
    if (paths.length === 0) return
    const missingPaths = paths.filter(p => planOriginalContents.value[p] === undefined)
    if (missingPaths.length > 0) {
      statusMessage.value = `Loading ${missingPaths.length} file(s)...`
      try {
        await Promise.all(missingPaths.map(async (path) => {
          planOriginalContents.value[path] = await getFileContent(path)
        }))
      } finally {
        statusMessage.value = ''
      }
    }
    paths.forEach(p => visibleDiffs.value.add(p))
  }
}

const acceptChange = async (path, type) => {
  if (type === 'delete') {
    if (planOriginalContents.value[path] === undefined) {
      planOriginalContents.value[path] = await getFileContent(path)
    }
    const success = await deleteFile(path)
    if (success) {
      planFileStates.value[path] = 'deleted'
      visibleDiffs.value.delete(path)
    }
  } else {
    const content = lastAiResponse.value.updates[path] || lastAiResponse.value.creations[path]
    if (type === 'modify' && planOriginalContents.value[path] === undefined) {
      planOriginalContents.value[path] = await getFileContent(path)
    }
    const success = await applyFileChange(path, content)
    if (success) {
      planFileStates.value[path] = 'applied'
      visibleDiffs.value.delete(path)
    }
  }
}

const discardChange = (path) => {
  planFileStates.value[path] = 'rejected'
  visibleDiffs.value.delete(path)
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

  visibleDiffs.value.clear()

  // Activate the Verification tab automatically after batch apply
  if (tabs.value.find(t => t.id === 'verification')) {
    activeTab.value = 'verification'
  }
}

const handlePasteNext = async () => {
  const success = await processPaste()
  if (success) {
    visibleDiffs.value.clear()

    // Reset tab to Intro if available, matching fresh behavior
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
  <div id="review-modal" class="absolute inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
    <div class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[92vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar">
        <h2 class="text-xl font-bold text-white">AI Response Review</h2>
        <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors" title="Close review window">
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
          id="btn-review-copy-correction"
          @click="copyAdmonishment"
          v-info="'review_admonish'"
          class="bg-[#DE6808] hover:bg-orange-500 text-white text-xs font-bold py-1.5 px-4 rounded transition-colors"
          title="Tell the AI that the response followed no usable format"
        >
          Copy Correction Prompt
        </button>
      </div>

      <!-- Tabs Navigation -->
      <div id="review-tabs" class="flex bg-cm-top-bar border-b border-gray-700 px-4 shrink-0" v-info="'review_tabs'">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          v-info="`review_tab_${tab.id}`"
          class="px-5 py-3 text-sm font-medium transition-all border-b-2 flex items-center space-x-2"
          :class="activeTab === tab.id ? 'border-cm-blue text-white bg-white/5' : 'border-transparent text-gray-500 hover:text-white hover:bg-white/5'"
          :title="tab.tooltip"
        >
          <component :is="tab.icon" class="w-4 h-4" :class="tab.color" />
          <span>{{ tab.name }}</span>
        </button>
      </div>

      <!-- Scrollable Tab Content Container -->
      <div id="review-content-viewport" ref="tabContentContainer" class="flex-grow overflow-y-auto custom-scrollbar bg-cm-dark-bg" @wheel.ctrl.prevent="handleZoom">
        <div v-for="tab in tabs" :key="tab.id" v-show="activeTab === tab.id" class="p-8">

          <!-- Standard Content Tabs -->
          <template v-if="tab.id !== 'changes'">
            <MarkdownRenderer :content="tab.content" :fontSize="editorFontSize" />
          </template>

          <!-- Interactive Changes Tab -->
          <ReviewChangesTab
            v-else
            :commentary="tab.content"
            :visible-diffs="visibleDiffs"
            :is-all-expanded="isAllExpanded"
            :get-skipped-message="getSkippedMessage"
            @toggle-diff="toggleDiff"
            @toggle-all-diffs="toggleAllDiffs"
            @accept="acceptChange"
            @discard="discardChange"
            @undo="undoChange"
          />

        </div>
      </div>

      <!-- Footer Actions -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex items-center shrink-0">
        <!-- Left Aligned Group -->
        <button
          id="btn-review-paste-next"
          v-if="getPendingCount === 0"
          @click="handlePasteNext"
          v-info="'paste_changes'"
          class="bg-cm-green hover:bg-green-600 text-white font-bold py-2 px-8 rounded shadow-md transition-all text-sm flex items-center justify-center whitespace-nowrap"
          title="Apply new response from your clipboard"
        >
          <ClipboardPaste class="w-4 h-4 mr-2" />
          <span>Paste Next</span>
        </button>

        <!-- Dynamic Spacer ensures standard edge-alignment for primary/secondary buttons -->
        <div class="flex-grow"></div>

        <!-- Right Aligned Group -->
        <div class="flex items-center space-x-3">
          <button
            @click="emit('close')"
            v-info="getPendingCount === 0 ? 'review_close' : 'review_cancel'"
            class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-8 rounded transition-colors text-sm flex items-center justify-center whitespace-nowrap"
            :title="getPendingCount === 0 ? 'Close review window' : 'Discard proposed changes'"
          >
            {{ getPendingCount === 0 ? 'Close' : 'Cancel' }}
          </button>
          <button
            id="btn-review-apply"
            v-if="getPendingCount > 0"
            @click="applyAllPending"
            v-info="'review_apply'"
            class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-2 px-12 rounded shadow-md transition-all text-sm flex items-center justify-center whitespace-nowrap"
            title="Accept and write all pending modifications to disk"
          >
            <CheckCircle class="w-4 h-4 mr-2" />
            <span>{{ applyAllLabel }}</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>