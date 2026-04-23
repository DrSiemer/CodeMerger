<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import {
  Milestone, ArrowUpToLine, ArrowUp, ArrowDown, ArrowDownToLine,
  ArrowDownUp
} from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { DEFAULT_TOKEN_COLOR_THRESHOLD } from '../utils/constants'

const props = defineProps({
  listItems: Array,
  filterText: String,
  mergeListRef: Object,
  totalTokens: Number,
  tokenColorClass: String,
  showFullPaths: Boolean,
  isOrderPulseActive: Boolean
})

const emit = defineEmits([
  'update:showFullPaths',
  'file-click',
  'token-interaction',
  'order-request'
])

const {
  openFile, statusMessage, getClipboardText,
  showOrderErrorModal, orderErrorMessage, config
} = useAppState()
const selectedIndices = ref(new Set())
const lastSelectedIndex = ref(null)

// Local template ref for reliable internal access to the UL element
const listRoot = ref(null)
const tempHighlightedPath = ref(null)
let highlightTimeout = null

const onKeyDown = (e) => {
  if (e.key === 'Delete' && selectedIndices.value.size > 0) {
    const target = e.target
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return
    e.preventDefault()
    removeSelected()
  }
}

onMounted(() => {
  // Synchronize the local element with the parent's Drag and Drop ref
  if (props.mergeListRef && listRoot.value) {
    props.mergeListRef.value = listRoot.value
  }
  window.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})

const TOKEN_COLOR_RANGE_MAX = 2500

const matchesFilter = (path) => {
  if (!props.filterText) return true
  return path.toLowerCase().includes(props.filterText.toLowerCase())
}

const getTokenColor = (file) => {
  if (!file) return 'text-gray-500'
  if (file.ignoreTokens) return 'text-gray-600'
  const count = file.tokens
  if (count === undefined || count === null || count < 0) return 'text-gray-500'

  const tokenValues = props.listItems
    .filter(f => f && !f.ignoreTokens)
    .map(f => f.tokens || 0)

  const rangeMax = config.value.token_color_threshold || DEFAULT_TOKEN_COLOR_THRESHOLD
  const maxInList = tokenValues.length > 0 ? Math.max(...tokenValues, rangeMax) : rangeMax
  const p = count / maxInList
  if (p < 0.2) return 'text-gray-500'
  if (p < 0.4) return 'text-gray-400'
  if (p < 0.6) return 'text-[#B77B06]'
  if (p < 0.8) return 'text-[#DE6808]'
  return 'text-[#DF2622]'
}

const handleFileClick = (index, event) => {
  const item = props.listItems[index]
  if (!item) return

  if (event.shiftKey && lastSelectedIndex.value !== null) {
    const start = Math.min(lastSelectedIndex.value, index)
    const end = Math.max(lastSelectedIndex.value, index)
    selectedIndices.value.clear()
    for (let i = start; i <= end; i++) selectedIndices.value.add(i)
  } else if (event.ctrlKey) {
    if (selectedIndices.value.has(index)) selectedIndices.value.delete(index)
    else {
      selectedIndices.value.add(index)
      lastSelectedIndex.value = index
    }
  } else {
    selectedIndices.value.clear()
    selectedIndices.value.add(index)
    lastSelectedIndex.value = index
    emit('file-click', item.path)
  }
}

const handleFileDoubleClick = (index) => {
  const item = props.listItems[index]
  if (item) {
    openFile(item.path)
  }
}

const handleOrderClick = (event) => {
  if (event.ctrlKey) {
    handlePasteOrder()
  } else {
    emit('order-request')
  }
}

const handlePasteOrder = async () => {
  if (props.listItems.length === 0) {
    statusMessage.value = "Merge order is empty, nothing to reorder."
    return
  }

  try {
    // CRITICAL: Using backend-bridged getClipboardText() to bypass browser permission dialogs
    const pastedText = await getClipboardText()
    if (!pastedText || !pastedText.trim()) {
      statusMessage.value = "Clipboard is empty."
      return
    }

    const startIdx = pastedText.indexOf('[')
    const endIdx = pastedText.lastIndexOf(']')
    if (startIdx === -1 || endIdx === -1) {
      throw new Error("Could not find a JSON array in the response.")
    }

    const jsonStr = pastedText.substring(startIdx, endIdx + 1)
    const newOrderList = JSON.parse(jsonStr)

    if (!Array.isArray(newOrderList)) {
      throw new Error("Parsed JSON is not a list.")
    }

    const currentPathsSet = new Set(props.listItems.map(f => f.path))
    const newPathsSet = new Set(newOrderList)

    const missingFiles = [...currentPathsSet].filter(p => !newPathsSet.has(p))
    const unknownFiles = [...newPathsSet].filter(p => !currentPathsSet.has(p))
    const duplicates = newOrderList.filter((item, index) => newOrderList.indexOf(item) !== index)

    if (missingFiles.length || unknownFiles.length || duplicates.length) {
      let errorParts = []
      if (missingFiles.length) {
        errorParts.push(`Missing Files:\n${JSON.stringify(missingFiles.sort(), null, 2)}`)
      }
      if (unknownFiles.length) {
        errorParts.push(`Unknown Files:\n${JSON.stringify(unknownFiles.sort(), null, 2)}`)
      }
      if (duplicates.length) {
        errorParts.push(`Duplicate Entries Found:\n${JSON.stringify([...new Set(duplicates)].sort(), null, 2)}`)
      }

      orderErrorMessage.value = errorParts.join('\n\n')
      showOrderErrorModal.value = true
      return
    }

    const pathMap = new Map(props.listItems.map(f => [f.path, f]))
    const newOrderedItems = newOrderList.map(p => pathMap.get(p))

    props.listItems.splice(0, props.listItems.length, ...newOrderedItems)

    selectedIndices.value.clear()
    lastSelectedIndex.value = null

    statusMessage.value = "File merge order updated from clipboard."

  } catch (err) {
    orderErrorMessage.value = `Could not parse the new file order.\n\nError: ${err.message}`
    showOrderErrorModal.value = true
  }
}

const scrollToSelection = (alignToTop = false) => {
  nextTick(() => {
    const selectedEl = listRoot.value?.querySelector('.bg-cm-blue')
    if (selectedEl) {
      selectedEl.scrollIntoView({ behavior: 'smooth', block: alignToTop ? 'start' : 'nearest' })
    }
  })
}

const scrollToPath = (path) => {
  const index = props.listItems.findIndex(f => f.path === path)
  if (index === -1) return

  // Apply subtle highlight
  tempHighlightedPath.value = path
  if (highlightTimeout) clearTimeout(highlightTimeout)
  highlightTimeout = setTimeout(() => {
    tempHighlightedPath.value = null
  }, 2000)

  // Use double requestAnimationFrame for maximum snappiness while ensuring the item is in the DOM
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      const listEl = listRoot.value
      if (!listEl) return

      const items = listEl.querySelectorAll('li')
      if (items[index]) {
        items[index].scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    })
  })
}

// --- Reorder Methods ---

const moveSelectionToTop = () => {
  if (selectedIndices.value.size === 0) return
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => a - b)
  const itemsToMove = sortedIndices.map(i => props.listItems[i])
  for (let i = sortedIndices.length - 1; i >= 0; i--) props.listItems.splice(sortedIndices[i], 1)
  props.listItems.unshift(...itemsToMove)
  selectedIndices.value.clear()
  for (let i = 0; i < itemsToMove.length; i++) selectedIndices.value.add(i)
  lastSelectedIndex.value = 0
  scrollToSelection(true)
}

const moveSelectionUp = () => {
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => a - b)
  if (sortedIndices.length === 0 || sortedIndices[0] === 0) return
  const newIndices = new Set()
  sortedIndices.forEach(i => {
    const item = props.listItems.splice(i, 1)[0]
    props.listItems.splice(i - 1, 0, item)
    newIndices.add(i - 1)
  })
  selectedIndices.value = newIndices
  lastSelectedIndex.value = Array.from(newIndices)[0]
  scrollToSelection()
}

const moveSelectionDown = () => {
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => b - a)
  if (sortedIndices.length === 0 || sortedIndices[0] === props.listItems.length - 1) return
  const newIndices = new Set()
  sortedIndices.forEach(i => {
    const item = props.listItems.splice(i, 1)[0]
    props.listItems.splice(i + 1, 0, item)
    newIndices.add(i + 1)
  })
  selectedIndices.value = newIndices
  lastSelectedIndex.value = Array.from(newIndices)[0]
  scrollToSelection()
}

const moveSelectionToBottom = () => {
  if (selectedIndices.value.size === 0) return
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => a - b)
  const itemsToMove = sortedIndices.map(i => props.listItems[i])
  for (let i = sortedIndices.length - 1; i >= 0; i--) props.listItems.splice(sortedIndices[i], 1)
  props.listItems.push(...itemsToMove)
  selectedIndices.value.clear()
  const startIdx = props.listItems.length - itemsToMove.length
  for (let i = 0; i < itemsToMove.length; i++) selectedIndices.value.add(startIdx + i)
  lastSelectedIndex.value = startIdx
  scrollToSelection(true)
}

const removeSelected = () => {
  const sortedIndices = Array.from(selectedIndices.value).sort((a, b) => b - a)
  sortedIndices.forEach(i => props.listItems.splice(i, 1))
  selectedIndices.value.clear()
  lastSelectedIndex.value = null
}

defineExpose({
  clearSelection: () => {
    selectedIndices.value.clear()
    lastSelectedIndex.value = null
  },
  scrollToPath
})
</script>

<template>
  <div id="fm-merge-order" class="flex flex-col p-5 bg-cm-dark-bg transition-all duration-300">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3 min-w-0">
        <h3 class="font-semibold text-gray-200 shrink-0">Merge Order</h3>
        <span id="fm-total-tokens" :class="tokenColorClass" class="text-sm font-mono pt-0.5 truncate" v-info="'fm_tokens'">
          ({{ listItems.length }} files, {{ totalTokens.toLocaleString() }} tokens)
        </span>
      </div>
      <div class="flex items-center space-x-2">
        <button
          id="btn-fm-order-request"
          @click="handleOrderClick"
          class="p-1.5 rounded border border-gray-600 enabled:hover:border-cm-blue text-gray-500 enabled:hover:text-cm-blue transition-colors relative"
          :class="{ 'click-pulse': isOrderPulseActive }"
          :style="isOrderPulseActive ? { '--click-color': '#DE680888' } : {}"
          title="Single-click: Copy request prompt | Ctrl+Click: Paste new order"
          v-info="'fm_order'"
        >
          <ArrowDownUp class="w-4 h-4" />
        </button>
        <button
          id="btn-fm-toggle-paths"
          @click="emit('update:showFullPaths', !showFullPaths)"
          class="p-1.5 rounded border transition-colors"
          :class="showFullPaths ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-500'"
          title="Toggle Path Visibility"
          v-info="'fm_list_tools'"
        >
          <Milestone class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Merge List -->
    <div class="flex-grow overflow-y-auto custom-scrollbar mb-2 pr-2" v-info="'fm_list'">
      <ul ref="listRoot" class="space-y-1">
        <li
          v-for="(file, index) in listItems"
          :key="file.path"
          v-show="matchesFilter(file.path)"
          v-info="'fm_list_item'"
          class="group flex items-center border rounded p-2 text-sm transition-all duration-300"
          :class="[
            selectedIndices.has(index) ? 'bg-cm-blue border-cm-blue' : 'bg-cm-input-bg border-gray-700 hover:border-gray-500',
            tempHighlightedPath === file.path ? 'ring-1 ring-cm-blue/50 bg-cm-blue/20 border-cm-blue/50' : ''
          ]"
          @click="handleFileClick(index, $event)"
          @dblclick="handleFileDoubleClick(index)"
          :title="`${file.path} (Double-click to open)`"
        >
          <div class="drag-handle cursor-grab active:cursor-grabbing mr-3 text-gray-600 group-hover:text-gray-400" @click.stop>
            <div class="grid grid-cols-2 gap-0.5 w-3">
              <div v-for="n in 6" :key="n" class="w-1 h-1 bg-current rounded-full"></div>
            </div>
          </div>

          <span class="flex-grow truncate pr-4" :class="selectedIndices.has(index) ? 'text-white font-medium' : 'text-gray-200'">
            {{ showFullPaths ? file.path : file.path.split('/').pop() }}
          </span>

          <div
            class="flex items-center space-x-3 shrink-0 cursor-help"
            @click="emit('token-interaction', index, $event)"
            title="Ctrl+Click: Copy refactor request | Alt+Click: Toggle Ignore tokens"
            v-info="'fm_tokens_item'"
          >
            <span class="text-xs font-mono" :class="selectedIndices.has(index) ? 'text-blue-100 font-bold' : getTokenColor(file)">
              {{ file.ignoreTokens ? `[${file.tokens?.toLocaleString()}]` : ((file.tokens !== undefined && file.tokens !== null && file.tokens >= 0) ? file.tokens.toLocaleString() : '?') }}
            </span>
          </div>
        </li>
      </ul>
      <div v-if="listItems.length === 0" class="h-full flex items-center justify-center text-gray-600 italic">
        No files selected to merge.
      </div>
    </div>

    <!-- Reorder Toolbar -->
    <div id="fm-reorder-toolbar" class="flex items-center justify-center space-x-2 pt-2">
      <button @click="moveSelectionToTop" v-info="'fm_sort_top'" class="p-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="selectedIndices.size === 0" title="Move Selected to Top"><ArrowUpToLine class="w-4 h-4" /></button>
      <button @click="moveSelectionUp" v-info="'fm_sort_up'" class="p-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="selectedIndices.size === 0" title="Move Selected Up"><ArrowUp class="w-4 h-4" /></button>
      <button @click="removeSelected" v-info="'fm_sort_remove'" class="px-5 py-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-red-900/50 enabled:hover:text-red-400 text-gray-400 disabled:opacity-30 text-sm font-medium transition-colors" :disabled="selectedIndices.size === 0" title="Remove Selected (Delete Key)">Remove</button>
      <button @click="moveSelectionDown" v-info="'fm_sort_down'" class="p-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="selectedIndices.size === 0" title="Move Selected Down"><ArrowDown class="w-4 h-4" /></button>
      <button @click="moveSelectionToBottom" v-info="'fm_sort_bottom'" class="p-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="selectedIndices.size === 0" title="Move Selected to Bottom"><ArrowDownToLine class="w-4 h-4" /></button>
    </div>
  </div>
</template>