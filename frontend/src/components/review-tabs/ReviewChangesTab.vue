<script setup>
import { ref, computed } from 'vue'
import {
  Eye, Undo2, BookOpen, ChevronDown, ChevronRight,
  ChevronDownSquare, ChevronUpSquare, ChevronUp
} from 'lucide-vue-next'
import MarkdownRenderer from '../MarkdownRenderer.vue'
import DiffViewer from '../DiffViewer.vue'
import { useAppState } from '../../composables/useAppState'

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

const { lastAiResponse, planFileStates, planOriginalContents, editorFontSize } = useAppState()

const showCommentary = ref(false)

// Re-define computed properties for clarity and localized reactivity
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

const collapseAndScroll = (path) => {
  emit('toggle-diff', path)
  setTimeout(() => {
    const el = document.getElementById(getHeaderId(path))
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 50)
}

const acceptAndScroll = (path, type) => {
  emit('accept', path, type)
  setTimeout(() => {
    const el = document.getElementById(getHeaderId(path))
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 50)
}

const discardAndScroll = (path) => {
  emit('discard', path)
  setTimeout(() => {
    const el = document.getElementById(getHeaderId(path))
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 50)
}

const undoAndScroll = (path, type) => {
  emit('undo', path, type)
  setTimeout(() => {
    const el = document.getElementById(getHeaderId(path))
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 50)
}

const collapseCommentary = () => {
  showCommentary.value = false
  setTimeout(() => {
    const el = document.getElementById('commentary-header')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 50)
}
</script>

<template>
  <div class="space-y-8 max-w-5xl mx-auto pb-12">

    <!-- AI Commentary Expandable -->
    <div v-if="commentary" class="border border-gray-700 rounded bg-[#1A1A1A] overflow-hidden">
      <button
        id="commentary-header"
        @click="showCommentary = !showCommentary"
        v-info="'review_commentary'"
        class="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
        title="Read technical explanations for these changes"
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
        <MarkdownRenderer :content="commentary" :fontSize="editorFontSize" />
        <div class="flex justify-end mt-3">
          <button @click="collapseCommentary" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-1.5 rounded transition-colors flex items-center">
            <ChevronUp class="w-3.5 h-3.5 mr-1" />
            Collapse
          </button>
        </div>
      </div>
    </div>

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
        <div v-for="(content, path) in lastAiResponse.updates" :key="path" class="border border-gray-700 rounded bg-cm-input-bg/30">
          <div class="flex items-center justify-between p-3" :id="getHeaderId(path)">
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
                <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors flex items-center" title="Inspect text changes">
                  <Eye class="w-3.5 h-3.5 mr-1.5" />
                  Diff
                </button>
                <button @click="$emit('discard', path)" v-info="'review_file_action'" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors" title="Skip this file for now">Discard</button>
                <button @click="$emit('accept', path, 'modify')" v-info="'review_file_action'" class="text-xs font-bold bg-cm-green hover:bg-green-600 text-white px-3 py-1 rounded transition-colors" title="Apply change to this file">Accept</button>
              </template>
              <div v-else class="flex items-center space-x-2">
                <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="Inspect text changes for this applied file">
                  <Eye class="w-3.5 h-3.5 mr-1.5" />
                  Diff
                </button>
                <button @click="$emit('undo', path, 'modify')" v-info="'review_file_action'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="Revert to local disk version">
                  <Undo2 class="w-3.5 h-3.5 mr-1.5" />
                  Undo
                </button>
              </div>
            </div>
          </div>
          <div v-if="visibleDiffs.has(path)" class="p-3 pt-0">
            <DiffViewer :old-text="planOriginalContents[path]" :new-text="content" :fontSize="editorFontSize" :filename="path" />
            <div class="flex justify-end items-center space-x-2 mt-3">
              <button @click="collapseAndScroll(path)" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-1.5 rounded transition-colors flex items-center">
                <ChevronUp class="w-3.5 h-3.5 mr-1" />
                Collapse
              </button>
              <template v-if="planFileStates[path] === 'pending'">
                <button @click="discardAndScroll(path)" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-1.5 rounded transition-colors">Discard</button>
                <button @click="acceptAndScroll(path, 'modify')" class="text-xs font-bold bg-cm-green hover:bg-green-600 text-white px-4 py-1.5 rounded transition-colors">Accept</button>
              </template>
              <template v-else-if="planFileStates[path] !== 'skipped'">
                 <button @click="undoAndScroll(path, 'modify')" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-4 py-1.5 rounded transition-colors flex items-center">
                   <Undo2 class="w-3.5 h-3.5 mr-1.5" /> Undo
                 </button>
              </template>
            </div>
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
          <div class="flex items-center justify-between p-3" :id="getHeaderId(path)">
            <span class="font-mono text-sm text-gray-200" :class="{'text-gray-500 line-through': planFileStates[path] === 'applied'}">{{ path }}</span>
            <div class="flex items-center space-x-2">
              <template v-if="planFileStates[path] === 'pending'">
                <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors" title="View file content">View</button>
                <button @click="$emit('discard', path)" v-info="'review_file_action'" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors" title="Do not create this file">Discard</button>
                <button @click="$emit('accept', path, 'create')" v-info="'review_file_action'" class="text-xs font-bold bg-cm-green hover:bg-green-600 text-white px-3 py-1 rounded transition-colors" title="Create this new file">Accept</button>
              </template>
              <div v-else class="flex items-center space-x-2">
                <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="View file content for this newly created file">
                  <Eye class="w-3.5 h-3.5 mr-1.5" />
                  View
                </button>
                <button @click="$emit('undo', path, 'create')" v-info="'review_file_action'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="Delete the newly created file">
                  <Undo2 class="w-3.5 h-3.5 mr-1.5" />
                  Undo
                </button>
              </div>
            </div>
          </div>
          <div v-if="visibleDiffs.has(path)" class="p-3 pt-0">
            <DiffViewer :new-text="content" :fontSize="editorFontSize" :filename="path" />
            <div class="flex justify-end items-center space-x-2 mt-3">
              <button @click="collapseAndScroll(path)" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-1.5 rounded transition-colors flex items-center">
                <ChevronUp class="w-3.5 h-3.5 mr-1" />
                Collapse
              </button>
              <template v-if="planFileStates[path] === 'pending'">
                <button @click="discardAndScroll(path)" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-1.5 rounded transition-colors">Discard</button>
                <button @click="acceptAndScroll(path, 'create')" class="text-xs font-bold bg-cm-green hover:bg-green-600 text-white px-4 py-1.5 rounded transition-colors">Accept</button>
              </template>
              <template v-else-if="planFileStates[path] !== 'skipped'">
                 <button @click="undoAndScroll(path, 'create')" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-4 py-1.5 rounded transition-colors flex items-center">
                   <Undo2 class="w-3.5 h-3.5 mr-1.5" /> Undo
                 </button>
              </template>
            </div>
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
        <div class="p-3 flex items-center justify-between" :id="getHeaderId(path)">
          <span
            class="font-mono text-sm truncate"
            :class="['pending', 'skipped'].includes(planFileStates[path]) ? (planFileStates[path] === 'skipped' ? 'text-[#888888]' : 'text-gray-200') : 'text-gray-500 line-through'"
          >{{ path }}</span>
          <div class="flex items-center space-x-2">
            <template v-if="planFileStates[path] === 'skipped'">
              <span class="text-xs font-bold text-gray-500 px-3 py-1 bg-gray-800 rounded">{{ getSkippedMessage(path) }}</span>
            </template>
            <template v-else-if="planFileStates[path] === 'pending'">
              <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors" title="View file content before deletion">View</button>
              <button @click="$emit('discard', path)" v-info="'review_file_action'" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors" title="Keep this file">Keep</button>
              <button @click="$emit('accept', path, 'delete')" v-info="'review_file_action'" class="text-xs font-bold bg-cm-warn hover:bg-red-500 text-white px-3 py-1 rounded transition-colors" title="Delete this file from disk">Accept Delete</button>
            </template>
            <div v-else class="flex items-center space-x-2">
              <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="View file content that was deleted">
                <Eye class="w-3.5 h-3.5 mr-1.5" />
                View
              </button>
              <button @click="$emit('undo', path, 'delete')" v-info="'review_file_action'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="Restore the deleted file">
                <Undo2 class="w-3.5 h-3.5 mr-1.5" />
                Undo
              </button>
            </div>
          </div>
        </div>
        <div v-if="visibleDiffs.has(path)" class="p-3 pt-0">
          <!-- For deletions, DiffViewer shows current content as 'removed' -->
          <DiffViewer :old-text="planOriginalContents[path]" new-text="" :fontSize="editorFontSize" :filename="path" />
          <div class="flex justify-end items-center space-x-2 mt-3">
            <button @click="collapseAndScroll(path)" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-1.5 rounded transition-colors flex items-center">
              <ChevronUp class="w-3.5 h-3.5 mr-1" />
              Collapse
            </button>
            <template v-if="planFileStates[path] === 'pending'">
              <button @click="discardAndScroll(path)" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-1.5 rounded transition-colors">Keep</button>
              <button @click="acceptAndScroll(path, 'delete')" class="text-xs font-bold bg-cm-warn hover:bg-red-500 text-white px-4 py-1.5 rounded transition-colors">Accept Delete</button>
            </template>
            <template v-else-if="planFileStates[path] !== 'skipped'">
               <button @click="undoAndScroll(path, 'delete')" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-4 py-1.5 rounded transition-colors flex items-center">
                 <Undo2 class="w-3.5 h-3.5 mr-1.5" /> Undo
               </button>
            </template>
          </div>
        </div>
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