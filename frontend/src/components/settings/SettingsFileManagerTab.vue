<script setup>
const props = defineProps({
  localConfig: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="space-y-6">
    <div v-info="'set_fm_tokens'">
      <label class="flex items-center space-x-3 cursor-pointer">
        <input type="checkbox" v-model="localConfig.token_count_enabled" class="w-4 h-4 bg-cm-input-bg border-gray-600 rounded text-cm-blue focus:ring-cm-blue">
        <span class="text-gray-200">Enable token counting</span>
      </label>
    </div>

    <div class="flex items-center space-x-3" v-info="'set_fm_limit'">
      <span class="text-gray-200 w-64">Max token limit (empty for none):</span>
      <input type="number" v-model="localConfig.token_limit" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
    </div>

    <div class="flex items-center space-x-3">
      <span class="text-gray-200 w-64">Token color warning threshold:</span>
      <input type="number" v-model="localConfig.token_color_threshold" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
      <span class="text-gray-400 text-sm">tokens</span>
    </div>

    <div class="flex items-center space-x-3" v-info="'set_fm_threshold'">
      <span class="text-gray-200 w-64">Warn when 'Add all' exceeds:</span>
      <input type="number" v-model="localConfig.add_all_warning_threshold" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
      <span class="text-gray-400 text-sm">files</span>
    </div>

    <div class="flex items-center space-x-3" v-info="'set_fm_alert_threshold'">
      <span class="text-gray-200 w-64">New file alert threshold:</span>
      <input type="number" v-model="localConfig.new_file_alert_threshold" class="bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-1.5 w-24 outline-none focus:border-cm-blue">
      <span class="text-gray-400 text-sm">files</span>
    </div>
  </div>
</template>