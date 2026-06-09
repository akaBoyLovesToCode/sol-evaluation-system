<template>
  <div>
    <el-card class="detail-panel info-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('evaluation.evaluationProcesses') }}</span>
          <el-button
            v-if="canEdit"
            type="primary"
            plain
            class="detail-button"
            @click="openProcessDrawer"
          >
            {{ $t('evaluation.manageNestedProcesses') }}
          </el-button>
        </div>
      </template>

      <el-empty v-if="!hasBuilderSteps" :description="$t('nested.summary.empty')" />

      <div v-else class="nested-summary">
        <div v-for="process in summaryProcesses" :key="process.key" class="nested-process-summary">
          <div class="nested-process-header">
            <strong>{{ process.name }}</strong>
            <span class="nested-process-chain">
              {{
                process.steps
                  .map((step) => stepLabelForPath(step, $t('nested.newStep')))
                  .join(' → ')
              }}
            </span>
          </div>
          <ul v-if="process.lots.length" class="nested-process-lots">
            <li v-for="lot in process.lots" :key="lot.client_id">{{ lot.label }}</li>
          </ul>
          <div class="nested-process-body">
            <section class="nested-step-column">
              <h4>{{ $t('nested.stepRecords') }}</h4>
              <div
                v-for="step in process.steps"
                :key="`${process.key}-${step.order_index}`"
                class="nested-summary-item"
              >
                <div class="nested-step-title">
                  <strong>{{ step.order_index }}. {{ step.step_code }}</strong>
                  <span v-if="step.step_label"> - {{ step.step_label }}</span>
                </div>
                <div class="nested-step-meta">
                  <template v-if="step.results_applicable === false">
                    {{ $t('nested.summary.noResults') }}
                  </template>
                  <template v-else-if="isReliabilityStepCode(step.step_code)">
                    {{ reliabilitySummaryFor(step) || totalsSummaryFor(step) }}
                  </template>
                  <template v-else>
                    {{ totalsSummaryFor(step) }}
                  </template>
                </div>
                <div class="nested-step-lots">
                  {{ $t('nested.summary.appliesTo') }}
                  {{ describeStepLots(process, step.lot_refs) }}
                </div>
                <div v-if="hasFailures(step)" class="nested-failure-panel">
                  <div class="nested-failure-header">
                    <div class="nested-failure-title">
                      <el-tag size="small" type="danger" effect="dark">{{
                        $t('nested.failureTitle')
                      }}</el-tag>
                      <span class="nested-failure-count text-sm">
                        {{ $t('nested.summary.failuresCount', { count: step.failures.length }) }}
                      </span>
                    </div>
                  </div>
                  <div class="nested-failure-table-wrapper">
                    <table class="nested-failure-table">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>{{ $t('nested.failCode') }} / {{ $t('nested.failName') }}</th>
                          <th>{{ $t('nested.serialNumber') }}</th>
                          <th>{{ $t('nested.analysisResult') }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="(failure, failureIndex) in step.failures"
                          :key="`${process.key}-${step.order_index}-${failure.sequence || failure.serial_number || failure.fail_code_text || failureIndex}`"
                        >
                          <td>#{{ failure.sequence || failureIndex + 1 }}</td>
                          <td>
                            <div class="flex flex-wrap gap-1 items-center">
                              <el-tag size="small" type="danger" effect="plain">
                                {{ failure.fail_code_text || $t('nested.failCode') }}
                              </el-tag>
                              <el-tag
                                v-if="failure.fail_code_name_snapshot"
                                size="small"
                                type="info"
                                effect="plain"
                              >
                                {{ failure.fail_code_name_snapshot }}
                              </el-tag>
                            </div>
                          </td>
                          <td>
                            <el-tag
                              v-if="failure.serial_number"
                              size="small"
                              type="info"
                              effect="plain"
                            >
                              {{ failure.serial_number }}
                            </el-tag>
                            <span v-else class="muted">-</span>
                          </td>
                          <td>
                            <p>{{ failure.analysis_result || '-' }}</p>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </section>
            <aside class="nested-result-column">
              <h4>{{ $t('nested.processResult') }}</h4>
              <ProcessResultContent
                v-if="process.result_html"
                class="nested-result-content"
                :html="process.result_html"
              />
              <div v-else class="nested-result-empty">{{ $t('nested.processResultEmpty') }}</div>
            </aside>
          </div>
        </div>
      </div>

      <el-alert
        v-if="warnings.length"
        type="warning"
        show-icon
        class="mt-3"
        @close="$emit('clear-warnings')"
      >
        <ul class="list-none p-0 m-0">
          <li v-for="(warning, index) in warnings" :key="`nested-warning-${index}`">
            {{ warning }}
          </li>
        </ul>
      </el-alert>
      <el-alert v-if="error" type="error" show-icon class="mt-3" @close="$emit('clear-error')">
        {{ error }}
      </el-alert>
    </el-card>

    <el-drawer
      v-model="drawerVisible"
      :size="drawerSize"
      :before-close="handleProcessDrawerBeforeClose"
      :title="$t('evaluation.manageNestedProcesses')"
      class="detail-process-drawer"
    >
      <ProcessBuilder
        ref="processBuilderRef"
        :initial-payload="builderPayload"
        :server-warnings="builderWarnings"
        :show-save-button="false"
        @dirty-change="handleBuilderDirtyChange"
      />
      <template #footer>
        <div class="flex justify-end gap-3">
          <el-button @click="handleDrawerCancel">{{ $t('common.close') }}</el-button>
          <el-button type="primary" @click="commitBuilderChanges">{{
            $t('common.save')
          }}</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessageBox } from 'element-plus'
import ProcessBuilder from '../../components/ProcessBuilder.vue'
import ProcessResultContent from '../../components/ProcessResultContent.vue'
import {
  buildReliabilitySummary,
  buildTotalsSummary,
  stepLabelForPath,
  isReliabilityStep,
} from '../../utils/reliability'
import { hasBuilderSteps, normalizeBuilderPayload } from '../../utils/processMapper'

const props = defineProps({
  builderPayload: { type: Object, default: () => ({}) },
  warnings: { type: Array, default: () => [] },
  error: { type: String, default: '' },
  canEdit: Boolean,
  canCancel: Boolean,
})

const emit = defineEmits(['save-nested', 'clear-warnings', 'clear-error', 'cancel-evaluation'])

const { t } = useI18n()
const drawerVisible = ref(false)
const processBuilderRef = ref(null)
const processBuilderDirty = ref(false)
const builderWarnings = ref([])

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)
const drawerSize = computed(() => (isMobile.value ? '100%' : '60%'))

const updateWidth = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', updateWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})

const summaryProcesses = computed(() => {
  const processes = Array.isArray(props.builderPayload.processes)
    ? props.builderPayload.processes
    : []

  return processes.map((process, processIndex) => {
    const lots = Array.isArray(process.lots) ? process.lots : []
    const lotLabels = lots.map((lot, lotIndex) => {
      const quantity = Number(lot.quantity) || 0
      const lotNumber = lot.lot_number || t('nested.summary.lotFallback', { index: lotIndex + 1 })
      const label = quantity ? `${lotNumber} (${quantity})` : lotNumber
      return {
        client_id: lot.client_id || lot.temp_id || `${process.key || 'proc'}-lot-${lotIndex}`,
        label,
      }
    })
    const lotLabelMap = new Map(lotLabels.map((lot) => [String(lot.client_id), lot.label]))

    return {
      key: process.key || `proc_${processIndex + 1}`,
      name: process.name || t('nested.defaultProcessName', { index: processIndex + 1 }),
      order_index: process.order_index || processIndex + 1,
      result_html: process.result_html || '',
      lots: lotLabels,
      lotLabelMap,
      steps: Array.isArray(process.steps) ? process.steps : [],
    }
  })
})

const describeStepLots = (process, lotRefs) => {
  if (!Array.isArray(lotRefs) || !lotRefs.length) {
    return t('nested.summary.allLots')
  }
  const labels = lotRefs
    .map((ref) => process.lotLabelMap.get(String(ref)) || process.lotLabelMap.get(ref))
    .filter(Boolean)
  if (!labels.length) {
    return t('nested.summary.allLots')
  }
  return labels.join(', ')
}

const reliabilitySummaryFor = (step) => buildReliabilitySummary(step, t)
const totalsSummaryFor = (step) => buildTotalsSummary(step, t)
const isReliabilityStepCode = (code) => isReliabilityStep(code)
const hasFailures = (step) => Array.isArray(step?.failures) && step.failures.length > 0

const openProcessDrawer = async () => {
  builderWarnings.value = Array.isArray(props.warnings) ? [...props.warnings] : []
  drawerVisible.value = true
  await nextTick()
  processBuilderRef.value?.setPayload(props.builderPayload, { markClean: true })
  processBuilderDirty.value = false
}

const handleProcessDrawerBeforeClose = async (done) => {
  if (processBuilderDirty.value) {
    try {
      await ElMessageBox.confirm(t('nested.discardChanges'), t('common.confirmAction'), {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      })
      processBuilderRef.value?.markPristine()
      processBuilderDirty.value = false
    } catch {
      return
    }
  }
  drawerVisible.value = false
  if (typeof done === 'function') done()
}

const handleDrawerCancel = () => {
  handleProcessDrawerBeforeClose(() => {
    drawerVisible.value = false
  })
}

const handleBuilderDirtyChange = (value) => {
  processBuilderDirty.value = value
}

const commitBuilderChanges = async () => {
  if (!processBuilderRef.value) return
  const newPayload = normalizeBuilderPayload(processBuilderRef.value.getPayload())
  builderWarnings.value = []
  processBuilderRef.value.markPristine()
  processBuilderDirty.value = false
  drawerVisible.value = false
  emit('save-nested', newPayload)
}

defineExpose({ openProcessDrawer })
</script>

<style scoped>
.detail-panel {
  --console-line: #d8dee8;
  --console-line-soft: #e8edf3;
  --console-ink: #1f2937;
  --console-muted: #667085;
  margin-bottom: 0;
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
  padding: 12px;
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
  min-height: 28px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
}

.nested-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nested-process-summary {
  border: 1px solid var(--console-line-soft);
  border-radius: 6px;
  background: #fff;
}

.nested-process-header {
  min-height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 10px;
  border-bottom: 1px solid var(--console-line-soft);
}

.nested-process-header strong {
  color: var(--console-ink);
  font-size: 13px;
}

.nested-process-chain,
.nested-step-meta,
.nested-step-lots,
.muted {
  color: var(--console-muted);
  font-size: 12px;
}

.nested-process-lots {
  margin: 8px 10px;
  padding-left: 18px;
  color: var(--console-muted);
  font-size: 12px;
}

.nested-process-body {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(0, 2fr);
  border-top: 1px solid var(--console-line-soft);
}

.nested-step-column,
.nested-result-column {
  min-width: 0;
  padding: 10px;
}

.nested-result-column {
  border-left: 1px solid var(--console-line-soft);
  background: #fbfcfe;
}

.nested-step-column h4,
.nested-result-column h4 {
  margin: 0 0 8px;
  color: var(--console-muted);
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.nested-summary-item {
  margin: 0 0 8px;
  padding: 9px 10px;
  border: 1px solid var(--console-line-soft);
  border-radius: 6px;
  background: #f8fafc;
}

.nested-summary-item:last-child {
  margin-bottom: 0;
}

.nested-result-content,
.nested-result-empty {
  min-height: 96px;
  padding: 9px 10px;
  border: 1px solid var(--console-line-soft);
  border-radius: 6px;
  background: #fff;
  color: var(--console-ink);
  font-size: 12px;
  line-height: 1.5;
}

.nested-result-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--console-muted);
  text-align: center;
}

.nested-result-content :deep(p),
.nested-result-content :deep(div) {
  margin: 0 0 6px;
}

.nested-result-content :deep(table) {
  width: 100%;
  margin: 8px 0;
  border-collapse: collapse;
  table-layout: fixed;
}

.nested-result-content :deep(th),
.nested-result-content :deep(td) {
  padding: 6px 8px;
  border: 1px solid var(--console-line);
  text-align: left;
  vertical-align: top;
  overflow-wrap: anywhere;
}

.nested-result-content :deep(th) {
  background: #f2f4f7;
  font-weight: 700;
}

.nested-step-title {
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 650;
}

.nested-step-meta,
.nested-step-lots {
  margin-top: 4px;
  line-height: 1.4;
}

.nested-failure-panel {
  margin-top: 8px;
  padding: 10px;
  border: 1px solid #fecaca;
  border-radius: 6px;
  background: #fff7f7;
}

.nested-failure-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.nested-failure-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #b42318;
  font-weight: 750;
}

.nested-failure-table-wrapper {
  overflow-x: auto;
}

.nested-failure-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 12px;
}

.nested-failure-table th,
.nested-failure-table td {
  padding: 7px 8px;
  border-bottom: 1px solid #fee2e2;
  text-align: left;
  vertical-align: top;
}

.nested-failure-table th {
  background: #fff1f2;
  color: #b42318;
  font-weight: 750;
}

.nested-failure-table tr:last-child td {
  border-bottom: 0;
}

.nested-failure-table p {
  margin: 0;
  color: var(--console-ink);
}

@media (max-width: 900px) {
  .nested-process-body {
    grid-template-columns: 1fr;
  }

  .nested-result-column {
    border-top: 1px solid var(--console-line-soft);
    border-left: 0;
  }
}
</style>
