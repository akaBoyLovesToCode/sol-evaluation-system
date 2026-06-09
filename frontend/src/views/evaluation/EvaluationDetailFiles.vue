<template>
  <el-card class="detail-panel sidebar-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('evaluation.relatedFiles') }}</span>
        <el-tooltip
          v-if="canEdit"
          effect="dark"
          :content="disableActions ? $t('evaluation.fileUploadInDevelopment') : ''"
          placement="top"
        >
          <el-button
            size="small"
            class="detail-button"
            :disabled="disableActions"
            @click="$emit('upload')"
          >
            {{ $t('evaluation.upload') }}
          </el-button>
        </el-tooltip>
      </div>
    </template>
    <div class="files-list">
      <div v-for="file in files" :key="file.id" class="file-item">
        <el-icon class="file-icon"><Document /></el-icon>
        <div class="file-info">
          <div class="file-name">{{ file.filename }}</div>
          <div class="file-meta">
            {{ formatFileSize(file.size) }} •
            {{ formatDate(file.created_at) }}
          </div>
        </div>
        <el-tooltip
          effect="dark"
          :content="disableActions ? $t('evaluation.fileDownloadInDevelopment') : ''"
          placement="top"
        >
          <el-button
            size="small"
            aria-label="Download file"
            title="Download file"
            :disabled="disableActions"
            @click="$emit('download', file)"
          >
            <template #icon><Download /></template>
          </el-button>
        </el-tooltip>
      </div>
      <div v-if="!files || files.length === 0" class="empty-files">
        {{ $t('evaluation.noRelatedFiles') }}
      </div>
    </div>
    <el-card v-if="legacyProcessNotes.length" class="legacy-card" shadow="never">
      <template #header>
        <span>Legacy (view-only)</span>
      </template>
      <div
        v-for="(note, index) in legacyProcessNotes"
        :key="`legacy-note-${index}`"
        class="legacy-note"
      >
        <h4 class="legacy-title">{{ note.title }}</h4>
        <pre class="legacy-content">{{ note.content }}</pre>
      </div>
    </el-card>
  </el-card>
</template>

<script setup>
defineProps({
  files: { type: Array, default: () => [] },
  legacyProcessNotes: { type: Array, default: () => [] },
  canEdit: Boolean,
  disableActions: { type: Boolean, default: false },
})

defineEmits(['upload', 'download'])

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.detail-panel {
  --console-line: #d8dee8;
  --console-line-soft: #e8edf3;
  --console-ink: #1f2937;
  --console-muted: #667085;
  margin-bottom: 12px;
  border: 1px solid var(--console-line);
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
  overflow: hidden;
}

.detail-panel :deep(.el-card__header) {
  min-height: 42px;
  padding: 6px 12px;
  background: #fff;
  border-bottom: 1px solid var(--console-line);
  font-weight: 750;
}

.detail-panel :deep(.el-card__body) {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 750;
}

.detail-button {
  height: 28px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
}

.files-list {
  padding: 2px 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 48px;
  padding: 8px 0;
  border-bottom: 1px solid var(--console-line-soft);
}

.file-item:last-child {
  border-bottom: 0;
}

.file-icon {
  color: #155eef;
  font-size: 18px;
}

.file-info {
  min-width: 0;
  flex: 1;
}

.file-name {
  margin-bottom: 2px;
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 650;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  color: var(--console-muted);
  font-size: 12px;
}

.empty-files {
  padding: 18px 0;
  color: var(--console-muted);
  font-size: 12px;
  text-align: center;
}

.legacy-card {
  margin: 10px 12px 12px;
  border-color: var(--console-line-soft);
  border-radius: 6px;
}

.legacy-card :deep(.el-card__header) {
  min-height: 36px;
  padding: 7px 10px;
  background: #f8fafc;
  color: var(--console-muted);
  font-size: 12px;
}

.legacy-card :deep(.el-card__body) {
  padding: 10px;
}

.legacy-note {
  margin-bottom: 10px;
}

.legacy-note:last-child {
  margin-bottom: 0;
}

.legacy-title {
  margin: 0 0 4px;
  color: var(--console-ink);
  font-size: 12px;
  font-weight: 700;
}

.legacy-content {
  margin: 0;
  padding: 8px;
  overflow-x: auto;
  border-radius: 6px;
  background: #f8fafc;
  color: var(--console-ink);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  font-size: 11px;
  white-space: pre-wrap;
}
</style>
