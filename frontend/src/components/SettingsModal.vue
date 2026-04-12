<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  X, Settings, FolderClosed, Bot, Play,
  Terminal, FileCode2, Trash2, Plus, CheckSquare, Square
} from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'

const props = defineProps({
  initialTab: {
    type: String,
    default: 'application'
  }
})

const emit = defineEmits(['close'])
const { config, saveConfig, getFiletypes, saveFiletypes, resizeWindow } = useAppState()

const localConfig = ref({})
const activeTab = ref(props.initialTab)

// Filetypes State
const localFiletypes = ref([])
const newExt = ref('')
const newDesc = ref('')
const searchQuery = ref('')

onMounted(async () => {
  // Smart Growth: Ensure the main window is large enough for the settings layout
  // 1000x700 is the recommended comfortable footprint for settings.
  await resizeWindow(1000, 700)

  // Deep clone to prevent mutating global state before saving
  localConfig.value = JSON.parse(JSON.stringify(config.value))
  localFiletypes.value = await getFiletypes()
})

const handleSave = async () => {
  // Sanitize numerical inputs
  localConfig.value.new_file_check_interval = parseInt(localConfig.value.new_file_check_interval) || 5
  localConfig.value.token_limit = parseInt(localConfig.value.token_limit) || 0
  localConfig.value.add_all_warning_threshold = parseInt(localConfig.value.add_all_warning_threshold) || 100
  localConfig.value.new_file_alert_threshold = parseInt(localConfig.value.new_file_alert_threshold) || 5

  // Save settings and filetypes sequentially
  await saveConfig(localConfig.value)
  await saveFiletypes(localFiletypes.value)
  emit('close')
}

const tabs = [
  { id: 'application', name: 'Application', icon: Settings, info: 'set_app' },
  { id: 'filemanager', name: 'File Manager', icon: FolderClosed, info: 'set_fm' },
  { id: 'filetypes', name: 'Filetypes', icon: FileCode2, info: 'filetypes' },
  { id: 'prompts', name: 'Prompts', icon: Bot, info: 'set_prompts' },
  { id: 'starter', name: 'Starter', icon: Play, info: 'set_starter' },
  { id: 'editor', name: 'Editor', icon: Terminal, info: 'set_editor' }
]

const activeTabInfoKey = computed(() => {
  return tabs.find(t => t.id === activeTab.value)?.info || ''
})

// --- Filetypes Logic ---
const filteredTypes = computed(() => {
  let list = localFiletypes.value
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
  localFiletypes.value = localFiletypes.value.filter(ft => ft.ext !== ext)
}

const addFiletype = () => {
  let ext = newExt.value.trim().toLowerCase()
  if (!ext) return
  if (!ext.startsWith('.')) ext = `.${ext}` // Auto-prepend dot if missing for common extensions

  // Check duplicate
  if (localFiletypes.value.some(ft => ft.ext === ext)) {
    alert(`The extension '${ext}' already exists.`)
    return
  }

  localFiletypes.value.push({
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
  <div id="settings-modal" class="absolute inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
    <div class="bg-cm-dark-bg w-full max-w-4xl h-[650px] rounded shadow-2xl border border-gray-600 flex overflow-hidden">

      <!-- Sidebar Navigation -->
      <div id="settings-sidebar" class="w-48 bg-cm-top-bar border-r border-gray-700 flex flex-col shrink-0">
        <div class="p-4 text-lg font-bold text-white mb-2">Settings</div>

        <div class="flex-grow flex flex-col px-2 space-y-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            v-info="tab.info"
            class="flex items-center px-3 py-2 rounded text-sm transition-colors text-left"
            :class="activeTab === tab.id ? 'bg-cm-blue text-white font-medium' : 'text-gray-300 hover:bg-gray-700 hover:text-white'"
          >
            <component :is="tab.icon" class="w-4 h-4 mr-3" />
            {{ tab.name }}
          </button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div id="settings-viewport" class="flex-grow flex flex-col h-full bg-cm-dark-bg min-w-0">
        <!-- Header -->
        <div class="flex justify-between items-center p-4 border-b border-gray-700 shrink-0">
          <h2 class="text-xl font-semibold text-white" v-info="activeTabInfoKey">
            {{ tabs.find(t => t.id === activeTab)?.name }}
          </h2>
          <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors">
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Scrollable Settings Body -->
        <div class="flex-grow overflow-y-auto p-6 custom-scrollbar flex flex-col">

          <!-- APPLICATION -->
          <template v-if="activeTab === 'application'">
            <div class="space-y-4">
              <div v-info="'set_app_new_file'" class="flex flex-col space-y-4">
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" v-model="localConfig.enable_new_file_check" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                  <span class="text-gray-200">Periodically check for new project files</span>
                </label>

                <div class="pl-7 flex items-center space-x-3" :class="{'opacity-50 pointer-events-none': !localConfig.enable_new_file_check}">
                  <span class="text-gray-300 text-sm" v-info="'set_app_interval'">Check every:</span>
                  <select v-model="localConfig.new_file_check_interval" v-info="'set_app_interval'" class="bg-cm-input-bg border border-gray-600 text-white rounded px-2 py-1 text-sm outline-none focus:border-cm-blue">
                    <option value="2">2</option>
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="30">30</option>
                    <option value="60">60</option>
                  </select>
                  <span class="text-gray-300 text-sm" v-info="'set_app_interval'">seconds</span>
                </div>
              </div>

              <div v-info="'set_app_secrets'" class="pt-2">
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" v-model="localConfig.scan_for_secrets" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                  <span class="text-gray-200">Scan for secrets (on each copy)</span>
                </label>
              </div>

              <div v-info="'set_app_feedback'" class="pt-2">
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" v-model="localConfig.show_feedback_on_paste" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                  <span class="text-gray-200">Show LLM feedback window automatically on paste</span>
                </label>
              </div>

              <div v-info="'set_app_compact'" class="pt-2">
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" v-model="localConfig.enable_compact_mode_on_minimize" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                  <span class="text-gray-200">Activate compact mode when main window is minimized</span>
                </label>
              </div>

              <div v-info="'set_app_updates'" class="pt-2">
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" v-model="localConfig.check_for_updates" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                  <span class="text-gray-200">Automatically check for updates daily</span>
                </label>
                <!-- Manual Check Button inside the updates documentation scope -->
                <div class="pl-7 pt-2">
                   <button
                    id="btn-check-updates-now"
                    @click="window.pywebview.api.check_for_updates_manual()"
                    v-info="'set_app_check_now'"
                    class="bg-gray-700 hover:bg-gray-600 text-white text-xs font-bold py-1.5 px-4 rounded transition-colors"
                  >
                    Check for Updates Now
                  </button>
                </div>
              </div>
            </div>
          </template>

          <!-- FILE MANAGER -->
          <template v-if="activeTab === 'filemanager'">
            <div class="space-y-6">
              <div v-info="'set_fm_tokens'">
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" v-model="localConfig.token_count_enabled" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                  <span class="text-gray-200">Enable token counting</span>
                </label>
              </div>

              <div class="flex items-center space-x-3" v-info="'set_fm_limit'">
                <span class="text-gray-200 w-64">Max token limit (empty for none):</span>
                <input type="number" v-model="localConfig.token_limit" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
              </div>

              <div class="flex items-center space-x-3" v-info="'set_fm_threshold'">
                <span class="text-gray-200 w-64">Warn when 'Add all' exceeds:</span>
                <input type="number" v-model="localConfig.add_all_warning_threshold" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
                <span class="text-gray-400 text-sm">files</span>
              </div>

              <div class="flex items-center space-x-3" v-info="'set_fm_alert_threshold'">
                <span class="text-gray-200 w-64">New file alert threshold:</span>
                <input type="number" v-model="localConfig.new_file_alert_threshold" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
                <span class="text-gray-400 text-sm">files</span>
              </div>
            </div>
          </template>

          <!-- FILETYPES -->
          <template v-if="activeTab === 'filetypes'">
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
                  >
                    <Plus class="w-4 h-4 mr-1" /> Add
                  </button>
                </div>
              </div>
            </div>
          </template>

          <!-- PROMPTS -->
          <template v-if="activeTab === 'prompts'">
            <div class="space-y-6">
              <div class="space-y-2" v-info="'set_prompt_merged'">
                <label class="text-gray-200 font-medium">"Copy Code Only" Prompt</label>
                <textarea
                  v-model="localConfig.copy_merged_prompt"
                  rows="3"
                  class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 text-sm outline-none focus:border-cm-blue custom-scrollbar"
                ></textarea>
              </div>

              <div class="space-y-2" v-info="'set_prompt_intro'">
                <label class="text-gray-200 font-medium">Default Intro Instructions</label>
                <textarea
                  v-model="localConfig.default_intro_prompt"
                  rows="4"
                  class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 text-sm outline-none focus:border-cm-blue custom-scrollbar"
                ></textarea>
              </div>

              <div class="space-y-2" v-info="'set_prompt_outro'">
                <label class="text-gray-200 font-medium">Default Outro Instructions</label>
                <textarea
                  v-model="localConfig.default_outro_prompt"
                  rows="4"
                  class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 text-sm outline-none focus:border-cm-blue custom-scrollbar"
                ></textarea>
              </div>
            </div>
          </template>

          <!-- STARTER -->
          <template v-if="activeTab === 'starter'">
            <div class="space-y-2" v-info="'set_starter_folder'">
              <label class="text-gray-200 font-medium">Default parent folder for new projects</label>
              <input
                type="text"
                v-model="localConfig.default_parent_folder"
                placeholder="C:\Projects"
                class="w-full bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-2 outline-none focus:border-cm-blue"
              >
            </div>
          </template>

          <!-- EDITOR -->
          <template v-if="activeTab === 'editor'">
            <div class="space-y-2" v-info="'set_editor_path'">
              <label class="text-gray-200 font-medium">Default Editor Executable</label>
              <input
                type="text"
                v-model="localConfig.default_editor"
                placeholder="Leave blank to use OS default"
                class="w-full bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-2 outline-none focus:border-cm-blue"
              >
              <p class="text-sm text-gray-500 mt-1">Provide the full path to your code editor (e.g., sublime_text.exe).</p>
            </div>
          </template>

        </div>

        <!-- Footer -->
        <div class="p-4 border-t border-gray-700 shrink-0 bg-cm-top-bar flex justify-end">
          <button
            @click="emit('close')"
            v-info="'settings_cancel'"
            class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-5 rounded mr-3 transition-colors"
          >
            Cancel
          </button>
          <button
            id="btn-settings-save"
            @click="handleSave"
            v-info="'settings_save'"
            class="bg-cm-blue hover:bg-blue-500 text-white font-medium py-2 px-5 rounded shadow-sm transition-colors"
          >
            Save Changes
          </button>
        </div>
      </div>

    </div>
  </div>
</template>