<template>
  <div class="process-prototype">
    <el-page-header content="Process Builder Prototype" @back="handleBack" />

    <el-alert
      class="intro"
      type="info"
      :closable="false"
      title="Mock sandbox for the nested process editor"
    >
      <p>
        This page runs entirely on local state so you can explore the multi-lot workflow, step
        presets, and result-optional toggles without touching the API. Use the actions below to
        reset the payload or simulate a save cycle.
      </p>
    </el-alert>

    <div class="toolbar">
      <el-button :icon="Refresh" @click="reloadSample">Reload sample data</el-button>
      <el-button :icon="DocumentDelete" type="warning" plain @click="loadEmpty">
        Start empty
      </el-button>
      <el-button v-if="savedPayload" :icon="Delete" type="danger" plain @click="clearSaved">
        Clear saved payload
      </el-button>
      <el-tag v-if="builderDirty" type="warning">Unsaved changes</el-tag>
    </div>

    <ProcessBuilder
      ref="builderRef"
      :initial-payload="builderPayload"
      :server-warnings="builderWarnings"
      :show-save-button="true"
      @save="handleSave"
      @dirty-change="handleDirtyChange"
    />

    <el-card v-if="savedPayload" class="result-card">
      <template #header>
        <div class="card-header">
          <span>Last mock save</span>
          <el-tag v-if="savedWarnings.length" type="warning">
            {{ savedWarnings.length }} warning{{ savedWarnings.length > 1 ? 's' : '' }}
          </el-tag>
        </div>
      </template>
      <p class="result-note">
        Saves are mocked: the payload below shows what would be POSTed to
        <code>/api/evaluations/:id/processes/nested</code>.
      </p>
      <pre class="payload-preview">{{ formattedSavedPayload }}</pre>
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, DocumentDelete, Refresh } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import ProcessBuilder from '../components/ProcessBuilder.vue'
import { createEmptyBuilderPayload, normalizeBuilderPayload } from '../utils/processMapper'

const router = useRouter()
const { t } = useI18n()

const builderRef = ref(null)
const builderWarnings = ref([])
const builderDirty = ref(false)
const savedPayload = ref(null)
const savedWarnings = ref([])

const clone = (value) => JSON.parse(JSON.stringify(value ?? null))

const SAMPLE_SOURCE = {
  lots: [
    { temp_id: 'l1', lot_number: 'X0DZ000449', quantity: 27 },
    { temp_id: 'l2', lot_number: 'X0E1000449', quantity: 31 },
  ],
  steps: [
    {
      order_index: 1,
      step_code: 'M031',
      step_label: 'iARTs',
      eval_code: 'S888',
      lot_refs: ['l1', 'l2'],
      results_applicable: true,
      total_units: 58,
      total_units_manual: false,
      pass_units: 55,
      fail_units: 3,
      notes: 'Initial screening across both lots',
      failures: [
        {
          sequence: 1,
          serial_number: 'X0DZ000449-001',
          fail_code_id: null,
          fail_code_text: '3379',
          fail_code_name_snapshot: 'Write amplification spike',
          analysis_result: 'Recovered after retest',
        },
        {
          sequence: 2,
          serial_number: 'X0E1000449-015',
          fail_code_id: 42,
          fail_code_text: '3344',
          fail_code_name_snapshot: 'UECC',
          analysis_result: 'Flash block failure',
        },
        {
          sequence: 3,
          serial_number: 'X0E1000449-016',
          fail_code_id: null,
          fail_code_text: '7710',
          fail_code_name_snapshot: null,
          analysis_result: 'Controller timeout investigation pending',
        },
      ],
    },
    {
      order_index: 2,
      step_code: 'M100',
      step_label: 'Aging',
      eval_code: null,
      lot_refs: ['l2'],
      results_applicable: false,
      total_units: null,
      total_units_manual: false,
      pass_units: null,
      fail_units: null,
      notes: 'Legacy chamber data only; no discrete test results captured',
      failures: [],
    },
  ],
}

const builderPayload = ref(normalizeBuilderPayload(clone(SAMPLE_SOURCE)))

const formattedSavedPayload = computed(() =>
  savedPayload.value ? JSON.stringify(savedPayload.value, null, 2) : '',
)

function handleBack() {
  router.back()
}

function reloadSample() {
  builderWarnings.value = []
  builderPayload.value = normalizeBuilderPayload(clone(SAMPLE_SOURCE))
  nextTickMarkClean()
}

function loadEmpty() {
  builderWarnings.value = []
  builderPayload.value = normalizeBuilderPayload(createEmptyBuilderPayload())
  nextTickMarkClean()
}

function clearSaved() {
  savedPayload.value = null
  savedWarnings.value = []
}

function handleSave(payload) {
  const warnings = collectMockWarnings(payload)
  builderWarnings.value = warnings
  savedPayload.value = payload
  savedWarnings.value = warnings
  builderDirty.value = false
  builderRef.value?.markPristine(payload)
  builderRef.value?.setWarnings(warnings)
  ElMessage.success(t('nested.mockSaveComplete'))
}

function nextTickMarkClean() {
  nextTick(() => {
    builderRef.value?.setPayload(builderPayload.value, { markClean: true })
    builderDirty.value = false
    builderRef.value?.setWarnings([])
  })
}

function handleDirtyChange(value) {
  builderDirty.value = value
}

function collectMockWarnings(payload) {
  if (!payload || typeof payload !== 'object') return []

  const warnings = []
  const lotQuantityMap = new Map()
  const lots = Array.isArray(payload.lots) ? payload.lots : []
  lots.forEach((lot) => {
    const key = String(lot.temp_id || lot.client_id || lot.id || '')
    lotQuantityMap.set(key, Number(lot.quantity) || 0)
  })

  const steps = Array.isArray(payload.steps) ? payload.steps : []
  steps.forEach((step, index) => {
    if (step.results_applicable === false) {
      if (Array.isArray(step.failures) && step.failures.length) {
        warnings.push(t('nested.warnings.failuresIgnored', { index: index + 1 }))
      }
      return
    }

    const failCount = Array.isArray(step.failures) ? step.failures.length : 0
    if (typeof step.fail_units === 'number' && step.fail_units !== failCount) {
      warnings.push(t('nested.warnings.failUnitsReset', { index: index + 1, count: failCount }))
    }

    if (step.total_units_manual && Array.isArray(step.lot_refs) && step.lot_refs.length) {
      const lotSum = step.lot_refs.reduce(
        (sum, ref) => sum + (lotQuantityMap.get(String(ref)) || 0),
        0,
      )
      if (typeof step.total_units === 'number' && lotSum !== step.total_units) {
        warnings.push(
          t('nested.warnings.lotTotalMismatch', {
            index: index + 1,
            total: step.total_units,
            auto: lotSum,
          }),
        )
      }
    }
  })

  return warnings
}
</script>

<style scoped>
.process-prototype {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.intro {
  max-width: 960px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.result-card {
  max-width: 960px;
}

.result-note {
  margin-bottom: 12px;
  color: #606266;
  font-size: 13px;
}

.payload-preview {
  max-height: 360px;
  overflow: auto;
  background: #0f172a;
  color: #f1f5f9;
  padding: 16px;
  border-radius: 6px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  font-size: 13px;
}
</style>
