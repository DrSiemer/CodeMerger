<script setup>
import { Network, FileCode, ChevronRight, ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  activeId: {
    type: Number,
    default: null
  },
  expandedNodes: {
    type: Object, // Set
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
})

defineEmits(['activate', 'toggle'])
</script>

<template>
  <div>
    <div
      @click="$emit('activate', node)"
      class="flex items-center py-2 px-3 rounded cursor-pointer transition-all group border"
      :class="activeId === node.id ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'"
      :style="{ marginLeft: (level * 16) + 'px' }"
    >
      <div @click.stop="$emit('toggle', node)" class="w-6 flex shrink-0 justify-center">
        <template v-if="node.children && node.children.length > 0">
          <ChevronDown v-if="expandedNodes.has(node.id)" class="w-4 h-4 text-gray-500" />
          <ChevronRight v-else class="w-4 h-4 text-gray-500" />
        </template>
      </div>

      <Network
        v-if="node.children && node.children.length > 0"
        class="w-4 h-4 mr-3 shrink-0"
        :class="activeId === node.id ? 'text-cm-blue' : 'text-gray-600'"
      />
      <FileCode
        v-else
        class="w-4 h-4 mr-3 shrink-0"
        :class="activeId === node.id ? 'text-cm-blue' : 'text-gray-700'"
      />

      <span class="truncate font-medium text-sm">{{ node.name }}</span>

      <span v-if="node.files && node.files.length > 0" class="ml-auto text-[10px] bg-black/40 px-1.5 py-0.5 rounded text-gray-600 font-bold tracking-tighter">
        {{ node.files.length }}
      </span>
    </div>

    <div v-if="expandedNodes.has(node.id) && node.children">
      <VisualizerTreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :active-id="activeId"
        :expanded-nodes="expandedNodes"
        :level="level + 1"
        @activate="$emit('activate', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </div>
  </div>
</template>