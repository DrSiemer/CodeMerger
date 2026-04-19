<script setup>
import { ref, computed } from 'vue'
import { ChevronDownSquare, ChevronUpSquare } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'
import ReviewCommentary from './ReviewCommentary.vue'
import ReviewFileItem from './ReviewFileItem.vue'

const props = defineProps({
  commentary: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['request-tab-switch'])

const {
  lastAiResponse,
  planFileStates,
  planOriginalContents,
  getFileContent,
  applyFileChange,
  deleteFile,
  statusMessage
} = useAppState()

const visibleDiffs = ref(new Set())

const hasUpdates = computed(() => Object.keys(lastAiResponse.value?.updates || {}).length > 0)
const hasCreations = computed(() => Object.keys(lastAiResponse.value?.creations || {}).length > 0)
const hasDeletions = computed(() => (lastAiResponse.value?.deletions_proposed || []).length > 0)

const allReviewPaths = computed(() => {
  const response = lastAiResponse.value
  if (!response) return []
  return [
    ...Object.keys(response.updates || {}),
    ...Object.keys(response.creations || {}),
    ...(response.deletions_proposed || [])
  ]
})

const totalFileCount = computed(() => allReviewPaths.value.length)

const expandablePaths = computed(() => {
  const allNonSkipped = allReviewPaths.value.filter(p => planFileStates.value[p] !== 'skipped')
  const pending = allNonSkipped.filter(p => planFileStates.value[p] === 'pending')
  return pending.length > 0 ? pending : allNonSkipped
})

const isAllExpanded = computed(() => {
  const paths = expandablePaths.value
  if (paths.length === 0) return visibleDiffs.value.size > 0
  return paths.every(p => visibleDiffs.value.has(p))
})

const getHeaderId = (path) => `file-header-${path.replace(/[\\/.]/g, '-')}`

const scrollAfterAction = (path) => {
  setTimeout(() => {
    const el = document.getElementById(getHeaderId(path))
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 50)
}

const toggleDiff = async (path) => {
  if (visibleDiffs.value.has(path)) {
    visibleDiffs.value.delete(path)
  } else {
    if (planOriginalContents.value[path] === undefined) {
      planOriginalContents.value[path] = await getFileContent(path)
    }
    visibleDiffs.value.add(path)
    scrollAfterAction(path)
  }
}

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
      if (allReviewPaths.value.length === 1) emit('request-tab-switch', 'verification')
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
      if (allReviewPaths.value.length === 1) emit('request-tab-switch', 'verification')
    }
  }
  scrollAfterAction(path)
}

const discardChange = (path) => {
  planFileStates.value[path] = 'rejected'
  visibleDiffs.value.delete(path)
  scrollAfterAction(path)
}

const undoChange = async (path, type) => {
  if (planFileStates.value[path] === 'rejected') {
    planFileStates.value[path] = 'pending'
  } else {
    const originalText = planOriginalContents.value[path]
    if (type === 'create') {
      const success = await deleteFile(path)
      if (success) planFileStates.value[path] = 'pending'
    } else {
      if (originalText === undefined) return
      const success = await applyFileChange(path, originalText)
      if (success) planFileStates.value[path] = 'pending'
    }
  }
  scrollAfterAction(path)
}

const getSkippedMessage = (path) => {
  const isDeletion = lastAiResponse.value?.deletions_proposed?.includes(path)
  return isDeletion ? 'Already deleted' : 'No changes'
}
</script>

<template>
  <div class="space-y-8 max-w-5xl mx-auto pb-12">

    <!-- AI Commentary -->
    <ReviewCommentary v-if="commentary" :commentary="commentary" />

    <!-- Bulk Toggle Toolbar (Top) -->
    <div v-if="totalFileCount > 1" class="flex justify-end items-center">
      <button
        @click="toggleAllDiffs"
        class="text-xs font-bold text-gray-400 hover:text-white flex items-center space-x-2 transition-colors uppercase tracking-tight"
        :title="isAllExpanded ? 'Close all open diffs' : 'Open all file diffs'"
      >
        <component :is="isAllExpanded ? ChevronUpSquare : ChevronDownSquare" class="w-4 h-4" />
        <span>{{ isAllExpanded ? 'Collapse All' : 'Expand All' }}</span>
      </button>
    </div>

    <!-- Updates -->
    <div v-if="hasUpdates">
      <div class="flex items-center space-x-4 mb-4">
        <h4 class="text-xs font-bold text-cm-blue uppercase tracking-widest shrink-0">Modify Content</h4>
        <div class="h-px bg-cm-blue/30 flex-grow"></div>
      </div>
      <div class="space-y-3">
        <ReviewFileItem
          v-for="(content, path) in lastAiResponse.updates"
          :key="path"
          :path="path"
          type="modify"
          :new-text="content"
          :original-text="planOriginalContents[path]"
          :state="planFileStates[path]"
          :is-expanded="visibleDiffs.has(path)"
          :header-id="getHeaderId(path)"
          :get-skipped-message="getSkippedMessage"
          @toggle-diff="toggleDiff"
          @accept="acceptChange"
          @discard="discardChange"
          @undo="undoChange"
        />
      </div>
    </div>

    <!-- Creations -->
    <div v-if="hasCreations">
      <div class="flex items-center space-x-4 mb-4">
        <h4 class="text-xs font-bold text-cm-green uppercase tracking-widest shrink-0">Create New File</h4>
        <div class="h-px bg-cm-green/30 flex-grow"></div>
      </div>
      <div class="space-y-3">
        <ReviewFileItem
          v-for="(content, path) in lastAiResponse.creations"
          :key="path"
          :path="path"
          type="create"
          :new-text="content"
          :state="planFileStates[path]"
          :is-expanded="visibleDiffs.has(path)"
          :header-id="getHeaderId(path)"
          :get-skipped-message="getSkippedMessage"
          @toggle-diff="toggleDiff"
          @accept="acceptChange"
          @discard="discardChange"
          @undo="undoChange"
        />
      </div>
    </div>

    <!-- Deletions -->
    <div v-if="hasDeletions">
      <div class="flex items-center space-x-4 mb-4">
        <h4 class="text-xs font-bold text-cm-warn uppercase tracking-widest shrink-0">Delete File</h4>
        <div class="h-px bg-cm-warn/30 flex-grow"></div>
      </div>
      <div class="space-y-3">
        <ReviewFileItem
          v-for="path in lastAiResponse.deletions_proposed"
          :key="path"
          :path="path"
          type="delete"
          new-text=""
          :original-text="planOriginalContents[path]"
          :state="planFileStates[path]"
          :is-expanded="visibleDiffs.has(path)"
          :header-id="getHeaderId(path)"
          :get-skipped-message="getSkippedMessage"
          @toggle-diff="toggleDiff"
          @accept="acceptChange"
          @discard="discardChange"
          @undo="undoChange"
        />
      </div>
    </div>

    <!-- Bulk Toggle Toolbar (Bottom) -->
    <div v-if="totalFileCount > 2" class="flex justify-end items-center pt-4">
      <button
        @click="toggleAllDiffs"
        class="text-xs font-bold text-gray-400 hover:text-white flex items-center space-x-2 transition-colors uppercase tracking-tight"
        :title="isAllExpanded ? 'Close all open diffs' : 'Open all file diffs'"
      >
        <component :is="isAllExpanded ? ChevronUpSquare : ChevronDownSquare" class="w-4 h-4" />
        <span>{{ isAllExpanded ? 'Collapse All' : 'Expand All' }}</span>
      </button>
    </div>

  </div>
</template>