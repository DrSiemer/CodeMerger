<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { CheckCheck, LockKeyhole, LockKeyholeOpen } from 'lucide-vue-next'

const props = defineProps({
  orderedKeys: Array,
  friendlyNames: Object,
  signoffs: Object,
  baselines: Object,
  activeSegmentKey: String,
  segments: Object
})

const emit = defineEmits(['select', 'reset', 'toggle-signoff', 'accept-all'])

const acceptAllConfirm = ref(false)
let acceptAllTimer = null

const hasPendingDiffs = computed(() => {
  return Object.keys(props.baselines).some(k => k !== '__merged__' && props.baselines[k] !== undefined)
})

const handleAcceptAllClick = () => {
  if (acceptAllConfirm.value) {
    emit('accept-all')
    acceptAllConfirm.value = false
    if (acceptAllTimer) clearTimeout(acceptAllTimer)
  } else {
    acceptAllConfirm.value = true
    acceptAllTimer = setTimeout(() => { acceptAllConfirm.value = false }, 2500)
  }
}

const toggleSignoff = (key) => {
  const content = props.segments[key] || ''
  if (!props.signoffs[key] && /<ALTERNATIVES>[\s\S]*?<\/ALTERNATIVES>/gi.test(content)) {
    alert("You must resolve all architectural alternatives (Pivot or Discard) in this segment before locking it.")
    return
  }
  emit('toggle-signoff', key)
}

onUnmounted(() => { if (acceptAllTimer) clearTimeout(acceptAllTimer) })
</script>

<template>
  <div class="w-72 shrink-0 border-r border-gray-700 pr-4 overflow-y-auto space-y-2" v-info="'starter_seg_nav'">
    <div class="p-2 mb-4 border-b border-gray-700 flex flex-col items-center space-y-3 pb-3">
      <button @click="$emit('reset')" v-info="'starter_nav_reset'" class="text-gray-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest">Start Over</button>
      <button
        v-if="hasPendingDiffs"
        @click="handleAcceptAllClick"
        class="transition-colors text-[10px] font-bold uppercase tracking-widest flex items-center px-3 py-1.5 rounded border select-none w-full justify-center"
        :class="acceptAllConfirm ? 'bg-cm-green text-white border-cm-green' : 'text-cm-green hover:text-green-400 bg-cm-green/10 border-cm-green/30 hover:bg-cm-green/20'"
      >
        <CheckCheck class="w-3.5 h-3.5 mr-1.5 shrink-0" />
        <span class="truncate">{{ acceptAllConfirm ? 'Click to confirm' : 'Accept All Diffs' }}</span>
      </button>
    </div>

    <div v-for="key in orderedKeys" :key="key"
         @click="$emit('select', key)"
         class="p-3 rounded cursor-pointer border transition-all flex items-center justify-between group"
         :class="activeSegmentKey === key ? 'bg-cm-blue/20 border-cm-blue text-white' : 'border-transparent text-gray-400 hover:bg-gray-800'">
      <div class="flex items-center space-x-2 truncate">
        <div v-if="baselines[key]" class="w-1.5 h-1.5 rounded-full bg-cm-green shrink-0"></div>
        <span class="truncate pr-2">{{ friendlyNames[key] || key }}</span>
      </div>
      <button @click.stop="toggleSignoff(key)" v-info="'starter_seg_indicator'" class="shrink-0 opacity-70 hover:opacity-100 transition-opacity" :title="signoffs[key] ? 'Unlock' : 'Lock'">
        <LockKeyhole v-if="signoffs[key]" class="w-4 h-4 text-cm-green" :stroke-width="2.5" />
        <LockKeyholeOpen v-else class="w-4 h-4 text-gray-500" :stroke-width="2.5" />
      </button>
    </div>
  </div>
</template>