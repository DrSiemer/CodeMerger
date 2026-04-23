<script setup>
import { Loader2, AlertTriangle, Trash2, Eye } from 'lucide-vue-next'

defineProps({
  isCopying: Boolean,
  hasInstructions: Boolean,
  newFileCount: Number,
  hasPending: Boolean,
  hasLastResponse: Boolean,
  pasteTooltip: String
})

defineEmits(['copy', 'paste', 'clear', 'review', 'manage'])
</script>

<template>
  <div class="p-1.5 space-y-1.5">
    <div class="flex items-center space-x-1.5 h-8">
      <button
        @click="$emit('copy', $event)"
        :disabled="isCopying"
        class="flex-grow text-[11px] font-bold py-1.5 rounded shadow transition-all flex items-center justify-center space-x-2 disabled:opacity-50 active:scale-95 leading-tight h-8"
        :class="hasInstructions ? 'bg-cm-blue hover:bg-blue-500 text-white' : 'bg-gray-300 hover:bg-gray-200 text-gray-900'"
        title="Copy with Instructions (Ctrl-Click: Code Only)"
      >
        <Loader2 v-if="isCopying" class="w-3.5 h-3.5 animate-spin" />
        <span v-else class="truncate px-1">Copy Prompt</span>
      </button>

      <button
        v-if="newFileCount > 0"
        @click="$emit('manage', $event)"
        v-info="'new_files_alert'"
        class="bg-gray-800 hover:bg-gray-700 text-cm-green w-6 py-1.5 rounded flex items-center justify-center transition-all active:scale-95 shadow shrink-0 h-8"
        title="New files detected! Click: Manage, Ctrl-Click: Add all"
      >
        <AlertTriangle class="w-4 h-4 animate-pulse" />
      </button>
    </div>

    <div class="w-full flex items-center space-x-1.5">
      <div class="relative flex-grow flex h-8">
        <button
          @click="$emit('paste', $event)"
          class="w-full text-white font-bold py-1.5 rounded text-[11px] transition-all active:scale-95 shadow h-full"
          :class="hasPending ? 'bg-[#DE6808]' : 'bg-cm-green hover:bg-green-600'"
          :title="pasteTooltip"
        >
          <span>Paste</span>
        </button>
        <button
          v-if="hasPending"
          @click.stop="$emit('clear')"
          class="absolute top-0.5 right-0.5 p-0.5 text-white/50 hover:text-white transition-colors"
          title="Clear unapplied response"
        >
          <Trash2 class="w-3 h-3" />
        </button>
      </div>

      <button
        v-if="hasLastResponse"
        @click="$emit('review')"
        class="bg-gray-800 hover:bg-gray-700 text-white w-6 py-1.5 rounded flex items-center justify-center transition-all active:scale-95 shadow shrink-0 h-8"
        title="View response review"
      >
        <Eye class="w-3.5 h-3.5" :class="hasPending ? 'text-[#DE6808]' : 'text-gray-400'" />
      </button>
    </div>
  </div>
</template>