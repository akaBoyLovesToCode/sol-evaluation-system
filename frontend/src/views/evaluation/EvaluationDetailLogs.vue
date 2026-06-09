<template>
  <el-card class="detail-panel sidebar-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('evaluation.operationLogs') }}</span>
      </div>
    </template>
    <div class="logs-list">
      <el-timeline>
        <el-timeline-item
          v-for="log in logs"
          :key="log.id || log.created_at"
          :color="getOperationColor(log.operation_type)"
        >
          <template #dot>
            <el-icon>
              <component :is="getOperationIconName(log.operation_type)" />
            </el-icon>
          </template>
          <div class="log-content">
            <div class="log-time">
              {{ formatDateTime(log.created_at) }}
            </div>
            <div class="log-user">
              <el-tag size="small" type="info">{{
                (log.request_method || 'GET').toUpperCase()
              }}</el-tag>
              <el-tag size="small" :type="log.success ? 'success' : 'danger'" class="status-code">{{
                log.status_code || '-'
              }}</el-tag>
              <span class="request-path">{{ log.request_path }}</span>
            </div>
            <div class="log-action">
              {{ getOperationDescription(log) }}
            </div>
            <div class="log-meta">
              <span>IP: {{ log.ip_address || '-' }}</span>
              <span>UA: {{ (log.user_agent || '').slice(0, 80) }}</span>
            </div>
            <div v-if="log.old_data || log.new_data" class="log-diff">
              <el-button link type="primary" size="small" @click="toggleLog(log.id)">
                {{
                  logExpanded[log.id]
                    ? $t('common.hide') || 'Hide'
                    : $t('common.details') || 'Details'
                }}
              </el-button>
              <div v-show="logExpanded[log.id]" class="log-diff-content">
                <div v-if="getLogDiff(log).length > 0">
                  <div v-for="d in getLogDiff(log)" :key="d.key" class="diff-row">
                    <span class="diff-key">{{ d.key }}</span>
                    <span class="diff-from">{{ stringify(d.from) }}</span>
                    <span class="diff-arrow">→</span>
                    <span class="diff-to">{{ stringify(d.to) }}</span>
                  </div>
                </div>
                <div v-else>
                  <div v-if="log.new_data">
                    <strong>New:</strong> {{ stringify(parseJson(log.new_data)) }}
                  </div>
                  <div v-if="log.old_data">
                    <strong>Old:</strong> {{ stringify(parseJson(log.old_data)) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
      <div v-if="logs.length === 0" class="empty-logs">
        <el-empty :image-size="60" :description="$t('evaluation.noOperationLogs')" />
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps({
  logs: { type: Array, default: () => [] },
})

const { t } = useI18n()
const logExpanded = reactive({})

const toggleLog = (id) => {
  logExpanded[id] = !logExpanded[id]
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

const getOperationIconName = (operationType) => {
  const iconMap = {
    create: 'CirclePlus',
    update: 'EditPen',
    delete: 'Delete',
    view: 'View',
    login: 'User',
    logout: 'User',
    export: 'Download',
  }
  return iconMap[operationType] || 'EditPen'
}

const getOperationColor = (operationType) => {
  const colorMap = {
    create: '#67C23A',
    update: '#E6A23C',
    delete: '#F56C6C',
    view: '#909399',
    login: '#409EFF',
    logout: '#909399',
    export: '#409EFF',
  }
  return colorMap[operationType] || '#409EFF'
}

const getOperationDescription = (log) => {
  if (log.operation_type === 'create') return t('evaluation.operations.created')
  if (log.operation_type === 'update') {
    if (log.operation_description && log.operation_description.toLowerCase().includes('status')) {
      return t('evaluation.operations.statusChanged')
    }
    return t('evaluation.operations.updated')
  }
  if (log.operation_type === 'delete') return t('evaluation.operations.deleted')
  if (log.operation_type === 'export') return t('evaluation.operations.exported')
  if (log.operation_type === 'view') return t('evaluation.operations.viewed')
  if (log.operation_type === 'login') return t('evaluation.operations.loggedIn')
  if (log.operation_type === 'logout') return t('evaluation.operations.loggedOut')
  return log.operation_description || t('evaluation.operations.unknown')
}

const parseJson = (v) => {
  try {
    if (!v) return null
    return typeof v === 'string' ? JSON.parse(v) : v
  } catch {
    return null
  }
}

const stringify = (v) => {
  if (v === null || v === undefined) return ''
  return typeof v === 'object' ? JSON.stringify(v) : String(v)
}

const getLogDiff = (log) => {
  const oldObj = parseJson(log.old_data)
  const newObj = parseJson(log.new_data)
  if (!oldObj || !newObj) return []
  const keys = new Set([...Object.keys(oldObj), ...Object.keys(newObj)])
  const diffs = []
  keys.forEach((k) => {
    const a = oldObj[k]
    const b = newObj[k]
    if (JSON.stringify(a) !== JSON.stringify(b)) {
      diffs.push({ key: k, from: a, to: b })
    }
  })
  return diffs
}
</script>

<style scoped>
.detail-panel {
  --console-line: #d8dee8;
  --console-line-soft: #e8edf3;
  --console-ink: #1f2937;
  --console-muted: #667085;
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
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 750;
}

.logs-list {
  height: 300px;
  padding: 12px;
  overflow-y: auto;
}

.logs-list :deep(.el-timeline) {
  padding-left: 2px;
}

.logs-list :deep(.el-timeline-item__wrapper) {
  padding-left: 20px;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--console-ink);
}

.log-time {
  color: var(--console-muted);
  font-size: 11px;
  font-weight: 650;
}

.log-user {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--console-ink);
  font-size: 12px;
  font-weight: 650;
}

.request-path {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-action {
  color: #475467;
  font-size: 12px;
  line-height: 1.45;
}

.log-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  color: var(--console-muted);
  font-size: 11px;
}

.log-diff {
  margin-top: 2px;
}

.log-diff-content {
  margin-top: 6px;
  padding: 8px;
  border: 1px solid var(--console-line-soft);
  border-radius: 6px;
  background: #f8fafc;
  font-size: 11px;
}

.diff-row {
  display: grid;
  grid-template-columns: minmax(80px, 0.8fr) minmax(80px, 1fr) 18px minmax(80px, 1fr);
  gap: 6px;
  padding: 4px 0;
  border-bottom: 1px solid var(--console-line-soft);
}

.diff-row:last-child {
  border-bottom: 0;
}

.diff-key {
  color: #155eef;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
}

.diff-from {
  color: #b42318;
  text-decoration: line-through;
}

.diff-arrow {
  color: var(--console-muted);
}

.diff-to {
  color: #14804a;
}

.empty-logs {
  padding: 18px 0;
  color: var(--console-muted);
  font-size: 12px;
  text-align: center;
}
</style>
