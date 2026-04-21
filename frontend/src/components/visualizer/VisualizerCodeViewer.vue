<script setup>
defineProps({
  isCodeLoading: Boolean,
  highlightedLines: Array
})
</script>

<template>
  <div class="absolute inset-0 m-2 bg-[#1e1e1e] border border-gray-800 rounded-xl shadow-inner overflow-hidden flex flex-col">
    <div v-if="isCodeLoading" class="flex-grow flex items-center justify-center">
      <span class="text-gray-500 italic font-mono">Loading code...</span>
    </div>
    <div v-else class="flex-grow overflow-auto p-4 custom-scrollbar highlight">
      <table class="w-full border-collapse font-mono text-[12px] leading-relaxed selectable">
        <tbody>
          <tr v-for="(line, idx) in highlightedLines" :key="idx" class="group">
            <td class="w-10 pr-4 text-right text-gray-600 select-none border-r border-gray-800/50 group-hover:text-gray-400">{{ idx + 1 }}</td>
            <td class="pl-4 whitespace-pre" v-html="line || ' '"></td>
          </tr>
        </tbody>
      </table>
      <div v-if="highlightedLines.length === 0" class="p-6 text-gray-500 italic">File is empty or could not be read.</div>
    </div>
  </div>
</template>

<style scoped>
.selectable { user-select: text; }
</style>