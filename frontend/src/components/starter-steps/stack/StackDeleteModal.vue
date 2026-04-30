<script setup>
import { computed } from 'vue'
import { Trash2 } from 'lucide-vue-next'

const props = defineProps({
  target: Object
})

defineEmits(['confirm', 'abort'])

const hasVisibleWarning = computed(() => {
  const t = props.target
  if (!t || t.isManual || !t.warning) return false
  const low = t.warning.toLowerCase()
  return !(low.includes('manually added') || low.trim() === '')
})
</script>

<template>
  <Teleport to="#project-starter-modal">
    <div class="absolute inset-0 bg-black/85 flex items-center justify-center z-[110] p-4">
      <div class="bg-cm-dark-bg w-full max-w-lg rounded-xl shadow-2xl border border-gray-700 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div class="bg-cm-top-bar px-6 py-5 border-b border-gray-700 flex items-center space-x-3">
          <Trash2 class="w-5 h-5 text-gray-400" />
          <h3 class="text-xl font-bold text-white">Remove Subject?</h3>
        </div>

        <div class="p-8 space-y-6">
          <p class="text-gray-200 text-lg leading-snug">Are you sure you want to remove <span class="font-black text-cm-blue">{{ target?.tech || 'this item' }}</span> from the project stack?</p>

          <div v-if="hasVisibleWarning" class="bg-black/30 border border-gray-800 rounded-lg p-5">
            <span class="block text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] mb-2">Architectural Warning</span>
            <p v-info="'starter_stack_delete_warning'" class="text-gray-300 leading-relaxed">{{ target?.warning }}</p>
          </div>
        </div>

        <div class="px-6 py-5 bg-cm-top-bar border-t border-gray-800 flex justify-end space-x-3">
          <button @click="$emit('abort')" class="px-6 py-2 rounded font-bold text-gray-400 hover:text-white transition-colors">Cancel</button>
          <button @click="$emit('confirm')" class="bg-cm-warn hover:bg-red-600 text-white font-bold px-10 py-2 rounded shadow-lg transition-all">Remove</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>