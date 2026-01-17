<template>
  <el-card class="sidebar-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('evaluation.operationLogs') }}</span>
      </div>
    </template>
    <div class="logs-list h-[300px] overflow-y-auto p-4">
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
          <div class="log-content flex flex-col gap-1">
            <div class="log-time text-xs text-gray-400 font-medium mb-1">
              {{ formatDateTime(log.created_at) }}
            </div>
            <div class="log-user text-sm font-semibold text-gray-700">
              <el-tag size="small" type="info">{{
                (log.request_method || 'GET').toUpperCase()
              }}</el-tag>
              <el-tag size="small" :type="log.success ? 'success' : 'danger'" class="ml-1">{{
                log.status_code || '-'
              }}</el-tag>
              <span class="ml-2">{{ log.request_path }}</span>
            </div>
            <div class="log-action text-sm text-gray-600 leading-snug">
              {{ getOperationDescription(log) }}
            </div>
            <div class="log-meta text-xs text-gray-400 mt-1">
              <span>IP: {{ log.ip_address || '-' }}</span>
              <span class="ml-2">UA: {{ (log.user_agent || '').slice(0, 80) }}</span>
            </div>
            <div v-if="log.old_data || log.new_data" class="log-diff mt-1">
              <el-button link type="primary" size="small" @click="toggleLog(log.id)">
                {{
                  logExpanded[log.id]
                    ? $t('common.hide') || 'Hide'
                    : $t('common.details') || 'Details'
                }}
              </el-button>
              <div v-show="logExpanded[log.id]" class="mt-2 bg-gray-50 p-2 rounded text-xs">
                <div v-if="getLogDiff(log).length > 0">
                  <div
                    v-for="d in getLogDiff(log)"
                    :key="d.key"
                    class="diff-row flex gap-2 border-b border-gray-100 last:border-0 py-1"
                  >
                    <span class="diff-key font-mono text-blue-600">{{ d.key }}</span>
                    <span class="diff-from text-red-500 line-through">{{ stringify(d.from) }}</span>
                    <span class="diff-arrow text-gray-400">→</span>
                    <span class="diff-to text-green-600">{{ stringify(d.to) }}</span>
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
      <div v-if="logs.length === 0" class="empty-logs text-center py-5 text-gray-400 text-sm">
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
    approve: 'CircleCheck',
    reject: 'CircleClose',
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
    approve: '#67C23A',
    reject: '#F56C6C',
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
