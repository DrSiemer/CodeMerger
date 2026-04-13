<script setup>
import { ref } from 'vue'
import { useAppState } from '../../composables/useAppState'

const emit = defineEmits(['open-file-manager', 'open-new-profile-modal', 'open-starter-modal', 'open-project-modal'])

const {
  activeProject,
  isProjectLoading,
  starterIcon,
  starterActiveIcon,
  switchProfile,
  deleteProfile
} = useAppState()

const isStarterHovered = ref(false)

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
</script>

<template>
  <div id="dashboard-nav-actions" class="px-6 py-5 flex items-center justify-between bg-cm-dark-bg shrink-0">
    <div class="flex items-center space-x-4">
      <button
        id="btn-edit-merge-list"
        class="bg-gray-300 hover:bg-gray-200 text-gray-900 font-semibold py-2 px-6 rounded shadow-sm disabled:opacity-50 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors h-[38px]"
        :disabled="!activeProject.path || isProjectLoading"
        @click="emit('open-file-manager')"
        title="Manage selected files and their order"
        v-info="'manage_files'"
      >
        Edit Merge List
      </button>

      <div id="profile-navigator" class="flex items-center space-x-2" v-if="activeProject.path">
        <!-- Multi-profile navigator -->
        <div v-if="activeProject.profiles.length > 1" class="flex items-center" v-info="'profile_nav'">
          <button @click="prevProfile" class="w-7 h-[38px] bg-cm-input-bg text-gray-400 hover:text-white rounded-l border border-gray-600 border-r-0 flex items-center justify-center transition-colors" title="Previous Profile" :disabled="isProjectLoading">&lt;</button>
          <span class="text-white bg-cm-input-bg px-4 py-2 text-sm font-medium border-y border-gray-600 h-[38px] flex items-center min-w-[80px] justify-center truncate">{{ activeProject.activeProfile }}</span>
          <button @click="nextProfile" class="w-7 h-[38px] bg-cm-input-bg text-gray-400 hover:text-white rounded-r border border-gray-600 border-l-0 flex items-center justify-center transition-colors" title="Next Profile" :disabled="isProjectLoading">&gt;</button>
        </div>

        <!-- Single profile view -->
        <span v-else class="text-white bg-cm-input-bg px-4 py-2 rounded text-sm font-medium border border-gray-600 h-[38px] flex items-center truncate max-w-[120px]">{{ activeProject.activeProfile }}</span>

        <button @click="emit('open-new-profile-modal')" class="border border-gray-500 hover:bg-gray-700 text-white w-9 h-[38px] rounded flex items-center justify-center font-bold transition-colors" title="Add Profile" v-info="'profile_add'" :disabled="isProjectLoading">+</button>

        <button v-if="activeProject.profiles.length > 1 && activeProject.activeProfile !== 'Default'" @click="deleteProfileHandler" class="border border-gray-500 hover:bg-red-900/50 hover:text-red-400 hover:border-red-400 text-gray-300 w-9 h-[38px] rounded flex items-center justify-center font-bold transition-colors" title="Delete Profile" v-info="'profile_delete'" :disabled="isProjectLoading">-</button>
      </div>
    </div>

    <div class="flex items-center space-x-3">
      <!-- Project Starter Icon Button -->
      <button
        id="btn-starter"
        class="hover:brightness-110 transition-all p-1 flex items-center justify-center"
        title="Open Project Starter wizard"
        @mouseenter="isStarterHovered = true"
        @mouseleave="isStarterHovered = false"
        @click="emit('open-starter-modal')"
        v-info="'starter'"
        :disabled="isProjectLoading"
      >
        <img
          v-if="starterIcon"
          :src="isStarterHovered ? (starterActiveIcon || starterIcon) : starterIcon"
          class="w-7 h-7"
          alt="Project Starter"
        />
      </button>

      <button
        id="btn-select-project"
        @click="emit('open-project-modal')"
        :disabled="isProjectLoading"
        class="bg-cm-blue hover:bg-blue-500 text-white font-semibold py-2 px-6 rounded shadow-sm transition-colors h-[38px]"
        title="Open project selector"
        v-info="'select_project'"
      >
        Select Project
      </button>
    </div>
  </div>
</template>