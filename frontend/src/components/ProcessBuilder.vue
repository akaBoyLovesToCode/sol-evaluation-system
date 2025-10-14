<template>
  <div class="process-builder">
    <div v-if="processSummary" class="process-summary">
      <span class="summary-label">{{ $t('nested.processSummary') }}</span>
      <span class="summary-content">{{ processSummary }}</span>
    </div>

    <div class="builder-actions">
      <slot name="actions">
        <el-button v-if="showSaveButton" type="primary" @click="emitSave">
          <template #icon><Check /></template>
          {{ t('common.save') }}
        </el-button>
      </slot>
    </div>

    <div v-if="!readonly" class="process-toolbar">
      <el-button type="primary" @click="addProcess">
        <template #icon><Plus /></template>
        {{ $t('nested.addProcess') }}
      </el-button>
      <el-button :disabled="!currentProcess" @click="duplicateProcess(activeProcessIndex)">
        <template #icon><DocumentCopy /></template>
        {{ $t('nested.duplicateProcess') }}
      </el-button>
    </div>

    <div class="process-list">
      <div
        v-for="(process, pIndex) in processForm.processes"
        :key="process.key"
        class="process-panel"
        :class="{ active: pIndex === activeProcessIndex }"
        draggable="!readonly"
        @dragstart="onProcessDragStart(pIndex)"
        @dragover.prevent
        @drop="onProcessDrop(pIndex)"
        @click="setActiveProcess(pIndex)"
      >
        <div class="process-header">
          <div class="process-title">
            <el-tag size="small" type="info">{{ $t('nested.processTag') }} {{ pIndex + 1 }}</el-tag>
            <el-input
              v-model="process.name"
              class="process-name-input"
              :placeholder="$t('nested.processNamePlaceholder')"
              :readonly="readonly"
            />
          </div>
          <div v-if="!readonly" class="process-actions">
            <el-button text @click.stop="toggleCollapse(pIndex)">
              <template #icon>
                <component :is="isCollapsed(pIndex) ? 'ArrowDown' : 'ArrowUp'" />
              </template>
              {{ isCollapsed(pIndex) ? $t('nested.expand') : $t('nested.collapse') }}
            </el-button>
            <el-button text @click.stop="duplicateProcess(pIndex)">
              <template #icon><DocumentCopy /></template>
              {{ $t('nested.duplicateProcess') }}
            </el-button>
            <el-button text type="danger" @click.stop="removeProcess(pIndex)">
              <template #icon><Delete /></template>
              {{ $t('nested.deleteProcess') }}
            </el-button>
          </div>
        </div>

        <transition name="fade">
          <div v-show="!collapsedProcesses.has(process.key)" class="process-body">
            <process-lots
              :process-index="pIndex"
              :process="process"
              :readonly="readonly"
              :t="t"
              @add-lot="addLot"
              @duplicate-lot="duplicateLot"
              @remove-lot="removeLot"
              @paste-lots="openPasteLots"
            />

            <div class="steps-container">
              <step-card
                v-for="(step, sIndex) in process.steps"
                :key="step.__uid"
                :process-index="pIndex"
                :step-index="sIndex"
                :process="process"
                :step="step"
                :readonly="readonly"
                :dictionary-entries="dictionaryEntries.value"
                :label-suggestions="STEP_LABEL_SUGGESTIONS"
                :step-code-options="STEP_CODE_OPTIONS"
                :lot-options="lotOptions(process)"
                :t="t"
                @add-step="addStepAfter"
                @duplicate-step="duplicateStep"
                @remove-step="removeStep"
                @add-failure="addFailureRow"
                @remove-failure="removeFailureRow"
                @assign-fail-code="assignFailCode"
                @normalize-fail-code="normalizeFailCode"
                @total-input="handleTotalUnitsInput"
                @lot-change="handleLotRefsChange"
                @code-change="handleStepCodeChange"
                @results-change="handleResultsApplicabilityChange"
                @fail-units-change="syncPassUnits"
                @apply-suggestion="applyLabelSuggestion"
              />

              <el-button
                v-if="!readonly"
                type="primary"
                plain
                class="add-step-button"
                @click="addStepAfter(pIndex, process.steps.length - 1)"
              >
                <template #icon><Plus /></template>
                {{ $t('nested.addStep') }}
              </el-button>
            </div>
          </div>
        </transition>
      </div>
      <el-empty v-if="!processForm.processes.length" :description="$t('nested.noProcess')" />
    </div>

    <div v-if="validationMessages.length" class="validation-block">
      <el-alert :title="$t('nested.validationTitle')" type="warning" :closable="false" show-icon>
        <ul class="validation-list">
          <li v-for="(message, idx) in validationMessages" :key="idx">{{ message }}</li>
        </ul>
      </el-alert>
    </div>

    <div v-if="combinedWarnings.length" class="validation-block">
      <el-alert :title="$t('nested.warningTitle')" type="warning" :closable="false" show-icon>
        <ul class="validation-list">
          <li v-for="(message, idx) in combinedWarnings" :key="`warning-${idx}`">{{ message }}</li>
        </ul>
      </el-alert>
    </div>

    <el-card v-if="showDebug" class="form-section">
      <template #header>
        <div class="payload-header">
          <span>{{ $t('nested.debugPayload') }}</span>
          <el-button size="small" @click="copyPayload">
            <template #icon><DocumentCopy /></template>
            {{ $t('nested.copyPayload') }}
          </el-button>
        </div>
      </template>
      <el-alert
        v-if="!validationMessages.length"
        type="success"
        :closable="false"
        show-icon
        :title="$t('nested.payloadValid')"
        class="compact-alert"
      />
      <pre class="payload-preview">{{ formattedPayload }}</pre>
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProcessLots from './ProcessLots.vue'
import StepCard from './StepCard.vue'

const { t } = useI18n()

const STEP_CODE_OPTIONS = [
  { label: 'M010', value: 'M010' },
  { label: 'M031', value: 'M031' },
  { label: 'M033', value: 'M033' },
  { label: 'M100', value: 'M100' },
  { label: 'M111', value: 'M111' },
  { label: 'M130', value: 'M130' },
  { label: 'AQL', value: 'AQL' },
  { label: 'Basic', value: 'Basic' },
]

const STEP_LABEL_SUGGESTIONS = {
  M010: 'SMT',
  M031: 'iARTs',
  M033: 'Router',
  M100: 'Aging',
  M111: 'Aging',
  M130: 'LI',
}

const RESULT_OPTIONAL_CODES = new Set(['M010', 'M033', 'M100'])

const props = defineProps({
  initialPayload: {
    type: Object,
    default: () => ({ processes: [] }),
  },
  serverWarnings: {
    type: Array,
    default: () => [],
  },
  readonly: {
    type: Boolean,
    default: false,
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
  processes: [],
  legacy_lot_number: null,
  legacy_quantity: null,
})

const collapsedProcesses = reactive(new Set())
const activeProcessIndex = ref(0)

const warningsFromServer = ref([])
const dirty = ref(false)
const initialSnapshot = ref('')
let initializing = false
let processCounter = 0
let lotUid = 0
let stepUid = 0

const draggingData = {
  index: -1,
}

function generateProcessKey() {
  processCounter += 1
  return `proc_${Date.now()}_${processCounter}`
}

function generateLotClientId(processKey) {
  lotUid += 1
  return `${processKey || 'proc'}_lot_${Date.now()}_${lotUid}`
}

function createLot(overrides = {}, processKey) {
  const clientId = overrides.client_id || generateLotClientId(processKey)
  return {
    id: overrides.id ?? null,
    temp_id: overrides.temp_id ?? clientId,
    client_id: clientId,
    lot_number: overrides.lot_number ?? '',
    quantity: Number(overrides.quantity ?? 0),
  }
}

function normalizeFailure(failure, index = 0) {
  return {
    sequence: failure.sequence ?? index + 1,
    serial_number: failure.serial_number ?? '',
    fail_code_id: failure.fail_code_id ?? null,
    fail_code_text: (failure.fail_code_text || '').trim().toUpperCase(),
    fail_code_name_snapshot: failure.fail_code_name_snapshot ?? '',
    analysis_result: failure.analysis_result ?? '',
  }
}

function toCanonicalStepCode(code) {
  const upper = (code || '').toString().toUpperCase()
  const option = STEP_CODE_OPTIONS.find((item) => item.value.toUpperCase() === upper)
  return option ? option.value : upper
}

function isResultOptionalCode(code) {
  return RESULT_OPTIONAL_CODES.has((code || '').toUpperCase())
}

function createStep(process, overrides = {}) {
  const normalizedCode = toCanonicalStepCode(overrides.step_code ?? '')
  const suggestion = STEP_LABEL_SUGGESTIONS[normalizedCode] || null
  const resultsProvided =
    overrides.results_applicable === undefined
      ? !isResultOptionalCode(normalizedCode)
      : Boolean(overrides.results_applicable)

  const lotClientIds = process.lots.map((lot) => lot.client_id)
  const providedRefs = Array.isArray(overrides.lot_refs) ? overrides.lot_refs.filter(Boolean) : []
  const uniqueRefs = providedRefs.length ? [...new Set(providedRefs)] : [...lotClientIds]

  const step = {
    __uid: overrides.__uid || `step-${Date.now()}-${stepUid++}`,
    order_index: overrides.order_index ?? process.steps.length + 1,
    step_code: normalizedCode,
    step_label: overrides.step_label ?? '',
    eval_code: overrides.eval_code ?? '',
    lot_refs: uniqueRefs,
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
    __lastAppliedSuggestion: overrides.__lastAppliedSuggestion ?? null,
    __resultsManualOverride: Boolean(overrides.__resultsManualOverride),
    __userTotalTouched: Boolean(overrides.__userTotalTouched),
  }

  if (!step.step_label && suggestion) {
    step.step_label = suggestion
    step.__lastAppliedSuggestion = suggestion
  }

  if (!step.results_applicable) {
    step.total_units = null
    step.pass_units = null
    step.fail_units = 0
  } else {
    if (step.fail_units === null) {
      step.fail_units = step.failures.length
    }
    if (step.total_units === null) {
      step.total_units = autoTotalForStep(process, step)
      step.__userTotalTouched = false
    }
    if (step.pass_units === null) {
      const total = Number(step.total_units ?? 0)
      const fail = Number(step.fail_units ?? 0)
      step.pass_units = Math.max(total - fail, 0)
    }
  }

  return step
}

function createProcess(overrides = {}) {
  const key = overrides.key || generateProcessKey()
  const process = {
    key,
    name:
      overrides.name ||
      overrides.process_name ||
      t('nested.defaultProcessName', { index: processCounter }),
    order_index: overrides.order_index ?? processForm.processes.length + 1,
    lots: [],
    steps: [],
  }

  const lots = Array.isArray(overrides.lots) ? overrides.lots : []
  lots.forEach((lot) => {
    process.lots.push(createLot(lot, key))
  })
  if (!process.lots.length) {
    process.lots.push(createLot({}, key))
  }

  const steps = Array.isArray(overrides.steps) ? overrides.steps : []
  steps.forEach((step) => {
    process.steps.push(createStep(process, step))
  })
  if (!process.steps.length) {
    process.steps.push(createStep(process, {}))
  }

  reindexProcess(process)
  return process
}

function reindexProcess(process) {
  process.order_index = Math.max(process.order_index || 0, 1)
  process.steps.forEach((step, idx) => {
    step.order_index = idx + 1
    step.failures.forEach((failure, failureIdx) => {
      failure.sequence = failureIdx + 1
    })
  })
}

function getProcess(index) {
  return processForm.processes[index]
}

function ensureProcessLotRefs(process) {
  const lotIds = process.lots.map((lot) => lot.client_id)
  process.steps.forEach((step) => {
    if (!Array.isArray(step.lot_refs)) {
      step.lot_refs = [...lotIds]
    } else {
      step.lot_refs = step.lot_refs.filter((ref) => lotIds.includes(ref))
      if (!step.lot_refs.length) {
        step.lot_refs = [...lotIds]
      }
    }
  })
}

function lotOptions(process) {
  return process.lots.map((lot) => ({
    value: lot.client_id,
    label: lot.lot_number
      ? `${lot.lot_number}${lot.quantity ? ` (${lot.quantity})` : ''}`
      : t('nested.unnamedLot'),
  }))
}

function lotQuantity(process, clientId) {
  const lot = process.lots.find((entry) => entry.client_id === clientId)
  return Number(lot?.quantity ?? 0)
}

function autoTotalForStep(process, step) {
  if (!step || !Array.isArray(step.lot_refs)) return 0
  return step.lot_refs.reduce((sum, ref) => sum + lotQuantity(process, ref), 0)
}

function handleTotalUnitsInput(processIndex, stepIndex) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
  if (!step || !step.results_applicable) return
  step.__userTotalTouched = true
  if (step.total_units === null || step.total_units === undefined) {
    step.total_units = 0
  }
  syncPassUnits(processIndex, stepIndex)
}

function syncPassUnits(processIndex, stepIndex) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
  if (!step || !step.results_applicable) return
  const total = Number(step.total_units ?? 0)
  const fail = Number(step.fail_units ?? 0)
  step.pass_units = Math.max(total - fail, 0)
}

function getStepLabelSuggestion(step) {
  if (!step) return null
  return STEP_LABEL_SUGGESTIONS[step.step_code] || null
}

function applyLabelSuggestion(processIndex, stepIndex) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
  if (!step) return
  const suggestion = getStepLabelSuggestion(step)
  if (!suggestion) return
  step.step_label = suggestion
  step.__lastAppliedSuggestion = suggestion
}

function handleLotRefsChange(processIndex, stepIndex) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
  if (!step) return
  if (!Array.isArray(step.lot_refs) || !step.lot_refs.length) {
    step.total_units = autoTotalForStep(process, step)
    step.__userTotalTouched = false
  }
  syncPassUnits(processIndex, stepIndex)
}

function setResultsApplicability(processIndex, stepIndex, value, options = {}) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
  if (!step) return
  const boolValue = Boolean(value)
  step.results_applicable = boolValue
  if (options.manual) {
    step.__resultsManualOverride = true
  } else if (options.resetManual) {
    step.__resultsManualOverride = false
  }

  if (!boolValue) {
    step.total_units = null
    step.pass_units = null
    step.fail_units = 0
    step.total_units_manual = false
    step.__userTotalTouched = false
    step.failures = []
  } else {
    if (step.total_units === null || step.total_units === undefined || !step.__userTotalTouched) {
      step.total_units = autoTotalForStep(process, step)
      step.__userTotalTouched = false
    }
    if (step.fail_units === null) {
      step.fail_units = step.failures.length
    }
  }
  syncPassUnits(processIndex, stepIndex)
}

function handleResultsApplicabilityChange(processIndex, stepIndex, value, manualChange = false) {
  setResultsApplicability(processIndex, stepIndex, value, { manual: manualChange })
}

function handleStepCodeChange(processIndex, stepIndex, value, options = {}) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
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

  if (!options.initial) {
    if (!step.__resultsManualOverride) {
      if (isResultOptionalCode(canonical)) {
        setResultsApplicability(processIndex, stepIndex, false, { resetManual: true })
      } else {
        setResultsApplicability(processIndex, stepIndex, true, { resetManual: true })
      }
    } else if (!isResultOptionalCode(canonical) && !step.results_applicable) {
      setResultsApplicability(processIndex, stepIndex, true)
    } else {
      syncPassUnits(processIndex, stepIndex)
    }
  } else {
    syncPassUnits(processIndex, stepIndex)
  }
}

const currentProcess = computed(() => getProcess(activeProcessIndex.value))

function addProcess() {
  const process = createProcess({
    name: t('nested.defaultProcessName', { index: processForm.processes.length + 1 }),
  })
  processForm.processes.push(process)
  activeProcessIndex.value = processForm.processes.length - 1
}

function duplicateProcess(index) {
  const source = getProcess(index)
  if (!source) return
  const duplicated = createProcess({
    key: generateProcessKey(),
    name: `${source.name} ${t('nested.copySuffix')}`,
    order_index: processForm.processes.length + 1,
    lots: source.lots,
    steps: source.steps,
  })
  processForm.processes.splice(index + 1, 0, duplicated)
  reindexAllProcesses()
  activeProcessIndex.value = index + 1
}

function removeProcess(index) {
  if (processForm.processes.length <= 1) {
    ElMessage.warning(t('nested.processRequiredMessage'))
    return
  }
  processForm.processes.splice(index, 1)
  if (activeProcessIndex.value >= processForm.processes.length) {
    activeProcessIndex.value = processForm.processes.length - 1
  }
  reindexAllProcesses()
}

function reindexAllProcesses() {
  processForm.processes.forEach((process, idx) => {
    process.order_index = idx + 1
    reindexProcess(process)
  })
}

function setActiveProcess(index) {
  activeProcessIndex.value = index
}

function toggleCollapse(index) {
  const process = getProcess(index)
  if (!process) return
  if (collapsedProcesses.has(process.key)) {
    collapsedProcesses.delete(process.key)
  } else {
    collapsedProcesses.add(process.key)
  }
}

function isCollapsed(index) {
  const process = getProcess(index)
  if (!process) return false
  return collapsedProcesses.has(process.key)
}

function onProcessDragStart(index) {
  if (props.readonly) return
  draggingData.index = index
}

function onProcessDrop(targetIndex) {
  if (props.readonly) return
  const sourceIndex = draggingData.index
  if (sourceIndex === targetIndex || sourceIndex === -1) return
  const [moved] = processForm.processes.splice(sourceIndex, 1)
  processForm.processes.splice(targetIndex, 0, moved)
  draggingData.index = -1
  reindexAllProcesses()
  activeProcessIndex.value = targetIndex
}

function addLot(processIndex) {
  const process = getProcess(processIndex)
  if (!process) return
  process.lots.push(createLot({}, process.key))
  ensureProcessLotRefs(process)
}

function duplicateLot(processIndex, lotIndex) {
  const process = getProcess(processIndex)
  const original = process?.lots[lotIndex]
  if (!original) return
  process.lots.splice(
    lotIndex + 1,
    0,
    createLot({ lot_number: original.lot_number, quantity: original.quantity }, process.key),
  )
  ensureProcessLotRefs(process)
}

function removeLot(processIndex, lotIndex) {
  const process = getProcess(processIndex)
  if (!process) return
  if (process.lots.length <= 1) {
    ElMessage.warning(t('nested.lotRequiredMessage'))
    return
  }
  process.lots.splice(lotIndex, 1)
  ensureProcessLotRefs(process)
}

async function openPasteLots(processIndex) {
  const process = getProcess(processIndex)
  if (!process || props.readonly) return
  try {
    const result = await ElMessageBox.prompt(
      t('nested.pasteLotsMessage'),
      t('nested.pasteLotsTitle'),
      {
        confirmButtonText: t('nested.apply'),
        cancelButtonText: t('common.cancel'),
        inputType: 'textarea',
        inputPlaceholder: t('nested.pasteLotsPlaceholder'),
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
      return createLot({ lot_number: lotNumber, quantity }, process.key)
    })

    newLots.forEach((lot) => process.lots.push(lot))
    ensureProcessLotRefs(process)
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    console.error('Failed to paste lots', error)
  }
}

function addStepAfter(processIndex, stepIndex) {
  const process = getProcess(processIndex)
  if (!process) return
  const insertIndex =
    Number.isInteger(stepIndex) && stepIndex >= 0 ? stepIndex + 1 : process.steps.length
  const newStep = createStep(process, { order_index: insertIndex + 1 })
  process.steps.splice(insertIndex, 0, newStep)
  reindexProcess(process)
  handleStepCodeChange(processIndex, insertIndex, newStep.step_code, { initial: true })
}

function duplicateStep(processIndex, stepIndex) {
  const process = getProcess(processIndex)
  const source = process?.steps[stepIndex]
  if (!source) return
  const duplicatePayload = JSON.parse(JSON.stringify(source))
  duplicatePayload.__uid = undefined
  const duplicate = createStep(process, duplicatePayload)
  process.steps.splice(stepIndex + 1, 0, duplicate)
  reindexProcess(process)
  handleStepCodeChange(processIndex, stepIndex + 1, duplicate.step_code, { initial: true })
}

function removeStep(processIndex, stepIndex) {
  const process = getProcess(processIndex)
  if (!process) return
  if (process.steps.length <= 1) {
    ElMessage.warning(t('nested.stepRequiredMessage'))
    return
  }
  process.steps.splice(stepIndex, 1)
  reindexProcess(process)
}

function addFailureRow(processIndex, stepIndex) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
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
  reindexProcess(process)
  syncPassUnits(processIndex, stepIndex)
}

function removeFailureRow(processIndex, stepIndex, failureIndex) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
  if (!step) return
  step.failures.splice(failureIndex, 1)
  reindexProcess(process)
  step.fail_units = step.failures.length
  syncPassUnits(processIndex, stepIndex)
}

function assignFailCode(processIndex, stepIndex, failureIndex, item) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
  const failure = step?.failures[failureIndex]
  if (!failure) return
  failure.fail_code_text = item.code
  failure.fail_code_id = item.id
  failure.fail_code_name_snapshot = item.name ?? ''
}

function normalizeFailCode(processIndex, stepIndex, failureIndex) {
  const process = getProcess(processIndex)
  const step = process?.steps[stepIndex]
  const failure = step?.failures[failureIndex]
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

const dictionaryIndex = computed(() => {
  const index = new Map()
  dictionaryEntries.value.forEach((entry) => {
    index.set(entry.code.toUpperCase(), entry)
  })
  return index
})

watch(
  () =>
    processForm.processes.map((process) =>
      process.lots.map((lot) => `${lot.client_id}:${Number(lot.quantity) || 0}`).join('|'),
    ),
  () => {
    processForm.processes.forEach((process, pIndex) => {
      ensureProcessLotRefs(process)
      process.steps.forEach((_, sIndex) => syncPassUnits(pIndex, sIndex))
    })
  },
  { deep: true },
)

function setPayload(payload, { markClean = false } = {}) {
  initializing = true
  processForm.processes.splice(0, processForm.processes.length)
  collapsedProcesses.clear()
  processForm.legacy_lot_number = payload?.legacy_lot_number ?? null
  processForm.legacy_quantity = payload?.legacy_quantity ?? null

  const processes =
    Array.isArray(payload?.processes) && payload.processes.length
      ? payload.processes
      : [
          {
            key: payload?.key || generateProcessKey(),
            name:
              payload?.name ||
              payload?.process_name ||
              t('nested.defaultProcessName', { index: 1 }),
            order_index: payload?.order_index || payload?.process_order_index || 1,
            lots: payload?.lots || [],
            steps: payload?.steps || [],
          },
        ]

  processes
    .sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
    .forEach((process) => {
      processForm.processes.push(createProcess(process))
    })

  if (!processForm.processes.length) {
    addProcess()
  }

  reindexAllProcesses()
  activeProcessIndex.value = Math.min(activeProcessIndex.value, processForm.processes.length - 1)
  processForm.processes.forEach((process, pIndex) => {
    ensureProcessLotRefs(process)
    process.steps.forEach((_, sIndex) => syncPassUnits(pIndex, sIndex))
  })
  if (markClean) {
    markPristine()
  }
  initializing = false
}

const normalizedPayload = computed(() => normalizeCurrentState())
const formattedPayload = computed(() => JSON.stringify(normalizedPayload.value, null, 2))

function snapshotPayload() {
  const value = normalizedPayload.value
  return JSON.stringify(value ?? {})
}

function normalizeCurrentState() {
  const normalizedProcesses = processForm.processes.map((process, processIndex) => {
    const normalizedLots = process.lots.map((lot) => ({
      id: lot.id ?? undefined,
      temp_id: lot.temp_id || lot.client_id,
      client_id: lot.client_id,
      lot_number: lot.lot_number?.trim() || '',
      quantity: Number(lot.quantity) || 0,
    }))

    const lotIdMap = new Map(normalizedLots.map((lot) => [lot.client_id, lot.client_id]))

    const normalizedSteps = process.steps.map((step, stepIndex) => {
      const normalizedLotRefs = Array.isArray(step.lot_refs)
        ? step.lot_refs.map((ref) => lotIdMap.get(ref) || null).filter(Boolean)
        : []

      const resultsApplicable = step.results_applicable !== false
      const autoTotal = resultsApplicable
        ? normalizedLotRefs.reduce((sum, ref) => {
            const lot = normalizedLots.find((entry) => entry.client_id === ref)
            return sum + (Number(lot?.quantity) || 0)
          }, 0)
        : 0
      const normalizedTotal = resultsApplicable
        ? step.total_units === null || step.total_units === undefined
          ? null
          : Number(step.total_units)
        : null
      let normalizedFail = null
      if (resultsApplicable) {
        if (step.fail_units === null || step.fail_units === undefined) {
          normalizedFail = step.failures.length
        } else {
          normalizedFail = Number(step.fail_units)
        }
      }

      let normalizedPass = null
      if (resultsApplicable) {
        if (normalizedTotal !== null && normalizedFail !== null) {
          normalizedPass = Math.max(Number(normalizedTotal) - Number(normalizedFail), 0)
        } else if (step.pass_units !== null && step.pass_units !== undefined) {
          normalizedPass = Number(step.pass_units)
        }
      }

      const normalizedEval = step.eval_code?.trim()

      return {
        order_index: step.order_index ?? stepIndex + 1,
        step_code: step.step_code?.trim().toUpperCase() ?? '',
        step_label: step.step_label?.trim() || '',
        eval_code: normalizedEval ? normalizedEval : null,
        lot_refs: normalizedLotRefs,
        results_applicable: resultsApplicable,
        total_units: normalizedTotal,
        total_units_manual:
          resultsApplicable && normalizedTotal !== null ? normalizedTotal !== autoTotal : false,
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
      key: process.key,
      name: process.name?.trim() || t('nested.defaultProcessName', { index: processIndex + 1 }),
      order_index: process.order_index ?? processIndex + 1,
      lots: normalizedLots,
      steps: normalizedSteps,
    }
  })

  return {
    processes: normalizedProcesses,
    legacy_lot_number: processForm.legacy_lot_number ?? null,
    legacy_quantity: processForm.legacy_quantity ?? null,
  }
}

function markPristine(snapshot) {
  let snapshotValue = snapshot ?? snapshotPayload()
  if (snapshot && typeof snapshot !== 'string') {
    snapshotValue = JSON.stringify(snapshot)
  }
  initialSnapshot.value = snapshotValue
  dirty.value = false
  emit('dirty-change', false)
}

watch(
  normalizedPayload,
  (newVal) => {
    if (initializing) return
    if (!newVal) return
    const currentSnapshot = snapshotPayload()
    const snapshot = initialSnapshot.value
    dirty.value = snapshot !== currentSnapshot
    emit('dirty-change', dirty.value)
  },
  { deep: true },
)

watch(
  () => props.initialPayload,
  (newPayload) => {
    setPayload(newPayload, { markClean: true })
  },
  { deep: true, immediate: true },
)

watch(
  () => props.serverWarnings,
  (warnings) => {
    warningsFromServer.value = Array.isArray(warnings) ? [...warnings] : []
  },
  { deep: true, immediate: true },
)

const processSummary = computed(() => {
  if (!processForm.processes.length) return ''
  return processForm.processes
    .map((process) => {
      const codes = process.steps.map((step) => step.step_code || t('nested.newStep'))
      return `${process.name || t('nested.defaultProcessName', { index: process.order_index })}: ${codes.join(' → ')}`
    })
    .join(' | ')
})

const validationMessages = computed(() => {
  const messages = []
  if (!processForm.processes.length) {
    messages.push(t('nested.validation.processRequired'))
  }
  processForm.processes.forEach((process, pIndex) => {
    if (!process.name?.trim()) {
      messages.push(t('nested.validation.processName', { index: pIndex + 1 }))
    }
    if (!process.lots.length) {
      messages.push(t('nested.validation.processLotRequired', { index: pIndex + 1 }))
    }
    process.lots.forEach((lot, lotIndex) => {
      if (!lot.lot_number?.trim()) {
        messages.push(
          t('nested.validation.lotNumber', { process: pIndex + 1, index: lotIndex + 1 }),
        )
      }
      if (Number(lot.quantity) < 0) {
        messages.push(
          t('nested.validation.lotQuantity', { process: pIndex + 1, index: lotIndex + 1 }),
        )
      }
    })
    if (!process.steps.length) {
      messages.push(t('nested.validation.stepRequiredProcess', { index: pIndex + 1 }))
    }
    process.steps.forEach((step, stepIndex) => {
      if (!step.step_code?.trim()) {
        messages.push(
          t('nested.validation.stepCodeProcess', { process: pIndex + 1, index: stepIndex + 1 }),
        )
      }
      if (!Array.isArray(step.lot_refs) || !step.lot_refs.length) {
        messages.push(
          t('nested.validation.stepLots', { index: stepIndex + 1, process: pIndex + 1 }),
        )
      }
      if (step.results_applicable) {
        if (
          step.total_units !== null &&
          Number(step.total_units ?? 0) < Number(step.fail_units ?? 0)
        ) {
          messages.push(
            t('nested.validation.totalLessThanFailProcess', {
              process: pIndex + 1,
              index: stepIndex + 1,
            }),
          )
        }
        step.failures.forEach((failure, failureIndex) => {
          if (!failure.fail_code_text?.trim()) {
            messages.push(
              t('nested.validation.failCodeEmptyProcess', {
                process: pIndex + 1,
                index: stepIndex + 1,
                row: failureIndex + 1,
              }),
            )
          }
        })
      } else if (step.failures.length) {
        messages.push(
          t('nested.validation.removeFailuresProcess', {
            process: pIndex + 1,
            index: stepIndex + 1,
          }),
        )
      }
    })
  })
  return messages
})

const combinedWarnings = computed(() => [...warningsFromServer.value])

const showDebug = computed(() => {
  if (import.meta.env.VITE_BUILDER_DEBUG === '1') return true
  if (import.meta.env.DEV) return true
  if (typeof window !== 'undefined') {
    const search = new URLSearchParams(window.location.search)
    const debugParam = search.get('debug') || search.get('builderDebug')
    if (debugParam && ['1', 'true', 'yes'].includes(debugParam.toLowerCase())) {
      return true
    }
  }
  return false
})

function emitSave() {
  emit('save', normalizedPayload.value)
}

async function copyPayload() {
  try {
    await navigator.clipboard.writeText(formattedPayload.value)
    ElMessage.success(t('nested.copySuccess'))
  } catch (error) {
    ElMessage.error(t('nested.copyError'))
    console.error(error)
  }
}

const exposeSteps = {
  getPayload: () => normalizedPayload.value,
  setPayload,
  markPristine,
  isDirty: () => dirty.value,
  hasSteps: () => processForm.processes.some((process) => process.steps.length > 0),
  setWarnings: (warnings) => {
    warningsFromServer.value = Array.isArray(warnings) ? [...warnings] : []
  },
}

defineExpose(exposeSteps)

nextTick(() => {
  if (!processForm.processes.length) {
    addProcess()
  }
})
</script>

<style scoped>
.process-builder {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.process-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.summary-label {
  font-weight: 600;
}

.process-toolbar {
  display: flex;
  gap: 8px;
}

.builder-actions {
  display: flex;
  justify-content: flex-end;
}

.process-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.process-panel {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  cursor: grab;
}

.process-panel.active {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.process-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.process-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.process-name-input :deep(.el-input__inner) {
  font-weight: 600;
}

.process-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.process-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
  overflow-x: auto;
}

.add-step-button {
  align-self: flex-start;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
