<script setup>
import { FolderPlus, Trash2 } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  pData: {
    type: Object,
    required: true
  },
  isLookingBack: {
    type: Boolean,
    default: false
  }
})

defineEmits(['next'])

const { selectDirectory, getBaseProjectData } = useAppState()

const browseBaseProject = async () => {
  const folder = await selectDirectory()
  if (folder) {
    props.pData.base_project_path = folder
    const existingData = await getBaseProjectData(folder)
    if (existingData && existingData.selected_files?.length) {
      props.pData.base_project_files = existingData.selected_files
    } else {
      props.pData.base_project_files = []
    }
  }
}

const clearBaseProject = () => {
  props.pData.base_project_path = ''
  props.pData.base_project_files = []
}
</script>

<template>
  <div class="max-w-3xl mx-auto flex flex-col h-full w-full">
    <div class="space-y-8">
      <h3 class="text-2xl font-bold text-white">Project Details</h3>
      <div class="space-y-4">
        <p class="text-gray-400 text-lg">Enter the initial details for your new project.</p>
      </div>

      <div class="space-y-6">
        <div v-info="'starter_details_name'">
          <label class="block text-gray-200 font-bold mb-2 uppercase tracking-wider text-xs">Project Name</label>
          <input v-model="pData.name" type="text" class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 focus:border-cm-blue outline-none text-lg" placeholder="e.g. My Next Big Idea">
        </div>

        <div class="pt-6 border-t border-gray-700">
          <label class="block text-gray-200 font-bold mb-2 uppercase tracking-wider text-xs">Start from an existing project <span class="text-[#DE6808]">(OPTIONAL)</span></label>
          <div class="flex items-center space-x-4 mt-3">
            <button @click="browseBaseProject" v-info="'starter_details_base'" class="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded font-semibold transition-colors flex items-center shrink-0">
              <FolderPlus class="w-5 h-5 mr-2" />
              {{ pData.base_project_path ? 'Change base project' : 'Select base project' }}
            </button>

            <div v-if="pData.base_project_path" class="flex items-center space-x-3 bg-cm-input-bg border border-gray-600 rounded px-4 py-2 max-w-full overflow-hidden">
              <span class="text-gray-300 font-mono text-sm truncate">{{ pData.base_project_path }}</span>
              <button @click="clearBaseProject" class="text-gray-500 hover:text-red-400 p-1 rounded transition-colors shrink-0" title="Clear base project">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
            <span v-else class="text-gray-400 font-mono text-sm break-all">No base project selected</span>
          </div>
        </div>

      </div>
    </div>

    <div class="mt-auto pt-8 pb-8">
      <div class="bg-cm-blue/10 border border-cm-blue/30 rounded p-4 text-sm text-blue-100 leading-relaxed italic shadow-inner space-y-2">
        <p>Tip: It is highly recommended to start a fresh chat with your LLM before pasting prompts from this starter.</p>
        <p>Note: All project documentation is written in <span class="font-bold">Markdown</span>. See the <a href="https://www.markdownguide.org/basic-syntax/" target="_blank" class="text-cm-blue hover:underline not-italic font-bold ml-1">Basic Syntax Guide</a> for formatting tips.</p>
      </div>
    </div>
  </div>
</template>