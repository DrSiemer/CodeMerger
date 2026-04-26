<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Sprout, Network, ChevronDown, Trash2, Plus } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const emit = defineEmits(['open-file-manager', 'open-new-profile-modal', 'open-starter-modal', 'open-project-modal', 'open-visualizer'])

const {
  activeProject,
  isProjectLoading,
  switchProfile,
  deleteProfile
} = useAppState()

// --- Profile Management ---
const showProfileDropdown = ref(false)

const currentProfileDisplay = computed(() => {
  const p = activeProject.profiles.find(p => p.id === activeProject.activeProfile)
  return p ? p.name : activeProject.activeProfile
})

const handleSwitch = async (id) => {
  showProfileDropdown.value = false
  if (id !== activeProject.activeProfile) {
    await switchProfile(id)
  }
}

const handleOpenNewProfile = () => {
  showProfileDropdown.value = false
  emit('open-new-profile-modal')
}

const deleteProfileHandler = async (id, name) => {
  if (confirm(`Are you sure you want to delete the profile '${name}'?\nThis cannot be undone.`)) {
    await deleteProfile(id)
  }
}

const toggleDropdown = () => {
  if (isProjectLoading.value) return
  showProfileDropdown.value = !showProfileDropdown.value
}

const closeDropdown = (e) => {
  if (showProfileDropdown.value && !e.target.closest('#profile-selector-container')) {
    showProfileDropdown.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  window.removeEventListener('click', closeDropdown)
})
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

      <div id="profile-selector-container" class="relative" v-if="activeProject.path">
        <div class="flex items-center space-x-2">
          <!-- Profile Selection Dropdown Trigger -->
          <button
            @click="toggleDropdown"
            v-info="'profile_nav'"
            class="flex items-center justify-between bg-cm-input-bg hover:bg-gray-700 text-white px-4 py-2 rounded text-sm font-medium border border-gray-600 h-[38px] transition-colors min-w-[120px] max-w-[200px]"
            :disabled="isProjectLoading"
            title="Switch project profile"
          >
            <span class="truncate pr-2">{{ currentProfileDisplay }}</span>
            <ChevronDown class="w-4 h-4 text-gray-500 shrink-0 transition-transform duration-200" :class="{'rotate-180': showProfileDropdown}" />
          </button>

          <!-- Quick Add Profile -->
          <button
            @click="handleOpenNewProfile"
            v-info="'profile_add'"
            class="border border-gray-500 hover:bg-gray-700 text-white w-9 h-[38px] rounded flex items-center justify-center transition-colors shadow-sm"
            title="Create new profile"
            :disabled="isProjectLoading"
          >
            <Plus class="w-5 h-5" />
          </button>
        </div>

        <!-- Dropdown Menu -->
        <transition name="dropdown">
          <div
            v-if="showProfileDropdown"
            class="absolute top-full left-0 mt-1 w-64 bg-cm-status-bg border border-gray-700 rounded-lg shadow-2xl z-[100] py-2 overflow-hidden"
          >
            <div class="px-3 py-1.5 mb-1">
               <span class="text-[10px] font-black text-gray-500 uppercase tracking-widest">Switch Profile</span>
            </div>

            <div class="max-h-60 overflow-y-auto custom-scrollbar">
              <div
                v-for="p in activeProject.profiles"
                :key="p.id"
                class="group flex items-center justify-between px-3 py-2 hover:bg-cm-blue/20 cursor-pointer transition-colors"
                @click="handleSwitch(p.id)"
              >
                <div class="flex items-center min-w-0 flex-grow">
                  <div class="w-1.5 h-1.5 rounded-full mr-3 shrink-0" :class="p.id === activeProject.activeProfile ? 'bg-cm-blue' : 'bg-transparent'"></div>
                  <span class="text-sm truncate" :class="p.id === activeProject.activeProfile ? 'text-white font-bold' : 'text-gray-300'">{{ p.name }}</span>
                </div>

                <!-- Delete Icon per Profile in Dropdown -->
                <button
                  v-if="p.id !== 'default'"
                  @click.stop="deleteProfileHandler(p.id, p.name)"
                  v-info="'profile_delete'"
                  class="p-1 text-gray-500 hover:text-red-400 opacity-40 hover:opacity-100 transition-opacity ml-2"
                  title="Delete this profile"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <div class="flex items-center space-x-3">
      <!-- Visualizer Icon Button -->
      <button
        id="btn-visualizer"
        class="transition-all p-1 flex items-center justify-center group"
        title="Open Architecture Explorer"
        @click="emit('open-visualizer')"
        v-info="'visualizer'"
        :disabled="!activeProject.path || isProjectLoading"
      >
        <Network
          class="w-6 h-6 text-gray-400 group-hover:text-cm-blue transition-colors"
          :stroke-width="1.5"
        />
      </button>

      <!-- Project Starter Icon Button -->
      <button
        id="btn-starter"
        class="transition-all p-1 flex items-center justify-center group"
        title="Open Project Starter wizard"
        @click="emit('open-starter-modal')"
        v-info="'starter'"
        :disabled="isProjectLoading"
      >
        <Sprout
          class="w-7 h-7 text-gray-400 group-hover:text-cm-green transition-colors"
          :stroke-width="1.5"
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

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease-out;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>