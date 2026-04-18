<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { X } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { useEscapeKey } from '../composables/useEscapeKey'

const emit = defineEmits(['close'])
const { activeProject, createProfile, resizeWindow } = useAppState()

const profileName = ref('')
const copyFiles = ref(false)
const copyInstructions = ref(false)
const nameInput = ref(null)

useEscapeKey(() => emit('close'))

onMounted(async () => {
  await resizeWindow(800, 550)

  nextTick(() => {
    nameInput.value?.focus()
  })
})

const handleCreate = async () => {
  const name = profileName.value.trim()
  if (!name) return

  if (activeProject.profiles.some(p => p.toLowerCase() === name.toLowerCase())) {
    alert(`A profile named '${name}' already exists.`)
    return
  }

  const success = await createProfile(name, copyFiles.value, copyInstructions.value)
  if (success) {
    emit('close')
  }
}
</script>

<template>
  <div id="new-profile-modal" class="absolute inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
    <div class="bg-cm-dark-bg w-full max-w-[400px] rounded shadow-2xl border border-gray-600 flex flex-col">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar">
        <h2 class="text-lg font-bold text-white">Create New Profile</h2>
        <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors" title="Close new profile dialog">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 flex flex-col space-y-5">
        <div>
          <label class="block text-gray-200 mb-2">Enter a unique name for the new profile:</label>
          <input
            id="input-profile-name"
            ref="nameInput"
            v-model="profileName"
            v-info="'profile_name'"
            type="text"
            class="w-full bg-cm-input-bg text-white px-3 py-2 rounded border border-gray-600 focus:border-cm-blue focus:outline-none"
            @keyup.enter="handleCreate"
          >
        </div>

        <div class="space-y-3">
          <label class="flex items-center space-x-3 cursor-pointer" v-info="'profile_copy_files'">
            <input type="checkbox" v-model="copyFiles" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
            <span class="text-gray-200">Copy current file selection</span>
          </label>

          <label class="flex items-center space-x-3 cursor-pointer" v-info="'profile_copy_inst'">
            <input type="checkbox" v-model="copyInstructions" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
            <span class="text-gray-200">Copy current instructions</span>
          </label>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end space-x-3">
        <button
          @click="emit('close')"
          v-info="'profile_cancel'"
          class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-6 rounded transition-colors text-sm"
          title="Discard profile details and exit"
        >
          Cancel
        </button>
        <button
          id="btn-profile-create"
          @click="handleCreate"
          :disabled="!profileName.trim()"
          v-info="'profile_create'"
          class="bg-cm-blue hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2 px-6 rounded shadow-md transition-all text-sm"
          title="Create the new project configuration profile"
        >
          Create
        </button>
      </div>

    </div>
  </div>
</template>