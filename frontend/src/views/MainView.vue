<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useAppState } from '../composables/useAppState'
import DashboardHeader from '../components/dashboard/DashboardHeader.vue'
import DashboardNav from '../components/dashboard/DashboardNav.vue'
import DashboardActions from '../components/dashboard/DashboardActions.vue'
import ProjectSelectorModal from '../components/ProjectSelectorModal.vue'
import SettingsModal from '../components/SettingsModal.vue'
import FileManagerModal from '../components/FileManagerModal.vue'
import ReviewModal from '../components/ReviewModal.vue'
import InstructionsModal from '../components/InstructionsModal.vue'
import ProjectStarterModal from '../components/ProjectStarterModal.vue'
import NewProfileModal from '../components/NewProfileModal.vue'

const {
  activeProject,
  lastAiResponse,
  revertToCompactOnClose,
  planFileStates,
  planOriginalContents,
  minimizeWindow,
  claimLastPlan,
  processPaste,
  applyFullPlan,
  config,
  statusMessage
} = useAppState()

const showProjectModal = ref(false)
const showSettingsModal = ref(false)
const showFileManagerModal = ref(false)
const showInstructionsModal = ref(false)
const showStarterModal = ref(false)
const showNewProfileModal = ref(false)
const settingsTab = ref('application')

const showReviewModal = ref(false)
const reviewMode = ref('new')

const openSettings = (tab = 'application') => {
  settingsTab.value = tab
  showSettingsModal.value = true
}

const openReviewModal = (mode) => {
  reviewMode.value = mode
  showReviewModal.value = true
}

const closeReviewModal = () => {
  showReviewModal.value = false
  if (revertToCompactOnClose.value) {
    revertToCompactOnClose.value = false
    minimizeWindow()
  }
}

/**
 * Handles paste handoff requests originating from the Compact window context.
 */
const onRemotePasteRequest = async (event) => {
  const { revertOnClose } = event.detail

  // Claim the pre-parsed plan from the Python session state
  const plan = await claimLastPlan()
  if (!plan) return

  // Handle parsing errors claimed from compact mode via standard alert (dashboard flow)
  if (plan.status === 'ERROR') {
    alert(plan.message)
    return
  }

  lastAiResponse.value = plan
  revertToCompactOnClose.value = revertOnClose
  reviewMode.value = 'new'

  // Reset Review State for new plan
  planFileStates.value = {}
  planOriginalContents.value = {}

  const updates = plan.updates || {}
  const creations = plan.creations || {}
  const deletions = plan.deletions_proposed || []
  const skipped = plan.skipped_files || []

  // Initialize handled states, accounting for byte-for-byte identical files
  Object.keys(updates).forEach(p => planFileStates.value[p] = skipped.includes(p) ? 'skipped' : 'pending')
  Object.keys(creations).forEach(p => planFileStates.value[p] = 'pending')
  deletions.forEach(p => planFileStates.value[p] = skipped.includes(p) ? 'skipped' : 'pending')

  showReviewModal.value = true
}

/**
 * Handles global keyboard shortcuts dispatched from App.vue
 */
const handleShortcutPaste = async (event) => {
  if (!activeProject.path) return

  const { toggleReview } = event.detail
  const success = await processPaste()

  if (success) {
    const autoShow = config.value.show_feedback_on_paste ?? true
    // toggleReview (Shift+Ctrl+V) does the opposite of current settings
    const shouldShow = toggleReview ? !autoShow : autoShow

    if (shouldShow) {
      reviewMode.value = 'new'
      showReviewModal.value = true
    } else {
      // Instant Apply
      const res = await applyFullPlan(lastAiResponse.value)
      if (res && res[0]) {
        statusMessage.value = res[1]
      }
    }
  }
}

onMounted(() => {
  window.addEventListener('cm-remote-paste-request', onRemotePasteRequest)
  window.addEventListener('cm-shortcut-paste', handleShortcutPaste)
})

onUnmounted(() => {
  window.removeEventListener('cm-remote-paste-request', onRemotePasteRequest)
  window.removeEventListener('cm-shortcut-paste', handleShortcutPaste)
})
</script>

<template>
  <div id="dashboard-view" class="flex-grow flex flex-col overflow-hidden text-gray-100 bg-cm-dark-bg font-sans relative">
    <!-- Top Bar -->
    <DashboardHeader
      :is-file-manager-open="showFileManagerModal"
      @open-project-modal="showProjectModal = true"
      @open-file-manager="showFileManagerModal = true"
    />

    <!-- Navigation Buttons Row -->
    <DashboardNav
      @open-file-manager="showFileManagerModal = true"
      @open-new-profile-modal="showNewProfileModal = true"
      @open-starter-modal="showStarterModal = true"
      @open-project-modal="showProjectModal = true"
    />

    <!-- Main Dashboard Content -->
    <DashboardActions
      @open-settings="openSettings"
      @open-instructions-modal="showInstructionsModal = true"
      @open-review-modal="openReviewModal"
    />

    <!-- Modal Layers -->
    <ProjectSelectorModal v-if="showProjectModal" @close="showProjectModal = false" />
    <SettingsModal v-if="showSettingsModal" :initial-tab="settingsTab" @close="showSettingsModal = false" />
    <FileManagerModal v-if="showFileManagerModal" @close="showFileManagerModal = false" />
    <ReviewModal v-if="showReviewModal" :mode="reviewMode" @close="closeReviewModal" />
    <InstructionsModal v-if="showInstructionsModal" @close="showInstructionsModal = false" />
    <ProjectStarterModal v-if="showStarterModal" @close="showStarterModal = false" />
    <NewProfileModal v-if="showNewProfileModal" @close="showNewProfileModal = false" />
  </div>
</template>