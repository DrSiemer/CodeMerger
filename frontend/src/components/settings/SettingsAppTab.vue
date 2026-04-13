<script setup>
const props = defineProps({
  localConfig: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="space-y-4">
    <div v-info="'set_app_new_file'" class="flex flex-col space-y-4">
      <label class="flex items-center space-x-3 cursor-pointer">
        <input type="checkbox" v-model="localConfig.enable_new_file_check" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
        <span class="text-gray-200">Periodically check for new project files</span>
      </label>

      <div class="pl-7 flex items-center space-x-3" :class="{'opacity-50 pointer-events-none': !localConfig.enable_new_file_check}">
        <span class="text-gray-300 text-sm" v-info="'set_app_interval'">Check every:</span>
        <select v-model="localConfig.new_file_check_interval" v-info="'set_app_interval'" class="bg-cm-input-bg border border-gray-600 text-white rounded px-2 py-1 text-sm outline-none focus:border-cm-blue">
          <option value="2">2</option>
          <option value="5">5</option>
          <option value="10">10</option>
          <option value="30">30</option>
          <option value="60">60</option>
        </select>
        <span class="text-gray-300 text-sm" v-info="'set_app_interval'">seconds</span>
      </div>
    </div>

    <div v-info="'set_app_secrets'" class="pt-2">
      <label class="flex items-center space-x-3 cursor-pointer">
        <input type="checkbox" v-model="localConfig.scan_for_secrets" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
        <span class="text-gray-200">Scan for secrets (on each copy)</span>
      </label>
    </div>

    <div v-info="'set_app_feedback'" class="pt-2">
      <label class="flex items-center space-x-3 cursor-pointer">
        <input type="checkbox" v-model="localConfig.show_feedback_on_paste" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
        <span class="text-gray-200">Show LLM feedback window automatically on paste</span>
      </label>
    </div>

    <div v-info="'set_app_compact'" class="pt-2">
      <label class="flex items-center space-x-3 cursor-pointer">
        <input type="checkbox" v-model="localConfig.enable_compact_mode_on_minimize" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
        <span class="text-gray-200">Activate compact mode when main window is minimized</span>
      </label>
    </div>

    <div v-info="'set_app_updates'" class="pt-2">
      <label class="flex items-center space-x-3 cursor-pointer">
        <input type="checkbox" v-model="localConfig.check_for_updates" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
        <span class="text-gray-200">Automatically check for updates daily</span>
      </label>
      <!-- Manual Check Button inside the updates documentation scope -->
      <div class="pl-7 pt-2">
         <button
          id="btn-check-updates-now"
          @click="window.pywebview.api.check_for_updates_manual()"
          v-info="'set_app_check_now'"
          class="bg-gray-700 hover:bg-gray-600 text-white text-xs font-bold py-1.5 px-4 rounded transition-colors"
          title="Bypass daily timer and check GitHub now"
        >
          Check for Updates Now
        </button>
      </div>
    </div>
  </div>
</template>