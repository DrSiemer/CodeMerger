<script setup>
import { FileCode, ClipboardPaste } from 'lucide-vue-next'

defineProps({
  displayNode: Object,
  canCopy: Boolean
})

const emit = defineEmits(['copy-code', 'open-file'])
</script>

<template>
  <div class="w-1/3 flex flex-col p-8 bg-black/20 overflow-y-auto custom-scrollbar" v-info="'viz_details'">
    <div v-if="displayNode" class="space-y-8 animate-in fade-in duration-300">
      <!-- Title & Domain -->
      <div class="space-y-2">
        <div class="flex items-start justify-between">
          <h3 class="text-3xl font-extralight text-white leading-tight break-words pr-4">{{ displayNode.name }}</h3>
          <span v-if="displayNode.domain" class="text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded shrink-0" :style="{ backgroundColor: displayNode.color + '40', color: displayNode.color }">{{ displayNode.domain }}</span>
        </div>
        <div class="h-1 w-20 rounded" :style="{ backgroundColor: displayNode.color }"></div>
      </div>

      <!-- Description -->
      <div class="space-y-4">
        <div class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]">Architectural Description</div>
        <p class="text-gray-200 text-lg leading-relaxed italic">"{{ displayNode.description || "No description provided for this node." }}"</p>
      </div>

      <!-- Actions (Contextual Copy) -->
      <div v-if="canCopy" class="space-y-4 pt-6 border-t border-gray-700/50">
        <div class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]">Actions</div>
        <button
          @click="emit('copy-code', displayNode)"
          v-info="'viz_details_copy'"
          class="hover:brightness-110 text-white px-6 py-2 rounded font-black text-[10px] uppercase tracking-widest shadow-lg transition-all flex items-center justify-center space-x-2 active:scale-[0.98] w-fit"
          :style="{ backgroundColor: displayNode.color }"
        >
          <ClipboardPaste class="w-3.5 h-3.5" />
          <span>Copy Merged Code</span>
        </button>
      </div>

      <!-- Quick File List -->
      <div v-if="displayNode.files?.length" class="space-y-4 pt-6">
        <div class="text-xs font-black text-gray-500 uppercase tracking-[0.2em]">Files ({{ displayNode.files.length }})</div>
        <div class="space-y-1">
          <div
            v-for="file in displayNode.files"
            :key="file.path"
            @click="emit('open-file', file.path)"
            class="flex items-center space-x-2 text-gray-400 group cursor-pointer hover:text-white transition-colors"
          >
              <FileCode class="w-3 h-3 text-gray-600 group-hover:text-cm-blue shrink-0 transition-colors" />
              <span class="text-xs font-mono truncate text-gray-300 group-hover:text-white transition-colors">{{ file.path }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="h-full flex items-center justify-center text-gray-600 italic">
      Select a node to view details
    </div>
  </div>
</template>