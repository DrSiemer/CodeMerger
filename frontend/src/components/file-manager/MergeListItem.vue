<script setup>
import { computed } from 'vue'

const props = defineProps({
  file: { type: Object, required: true },
  index: { type: Number, required: true },
  isSelected: { type: Boolean, default: false },
  isHighlighted: { type: Boolean, default: false },
  showFullPaths: { type: Boolean, default: false },
  filterText: { type: String, default: '' },
  tokenColorThreshold: { type: Number, default: 4000 },
  maxTokensInList: { type: Number, default: 4000 }
})

const emit = defineEmits(['click', 'dblclick', 'token-interaction'])

const matchesFilter = computed(() => {
  if (!props.filterText) return true
  return props.file.path.toLowerCase().includes(props.filterText.toLowerCase())
})

const getTokenColor = computed(() => {
  if (props.file.ignoreTokens) return 'text-gray-600'
  const count = props.file.tokens
  if (count === undefined || count === null || count < 0) return 'text-gray-500'

  const p = count / props.maxTokensInList
  if (p < 0.2) return 'text-gray-500'
  if (p < 0.4) return 'text-gray-400'
  if (p < 0.6) return 'text-[#B77B06]'
  if (p < 0.8) return 'text-[#DE6808]'
  return 'text-[#DF2622]'
})

const displayName = computed(() => {
  return props.showFullPaths ? props.file.path : props.file.path.split('/').pop()
})
</script>

<template>
  <li
    v-show="matchesFilter"
    v-info="'fm_list_item'"
    class="group flex items-center border rounded p-2 text-sm transition-all duration-300"
    :class="[
      isSelected ? 'bg-cm-blue border-cm-blue' : 'bg-cm-input-bg border-gray-700 hover:border-gray-500',
      isHighlighted ? 'ring-1 ring-cm-blue/50 bg-cm-blue/20 border-cm-blue/50' : ''
    ]"
    @click="$emit('click', $event)"
    @dblclick="$emit('dblclick')"
    :title="`${file.path} (Double-click to open)`"
  >
    <!-- Drag Handle for @formkit/drag-and-drop -->
    <div class="drag-handle cursor-grab active:cursor-grabbing mr-3 text-gray-600 group-hover:text-gray-400" @click.stop>
      <div class="grid grid-cols-2 gap-0.5 w-3">
        <div v-for="n in 6" :key="n" class="w-1 h-1 bg-current rounded-full"></div>
      </div>
    </div>

    <span class="flex-grow truncate pr-4" :class="isSelected ? 'text-white font-medium' : 'text-gray-200'">
      {{ displayName }}
    </span>

    <div
      class="flex items-center space-x-3 shrink-0 cursor-help"
      @click="$emit('token-interaction', $event)"
      title="Ctrl+Click: Copy refactor request | Alt+Click: Toggle Ignore tokens"
      v-info="'fm_tokens_item'"
    >
      <span class="text-xs font-mono" :class="isSelected ? 'text-blue-100 font-bold' : getTokenColor">
        {{ file.ignoreTokens ? `[${file.tokens?.toLocaleString()}]` : ((file.tokens !== undefined && file.tokens !== null && file.tokens >= 0) ? file.tokens.toLocaleString() : '?') }}
      </span>
    </div>
  </li>
</template>