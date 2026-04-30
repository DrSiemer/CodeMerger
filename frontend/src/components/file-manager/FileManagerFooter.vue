<script setup>
import { Search, Save, X } from 'lucide-vue-next'

defineProps({
  filterText: { type: String, default: '' },
  hasUnsavedChanges: { type: Boolean, default: false }
})

defineEmits(['update:filterText', 'save', 'cancel'])
</script>

<template>
  <div
    id="fm-footer"
    class="px-6 py-3 border-t border-gray-700 bg-cm-top-bar flex items-center justify-between shrink-0"
    :class="{'has-changes': hasUnsavedChanges}"
  >
    <div class="footer-col-side flex justify-start"></div>

    <div class="footer-search-col mx-4">
      <div class="relative w-full">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          id="fm-filter-input"
          :value="filterText"
          @input="$emit('update:filterText', $event.target.value)"
          type="text"
          placeholder="Filter both lists..."
          class="w-full bg-cm-input-bg text-white pl-10 pr-10 py-1.5 rounded border border-gray-600 focus:border-cm-blue outline-none text-sm transition-all"
        >
        <button
          v-if="filterText"
          @click="$emit('update:filterText', '')"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
          title="Clear filter"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <div class="footer-col-side flex justify-end items-center space-x-3">
      <button
        @click="$emit('cancel')"
        class="bg-gray-600 hover:bg-gray-500 text-white font-medium py-1.5 px-6 rounded transition-colors text-sm shrink-0"
      >
        {{ hasUnsavedChanges ? 'Cancel' : 'Close' }}
      </button>
      <button
        id="btn-fm-save"
        v-if="hasUnsavedChanges"
        @click="$emit('save')"
        class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-1.5 px-10 rounded shadow-md transition-all flex items-center text-sm shrink-0"
      >
        <Save class="w-4 h-4 mr-2" />
        Save Merge List
      </button>
    </div>
  </div>
</template>

<style scoped>
.footer-col-side, .footer-search-col {
  transition: all 0.4s ease-in-out 0.1s;
}
.has-changes .footer-col-side,
.has-changes .footer-search-col {
  transition: all 0.4s ease-in-out;
}
.footer-col-side {
  flex: 1 1 0px;
  min-width: 90px;
}
.footer-search-col {
  flex: 1 1 auto;
  max-width: 448px;
  min-width: 180px;
  display: flex;
  justify-content: center;
}
.has-changes .footer-col-side:last-child {
  min-width: 240px;
  flex: 0 0 auto;
}
.has-changes .footer-search-col {
  flex-grow: 0;
  flex-basis: 320px;
  max-width: 320px;
}
</style>