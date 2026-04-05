<script setup>
import { onMounted, ref, nextTick } from 'vue'
import { useAppState } from './composables/useAppState'
import ProjectSelectorModal from './components/ProjectSelectorModal.vue'
import SettingsModal from './components/SettingsModal.vue'
import {
  Settings, Copy, ClipboardPaste, BookOpen, Info, PenLine
} from 'lucide-vue-next'

const { activeProject, statusMessage, init, copyCode, renameProject, getImage } = useAppState()

const showProjectModal = ref(false)
const showSettingsModal = ref(false)
const settingsTab = ref('application')

// Image Assets
const starterIcon = ref('')
const starterActiveIcon = ref('')
const isStarterHovered = ref(false)

const folderIcon = ref('')
const folderActiveIcon = ref('')
const isFolderHovered = ref(false)

// Interaction state
let clickTimer = null

// Title Editing State
const isEditingName = ref(false)
const tempName = ref('')
const nameInput = ref(null)

const handleTitleInteraction = () => {
  if (!activeProject.path) return

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

const loadAssets = async () => {
  starterIcon.value = await getImage('project_starter.png')
  starterActiveIcon.value = await getImage('project_starter_active.png')
  folderIcon.value = await getImage('folder.png')
  folderActiveIcon.value = await getImage('folder_active.png')
}

onMounted(() => {
  if (window.pywebview) {
    init()
    loadAssets()
  } else {
    window.addEventListener('pywebviewready', () => {
      init()
      loadAssets()
    })
  }
})
</script>

<template>
  <div class="h-screen w-screen bg-cm-dark-bg text-gray-100 flex flex-col font-sans selection:bg-cm-blue selection:text-white overflow-hidden">
    <!-- Top Bar -->
    <header class="bg-cm-top-bar px-6 py-4 flex items-center justify-between border-b border-gray-700 h-[76px] shrink-0">
      <div class="flex items-center space-x-4 min-w-0 flex-grow">
        <!-- Color Swatch -->
        <div
          v-if="activeProject.path"
          class="w-6 h-6 rounded cursor-pointer border border-gray-600 shadow-sm shrink-0"
          :style="{ backgroundColor: activeProject.color }"
          title="Change project color"
        ></div>

        <!-- Title & Rename Logic -->
        <div class="flex items-center min-w-0 flex-grow text-white">
          <div v-if="isEditingName" class="flex items-center space-x-2 w-full max-w-md">
            <input
              ref="nameInput"
              v-model="tempName"
              @keyup.enter="saveName"
              @keyup.esc="cancelEditing"
              @blur="saveName"
              class="bg-cm-input-bg text-white border border-cm-blue rounded px-2 py-1 text-2xl font-bold w-full focus:outline-none"
            >
          </div>
          <div
            v-else
            class="flex items-center group cursor-pointer min-w-0"
            title="Click to select project, double-click to edit title"
            @click="handleTitleInteraction"
          >
            <h1 class="text-2xl font-bold tracking-tight truncate" :class="{'text-gray-500': !activeProject.path}">
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

      <!-- Right-aligned Header Actions -->
      <div class="flex items-center space-x-5 shrink-0 ml-4">
        <!-- Folder Icon -->
        <img
          v-if="activeProject.path && folderIcon"
          :src="isFolderHovered ? folderActiveIcon : folderIcon"
          class="w-7 h-auto cursor-pointer transition-opacity"
          title="Open project folder"
          @mouseenter="isFolderHovered = true"
          @mouseleave="isFolderHovered = false"
        />
      </div>
    </header>

    <!-- Navigation Buttons Row -->
    <div class="px-6 py-5 flex items-center justify-between bg-cm-dark-bg shrink-0">
      <div class="flex items-center space-x-4">
        <button
          class="bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-2 px-6 rounded shadow-sm disabled:opacity-50 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors h-[38px]"
          :disabled="!activeProject.path"
        >
          Edit Merge List
        </button>

        <!-- Profiles -->
        <div class="flex items-center space-x-2" v-if="activeProject.path">
          <span class="text-white bg-cm-input-bg px-4 py-2 rounded text-sm font-medium border border-gray-600 h-[38px] flex items-center">Default</span>
          <button class="border border-gray-500 hover:bg-gray-700 text-white w-9 h-9 rounded flex items-center justify-center font-bold transition-colors" title="Add Profile">+</button>
        </div>
      </div>

      <div class="flex items-center space-x-6">
        <button
          v-if="starterIcon"
          class="hover:opacity-80 transition-opacity p-1"
          title="Launch Project Starter Wizard"
          @mouseenter="isStarterHovered = true"
          @mouseleave="isStarterHovered = false"
        >
          <img :src="isStarterHovered ? starterActiveIcon : starterIcon" class="w-7 h-7" />
        </button>
        <button
          @click="showProjectModal = true"
          class="bg-cm-blue hover:bg-blue-500 text-white font-semibold py-2 px-6 rounded shadow-sm transition-colors h-[38px]"
        >
          Select Project
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <main class="flex-grow flex flex-col relative bg-cm-dark-bg">
      <!-- Bottom-Left Tools -->
      <div class="absolute bottom-4 left-6 flex flex-col">
        <button @click="openSettings('application')" class="text-gray-400 hover:text-white transition-colors" title="Settings">
          <Settings class="w-7 h-7" />
        </button>
      </div>

      <!-- Actions Box Container -->
      <div class="flex-grow flex items-center justify-center pb-4">
        <div v-if="activeProject.path" class="w-full max-w-[620px] border border-gray-600 rounded bg-cm-dark-bg p-6 flex flex-col shadow-sm">
          <div class="flex justify-between items-center mb-5">
            <h2 class="text-[17px] font-medium text-white">Actions</h2>
            <button class="text-gray-500 hover:text-gray-300 text-sm font-mono font-bold transition-colors" title="Copy comment cleanup prompt">//</button>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <!-- Conditional Copy Button Layout -->
            <template v-if="activeProject.hasInstructions">
              <button
                @click="copyCode(true)"
                class="bg-cm-blue hover:bg-blue-500 text-white font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex flex-col items-center justify-center space-y-1 leading-tight"
                title="Copy Prompt: includes code wrapped with custom intro/outro instructions"
              >
                <span>Copy with Instructions</span>
              </button>
              <button
                @click="copyCode(false)"
                class="bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex flex-col items-center justify-center space-y-1 leading-tight"
                title="Copy Prompt: merges code and prepends the default context prompt"
              >
                <span>Copy Code Only</span>
              </button>
            </template>

            <template v-else>
              <button
                @click="copyCode(false)"
                class="col-span-2 bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-[22px] rounded shadow-sm text-lg transition-colors flex items-center justify-center space-x-2"
                title="Copy Prompt: merges code and prepends the default context prompt"
              >
                <Copy class="w-5 h-5" />
                <span>Copy Code Only</span>
              </button>
            </template>

            <!-- Small Buttons -->
            <button class="bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-2.5 rounded shadow-sm flex items-center justify-center space-x-2 transition-colors text-[15px]">
              <BookOpen class="w-4 h-4" />
              <span>Define Instructions</span>
            </button>
            <button class="bg-cm-green hover:bg-green-600 text-white font-semibold py-2.5 rounded shadow-sm flex items-center justify-center space-x-2 transition-colors text-[15px]">
              <ClipboardPaste class="w-4 h-4" />
              <span>Paste Changes</span>
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="mb-4 text-gray-500 text-[17px]">
          Select a project to get started
        </div>
      </div>
    </main>

    <!-- Status Bar -->
    <footer class="bg-cm-status-bg text-gray-300 px-6 py-2 flex items-center justify-between text-sm font-medium shrink-0 h-[36px]">
      <div class="tracking-wide truncate pr-4">{{ statusMessage }}</div>
      <button class="text-gray-400 hover:text-white transition-colors shrink-0" title="Toggle Info Mode">
        <Info class="w-5 h-5" />
      </button>
    </footer>

    <!-- Modals -->
    <ProjectSelectorModal
      v-if="showProjectModal"
      @close="showProjectModal = false"
    />
    <SettingsModal
      v-if="showSettingsModal"
      :initial-tab="settingsTab"
      @close="showSettingsModal = false"
    />
  </div>
</template>