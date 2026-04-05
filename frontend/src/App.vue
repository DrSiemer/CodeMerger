<script setup>
import { ref } from 'vue'

const apiResponse = ref('')
const selectedDir = ref('')

const testApi = async () => {
  if (window.pywebview && window.pywebview.api) {
    try {
      apiResponse.value = await window.pywebview.api.test()
    } catch (e) {
      apiResponse.value = `Error: ${e}`
    }
  } else {
    apiResponse.value = "PyWebView API not injected yet."
  }
}

const selectDirectory = async () => {
  if (window.pywebview && window.pywebview.api) {
    const result = await window.pywebview.api.select_directory()
    if (result) {
      selectedDir.value = result
    } else {
      selectedDir.value = "(Selection cancelled)"
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-cm-dark-bg text-gray-100 flex flex-col items-center justify-center p-8">
    <div class="max-w-2xl w-full bg-cm-input-bg p-8 rounded-xl shadow-lg border border-gray-600">
      <h1 class="text-3xl font-bold mb-2 text-white">CodeMerger</h1>
      <p class="text-gray-400 mb-8">Vue 3 + PyWebView UI Rewrite - Phase 1 Validation</p>

      <div class="space-y-6">
        <!-- API Test -->
        <div class="p-5 bg-cm-top-bar rounded-lg border border-gray-600">
          <h2 class="text-xl font-semibold mb-3 flex items-center">
            <svg class="w-5 h-5 mr-2 text-cm-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            API Bridge Test
          </h2>
          <button
            @click="testApi"
            class="bg-cm-blue hover:bg-blue-600 text-white font-medium py-2 px-4 rounded transition-colors w-full sm:w-auto"
          >
            Test Python API
          </button>
          <div class="mt-4 p-3 bg-black/30 rounded text-sm font-mono text-green-400 min-h-[44px] flex items-center">
            {{ apiResponse || 'Awaiting response...' }}
          </div>
        </div>

        <!-- Dialog Test -->
        <div class="p-5 bg-cm-top-bar rounded-lg border border-gray-600">
          <h2 class="text-xl font-semibold mb-3 flex items-center">
            <svg class="w-5 h-5 mr-2 text-cm-green" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
            Native Dialog Test
          </h2>
          <button
            @click="selectDirectory"
            class="bg-cm-green hover:bg-green-600 text-white font-medium py-2 px-4 rounded transition-colors w-full sm:w-auto"
          >
            Select Directory
          </button>
          <div class="mt-4 p-3 bg-black/30 rounded text-sm font-mono text-green-400 min-h-[44px] flex items-center overflow-x-auto break-all">
            {{ selectedDir || 'Awaiting selection...' }}
          </div>
        </div>
      </div>

      <div class="mt-8 text-center text-sm text-gray-500">
        Run <code class="bg-black/50 px-1 py-0.5 rounded text-gray-400">python run_webview.py --dev</code> to view this window.
      </div>
    </div>
  </div>
</template>