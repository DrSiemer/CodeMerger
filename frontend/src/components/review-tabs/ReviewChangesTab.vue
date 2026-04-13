<script setup>
import { ref, computed } from 'vue'
import { Eye, Undo2, BookOpen, ChevronDown, ChevronRight } from 'lucide-vue-next'
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
  getSkippedMessage: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['toggle-diff', 'accept', 'discard', 'undo'])

const { lastAiResponse, planFileStates, planOriginalContents, editorFontSize } = useAppState()

const showCommentary = ref(false)

// Re-define computed properties for clarity and localized reactivity
const hasUpdates = computed(() => Object.keys(lastAiResponse.value?.updates || {}).length > 0)
const hasCreations = computed(() => Object.keys(lastAiResponse.value?.creations || {}).length > 0)
const hasDeletions = computed(() => (lastAiResponse.value?.deletions_proposed || []).length > 0)
</script>

<template>
  <div class="space-y-8 max-w-5xl mx-auto">

    <!-- AI Commentary Expandable -->
    <div v-if="commentary" class="border border-gray-700 rounded bg-[#1A1A1A] overflow-hidden">
      <button
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
                <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors flex items-center" title="Inspect text changes">
                  <Eye class="w-3.5 h-3.5 mr-1.5" />
                  Diff
                </button>
                <button @click="$emit('accept', path, 'modify')" v-info="'review_file_action'" class="text-xs font-bold bg-cm-green hover:bg-green-600 text-white px-3 py-1 rounded transition-colors" title="Apply change to this file">Accept</button>
                <button @click="$emit('discard', path)" v-info="'review_file_action'" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors" title="Skip this file for now">Discard</button>
              </template>
              <button v-else @click="$emit('undo', path, 'modify')" v-info="'review_file_action'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="Revert to local disk version">
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
                <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors" title="View file content">View</button>
                <button @click="$emit('accept', path, 'create')" v-info="'review_file_action'" class="text-xs font-bold bg-cm-green hover:bg-green-600 text-white px-3 py-1 rounded transition-colors" title="Create this new file">Accept</button>
                <button @click="$emit('discard', path)" v-info="'review_file_action'" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors" title="Do not create this file">Discard</button>
              </template>
              <button v-else @click="$emit('undo', path, 'create')" v-info="'review_file_action'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="Delete the newly created file">
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
              <button @click="$emit('toggle-diff', path)" v-info="'review_diff'" class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors" title="View file content before deletion">View</button>
              <button @click="$emit('accept', path, 'delete')" v-info="'review_file_action'" class="text-xs font-bold bg-cm-warn hover:bg-red-500 text-white px-3 py-1 rounded transition-colors" title="Delete this file from disk">Accept Delete</button>
              <button @click="$emit('discard', path)" v-info="'review_file_action'" class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors" title="Keep this file">Keep</button>
            </template>
            <button v-else @click="$emit('undo', path, 'delete')" v-info="'review_file_action'" class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center" title="Restore the deleted file">
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