<template>
  <div v-loading="loading" :class="['evaluation-detail-page', inDialog ? 'dialog-mode' : '']">
    <!-- Page Header (only when not in dialog) -->
    <EvaluationDetailHeader
      v-if="evaluation && !inDialog"
      :evaluation="evaluation"
      :can-edit="canEdit"
      :can-operate="canOperate"
      :can-pause="canPause"
      :can-resume="canResume"
      :can-cancel="canCancel"
      @edit="handleEdit"
      @manage-nested="goToNestedEditor"
      @operation="handleOperation"
    />

    <div v-if="evaluation" class="detail-content dialog-scroll">
      <!-- Dialog mode: Tabbed layout to reduce scrolling -->
      <template v-if="inDialog">
        <el-tabs v-model="activeTab" type="border-card" class="dialog-tabs">
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
      <el-row v-else :gutter="20">
        <!-- Main Content Column -->
        <el-col :xs="24" :md="16">
          <EvaluationDetailInfo
            ref="infoRef"
            :evaluation="evaluation"
            :can-edit="canEdit"
            :process-step-options="processStepOptions"
            @update="handleUpdateEvaluation"
            @save-start="saving = true"
            @save-end="saving = false"
          />

          <div class="mt-5">
            <EvaluationDetailSpecs
              :evaluation="evaluation"
              :can-edit="canEdit"
              @update="handleUpdateEvaluation"
              @save-start="saving = true"
              @save-end="saving = false"
            />
          </div>

          <div class="mt-5">
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
          <div v-if="evaluation.results && evaluation.results.length > 0" class="mt-5">
            <el-card class="info-card">
              <template #header>
                <span>{{ $t('evaluation.evaluationResults') }}</span>
              </template>
              <div class="results-section p-4">
                <div
                  v-for="result in evaluation.results"
                  :key="result.id"
                  class="result-item bg-gray-50 p-4 rounded-lg mb-4 last:mb-0"
                >
                  <div class="result-header flex justify-between items-center mb-2">
                    <h4 class="font-semibold text-gray-700 m-0">{{ result.test_item }}</h4>
                    <el-tag :type="result.result === 'pass' ? 'success' : 'danger'">
                      {{ result.result === 'pass' ? $t('evaluation.pass') : $t('evaluation.fail') }}
                    </el-tag>
                  </div>
                  <div class="result-content text-sm text-gray-600">
                    <p class="mb-1">
                      <strong>{{ $t('evaluation.testConditions') }}：</strong
                      >{{ result.test_conditions }}
                    </p>
                    <p class="mb-1">
                      <strong>{{ $t('evaluation.testResult') }}：</strong>{{ result.test_result }}
                    </p>
                    <p v-if="result.remarks">
                      <strong>{{ $t('evaluation.remarks') }}：</strong>{{ result.remarks }}
                    </p>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>

        <!-- Sidebar Column -->
        <el-col :xs="24" :md="8">
          <!-- Status Info (In sidebar for desktop, implicit in Info for mobile/dialog?) 
               Actually, Status Info was a separate card in the original.
               I should probably extract it or keep it here.
               For now, I'll keep the Status Card here as it's small.
          -->
          <el-card class="sidebar-card mb-5">
            <template #header>
              <span class="font-semibold">{{ $t('evaluation.statusInformation') }}</span>
            </template>
            <div class="status-info py-4">
              <div class="status-item flex justify-between mb-3 text-sm">
                <span class="text-gray-500">{{ $t('evaluation.currentStatus') }}：</span>
                <el-tag :type="getStatusTagType(evaluation.status)">
                  {{ $t(`status.${evaluation.status}`) }}
                </el-tag>
              </div>
              <div class="status-item flex justify-between mb-3 text-sm">
                <span class="text-gray-500">{{ $t('evaluation.createdAt') }}：</span>
                <span>{{ formatDateTime(evaluation.created_at) }}</span>
              </div>
              <div class="status-item flex justify-between mb-3 text-sm">
                <span class="text-gray-500">{{ $t('evaluation.updatedAt') }}：</span>
                <span>{{ formatDateTime(evaluation.updated_at) }}</span>
              </div>
            </div>
          </el-card>

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
        </el-col>
      </el-row>
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
  return ['draft', 'in_progress', 'paused'].includes(evaluation.value.status)
})

const canPause = computed(() => evaluation.value?.status === 'in_progress')
const canResume = computed(() => evaluation.value?.status === 'paused')
const canCancel = computed(() => {
  if (!evaluation.value) return false
  return !['completed', 'cancelled', 'rejected'].includes(evaluation.value.status)
})
const canOperate = computed(() => canPause.value || canResume.value || canCancel.value)

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

    let message = ''
    let confirmText = ''

    if (command === 'pause') {
      message = t('evaluation.confirmPause')
      confirmText = t('evaluation.pause')
    } else if (command === 'resume') {
      message = t('evaluation.confirmResume')
      confirmText = t('evaluation.resume')
    }

    await ElMessageBox.confirm(message, t('common.confirmAction'), {
      confirmButtonText: confirmText,
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })

    const status = command === 'pause' ? 'paused' : 'in_progress'
    await api.put(`/evaluations/${evaluation.value.id}/status`, { status })

    ElMessage.success(t('evaluation.operationSuccess'))
    fetchEvaluation()
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

const handleUploadFile = () => {
  ElMessage.info(t('evaluation.fileUploadInDevelopment') || 'Feature in development')
}

const handleDownloadFile = () => {
  ElMessage.info(t('evaluation.fileDownloadInDevelopment') || 'Feature in development')
}

// Utils
const getStatusTagType = (status) => {
  const typeMap = {
    draft: 'info',
    in_progress: 'primary',
    pending_approval: 'warning',
    completed: 'success',
    paused: 'info',
    cancelled: 'danger',
    rejected: 'danger',
  }
  return typeMap[status] || 'info'
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
})
</script>

<style scoped>
.evaluation-detail-page {
  padding: 0;
}

.dialog-mode .page-header {
  display: none;
}

.dialog-scroll {
  max-height: calc(80vh - 140px);
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
}

.info-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
}

.sidebar-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>
