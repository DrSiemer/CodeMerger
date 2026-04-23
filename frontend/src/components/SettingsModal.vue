<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import {
  X, Settings, FolderClosed, Bot, Play,
  Terminal, FileCode2
} from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { useEscapeKey } from '../composables/useEscapeKey'
import { WINDOW_SIZES } from '../utils/constants'

import SettingsAppTab from './settings/SettingsAppTab.vue'
import SettingsFileManagerTab from './settings/SettingsFileManagerTab.vue'
import SettingsFiletypesTab from './settings/SettingsFiletypesTab.vue'
import SettingsPromptsTab from './settings/SettingsPromptsTab.vue'
import SettingsStarterTab from './settings/SettingsStarterTab.vue'
import SettingsEditorTab from './settings/SettingsEditorTab.vue'

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

const localFiletypes = ref([])

const initialConfigString = ref('')
const initialFiletypesString = ref('')

useEscapeKey(() => emit('close'))

onMounted(async () => {
  // Smart Growth: Ensure the main window is large enough for the settings layout
  await resizeWindow(WINDOW_SIZES.SETTINGS.width, WINDOW_SIZES.SETTINGS.height)

  localConfig.value = JSON.parse(JSON.stringify(config.value))
  initialConfigString.value = JSON.stringify(localConfig.value)

  localFiletypes.value = await getFiletypes()
  initialFiletypesString.value = JSON.stringify(localFiletypes.value)
})

const hasChanges = computed(() => {
  if (!initialConfigString.value || !initialFiletypesString.value) return false
  return JSON.stringify(localConfig.value) !== initialConfigString.value ||
         JSON.stringify(localFiletypes.value) !== initialFiletypesString.value
})

const handleSave = async () => {
  localConfig.value.new_file_check_interval = parseInt(localConfig.value.new_file_check_interval) || 5
  localConfig.value.token_limit = parseInt(localConfig.value.token_limit) || 0
  localConfig.value.add_all_warning_threshold = parseInt(localConfig.value.add_all_warning_threshold) || 50
  localConfig.value.new_file_alert_threshold = parseInt(localConfig.value.new_file_alert_threshold) || 5

  await saveConfig(localConfig.value)
  await saveFiletypes(localFiletypes.value)
  emit('close')
}

const tabs = [
  { id: 'application', name: 'Application', icon: markRaw(Settings), info: 'set_app', component: markRaw(SettingsAppTab) },
  { id: 'filemanager', name: 'File Manager', icon: markRaw(FolderClosed), info: 'set_fm', component: markRaw(SettingsFileManagerTab) },
  { id: 'filetypes', name: 'Filetypes', icon: markRaw(FileCode2), info: 'filetypes', component: markRaw(SettingsFiletypesTab) },
  { id: 'prompts', name: 'Prompts', icon: markRaw(Bot), info: 'set_prompts', component: markRaw(SettingsPromptsTab) },
  { id: 'starter', name: 'Starter', icon: markRaw(Play), info: 'set_starter', component: markRaw(SettingsStarterTab) },
  { id: 'editor', name: 'Editor', icon: markRaw(Terminal), info: 'set_editor', component: markRaw(SettingsEditorTab) }
]

const activeTabInfoKey = computed(() => {
  return tabs.find(t => t.id === activeTab.value)?.info || ''
})
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
          <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors" title="Close settings window">
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Scrollable Settings Body -->
        <div class="flex-grow overflow-y-auto p-6 custom-scrollbar flex flex-col">

          <component
            :is="tabs.find(t => t.id === activeTab)?.component"
            :localConfig="localConfig"
            :localFiletypes="localFiletypes"
          />

        </div>

        <!-- Footer -->
        <div class="p-4 border-t border-gray-700 shrink-0 bg-cm-top-bar flex justify-end">
          <template v-if="hasChanges">
            <button
              @click="emit('close')"
              v-info="'settings_cancel'"
              class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-5 rounded mr-3 transition-colors"
              title="Discard modifications and exit"
            >
              Cancel
            </button>
            <button
              id="btn-settings-save"
              @click="handleSave"
              v-info="'settings_save'"
              class="bg-cm-blue hover:bg-blue-500 text-white font-medium py-2 px-5 rounded shadow-sm transition-colors"
              title="Commit all settings to configuration"
            >
              Save Changes
            </button>
          </template>
          <template v-else>
            <button
              @click="emit('close')"
              v-info="'settings_cancel'"
              class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-2 px-5 rounded transition-colors"
              title="Close settings window"
            >
              Close
            </button>
          </template>
        </div>
      </div>

    </div>
  </div>
</template>