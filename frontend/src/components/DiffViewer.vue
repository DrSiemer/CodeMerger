<script setup>
import { computed } from 'vue'
import * as Diff from 'diff'

const props = defineProps({
  oldText: {
    type: String,
    default: ''
  },
  newText: {
    type: String,
    default: ''
  },
  fontSize: {
    type: Number,
    default: 13
  }
})

const diffLines = computed(() => {
  // Use jsdiff to compute line-level changes
  const changes = Diff.diffLines(props.oldText || '', props.newText || '')

  // Format into rows with metadata for rendering
  const rows = []
  changes.forEach(part => {
    const lines = part.value.split('\n')
    // Remove the trailing empty string from split if it exists
    if (lines[lines.length - 1] === '') lines.pop()

    lines.forEach(line => {
      rows.push({
        text: line,
        added: part.added,
        removed: part.removed
      })
    })
  })

  return rows
})
</script>

<template>
  <div
    class="bg-[#1A1A1A] border border-gray-700 rounded overflow-hidden font-mono leading-relaxed selectable h-fit"
    :style="{ fontSize: fontSize + 'px' }"
  >
    <div v-if="diffLines.length === 0" class="p-4 text-gray-500 italic">
      No changes detected in file content.
    </div>

    <div v-else class="flex flex-col min-w-0">
      <div
        v-for="(line, idx) in diffLines"
        :key="idx"
        class="flex min-w-0 border-b border-gray-800/30 last:border-0"
        :class="{
          'bg-[#1e301e] text-[#a7f0a7]': line.added,
          'bg-[#3a1e1e] text-[#f0a7a7]': line.removed,
          'text-gray-400': !line.added && !line.removed
        }"
      >
        <!-- Line prefix - Fixed width, no wrap -->
        <div class="w-8 shrink-0 text-center select-none opacity-50 border-r border-gray-800 mr-2 py-0.5">
          {{ line.added ? '+' : (line.removed ? '-' : ' ') }}
        </div>
        <!-- Text content - Allow wrapping -->
        <div class="whitespace-pre-wrap break-words px-2 py-0.5 flex-grow min-w-0">
          {{ line.text || ' ' }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.selectable {
  user-select: text !important;
}
</style>