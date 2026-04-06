<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Search, X } from 'lucide-vue-next'
import { useAppState } from '../../composables/useAppState'
import FileTreeNode from '../FileTreeNode.vue'

const props = defineProps({
  pData: {
    type: Object,
    required: true
  }
})

const { getBaseFileTree, getTokenCountForPath } = useAppState()

const baseFileTree = ref([])
const baseFilterText = ref('')
const baseIsExtFilter = ref(true)
const baseIsGitFilter = ref(true)

const refreshBaseTree = async () => {
  baseFileTree.value = await getBaseFileTree(
    props.pData.base_project_path,
    baseFilterText.value,
    baseIsExtFilter.value,
    baseIsGitFilter.value,
    props.pData.base_project_files
  )
}

onMounted(() => {
  if (props.pData.base_project_path) {
    refreshBaseTree()
  }
})

watch(baseFilterText, () => refreshBaseTree())

const toggleBaseFile = async (path) => {
  const idx = props.pData.base_project_files.findIndex(f => f.path === path)
  if (idx !== -1) {
    props.pData.base_project_files.splice(idx, 1)
  } else {
    const tokens = await getTokenCountForPath(props.pData.base_project_path, path)
    props.pData.base_project_files.push({ path, tokens, ignoreTokens: false })
  }
}

const baseTotalTokens = computed(() => {
  return props.pData.base_project_files.reduce((acc, f) => acc + (f.tokens || 0), 0)
})
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex items-center justify-between mb-4 shrink-0">
      <div>
        <h3 class="text-2xl font-bold text-white">Select Base Files</h3>
        <p class="text-gray-400 text-sm">Choose files from <span class="text-cm-blue font-mono">{{ pData.base_project_path }}</span> as reference context.</p>
      </div>
      <div class="text-right">
        <div class="text-xs font-bold text-gray-500 uppercase">Starter Selection</div>
        <div class="text-cm-blue font-mono font-bold">{{ pData.base_project_files.length }} files / {{ baseTotalTokens.toLocaleString() }} tokens</div>
      </div>
    </div>

    <div class="flex-grow flex min-h-0 border border-gray-700 rounded overflow-hidden">
      <div class="w-1/2 flex flex-col bg-gray-900 border-r border-gray-700 p-4">
        <div class="relative mb-4">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input v-model="baseFilterText" type="text" placeholder="Filter base project..." class="w-full bg-cm-input-bg text-white pl-10 pr-4 py-2 rounded border border-gray-700 outline-none text-sm">
        </div>
        <div class="flex-grow overflow-y-auto custom-scrollbar">
          <FileTreeNode
            v-for="node in baseFileTree"
            :key="node.path"
            :node="node"
            :selected-paths="pData.base_project_files.map(f => f.path)"
            @toggle-select="toggleBaseFile"
          />
        </div>
      </div>
      <div class="w-1/2 flex flex-col bg-cm-dark-bg p-4">
        <div class="flex items-center justify-between mb-4">
          <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">Merge Order</span>
        </div>
        <div class="flex-grow overflow-y-auto custom-scrollbar space-y-1 pr-1">
          <div v-for="(file, idx) in pData.base_project_files" :key="file.path" class="flex items-center justify-between bg-cm-input-bg p-2 rounded border border-gray-700 group transition-colors hover:border-gray-500">
            <span class="text-sm text-gray-300 truncate pr-4">{{ file.path }}</span>
            <button @click="pData.base_project_files.splice(idx, 1)" class="text-gray-500 hover:text-red-400 p-1 transition-colors"><X class="w-4 h-4"/></button>
          </div>
          <div v-if="!pData.base_project_files.length" class="h-full flex items-center justify-center text-gray-600 italic">No files selected.</div>
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
  background: #444;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>