<script setup>
import { Milestone, ArrowDownUp } from 'lucide-vue-next'

defineProps({
  fileCount: Number,
  totalTokens: Number,
  tokenColorClass: String,
  showFullPaths: Boolean,
  isOrderPulseActive: Boolean
})

defineEmits(['update:showFullPaths', 'order-click'])
</script>

<template>
  <div class="flex items-center justify-between mb-4">
    <div class="flex items-center space-x-3 min-w-0">
      <h3 class="font-semibold text-gray-200 shrink-0">Merge Order</h3>
      <span id="fm-total-tokens" :class="tokenColorClass" class="text-sm font-mono pt-0.5 truncate" v-info="'fm_tokens'">
        ({{ fileCount }} files, {{ totalTokens.toLocaleString() }} tokens)
      </span>
    </div>
    <div class="flex items-center space-x-2">
      <button
        id="btn-fm-order-request"
        @click="$emit('order-click', $event)"
        class="p-1.5 rounded border border-gray-600 enabled:hover:border-cm-blue text-gray-500 enabled:hover:text-cm-blue transition-colors relative"
        :class="{ 'click-pulse': isOrderPulseActive }"
        :style="isOrderPulseActive ? { '--click-color': '#DE680888' } : {}"
        title="Single-click: Copy request prompt | Ctrl+Click: Paste new order"
        v-info="'fm_order'"
      >
        <ArrowDownUp class="w-4 h-4" />
      </button>
      <button
        id="btn-fm-toggle-paths"
        @click="$emit('update:showFullPaths', !showFullPaths)"
        class="p-1.5 rounded border transition-colors"
        :class="showFullPaths ? 'bg-cm-blue/20 border-cm-blue text-cm-blue' : 'bg-gray-800 border-gray-600 text-gray-500'"
        title="Toggle Path Visibility"
        v-info="'fm_list_tools'"
      >
        <Milestone class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>