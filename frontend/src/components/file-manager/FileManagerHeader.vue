<script setup>
import { X } from 'lucide-vue-next'

defineProps({
  projectName: {
    type: String,
    required: true
  }
})

defineEmits(['close'])
</script>

<template>
  <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-cm-top-bar shrink-0">
    <div class="flex items-center space-x-3">
      <h2 class="text-xl font-bold text-white">Edit Merge List</h2>
      <span class="text-gray-500 text-sm font-medium">/ {{ projectName }}</span>
    </div>
    <button @click="$emit('close')" class="text-gray-400 hover:text-white transition-colors" title="Close merge list editor">
      <X class="w-6 h-6" />
    </button>
  </div>
</template>