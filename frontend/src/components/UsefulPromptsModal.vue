<script setup>
import { ref, onMounted } from 'vue'
import {
  X, Sparkles, Eraser, Anchor, Droplets,
  Hash, Skull, ChevronDown, ChevronUp
} from 'lucide-vue-next'
import { useAppState } from '../composables/useAppState'
import { useEscapeKey } from '../composables/useEscapeKey'
import { WINDOW_SIZES } from '../utils/constants'

const emit = defineEmits(['close'])
const { copyUsefulPrompt, resizeWindow } = useAppState()

const expandedId = ref(null)

useEscapeKey(() => emit('close'))

const prompts = [
  {
    id: 'cleanup',
    title: 'Comment Cleanup',
    icon: Eraser,
    hoverColor: 'group-hover:text-green-400',
    description: 'Instructs the AI to strip historical notes, redundant explanations, and transient tags from your comments while strictly preserving all code logic and structure.'
  },
  {
    id: 'brutal_review',
    title: 'Brutal Review',
    icon: Skull,
    hoverColor: 'group-hover:text-red-500',
    description: 'Prompts the AI to act as an impatient senior reviewer. Expect concise, direct, and unvarnished feedback identifying over-engineering and logic flaws.'
  },
  {
    id: 'dead_weight',
    title: 'Find Dead Weight',
    icon: Anchor,
    hoverColor: 'group-hover:text-orange-400',
    description: 'An audit prompt that asks the AI to identify and remove unused functions, variables, imports, and orphan files that are no longer referenced in the current context.'
  },
  {
    id: 'dry_up',
    title: 'DRY Up Code',
    icon: Droplets,
    hoverColor: 'group-hover:text-blue-400',
    description: 'Directs the AI to find duplicated logic patterns and suggest reusable abstractions to reduce redundancy without changing the application behavior.'
  },
  {
    id: 'magic_numbers',
    title: 'Hunt Magic Numbers',
    icon: Hash,
    hoverColor: 'group-hover:text-purple-400',
    description: 'Focuses on extracting hardcoded numerical values into named constants, moving them to your project\'s centralized constants or configuration files.'
  }
]

onMounted(async () => {
  await resizeWindow(WINDOW_SIZES.USEFUL_PROMPTS.width, WINDOW_SIZES.USEFUL_PROMPTS.height)
})

const handleCopyAndClose = async (pId) => {
  await copyUsefulPrompt(pId)
  emit('close')
}

const toggleExpand = (id) => {
  expandedId.value = expandedId.value === id ? null : id
}
</script>

<template>
  <div id="useful-prompts-modal" class="absolute inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
    <div class="bg-cm-dark-bg w-full max-w-[500px] rounded shadow-2xl border border-gray-600 flex flex-col max-h-[85%] overflow-hidden">

      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700 bg-cm-top-bar">
        <div class="flex items-center space-x-3 text-white" v-info="'useful_prompts'">
          <Sparkles class="w-5 h-5 text-cm-blue" />
          <h2 class="text-xl font-bold">Useful Prompts</h2>
        </div>
        <button @click="emit('close')" class="text-gray-400 hover:text-white transition-colors" title="Close prompts menu">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="p-5 flex-grow flex flex-col min-h-0">
        <p class="text-gray-400 text-sm mb-4" v-info="'useful_prompts_instruction'">Click a prompt to copy it to your clipboard and close this window.</p>

        <!-- List Container -->
        <div class="flex-grow overflow-y-auto pr-1 custom-scrollbar">
          <div
            v-for="p in prompts"
            :key="p.id"
            class="flex flex-col"
          >
            <div class="flex items-stretch group transition-colors rounded-md overflow-hidden">
              <!-- Copy Action Zone -->
              <button
                @click="handleCopyAndClose(p.id)"
                v-info="'useful_prompts_item'"
                class="flex-grow flex items-center py-2 px-4 space-x-4 text-left hover:bg-white/5 transition-colors"
              >
                <div
                  class="w-8 h-8 rounded bg-gray-800/50 flex items-center justify-center text-gray-500 transition-all duration-300 shrink-0"
                  :class="p.hoverColor"
                >
                  <component :is="p.icon" class="w-4 h-4" />
                </div>
                <span class="text-white font-semibold">{{ p.title }}</span>
              </button>

              <!-- Expand Toggle Zone -->
              <button
                @click="toggleExpand(p.id)"
                v-info="'useful_prompts_expand'"
                class="w-12 shrink-0 flex items-center justify-center hover:bg-white/10 transition-colors text-gray-500 hover:text-gray-300"
                :title="expandedId === p.id ? 'Hide description' : 'Show description'"
              >
                <ChevronUp v-if="expandedId === p.id" class="w-4 h-4 text-cm-blue" />
                <ChevronDown v-else class="w-4 h-4" />
              </button>
            </div>

            <!-- Description -->
            <transition name="expand">
              <div v-if="expandedId === p.id" class="overflow-hidden">
                <div class="px-16 pb-4 pt-0">
                   <p class="text-sm text-gray-400 leading-relaxed italic">
                     {{ p.description }}
                   </p>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease-out;
  max-height: 150px;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>