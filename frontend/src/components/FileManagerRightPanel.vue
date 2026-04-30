<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useAppState } from '../composables/useAppState'
import { DEFAULT_TOKEN_COLOR_THRESHOLD } from '../utils/constants'
import MergeListToolbar from './file-manager/MergeListToolbar.vue'
import MergeListItem from './file-manager/MergeListItem.vue'
import ReorderToolbar from './file-manager/ReorderToolbar.vue'

const props = defineProps({
  listItems: Array,
  filterText: String,
  setListRef: Function,
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

const listRoot = ref(null)
const tempHighlightedPath = ref(null)
let highlightTimeout = null

const handleListRef = (el) => {
  listRoot.value = el
  if (props.setListRef) props.setListRef(el)
}

const onKeyDown = (e) => {
  if (e.key === 'Delete' && selectedIndices.value.size > 0) {
    const target = e.target
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return
    e.preventDefault()
    removeSelected()
  }
}

onMounted(() => { window.addEventListener('keydown', onKeyDown) })
onUnmounted(() => { window.removeEventListener('keydown', onKeyDown) })

const maxTokensInList = computed(() => {
  const tokenValues = props.listItems
    .filter(f => f && !f.ignoreTokens)
    .map(f => f.tokens || 0)
  const rangeMax = config.value.token_color_threshold || DEFAULT_TOKEN_COLOR_THRESHOLD
  return tokenValues.length > 0 ? Math.max(...tokenValues, rangeMax) : rangeMax
})

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

const handleOrderClick = (event) => {
  if (event.ctrlKey) handlePasteOrder()
  else emit('order-request')
}

const handlePasteOrder = async () => {
  if (props.listItems.length === 0) {
    statusMessage.value = "Merge order is empty, nothing to reorder."
    return
  }

  try {
    const pastedText = await getClipboardText()
    if (!pastedText || !pastedText.trim()) {
      statusMessage.value = "Clipboard is empty."
      return
    }

    const startIdx = pastedText.indexOf('[')
    const endIdx = pastedText.lastIndexOf(']')
    if (startIdx === -1 || endIdx === -1) throw new Error("Could not find a JSON array in the response.")

    const jsonStr = pastedText.substring(startIdx, endIdx + 1)
    const newOrderList = JSON.parse(jsonStr)

    if (!Array.isArray(newOrderList)) throw new Error("Parsed JSON is not a list.")

    const currentPathsSet = new Set(props.listItems.map(f => f.path))
    const newPathsSet = new Set(newOrderList)

    const missingFiles = [...currentPathsSet].filter(p => !newPathsSet.has(p))
    const unknownFiles = [...newPathsSet].filter(p => !currentPathsSet.has(p))
    const duplicates = newOrderList.filter((item, index) => newOrderList.indexOf(item) !== index)

    if (missingFiles.length || unknownFiles.length || duplicates.length) {
      let errorParts = []
      if (missingFiles.length) errorParts.push(`Missing Files:\n${JSON.stringify(missingFiles.sort(), null, 2)}`)
      if (unknownFiles.length) errorParts.push(`Unknown Files:\n${JSON.stringify(unknownFiles.sort(), null, 2)}`)
      if (duplicates.length) errorParts.push(`Duplicate Entries Found:\n${JSON.stringify([...new Set(duplicates)].sort(), null, 2)}`)

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
    if (selectedEl) selectedEl.scrollIntoView({ behavior: 'smooth', block: alignToTop ? 'start' : 'nearest' })
  })
}

const scrollToPath = (path) => {
  const index = props.listItems.findIndex(f => f.path === path)
  if (index === -1) return
  tempHighlightedPath.value = path
  if (highlightTimeout) clearTimeout(highlightTimeout)
  highlightTimeout = setTimeout(() => { tempHighlightedPath.value = null }, 2000)

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      const listEl = listRoot.value
      if (!listEl) return
      const items = listEl.querySelectorAll('li')
      if (items[index]) items[index].scrollIntoView({ behavior: 'smooth', block: 'center' })
    })
  })
}

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
    <MergeListToolbar
      :fileCount="listItems.length"
      :totalTokens="totalTokens"
      :tokenColorClass="tokenColorClass"
      :showFullPaths="showFullPaths"
      :isOrderPulseActive="isOrderPulseActive"
      @update:showFullPaths="$emit('update:showFullPaths', $event)"
      @order-click="handleOrderClick"
    />

    <div class="flex-grow overflow-y-auto custom-scrollbar mb-2 pr-2" v-info="'fm_list'">
      <ul :ref="handleListRef" class="space-y-1">
        <MergeListItem
          v-for="(file, index) in listItems"
          :key="file.path"
          :file="file"
          :index="index"
          :isSelected="selectedIndices.has(index)"
          :isHighlighted="tempHighlightedPath === file.path"
          :showFullPaths="showFullPaths"
          :filterText="filterText"
          :maxTokensInList="maxTokensInList"
          @click="handleFileClick(index, $event)"
          @dblclick="openFile(file.path)"
          @token-interaction="emit('token-interaction', index, $event)"
        />
      </ul>
      <div v-if="listItems.length === 0" class="h-full flex items-center justify-center text-gray-600 italic">
        No files selected to merge.
      </div>
    </div>

    <ReorderToolbar
      :hasSelection="selectedIndices.size > 0"
      @top="moveSelectionToTop"
      @up="moveSelectionUp"
      @remove="removeSelected"
      @down="moveSelectionDown"
      @bottom="moveSelectionToBottom"
    />
  </div>
</template>