<script setup>
import { useAppState } from '../../composables/useAppState'

const props = defineProps({
  localConfig: {
    type: Object,
    required: true
  }
})

const { selectEditorExecutable } = useAppState()

const handleBrowseEditor = async () => {
  const path = await selectEditorExecutable()
  if (path) {
    props.localConfig.default_editor = path
  }
}
</script>

<template>
  <div class="space-y-2" v-info="'set_editor_path'">
    <label class="text-gray-200 font-medium">Default Editor Executable</label>
    <div class="flex space-x-3">
      <input
        type="text"
        v-model="localConfig.default_editor"
        placeholder="Leave blank to use system defaults"
        class="flex-grow bg-cm-input-bg border border-gray-600 text-white rounded px-3 py-2 outline-none focus:border-cm-blue"
      >
      <button
        @click="handleBrowseEditor"
        class="bg-gray-700 hover:bg-gray-600 text-white font-bold px-4 py-2 rounded text-sm transition-colors shrink-0"
      >
        Browse
      </button>
      <button
        v-if="localConfig.default_editor"
        @click="localConfig.default_editor = ''"
        class="bg-gray-800 hover:bg-red-900/40 text-gray-500 hover:text-red-400 font-bold px-4 py-2 rounded text-sm transition-colors shrink-0"
      >
        Clear
      </button>
    </div>
    <p class="text-sm text-gray-500 mt-1">Provide the full path to your code editor (e.g., sublime_text.exe).</p>
  </div>
</template>