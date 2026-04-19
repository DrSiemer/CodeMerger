<script setup>
import { useSystem } from '../../composables/useSystem'

const props = defineProps({
  localConfig: Object
})

const { checkForUpdatesManual } = useSystem()
</script>

<template>
  <div id="settings-app-tab" class="space-y-8">

    <!-- File Monitoring Section -->
    <section class="space-y-4">
      <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest flex items-center">
        File System Monitoring
      </h3>
      <div class="grid grid-cols-1 gap-4 bg-black/20 p-4 rounded border border-gray-800">
        <label class="flex items-center space-x-3 cursor-pointer" v-info="'set_app_new_file'">
          <input type="checkbox" v-model="localConfig.enable_new_file_check" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
          <span class="text-gray-200">Periodically check for new project files</span>
        </label>

        <div class="flex items-center space-x-4 pl-7" :class="{'opacity-50 pointer-events-none': !localConfig.enable_new_file_check}">
          <span class="text-sm text-gray-400" v-info="'set_app_interval'">Check interval (seconds):</span>
          <select
            v-model="localConfig.new_file_check_interval"
            class="bg-cm-input-bg text-white text-sm rounded border border-gray-600 px-2 py-1 outline-none focus:border-cm-blue"
          >
            <option :value="2">2</option>
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="30">30</option>
            <option :value="60">60</option>
          </select>
        </div>
      </div>
    </section>

    <!-- Security & Automation Section -->
    <section class="space-y-4">
      <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest">Security & Automation</h3>
      <div class="grid grid-cols-1 gap-4 bg-black/20 p-4 rounded border border-gray-800">
        <label class="flex items-center space-x-3 cursor-pointer" v-info="'set_app_secrets'">
          <input type="checkbox" v-model="localConfig.scan_for_secrets" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
          <span class="text-gray-200">Scan for secrets (API keys, etc) before copying code</span>
        </label>

        <label class="flex items-center space-x-3 cursor-pointer" v-info="'set_app_feedback'">
          <input type="checkbox" v-model="localConfig.show_feedback_on_paste" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
          <span class="text-gray-200">Show Response Review window automatically on paste</span>
        </label>

        <label class="flex items-center space-x-3 cursor-pointer" v-info="'set_app_compact'">
          <input type="checkbox" v-model="localConfig.enable_compact_mode_on_minimize" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
          <span class="text-gray-200">Always activate Compact Mode when main window is minimized</span>
        </label>

        <label class="flex items-center space-x-3 cursor-pointer">
          <input type="checkbox" v-model="localConfig.enable_ultra_compact_mode" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
          <span class="text-gray-200">Enable Ultra Compact Mode (Minimalist single row)</span>
        </label>
      </div>
    </section>

    <!-- Updates Section -->
    <section class="space-y-4">
      <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest">Application Updates</h3>
      <div class="bg-black/20 p-4 rounded border border-gray-800 flex items-center justify-between">
        <label class="flex items-center space-x-3 cursor-pointer" v-info="'set_app_updates'">
          <input type="checkbox" v-model="localConfig.check_for_updates" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
          <span class="text-gray-200">Enable automatic daily update checks</span>
        </label>

        <button
          @click="checkForUpdatesManual"
          v-info="'set_app_check_now'"
          class="bg-gray-700 hover:bg-gray-600 text-white text-xs font-bold py-1.5 px-4 rounded transition-colors shadow-sm"
        >
          Check Now
        </button>
      </div>
    </section>

  </div>
</template>