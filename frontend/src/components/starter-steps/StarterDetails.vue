<script setup>
import { FolderPlus, Trash2, Sparkles, LayoutPanelLeft } from 'lucide-vue-next'
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

const emit = defineEmits(['next'])

const { selectDirectory, getBaseProjectData, statusMessage } = useAppState()

const setStartFresh = () => {
  props.pData.starting_mode = 'fresh'
}

const setUseReference = () => {
  props.pData.starting_mode = 'base'
}

const browseBaseProject = async () => {
  const folder = await selectDirectory()
  if (folder) {
    props.pData.base_project_path = folder
    const existingData = await getBaseProjectData(folder)

    if (existingData?.status_msg?.startsWith("ERROR")) {
      statusMessage.value = existingData.status_msg
      props.pData.base_project_path = ''
      props.pData.base_project_files = []
      return
    }

    props.pData.starting_mode = 'base'

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
  props.pData.starting_mode = null
}
</script>

<template>
  <div class="max-w-4xl mx-auto flex flex-col h-full w-full">
    <div class="space-y-8">
      <div class="text-center space-y-2">
        <h3 class="text-3xl font-bold text-white">Choose your starting point</h3>
        <p class="text-gray-400 text-lg">Decide whether to begin with a blank slate or use an existing project as a reference.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
        <!-- Option 1: Start Fresh -->
        <button
          @click="setStartFresh"
          class="flex flex-col items-center text-center p-8 rounded-xl border-2 transition-all duration-300 group relative overflow-hidden"
          :class="pData.starting_mode === 'fresh' ? 'bg-cm-blue/10 border-cm-blue shadow-lg' : 'bg-gray-800/40 border-gray-700 hover:border-gray-500 hover:bg-gray-800/60'"
        >
          <div class="w-16 h-16 rounded-full bg-cm-blue/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <Sparkles class="w-8 h-8 text-cm-blue" />
          </div>
          <h4 class="text-xl font-bold text-white mb-2">Start Fresh</h4>
          <p class="text-gray-400 text-sm leading-relaxed">Begin a completely new project from scratch. Best for exploring new ideas or unique architectures.</p>
        </button>

        <!-- Option 2: Reference Project -->
        <div
          @click="setUseReference"
          class="flex flex-col items-center text-center p-8 rounded-xl border-2 transition-all duration-300 group relative overflow-hidden cursor-pointer"
          :class="pData.starting_mode === 'base' ? 'bg-cm-blue/10 border-cm-blue shadow-lg' : 'bg-gray-800/40 border-gray-700 hover:border-gray-500 hover:bg-gray-800/60'"
        >
          <div class="w-16 h-16 rounded-full bg-cm-blue/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <LayoutPanelLeft class="w-8 h-8 text-cm-blue" />
          </div>
          <h4 class="text-xl font-bold text-white mb-2">Use Reference</h4>
          <p class="text-gray-400 text-sm leading-relaxed mb-6">Load an existing project to guide the AI on coding style, tech stack, and architectural patterns.</p>

          <button
            @click.stop="browseBaseProject"
            v-info="'starter_details_base'"
            class="mt-auto bg-gray-700 hover:bg-gray-600 text-white px-6 py-2.5 rounded font-bold transition-colors flex items-center text-sm shadow-md"
          >
            <FolderPlus class="w-4 h-4 mr-2" />
            {{ pData.base_project_path ? 'Change reference' : 'Select reference folder' }}
          </button>

          <div v-if="pData.base_project_path" class="mt-4 flex items-center space-x-2 bg-black/30 px-3 py-1.5 rounded-full border border-gray-700 max-w-full">
            <span class="text-gray-300 font-mono text-[10px] truncate">{{ pData.base_project_path }}</span>
            <button @click="clearBaseProject" class="text-gray-500 hover:text-red-400 transition-colors" title="Clear selection">
               <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-auto pt-12 pb-8">
      <div class="bg-cm-blue/10 border border-cm-blue/30 rounded p-4 text-sm text-blue-100 leading-relaxed italic shadow-inner space-y-2">
        <p>Tip: It is highly recommended to start a fresh chat with your LLM before pasting prompts from this starter.</p>
        <p>Note: All project documentation is written in <span class="font-bold">Markdown</span>. See the <a href="https://www.markdownguide.org/basic-syntax/" target="_blank" class="text-cm-blue hover:underline not-italic font-bold ml-1">Basic Syntax Guide</a> for formatting tips.</p>
      </div>
    </div>
  </div>
</template>