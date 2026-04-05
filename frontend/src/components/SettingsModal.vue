<script setup>
import { ref, onMounted } from 'vue'
import { X, Settings, FolderClosed, Bot, Play, FileCode2 } from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'

const emit = defineEmits(['close'])
const { config, saveConfig } = useAppState()

const localConfig = ref({})
const activeTab = ref('application')

onMounted(() => {
  // Deep clone to prevent mutating global state before saving
  localConfig.value = JSON.parse(JSON.stringify(config.value))
})

const handleSave = async () => {
  // Sanitize numerical inputs
  localConfig.value.new_file_check_interval = parseInt(localConfig.value.new_file_check_interval) || 5
  localConfig.value.token_limit = parseInt(localConfig.value.token_limit) || 0
  localConfig.value.add_all_warning_threshold = parseInt(localConfig.value.add_all_warning_threshold) || 100
  localConfig.value.new_file_alert_threshold = parseInt(localConfig.value.new_file_alert_threshold) || 5

  await saveConfig(localConfig.value)
  emit('close')
}

const tabs = [
  { id: 'application', name: 'Application', icon: Settings },
  { id: 'filemanager', name: 'File Manager', icon: FolderClosed },
  { id: 'prompts', name: 'Prompts', icon: Bot },
  { id: 'starter', name: 'Starter', icon: Play },
  { id: 'editor', name: 'Editor', icon: FileCode2 }
]
</script>

<template>
  <div class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
    <div class="bg-cm-dark-bg w-full max-w-4xl h-[650px] rounded shadow-2xl border border-gray-600 flex overflow-hidden">

      <!-- Sidebar Navigation -->
      <div class="w-48 bg-cm-top-bar border-r border-gray-700 flex flex-col">
        <div class="p-4 text-lg font-bold text-white mb-2">Settings</div>

        <div class="flex-grow flex flex-col px-2 space-y-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            class="flex items-center px-3 py-2 rounded text-sm transition-colors text-left"
            :class="activeTab === tab.id ? 'bg-cm-blue text-white font-medium' : 'text-gray-300 hover:bg-gray-700 hover:text-white'"
          >
            <component :is="tab.icon" class="w-4 h-4 mr-3" />
            {{ tab.name }}
          </button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-grow flex flex-col h-full bg-cm-dark-bg min-w-0">
        <!-- Header -->
        <div class="flex justify-between items-center p-4 border-b border-gray-700 shrink-0">
          <h2 class="text-xl font-semibold text-white">
            {{ tabs.find(t => t.id === activeTab)?.name }}
          </h2>
          <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors">
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Scrollable Settings -->
        <div class="flex-grow overflow-y-auto p-6 space-y-6 custom-scrollbar">

          <!-- APPLICATION -->
          <template v-if="activeTab === 'application'">
            <div class="space-y-4">
              <label class="flex items-center space-x-3 cursor-pointer">
                <input type="checkbox" v-model="localConfig.enable_new_file_check" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                <span class="text-gray-200">Periodically check for new project files</span>
              </label>

              <div class="pl-7 flex items-center space-x-3" :class="{'opacity-50 pointer-events-none': !localConfig.enable_new_file_check}">
                <span class="text-gray-300 text-sm">Check every:</span>
                <select v-model="localConfig.new_file_check_interval" class="bg-cm-input-bg border border-gray-600 text-white rounded px-2 py-1 text-sm outline-none focus:border-cm-blue">
                  <option value="2">2</option>
                  <option value="5">5</option>
                  <option value="10">10</option>
                  <option value="30">30</option>
                  <option value="60">60</option>
                </select>
                <span class="text-gray-300 text-sm">seconds</span>
              </div>

              <label class="flex items-center space-x-3 cursor-pointer pt-2">
                <input type="checkbox" v-model="localConfig.scan_for_secrets" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                <span class="text-gray-200">Scan for secrets (on each copy)</span>
              </label>

              <label class="flex items-center space-x-3 cursor-pointer">
                <input type="checkbox" v-model="localConfig.show_feedback_on_paste" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                <span class="text-gray-200">Show LLM feedback window automatically on paste</span>
              </label>

              <label class="flex items-center space-x-3 cursor-pointer">
                <input type="checkbox" v-model="localConfig.enable_compact_mode_on_minimize" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                <span class="text-gray-200">Activate compact mode when main window is minimized</span>
              </label>

              <label class="flex items-center space-x-3 cursor-pointer pt-2">
                <input type="checkbox" v-model="localConfig.check_for_updates" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                <span class="text-gray-200">Automatically check for updates daily</span>
              </label>
            </div>
          </template>

          <!-- FILE MANAGER -->
          <template v-if="activeTab === 'filemanager'">
            <div class="space-y-6">
              <label class="flex items-center space-x-3 cursor-pointer">
                <input type="checkbox" v-model="localConfig.token_count_enabled" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
                <span class="text-gray-200">Enable token counting</span>
              </label>

              <div class="flex items-center space-x-3">
                <span class="text-gray-200 w-64">Max token limit (empty for none):</span>
                <input type="number" v-model="localConfig.token_limit" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
              </div>

              <div class="flex items-center space-x-3">
                <span class="text-gray-200 w-64">Warn when 'Add all' exceeds:</span>
                <input type="number" v-model="localConfig.add_all_warning_threshold" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
                <span class="text-gray-400 text-sm">files</span>
              </div>

              <div class="flex items-center space-x-3">
                <span class="text-gray-200 w-64">New file alert threshold:</span>
                <input type="number" v-model="localConfig.new_file_alert_threshold" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
                <span class="text-gray-400 text-sm">files</span>
              </div>
            </div>
          </template>

          <!-- PROMPTS -->
          <template v-if="activeTab === 'prompts'">
            <div class="space-y-6">
              <div class="space-y-2">
                <label class="text-gray-200 font-medium">"Copy Code Only" Prompt</label>
                <textarea
                  v-model="localConfig.copy_merged_prompt"
                  rows="3"
                  class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 text-sm outline-none focus:border-cm-blue custom-scrollbar"
                ></textarea>
              </div>

              <div class="space-y-2">
                <label class="text-gray-200 font-medium">Default Intro Instructions</label>
                <textarea
                  v-model="localConfig.default_intro_prompt"
                  rows="4"
                  class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 text-sm outline-none focus:border-cm-blue custom-scrollbar"
                ></textarea>
              </div>

              <div class="space-y-2">
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
            <div class="space-y-2">
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
            <div class="space-y-2">
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