<script setup>
import { ref, watch, computed } from 'vue'
import { ChevronRight, ChevronDown, Folder, CheckSquare, Square } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  selectedPaths: {
    type: Array,
    default: () => []
  },
  initialExpandedPaths: {
    type: Array,
    default: () => []
  },
  level: {
    type: Number,
    default: 0
  },
  highlightedPath: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['toggle-select', 'toggle-expand', 'file-click'])
const { openFile } = useAppState()

const isExpanded = ref(props.initialExpandedPaths.includes(props.node.path))

// Handle external changes to expanded state (e.g. on mount)
watch(() => props.initialExpandedPaths, (newPaths) => {
  if (props.node.type === 'dir') {
    isExpanded.value = newPaths.includes(props.node.path)
  }
}, { deep: true })

const isFileSelected = computed(() => props.selectedPaths.includes(props.node.path))
const isHighlighted = computed(() => props.highlightedPath === props.node.path)

// --- Visual Completeness Logic (Mirrors Python UI) ---
// Folders turn grey if all "relevant" (non-init) files inside are selected
const IGNORED_FOR_COMPLETENESS = ['__init__.py']

const isFolderComplete = computed(() => {
  if (props.node.type !== 'dir') return false

  const getRelevantFiles = (node) => {
    let files = []
    if (node.type === 'file') {
      if (!IGNORED_FOR_COMPLETENESS.includes(node.name)) {
        files.push(node.path)
      }
    } else if (node.children) {
      node.children.forEach(child => {
        files = files.concat(getRelevantFiles(child))
      })
    }
    return files
  }

  const relevantFiles = getRelevantFiles(props.node)
  if (relevantFiles.length === 0) return true // Empty or only __init__.py

  return relevantFiles.every(path => props.selectedPaths.includes(path))
})

const textClass = computed(() => {
  if (props.node.type === 'file') {
    // Priority 1: New Files (High-contrast Green)
    if (props.node.is_new) return 'text-[#40C040] font-bold'

    // Priority 2: Filtered files (Purple)
    if (isFileSelected.value && props.node.is_filtered) return 'text-[#BB86FC]'

    // Priority 3: Selected files (Medium Grey - accounted for)
    if (isFileSelected.value) return 'text-[#888888]'

    // Priority 4: __init__.py (Darkest Grey - boilerplate)
    if (IGNORED_FOR_COMPLETENESS.includes(props.node.name)) return 'text-gray-600'

    // Priority 5: Normal files (Bright)
    return 'text-gray-200 group-hover:text-white'
  } else {
    // Directory coloring: Dark if complete, else Bright
    return isFolderComplete.value ? 'text-gray-600' : 'text-gray-200 font-medium'
  }
})

const handleClick = (event) => {
  if (props.node.type === 'dir') {
    isExpanded.value = !isExpanded.value
    emit('toggle-expand', { path: props.node.path, expanded: isExpanded.value })
  } else {
    // File Click
    if (event.ctrlKey) {
      openFile(props.node.path)
    } else {
      emit('file-click', props.node.path)
    }
  }
}

const handleIconClick = (event) => {
  event.stopPropagation()
  if (props.node.type === 'file') {
    emit('toggle-select', props.node.path)
  } else {
    handleClick(event)
  }
}

const handleDoubleClick = () => {
  if (props.node.type === 'file') {
    emit('toggle-select', props.node.path)
  }
}

const onChildToggleSelect = (path) => {
  emit('toggle-select', path)
}

const onChildFileClick = (path) => {
  emit('file-click', path)
}

const onChildToggleExpand = (data) => {
  emit('toggle-expand', data)
}
</script>

<template>
  <div :id="`node-${node.path.replace(/[\\/.]/g, '-')}`" class="select-none">
    <div
      class="flex items-center py-1 hover:bg-cm-blue/10 cursor-pointer rounded transition-colors group"
      :class="{ 'bg-cm-blue/20': isHighlighted }"
      :style="{ paddingLeft: `${level * 20}px` }"
      @click="handleClick"
      @dblclick="handleDoubleClick"
    >
      <!-- Expand Icon -->
      <div class="w-5 flex shrink-0 justify-center">
        <template v-if="node.type === 'dir'">
          <ChevronDown v-if="isExpanded" class="w-4 h-4 text-gray-500" />
          <ChevronRight v-else class="w-4 h-4 text-gray-500" />
        </template>
      </div>

      <!-- Type Icon (Instant toggle click area) -->
      <div class="w-5 flex shrink-0 justify-center mr-2" @click="handleIconClick">
        <Folder
          v-if="node.type === 'dir'"
          class="w-4 h-4"
          :class="isFolderComplete ? 'text-gray-600' : 'text-cm-blue fill-cm-blue/20'"
        />
        <template v-else>
          <CheckSquare v-if="isFileSelected" class="w-4 h-4 text-cm-blue" />
          <Square
            v-else
            class="w-4 h-4"
            :class="node.is_new ? 'text-[#40C040]' : 'text-gray-600 group-hover:text-gray-400'"
          />
        </template>
      </div>

      <!-- Label -->
      <span
        class="text-sm truncate"
        :class="textClass"
        :title="node.is_filtered ? 'Normally hidden by filters' : (node.type === 'file' ? `${node.name} (Ctrl+Click to open)` : node.name)"
      >
        {{ node.name }}
      </span>
    </div>

    <!-- Recursive Children -->
    <div v-if="node.type === 'dir' && isExpanded" class="overflow-hidden">
      <FileTreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :selected-paths="selectedPaths"
        :initial-expanded-paths="initialExpandedPaths"
        :highlightedPath="highlightedPath"
        :level="level + 1"
        @toggle-select="onChildToggleSelect"
        @file-click="onChildFileClick"
        @toggle-expand="onChildToggleExpand"
      />
    </div>
  </div>
</template>