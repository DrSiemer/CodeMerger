<script setup>
import { computed } from 'vue'
import markdownit from 'markdown-it'

const props = defineProps({
  content: {
    type: String,
    default: ''
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
  <div class="prose prose-invert max-w-none prose-sm leading-relaxed text-gray-300 prose-headings:text-white prose-a:text-cm-blue prose-code:text-[#DEB887] prose-pre:bg-cm-input-bg prose-pre:border prose-pre:border-gray-700 selectable" v-html="renderedHtml">
  </div>
</template>

<style>
/* Allow selection inside the renderer */
.selectable {
  user-select: text !important;
}

/* Restoring bullet visibility and list formatting hidden by Tailwind reset */
.prose ul {
  list-style-type: disc !important;
  margin-left: 1.5rem !important;
  margin-bottom: 1rem !important;
}

.prose ol {
  list-style-type: decimal !important;
  margin-left: 1.5rem !important;
  margin-bottom: 1rem !important;
}

.prose li {
  display: list-item !important;
  margin-bottom: 0.25rem !important;
}

.prose h1, .prose h2, .prose h3 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 700;
}
.prose h1 { font-size: 1.5rem; border-bottom: 1px solid #374151; padding-bottom: 0.25rem; }
.prose h2 { font-size: 1.25rem; }
.prose h3 { font-size: 1.1rem; }

.prose p { margin-bottom: 1em; }

.prose code {
  background-color: #374151;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.prose pre {
  padding: 1rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  margin-bottom: 1.5em;
}

.prose pre code {
  background-color: transparent;
  padding: 0;
}
</style>