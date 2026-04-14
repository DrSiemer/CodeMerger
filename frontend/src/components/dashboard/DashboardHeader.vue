<script setup>
import { ref, computed, nextTick } from 'vue'
import { PenLine, AlertTriangle, Minimize2, FolderOpen } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  isFileManagerOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['open-project-modal', 'open-file-manager'])

const {
  activeProject,
  isProjectLoading,
  logoMask,
  renameProject,
  openProjectFolder,
  addAllNewFiles,
  selectColor,
  minimizeWindow,
  config
} = useAppState()

// Interaction state to distinguish between single and double clicks on the project title
let clickTimer = null

const handleTitleInteraction = () => {
  if (isProjectLoading.value) return

  if (!activeProject.path) {
    emit('open-project-modal')
    return
  }

  if (clickTimer) {
    clearTimeout(clickTimer)
    clickTimer = null
    startEditing()
  } else {
    clickTimer = setTimeout(() => {
      clickTimer = null
      emit('open-project-modal')
    }, 250)
  }
}

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

const handleNewFilesClick = async (event) => {
  if (event.ctrlKey) {
    await addAllNewFiles()
  } else {
    emit('open-file-manager')
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

const minimizeInfoKey = computed(() => {
  return config.value.enable_compact_mode_on_minimize ? 'minimize_to_taskbar' : 'minimize_to_compact'
})

const minimizeTitle = computed(() => {
  return config.value.enable_compact_mode_on_minimize ? 'Minimize without showing Compact Mode' : 'Minimize to Compact Mode'
})
</script>

<template>
  <header id="dashboard-header" class="bg-cm-top-bar px-6 py-0 flex items-center justify-between border-b border-gray-700 h-[76px] shrink-0">
    <div class="flex items-center space-x-4 min-w-0 flex-grow h-full">
      <!-- Masked Logo Swatch -->
      <div
        v-if="activeProject.path && logoMask"
        id="project-logo"
        class="w-12 h-12 cursor-pointer shrink-0"
        :style="swatchStyle"
        @click="selectColor"
        v-info="'color_swatch'"
        title="Change project color"
      ></div>

      <!-- Fallback if mask not loaded -->
      <div
        v-else-if="activeProject.path"
        id="project-logo"
        class="w-10 h-10 rounded cursor-pointer border border-gray-600 shadow-sm shrink-0"
        :style="{ backgroundColor: activeProject.color }"
        @click="selectColor"
        v-info="'color_swatch'"
        title="Change project color"
      ></div>

      <div id="project-name-container" class="flex items-center min-w-0 flex-grow text-white h-full">
        <div v-if="isEditingName" class="flex items-center space-x-2 w-full max-w-md h-full">
          <input
            ref="nameInput"
            v-model="tempName"
            @keyup.enter="saveName"
            @keyup.esc="cancelEditing"
            @blur="saveName"
            class="bg-cm-input-bg text-white border border-cm-blue rounded px-2 py-0 text-4xl font-extralight tracking-[0.01em] leading-none h-[60px] w-full focus:outline-none"
          >
        </div>
        <div
          v-else
          class="flex items-center group cursor-pointer min-w-0 h-full"
          title="Click to select project, double-click to edit title"
          @click="handleTitleInteraction"
          v-info="'project_name'"
        >
          <h1 v-if="isProjectLoading" class="text-4xl font-extralight tracking-[0.01em] leading-none whitespace-nowrap text-gray-500 loading-dots">
            Loading
          </h1>
          <h1 v-else class="text-4xl font-extralight tracking-[0.01em] leading-none whitespace-nowrap" :class="{'text-gray-500': !activeProject.path}">
            {{ activeProject.name || '(no active project)' }}
          </h1>
          <button
            v-if="activeProject.path && !isProjectLoading"
            @click.stop="startEditing"
            class="shrink-0 p-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-white"
            title="Edit project title"
          >
            <PenLine class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <div class="flex items-center space-x-5 shrink-0 ml-4 h-full">
      <!-- New Files Alert (Syncs with background monitor thread) -->
      <div
        v-if="activeProject.newFileCount > 0 && !isFileManagerOpen"
        class="flex items-center text-cm-green cursor-pointer hover:brightness-125 transition-all"
        title="New files found. Click: Open manager, Ctrl-Click: Add all to merge list"
        @click="handleNewFilesClick($event)"
      >
        <AlertTriangle class="w-6 h-6" />
      </div>

      <!-- Inverse Minimize Toggle -->
      <button
        v-if="activeProject.path"
        @click="minimizeWindow(true)"
        class="text-gray-400 hover:text-white transition-colors p-1"
        :title="minimizeTitle"
        v-info="minimizeInfoKey"
      >
        <Minimize2 class="w-5 h-5" />
      </button>

      <!-- Folder Icon (Lucide SVG replacement) -->
      <button
        v-if="activeProject.path"
        @click="openProjectFolder($event)"
        class="text-gray-400 hover:text-white transition-colors p-1"
        title="Open project folder (Ctrl-Click: Copy Path, Alt-Click: Open Command Prompt)"
        v-info="'folder_icon'"
      >
        <FolderOpen class="w-6 h-6" />
      </button>
    </div>
  </header>
</template>