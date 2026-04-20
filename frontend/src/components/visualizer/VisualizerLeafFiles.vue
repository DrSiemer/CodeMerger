<script setup>
import { computed } from 'vue'
import { FileCode, ExternalLink } from 'lucide-vue-next'

const props = defineProps({
  node: Object,
  searchQuery: String
})

const emit = defineEmits(['open-file'])

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
</script>

<template>
  <div class="absolute inset-0 m-2 overflow-y-auto custom-scrollbar bg-[#222222] rounded-xl border border-gray-800 p-6 space-y-4">
    <h4 class="text-lg font-bold text-white mb-4 flex items-center">
      <FileCode class="w-5 h-5 mr-2 text-cm-blue" />
      Files in this node
    </h4>

    <div
      v-for="file in processedLeafFiles"
      :key="file.path"
      @click="emit('open-file', file.path)"
      class="bg-[#2a2a2a] border rounded-lg p-5 shadow-sm hover:border-gray-500 transition-all duration-300 cursor-pointer group/file"
      :class="[searchQuery && (file.path.toLowerCase().includes(searchQuery.toLowerCase()) || (file.description && file.description.toLowerCase().includes(searchQuery.toLowerCase()))) ? 'border-cm-blue ring-1 ring-cm-blue/30 scale-[1.01]' : 'border-gray-700']"
    >
      <div class="flex items-center justify-between mb-3 min-w-0">
        <span class="text-cm-blue font-mono font-bold text-sm break-all" v-html="highlightMatch(file.path, searchQuery)"></span>
        <ExternalLink class="w-4 h-4 text-gray-500 opacity-0 group-hover/file:opacity-100 transition-opacity shrink-0 ml-2" />
      </div>
      <p class="text-gray-300 text-[15px] leading-relaxed" v-html="highlightMatch(file.description, searchQuery)"></p>
    </div>
  </div>
</template>