<script setup>
import { ref, computed } from 'vue'
import { Trash2, Plus, CheckSquare, Square } from 'lucide-vue-next'

const props = defineProps({
  localFiletypes: {
    type: Array,
    required: true
  }
})

const newExt = ref('')
const newDesc = ref('')
const searchQuery = ref('')

const filteredTypes = computed(() => {
  let list = props.localFiletypes
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(ft => ft.ext.toLowerCase().includes(q) || ft.description.toLowerCase().includes(q))
  }
  return [...list].sort((a, b) => a.ext.localeCompare(b.ext))
})

const toggleActive = (ft) => {
  ft.active = !ft.active
}

const deleteFiletype = (ext) => {
  const index = props.localFiletypes.findIndex(ft => ft.ext === ext)
  if (index !== -1) {
    props.localFiletypes.splice(index, 1)
  }
}

const addFiletype = () => {
  let ext = newExt.value.trim().toLowerCase()
  if (!ext) return
  if (!ext.startsWith('.')) ext = `.${ext}`

  if (props.localFiletypes.some(ft => ft.ext === ext)) {
    alert(`The extension '${ext}' already exists.`)
    return
  }

  props.localFiletypes.push({
    ext: ext,
    description: newDesc.value.trim(),
    active: true,
    default: false
  })

  newExt.value = ''
  newDesc.value = ''
}
</script>

<template>
  <div class="space-y-6">
    <p class="text-gray-300 shrink-0">
      Only files matching these extensions are scanned. Click the checkbox to enable or disable them.
    </p>

    <!-- Search / Filter -->
    <div class="flex items-center space-x-3 shrink-0">
      <input
        id="filetypes-search-input"
        v-model="searchQuery"
        type="text"
        class="flex-grow bg-cm-input-bg text-white px-3 py-2 rounded border border-gray-600 focus:border-cm-blue focus:outline-none text-sm"
        placeholder="Search extensions..."
      >
    </div>

    <!-- List -->
    <div id="filetypes-list-container" class="border border-gray-600 rounded bg-cm-input-bg overflow-hidden shrink-0" v-info="'ft_list'">
      <table class="w-full text-sm text-left">
        <thead class="text-gray-400 bg-gray-800">
          <tr>
            <th class="px-4 py-2 font-medium w-16 text-center">Active</th>
            <th class="px-4 py-2 font-medium w-32">Extension</th>
            <th class="px-4 py-2 font-medium">Description</th>
            <th class="px-4 py-2 font-medium w-16 text-center">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-700">
          <tr
            v-for="ft in filteredTypes"
            :key="ft.ext"
            class="hover:bg-gray-700 transition-colors"
            :class="{'opacity-60': !ft.active}"
          >
            <td class="px-4 py-2 text-center cursor-pointer" @click="toggleActive(ft)" v-info="'ft_action'">
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
    <div id="filetypes-add-form" class="bg-gray-800 p-4 rounded border border-gray-700 shrink-0" v-info="'ft_add'">
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
          title="Add new extension to indexed types list"
        >
          <Plus class="w-4 h-4 mr-1" /> Add
        </button>
      </div>
    </div>
  </div>
</template>