<template>
  <div class="process-prototype">
    <el-page-header content="Process Builder Prototype" @back="handleBack" />

    <el-alert
      class="intro"
      type="info"
      :closable="false"
      title="Static mock for the nested evaluation process payload"
      description="Interact with the form below to see how the contract payload evolves. This prototype works on mock data only."
    />

    <el-card class="form-section">
      <template #header>
        <div class="card-header">
          <span>Process Summary</span>
          <div class="header-actions">
            <el-button
              v-if="canSave"
              type="primary"
              :icon="Check"
              :loading="saving"
              @click="saveNestedProcesses"
            >
              Save
            </el-button>
          </div>
        </div>
      </template>
      <el-form label-position="top" class="summary-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Lot Number">
              <el-input v-model="processForm.lot_number" placeholder="Enter lot number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Quantity">
              <el-input-number
                v-model="processForm.quantity"
                :min="0"
                :step="1"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <div class="steps-container">
      <transition-group name="fade" tag="div">
        <el-card
          v-for="(step, index) in processForm.steps"
          :key="step.order_index"
          class="form-section step-card"
        >
          <template #header>
            <div class="step-header">
              <div class="step-title">
                <el-tag type="info">Step {{ index + 1 }}</el-tag>
                <span>{{ step.step_code || 'New Step' }}</span>
                <span v-if="step.step_label" class="step-label">{{ step.step_label }}</span>
              </div>
              <div class="step-actions">
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
            <el-row :gutter="12" class="step-inputs">
              <el-col :span="6">
                <el-form-item label="Step Code" required>
                  <el-input
                    v-model="step.step_code"
                    placeholder="e.g. M031"
                    @blur="() => normalizeStepCode(index)"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Step Label">
                  <el-input v-model="step.step_label" placeholder="Optional label" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Eval Code" required>
                  <el-input
                    v-model="step.eval_code"
                    placeholder="Single eval code"
                    @blur="() => normalizeEvalCode(index)"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Notes">
                  <el-input v-model="step.notes" placeholder="Optional notes" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="12" class="step-metrics">
              <el-col :span="8">
                <el-form-item label="Total Units" required>
                  <el-input-number
                    v-model="step.total_units"
                    :min="0"
                    :step="1"
                    controls-position="right"
                    @change="() => enforceTotals(index)"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Pass Units" required>
                  <el-input-number
                    v-model="step.pass_units"
                    :min="0"
                    :step="1"
                    controls-position="right"
                    @change="() => enforceTotals(index)"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Fail Units" required>
                  <el-input-number
                    v-model="step.fail_units"
                    :min="0"
                    :step="1"
                    controls-position="right"
                    @change="() => enforceTotals(index)"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <el-alert
            v-if="stepMismatch(index)"
            type="warning"
            class="compact-alert"
            show-icon
            :closable="false"
            :title="`Mismatch: pass (${step.pass_units}) + fail (${step.fail_units}) !== total (${step.total_units})`"
          />

          <div class="failure-header">
            <h4>Failure Details</h4>
            <el-button size="small" :icon="Plus" @click="addFailureRow(index)"
              >Add Failure</el-button
            >
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
            <el-table-column label="Serial Number">
              <template #default="{ row }">
                <el-input v-model="row.serial_number" placeholder="Enter SN" />
              </template>
            </el-table-column>
            <el-table-column label="Fail Code" width="200">
              <template #default="{ row, $index }">
                <el-autocomplete
                  v-model="row.fail_code_text"
                  class="code-input"
                  :fetch-suggestions="(query, cb) => queryFailCodes(query, cb)"
                  :trigger-on-focus="false"
                  placeholder="Fail code"
                  @select="(item) => assignFailCode(index, $index, item)"
                  @blur="() => normalizeFailCode(index, $index)"
                />
                <div class="code-hints">
                  <el-tag v-if="row.fail_code_id" size="small" type="success">dictionary</el-tag>
                  <el-tag v-else-if="row.fail_code_text" size="small" type="warning"
                    >not in dictionary</el-tag
                  >
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Fail Name" min-width="160">
              <template #default="{ row }">
                <el-input v-model="row.fail_code_name_snapshot" placeholder="Optional fail name" />
              </template>
            </el-table-column>
            <el-table-column label="Analysis Result">
              <template #default="{ row }">
                <el-input
                  v-model="row.analysis_result"
                  type="textarea"
                  :rows="2"
                  placeholder="Analysis details"
                />
              </template>
            </el-table-column>
            <el-table-column width="70" fixed="right">
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
        </el-card>
      </transition-group>

      <el-button
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

    <div v-if="warningsFromServer.length" class="validation-block">
      <el-alert title="Server warnings" type="warning" :closable="false" show-icon>
        <ul class="validation-list">
          <li v-for="(message, idx) in warningsFromServer" :key="`server-warning-${idx}`">{{ message }}</li>
        </ul>
      </el-alert>
    </div>

    <el-card class="form-section">
      <template #header>
        <div class="payload-header">
          <span>Normalized Payload</span>
          <el-button size="small" :icon="DocumentCopy" @click="copyPayload">Copy JSON</el-button>
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
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, DocumentCopy, Plus, Check } from '@element-plus/icons-vue'
import api from '../utils/api'

const props = defineProps({
  evaluationId: { type: [String, Number], default: null },
})

const route = useRoute()

const evaluationId = computed(() => props.evaluationId ?? route.params?.id ?? null)
const isPrototypeRoute = computed(() => route.name === 'ProcessPrototype')
const canSave = computed(() => Boolean(evaluationId.value))

const saving = ref(false)
const warningsFromServer = ref([])
const evaluationMeta = ref(null)

const dictionaryEntries = ref([
  { id: 42, code: '3344', name: 'UECC (Uncorrectable ECC)' },
  { id: 77, code: '7710', name: 'Controller timeout' },
  { id: 88, code: '3404', name: 'Read disturb' },
  { id: 93, code: '3379', name: 'Write amplification spike' },
])

function createStep(overrides = {}) {
  return reactive({
    order_index: overrides.order_index ?? 1,
    step_code: overrides.step_code ?? '',
    step_label: overrides.step_label ?? '',
    eval_code: overrides.eval_code ?? '',
    total_units: overrides.total_units ?? 0,
    pass_units: overrides.pass_units ?? 0,
    fail_units: overrides.fail_units ?? 0,
    notes: overrides.notes ?? '',
    failures: overrides.failures
      ? overrides.failures.map((failure) => createFailure(failure))
      : [],
  })
}

function createFailure(overrides = {}) {
  return reactive({
    sequence: overrides.sequence ?? 1,
    serial_number: overrides.serial_number ?? '',
    fail_code_id: overrides.fail_code_id ?? null,
    fail_code_text: overrides.fail_code_text ?? '',
    fail_code_name_snapshot: overrides.fail_code_name_snapshot ?? '',
    analysis_result: overrides.analysis_result ?? '',
  })
}

const processForm = reactive({
  lot_number: '',
  quantity: 0,
  steps: [createStep({ order_index: 1 })],
})

const dictionaryIndex = computed(() => {
  const index = new Map()
  dictionaryEntries.value.forEach((entry) => {
    index.set(entry.code.toUpperCase(), entry)
  })
  return index
})

function resetForm() {
  processForm.lot_number = ''
  processForm.quantity = 0
  processForm.steps.splice(0, processForm.steps.length, createStep({ order_index: 1 }))
  reindexSteps()
}

function seedSampleData() {
  processForm.lot_number = 'X0JWN0540'
  processForm.quantity = 100
  processForm.steps.splice(
    0,
    processForm.steps.length,
    createStep({
      order_index: 1,
      step_code: 'M031',
      step_label: 'iARTs',
      eval_code: 'S888',
      total_units: 100,
      pass_units: 96,
      fail_units: 4,
      failures: [
        {
          sequence: 1,
          serial_number: 'X0JWN0540301A010001',
          fail_code_id: 42,
          fail_code_text: '3344',
          fail_code_name_snapshot: 'UECC',
          analysis_result: 'Nand fail',
        },
        {
          sequence: 2,
          serial_number: 'X0JWN0540301A010017',
          fail_code_id: null,
          fail_code_text: '7710',
          fail_code_name_snapshot: 'Controller timeout',
          analysis_result: 'CSR reset resolved issue',
        },
      ],
    }),
  )
  reindexSteps()
}

async function loadEvaluation() {
  if (!evaluationId.value) return
  try {
    const response = await api.get(`/evaluations/${evaluationId.value}`)
    const evaluation = response.data?.data?.evaluation
    evaluationMeta.value = evaluation || null
    warningsFromServer.value = []
    resetForm()
    if (evaluation) {
      const firstProcess =
        Array.isArray(evaluation.processes) && evaluation.processes.length
          ? evaluation.processes[0]
          : null
      processForm.lot_number =
        (firstProcess && firstProcess.lot_number) || evaluation.evaluation_number || ''
      processForm.quantity = (firstProcess && firstProcess.quantity) || 0
    }
  } catch (error) {
    ElMessage.error('Failed to load evaluation context')
    console.error('Failed to load evaluation context', error)
  }
}

watch(
  evaluationId,
  async (id) => {
    if (id) {
      await loadEvaluation()
    } else {
      warningsFromServer.value = []
      resetForm()
      if (isPrototypeRoute.value) {
        seedSampleData()
      }
    }
  },
  { immediate: true },
)

watch(isPrototypeRoute, (isPrototype) => {
  if (!evaluationId.value && isPrototype) {
    seedSampleData()
  }
})

function handleBack() {
  window.history.back()
}

function reindexSteps() {
  processForm.steps.forEach((step, stepIdx) => {
    step.order_index = stepIdx + 1
    step.failures.forEach((failure, failureIdx) => {
      failure.sequence = failureIdx + 1
    })
  })
}

function addStepAfter(index) {
  const insertIndex = Number.isInteger(index) && index >= 0 ? index + 1 : processForm.steps.length
  processForm.steps.splice(insertIndex, 0, createStep({ order_index: insertIndex + 1 }))
  reindexSteps()
}

function duplicateStep(index) {
  const source = processForm.steps[index]
  const duplicate = createStep({
    ...stripReactivity(source),
    failures: source.failures.map((failure) => stripReactivity(failure)),
  })
  processForm.steps.splice(index + 1, 0, duplicate)
  reindexSteps()
}

function removeStep(index) {
  if (processForm.steps.length === 1) {
    ElMessage.warning('At least one step is required')
    return
  }
  processForm.steps.splice(index, 1)
  reindexSteps()
}

function stripReactivity(payload) {
  return JSON.parse(JSON.stringify(payload))
}

function normalizeStepCode(index) {
  const step = processForm.steps[index]
  if (!step) return
  step.step_code = step.step_code?.trim().toUpperCase() ?? ''
}

function normalizeEvalCode(index) {
  const step = processForm.steps[index]
  if (!step) return
  step.eval_code = step.eval_code?.trim().toUpperCase() ?? ''
}

function enforceTotals(index) {
  const step = processForm.steps[index]
  if (!step) return
  const total = Number(step.total_units) || 0
  const passUnits = Number(step.pass_units) || 0
  const failUnits = Number(step.fail_units) || 0

  step.total_units = total
  step.pass_units = passUnits
  step.fail_units = failUnits
}

function stepMismatch(index) {
  const step = processForm.steps[index]
  if (!step) return false
  const total = Number(step.total_units) || 0
  const passUnits = Number(step.pass_units) || 0
  const failUnits = Number(step.fail_units) || 0
  return total !== passUnits + failUnits
}

function addFailureRow(stepIndex) {
  const step = processForm.steps[stepIndex]
  if (!step) return
  step.failures.push(createFailure())
  reindexSteps()
}

function removeFailureRow(stepIndex, failureIndex) {
  const step = processForm.steps[stepIndex]
  if (!step) return
  step.failures.splice(failureIndex, 1)
  reindexSteps()
}

function queryFailCodes(queryString, cb) {
  const normalized = (queryString || '').trim().toUpperCase()
  let results = dictionaryEntries.value
  if (normalized) {
    results = results.filter(
      (entry) => entry.code.includes(normalized) || entry.name?.toUpperCase().includes(normalized),
    )
  }
  cb(results.map((entry) => ({ value: entry.code, ...entry })))
}

function assignFailCode(stepIndex, failureIndex, item) {
  const step = processForm.steps[stepIndex]
  if (!step) return
  const failure = step.failures[failureIndex]
  if (!failure) return
  failure.fail_code_text = item.code
  failure.fail_code_id = item.id
  failure.fail_code_name_snapshot = item.name ?? ''
}

function normalizeFailCode(stepIndex, failureIndex) {
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

const validationMessages = computed(() => {
  const messages = []
  if (!processForm.lot_number?.trim()) {
    messages.push('Lot number is required')
  }
  if (!processForm.quantity || processForm.quantity <= 0) {
    messages.push('Quantity must be greater than zero')
  }
  if (!processForm.steps.length) {
    messages.push('At least one process step is required')
  }

  processForm.steps.forEach((step, index) => {
    if (!step.step_code?.trim()) {
      messages.push(`Step ${index + 1}: step code is required`)
    }
    if (!step.eval_code?.trim()) {
      messages.push(`Step ${index + 1}: eval code is required`)
    }
    if (stepMismatch(index)) {
      messages.push(`Step ${index + 1}: pass + fail must equal total units`)
    }
    step.failures.forEach((failure, failureIndex) => {
      if (!failure.fail_code_text?.trim()) {
        messages.push(`Step ${index + 1}, failure ${failureIndex + 1}: fail code is required`)
      }
    })
  })

  return messages
})

const normalizedPayload = computed(() => {
  return {
    lot_number: processForm.lot_number?.trim() ?? '',
    quantity: Number(processForm.quantity) || 0,
    steps: processForm.steps.map((step) => ({
      order_index: step.order_index,
      step_code: step.step_code?.trim().toUpperCase() ?? '',
      step_label: step.step_label?.trim() || undefined,
      eval_code: step.eval_code?.trim().toUpperCase() ?? '',
      total_units: Number(step.total_units) || 0,
      pass_units: Number(step.pass_units) || 0,
      fail_units: Number(step.fail_units) || 0,
      notes: step.notes?.trim() || undefined,
      failures: step.failures.map((failure) => ({
        sequence: failure.sequence,
        serial_number: failure.serial_number?.trim() || undefined,
        fail_code_id: failure.fail_code_id ?? undefined,
        fail_code_text: failure.fail_code_text?.trim().toUpperCase() ?? '',
        fail_code_name_snapshot: failure.fail_code_name_snapshot?.trim() || undefined,
        analysis_result: failure.analysis_result?.trim() || undefined,
      })),
    })),
  }
})

const formattedPayload = computed(() => JSON.stringify(normalizedPayload.value, null, 2))

async function copyPayload() {
  try {
    await navigator.clipboard.writeText(formattedPayload.value)
    ElMessage.success('Payload copied to clipboard')
  } catch (error) {
    ElMessage.error('Unable to copy payload')
    console.error(error)
  }
}

async function saveNestedProcesses() {
  if (!evaluationId.value) {
    ElMessage.warning('Open this editor from an evaluation to save changes')
    return
  }
  if (validationMessages.value.length) {
    ElMessage.warning('Fix validation issues before saving')
    return
  }

  saving.value = true
  warningsFromServer.value = []
  try {
    const response = await api.post(
      `/evaluations/${evaluationId.value}/processes/nested`,
      normalizedPayload.value,
    )
    const serverWarnings = response.data?.data?.warnings || []
    warningsFromServer.value = serverWarnings
    if (serverWarnings.length) {
      ElMessage.warning('Saved with warnings. Review details below.')
    } else {
      ElMessage.success('Nested processes saved')
    }
  } catch (error) {
    warningsFromServer.value = []
    ElMessage.error('Failed to save nested processes')
    console.error('Failed to save nested processes', error)
  } finally {
    saving.value = false
  }
}

reindexSteps()
</script>

<style scoped>
.process-prototype {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.intro {
  margin-bottom: 8px;
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

.failure-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0 8px;
}

.failure-table {
  margin-bottom: 8px;
}

.code-input {
  width: 100%;
}

.code-hints {
  margin-top: 4px;
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

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
