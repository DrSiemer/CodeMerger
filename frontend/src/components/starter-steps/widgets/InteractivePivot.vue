<script setup>
import { ref } from 'vue'
import { Waypoints, Check, ChevronDown, ChevronUp } from 'lucide-vue-next'
import MarkdownRenderer from '../../MarkdownRenderer.vue'

const props = defineProps({
  chunk: Object,
  isLocked: Boolean,
  fontSize: Number
})

const emit = defineEmits(['pivot', 'discard'])

const isOpen = ref(false)

const handleToggle = () => {
  if (!props.isLocked) isOpen.value = !isOpen.value
}
</script>

<template>
  <div class="pt-6 mb-0">
    <div
      @click="handleToggle"
      class="border-l-4 border-cm-blue pl-6 pt-8 pb-1 bg-blue-900/10 rounded-r-lg text-gray-200 shadow-md relative group transition-all mb-0"
      :class="!isLocked ? 'cursor-pointer hover:bg-blue-900/20' : 'cursor-default'"
    >
      <div class="absolute -top-3.5 left-3 right-4 flex items-center justify-between">
        <div class="flex items-center space-x-2 pointer-events-none">
          <span class="bg-cm-blue text-white text-[10px] font-black px-2 py-1 rounded shadow tracking-widest uppercase">Selected Path</span>
          <div v-if="!isLocked" class="bg-gray-800 text-cm-blue text-[10px] font-bold px-2 py-1 rounded shadow border border-cm-blue/30 group-hover:border-cm-blue transition-colors">Click to see alternatives</div>
        </div>

        <div v-if="!isLocked" class="flex items-center space-x-3">
          <button
            @click.stop="$emit('discard', chunk)"
            class="bg-cm-top-bar border border-gray-600 text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-cm-green hover:border-cm-green/50 flex items-center px-3 py-1 rounded shadow-lg transition-all active:scale-95 pointer-events-auto"
            title="Finalize this choice and remove alternatives"
          >
            <Check class="w-3.5 h-3.5 mr-1.5" />
            Accept Path
          </button>

          <div class="text-cm-blue/60 group-hover:text-cm-blue transition-colors bg-cm-top-bar p-1 rounded-full border border-gray-600 shadow-md pointer-events-none">
             <ChevronDown v-if="!isOpen" class="w-5 h-5" />
             <ChevronUp v-else class="w-5 h-5" />
          </div>
        </div>
      </div>

      <MarkdownRenderer :content="chunk.selectedText" :fontSize="fontSize" />
    </div>

    <transition name="pivot-slide">
      <div v-if="isOpen && !isLocked" class="pl-4 border-l-2 border-dashed border-gray-700 space-y-2 pt-7 pb-2">
        <div class="flex items-center justify-between ml-2">
          <div class="flex items-center text-gray-500">
            <Waypoints class="w-4 h-4 mr-2" />
            <span class="text-[10px] font-black uppercase tracking-widest">Architectural Alternatives</span>
          </div>
        </div>
        <div class="grid grid-cols-1 gap-3">
          <button
            v-for="alt in chunk.alternatives"
            :key="alt.title"
            @click="$emit('pivot', alt, chunk.selectedText)"
            class="bg-gray-800 border border-gray-700 hover:border-cm-blue hover:bg-gray-700 p-4 rounded-lg text-left transition-all group flex flex-col shadow-sm relative overflow-hidden"
          >
            <div class="absolute top-0 right-0 w-1 h-full bg-cm-blue transform translate-x-full group-hover:translate-x-0 transition-transform"></div>
            <div class="font-bold text-cm-blue mb-1 text-base group-hover:text-blue-400">{{ alt.title }}</div>
            <div class="text-sm text-gray-400 group-hover:text-gray-300 leading-relaxed">{{ alt.description }}</div>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.pivot-slide-enter-active, .pivot-slide-leave-active { transition: all 0.3s ease-out; max-height: 800px; }
.pivot-slide-enter-from, .pivot-slide-leave-to { opacity: 0; max-height: 0; transform: translateY(-10px); }
</style>