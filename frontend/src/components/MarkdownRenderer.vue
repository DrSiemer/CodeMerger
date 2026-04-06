<script setup>
import { computed } from 'vue'
import markdownit from 'markdown-it'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  fontSize: {
    type: Number,
    default: 14
  }
})

const md = markdownit({
  html: false,
  linkify: true,
  typographer: true
})

const renderedHtml = computed(() => {
  if (!props.content) return ''
  return md.render(props.content)
})
</script>

<template>
  <div
    class="prose prose-invert max-w-none leading-relaxed text-gray-300 prose-headings:text-white prose-a:text-cm-blue prose-code:text-[#DEB887] prose-pre:bg-cm-input-bg prose-pre:border prose-pre:border-gray-700 selectable"
    :style="{ fontSize: fontSize + 'px' }"
    v-html="renderedHtml"
  >
  </div>
</template>

<style>
/* Allow selection inside the renderer */
.selectable {
  user-select: text !important;
}

/* Remove top margin from the first element in the prose container */
.prose > :first-child {
  margin-top: 0 !important;
}

/* Restoring bullet visibility and list formatting hidden by Tailwind reset */
.prose ul {
  list-style-type: disc !important;
  margin-left: 1.5em !important;
  margin-bottom: 1rem !important;
}

.prose ol {
  list-style-type: decimal !important;
  margin-left: 1.5em !important;
  margin-bottom: 1rem !important;
}

.prose li {
  display: list-item !important;
  margin-bottom: 0.25em !important;
}

.prose h1, .prose h2, .prose h3 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 700;
}
.prose h1 { font-size: 1.5em; border-bottom: 1px solid #374151; padding-bottom: 0.25em; }
.prose h2 { font-size: 1.25em; }
.prose h3 { font-size: 1.1em; }

.prose p { margin-bottom: 1em; }

.prose code {
  background-color: #374151;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.prose pre {
  padding: 1em;
  border-radius: 0.375em;
  overflow-x: auto;
  margin-bottom: 1.5em;
}

.prose pre code {
  background-color: transparent;
  padding: 0;
}
</style>