<template>
  <el-card class="sidebar-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('evaluation.relatedFiles') }}</span>
        <el-tooltip
          v-if="canEdit"
          effect="dark"
          :content="disableActions ? $t('evaluation.fileUploadInDevelopment') : ''"
          placement="top"
        >
          <el-button size="small" :disabled="disableActions" @click="$emit('upload')">
            <template #icon><Plus /></template>
            {{ $t('evaluation.upload') }}
          </el-button>
        </el-tooltip>
      </div>
    </template>
    <div class="files-list py-4">
      <div
        v-for="file in files"
        :key="file.id"
        class="file-item flex items-center gap-3 py-3 border-b border-gray-100 last:border-0"
      >
        <el-icon class="file-icon text-blue-500 text-xl"><Document /></el-icon>
        <div class="file-info flex-1">
          <div class="file-name text-sm text-gray-800 mb-1">{{ file.filename }}</div>
          <div class="file-meta text-xs text-gray-400">
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
      <div
        v-if="!files || files.length === 0"
        class="empty-files text-center py-5 text-gray-400 text-sm"
      >
        {{ $t('evaluation.noRelatedFiles') }}
      </div>
    </div>
    <el-card v-if="legacyProcessNotes.length" class="legacy-card mt-4" shadow="never">
      <template #header>
        <span>Legacy (view-only)</span>
      </template>
      <div
        v-for="(note, index) in legacyProcessNotes"
        :key="`legacy-note-${index}`"
        class="legacy-note mb-3 last:mb-0"
      >
        <h4 class="legacy-title text-sm font-semibold text-gray-700 mb-1">{{ note.title }}</h4>
        <pre
          class="legacy-content bg-gray-100 rounded p-3 text-xs overflow-x-auto whitespace-pre-wrap font-mono"
          >{{ note.content }}</pre
        >
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
.sidebar-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
