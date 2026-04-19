<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  oldText: { type: String, default: '' },
  newText: { type: String, default: '' },
  filename: { type: String, default: 'file' },
  fontSize: { type: Number, default: 13 },
  fullContext: { type: Boolean, default: false }
})

const diffLines = ref([])
const isLoading = ref(true)

// Fetch the highlighted diff from the Python backend
const loadDiff = async () => {
  isLoading.value = true
  if (window.pywebview) {
    diffLines.value = await window.pywebview.api.get_syntax_diff(
      props.oldText,
      props.newText,
      props.filename,
      props.fullContext
    )
  }
  isLoading.value = false
}

onMounted(() => {
  loadDiff()

  // Inject Pygments CSS globally if it hasn't been injected yet
  if (window.pywebview && !document.getElementById('pygments-css')) {
    window.pywebview.api.get_pygments_style().then(css => {
      const style = document.createElement('style')
      style.id = 'pygments-css'
      style.innerHTML = css // Inject raw CSS
      document.head.appendChild(style)
    })
  }
})

// Recalculate if the text changes (e.g., Undo/Redo)
watch([() => props.oldText, () => props.newText], loadDiff)
</script>

<template>
  <div
    class="bg-[#1A1A1A] border border-gray-700 rounded overflow-hidden font-mono leading-relaxed selectable h-fit highlight"
    :style="{ fontSize: fontSize + 'px' }"
  >
    <div v-if="isLoading" class="p-4 text-gray-500 italic">
      Generating diff...
    </div>

    <div v-else-if="diffLines.length === 0" class="p-4 text-gray-500 italic">
      No changes detected in file content.
    </div>

    <div v-else class="flex flex-col min-w-0">
      <div
        v-for="(line, idx) in diffLines"
        :key="idx"
        class="flex min-w-0 border-b border-gray-800/30 last:border-0"
        :class="{
          'bg-[#1e301e]': line.type === 'add',       /* Dark Green Background */
          'bg-[#3a1e1e]': line.type === 'remove',    /* Dark Red Background */
        }"
      >
        <!-- The +/- Prefix -->
        <div
          class="w-10 shrink-0 text-center select-none border-r border-gray-800 mr-2 py-0.5"
          :class="{
            'text-[#a7f0a7]': line.type === 'add',
            'text-[#f0a7a7]': line.type === 'remove',
            'text-gray-600': line.type === 'context',
            'text-[#85b5d5] font-bold': line.type === 'header'
          }"
        >
          {{ line.prefix }}
        </div>

        <!-- The Rendered HTML from Pygments -->
        <div
          class="whitespace-pre-wrap break-words px-2 py-0.5 flex-grow min-w-0"
          :class="{
            'opacity-50': line.type === 'context',
            'text-[#85b5d5] font-bold': line.type === 'header'
          }"
          v-html="line.html || ' '"
        ></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.selectable {
  user-select: text;
}
</style>