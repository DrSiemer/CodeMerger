<script setup>
import { Check, HelpCircle } from 'lucide-vue-next'

defineProps({
  feedback: { type: Object, required: true },
  isUltra: { type: Boolean, default: false }
})

defineEmits(['confirm', 'cancel'])
</script>

<template>
  <transition name="feedback-slide">
    <div v-if="feedback.active" class="absolute inset-0 z-50 p-1.5 flex flex-col">
      <!-- Success/Error Banner -->
      <div v-if="feedback.mode !== 'confirm'" class="w-full h-full rounded shadow-lg flex items-center justify-center px-2 py-1 overflow-hidden" :class="feedback.mode === 'success' ? 'bg-cm-green' : 'bg-cm-warn'">
        <div class="flex flex-col items-center justify-center text-center">
          <Check v-if="feedback.mode === 'success'" class="w-3.5 h-3.5 text-white mb-0.5 shrink-0" />
          <span class="text-[9px] font-black text-white uppercase tracking-wider leading-tight whitespace-normal max-w-full px-1 text-center">{{ feedback.msg }}</span>
        </div>
      </div>

      <!-- Choice/Confirmation Banner -->
      <div v-else class="w-full h-full rounded shadow-lg bg-[#DE6808] flex flex-col overflow-hidden">
        <template v-if="isUltra">
          <div class="flex-grow flex items-center justify-center pt-1" title="Overwrite pending changes?">
            <span class="text-[10px] font-black text-white uppercase">OWR?</span>
          </div>
          <div class="flex h-7 border-t border-white/20">
            <button @click="$emit('confirm')" class="flex-1 bg-white/10 hover:bg-white/20 text-white text-[11px] font-black transition-colors">Y</button>
            <button @click="$emit('cancel')" class="flex-1 bg-black/10 hover:bg-black/20 text-white/80 text-[11px] font-black transition-colors border-l border-white/20">N</button>
          </div>
        </template>
        <template v-else>
          <div class="flex-grow flex items-center justify-center px-2 py-1">
            <HelpCircle class="w-3.5 h-3.5 text-white mr-1.5 shrink-0" />
            <span class="text-[10px] font-bold text-white uppercase tracking-tighter leading-tight text-center whitespace-normal">{{ feedback.msg }}</span>
          </div>
          <div class="flex h-8 border-t border-white/20">
            <button @click="$emit('confirm')" class="flex-1 bg-white/10 hover:bg-white/20 text-white text-[9px] font-black uppercase tracking-widest transition-colors">Confirm</button>
            <button @click="$emit('cancel')" class="flex-1 bg-black/10 hover:bg-black/20 text-white/80 text-[9px] font-black uppercase tracking-widest transition-colors border-l border-white/20">Abort</button>
          </div>
        </template>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.feedback-slide-enter-active, .feedback-slide-leave-active { transition: transform 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67), opacity 0.2s ease; }
.feedback-slide-enter-from { transform: translateY(10px); opacity: 0; }
.feedback-slide-leave-to { transform: translateY(-10px); opacity: 0; }
</style>