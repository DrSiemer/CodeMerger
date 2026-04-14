<script setup>
import { onMounted } from 'vue'
import { useAppState } from '../composables/useAppState'

const { newlyAddedFiletypes, clearNewlyAddedFiletypes, resizeWindow } = useAppState()

onMounted(async () => {
  await resizeWindow(500, 500)
})
</script>

<template>
  <div id="new-filetypes-modal" class="absolute inset-0 bg-black/70 flex items-center justify-center z-[110] p-6">
    <div class="bg-cm-dark-bg w-full max-w-[450px] rounded shadow-2xl border border-gray-600 flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-700 bg-cm-top-bar shrink-0">
        <h2 class="text-lg font-bold text-white uppercase tracking-wider">New Filetypes Added</h2>
      </div>

      <!-- Body -->
      <div class="p-6 flex flex-col min-h-0">
        <p class="text-gray-300 text-sm mb-4 leading-relaxed">
          The following new default filetypes have been added to your configuration and are now active for indexing:
        </p>

        <!-- Scrollable List -->
        <div class="flex-grow overflow-y-auto custom-scrollbar border border-gray-700 rounded bg-black/20 p-2 max-h-[300px]">
          <div
            v-for="ft in newlyAddedFiletypes"
            :key="ft.ext"
            class="flex items-center space-x-4 p-3 border-b border-gray-800/50 last:border-0"
          >
            <span class="font-mono text-cm-blue font-bold shrink-0 min-w-[70px]">{{ ft.ext }}</span>
            <span class="text-gray-400 text-xs leading-tight">{{ ft.description }}</span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-cm-top-bar flex justify-end shrink-0">
        <button
          id="btn-new-filetypes-ok"
          @click="clearNewlyAddedFiletypes"
          v-info="'ft_new_ok'"
          class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-2 px-10 rounded shadow-md transition-all text-sm"
          title="Dismiss notification"
        >
          OK
        </button>
      </div>

    </div>
  </div>
</template>