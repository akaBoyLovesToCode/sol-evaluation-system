<template>
  <div>
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('evaluation.evaluationProcesses') }}</span>
          <el-button v-if="canEdit" type="primary" plain @click="openProcessDrawer">
            <template #icon><Connection /></template>
            {{ $t('evaluation.manageNestedProcesses') }}
          </el-button>
        </div>
      </template>

      <el-empty v-if="!hasBuilderSteps" :description="$t('nested.summary.empty')" />

      <div v-else class="nested-summary flex flex-col gap-3">
        <div
          v-for="process in summaryProcesses"
          :key="process.key"
          class="nested-process-summary border border-gray-200 rounded-lg p-3 bg-white"
        >
          <div class="nested-process-header flex justify-between items-center mb-2">
            <strong class="text-gray-700">{{ process.name }}</strong>
            <span class="nested-process-chain text-gray-400 text-sm">
              {{
                process.steps
                  .map((step) => stepLabelForPath(step, $t('nested.newStep')))
                  .join(' → ')
              }}
            </span>
          </div>
          <ul
            v-if="process.lots.length"
            class="nested-process-lots pl-4 text-sm text-gray-500 mb-2 list-disc"
          >
            <li v-for="lot in process.lots" :key="lot.client_id">{{ lot.label }}</li>
          </ul>
          <div
            v-for="step in process.steps"
            :key="`${process.key}-${step.order_index}`"
            class="nested-summary-item border border-gray-100 rounded p-3 bg-gray-50 mb-2"
          >
            <div class="nested-step-title font-semibold text-gray-700">
              <strong>{{ step.order_index }}. {{ step.step_code }}</strong>
              <span v-if="step.step_label"> - {{ step.step_label }}</span>
            </div>
            <div class="nested-step-meta text-sm text-gray-500 mt-1">
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
            <div class="nested-step-lots text-xs text-gray-400 mt-1">
              {{ $t('nested.summary.appliesTo') }}
              {{ describeStepLots(process, step.lot_refs) }}
            </div>
            <div
              v-if="hasFailures(step)"
              class="nested-failure-panel mt-2 p-3 border border-red-200 rounded-lg bg-red-50"
            >
              <div class="nested-failure-header flex justify-between items-center mb-2">
                <div class="nested-failure-title flex items-center gap-2 text-red-600 font-bold">
                  <el-tag size="small" type="danger" effect="dark">{{
                    $t('nested.failureTitle')
                  }}</el-tag>
                  <span class="nested-failure-count text-sm">
                    {{ $t('nested.summary.failuresCount', { count: step.failures.length }) }}
                  </span>
                </div>
              </div>
              <div class="nested-failure-table-wrapper overflow-x-auto">
                <table
                  class="nested-failure-table w-full border-collapse bg-white border border-red-200 rounded text-sm"
                >
                  <thead>
                    <tr class="bg-red-50 text-red-600">
                      <th class="p-2 text-left w-12">#</th>
                      <th class="p-2 text-left">
                        {{ $t('nested.failCode') }} / {{ $t('nested.failName') }}
                      </th>
                      <th class="p-2 text-left">{{ $t('nested.serialNumber') }}</th>
                      <th class="p-2 text-left">{{ $t('nested.analysisResult') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(failure, failureIndex) in step.failures"
                      :key="`${process.key}-${step.order_index}-${failure.sequence || failure.serial_number || failure.fail_code_text || failureIndex}`"
                      class="border-b border-gray-100 last:border-0"
                    >
                      <td class="p-2 text-red-600 font-bold">
                        #{{ failure.sequence || failureIndex + 1 }}
                      </td>
                      <td class="p-2">
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
                      <td class="p-2 min-w-[100px]">
                        <el-tag
                          v-if="failure.serial_number"
                          size="small"
                          type="info"
                          effect="plain"
                        >
                          {{ failure.serial_number }}
                        </el-tag>
                        <span v-else class="text-gray-400">—</span>
                      </td>
                      <td class="p-2 text-gray-700">
                        <p>{{ failure.analysis_result || '-' }}</p>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
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
      :before-close="handleDrawerBeforeClose"
      :title="$t('evaluation.manageNestedProcesses')"
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
.info-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
