<script setup>
import { ref, onMounted, computed } from 'vue'
import { X, Trash2, Plus, CheckSquare, Square } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'

const emit = defineEmits(['close'])
const { getFiletypes, saveFiletypes } = useAppState()

const filetypes = ref([])
const newExt = ref('')
const newDesc = ref('')
const searchQuery = ref('')

onMounted(async () => {
  filetypes.value = await getFiletypes()
})

const filteredTypes = computed(() => {
  let list = filetypes.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(ft => ft.ext.toLowerCase().includes(q) || ft.description.toLowerCase().includes(q))
  }
  // Sort alphabetically
  return list.sort((a, b) => a.ext.localeCompare(b.ext))
})

const toggleActive = (ft) => {
  ft.active = !ft.active
}

const deleteFiletype = (ext) => {
  filetypes.value = filetypes.value.filter(ft => ft.ext !== ext)
}

const addFiletype = () => {
  let ext = newExt.value.trim().toLowerCase()
  if (!ext) return
  if (!ext.startsWith('.')) ext = `.${ext}` // Auto-prepend dot if missing for common extensions

  // Check duplicate
  if (filetypes.value.some(ft => ft.ext === ext)) {
    alert(`The extension '${ext}' already exists.`)
    return
  }

  filetypes.value.push({
    ext: ext,
    description: newDesc.value.trim(),
    active: true,
    default: false
  })

  newExt.value = ''
  newDesc.value = ''
}

const handleSave = async () => {
  await saveFiletypes(filetypes.value)
  emit('close')
}
</script>

<template>
  <div class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
    <div class="bg-cm-dark-bg w-full max-w-2xl h-[700px] rounded shadow-2xl border border-gray-600 flex flex-col">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar shrink-0">
        <h2 class="text-xl font-bold text-white">Manage Filetypes</h2>
        <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Main Content -->
      <div class="flex-grow flex flex-col p-6 min-h-0">
        <p class="text-gray-300 mb-4 shrink-0">
          Only files matching these extensions are scanned. Click the checkbox to enable or disable them.
        </p>

        <!-- Search / Filter -->
        <div class="flex items-center space-x-3 mb-4 shrink-0">
          <input
            v-model="searchQuery"
            type="text"
            class="flex-grow bg-cm-input-bg text-white px-3 py-2 rounded border border-gray-600 focus:border-cm-blue focus:outline-none text-sm"
            placeholder="Search extensions..."
          >
        </div>

        <!-- Scrollable List -->
        <div class="flex-grow overflow-y-auto border border-gray-600 rounded bg-cm-input-bg custom-scrollbar relative">
          <table class="w-full text-sm text-left">
            <thead class="text-gray-400 bg-gray-800 sticky top-0 z-10">
              <tr>
                <th class="px-4 py-2 font-medium w-16 text-center">Active</th>
                <th class="px-4 py-2 font-medium w-32">Extension</th>
                <th class="px-4 py-2 font-medium">Description</th>
                <th class="px-4 py-2 font-medium w-16 text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="ft in filteredTypes"
                :key="ft.ext"
                class="border-b border-gray-700 hover:bg-gray-700 transition-colors"
                :class="{'opacity-60': !ft.active}"
              >
                <td class="px-4 py-2 text-center cursor-pointer" @click="toggleActive(ft)">
                  <CheckSquare v-if="ft.active" class="w-5 h-5 inline-block text-cm-blue" />
                  <Square v-else class="w-5 h-5 inline-block text-gray-500" />
                </td>
                <td class="px-4 py-2 font-mono text-gray-200">{{ ft.ext }}</td>
                <td class="px-4 py-2 text-gray-400 truncate max-w-xs" :title="ft.description">{{ ft.description }}</td>
                <td class="px-4 py-2 text-center">
                  <button
                    v-if="!ft.default"
                    @click="deleteFiletype(ft.ext)"
                    class="text-gray-500 hover:text-red-400 transition-colors"
                    title="Delete custom filetype"
                  >
                    <Trash2 class="w-4 h-4 inline-block" />
                  </button>
                </td>
              </tr>
              <tr v-if="filteredTypes.length === 0">
                <td colspan="4" class="px-4 py-8 text-center text-gray-500">No filetypes found.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Add New Section -->
        <div class="mt-6 shrink-0 bg-gray-800 p-4 rounded border border-gray-700">
          <h3 class="text-sm font-bold text-gray-300 mb-3 uppercase tracking-wider">Add New Filetype</h3>
          <div class="flex space-x-3">
            <input
              v-model="newExt"
              type="text"
              placeholder=".ext"
              class="w-24 bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-2 outline-none focus:border-cm-blue text-sm font-mono"
            >
            <input
              v-model="newDesc"
              type="text"
              placeholder="Description..."
              class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-2 outline-none focus:border-cm-blue text-sm"
              @keyup.enter="addFiletype"
            >
            <button
              @click="addFiletype"
              :disabled="!newExt.trim()"
              class="bg-gray-600 hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded transition-colors flex items-center"
            >
              <Plus class="w-4 h-4 mr-1" /> Add
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end shrink-0 rounded-b">
        <button
          @click="emit('close')"
          class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-5 rounded mr-3 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="handleSave"
          class="bg-cm-blue hover:bg-blue-500 text-white font-medium py-2 px-5 rounded shadow-sm transition-colors"
        >
          Save Changes
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #777;
}
</style>