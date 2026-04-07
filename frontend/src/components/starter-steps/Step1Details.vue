<script setup>
import { FolderPlus } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  pData: {
    type: Object,
    required: true
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
</script>

<template>
  <div class="max-w-3xl mx-auto flex flex-col h-full w-full">
    <div class="space-y-8">
      <h3 class="text-2xl font-bold text-white">Project Details</h3>
      <div class="space-y-4">
        <p class="text-gray-400 text-lg">Enter the initial details for your new project.</p>
      </div>

      <div class="space-y-6">
        <div>
          <label class="block text-gray-200 font-bold mb-2 uppercase tracking-wider text-xs">Project Name</label>
          <input v-model="pData.name" type="text" class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 focus:border-cm-blue outline-none text-lg" placeholder="e.g. My Next Big Idea">
        </div>

        <div class="pt-6 border-t border-gray-700">
          <label class="block text-gray-200 font-bold mb-2 uppercase tracking-wider text-xs">Start from an existing project <span class="text-[#DE6808]">(OPTIONAL)</span></label>
          <div class="flex items-center space-x-4 mt-3">
            <button @click="browseBaseProject" class="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded font-semibold transition-colors flex items-center shrink-0">
              <FolderPlus class="w-5 h-5 mr-2" />
              Select base project
            </button>
            <span class="text-gray-400 font-mono text-sm break-all">{{ pData.base_project_path || 'No base project selected' }}</span>
          </div>
        </div>

        <div v-if="pData.name.trim()" class="pt-8 animate-in fade-in slide-in-from-top-2 duration-300">
            <button @click="$emit('next')" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-3 px-12 rounded shadow-lg transition-all flex items-center">
              Next Step &gt;
            </button>
        </div>
      </div>
    </div>

    <div class="mt-auto pt-8">
      <div class="bg-cm-blue/10 border border-cm-blue/30 rounded p-4 text-sm text-blue-100 leading-relaxed italic shadow-inner">
        Tip: It is highly recommended to start a fresh chat with your LLM before pasting prompts from this starter.
      </div>
    </div>
  </div>
</template>