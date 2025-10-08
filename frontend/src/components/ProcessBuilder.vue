<template>
  <div class="process-builder">
    <el-card class="form-section">
      <template #header>
        <div class="card-header">
          <span>Process Lots</span>
          <div class="header-actions">
            <slot name="actions">
              <el-button v-if="showSaveButton" type="primary" :icon="Check" @click="emitSave">
                Save
              </el-button>
            </slot>
            <el-button v-if="!readonly" size="small" :icon="DocumentCopy" @click="openPasteLots">
              Paste List
            </el-button>
            <el-button v-if="!readonly" type="primary" size="small" :icon="Plus" @click="addLot">
              Add Lot
            </el-button>
          </div>
        </div>
      </template>
      <el-table
        v-if="processForm.lots.length"
        :data="processForm.lots"
        border
        size="small"
        class="lots-table"
      >
        <el-table-column label="#" width="60">
          <template #default="{ $index }">{{ $index + 1 }}</template>
        </el-table-column>
        <el-table-column label="Lot Number">
          <template #default="{ row }">
            <el-input
              v-model="row.lot_number"
              placeholder="Enter lot number"
              :readonly="readonly"
            />
          </template>
        </el-table-column>
        <el-table-column label="Quantity" width="180">
          <template #default="{ row }">
            <el-input-number
              v-model="row.quantity"
              :min="0"
              :step="1"
              controls-position="right"
              :disabled="readonly"
            />
          </template>
        </el-table-column>
        <el-table-column v-if="!readonly" label="Actions" width="160" align="right">
          <template #default="{ $index }">
            <div class="lots-actions">
              <el-button size="small" :icon="DocumentCopy" @click="duplicateLot($index)">
                Duplicate
              </el-button>
              <el-button size="small" type="danger" :icon="Delete" @click="removeLot($index)" />
            </div>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="Add at least one lot" />
    </el-card>

    <div class="steps-container">
      <el-card
        v-for="(step, index) in processForm.steps"
        :key="`${step.order_index}-${index}`"
        class="form-section step-card"
      >
        <template #header>
          <div class="step-header">
            <div class="step-title">
              <el-tag type="info">Step {{ index + 1 }}</el-tag>
              <span>{{ step.step_code || 'New Step' }}</span>
              <span v-if="step.step_label" class="step-label">{{ step.step_label }}</span>
            </div>
            <div v-if="!readonly" class="step-actions">
              <el-button size="small" :icon="Plus" @click="addStepAfter(index)"
                >Add After</el-button
              >
              <el-button size="small" :icon="DocumentCopy" @click="duplicateStep(index)"
                >Duplicate</el-button
              >
              <el-button size="small" :icon="Delete" type="danger" @click="removeStep(index)" />
            </div>
          </div>
        </template>

        <el-form label-position="top" class="step-form">
          <div class="step-header-row">
            <el-form-item label="Step Code" required class="header-item code-item">
              <el-select
                v-model="step.step_code"
                placeholder="Select code"
                :disabled="readonly"
                @change="(value) => handleStepCodeChange(index, value)"
              >
                <el-option
                  v-for="option in STEP_CODE_OPTIONS"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="Step Label" required class="header-item label-item">
              <el-input v-model="step.step_label" placeholder="Enter label" :readonly="readonly" />
              <el-link
                v-if="labelSuggestionAvailable(step)"
                type="primary"
                class="suggestion-link"
                :underline="false"
                @click="applyLabelSuggestion(index)"
              >
                Apply suggestion: {{ getStepLabelSuggestion(step) }}
              </el-link>
            </el-form-item>
            <el-form-item label="Eval Code" class="header-item eval-item">
              <el-input
                v-model="step.eval_code"
                placeholder="Optional eval code"
                :readonly="readonly"
              />
            </el-form-item>
            <el-form-item label="No test results" class="header-item toggle-item">
              <el-switch
                v-model="step.results_applicable"
                :active-value="false"
                :inactive-value="true"
                :disabled="readonly"
                @change="(value) => handleResultsApplicabilityChange(index, value, true)"
              />
            </el-form-item>
          </div>

          <div class="step-header-row second-row">
            <el-form-item label="Applies to lots" required class="header-item lots-item">
              <el-select
                v-model="step.lot_refs"
                multiple
                collapse-tags
                collapse-tags-tooltip
                :disabled="readonly || !processForm.lots.length"
                placeholder="Select lots"
                @change="(value) => handleLotRefsChange(index, value)"
              >
                <el-option
                  v-for="lotOption in lotOptions"
                  :key="lotOption.value"
                  :label="lotOption.label"
                  :value="lotOption.value"
                />
              </el-select>
            </el-form-item>

            <template v-if="step.results_applicable">
              <el-form-item label="Total Units" class="header-item number-item total-item">
                <div class="total-field">
                  <el-input-number
                    v-model="step.total_units"
                    :min="0"
                    :step="1"
                    controls-position="right"
                    :disabled="readonly"
                    @change="() => handleTotalUnitsInput(index)"
                  />
                  <div class="total-hint-row">
                    <span class="total-hint">{{ totalHintText(step) }}</span>
                    <template v-if="showTotalDelta(step)">
                      <el-tag size="small" type="info" class="delta-tag">{{ formatTotalDelta(step) }}</el-tag>
                      <el-link
                        v-if="!readonly"
                        type="primary"
                        :underline="false"
                        class="reset-link"
                        @click="resetTotalToComputed(index)"
                      >
                        Reset to computed
                      </el-link>
                    </template>
                  </div>
                </div>
              </el-form-item>

              <el-form-item label="Pass Units" class="header-item number-item">
                <el-input-number
                  v-model="step.pass_units"
                  :min="0"
                  :step="1"
                  controls-position="right"
                  :disabled="readonly"
                  @change="() => syncPassUnits(index)"
                />
              </el-form-item>

              <el-form-item label="Fail Units" class="header-item number-item">
                <div class="fail-field">
                  <el-input-number
                    v-model="step.fail_units"
                    :min="0"
                    :step="1"
                    controls-position="right"
                    :disabled="readonly"
                    @change="() => syncPassUnits(index)"
                  />
                  <span v-if="resultsMismatch(step)" class="inline-error"
                    >Rows {{ step.failures.length }}</span
                  >
                </div>
              </el-form-item>
            </template>
          </div>

          <el-row :gutter="12" class="step-inputs">
            <el-col :span="24">
              <el-form-item label="Notes">
                <el-input v-model="step.notes" placeholder="Optional notes" :readonly="readonly" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <el-alert
          v-if="step.results_applicable && stepMismatch(index)"
          type="warning"
          class="compact-alert"
          show-icon
          :closable="false"
          :title="`Mismatch: pass (${step.pass_units}) + fail (${step.fail_units}) !== total (${step.total_units})`"
        />

        <template v-if="step.results_applicable">
          <div class="failure-header">
            <h4>Failure Details</h4>
            <el-button v-if="!readonly" size="small" :icon="Plus" @click="addFailureRow(index)">
              Add Failure
            </el-button>
          </div>

          <el-table
            :data="step.failures"
            border
            size="small"
            class="failure-table"
            empty-text="No failure rows"
          >
            <el-table-column label="#" width="50">
              <template #default="{ row }">
                <span>{{ row.sequence }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Serial Number" min-width="160">
              <template #default="{ row }">
                <el-input v-model="row.serial_number" placeholder="Enter SN" :readonly="readonly" />
              </template>
            </el-table-column>
            <el-table-column label="Fail Code" min-width="120">
              <template #default="{ row, $index }">
                <el-autocomplete
                  v-model="row.fail_code_text"
                  class="code-input"
                  :fetch-suggestions="(query, cb) => queryFailCodes(query, cb)"
                  :trigger-on-focus="false"
                  placeholder="Fail code"
                  :disabled="readonly"
                  @select="(item) => assignFailCode(index, $index, item)"
                  @blur="() => normalizeFailCode(index, $index)"
                >
                  <template #suffix>
                    <el-tooltip
                      v-if="!row.fail_code_id && row.fail_code_text"
                      content="Not in dictionary"
                      placement="top"
                    >
                      <el-icon class="code-hint-icon"><WarningFilled /></el-icon>
                    </el-tooltip>
                  </template>
                </el-autocomplete>
              </template>
            </el-table-column>
            <el-table-column label="Fail Name" min-width="160">
              <template #default="{ row }">
                <el-input
                  v-model="row.fail_code_name_snapshot"
                  placeholder="Optional fail name"
                  :readonly="readonly"
                />
              </template>
            </el-table-column>
            <el-table-column label="Analysis Result" min-width="260">
              <template #default="{ row }">
                <el-input
                  v-model="row.analysis_result"
                  type="textarea"
                  :rows="2"
                  placeholder="Analysis details"
                  :readonly="readonly"
                />
              </template>
            </el-table-column>
            <el-table-column v-if="!readonly" width="70" fixed="right">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  :icon="Delete"
                  size="small"
                  circle
                  @click="removeFailureRow(index, $index)"
                />
              </template>
            </el-table-column>
          </el-table>
        </template>
      </el-card>

      <el-button
        v-if="!readonly"
        type="primary"
        plain
        :icon="Plus"
        @click="addStepAfter(processForm.steps.length - 1)"
      >
        Add Step
      </el-button>
    </div>

    <div v-if="validationMessages.length" class="validation-block">
      <el-alert title="Validation issues" type="warning" :closable="false" show-icon>
        <ul class="validation-list">
          <li v-for="(message, idx) in validationMessages" :key="idx">{{ message }}</li>
        </ul>
      </el-alert>
    </div>

    <div v-if="combinedWarnings.length" class="validation-block">
      <el-alert title="Warnings" type="warning" :closable="false" show-icon>
        <ul class="validation-list">
          <li v-for="(message, idx) in combinedWarnings" :key="`warning-${idx}`">{{ message }}</li>
        </ul>
      </el-alert>
    </div>

    <el-card v-if="showNormalizedPanel" class="form-section">
      <template #header>
        <div class="payload-header">
          <span>Normalized Payload</span>
          <el-button v-if="showCopyButton" size="small" :icon="DocumentCopy" @click="copyPayload"
            >Copy JSON</el-button
          >
        </div>
      </template>
      <el-alert
        v-if="!validationMessages.length"
        type="success"
        :closable="false"
        show-icon
        title="Payload currently passes validation rules"
        class="compact-alert"
      />
      <pre class="payload-preview">{{ formattedPayload }}</pre>
    </el-card>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, DocumentCopy, Plus, Check, WarningFilled } from '@element-plus/icons-vue'

const STEP_CODE_OPTIONS = [
  { label: 'M031', value: 'M031' },
  { label: 'M033', value: 'M033' },
  { label: 'M100', value: 'M100' },
  { label: 'M111', value: 'M111' },
  { label: 'M130', value: 'M130' },
  { label: 'AQL', value: 'AQL' },
  { label: 'Basic', value: 'Basic' },
]

const STEP_LABEL_SUGGESTIONS = {
  M031: 'iARTs',
  M100: 'Aging',
  M111: 'Aging',
  M130: 'LI',
}

const RESULT_OPTIONAL_CODES = new Set(['M033', 'M100'])

const toCanonicalStepCode = (code) => {
  const upper = (code || '').toString().toUpperCase()
  const option = STEP_CODE_OPTIONS.find((item) => item.value.toUpperCase() === upper)
  return option ? option.value : upper
}

const isResultOptionalCode = (code) => RESULT_OPTIONAL_CODES.has((code || '').toUpperCase())

const props = defineProps({
  initialPayload: {
    type: Object,
    default: () => ({
      lots: [],
      steps: [],
      legacy_lot_number: null,
      legacy_quantity: null,
    }),
  },
  serverWarnings: {
    type: Array,
    default: () => [],
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  showCopyButton: {
    type: Boolean,
    default: true,
  },
  showNormalizedPanel: {
    type: Boolean,
    default: true,
  },
  showSaveButton: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['save', 'dirty-change'])

const dictionaryEntries = ref([
  { id: 42, code: '3344', name: 'UECC (Uncorrectable ECC)' },
  { id: 77, code: '7710', name: 'Controller timeout' },
  { id: 88, code: '3404', name: 'Read disturb' },
  { id: 93, code: '3379', name: 'Write amplification spike' },
])

const processForm = reactive({
  lots: [],
  steps: [],
  legacy_lot_number: null,
  legacy_quantity: null,
})
const warningsFromServer = ref([])
const dirty = ref(false)
const initialSnapshot = ref('')
let initializing = false
let lotUid = 0

const generateLotKey = () => {
  lotUid += 1
  return `lot-${Date.now()}-${lotUid}`
}

const createLot = (overrides = {}) => ({
  id: overrides.id ?? null,
  temp_id: overrides.temp_id ?? null,
  client_id: overrides.client_id ?? generateLotKey(),
  lot_number: overrides.lot_number ?? '',
  quantity: overrides.quantity ?? 0,
})

const normalizeFailure = (failure, index = 0) => ({
  sequence: failure.sequence ?? index + 1,
  serial_number: failure.serial_number ?? '',
  fail_code_id: failure.fail_code_id ?? null,
  fail_code_text: (failure.fail_code_text || '').trim().toUpperCase(),
  fail_code_name_snapshot: failure.fail_code_name_snapshot ?? '',
  analysis_result: failure.analysis_result ?? '',
})

const createStep = (overrides = {}) => {
  const defaultRefs = processForm.lots.map((lot) => lot.client_id)
  const lotRefs =
    Array.isArray(overrides.lot_refs) && overrides.lot_refs.length
      ? [...new Set(overrides.lot_refs)]
      : [...defaultRefs]

  const normalizedCode = toCanonicalStepCode(overrides.step_code ?? '')
  const suggestion = STEP_LABEL_SUGGESTIONS[normalizedCode] || null
  const resultsProvided =
    overrides.results_applicable === undefined
      ? !isResultOptionalCode(normalizedCode)
      : Boolean(overrides.results_applicable)

  const step = {
    order_index: overrides.order_index ?? 1,
    step_code: normalizedCode,
    step_label: overrides.step_label ?? '',
    eval_code: overrides.eval_code ?? '',
    lot_refs: lotRefs,
    results_applicable: resultsProvided,
    total_units_manual: Boolean(overrides.total_units_manual),
    total_units:
      overrides.total_units === undefined || overrides.total_units === null
        ? null
        : Number(overrides.total_units),
    pass_units:
      overrides.pass_units === undefined || overrides.pass_units === null
        ? null
        : Number(overrides.pass_units),
    fail_units:
      overrides.fail_units === undefined || overrides.fail_units === null
        ? null
        : Number(overrides.fail_units),
    notes: overrides.notes ?? '',
    failures: (overrides.failures || []).map((failure, idx) => normalizeFailure(failure, idx)),
    __labelSuggestion: suggestion,
    __lastAppliedSuggestion: null,
    __resultsManualOverride: false,
    __userTotalTouched: Boolean(overrides.total_units_manual),
  }

  if (!step.lot_refs.length) {
    step.lot_refs = [...defaultRefs]
  }

  if (!step.step_label && suggestion) {
    step.step_label = suggestion
    step.__lastAppliedSuggestion = suggestion
  }

  if (!step.results_applicable) {
    step.total_units = null
    step.pass_units = null
    step.fail_units = 0
    step.total_units_manual = false
    step.__userTotalTouched = false
    step.failures = []
  } else {
    if (step.fail_units === null) {
      step.fail_units = step.failures.length
    }
    if (step.pass_units === null && step.total_units !== null && step.fail_units !== null) {
      step.pass_units = Math.max(Number(step.total_units) - Number(step.fail_units), 0)
    }
  }

  return step
}

const clonePayload = (payload) => JSON.parse(JSON.stringify(payload || {}))

function applyPayload(payload) {
  const cloned = clonePayload(payload)

  processForm.legacy_lot_number = cloned.legacy_lot_number ?? null
  processForm.legacy_quantity = cloned.legacy_quantity ?? null

  processForm.lots.splice(0, processForm.lots.length)
  const incomingLots = Array.isArray(cloned.lots) ? cloned.lots : []
  if (incomingLots.length) {
    incomingLots.forEach((lot) => {
      const client_id = String(lot.client_id || lot.temp_id || lot.id || generateLotKey())
      processForm.lots.push(
        createLot({
          id: lot.id ?? null,
          temp_id: lot.temp_id ?? client_id,
          client_id,
          lot_number: lot.lot_number || '',
          quantity: Number(lot.quantity) || 0,
        }),
      )
    })
  }
  if (!processForm.lots.length) {
    processForm.lots.push(createLot({}))
  }

  const lotRefMap = new Map()
  processForm.lots.forEach((lot) => {
    lotRefMap.set(String(lot.client_id), lot.client_id)
    if (lot.temp_id) {
      lotRefMap.set(String(lot.temp_id), lot.client_id)
    }
    if (lot.id !== null && lot.id !== undefined) {
      lotRefMap.set(String(lot.id), lot.client_id)
    }
  })

  processForm.steps.splice(0, processForm.steps.length)
  const incomingSteps = Array.isArray(cloned.steps) ? cloned.steps : []
  if (incomingSteps.length) {
    incomingSteps.forEach((step, index) => {
      const mappedRefs = Array.isArray(step.lot_refs)
        ? step.lot_refs.map((ref) => lotRefMap.get(String(ref)) || null).filter(Boolean)
        : []
      const createdStep = createStep({
        ...step,
        lot_refs: mappedRefs,
        order_index: step.order_index ?? index + 1,
      })
      processForm.steps.push(createdStep)
      handleStepCodeChange(processForm.steps.length - 1, createdStep.step_code, { initial: true })
    })
  } else {
    const createdStep = createStep({ order_index: 1 })
    processForm.steps.push(createdStep)
    handleStepCodeChange(0, createdStep.step_code, { initial: true })
  }

  ensureStepLotRefs()
  reindexSteps()
  refreshAllStepTotals()
}

function setPayload(payload, { markClean = false } = {}) {
  initializing = true
  applyPayload(payload)
  warningsFromServer.value = []
  const normalized = normalizeCurrentState()
  if (markClean) {
    markPristine(normalized)
  } else {
    dirty.value = false
    emit('dirty-change', dirty.value)
  }
  initializing = false
}

onMounted(() => {
  setPayload(props.initialPayload, { markClean: true })
})

watch(
  () => props.initialPayload,
  (newPayload) => {
    setPayload(newPayload, { markClean: true })
  },
  { deep: true },
)

watch(
  () => props.serverWarnings,
  (warnings) => {
    warningsFromServer.value = Array.isArray(warnings) ? [...warnings] : []
  },
  { deep: true, immediate: true },
)

const dictionaryIndex = computed(() => {
  const index = new Map()
  dictionaryEntries.value.forEach((entry) => {
    index.set(entry.code.toUpperCase(), entry)
  })
  return index
})

const stepMismatch = (index) => {
  const step = processForm.steps[index]
  if (!step || !step.results_applicable) return false
  if (step.total_units === null || step.pass_units === null || step.fail_units === null) {
    return false
  }
  const total = Number(step.total_units) || 0
  const passUnits = Number(step.pass_units) || 0
  const failUnits = Number(step.fail_units) || 0
  return total !== passUnits + failUnits
}

function ensureStepLotRefs() {
  const availableIds = processForm.lots.map((lot) => lot.client_id)
  if (!availableIds.length) {
    processForm.steps.forEach((step, idx) => {
      step.lot_refs = []
      refreshTotalsForStep(idx)
    })
    return
  }
  processForm.steps.forEach((step, idx) => {
    if (!Array.isArray(step.lot_refs)) {
      step.lot_refs = []
    }
    step.lot_refs = step.lot_refs.filter((ref) => availableIds.includes(ref))
    if (!step.lot_refs.length) {
      step.lot_refs = [...availableIds]
    }
    refreshTotalsForStep(idx)
  })
}

watch(
  () => processForm.lots.map((lot) => lot.client_id),
  (newIds, oldIds) => {
    if (!oldIds || newIds.length < oldIds.length) {
      ensureStepLotRefs()
    }
    refreshAllStepTotals()
  },
)

watch(
  () => processForm.lots.map((lot) => `${lot.client_id}:${Number(lot.quantity) || 0}`),
  () => {
    refreshAllStepTotals()
  },
  { deep: true },
)

const lotOptions = computed(() =>
  processForm.lots.map((lot) => ({
    value: lot.client_id,
    label: lot.lot_number
      ? `${lot.lot_number}${lot.quantity ? ` (${lot.quantity})` : ''}`
      : 'Unnamed lot',
  })),
)

const lotQuantityMap = computed(() => {
  const map = new Map()
  processForm.lots.forEach((lot) => {
    map.set(lot.client_id, Number(lot.quantity) || 0)
  })
  return map
})

function lotQuantitiesForStep(step) {
  if (!step || !Array.isArray(step.lot_refs)) {
    return []
  }
  return step.lot_refs.map((ref) => Number(lotQuantityMap.value.get(ref)) || 0)
}

function autoTotalForStep(step) {
  const quantities = lotQuantitiesForStep(step)
  return quantities.reduce((sum, value) => sum + value, 0)
}

function getTotalDelta(step) {
  if (!step || !step.results_applicable || step.total_units === null) {
    return 0
  }
  const total = Number(step.total_units ?? 0)
  const auto = autoTotalForStep(step)
  return total - auto
}

function totalHintText(step) {
  if (!step || !step.results_applicable) {
    return 'from lots: —'
  }
  const values = lotQuantitiesForStep(step)
  if (!values.length) {
    return 'from lots: —'
  }
  const total = values.reduce((sum, val) => sum + val, 0)
  if (values.length > 1) {
    return `from lots: ${values.join(' + ')} = ${total}`
  }
  return `from lots: ${total}`
}

function showTotalDelta(step) {
  return step && step.results_applicable && step.total_units !== null && getTotalDelta(step) !== 0
}

function formatTotalDelta(step) {
  const delta = getTotalDelta(step)
  if (!delta) return 'Δ 0'
  const prefix = delta > 0 ? '+' : ''
  return `Δ ${prefix}${delta}`
}

function refreshTotalsForStep(index) {
  const step = processForm.steps[index]
  if (!step) return
  if (!step.results_applicable) {
    step.total_units = null
    step.pass_units = null
    step.fail_units = 0
    step.total_units_manual = false
    step.__userTotalTouched = false
    return
  }

  const autoTotal = autoTotalForStep(step)
  if (step.total_units === null || step.total_units === undefined) {
    step.total_units = autoTotal
    step.__userTotalTouched = false
  } else if (!step.__userTotalTouched && Number(step.total_units) !== autoTotal) {
    step.total_units = autoTotal
  } else if (step.__userTotalTouched && Number(step.total_units) === autoTotal) {
    step.__userTotalTouched = false
  }

  if (step.fail_units === null || Number.isNaN(Number(step.fail_units))) {
    step.fail_units = step.failures.length
  }

  const total = Number(step.total_units ?? 0)
  const fail = Number(step.fail_units ?? 0)
  step.pass_units = Math.max(total - fail, 0)
  updateManualState(index, autoTotal)
}

function refreshAllStepTotals() {
  processForm.steps.forEach((_, idx) => refreshTotalsForStep(idx))
}

function syncPassUnits(index) {
  const step = processForm.steps[index]
  if (!step || !step.results_applicable) return
  if (step.fail_units === null) {
    step.fail_units = step.failures.length
  }
  const total = Number(step.total_units ?? 0)
  const fail = Number(step.fail_units ?? 0)
  step.pass_units = Math.max(total - fail, 0)
  updateManualState(index)
}

function updateManualState(index, providedAutoTotal) {
  const step = processForm.steps[index]
  if (!step) return
  if (!step.results_applicable) {
    step.total_units_manual = false
    step.__userTotalTouched = false
    return
  }
  const auto = providedAutoTotal ?? autoTotalForStep(step)
  if (step.total_units === null || step.total_units === undefined) {
    step.total_units_manual = false
    step.__userTotalTouched = false
    return
  }
  const manual = Number(step.total_units ?? 0) !== auto
  step.total_units_manual = manual
  if (!manual) {
    step.__userTotalTouched = false
  }
}

function handleTotalUnitsInput(index) {
  const step = processForm.steps[index]
  if (!step || !step.results_applicable) return
  step.__userTotalTouched = true
  if (step.total_units === null || step.total_units === undefined) {
    step.total_units = 0
  }
  syncPassUnits(index)
}

function resetTotalToComputed(index) {
  const step = processForm.steps[index]
  if (!step || !step.results_applicable) return
  const auto = autoTotalForStep(step)
  step.total_units = auto
  step.__userTotalTouched = false
  syncPassUnits(index)
}

function resultsMismatch(step) {
  if (!step || !step.results_applicable) return false
  const failCount = step.failures.length
  const failUnits = Number(step.fail_units ?? 0)
  return failUnits !== failCount
}

function getStepLabelSuggestion(step) {
  if (!step) return null
  return STEP_LABEL_SUGGESTIONS[step.step_code] || null
}

function labelSuggestionAvailable(step) {
  const suggestion = getStepLabelSuggestion(step)
  if (!suggestion) return false
  const current = (step.step_label || '').trim()
  return current !== suggestion
}

function applyLabelSuggestion(index) {
  const step = processForm.steps[index]
  if (!step) return
  const suggestion = getStepLabelSuggestion(step)
  if (!suggestion) return
  step.step_label = suggestion
  step.__lastAppliedSuggestion = suggestion
}

function handleLotRefsChange(index) {
  const step = processForm.steps[index]
  if (!step) return
  if (!Array.isArray(step.lot_refs) || !step.lot_refs.length) {
    step.total_units = 0
    step.__userTotalTouched = false
  }
  refreshTotalsForStep(index)
}

function setResultsApplicability(index, isApplicable, options = {}) {
  const step = processForm.steps[index]
  if (!step) return
  const value = Boolean(isApplicable)
  step.results_applicable = value
  if (options.manual) {
    step.__resultsManualOverride = true
  } else if (options.resetManual) {
    step.__resultsManualOverride = false
  }

  if (!value) {
    step.total_units = null
    step.pass_units = null
    step.fail_units = 0
    step.total_units_manual = false
    step.__userTotalTouched = false
    step.failures = []
  } else {
    if (step.total_units === null || step.total_units === undefined || !step.__userTotalTouched) {
      step.total_units = autoTotalForStep(step)
      step.__userTotalTouched = false
    }
    if (step.fail_units === null) {
      step.fail_units = step.failures.length
    }
  }

  refreshTotalsForStep(index)
}

function handleResultsApplicabilityChange(index, value, manualChange = false) {
  setResultsApplicability(index, value, { manual: manualChange })
  refreshTotalsForStep(index)
}

function handleStepCodeChange(index, value, options = {}) {
  const step = processForm.steps[index]
  if (!step) return
  const canonical = toCanonicalStepCode(value)
  step.step_code = canonical

  const suggestion = STEP_LABEL_SUGGESTIONS[canonical] || null
  step.__labelSuggestion = suggestion

  const currentLabel = (step.step_label || '').trim()
  if (
    suggestion &&
    (!currentLabel || currentLabel === step.__lastAppliedSuggestion || options.forceSuggestion)
  ) {
    step.step_label = suggestion
    step.__lastAppliedSuggestion = suggestion
  }

  if (
    !suggestion &&
    step.__lastAppliedSuggestion &&
    currentLabel === step.__lastAppliedSuggestion
  ) {
    step.__lastAppliedSuggestion = null
  }

  if (!options.initial) {
    if (!step.__resultsManualOverride) {
      if (isResultOptionalCode(canonical)) {
        setResultsApplicability(index, false, { resetManual: true })
      } else {
        setResultsApplicability(index, true, { resetManual: true })
      }
    } else if (!isResultOptionalCode(canonical) && !step.results_applicable) {
      setResultsApplicability(index, true)
    } else {
      refreshTotalsForStep(index)
    }
  } else {
    refreshTotalsForStep(index)
  }
}

const addStepAfter = (index) => {
  const insertIndex = Number.isInteger(index) && index >= 0 ? index + 1 : processForm.steps.length
  const newStep = createStep({ order_index: insertIndex + 1 })
  processForm.steps.splice(insertIndex, 0, newStep)
  reindexSteps()
  ensureStepLotRefs()
  handleStepCodeChange(insertIndex, newStep.step_code, { initial: true })
  refreshTotalsForStep(insertIndex)
}

const duplicateStep = (index) => {
  const source = processForm.steps[index]
  const duplicatePayload = clonePayload({
    order_index: source.order_index,
    step_code: source.step_code,
    step_label: source.step_label,
    eval_code: source.eval_code,
    lot_refs: source.lot_refs,
    results_applicable: source.results_applicable,
    total_units: source.total_units,
    pass_units: source.pass_units,
    fail_units: source.fail_units,
    notes: source.notes,
    failures: source.failures,
  })
  const duplicate = createStep(duplicatePayload)
  processForm.steps.splice(index + 1, 0, duplicate)
  reindexSteps()
  ensureStepLotRefs()
  handleStepCodeChange(index + 1, duplicate.step_code, { initial: true })
  refreshTotalsForStep(index + 1)
}

const removeStep = (index) => {
  if (processForm.steps.length === 1) {
    ElMessage.warning('At least one step is required')
    return
  }
  processForm.steps.splice(index, 1)
  reindexSteps()
  ensureStepLotRefs()
  refreshAllStepTotals()
}

const addFailureRow = (stepIndex) => {
  const step = processForm.steps[stepIndex]
  if (!step) return
  step.failures.push({
    sequence: step.failures.length + 1,
    serial_number: '',
    fail_code_id: null,
    fail_code_text: '',
    fail_code_name_snapshot: '',
    analysis_result: '',
  })
  step.fail_units = step.failures.length
  reindexSteps()
  syncPassUnits(stepIndex)
}

const removeFailureRow = (stepIndex, failureIndex) => {
  const step = processForm.steps[stepIndex]
  if (!step) return
  step.failures.splice(failureIndex, 1)
  reindexSteps()
  step.fail_units = step.failures.length
  syncPassUnits(stepIndex)
}

const queryFailCodes = (queryString, cb) => {
  const normalized = (queryString || '').trim().toUpperCase()
  let results = dictionaryEntries.value
  if (normalized) {
    results = results.filter(
      (entry) => entry.code.includes(normalized) || entry.name?.toUpperCase().includes(normalized),
    )
  }
  cb(results.map((entry) => ({ value: entry.code, ...entry })))
}

const assignFailCode = (stepIndex, failureIndex, item) => {
  const step = processForm.steps[stepIndex]
  if (!step) return
  const failure = step.failures[failureIndex]
  if (!failure) return
  failure.fail_code_text = item.code
  failure.fail_code_id = item.id
  failure.fail_code_name_snapshot = item.name ?? ''
}

const normalizeFailCode = (stepIndex, failureIndex) => {
  const step = processForm.steps[stepIndex]
  if (!step) return
  const failure = step.failures[failureIndex]
  if (!failure) return
  const code = failure.fail_code_text?.trim().toUpperCase()
  if (!code) {
    failure.fail_code_text = ''
    failure.fail_code_id = null
    failure.fail_code_name_snapshot = ''
    return
  }

  failure.fail_code_text = code
  const match = dictionaryIndex.value.get(code)
  if (match) {
    failure.fail_code_id = match.id
    failure.fail_code_name_snapshot = match.name ?? ''
  } else {
    failure.fail_code_id = null
  }
}

function addLot() {
  processForm.lots.push(createLot({}))
  ensureStepLotRefs()
}

function duplicateLot(index) {
  const original = processForm.lots[index]
  if (!original) return
  processForm.lots.splice(
    index + 1,
    0,
    createLot({ lot_number: original.lot_number, quantity: original.quantity }),
  )
  ensureStepLotRefs()
}

function removeLot(index) {
  if (processForm.lots.length <= 1) {
    ElMessage.warning('At least one lot is required')
    return
  }
  processForm.lots.splice(index, 1)
  ensureStepLotRefs()
}

async function openPasteLots() {
  try {
    const result = await ElMessageBox.prompt(
      'Enter one lot per line. Use "LOT123,27" or "LOT123 27" to include quantities.',
      'Paste Lots',
      {
        confirmButtonText: 'Apply',
        cancelButtonText: 'Cancel',
        inputType: 'textarea',
        inputPlaceholder: 'LOT123,27\nLOT124,31',
      },
    )

    const raw = result?.value || ''
    if (!raw.trim()) return

    const lines = raw
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)

    const newLots = lines.map((line) => {
      let lotNumber = line
      let quantity = 0
      const match = line.match(/(.+?)[,\s]+(\d+)$/)
      if (match) {
        lotNumber = match[1].trim()
        quantity = Number(match[2]) || 0
      }
      return createLot({ lot_number: lotNumber, quantity })
    })

    newLots.forEach((lot) => processForm.lots.push(lot))
    ensureStepLotRefs()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    console.error('Failed to paste lots', error)
  }
}

function reindexSteps() {
  processForm.steps.forEach((step, stepIdx) => {
    step.order_index = stepIdx + 1
    step.failures.forEach((failure, failureIdx) => {
      failure.sequence = failureIdx + 1
    })
    if (step.results_applicable) {
      step.fail_units = step.failures.length
    }
    refreshTotalsForStep(stepIdx)
  })
}

const validationMessages = computed(() => {
  const messages = []

  if (!processForm.lots.length) {
    messages.push('Add at least one lot before saving')
  }

  processForm.lots.forEach((lot, index) => {
    if (!lot.lot_number?.trim()) {
      messages.push(`Lot ${index + 1}: lot number is required`)
    }
    if (Number(lot.quantity) <= 0) {
      messages.push(`Lot ${index + 1}: quantity must be greater than zero`)
    }
  })

  if (!processForm.steps.length) {
    messages.push('At least one process step is required')
  }

  processForm.steps.forEach((step, index) => {
    if (!step.step_code?.trim()) {
      messages.push(`Step ${index + 1}: step code is required`)
    }
    if (!step.step_label?.trim()) {
      messages.push(`Step ${index + 1}: step label is required`)
    }
    if (!Array.isArray(step.lot_refs) || !step.lot_refs.length) {
      messages.push(`Step ${index + 1}: select at least one lot`)
    }
    if (step.results_applicable) {
      if (stepMismatch(index)) {
        messages.push(`Step ${index + 1}: pass + fail must equal total units`)
      }
      if (
        step.total_units !== null &&
        Number(step.total_units ?? 0) < Number(step.fail_units ?? 0)
      ) {
        messages.push(`Step ${index + 1}: total units must be greater than or equal to fail units`)
      }
      if (Number(step.fail_units ?? 0) !== step.failures.length) {
        messages.push(`Step ${index + 1}: fail units must match number of failure rows`)
      }
      step.failures.forEach((failure, failureIndex) => {
        if (!failure.fail_code_text?.trim()) {
          messages.push(`Step ${index + 1}, failure ${failureIndex + 1}: fail code is required`)
        }
      })
    } else {
      if (step.failures.length) {
        messages.push(`Step ${index + 1}: remove failure rows when no test results`)
      }
    }
  })

  return messages
})

function normalizeCurrentState() {
  const normalizedLots = []
  const lotIdMap = new Map()
  const lotQuantityLookup = new Map()

  processForm.lots.forEach((lot) => {
    const tempId = String(lot.temp_id || lot.client_id)
    normalizedLots.push({
      id: lot.id ?? undefined,
      temp_id: tempId,
      client_id: lot.client_id,
      lot_number: lot.lot_number?.trim() || '',
      quantity: Number(lot.quantity) || 0,
    })
    lotIdMap.set(lot.client_id, tempId)
    lotQuantityLookup.set(tempId, Number(lot.quantity) || 0)
  })

  const normalizedSteps = processForm.steps.map((step, index) => {
    const normalizedLotRefs = Array.isArray(step.lot_refs)
      ? step.lot_refs
          .map((ref) => lotIdMap.get(ref) || lotIdMap.get(String(ref)) || null)
          .filter(Boolean)
      : []

    const resultsApplicable = step.results_applicable !== false
    const autoTotal = resultsApplicable
      ? normalizedLotRefs.reduce((sum, ref) => sum + (lotQuantityLookup.get(ref) || 0), 0)
      : 0
    const normalizedTotal = resultsApplicable
      ? step.total_units === null || step.total_units === undefined
        ? null
        : Number(step.total_units)
      : null
    const normalizedFail = resultsApplicable
      ? step.fail_units === null || step.fail_units === undefined
        ? null
        : Number(step.fail_units)
      : null
    const normalizedPass = resultsApplicable
      ? step.pass_units === null || step.pass_units === undefined
        ? null
      : Number(step.pass_units)
      : null

    const normalizedEval = step.eval_code?.trim()

    return {
      order_index: step.order_index ?? index + 1,
      step_code: step.step_code?.trim().toUpperCase() ?? '',
      step_label: step.step_label?.trim() || '',
      eval_code: normalizedEval ? normalizedEval : null,
      lot_refs: normalizedLotRefs,
      results_applicable: resultsApplicable,
      total_units: normalizedTotal,
      total_units_manual:
        resultsApplicable && normalizedTotal !== null
          ? normalizedTotal !== autoTotal
          : false,
      pass_units: normalizedPass,
      fail_units: normalizedFail,
      notes: step.notes?.trim() || undefined,
      failures: resultsApplicable
        ? step.failures.map((failure) => ({
            sequence: failure.sequence,
            serial_number: failure.serial_number?.trim() || undefined,
            fail_code_id: failure.fail_code_id ?? undefined,
            fail_code_text: failure.fail_code_text?.trim().toUpperCase() ?? '',
            fail_code_name_snapshot: failure.fail_code_name_snapshot?.trim() || undefined,
            analysis_result: failure.analysis_result?.trim() || undefined,
          }))
        : [],
    }
  })

  return {
    lots: normalizedLots,
    steps: normalizedSteps,
    legacy_lot_number: processForm.legacy_lot_number ?? null,
    legacy_quantity: processForm.legacy_quantity ?? null,
  }
}

const normalizedPayload = computed(() => normalizeCurrentState())

const lotTotalsWarnings = computed(() => {
  const warnings = []
  processForm.steps.forEach((step, index) => {
    if (!step.results_applicable) {
      return
    }
    if (!Array.isArray(step.lot_refs) || !step.lot_refs.length) {
      return
    }
    const delta = getTotalDelta(step)
    if (delta !== 0 && step.total_units !== null) {
      const autoValue = autoTotalForStep(step)
      const totalUnits = Number(step.total_units ?? 0)
      warnings.push(
        `Step ${index + 1}: total units ${totalUnits} differ from selected lot quantity sum ${autoValue}`,
      )
    }
  })
  return warnings
})

const combinedWarnings = computed(() => [...warningsFromServer.value, ...lotTotalsWarnings.value])

watch(
  () => JSON.stringify(normalizedPayload.value),
  (newVal) => {
    if (initializing) {
      return
    }
    const snapshot = initialSnapshot.value
    dirty.value = snapshot !== newVal
    emit('dirty-change', dirty.value)
  },
)

const formattedPayload = computed(() => JSON.stringify(normalizedPayload.value, null, 2))

const copyPayload = async () => {
  try {
    await navigator.clipboard.writeText(formattedPayload.value)
    ElMessage.success('Payload copied to clipboard')
  } catch (error) {
    ElMessage.error('Unable to copy payload')
    console.error(error)
  }
}

function markPristine(snapshot) {
  const source = snapshot ?? normalizeCurrentState()
  initialSnapshot.value = JSON.stringify(source)
  dirty.value = false
  emit('dirty-change', false)
}

const emitSave = () => {
  emit('save', normalizedPayload.value)
}

defineExpose({
  getPayload: () => normalizedPayload.value,
  setPayload,
  markPristine,
  isDirty: () => dirty.value,
  hasSteps: () => processForm.steps.length > 0,
  setWarnings: (warnings) => {
    warningsFromServer.value = Array.isArray(warnings) ? [...warnings] : []
  },
})
</script>

<style scoped>
.process-builder {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.summary-form,
.step-form {
  width: 100%;
}

.summary-form :deep(.el-form-item),
.step-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-card {
  border-left: 4px solid #409eff;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
}

.step-label {
  color: #909399;
  font-size: 13px;
}

.step-actions {
  display: flex;
  gap: 8px;
}

.step-header-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.step-header-row .header-item {
  flex: 1 1 200px;
}

.step-header-row.second-row .number-item {
  flex: 1 1 160px;
}

.total-item {
  flex: 1 1 200px;
}

.step-header-row.second-row .lots-item {
  flex: 2 1 320px;
}

.step-header-row .toggle-item {
  flex: 0 1 160px;
  display: flex;
  align-items: flex-end;
}

.label-item {
  position: relative;
}

.suggestion-link {
  display: inline-flex;
  margin-top: 4px;
  font-size: 12px;
}

.total-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.total-hint-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.total-hint {
  white-space: nowrap;
}

.delta-tag {
  font-size: 11px;
}

.reset-link {
  font-size: 12px;
}

.number-item :deep(.el-input-number),
.lots-item :deep(.el-select),
.eval-item :deep(.el-input) {
  width: 100%;
}

.fail-field {
  display: flex;
  align-items: center;
  gap: 8px;
}

.inline-error {
  font-size: 12px;
  color: #f56c6c;
}

.code-hint-icon {
  color: #e6a23c;
}

.code-input {
  width: 100%;
}

.failure-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0 8px;
}

.failure-table {
  margin-bottom: 8px;
}

.validation-block {
  margin-top: 16px;
}

.validation-list {
  margin: 8px 0 0;
  padding-left: 16px;
}

.payload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.payload-preview {
  margin: 0;
  padding: 16px;
  background: #121417;
  color: #f7f7f7;
  border-radius: 8px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  font-size: 12px;
  line-height: 1.4;
  overflow: auto;
}

.compact-alert {
  margin-bottom: 12px;
}
</style>
