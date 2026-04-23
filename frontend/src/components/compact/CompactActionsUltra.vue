<script setup>
import { Loader2, AlertTriangle, Trash2, Eye } from 'lucide-vue-next'

defineProps({
  isCopying: Boolean,
  newFileCount: Number,
  hasPending: Boolean,
  hasLastResponse: Boolean,
  pasteTooltip: String
})

defineEmits(['copy', 'paste', 'clear', 'review', 'manage'])
</script>

<template>
  <div class="pt-0.5 px-1 pb-0 items-center space-y-1">
    <div class="flex items-center gap-1 w-full max-w-[64px]">
      <div class="relative flex-grow">
        <button
          @click="$emit('copy', $event)"
          @mousedown.stop
          :disabled="isCopying"
          class="w-full bg-cm-blue hover:bg-blue-500 text-white h-6 rounded flex items-center justify-center transition-all active:scale-95 disabled:opacity-50 text-[11px] font-black leading-none"
          title="Copy Prompt (Ctrl-Click: Code Only)"
        >
          <Loader2 v-if="isCopying" class="w-3.5 h-3.5 animate-spin" />
          <span v-else>C</span>
        </button>
      </div>
      <button
        v-if="newFileCount > 0"
        @click="$emit('manage', $event)"
        @mousedown.stop
        v-info="'new_files_alert'"
        class="bg-gray-800 hover:bg-gray-700 text-cm-green w-6 h-6 rounded flex items-center justify-center transition-all active:scale-95 shadow shrink-0"
        title="New files detected! Click: Manage, Ctrl-Click: Add all"
      >
        <AlertTriangle class="w-3.5 h-3.5 animate-pulse" />
      </button>
    </div>

    <div class="flex items-center gap-1 w-full max-w-[64px]">
      <div class="relative flex-grow">
        <button
          @click="$emit('paste', $event)"
          @mousedown.stop
          class="w-full text-white h-6 rounded flex items-center justify-center transition-all active:scale-95 text-[11px] font-black leading-none"
          :class="hasPending ? 'bg-[#DE6808]' : 'bg-cm-green hover:bg-green-600'"
          :title="pasteTooltip"
        >
          <span>P</span>
        </button>
        <button
          v-if="hasPending"
          @click.stop="$emit('clear')"
          @mousedown.stop
          class="absolute -top-1 -right-1 p-0.5 bg-gray-900 rounded-full text-white/70 hover:text-white shadow-sm border border-gray-700 transition-colors"
          title="Clear unapplied response"
        >
          <Trash2 class="w-2 h-2" />
        </button>
      </div>
      <button
        v-if="hasLastResponse"
        @click="$emit('review')"
        @mousedown.stop
        class="w-6 h-6 rounded flex items-center justify-center transition-all active:scale-95 bg-gray-800 text-gray-400 hover:text-white shrink-0"
        title="View response review"
      >
        <Eye class="w-3.5 h-3.5" :class="hasPending ? 'text-[#DE6808]' : 'text-gray-400'" />
      </button>
    </div>
  </div>
</template>