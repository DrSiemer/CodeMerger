<script setup>
import { onMounted, ref } from 'vue'
import { useAppState } from './composables/useAppState'
import ProjectSelectorModal from './components/ProjectSelectorModal.vue'
import SettingsModal from './components/SettingsModal.vue'
import {
  FolderOpen, PenLine, Settings, Play,
  Copy, ClipboardPaste, BookOpen, Info
} from 'lucide-vue-next'

const { config, activeProject, statusMessage, init, copyCode } = useAppState()

const showProjectModal = ref(false)
const showSettingsModal = ref(false)
const settingsTab = ref('application')

const openSettings = (tab = 'application') => {
  settingsTab.value = tab
  showSettingsModal.value = true
}

onMounted(() => {
  // Safe initialization depending on PyWebView injection timing
  if (window.pywebview) {
    init()
  } else {
    window.addEventListener('pywebviewready', () => {
      init()
    })
  }
})
</script>

<template>
  <div class="min-h-screen bg-cm-dark-bg text-gray-100 flex flex-col font-sans selection:bg-cm-blue selection:text-white">
    <!-- Top Bar -->
    <header class="bg-cm-top-bar px-6 py-4 flex items-center justify-between border-b border-gray-700 h-[76px]">
      <div class="flex items-center space-x-4">
        <!-- Color Swatch -->
        <div
          v-if="activeProject.path"
          class="w-6 h-6 rounded cursor-pointer border border-gray-600 shadow-sm"
          :style="{ backgroundColor: activeProject.color }"
          title="Change project color"
        ></div>

        <!-- Title -->
        <div
          class="flex items-center group cursor-pointer"
          title="Click to select project, double-click to edit title"
          @click="showProjectModal = true"
        >
          <h1 class="text-2xl font-bold tracking-tight" :class="{'text-gray-500': !activeProject.path}">
            {{ activeProject.name || '(no active project)' }}
          </h1>
          <PenLine v-if="activeProject.path" class="w-4 h-4 ml-3 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400" />
        </div>

        <!-- Folder Icon -->
        <FolderOpen
          v-if="activeProject.path"
          class="w-6 h-6 ml-2 text-gray-400 hover:text-white cursor-pointer transition-colors"
          title="Open project folder"
        />
      </div>

      <div class="flex items-center space-x-4">
        <!-- New Files Alert will go here -->
      </div>
    </header>

    <!-- Top Buttons -->
    <div class="px-6 py-5 flex items-center justify-between bg-cm-dark-bg">
      <div class="flex items-center space-x-4">
        <button
          class="bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-2 px-6 rounded shadow-sm disabled:opacity-50 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          :disabled="!activeProject.path"
        >
          Edit Merge List
        </button>

        <!-- Profiles -->
        <div class="flex items-center space-x-2" v-if="activeProject.path">
          <span class="text-white bg-cm-input-bg px-4 py-2 rounded text-sm font-medium border border-gray-600">Default</span>
          <button class="border border-gray-500 hover:bg-gray-700 text-white w-9 h-9 rounded flex items-center justify-center font-bold transition-colors" title="Add Profile">+</button>
        </div>
      </div>

      <div class="flex items-center space-x-4">
        <button class="text-gray-400 hover:text-white transition-colors" title="Project Starter">
          <Play class="w-7 h-7 fill-current" />
        </button>
        <button
          @click="showProjectModal = true"
          class="bg-cm-blue hover:bg-blue-500 text-white font-semibold py-2 px-6 rounded shadow-sm transition-colors"
        >
          Select Project
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <main class="flex-grow flex flex-col relative bg-cm-dark-bg pb-6">

      <!-- Bottom-Left Tools -->
      <div class="absolute bottom-4 left-6 flex flex-col space-y-5">
        <button @click="openSettings('application')" class="text-gray-400 hover:text-white transition-colors" title="Settings">
          <Settings class="w-7 h-7" />
        </button>
      </div>

      <!-- Actions Box Container -->
      <div class="flex-grow flex items-end justify-center pb-8">

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
        <div v-else class="mb-20 text-gray-500 text-[17px]">
          Select a project to get started
        </div>
      </div>

    </main>

    <!-- Status Bar -->
    <footer class="bg-cm-status-bg text-gray-300 px-6 py-2 flex items-center justify-between text-sm font-medium">
      <div class="tracking-wide">{{ statusMessage }}</div>
      <button class="text-gray-400 hover:text-white transition-colors" title="Toggle Info Mode">
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