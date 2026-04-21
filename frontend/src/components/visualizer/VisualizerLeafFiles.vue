<script setup>
import { computed } from 'vue'
import { FileCode, ExternalLink } from 'lucide-vue-next'
import MarkdownRenderer from '../MarkdownRenderer.vue'
import { useAppState } from '../../composables/useAppState'
import { getFreshnessColor } from '../../utils/visualizerUtils'

const { activeProject } = useAppState()

const props = defineProps({
  node: Object,
  searchQuery: String,
  rankedMtimeMap: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['open-file', 'select-file'])

const processedLeafFiles = computed(() => {
  if (!props.node || !props.node.files) return [];

  const query = props.searchQuery.trim().toLowerCase();
  if (!query) return props.node.files;

  return [...props.node.files].sort((a, b) => {
    const aMatch = a.path.toLowerCase().includes(query) || (a.description && a.description.toLowerCase().includes(query));
    const bMatch = b.path.toLowerCase().includes(query) || (b.description && b.description.toLowerCase().includes(query));
    if (aMatch && !bMatch) return -1;
    if (!aMatch && bMatch) return 1;
    return 0;
  });
});

const highlightMatch = (text, query) => {
  if (!query || !text) return text;
  const parts = text.split(new RegExp(`(${query})`, 'gi'));
  return parts.map(part =>
    part.toLowerCase() === query.toLowerCase()
      ? `<mark class="bg-yellow-500/30 text-yellow-100 rounded px-0.5">${part}</mark>`
      : part
  ).join('');
};

const getFileFreshnessColor = (path) => {
  // If the file isn't in the rank map (e.g. out of sync), default to 1.0 (Oldest color)
  const ratio = props.rankedMtimeMap[path] !== undefined ? props.rankedMtimeMap[path] : 1.0;
  return getFreshnessColor(ratio);
};
</script>

<template>
  <div class="absolute inset-0 m-2 overflow-y-auto custom-scrollbar bg-[#222222] rounded-xl border border-gray-800 p-6 space-y-4" v-info="'viz_leaf_list'">
    <h4 class="text-lg font-bold text-white mb-4 flex items-center">
      <FileCode class="w-5 h-5 mr-2 text-cm-blue" />
      Files in this node
    </h4>

    <div
      v-for="file in processedLeafFiles"
      :key="file.path"
      @click="emit('select-file', file)"
      class="bg-[#2a2a2a] border border-gray-800 border-l-4 rounded-lg p-5 shadow-sm hover:border-gray-600 transition-all duration-300 cursor-pointer group/file"
      :class="[
        searchQuery && (file.path.toLowerCase().includes(searchQuery.toLowerCase()) || (file.description && file.description.toLowerCase().includes(searchQuery.toLowerCase()))) ? 'ring-1 ring-cm-blue/30 scale-[1.01]' : '',
        searchQuery && !(file.path.toLowerCase().includes(searchQuery.toLowerCase()) || (file.description && file.description.toLowerCase().includes(searchQuery.toLowerCase()))) ? 'opacity-30 grayscale' : ''
      ]"
      :style="{ borderLeftColor: getFileFreshnessColor(file.path) }"
    >
      <div class="flex items-center justify-between mb-3 min-w-0">
        <div class="flex items-center truncate mr-2">
          <span class="text-cm-blue font-mono font-bold text-sm truncate" v-html="highlightMatch(file.path, searchQuery)"></span>
        </div>
        <button
          @click.stop="emit('open-file', file.path)"
          class="p-1.5 rounded bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700 transition-colors shrink-0 ml-2 opacity-0 group-hover/file:opacity-100 shadow"
          title="Open in Editor"
        >
          <ExternalLink class="w-4 h-4" />
        </button>
      </div>
      <MarkdownRenderer
        :content="highlightMatch(file.description, searchQuery)"
        :fontSize="15"
        class="text-gray-300"
      />
    </div>
  </div>
</template>