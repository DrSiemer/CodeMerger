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

defineEmits(['dblclick'])

const md = markdownit({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

const renderedHtml = computed(() => {
  if (!props.content) return ''

  // Pre-process task lists before rendering markdown
  // Matches "- [ ] " or "- [x] " at the start of lines, preserving indentation
  const processed = props.content
    .replace(/^(\s*)-\s+\[ \]\s+/gm, '$1- <span class="cm-todo-unfilled">☐</span> ')
    .replace(/^(\s*)-\s+\[x\]\s+/gim, '$1- <span class="cm-todo-filled">☑</span> ')

  return md.render(processed)
})
</script>

<template>
  <div
    class="prose prose-invert max-w-none leading-relaxed text-gray-300 prose-headings:text-white prose-a:text-cm-blue prose-code:text-[#DEB887] prose-pre:bg-cm-input-bg prose-pre:border prose-pre:border-gray-700 selectable"
    :style="{ fontSize: fontSize + 'px' }"
    v-html="renderedHtml"
    @dblclick="$emit('dblclick', $event)"
  >
  </div>
</template>

<style>
.selectable {
  user-select: text;
}

.cm-todo-unfilled {
  color: #6B7280;
  font-family: "Segoe UI Symbol", "Apple Color Emoji", "Segoe UI Emoji", sans-serif;
  font-weight: bold;
  margin-right: 4px;
  font-size: 1.1em;
  vertical-align: -1px;
}

.cm-todo-filled {
  color: #0078D4;
  font-family: "Segoe UI Symbol", "Apple Color Emoji", "Segoe UI Emoji", sans-serif;
  font-weight: bold;
  margin-right: 4px;
  font-size: 1.1em;
  vertical-align: -1px;
}

.prose > :first-child {
  margin-top: 0;
}

/* Restoring bullet visibility and list formatting hidden by Tailwind reset */
.prose ul {
  list-style-type: disc;
  margin-left: 1.5em;
  margin-bottom: 1rem;
}

.prose ol {
  list-style-type: decimal;
  margin-left: 1.5em;
  margin-bottom: 1rem;
}

.prose li {
  display: list-item;
  margin-bottom: 0.25em;
}

/* Ensure our custom checkboxes don't double up with bullets */
.prose li:has(> .cm-todo-unfilled),
.prose li:has(> .cm-todo-filled) {
  list-style-type: none;
  margin-left: -0.2em;
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