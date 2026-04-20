<script setup>
import { nodeHasMatch } from '../../utils/visualizerUtils'

const props = defineProps({
  navPath: Array,
  searchQuery: String
})

const emit = defineEmits(['nav-to', 'node-hover', 'dive-in'])

const getRectStyle = (layout) => {
  if (!layout) return {};
  return {
    left: `calc(${layout.x}% + 4px)`,
    top: `calc(${layout.y}% + 4px)`,
    width: `calc(${layout.w}% - 8px)`,
    height: `calc(${layout.h}% - 8px)`
  };
};
</script>

<template>
  <div class="flex-grow flex flex-col min-h-0">
    <!-- Breadcrumbs -->
    <div class="flex items-center space-x-1 text-sm px-6 py-3 bg-gray-800 border-b border-gray-700 shrink-0">
      <div v-for="(b, idx) in navPath" :key="b.id" class="flex items-center">
        <span v-if="idx > 0" class="mx-2 text-gray-500">/</span>
        <button
          @click="emit('nav-to', idx)"
          class="hover:text-white transition-colors"
          :class="idx === navPath.length - 1 ? 'text-white font-bold' : 'text-gray-400'"
        >
          {{ b.name }}
        </button>
      </div>
    </div>

    <!-- Tree Layout Area -->
    <div class="flex-grow flex min-h-0">
      <div class="flex-grow border-r border-gray-700 relative bg-[#1A1A1A] overflow-hidden p-2" v-info="'viz_explorer_tree'">
        <div v-if="navPath[navPath.length - 1]?.children?.length" class="absolute inset-0 m-2">
          <div
            v-for="child in navPath[navPath.length - 1].children"
            :key="child.id"
            class="absolute border border-gray-900 rounded-xl overflow-hidden cursor-pointer transition-all duration-300 hover:brightness-125 shadow-lg group"
            :class="{ 'opacity-20 grayscale': searchQuery && !nodeHasMatch(child, searchQuery) }"
            :style="getRectStyle(child.layout)"
            @click="emit('dive-in', child)"
            @mouseenter="emit('node-hover', child)"
            @mouseleave="emit('node-hover', null)"
          >
            <div class="absolute inset-0 opacity-25 group-hover:opacity-40 transition-opacity" :style="{ backgroundColor: child.color }"></div>

            <!-- Pre-render grand-children for depth effect -->
            <div v-if="child.children?.length" class="absolute inset-0 opacity-30">
              <div
                v-for="grandchild in child.children"
                :key="grandchild.id"
                class="absolute border border-gray-900 rounded-lg"
                :style="[getRectStyle(grandchild.layout), { backgroundColor: grandchild.color }]"
              ></div>
            </div>

            <!-- Content Overlay -->
            <div class="absolute inset-0 p-4 flex flex-col justify-start pointer-events-none">
              <div class="font-bold text-white text-xl drop-shadow-md truncate">{{ child.name }}</div>
              <div class="text-sm text-gray-300 drop-shadow-md font-medium">{{ child.weight }} items</div>
            </div>
          </div>
        </div>

        <!-- Dive-in leaf content slot -->
        <slot></slot>
      </div>

      <!-- Side panel slot -->
      <slot name="details"></slot>
    </div>
  </div>
</template>