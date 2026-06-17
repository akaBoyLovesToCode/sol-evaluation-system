<template>
  <div v-loading="loading" :class="['evaluation-detail-page', inDialog ? 'dialog-mode' : '']">
    <!-- Page Header (only when not in dialog) -->
    <EvaluationDetailHeader
      v-if="evaluation && !inDialog"
      :evaluation="evaluation"
      :can-edit="canEdit"
      :can-operate="canOperate"
      :can-reopen="canReopen"
      :can-cancel="canCancel"
      @edit="handleEdit"
      @manage-nested="goToNestedEditor"
      @operation="handleOperation"
    />

    <div v-if="evaluation" :class="['detail-content', inDialog ? 'dialog-scroll' : '']">
      <!-- Dialog mode: Tabbed layout to reduce scrolling -->
      <template v-if="inDialog">
        <el-tabs v-model="activeTab" type="card" class="detail-tabs">
          <el-tab-pane :label="$t('evaluation.basicInformation')" name="details">
            <EvaluationDetailInfo
              ref="infoRef"
              :evaluation="evaluation"
              :can-edit="canEdit"
              :process-step-options="processStepOptions"
              @update="handleUpdateEvaluation"
              @save-start="saving = true"
              @save-end="saving = false"
            />
            <div class="mt-4">
              <EvaluationDetailFiles
                :files="evaluation.files"
                :legacy-process-notes="legacyProcessNotes"
                :can-edit="canEdit"
                :disable-actions="true"
                @upload="handleUploadFile"
                @download="handleDownloadFile"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.technicalSpecifications')" name="specs">
            <EvaluationDetailSpecs
              :evaluation="evaluation"
              :can-edit="canEdit"
              @update="handleUpdateEvaluation"
              @save-start="saving = true"
              @save-end="saving = false"
            />
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.evaluationProcesses')" name="processes">
            <EvaluationDetailNestedProcesses
              ref="nestedRef"
              :builder-payload="builderPayload"
              :warnings="nestedSaveWarnings"
              :error="nestedSaveError"
              :can-edit="canEdit"
              :can-cancel="canCancel"
              @save-nested="handleSaveNested"
              @clear-warnings="nestedSaveWarnings = []"
              @clear-error="nestedSaveError = null"
              @cancel-evaluation="promptCancelEvaluation"
            />
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.operationLogs')" name="logs">
            <EvaluationDetailLogs :logs="filteredLogs" />
          </el-tab-pane>
        </el-tabs>
      </template>

      <!-- Full-page layout (non-dialog) -->
      <div v-else class="detail-layout">
        <main class="detail-main">
          <EvaluationDetailInfo
            ref="infoRef"
            :evaluation="evaluation"
            :can-edit="canEdit"
            :process-step-options="processStepOptions"
            @update="handleUpdateEvaluation"
            @save-start="saving = true"
            @save-end="saving = false"
          />

          <div class="detail-section">
            <EvaluationDetailSpecs
              :evaluation="evaluation"
              :can-edit="canEdit"
              @update="handleUpdateEvaluation"
              @save-start="saving = true"
              @save-end="saving = false"
            />
          </div>

          <div class="detail-section">
            <EvaluationDetailNestedProcesses
              ref="nestedRef"
              :builder-payload="builderPayload"
              :warnings="nestedSaveWarnings"
              :error="nestedSaveError"
              :can-edit="canEdit"
              :can-cancel="canCancel"
              @save-nested="handleSaveNested"
              @clear-warnings="nestedSaveWarnings = []"
              @clear-error="nestedSaveError = null"
              @cancel-evaluation="promptCancelEvaluation"
            />
          </div>

          <!-- Evaluation Results (Legacy/Simple) -->
          <div v-if="evaluation.results && evaluation.results.length > 0" class="detail-section">
            <section class="detail-panel results-panel">
              <div class="detail-panel-header">
                <span>{{ $t('evaluation.evaluationResults') }}</span>
              </div>
              <div class="results-section">
                <div v-for="result in evaluation.results" :key="result.id" class="result-item">
                  <div class="result-header">
                    <h4>{{ result.test_item }}</h4>
                    <el-tag :type="result.result === 'pass' ? 'success' : 'danger'">
                      {{ result.result === 'pass' ? $t('evaluation.pass') : $t('evaluation.fail') }}
                    </el-tag>
                  </div>
                  <div class="result-content">
                    <p>
                      <strong>{{ $t('evaluation.testConditions') }}：</strong
                      >{{ result.test_conditions }}
                    </p>
                    <p>
                      <strong>{{ $t('evaluation.testResult') }}：</strong>{{ result.test_result }}
                    </p>
                    <p v-if="result.remarks">
                      <strong>{{ $t('evaluation.remarks') }}：</strong>{{ result.remarks }}
                    </p>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </main>

        <!-- Sidebar Column -->
        <aside class="detail-aside">
          <section class="detail-panel sidebar-panel">
            <div class="detail-panel-header">
              <span>{{ $t('evaluation.statusInformation') }}</span>
            </div>
            <div class="status-info">
              <div class="status-item">
                <span>{{ $t('evaluation.currentStatus') }}：</span>
                <el-tag
                  v-if="isSupportedStatus(evaluation.status)"
                  :type="getStatusTagType(evaluation.status)"
                >
                  {{ formatStatusLabel(evaluation.status) }}
                </el-tag>
                <strong v-else>-</strong>
              </div>
              <div class="status-item">
                <span>{{ $t('evaluation.createdAt') }}：</span>
                <strong>{{ formatDateTime(evaluation.created_at) }}</strong>
              </div>
              <div class="status-item">
                <span>{{ $t('evaluation.updatedAt') }}：</span>
                <strong>{{ formatDateTime(evaluation.updated_at) }}</strong>
              </div>
            </div>
          </section>

          <EvaluationDetailFiles
            class="mb-5"
            :files="evaluation.files"
            :legacy-process-notes="legacyProcessNotes"
            :can-edit="canEdit"
            :disable-actions="true"
            @upload="handleUploadFile"
            @download="handleDownloadFile"
          />

          <EvaluationDetailLogs :logs="filteredLogs" />
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'
import {
  builderPayloadToNestedRequest,
  createEmptyBuilderPayload,
  evaluationToBuilderPayload,
  extractLegacyProcessNotes,
  normalizeBuilderPayload,
} from '../utils/processMapper'

// Lazy load sub-components
const EvaluationDetailHeader = defineAsyncComponent(
  () => import('./evaluation/EvaluationDetailHeader.vue'),
)
const EvaluationDetailInfo = defineAsyncComponent(
  () => import('./evaluation/EvaluationDetailInfo.vue'),
)
const EvaluationDetailSpecs = defineAsyncComponent(
  () => import('./evaluation/EvaluationDetailSpecs.vue'),
)
const EvaluationDetailNestedProcesses = defineAsyncComponent(
  () => import('./evaluation/EvaluationDetailNestedProcesses.vue'),
)
const EvaluationDetailLogs = defineAsyncComponent(
  () => import('./evaluation/EvaluationDetailLogs.vue'),
)
const EvaluationDetailFiles = defineAsyncComponent(
  () => import('./evaluation/EvaluationDetailFiles.vue'),
)

const props = defineProps({
  inDialog: { type: Boolean, default: false },
  evaluationId: { type: [String, Number], default: null },
  processStepOptions: {
    type: Array,
    default: () => ['iARTs', 'Aging', 'LI', 'Repair'],
  },
})

const route = useRoute()
const { t } = useI18n()
const supportedStatuses = ['in_progress', 'completed', 'cancelled']

const loading = ref(false)
const saving = ref(false)
const evaluation = ref(null)
const activeTab = ref('details')

// Nested Builder State
const builderPayload = ref(normalizeBuilderPayload(createEmptyBuilderPayload()))
const nestedSaveWarnings = ref([])
const nestedSaveError = ref(null)

// Refs
const infoRef = ref(null)
const nestedRef = ref(null)

const legacyProcessNotes = computed(() => extractLegacyProcessNotes(evaluation.value) || [])
const filteredLogs = computed(() => evaluation.value?.logs || [])

const canEdit = computed(() => {
  if (!evaluation.value) return false
  return evaluation.value.status === 'in_progress'
})

const canReopen = computed(() => {
  if (!evaluation.value) return false
  return ['completed', 'cancelled'].includes(evaluation.value.status)
})
const canCancel = computed(() => {
  if (!evaluation.value) return false
  return evaluation.value.status === 'in_progress'
})
const canOperate = computed(() => canReopen.value || canCancel.value)

// Data Fetching
async function fetchEvaluation(options = {}) {
  const { preserveWarnings = false } = options
  try {
    loading.value = true
    const id = props.evaluationId || route.params.id
    const response = await api.get(`/evaluations/${id}`)
    evaluation.value = response.data.data.evaluation

    if (evaluation.value) {
      builderPayload.value = normalizeBuilderPayload(evaluationToBuilderPayload(evaluation.value))
      if (!preserveWarnings) {
        nestedSaveWarnings.value = []
      }
      // Fetch combined logs
      try {
        const logsResp = await api.get(`/evaluations/${id}/logs`)
        if (logsResp.data?.data?.logs) {
          evaluation.value.logs = logsResp.data.data.logs
        }
      } catch (e) {
        console.warn('Failed to fetch combined logs', e)
      }

      // Also fetch nested separately to ensure sync?
      // The original code did `refreshNestedPayload`.
      await refreshNestedPayload(evaluation.value.id, evaluation.value, { preserveWarnings })
    }
  } catch (error) {
    ElMessage.error(t('evaluation.getEvaluationDetailsFailed'))
    console.error('Failed to fetch evaluation:', error)
  } finally {
    loading.value = false
  }
}

async function refreshNestedPayload(targetId, evaluationContext = null, options = {}) {
  const { preserveWarnings = false } = options
  try {
    const response = await api.get(`/evaluations/${targetId}/processes/nested`)
    const payload = response.data?.data?.payload
    const warnings = response.data?.data?.warnings || []

    if (payload) {
      builderPayload.value = normalizeBuilderPayload(payload)
    } else if (evaluationContext) {
      builderPayload.value = normalizeBuilderPayload(evaluationToBuilderPayload(evaluationContext))
    }

    if (!preserveWarnings) {
      nestedSaveWarnings.value = warnings
    }
  } catch (error) {
    console.error('Failed to load nested process payload', error)
    if (!preserveWarnings) {
      nestedSaveWarnings.value = []
    }
  }
}

// Actions
const handleEdit = () => {
  infoRef.value?.startEdit()
}

const goToNestedEditor = () => {
  nestedRef.value?.openProcessDrawer()
}

const handleUpdateEvaluation = async (formData) => {
  if (!evaluation.value) return
  try {
    // Merge new data with basic payload structure
    const payload = {
      ...formData,
      // Normalize multi-select fields to comma-separated strings for API
      process_step: Array.isArray(formData.process_step)
        ? formData.process_step.join(',')
        : formData.process_step,
      evaluation_reason: Array.isArray(formData.evaluation_reason)
        ? formData.evaluation_reason.join(',')
        : formData.evaluation_reason,
      // Ensure nulls for empty dates
      start_date: formData.start_date || null,
      end_date: formData.end_date || null,
    }

    await api.put(`/evaluations/${evaluation.value.id}`, payload)

    // Status update if changed
    if (formData.status && formData.status !== evaluation.value.status) {
      await api.put(`/evaluations/${evaluation.value.id}/status`, { status: formData.status })
    }

    ElMessage.success(t('common.saveSuccess'))
    await fetchEvaluation()
  } catch (error) {
    ElMessage.error(t('common.saveError'))
    console.error('Save evaluation failed:', error)
    throw error // Re-throw to let child handle state
  }
}

const handleSaveNested = async (newPayload) => {
  if (!evaluation.value) return
  try {
    const payload = builderPayloadToNestedRequest(newPayload)
    const response = await api.post(`/evaluations/${evaluation.value.id}/processes/nested`, payload)

    nestedSaveWarnings.value = response.data?.data?.warnings || []
    nestedSaveError.value = null

    await fetchEvaluation({ preserveWarnings: true })

    if (nestedSaveWarnings.value.length) {
      ElMessage.warning('Nested processes saved with warnings.')
    } else {
      ElMessage.success('Nested processes saved')
    }
  } catch (error) {
    nestedSaveError.value = 'Failed to save nested processes.'
    console.error('Failed to save nested processes', error)
  }
}

const handleOperation = async (command) => {
  if (!evaluation.value) return
  try {
    if (command === 'cancel') {
      await promptCancelEvaluation()
      return
    }
    if (command === 'reopen') {
      await promptReopenEvaluation()
      return
    }

    console.warn(`Unsupported evaluation operation: ${command}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('evaluation.operationFailed'))
    }
  }
}

const promptCancelEvaluation = async () => {
  if (!evaluation.value) return
  try {
    const { value } = await ElMessageBox.prompt(
      t('evaluation.cancelReasonPrompt'),
      t('evaluation.cancel'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.close'),
        inputPlaceholder: t('evaluation.cancelReasonPlaceholder'),
        inputType: 'textarea',
      },
    )

    await api.put(`/evaluations/${evaluation.value.id}/status`, {
      status: 'cancelled',
      cancel_reason: value || '',
    })

    ElMessage.success(t('evaluation.operationSuccess'))
    fetchEvaluation()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const promptReopenEvaluation = async () => {
  if (!evaluation.value) return
  try {
    await ElMessageBox.confirm(t('evaluation.confirmReopen'), t('common.confirmAction'), {
      confirmButtonText: t('evaluation.reopen'),
      cancelButtonText: t('common.close'),
      type: 'warning',
    })

    await api.put(`/evaluations/${evaluation.value.id}/status`, {
      status: 'in_progress',
    })

    ElMessage.success(t('evaluation.operationSuccess'))
    fetchEvaluation()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const handleUploadFile = () => {
  ElMessage.info(t('evaluation.fileUploadInDevelopment') || 'Feature in development')
}

const handleDownloadFile = () => {
  ElMessage.info(t('evaluation.fileDownloadInDevelopment') || 'Feature in development')
}

// Utils
const getStatusTagType = (status) => {
  const typeMap = {
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'danger',
  }
  return typeMap[status] || 'info'
}

const isSupportedStatus = (status) => supportedStatuses.includes(status)

const formatStatusLabel = (status) => {
  if (!isSupportedStatus(status)) return '-'
  return t(`status.${status}`)
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  fetchEvaluation()
})

// Expose for parent dialog usage
defineExpose({
  promptCancelEvaluation,
  promptReopenEvaluation,
  evaluation,
})
</script>

<style scoped>
.evaluation-detail-page {
  --console-bg: #f5f7fa;
  --console-panel: #ffffff;
  --console-line: #d8dee8;
  --console-line-soft: #e8edf3;
  --console-ink: #1f2937;
  --console-muted: #667085;
  --console-blue: #155eef;
  --console-blue-dark: #0f48b8;
  --console-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
  padding: 0;
  background: var(--console-bg);
  min-height: 100vh;
  color: var(--console-ink);
  font-size: 13px;
}

.dialog-mode .page-header {
  display: none;
}

.detail-content {
  width: 100%;
}

.dialog-scroll {
  max-height: calc(80vh - 140px);
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 360px);
  gap: 12px;
  align-items: start;
}

.detail-main,
.detail-aside {
  min-width: 0;
}

.detail-section {
  margin-top: 12px;
}

.detail-panel {
  background: var(--console-panel);
  border: 1px solid var(--console-line);
  border-radius: 6px;
  box-shadow: var(--console-shadow);
  overflow: hidden;
}

.detail-panel-header {
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 6px 12px;
  border-bottom: 1px solid var(--console-line);
  background: #fff;
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 750;
}

.sidebar-panel {
  margin-bottom: 12px;
}

.status-info {
  padding: 4px 12px;
}

.status-item {
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-bottom: 1px solid var(--console-line-soft);
  color: var(--console-muted);
  font-size: 12px;
}

.status-item:last-child {
  border-bottom: 0;
}

.status-item strong {
  color: var(--console-ink);
  font-size: 12px;
  font-weight: 650;
  text-align: right;
}

.results-section {
  padding: 12px;
}

.result-item {
  padding: 10px;
  border: 1px solid var(--console-line-soft);
  border-radius: 6px;
  background: #fff;
}

.result-item + .result-item {
  margin-top: 8px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

.result-header h4 {
  margin: 0;
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 750;
}

.result-content {
  color: #475467;
  font-size: 12px;
  line-height: 1.45;
}

.result-content p {
  margin: 0 0 4px;
}

.result-content p:last-child {
  margin-bottom: 0;
}

.detail-tabs {
  border: 1px solid var(--console-line);
  border-radius: 6px;
  box-shadow: var(--console-shadow);
  overflow: hidden;
}

.detail-tabs :deep(.el-tabs__header) {
  margin: 0;
  background: #fff;
  border-bottom: 1px solid var(--console-line);
}

.detail-tabs :deep(.el-tabs__nav) {
  border: 0;
}

.detail-tabs :deep(.el-tabs__item) {
  height: 36px;
  border-left: 0;
  color: var(--console-muted);
  font-size: 12px;
  font-weight: 700;
}

.detail-tabs :deep(.el-tabs__item.is-active) {
  color: var(--console-blue-dark);
  background: #eef4ff;
}

.detail-tabs :deep(.el-tabs__content) {
  padding: 12px;
  background: var(--console-bg);
}

@media (max-width: 1100px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
