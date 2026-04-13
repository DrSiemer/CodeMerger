<script setup>
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  localConfig: {
    type: Object,
    required: true
  }
})

const { selectDirectory } = useAppState()

const handleBrowse = async () => {
  const path = await selectDirectory()
  if (path) {
    props.localConfig.default_parent_folder = path
  }
}
</script>

<template>
  <div class="space-y-2" v-info="'set_starter_folder'">
    <label class="text-gray-200 font-medium">Default parent folder for new projects</label>
    <div class="flex space-x-3">
      <input
        type="text"
        v-model="localConfig.default_parent_folder"
        placeholder="C:\Projects"
        class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-2 outline-none focus:border-cm-blue"
      >
      <button
        @click="handleBrowse"
        class="bg-gray-700 hover:bg-gray-600 text-white font-bold px-4 py-2 rounded text-sm transition-colors shrink-0"
      >
        Browse
      </button>
    </div>
  </div>
</template>