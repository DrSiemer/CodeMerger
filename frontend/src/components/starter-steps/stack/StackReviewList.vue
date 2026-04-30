<script setup>
import { ref, computed, nextTick } from 'vue'
import {
  ChevronRight, Plus, Trash2, ChevronDown, ChevronUp, PencilLine,
  ChevronDownSquare, ChevronUpSquare
} from 'lucide-vue-next'

const props = defineProps({
  pData: Object,
  isLookingBack: Boolean
})

const emit = defineEmits(['next', 'reset', 'request-delete'])

const expandedIndices = ref(new Set())
const editingNameIndex = ref(null)
const nameInputRef = ref(null)

const toggleExpand = (idx) => {
  if (!props.pData.stack[idx].rationale) return
  if (expandedIndices.value.has(idx)) expandedIndices.value.delete(idx)
  else expandedIndices.value.add(idx)
}

const startEditingName = (idx) => {
  editingNameIndex.value = idx
  nextTick(() => {
    if (nameInputRef.value && nameInputRef.value[0]) {
      nameInputRef.value[0].focus()
      nameInputRef.value[0].select()
    }
  })
}

const stopEditingName = () => {
  editingNameIndex.value = null
}

const isAllExpanded = computed(() => {
  const expandable = props.pData.stack.filter(item => !!item.rationale)
  if (expandable.length === 0) return false
  return expandable.every(item => {
    const idx = props.pData.stack.indexOf(item)
    return expandedIndices.value.has(idx)
  })
})

const toggleAll = () => {
  if (isAllExpanded.value) {
    expandedIndices.value.clear()
  } else {
    props.pData.stack.forEach((item, idx) => {
      if (item.rationale) expandedIndices.value.add(idx)
    })
  }
}

const addManualSubject = () => {
  const newIdx = props.pData.stack.length
  props.pData.stack.push({
    tech: '',
    rationale: '',
    warning: '',
    isManual: true
  })
  startEditingName(newIdx)
}

defineExpose({ expandedIndices })
</script>

<template>
  <div class="flex flex-col h-full space-y-4">
    <div class="shrink-0 flex items-center justify-between">
      <div>
        <h3 class="text-2xl font-bold text-white">Selected Code Stack</h3>
        <p class="text-gray-400 mt-1">Review the chosen technologies. Click a subject to reveal its architectural rationale.</p>
      </div>
      <button @click="$emit('reset')" v-info="'starter_nav_reset'" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest">Start Over</button>
    </div>

    <div v-if="pData.stack.some(i => !!i.rationale)" class="flex justify-end items-center shrink-0">
      <button
        @click="toggleAll"
        class="text-[10px] font-bold text-gray-500 hover:text-white flex items-center space-x-2 transition-colors uppercase tracking-widest"
        :title="isAllExpanded ? 'Collapse all rationales' : 'Expand all rationales'"
      >
        <component :is="isAllExpanded ? ChevronUpSquare : ChevronDownSquare" class="w-3.5 h-3.5" />
        <span>{{ isAllExpanded ? 'Collapse All' : 'Expand All' }}</span>
      </button>
    </div>

    <div class="flex-grow overflow-y-auto custom-scrollbar space-y-2 pr-2" v-info="'starter_stack_edit'">
      <div v-for="(item, idx) in pData.stack" :key="idx" class="border border-gray-700 rounded-lg overflow-hidden transition-all duration-200">
        <div
          class="flex items-center justify-between p-4 cursor-pointer transition-colors group"
          :class="[
            expandedIndices.has(idx) ? 'bg-cm-blue/10' : 'bg-gray-800/40 hover:bg-gray-800/60',
            !item.rationale ? 'cursor-default' : 'cursor-pointer'
          ]"
          @click="toggleExpand(idx)"
          v-info="'starter_stack_item'"
        >
          <div class="flex items-center space-x-4 min-w-0 flex-grow">
             <component
               v-if="item.rationale"
               :is="expandedIndices.has(idx) ? ChevronUp : ChevronDown"
               class="w-5 h-5 text-gray-500 shrink-0"
             />
             <div v-else class="w-5 h-5 shrink-0"></div>

             <div class="flex-grow min-w-0 flex items-center">
                <input
                  v-if="editingNameIndex === idx"
                  ref="nameInputRef"
                  v-model="item.tech"
                  @click.stop
                  @blur="stopEditingName"
                  @keyup.enter="stopEditingName"
                  v-info="'starter_stack_edit_name'"
                  class="bg-black/30 border border-cm-blue text-white font-bold text-lg py-1 px-2 rounded w-full outline-none"
                  placeholder="Technology Name"
                >
                <div v-else class="flex items-center space-x-2 truncate">
                  <span class="text-white font-bold text-lg truncate">{{ item.tech || '(unnamed)' }}</span>
                  <button
                    @click.stop="startEditingName(idx)"
                    v-info="'starter_stack_edit_name'"
                    class="text-gray-500 hover:text-white p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Edit name"
                  >
                    <PencilLine class="w-4 h-4" />
                  </button>
                </div>
             </div>
          </div>

          <button @click.stop="$emit('request-delete', idx)" v-info="'starter_stack_delete'" class="ml-4 text-gray-600 hover:text-red-400 transition-colors p-2 shrink-0">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>

        <div v-if="expandedIndices.has(idx) && item.rationale" class="bg-black/20 p-6 border-t border-gray-700/50 animate-in slide-in-from-top-1 duration-200">
          <div class="space-y-3">
            <span class="block text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">Technical Rationale</span>
            <p v-info="'starter_stack_rationale'" class="text-gray-200 text-[15px] leading-relaxed whitespace-pre-wrap">{{ item.rationale }}</p>
          </div>
        </div>
      </div>

      <button @click="addManualSubject" v-info="'starter_stack_add'" class="w-full py-3 border border-dashed border-gray-700 rounded-lg text-gray-500 hover:text-gray-300 hover:border-gray-500 transition-all flex items-center justify-center space-x-2 bg-black/10">
        <Plus class="w-4 h-4" />
        <span class="font-bold text-sm">Add Subject</span>
      </button>
    </div>

    <div v-if="!isLookingBack" class="shrink-0 pt-6 flex justify-end">
      <button @click="$emit('next')" class="bg-cm-blue hover:bg-blue-500 text-white font-bold py-3 px-12 rounded shadow-lg transition-all flex items-center group">
        Next Step: System Design
        <ChevronRight class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
      </button>
    </div>
  </div>
</template>