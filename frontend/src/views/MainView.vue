<script setup>
import { onMounted, onUnmounted, ref, nextTick, computed } from 'vue'
import { useAppState } from '../composables/useAppState'
import ProjectSelectorModal from '../components/ProjectSelectorModal.vue'
import SettingsModal from '../components/SettingsModal.vue'
import FileManagerModal from '../components/FileManagerModal.vue'
import ReviewModal from '../components/ReviewModal.vue'
import InstructionsModal from '../components/InstructionsModal.vue'
import ProjectStarterModal from '../components/ProjectStarterModal.vue'
import NewProfileModal from '../components/NewProfileModal.vue'
import InfoPanel from '../components/InfoPanel.vue'
import {
  Settings, Copy, ClipboardPaste, BookOpen, PenLine, AlertTriangle, Eye, Loader2, Info
} from 'lucide-vue-next'

const {
  activeProject,
  lastAiResponse,
  statusMessage,
  statusVisible,
  showReviewModal,
  reviewMode,
  revertToCompactOnClose,
  planFileStates,
  planOriginalContents,
  logoMask,
  folderIcon,
  folderActiveIcon,
  starterIcon,
  starterActiveIcon,
  infoModeActive,
  toggleInfoMode,
  copyCode,
  renameProject,
  openProjectFolder,
  addAllNewFiles,
  clearUnknownFiles,
  selectColor,
  processPaste,
  copyCleanupPrompt,
  minimizeWindow,
  claimLastPlan,
  hasPendingChanges,
  switchProfile,
  deleteProfile
} = useAppState()

const showProjectModal = ref(false)
const showSettingsModal = ref(false)
const showFileManagerModal = ref(false)
const showInstructionsModal = ref(false)
const showStarterModal = ref(false)
const showNewProfileModal = ref(false)
const settingsTab = ref('application')

const cleanupPulse = ref(false)

// Loading states for copy buttons
const isCopyingInstructions = ref(false)
const isCopyingOnly = ref(false)

const isStarterHovered = ref(false)
const isFolderHovered = ref(false)

// Interaction state to distinguish between single and double clicks on the project title
let clickTimer = null

const handleTitleInteraction = () => {
  if (!activeProject.path) {
    showProjectModal.value = true
    return
  }

  if (clickTimer) {
    // Second click detected within 250ms -> Double Click (Rename)
    clearTimeout(clickTimer)
    clickTimer = null
    startEditing()
  } else {
    // First click -> Start timer for Single Click (Select Project)
    clickTimer = setTimeout(() => {
      clickTimer = null
      showProjectModal.value = true
    }, 250)
  }
}

// Title Editing State
const isEditingName = ref(false)
const tempName = ref('')
const nameInput = ref(null)

const startEditing = () => {
  tempName.value = activeProject.name
  isEditingName.value = true
  nextTick(() => {
    nameInput.value?.focus()
    nameInput.value?.select()
  })
}

const saveName = async () => {
  if (!isEditingName.value) return
  if (tempName.value.trim() && tempName.value !== activeProject.name) {
    await renameProject(tempName.value.trim())
  }
  isEditingName.value = false
}

const cancelEditing = () => {
  isEditingName.value = false
}

const openSettings = (tab = 'application') => {
  settingsTab.value = tab
  showSettingsModal.value = true
}

const openFileManager = async () => {
  showFileManagerModal.value = true
}

const handlePasteChanges = async () => {
  const success = await processPaste()
  if (success) {
    reviewMode.value = 'new'
    showReviewModal.value = true
  }
}

const openExistingReview = () => {
  reviewMode.value = 'resume'
  showReviewModal.value = true
}

const handleCleanup = async () => {
  cleanupPulse.value = true
  await copyCleanupPrompt()
  setTimeout(() => {
    cleanupPulse.value = false
  }, 450)
}

const handleNewFilesClick = async (event) => {
  if (event.ctrlKey) {
    await addAllNewFiles()
  } else {
    await openFileManager()
  }
}

const handleCopy = async (useWrapper) => {
  if (useWrapper) {
    isCopyingInstructions.value = true
  } else {
    isCopyingOnly.value = true
  }

  try {
    await copyCode(useWrapper)
  } finally {
    isCopyingInstructions.value = false
    isCopyingOnly.value = false
  }
}

// --- Profile Management ---
const prevProfile = async () => {
  const profiles = activeProject.profiles
  const idx = profiles.indexOf(activeProject.activeProfile)
  const prevIdx = (idx - 1 + profiles.length) % profiles.length
  await switchProfile(profiles[prevIdx])
}

const nextProfile = async () => {
  const profiles = activeProject.profiles
  const idx = profiles.indexOf(activeProject.activeProfile)
  const nextIdx = (idx + 1) % profiles.length
  await switchProfile(profiles[nextIdx])
}

const deleteProfileHandler = async () => {
  if (confirm(`Are you sure you want to delete the profile '${activeProject.activeProfile}'?\nThis cannot be undone.`)) {
    await deleteProfile(activeProject.activeProfile)
  }
}

// Robust Computed Style for the Project Swatch using the Base64 mask pipeline
const swatchStyle = computed(() => {
  if (!activeProject.path || !logoMask.value) return {}

  return {
    backgroundColor: activeProject.color,
    '-webkit-mask-image': `url(${logoMask.value})`,
    '-webkit-mask-size': 'contain',
    '-webkit-mask-repeat': 'no-repeat',
    '-webkit-mask-position': 'center',
    'mask-image': `url(${logoMask.value})`,
    'mask-size': 'contain',
    'mask-repeat': 'no-repeat',
    'mask-position': 'center'
  }
})

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

onMounted(() => {
  window.addEventListener('cm-remote-paste-request', onRemotePasteRequest)
})

onUnmounted(() => {
  window.removeEventListener('cm-remote-paste-request', onRemotePasteRequest)
})
</script>

<template>
  <div class="flex-grow flex flex-col overflow-hidden text-gray-100 bg-cm-dark-bg font-sans">
    <!-- Top Bar -->
    <header class="bg-cm-top-bar px-6 py-4 flex items-center justify-between border-b border-gray-700 h-[76px] shrink-0">
      <div class="flex items-center space-x-4 min-w-0 flex-grow">
        <!-- Masked Logo Swatch -->
        <div
          v-if="activeProject.path && logoMask"
          class="w-12 h-12 cursor-pointer shrink-0"
          :style="swatchStyle"
          @click="selectColor"
          v-info="'color_swatch'"
          title="Change project color"
        ></div>

        <!-- Fallback if mask not loaded -->
        <div
          v-else-if="activeProject.path"
          class="w-6 h-6 rounded cursor-pointer border border-gray-600 shadow-sm shrink-0"
          :style="{ backgroundColor: activeProject.color }"
          @click="selectColor"
          v-info="'color_swatch'"
          title="Change project color"
        ></div>

        <div class="flex items-center min-w-0 flex-grow text-white">
          <div v-if="isEditingName" class="flex items-center space-x-2 w-full max-w-md">
            <input
              ref="nameInput"
              v-model="tempName"
              @keyup.enter="saveName"
              @keyup.esc="cancelEditing"
              @blur="saveName"
              class="bg-cm-input-bg text-white border border-cm-blue rounded px-2 py-1 text-4xl font-thin tracking-[0.01em] w-full focus:outline-none"
            >
          </div>
          <div
            v-else
            class="flex items-center group cursor-pointer min-w-0"
            title="Click to select project, double-click to edit title"
            @click="handleTitleInteraction"
            v-info="'project_name'"
          >
            <h1 class="text-4xl font-thin tracking-[0.01em] whitespace-nowrap" :class="{'text-gray-500': !activeProject.path}">
              {{ activeProject.name || '(no active project)' }}
            </h1>
            <button
              v-if="activeProject.path"
              @click.stop="startEditing"
              class="shrink-0 p-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-white"
              title="Edit project title"
            >
              <PenLine class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center space-x-5 shrink-0 ml-4">
        <!-- New Files Alert (Syncs with background monitor thread) -->
        <div
          v-if="activeProject.newFileCount > 0 && !showFileManagerModal"
          class="flex items-center text-cm-green cursor-pointer hover:brightness-125 transition-all"
          title="New files found. Click: Open manager, Ctrl+Click: Add all to merge"
          @click="handleNewFilesClick($event)"
        >
          <AlertTriangle class="w-6 h-6" />
        </div>

        <!-- Folder Icon -->
        <img
          v-if="activeProject.path && folderIcon"
          :src="isFolderHovered ? (folderActiveIcon || folderIcon) : folderIcon"
          class="w-7 h-auto cursor-pointer transition-opacity"
          title="Open project folder (Ctrl+Click: Copy Path, Alt+Click: Open Console)"
          @click="openProjectFolder($event)"
          @mouseenter="isFolderHovered = true"
          @mouseleave="isFolderHovered = false"
          v-info="'folder_icon'"
        />
      </div>
    </header>

    <!-- Navigation Buttons Row -->
    <div class="px-6 py-5 flex items-center justify-between bg-cm-dark-bg shrink-0">
      <div class="flex items-center space-x-4">
        <button
          class="bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-2 px-6 rounded shadow-sm disabled:opacity-50 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors h-[38px]"
          :disabled="!activeProject.path"
          @click="openFileManager"
          v-info="'manage_files'"
        >
          Edit Merge List
        </button>

        <div class="flex items-center space-x-2" v-if="activeProject.path">
          <!-- Multi-profile navigator -->
          <div v-if="activeProject.profiles.length > 1" class="flex items-center" v-info="'profile_nav'">
            <button @click="prevProfile" class="w-7 h-[38px] bg-cm-input-bg text-gray-400 hover:text-white rounded-l border border-gray-600 border-r-0 flex items-center justify-center transition-colors" title="Previous Profile">&lt;</button>
            <span class="text-white bg-cm-input-bg px-4 py-2 text-sm font-medium border-y border-gray-600 h-[38px] flex items-center min-w-[80px] justify-center truncate">{{ activeProject.activeProfile }}</span>
            <button @click="nextProfile" class="w-7 h-[38px] bg-cm-input-bg text-gray-400 hover:text-white rounded-r border border-gray-600 border-l-0 flex items-center justify-center transition-colors" title="Next Profile">&gt;</button>
          </div>

          <!-- Single profile view -->
          <span v-else class="text-white bg-cm-input-bg px-4 py-2 rounded text-sm font-medium border border-gray-600 h-[38px] flex items-center truncate max-w-[120px]">{{ activeProject.activeProfile }}</span>

          <button @click="showNewProfileModal = true" class="border border-gray-500 hover:bg-gray-700 text-white w-9 h-[38px] rounded flex items-center justify-center font-bold transition-colors" title="Add Profile" v-info="'profile_add'">+</button>

          <button v-if="activeProject.profiles.length > 1 && activeProject.activeProfile !== 'Default'" @click="deleteProfileHandler" class="border border-gray-500 hover:bg-red-900/50 hover:text-red-400 hover:border-red-400 text-gray-300 w-9 h-[38px] rounded flex items-center justify-center font-bold transition-colors" title="Delete Profile" v-info="'profile_delete'">-</button>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <!-- Project Starter Icon Button -->
        <button
          class="hover:brightness-110 transition-all p-1 flex items-center justify-center"
          title="Project Starter"
          @mouseenter="isStarterHovered = true"
          @mouseleave="isStarterHovered = false"
          @click="showStarterModal = true"
          v-info="'starter'"
        >
          <img
            v-if="starterIcon"
            :src="isStarterHovered ? (starterActiveIcon || starterIcon) : starterIcon"
            class="w-7 h-7"
            alt="Project Starter"
          />
        </button>

        <button
          @click="showProjectModal = true"
          class="bg-cm-blue hover:bg-blue-500 text-white font-semibold py-2 px-6 rounded shadow-sm transition-colors h-[38px]"
          v-info="'select_project'"
        >
          Select Project
        </button>
      </div>
    </div>

    <!-- Main Dashboard Content -->
    <main class="flex-grow flex flex-col relative bg-cm-dark-bg min-h-0 overflow-y-auto">
      <div class="absolute bottom-4 left-6 flex flex-col">
        <button @click="openSettings('application')" class="text-gray-400 hover:text-white transition-colors" title="Settings" v-info="'settings'">
          <Settings class="w-7 h-7" />
        </button>
      </div>

      <div class="flex-grow flex items-center justify-center pb-4">
        <div v-if="activeProject.path" class="w-full max-w-[620px] border border-gray-600 rounded bg-cm-dark-bg p-6 flex flex-col shadow-sm">
          <div class="flex justify-between items-center mb-5">
            <h2 class="text-[17px] font-medium text-white">Actions</h2>
            <button
              @click="handleCleanup"
              class="text-gray-500 hover:text-gray-300 text-sm font-mono font-bold transition-colors relative"
              :class="{ 'click-pulse': cleanupPulse }"
              :style="cleanupPulse ? { '--click-color': 'rgba(255, 255, 255, 0.2)' } : {}"
              title="Copy comment cleanup prompt"
              v-info="'cleanup'"
            >
              //
            </button>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <!-- Conditional Copy Button Layout -->
            <template v-if="activeProject.hasInstructions">
              <button
                @click="handleCopy(true)"
                :disabled="isCopyingInstructions || isCopyingOnly"
                class="bg-cm-blue hover:bg-blue-500 text-white font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex flex-col items-center justify-center space-y-1 leading-tight disabled:opacity-50 disabled:cursor-not-allowed"
                title="Copy Prompt: includes code wrapped with custom intro/outro instructions"
                v-info="'copy_with_instructions'"
              >
                <Loader2 v-if="isCopyingInstructions" class="w-6 h-6 animate-spin" />
                <span v-else>Copy with Instructions</span>
              </button>
              <button
                @click="handleCopy(false)"
                :disabled="isCopyingInstructions || isCopyingOnly"
                class="bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex flex-col items-center justify-center space-y-1 leading-tight disabled:opacity-50 disabled:cursor-not-allowed"
                title="Copy Prompt: merges code and prepends the default context prompt"
                v-info="'copy_code'"
              >
                <Loader2 v-if="isCopyingOnly" class="w-6 h-6 animate-spin" />
                <span v-else>Copy Code Only</span>
              </button>
            </template>

            <template v-else>
              <button
                @click="handleCopy(false)"
                :disabled="isCopyingInstructions || isCopyingOnly"
                class="col-span-2 bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Copy Prompt: merges code and prepends the default context prompt"
                v-info="'copy_code'"
              >
                <Loader2 v-if="isCopyingOnly" class="w-6 h-6 animate-spin" />
                <template v-else>
                  <Copy class="w-5 h-5" />
                  <span>Copy Code Only</span>
                </template>
              </button>
            </template>

            <button
              @click="showInstructionsModal = true"
              class="self-start w-full bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-2.5 rounded shadow-sm flex items-center justify-center space-x-2 transition-colors text-[15px]"
              v-info="'instructions'"
            >
              <BookOpen class="w-4 h-4" />
              <span>Define Instructions</span>
            </button>

            <div class="flex flex-col space-y-4">
              <!-- Orange Attention styling when changes are pending in memory (Requirement) -->
              <button
                @click="handlePasteChanges"
                class="relative w-full text-white font-semibold py-2.5 rounded shadow-sm flex items-center justify-center space-x-2 transition-colors text-[15px]"
                :class="hasPendingChanges ? 'bg-[#DE6808] hover:bg-orange-500' : 'bg-cm-green hover:bg-green-600'"
                v-info="'paste_changes'"
              >
                <ClipboardPaste class="w-4 h-4" />
                <span>Paste Changes</span>
              </button>

              <button
                v-if="lastAiResponse"
                @click="openExistingReview"
                class="w-full bg-gray-600 hover:bg-gray-500 text-white font-semibold py-2.5 rounded shadow-sm flex items-center justify-center space-x-2 transition-colors text-[15px]"
                title="Review latest AI response"
                v-info="'response_review'"
              >
                <!-- Icon turns orange to signal unapplied work -->
                <Eye class="w-4 h-4" :class="hasPendingChanges ? 'text-[#DE6808]' : 'text-white'" />
                <span>AI Response Review</span>
              </button>
            </div>
          </div>
        </div>

        <div v-else class="mb-4 text-gray-500 text-[17px]">
          Select a project to get started
        </div>
      </div>
    </main>

    <!-- Shared Info Panel Component -->
    <InfoPanel />

    <!-- Global Status Bar -->
    <footer class="bg-cm-status-bg text-gray-300 px-6 py-2 flex items-center justify-between text-sm font-medium shrink-0 h-[36px] z-50">
      <div
        class="tracking-wide truncate pr-4"
        :class="statusVisible ? 'opacity-100' : 'opacity-0 transition-opacity duration-1000'"
      >
        {{ statusMessage }}
      </div>
      <button @click="toggleInfoMode" v-info="'info_toggle'" class="transition-colors shrink-0" :class="infoModeActive ? 'text-cm-blue hover:text-blue-400' : 'text-gray-400 hover:text-white'" title="Toggle Info Mode">
        <Info class="w-5 h-5" />
      </button>
    </footer>

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