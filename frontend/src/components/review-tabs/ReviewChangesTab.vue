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
  },
  visibleDiffs: {
    type: Set,
    required: true
  },
  isAllExpanded: {
    type: Boolean,
    default: false
  },
  getSkippedMessage: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['toggle-diff', 'toggle-all-diffs', 'accept', 'discard', 'undo'])

const { lastAiResponse, planFileStates, planOriginalContents } = useAppState()

const hasUpdates = computed(() => Object.keys(lastAiResponse.value?.updates || {}).length > 0)
const hasCreations = computed(() => Object.keys(lastAiResponse.value?.creations || {}).length > 0)
const hasDeletions = computed(() => (lastAiResponse.value?.deletions_proposed || []).length > 0)

const totalFileCount = computed(() => {
  const u = Object.keys(lastAiResponse.value?.updates || {}).length
  const c = Object.keys(lastAiResponse.value?.creations || {}).length
  const d = (lastAiResponse.value?.deletions_proposed || []).length
  return u + c + d
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

const onToggleDiff = (path) => {
  emit('toggle-diff', path)
  if (!props.visibleDiffs.has(path)) {
    scrollAfterAction(path)
  }
}

const onAccept = (path, type) => {
  emit('accept', path, type)
  scrollAfterAction(path)
}

const onDiscard = (path) => {
  emit('discard', path)
  scrollAfterAction(path)
}

const onUndo = (path, type) => {
  emit('undo', path, type)
  scrollAfterAction(path)
}
</script>

<template>
  <div class="space-y-8 max-w-5xl mx-auto pb-12">

    <!-- AI Commentary -->
    <ReviewCommentary v-if="commentary" :commentary="commentary" />

    <!-- Bulk Toggle Toolbar (Top) -->
    <div v-if="totalFileCount > 1" class="flex justify-end items-center">
      <button
        @click="$emit('toggle-all-diffs')"
        class="text-xs font-bold text-gray-400 hover:text-white flex items-center space-x-2 transition-colors uppercase tracking-tight"
        :title="isAllExpanded ? 'Close all open diffs' : 'Open all pending file diffs'"
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
          @toggle-diff="onToggleDiff"
          @accept="onAccept"
          @discard="onDiscard"
          @undo="onUndo"
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
          @toggle-diff="onToggleDiff"
          @accept="onAccept"
          @discard="onDiscard"
          @undo="onUndo"
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
          @toggle-diff="onToggleDiff"
          @accept="onAccept"
          @discard="onDiscard"
          @undo="onUndo"
        />
      </div>
    </div>

    <!-- Bulk Toggle Toolbar (Bottom) -->
    <div v-if="totalFileCount > 2" class="flex justify-end items-center pt-4">
      <button
        @click="$emit('toggle-all-diffs')"
        class="text-xs font-bold text-gray-400 hover:text-white flex items-center space-x-2 transition-colors uppercase tracking-tight"
        :title="isAllExpanded ? 'Close all open diffs' : 'Open all pending file diffs'"
      >
        <component :is="isAllExpanded ? ChevronUpSquare : ChevronDownSquare" class="w-4 h-4" />
        <span>{{ isAllExpanded ? 'Collapse All' : 'Expand All' }}</span>
      </button>
    </div>

  </div>
</template>