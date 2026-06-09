<template>
  <section class="process-result-editor">
    <div class="result-editor-header">
      <div>
        <strong>{{ t('nested.processResult') }}</strong>
        <span>{{ t('nested.processResultHint') }}</span>
      </div>
      <div v-if="!readonly" class="result-editor-toolbar">
        <button type="button" :title="t('nested.bold')" @click="executeCommand('bold')">
          <strong>B</strong>
        </button>
        <button type="button" :title="t('nested.italic')" @click="executeCommand('italic')">
          <em>I</em>
        </button>
        <button
          type="button"
          :title="t('nested.bulletList')"
          @click="executeCommand('insertUnorderedList')"
        >
          • List
        </button>
        <button
          type="button"
          :title="t('nested.numberedList')"
          @click="executeCommand('insertOrderedList')"
        >
          1. List
        </button>
        <button type="button" :title="t('nested.insertTable')" @click="insertEmptyTable">
          {{ t('nested.insertTable') }}
        </button>
      </div>
    </div>
    <div
      ref="editor"
      class="process-result-content"
      :class="{ readonly }"
      :contenteditable="!readonly"
      :data-placeholder="t('nested.processResultPlaceholder')"
      role="textbox"
      aria-multiline="true"
      @focus="saveSelection"
      @input="emitValue"
      @keyup="saveSelection"
      @mouseup="saveSelection"
      @paste="handlePaste"
    ></div>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  modelValue: { type: String, default: '' },
  readonly: Boolean,
})

const emit = defineEmits(['update:modelValue'])
const { t } = useI18n()
const editor = ref(null)
let savedRange = null
let resizeState = null

const MIN_COLUMN_WIDTH = 64

const escapeHtml = (value) =>
  value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')

const syncEditor = () => {
  if (!editor.value || editor.value === document.activeElement) return
  const value = props.modelValue || ''
  if (serializeEditor() !== value) {
    editor.value.innerHTML = value
  }
  decorateTables()
}

const saveSelection = () => {
  const selection = window.getSelection()
  if (!editor.value || !selection?.rangeCount) return
  const range = selection.getRangeAt(0)
  if (editor.value.contains(range.commonAncestorContainer)) {
    savedRange = range.cloneRange()
  }
}

const restoreSelection = () => {
  editor.value?.focus()
  const selection = window.getSelection()
  if (!selection || !editor.value) return
  selection.removeAllRanges()
  if (savedRange) {
    selection.addRange(savedRange)
    return
  }
  const range = document.createRange()
  range.selectNodeContents(editor.value)
  range.collapse(false)
  selection.addRange(range)
}

const emitValue = () => {
  if (!editor.value) return
  const hasText = Boolean(editor.value.textContent?.trim())
  const hasTable = Boolean(editor.value.querySelector('table'))
  emit('update:modelValue', hasText || hasTable ? serializeEditor() : '')
  saveSelection()
}

const serializeEditor = () => {
  if (!editor.value) return ''
  const clone = editor.value.cloneNode(true)
  clone.querySelectorAll('[data-column-resizer]').forEach((handle) => handle.remove())
  return clone.innerHTML.trim()
}

const ensureColumnGroup = (table, columnCount) => {
  let columnGroup = [...table.children].find((child) => child.tagName === 'COLGROUP')
  if (!columnGroup) {
    columnGroup = document.createElement('colgroup')
    table.insertBefore(columnGroup, table.firstChild)
  }

  const currentColumns = [...columnGroup.children].filter((child) => child.tagName === 'COL')
  while (currentColumns.length < columnCount) {
    const column = document.createElement('col')
    columnGroup.appendChild(column)
    currentColumns.push(column)
  }
  currentColumns.slice(columnCount).forEach((column) => column.remove())

  const firstRowCells = [...(table.rows[0]?.cells || [])]
  currentColumns.forEach((column, index) => {
    if (!column.getAttribute('width')) {
      const measuredWidth = firstRowCells[index]?.getBoundingClientRect().width
      const fallbackWidth = table.getBoundingClientRect().width / columnCount
      column.setAttribute(
        'width',
        String(Math.max(Math.round(measuredWidth || fallbackWidth || 160), MIN_COLUMN_WIDTH)),
      )
    }
  })
  return currentColumns
}

const stopColumnResize = () => {
  if (!resizeState) return
  window.removeEventListener('pointermove', resizeColumn)
  window.removeEventListener('pointerup', stopColumnResize)
  window.removeEventListener('pointercancel', stopColumnResize)
  document.body.classList.remove('resizing-result-column')
  resizeState = null
  emitValue()
}

const resizeColumn = (event) => {
  if (!resizeState) return
  const delta = event.clientX - resizeState.startX
  const currentWidth = Math.max(resizeState.currentWidth + delta, MIN_COLUMN_WIDTH)
  const nextWidth = Math.max(
    resizeState.currentWidth + resizeState.nextWidth - currentWidth,
    MIN_COLUMN_WIDTH,
  )
  const constrainedCurrentWidth = resizeState.currentWidth + resizeState.nextWidth - nextWidth
  resizeState.currentColumn.setAttribute('width', String(Math.round(constrainedCurrentWidth)))
  resizeState.nextColumn.setAttribute('width', String(Math.round(nextWidth)))
}

const startColumnResize = (event, table, columnIndex) => {
  if (props.readonly) return
  event.preventDefault()
  event.stopPropagation()

  const firstRowCells = [...(table.rows[0]?.cells || [])]
  if (columnIndex >= firstRowCells.length - 1) return
  const columns = ensureColumnGroup(table, firstRowCells.length)
  resizeState = {
    startX: event.clientX,
    currentColumn: columns[columnIndex],
    nextColumn: columns[columnIndex + 1],
    currentWidth: firstRowCells[columnIndex].getBoundingClientRect().width,
    nextWidth: firstRowCells[columnIndex + 1].getBoundingClientRect().width,
  }
  document.body.classList.add('resizing-result-column')
  window.addEventListener('pointermove', resizeColumn)
  window.addEventListener('pointerup', stopColumnResize)
  window.addEventListener('pointercancel', stopColumnResize)
}

const decorateTables = () => {
  if (!editor.value || props.readonly) return
  editor.value.querySelectorAll('[data-column-resizer]').forEach((handle) => handle.remove())
  editor.value.querySelectorAll('table').forEach((table) => {
    const firstRowCells = [...(table.rows[0]?.cells || [])]
    firstRowCells.slice(0, -1).forEach((cell, columnIndex) => {
      const handle = document.createElement('span')
      handle.dataset.columnResizer = 'true'
      handle.className = 'result-column-resizer'
      handle.contentEditable = 'false'
      handle.title = t('nested.resizeColumn')
      handle.addEventListener('pointerdown', (event) =>
        startColumnResize(event, table, columnIndex),
      )
      cell.appendChild(handle)
    })
  })
}

const insertHtml = (html) => {
  restoreSelection()
  document.execCommand('insertHTML', false, html)
  decorateTables()
  emitValue()
}

const executeCommand = (command) => {
  restoreSelection()
  document.execCommand(command, false)
  emitValue()
}

const buildTable = (rows) => {
  const normalizedRows = rows.filter((row) => row.some((cell) => cell.length > 0))
  if (!normalizedRows.length) return ''
  const columnCount = Math.max(...normalizedRows.map((row) => row.length))
  const columns = Array.from({ length: columnCount }, () => '<col width="160">').join('')
  const normalized = normalizedRows.map((row) => [
    ...row,
    ...Array(Math.max(columnCount - row.length, 0)).fill(''),
  ])
  const header = normalized[0].map((cell) => `<th>${escapeHtml(cell) || '<br>'}</th>`).join('')
  const body = normalized
    .slice(1)
    .map(
      (row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell) || '<br>'}</td>`).join('')}</tr>`,
    )
    .join('')
  return `<table><colgroup>${columns}</colgroup><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table><p><br></p>`
}

const insertEmptyTable = () => {
  const rows = [
    [1, 2, 3].map((index) => t('nested.resultColumn', { index })),
    ['', '', ''],
    ['', '', ''],
  ]
  insertHtml(buildTable(rows))
}

const handlePaste = (event) => {
  if (props.readonly) return
  const text = event.clipboardData?.getData('text/plain') || ''
  if (!text) return
  event.preventDefault()

  if (text.includes('\t')) {
    const rows = text
      .replace(/\r/g, '')
      .split('\n')
      .map((line) => line.split('\t'))
    insertHtml(buildTable(rows))
    return
  }

  insertHtml(escapeHtml(text).replace(/\r?\n/g, '<br>'))
}

watch(
  () => props.modelValue,
  () => nextTick(syncEditor),
)

onMounted(syncEditor)
onBeforeUnmount(stopColumnResize)
</script>

<style scoped>
.process-result-editor {
  border: 1px solid #d8dee8;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
}

.result-editor-header {
  min-height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 6px 8px 6px 10px;
  border-bottom: 1px solid #e8edf3;
  background: #f8fafc;
}

.result-editor-header > div:first-child {
  min-width: 0;
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.result-editor-header strong {
  color: #1f2937;
  font-size: 13px;
}

.result-editor-header span {
  color: #667085;
  font-size: 11px;
}

.result-editor-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.result-editor-toolbar button {
  min-height: 26px;
  padding: 3px 8px;
  border: 1px solid #d8dee8;
  border-radius: 4px;
  background: #fff;
  color: #344054;
  font-size: 12px;
  cursor: pointer;
}

.result-editor-toolbar button:hover {
  border-color: #84adff;
  color: #155eef;
}

.process-result-content {
  min-height: 150px;
  padding: 10px;
  overflow-x: auto;
  outline: none;
  color: #1f2937;
  font-size: 13px;
  line-height: 1.5;
}

.process-result-content:empty::before {
  color: #98a2b3;
  content: attr(data-placeholder);
  pointer-events: none;
}

.process-result-content:focus {
  box-shadow: inset 0 0 0 1px #84adff;
}

.process-result-content.readonly {
  min-height: auto;
}

.process-result-content :deep(table) {
  width: 100%;
  margin: 8px 0;
  border-collapse: collapse;
  table-layout: fixed;
}

.process-result-content :deep(th),
.process-result-content :deep(td) {
  min-width: 80px;
  padding: 6px 8px;
  border: 1px solid #d8dee8;
  text-align: left;
  vertical-align: top;
  overflow-wrap: anywhere;
  position: relative;
}

.process-result-content :deep(th) {
  background: #f2f4f7;
  font-weight: 700;
}

.process-result-content :deep(.result-column-resizer) {
  position: absolute;
  top: 0;
  right: -4px;
  z-index: 2;
  width: 8px;
  height: 100%;
  cursor: col-resize;
  user-select: none;
}

.process-result-content :deep(.result-column-resizer:hover) {
  background: rgba(21, 94, 239, 0.18);
}

:global(body.resizing-result-column) {
  cursor: col-resize;
  user-select: none;
}

@media (max-width: 768px) {
  .result-editor-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
