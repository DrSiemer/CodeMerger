<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { X, Search, FolderPlus, Trash2 } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'

const emit = defineEmits(['close'])
const { getRecentProjects, removeRecentProject, loadProject, selectProject, getImage, resizeWindow, infoModeActive, openProjectFolder } = useAppState()

const recents = ref([])
const searchQuery = ref('')
const isLoaded = ref(false)
const logoMaskSmall = ref('')

const handleEscape = (e) => {
  if (e.key === 'Escape') emit('close')
}

onMounted(async () => {
  const footerHeight = infoModeActive.value ? 116 : 36
  await resizeWindow(800, 500 + footerHeight)

  document.addEventListener('keydown', handleEscape)
  const initialRecents = await getRecentProjects()
  recents.value = Array.isArray(initialRecents) ? initialRecents : []
  logoMaskSmall.value = await getImage('logo_mask_small.png')
  isLoaded.value = true
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})

const filteredRecents = computed(() => {
  if (!recents.value || !searchQuery.value) return recents.value || []
  const q = searchQuery.value.toLowerCase()
  return recents.value.filter(p =>
    p.name.toLowerCase().includes(q) ||
    p.path.toLowerCase().includes(q)
  )
})

const handleSelect = async (path, event) => {
  if (event.ctrlKey) {
    if (window.pywebview) {
      await window.pywebview.api.open_path(path)
    }
    return
  }
  emit('close')
  await loadProject(path)
}

const handleRemove = async (proj) => {
  const msg = `Are you sure you want to remove "${proj.name}" from your recent projects?\n\nThis will not delete the files on your disk, but CodeMerger will no longer track its selection settings for this folder.`

  if (confirm(msg)) {
    const result = await removeRecentProject(proj.path)
    recents.value = Array.isArray(result) ? result : []
  }
}

const handleBrowse = async () => {
  const path = await selectProject()
  if (path) {
    emit('close')
    // Trigger loadProject ONLY after we have a valid path string from the OS picker
    // This ensures the overlay appears exactly when the scan starts
    await loadProject(path)
  }
}
</script>

<template>
  <div id="project-selector-modal" class="absolute inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
    <!-- max-h-[90%] ensures the modal height adjusts to the parent Content Area (which shrinks when Info Mode is ON) -->
    <div id="project-selector-window" class="bg-cm-dark-bg w-full max-w-[450px] rounded shadow-2xl border border-gray-600 flex flex-col max-h-[90%]">

      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700">
        <h2 class="text-xl font-bold text-white">Select Project</h2>
        <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors" title="Close project selector">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="px-5 py-4 flex-grow flex flex-col min-h-0">
        <p class="text-gray-300 mb-4">
          {{ recents.length > 0 ? 'Select a recent project or browse for a new one' : 'Browse for a project folder to get started' }}
        </p>

        <!-- Filter Bar -->
        <div v-if="recents.length >= 5 || searchQuery" class="flex items-center space-x-3 mb-4">
          <span class="text-gray-400 text-sm">Filter:</span>
          <div class="relative flex-grow">
            <input
              id="project-search-input"
              v-model="searchQuery"
              v-info="'sel_filter'"
              type="text"
              class="w-full bg-cm-input-bg text-white px-3 py-1.5 rounded border border-transparent focus:border-cm-blue focus:outline-none text-sm"
              placeholder="Search name or path..."
              autofocus
            >
            <button
              v-if="searchQuery"
              @click="searchQuery = ''"
              class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
              title="Clear search"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Scrollable List -->
        <div id="recent-projects-list" class="flex-grow overflow-y-auto pr-1 min-h-[100px] custom-scrollbar" v-info="'sel_list'">
          <div v-if="isLoaded && filteredRecents.length === 0 && recents.length > 0" class="text-gray-500 py-6 text-center">
            No projects match your filter.
          </div>

          <div class="space-y-1.5">
            <div
              v-for="proj in filteredRecents"
              :key="proj.path"
              class="group flex items-center justify-between bg-cm-input-bg hover:bg-gray-600 border border-transparent hover:border-gray-500 rounded p-2 cursor-pointer transition-colors"
              @click="handleSelect(proj.path, $event)"
              :title="`${proj.path}\n(Click to load, Ctrl-Click to open folder in explorer)`"
            >
              <div class="flex items-center min-w-0 flex-grow">
                <!-- Masked Logo Swatch -->
                <div
                  v-if="logoMaskSmall"
                  class="w-7 h-7 flex-shrink-0 mr-3"
                  :style="{
                    backgroundColor: proj.color,
                    maskImage: `url(${logoMaskSmall})`,
                    webkitMaskImage: `url(${logoMaskSmall})`,
                    maskSize: 'contain',
                    webkitMaskSize: 'contain',
                    maskRepeat: 'no-repeat',
                    webkitMaskRepeat: 'no-repeat'
                  }"
                ></div>
                <!-- Fallback if mask not loaded -->
                <div
                  v-else
                  class="w-4 h-4 rounded-sm flex-shrink-0 mr-3 border border-gray-600"
                  :style="{ backgroundColor: proj.color }"
                ></div>
                <span class="text-white font-medium truncate">{{ proj.name }}</span>
              </div>

              <button
                @click.stop="handleRemove(proj)"
                v-info="'sel_remove'"
                class="text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity ml-2 focus:opacity-100 p-1"
                title="Remove from recent list"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-5 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end rounded-b">
        <button
          id="btn-browse-new-project"
          @click="handleBrowse"
          v-info="'sel_browse'"
          class="bg-cm-blue hover:bg-blue-500 text-white font-semibold py-2 px-6 rounded shadow-sm transition-colors flex items-center"
          title="Browse your computer for a project folder"
        >
          <FolderPlus class="w-4 h-4 mr-2" />
          Add project
        </button>
      </div>

    </div>
  </div>
</template>