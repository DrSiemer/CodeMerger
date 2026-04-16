<script setup>
import { computed } from 'vue'
import { Eye, Undo2, ChevronUp } from 'lucide-vue-next'
import DiffViewer from '../DiffViewer.vue'
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  path: {
    type: String,
    required: true
  },
  type: {
    type: String,
    required: true // 'modify', 'create', 'delete'
  },
  newText: {
    type: String,
    default: ''
  },
  originalText: {
    type: String,
    default: undefined
  },
  state: {
    type: String,
    required: true
  },
  isExpanded: {
    type: Boolean,
    default: false
  },
  headerId: {
    type: String,
    default: ''
  },
  getSkippedMessage: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['toggle-diff', 'accept', 'discard', 'undo'])

const { editorFontSize } = useAppState()

const isModify = computed(() => props.type === 'modify')
const isCreate = computed(() => props.type === 'create')
const isDelete = computed(() => props.type === 'delete')

const pathClass = computed(() => {
  if (isCreate.value) {
    return props.state === 'applied' ? 'text-gray-500 line-through' : 'text-gray-200'
  }
  return ['pending', 'skipped'].includes(props.state)
    ? (props.state === 'skipped' ? 'text-[#888888]' : 'text-gray-200')
    : 'text-gray-500 line-through'
})

const undoTooltip = computed(() => {
  if (isCreate.value) return 'Delete the newly created file'
  if (isDelete.value) return 'Restore the deleted file'
  return 'Revert to local disk version'
})

const acceptLabel = computed(() => {
  if (isDelete.value) return 'Accept Delete'
  return 'Accept'
})

const discardLabel = computed(() => {
  if (isDelete.value) return 'Keep'
  return 'Discard'
})

const diffButtonLabel = computed(() => {
  if (isModify.value) return 'Diff'
  return 'View'
})

const diffButtonTooltip = computed(() => {
  if (isModify.value) {
    return props.state === 'pending' ? 'Inspect text changes' : 'Inspect text changes for this applied file'
  }
  if (isCreate.value) {
    return props.state === 'pending' ? 'View file content' : 'View file content for this newly created file'
  }
  return props.state === 'pending' ? 'View file content before deletion' : 'View file content that was deleted'
})
</script>

<template>
  <div class="border border-gray-700 rounded bg-cm-input-bg/30 overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between p-3" :id="headerId">
      <div class="flex items-center space-x-3 min-w-0">
        <span class="font-mono text-sm truncate" :class="pathClass">
          {{ path }}
        </span>
      </div>

      <div class="flex items-center space-x-2 shrink-0">
        <!-- Handled / Skipped State -->
        <template v-if="state === 'skipped'">
          <span class="text-xs font-bold text-gray-500 px-3 py-1 bg-gray-800 rounded">
            {{ getSkippedMessage(path) }}
          </span>
        </template>

        <!-- Pending State -->
        <template v-else-if="state === 'pending'">
          <button
            @click="$emit('toggle-diff', path)"
            v-info="'review_diff'"
            class="text-xs font-bold bg-cm-blue hover:bg-blue-500 text-white px-3 py-1 rounded transition-colors flex items-center"
            :title="diffButtonTooltip"
          >
            <Eye v-if="isModify" class="w-3.5 h-3.5 mr-1.5" />
            {{ diffButtonLabel }}
          </button>
          <button
            @click="$emit('discard', path)"
            v-info="'review_file_action'"
            class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition-colors"
            :title="isDelete ? 'Keep this file' : 'Skip this file for now'"
          >
            {{ discardLabel }}
          </button>
          <button
            @click="$emit('accept', path, type)"
            v-info="'review_file_action'"
            class="text-xs font-bold px-3 py-1 rounded transition-colors text-white"
            :class="isDelete ? 'bg-cm-warn hover:bg-red-500' : 'bg-cm-green hover:bg-green-600'"
            :title="isDelete ? 'Delete this file from disk' : 'Apply changes to this file'"
          >
            {{ acceptLabel }}
          </button>
        </template>

        <!-- Actioned State (Applied/Deleted) -->
        <div v-else class="flex items-center space-x-2">
          <button
            @click="$emit('toggle-diff', path)"
            v-info="'review_diff'"
            class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center"
            :title="diffButtonTooltip"
          >
            <Eye class="w-3.5 h-3.5 mr-1.5" />
            {{ diffButtonLabel }}
          </button>
          <button
            @click="$emit('undo', path, type)"
            v-info="'review_file_action'"
            class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1 rounded transition-colors flex items-center"
            :title="undoTooltip"
          >
            <Undo2 class="w-3.5 h-3.5 mr-1.5" />
            Undo
          </button>
        </div>
      </div>
    </div>

    <!-- Expandable Diff Area -->
    <div v-if="isExpanded" class="p-3 pt-0">
      <DiffViewer
        :old-text="originalText"
        :new-text="newText"
        :font-size="editorFontSize"
        :filename="path"
      />
      <div class="flex justify-end items-center space-x-2 mt-3">
        <button
          @click="$emit('toggle-diff', path)"
          class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-1.5 rounded transition-colors flex items-center"
        >
          <ChevronUp class="w-3.5 h-3.5 mr-1" />
          Collapse
        </button>

        <template v-if="state === 'pending'">
          <button
            @click="$emit('discard', path)"
            class="text-xs font-bold bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-1.5 rounded transition-colors"
          >
            {{ discardLabel }}
          </button>
          <button
            @click="$emit('accept', path, type)"
            class="text-xs font-bold px-4 py-1.5 rounded transition-colors text-white"
            :class="isDelete ? 'bg-cm-warn hover:bg-red-500' : 'bg-cm-green hover:bg-green-600'"
          >
            {{ acceptLabel }}
          </button>
        </template>

        <template v-else-if="state !== 'skipped'">
          <button
            @click="$emit('undo', path, type)"
            class="text-xs font-bold bg-gray-800 hover:bg-gray-700 text-gray-400 px-4 py-1.5 rounded transition-colors flex items-center"
          >
            <Undo2 class="w-3.5 h-3.5 mr-1.5" /> Undo
          </button>
        </template>
      </div>
    </div>
  </div>
</template>