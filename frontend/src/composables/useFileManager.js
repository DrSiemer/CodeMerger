import { ref, watch, computed, nextTick } from 'vue'
import { useAppState } from './useAppState'
import { useDragAndDrop } from '@formkit/drag-and-drop/vue'

export function useFileManager() {
  const {
    activeProject, getFileTree, updateProjectFiles,
    copyOrderRequest, statusMessage, config
  } = useAppState()

  const IGNORED_FOR_COMPLETENESS = ['__init__.py']

  // --- DND Setup ---
  const [mergeListRef, listItems] = useDragAndDrop(
    JSON.parse(JSON.stringify(activeProject.selectedFiles)),
    { handle: '.drag-handle' }
  )

  // --- State ---
  const fileTree = ref([])
  const filterText = ref('')
  const isExtFilter = ref(true)
  const isGitFilter = ref(true)
  const showFullPaths = ref(false)
  const currentExpandedDirs = ref(new Set(activeProject.expandedDirs))
  const isTreeLoading = ref(false)
  const isOrderPulseActive = ref(false)
  const highlightedPath = ref(null)
  const lastRequestId = ref(0)

  // --- Tree Scanning & Search ---
  const refreshTree = async () => {
    const requestId = ++lastRequestId.value
    if (!fileTree.value.length) isTreeLoading.value = true

    try {
      const currentPaths = listItems.value.map(f => f.path)
      const result = await getFileTree(filterText.value, isExtFilter.value, isGitFilter.value, currentPaths)
      if (requestId !== lastRequestId.value) return
      fileTree.value = result
    } finally {
      if (requestId === lastRequestId.value) isTreeLoading.value = false
    }
  }

  const debounce = (fn, delay) => {
    let timeout
    return (...args) => {
      clearTimeout(timeout)
      timeout = setTimeout(() => fn(...args), delay)
    }
  }
  const debouncedRefresh = debounce(refreshTree, 200)

  const autoHandleNewFiles = async () => {
    const newFiles = []
    const traverse = (nodes) => {
      nodes.forEach(node => {
        if (node.type === 'file' && node.is_new) {
          newFiles.push(node.path)
          const parts = node.path.split('/')
          let currentPath = ''
          for (let i = 0; i < parts.length - 1; i++) {
            currentPath += (i === 0 ? '' : '/') + parts[i]
            currentExpandedDirs.value.add(currentPath)
          }
        }
        if (node.children) traverse(node.children)
      })
    }
    traverse(fileTree.value)
    if (newFiles.length > 0) {
      newFiles.sort()
      const firstTargetId = `node-${newFiles[0].replace(/[\\/.]/g, '-')}`
      await nextTick()
      setTimeout(() => {
        const el = document.getElementById(firstTargetId)
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 100)
    }
  }

  // --- Selection Logic ---
  const toggleFileSelect = (path, rightPanelRef) => {
    highlightedPath.value = null
    const existingIdx = listItems.value.findIndex(f => f.path === path)

    if (existingIdx !== -1) {
      listItems.value.splice(existingIdx, 1)
      rightPanelRef?.clearSelection()
    } else {
      window.pywebview.api.get_token_count(path).then(tokens => {
        if (listItems.value.findIndex(f => f.path === path) === -1) {
          listItems.value.push({ path, tokens, ignoreTokens: false })
          nextTick(() => { rightPanelRef?.scrollToPath(path) })
        }
      })
    }
  }

  const toggleDirectorySelect = async (node, rightPanelRef) => {
    highlightedPath.value = null
    const subtreeFiles = []
    const traverse = (n) => {
      if (n.type === 'file' && !IGNORED_FOR_COMPLETENESS.includes(n.name)) subtreeFiles.push(n.path)
      if (n.children) n.children.forEach(traverse)
    }
    traverse(node)
    if (subtreeFiles.length === 0) return

    const currentPaths = new Set(listItems.value.map(f => f.path))
    const isFullySelected = subtreeFiles.every(p => currentPaths.has(p))

    if (isFullySelected) {
      const pathsToRemove = new Set(subtreeFiles)
      for (let i = listItems.value.length - 1; i >= 0; i--) {
        if (pathsToRemove.has(listItems.value[i].path)) listItems.value.splice(i, 1)
      }
      rightPanelRef?.clearSelection()
    } else {
      const toAdd = subtreeFiles.filter(p => !currentPaths.has(p))
      for (const path of toAdd) {
        const tokens = await window.pywebview.api.get_token_count(path)
        if (listItems.value.findIndex(f => f.path === path) === -1) {
          listItems.value.push({ path, tokens, ignoreTokens: false })
        }
      }
      if (toAdd.length > 0) {
        nextTick(() => { rightPanelRef?.scrollToPath(toAdd[toAdd.length - 1]) })
      }
    }
  }

  const addAll = async (rightPanelRef) => {
    highlightedPath.value = null
    const allFiles = []
    const traverse = (nodes) => {
      for (const node of nodes) {
        if (node.type === 'file' && !IGNORED_FOR_COMPLETENESS.includes(node.name)) allFiles.push(node.path)
        if (node.children) traverse(node.children)
      }
    }
    traverse(fileTree.value)
    const currentPaths = new Set(listItems.value.map(f => f.path))
    const toAdd = allFiles.filter(p => !currentPaths.has(p))
    const threshold = config.value.add_all_warning_threshold || 50
    if (toAdd.length > threshold && !confirm(`Add ${toAdd.length} files to list?`)) return

    for (const path of toAdd) {
      const tokens = await window.pywebview.api.get_token_count(path)
      if (listItems.value.findIndex(f => f.path === path) === -1) {
        listItems.value.push({ path, tokens, ignoreTokens: false })
      }
    }
    if (toAdd.length > 0) {
      nextTick(() => { rightPanelRef?.scrollToPath(toAdd[toAdd.length - 1]) })
    }
  }

  // --- Tokens & Order ---
  const totalTokens = computed(() => {
    return listItems.value.reduce((acc, f) => {
      if (!f || f.ignoreTokens) return acc
      return acc + (f.tokens || 0)
    }, 0)
  })

  const tokenColorClass = computed(() => {
    const limit = activeProject.tokenLimit || 0
    if (limit > 0 && totalTokens.value > limit) return 'text-cm-warn'
    return 'text-gray-400'
  })

  const handleOrderRequest = async () => {
    if (listItems.value.length === 0) return
    const success = await copyOrderRequest(JSON.parse(JSON.stringify(listItems.value)))
    if (success) {
      isOrderPulseActive.value = true
      setTimeout(() => { isOrderPulseActive.value = false }, 450)
    }
  }

  const hasUnsavedChanges = computed(() => {
    if (listItems.value.length !== activeProject.selectedFiles.length) return true
    for (let i = 0; i < listItems.value.length; i++) {
      const cur = listItems.value[i]
      const orig = activeProject.selectedFiles[i]
      if (cur.path !== orig.path || cur.ignoreTokens !== orig.ignoreTokens) return true
    }
    if (currentExpandedDirs.value.size !== activeProject.expandedDirs.length) return true
    for (const path of activeProject.expandedDirs) {
      if (!currentExpandedDirs.value.has(path)) return true
    }
    return false
  })

  const handleSave = async (onDone) => {
    await updateProjectFiles(listItems.value, totalTokens.value, Array.from(currentExpandedDirs.value))
    onDone()
  }

  // --- Watchers ---
  watch(filterText, () => { highlightedPath.value = null; debouncedRefresh() })
  watch([isExtFilter, isGitFilter], () => { highlightedPath.value = null; refreshTree() })

  return {
    mergeListRef, listItems, fileTree, filterText, isExtFilter, isGitFilter,
    showFullPaths, currentExpandedDirs, isTreeLoading, isOrderPulseActive,
    highlightedPath, totalTokens, tokenColorClass, hasUnsavedChanges,
    refreshTree, autoHandleNewFiles, toggleFileSelect, toggleDirectorySelect,
    addAll, handleOrderRequest, handleSave
  }
}