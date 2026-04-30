<script setup>
import { ref, onMounted } from 'vue'
import { useAppState } from '../composables/useAppState'
import { useEscapeKey } from '../composables/useEscapeKey'
import { useFileManager } from '../composables/useFileManager'
import { WINDOW_SIZES } from '../utils/constants'

import FileManagerLeftPanel from './FileManagerLeftPanel.vue'
import FileManagerRightPanel from './FileManagerRightPanel.vue'
import FileManagerHeader from './file-manager/FileManagerHeader.vue'
import FileManagerFooter from './file-manager/FileManagerFooter.vue'
import OrderErrorModal from './OrderErrorModal.vue'

const emit = defineEmits(['close'])
const { activeProject, resizeWindow, clearUnknownFiles, statusMessage, showOrderErrorModal, orderErrorMessage } = useAppState()

const {
  mergeListRef, listItems, fileTree, filterText, isExtFilter, isGitFilter,
  showFullPaths, currentExpandedDirs, isTreeLoading, isOrderPulseActive,
  highlightedPath, totalTokens, tokenColorClass, hasUnsavedChanges,
  refreshTree, autoHandleNewFiles, toggleFileSelect, toggleDirectorySelect,
  addAll, handleOrderRequest, handleSave
} = useFileManager()

const leftPanelRef = ref(null)
const rightPanelRef = ref(null)

useEscapeKey(() => {
  if (showOrderErrorModal.value) { showOrderErrorModal.value = false; return }
  handleCancel()
})

onMounted(async () => {
  await resizeWindow(WINDOW_SIZES.FILE_MANAGER.width, WINDOW_SIZES.FILE_MANAGER.height)
  await refreshTree()
  await autoHandleNewFiles()
  await clearUnknownFiles()
})

const handleCancel = () => {
  if (hasUnsavedChanges.value && !confirm('You have unsaved changes. Discard them?')) return
  emit('close')
}

const handleTokenInteraction = (index, event) => {
  const item = listItems.value[index]
  if (!item) return
  if (event.altKey) {
    item.ignoreTokens = !item.ignoreTokens
  } else if (event.ctrlKey) {
    window.pywebview.api.get_split_file_prompt(item.path).then(breakupMsg => {
      navigator.clipboard.writeText(breakupMsg)
      statusMessage.value = `Copied breakup request for ${item.path.split('/').pop()}`
    })
  }
}
</script>

<template>
  <div id="file-manager-modal" class="absolute inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
    <div class="bg-cm-dark-bg w-full max-w-6xl h-full max-h-[90vh] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden relative">

      <OrderErrorModal v-if="showOrderErrorModal" :message="orderErrorMessage" @close="showOrderErrorModal = false" />

      <FileManagerHeader :projectName="activeProject.name" @close="handleCancel" />

      <div class="flex-grow flex min-0 overflow-hidden">
        <FileManagerLeftPanel
          ref="leftPanelRef"
          :class="showFullPaths ? 'w-2/5' : 'w-1/2'"
          :fileTree="fileTree"
          v-model:isExtFilter="isExtFilter"
          v-model:isGitFilter="isGitFilter"
          :selectedPaths="listItems.map(f => f.path)"
          :expandedDirs="currentExpandedDirs"
          :highlightedPath="highlightedPath"
          :isLoading="isTreeLoading"
          @toggle-select="p => toggleFileSelect(p, rightPanelRef)"
          @toggle-directory="n => toggleDirectorySelect(n, rightPanelRef)"
          @remove-select="p => { const idx = listItems.findIndex(f => f.path === p); if (idx !== -1) listItems.splice(idx, 1) }"
          @file-click="p => rightPanelRef?.scrollToPath(p)"
          @toggle-expand="data => { if (data.expanded) currentExpandedDirs.add(data.path); else currentExpandedDirs.delete(data.path) }"
          @add-all="addAll(rightPanelRef)"
        />

        <FileManagerRightPanel
          ref="rightPanelRef"
          :class="showFullPaths ? 'w-3/5' : 'w-1/2'"
          :listItems="listItems"
          :filterText="filterText"
          :setListRef="el => mergeListRef = el"
          :totalTokens="totalTokens"
          :tokenColorClass="tokenColorClass"
          v-model:showFullPaths="showFullPaths"
          :isOrderPulseActive="isOrderPulseActive"
          @file-click="p => highlightedPath = p"
          @token-interaction="handleTokenInteraction"
          @order-request="handleOrderRequest"
        />
      </div>

      <FileManagerFooter
        v-model:filterText="filterText"
        :hasUnsavedChanges="hasUnsavedChanges"
        @save="handleSave(() => emit('close'))"
        @cancel="handleCancel"
      />

    </div>
  </div>
</template>