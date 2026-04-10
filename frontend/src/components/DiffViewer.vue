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
  filename: {
    type: String,
    default: 'file'
  },
  fontSize: {
    type: Number,
    default: 13
  },
  fullContext: {
    type: Boolean,
    default: false
  }
})

const diffLines = computed(() => {
  const oldStr = props.oldText || ''
  const newStr = props.newText || ''

  // --- FULL TEXT MODE (Used in Project Starter) ---
  // This mode shows every single line of the text without Git metadata headers.
  if (props.fullContext) {
    const changes = Diff.diffLines(oldStr, newStr)
    const rows = []

    changes.forEach(part => {
      // Split the value into lines while preserving empty lines
      const lines = part.value.split('\n')

      // If the part ends with a newline, the last element of split is an empty string
      // created by the trailing newline. We remove it to avoid double-spacing blocks.
      if (lines[lines.length - 1] === '') {
        lines.pop()
      }

      lines.forEach(line => {
        let type = 'context'
        let prefix = ' '

        if (part.added) {
          type = 'add'
          prefix = '+'
        } else if (part.removed) {
          type = 'remove'
          prefix = '-'
        }

        rows.push({
          prefix,
          text: line,
          type
        })
      })
    })

    return rows
  }

  // --- TRUNCATED DIFF MODE (Used in Dashboard / AI Response Review) ---
  // Standard patch logic with headers and hunk markers.
  const patch = Diff.structuredPatch(
    props.filename,
    props.filename,
    oldStr,
    newStr,
    '',
    '',
    { context: 3 }
  )

  if (!patch || patch.hunks.length === 0) {
    return []
  }

  const rows = []

  // Add traditional File Headers
  rows.push({ prefix: '---', text: props.filename, type: 'header' })
  rows.push({ prefix: '+++', text: props.filename, type: 'header' })

  // Process hunks
  patch.hunks.forEach(hunk => {
    // Add Hunk Header (@@ -start,len +start,len @@)
    rows.push({
      prefix: '@@',
      text: `-${hunk.oldStart},${hunk.oldLines} +${hunk.newStart},${hunk.newLines} @@`,
      type: 'header'
    })

    hunk.lines.forEach(line => {
      const char = line[0]
      const content = line.substring(1)
      let type = 'context'

      if (char === '+') type = 'add'
      else if (char === '-') type = 'remove'

      rows.push({
        prefix: char,
        text: content,
        type: type
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
          'bg-[#1e301e] text-[#a7f0a7]': line.type === 'add',
          'bg-[#3a1e1e] text-[#f0a7a7]': line.type === 'remove',
          'text-[#85b5d5] font-bold': line.type === 'header',
          'text-gray-400': line.type === 'context'
        }"
      >
        <!-- Line prefix (Gutter) -->
        <div class="w-10 shrink-0 text-center select-none opacity-50 border-r border-gray-800 mr-2 py-0.5">
          {{ line.prefix }}
        </div>
        <!-- Text content -->
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