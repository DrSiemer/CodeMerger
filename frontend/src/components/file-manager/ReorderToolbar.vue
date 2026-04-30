<script setup>
import { ArrowUpToLine, ArrowUp, ArrowDown, ArrowDownToLine } from 'lucide-vue-next'

defineProps({
  hasSelection: { type: Boolean, default: false }
})

defineEmits(['top', 'up', 'remove', 'down', 'bottom'])
</script>

<template>
  <div id="fm-reorder-toolbar" class="flex items-center justify-center space-x-2 pt-2">
    <button @click="$emit('top')" v-info="'fm_sort_top'" class="p-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="!hasSelection" title="Move Selected to Top"><ArrowUpToLine class="w-4 h-4" /></button>
    <button @click="$emit('up')" v-info="'fm_sort_up'" class="p-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="!hasSelection" title="Move Selected Up"><ArrowUp class="w-4 h-4" /></button>
    <button @click="$emit('remove')" v-info="'fm_sort_remove'" class="px-5 py-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-red-900/50 enabled:hover:text-red-400 text-gray-400 disabled:opacity-30 text-sm font-medium transition-colors" :disabled="!hasSelection" title="Remove Selected (Delete Key)">Remove</button>
    <button @click="$emit('down')" v-info="'fm_sort_down'" class="p-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="!hasSelection" title="Move Selected Down"><ArrowDown class="w-4 h-4" /></button>
    <button @click="$emit('bottom')" v-info="'fm_sort_bottom'" class="p-2 bg-gray-800 border border-gray-700 rounded enabled:hover:bg-gray-700 text-gray-400 disabled:opacity-30" :disabled="!hasSelection" title="Move Selected to Bottom"><ArrowDownToLine class="w-4 h-4" /></button>
  </div>
</template>