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
    <div class="space-y-2" v-info="'set_prompt_merged'">
      <label class="text-gray-200 font-medium">"Copy Code Only" Prompt</label>
      <textarea
        v-model="localConfig.copy_merged_prompt"
        rows="3"
        class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 text-sm outline-none focus:border-cm-blue custom-scrollbar"
      ></textarea>
    </div>

    <div class="space-y-2" v-info="'set_prompt_intro'">
      <label class="text-gray-200 font-medium">Default Intro Instructions</label>
      <textarea
        v-model="localConfig.default_intro_prompt"
        rows="4"
        class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 text-sm outline-none focus:border-cm-blue custom-scrollbar"
      ></textarea>
    </div>

    <div class="space-y-2" v-info="'set_prompt_outro'">
      <label class="text-gray-200 font-medium">Default Outro Instructions</label>
      <textarea
        v-model="localConfig.default_outro_prompt"
        rows="4"
        class="w-full bg-cm-input-bg border border-gray-600 text-white rounded p-3 text-sm outline-none focus:border-cm-blue custom-scrollbar"
      ></textarea>
    </div>
  </div>
</template>