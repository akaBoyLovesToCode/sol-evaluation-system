<template>
  <div v-loading="loading" class="new-evaluation-page">
    <div class="page-container">
      <div v-if="!inDialog" class="page-header">
        <h1 class="page-title">
          {{ isEditMode ? $t('evaluation.edit.title') : $t('evaluation.new.title') }}
        </h1>
        <p class="page-description">
          {{ isEditMode ? $t('evaluation.edit.description') : $t('evaluation.new.description') }}
        </p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="evaluation-form"
      >
        <el-card class="form-section fade-in-up" style="animation-delay: 0.1s">
          <template #header>
            <span>{{ $t('evaluation.basicInfo') }}</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('evaluation.typeLabel')" prop="evaluation_type">
                <el-radio-group v-model="form.evaluation_type" @change="handleTypeChange">
                  <el-radio value="new_product">{{ $t('evaluation.type.new_product') }}</el-radio>
                  <el-radio value="mass_production">{{
                    $t('evaluation.type.mass_production')
                  }}</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('evaluation.productName')" prop="product_name">
                <el-input
                  v-model="form.product_name"
                  :placeholder="$t('evaluation.placeholders.productName')"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('evaluation.partNumber')" prop="part_number">
                <el-input
                  v-model="form.part_number"
                  :placeholder="$t('evaluation.placeholders.partNumber')"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('evaluation.startDate')" prop="start_date">
                <el-date-picker
                  v-model="form.start_date"
                  type="date"
                  :placeholder="$t('evaluation.placeholders.startDate')"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col v-if="isEditMode" :span="12">
              <el-form-item :label="$t('evaluation.actualEndDate')" prop="end_date">
                <el-date-picker
                  v-model="form.end_date"
                  type="date"
                  :placeholder="$t('evaluation.placeholders.actualEndDate')"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('evaluation.reason')" prop="reason">
                <el-select
                  v-model="form.reason"
                  :placeholder="$t('evaluation.placeholders.reason')"
                  style="width: 100%"
                >
                  <el-option
                    v-for="option in reasonOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('evaluation.processStep')" prop="process_step">
                <el-select
                  v-model="form.process_step"
                  :placeholder="$t('evaluation.placeholders.processStep')"
                  multiple
                  collapse-tags
                  style="width: 100%"
                >
                  <el-option
                    v-for="step in processStepChoices"
                    :key="step"
                    :label="step"
                    :value="step"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('evaluation.scsCharger')" prop="scs_charger_name">
                <el-input
                  v-model="form.scs_charger_name"
                  :placeholder="$t('evaluation.placeholders.scsCharger')"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                :label="$t('evaluation.headOfficeCharger')"
                prop="head_office_charger_name"
              >
                <el-input
                  v-model="form.head_office_charger_name"
                  :placeholder="$t('evaluation.placeholders.headOfficeCharger')"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item :label="$t('evaluation.descriptionLabel')" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              :placeholder="$t('evaluation.placeholders.description')"
            />
          </el-form-item>
        </el-card>

        <el-card class="form-section fade-in-up" style="animation-delay: 0.3s">
          <template #header>
            <span>{{ $t('evaluation.technicalSpec') }}</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item :label="$t('evaluation.pgmVersion')" prop="pgm_version">
                <el-input
                  v-model="form.pgm_version"
                  :placeholder="$t('evaluation.placeholders.pgmVersion')"
                />
              </el-form-item>
            </el-col>

            <el-col :span="8">
              <el-form-item :label="$t('evaluation.testTime')" prop="pgm_test_time">
                <el-input
                  v-model="form.pgm_test_time"
                  :placeholder="$t('evaluation.placeholders.testTime')"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="form-section fade-in-up" style="animation-delay: 0.5s">
          <template #header>
            <div class="card-header">
              <span>{{ $t('evaluation.evaluationProcesses') }}</span>
              <el-button type="primary" plain @click="openProcessDrawer">
                <template #icon><Connection /></template>
                {{ $t('evaluation.manageNestedProcesses') }}
              </el-button>
            </div>
          </template>

          <el-empty v-if="!builderHasStepsSummary" :description="$t('nested.summary.empty')" />

          <div v-else class="nested-summary">
            <div
              v-for="process in builderSummaryProcesses"
              :key="process.key"
              class="nested-process-summary"
            >
              <div class="nested-process-header">
                <strong>{{ process.name }}</strong>
                <span class="nested-process-chain">
                  {{
                    process.steps.map((step) => step.step_code || $t('nested.newStep')).join(' → ')
                  }}
                </span>
              </div>
              <div
                v-for="step in process.steps"
                :key="`${process.key}-${step.order_index}`"
                class="nested-summary-item"
              >
                <div class="nested-step-title">
                  <strong>{{ step.order_index }}. {{ step.step_code }}</strong>
                  <span v-if="step.step_label"> - {{ step.step_label }}</span>
                </div>
                <div v-if="step.results_applicable !== false" class="nested-step-meta">
                  {{
                    $t('nested.summary.evalLine', {
                      eval: step.eval_code || '—',
                      total: formatUnit(step.total_units),
                      pass: formatUnit(step.pass_units),
                      fail: formatUnit(step.fail_units),
                    })
                  }}
                </div>
                <div v-else class="nested-step-meta">{{ $t('nested.summary.noResults') }}</div>
                <div class="nested-step-lots">
                  {{ $t('nested.summary.appliesTo') }}
                  {{ describeStepLots(process, step.lot_refs) }}
                </div>
                <div
                  v-if="Array.isArray(step.failures) && step.failures.length"
                  class="nested-failure-count"
                >
                  {{ $t('nested.summary.failuresCount', { count: step.failures.length }) }}
                </div>
              </div>
            </div>
          </div>

          <el-alert
            v-if="nestedSaveWarnings.length"
            type="warning"
            show-icon
            class="nested-warning"
            @close="clearNestedWarnings"
          >
            <ul class="alert-list">
              <li v-for="(warning, index) in nestedSaveWarnings" :key="`nested-warning-${index}`">
                {{ warning }}
              </li>
            </ul>
          </el-alert>
          <el-alert
            v-if="nestedSaveError"
            type="error"
            show-icon
            class="nested-warning"
            @close="clearNestedError"
          >
            {{ nestedSaveError }}
          </el-alert>
        </el-card>

        <el-drawer
          v-model="processDrawerVisible"
          size="60%"
          :before-close="handleProcessDrawerBeforeClose"
          :title="$t('evaluation.manageNestedProcesses')"
        >
          <ProcessBuilder
            ref="processBuilderRef"
            :initial-payload="builderPayload"
            :server-warnings="processBuilderWarnings"
            :show-save-button="false"
            @dirty-change="handleBuilderDirtyChange"
          />
          <template #footer>
            <div class="drawer-footer">
              <el-button @click="handleDrawerCancel">{{ $t('common.cancel') }}</el-button>
              <el-button type="primary" @click="commitBuilderChanges">{{
                $t('common.save')
              }}</el-button>
            </div>
          </template>
        </el-drawer>

        <div v-if="!inDialog" class="form-actions fade-in-up" style="animation-delay: 0.7s">
          <el-button @click="handleCancel">{{ $t('common.cancel') }}</el-button>

          <!-- Create Mode Buttons -->
          <template v-if="!isEditMode">
            <el-button type="primary" :loading="saving" @click="handleSave(false)">
              {{ $t('evaluation.saveDraft') }}
            </el-button>
            <el-button type="success" :loading="submitting" @click="handleSave(true)">
              {{ $t('evaluation.submit') }}
            </el-button>
          </template>

          <!-- Edit Mode Buttons -->
          <template v-if="isEditMode">
            <el-button type="danger" :loading="deleting" @click="handleDelete">
              {{ $t('common.delete') }}
            </el-button>
            <el-button type="primary" :loading="saving" @click="handleSave(false)">
              {{ $t('common.save') }}
            </el-button>
            <el-button type="success" :loading="finishing" @click="handleFinish">
              {{ $t('evaluation.finish') }}
            </el-button>
          </template>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const props = defineProps({
  inDialog: { type: Boolean, default: false },
  evaluationId: { type: [String, Number], default: null },
  processStepOptions: {
    type: Array,
    default: () => ['iARTs', 'Aging', 'LI', 'Repair'],
  },
})
const emit = defineEmits(['saved'])
import { useI18n } from 'vue-i18n'
import api from '../utils/api'
import ProcessBuilder from '../components/ProcessBuilder.vue'
import {
  builderPayloadToNestedRequest,
  createEmptyBuilderPayload,
  evaluationToBuilderPayload,
  hasBuilderSteps,
  normalizeBuilderPayload,
} from '../utils/processMapper'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const processStepChoices = computed(() => props.processStepOptions || [])

const parseProcessSteps = (value) => {
  if (!value) return []
  if (Array.isArray(value)) return value.filter(Boolean)
  return String(value)
    .split(/[|,]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const serializeProcessSteps = (steps) => {
  if (!Array.isArray(steps)) return steps ? String(steps) : ''
  return steps.filter(Boolean).join('|')
}
const formRef = ref()
const saving = ref(false)
const submitting = ref(false)
const loading = ref(false)
const deleting = ref(false)
const finishing = ref(false)
// Simplified app: no user directory; chargers are free-text

// Check if in edit mode
const isEditMode = computed(
  () => !!(props.evaluationId || (route.name === 'EditEvaluation' && route.params.id)),
)
const evaluationId = computed(() => props.evaluationId || route.params.id)

// Computed property for dynamic reason options based on evaluation type
const reasonOptions = computed(() => {
  if (form.evaluation_type === 'new_product') {
    return [
      {
        label: t('evaluation.reasons.horizontal_expansion'),
        value: 'horizontal_expansion',
      },
      {
        label: t('evaluation.reasons.direct_development'),
        value: 'direct_development',
      },
    ]
  } else if (form.evaluation_type === 'mass_production') {
    return [
      {
        label: t('evaluation.reasons.pgm_improvement'),
        value: 'pgm_improvement',
      },
      {
        label: t('evaluation.reasons.firmware_change'),
        value: 'firmware_change',
      },
      { label: t('evaluation.reasons.bom_change'), value: 'bom_change' },
      {
        label: t('evaluation.reasons.customer_requirement'),
        value: 'customer_requirement',
      },
      { label: t('evaluation.reasons.nand'), value: 'nand' },
      { label: t('evaluation.reasons.nprr'), value: 'nprr' },
      { label: t('evaluation.reasons.repair'), value: 'repair' },
      { label: t('evaluation.reasons.facility'), value: 'facility' },
      { label: t('evaluation.reasons.other'), value: 'other' },
    ]
  }
  return []
})

const form = reactive({
  evaluation_type: '',
  product_name: '',
  part_number: '',
  start_date: '',
  end_date: '',
  reason: '',
  process_step: [],
  description: '',
  pgm_version: '',
  pgm_test_time: '',
  scs_charger_name: '',
  head_office_charger_name: '',
})

const builderPayload = ref(normalizeBuilderPayload(createEmptyBuilderPayload()))
const processDrawerVisible = ref(false)
const processBuilderRef = ref(null)
const processBuilderWarnings = ref([])
const processBuilderDirty = ref(false)
const nestedSaveWarnings = ref([])
const nestedSaveError = ref(null)

const builderSummaryProcesses = computed(() => {
  const processes = Array.isArray(builderPayload.value.processes)
    ? builderPayload.value.processes
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

const builderHasStepsSummary = computed(() => hasBuilderSteps(builderPayload.value))

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

const formatUnit = (value) =>
  value === null || value === undefined || Number.isNaN(value) ? '—' : value

async function refreshNestedPayload(targetId, evaluationContext = null, options = {}) {
  const { preserveWarnings = false } = options
  if (!targetId) {
    const fallback = evaluationContext
      ? evaluationToBuilderPayload(evaluationContext)
      : createEmptyBuilderPayload()
    builderPayload.value = normalizeBuilderPayload(fallback)
    if (!preserveWarnings) {
      nestedSaveWarnings.value = []
    }
    processBuilderWarnings.value = []
    return
  }

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
    processBuilderWarnings.value = warnings
  } catch (error) {
    console.error('Failed to load nested process payload', error)
    if (evaluationContext) {
      builderPayload.value = normalizeBuilderPayload(evaluationToBuilderPayload(evaluationContext))
    }
    if (!preserveWarnings) {
      nestedSaveWarnings.value = []
    }
    processBuilderWarnings.value = []
  }
}

function handleBuilderDirtyChange(value) {
  processBuilderDirty.value = value
}

async function openProcessDrawer() {
  processBuilderWarnings.value = Array.isArray(nestedSaveWarnings.value)
    ? [...nestedSaveWarnings.value]
    : []
  processDrawerVisible.value = true
  await nextTick()
  processBuilderRef.value?.setPayload(builderPayload.value, { markClean: true })
  processBuilderDirty.value = false
}

async function handleProcessDrawerBeforeClose(done) {
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
      if (typeof done === 'function') {
        return
      }
      return
    }
  }
  processDrawerVisible.value = false
  if (typeof done === 'function') {
    done()
  }
}

function handleDrawerCancel() {
  handleProcessDrawerBeforeClose(() => {
    processDrawerVisible.value = false
  })
}

function commitBuilderChanges() {
  if (!processBuilderRef.value) return
  builderPayload.value = normalizeBuilderPayload(processBuilderRef.value.getPayload())
  processBuilderWarnings.value = []
  processBuilderRef.value.markPristine()
  processBuilderDirty.value = false
  processDrawerVisible.value = false
}

function clearNestedWarnings() {
  nestedSaveWarnings.value = []
  processBuilderWarnings.value = []
}

function clearNestedError() {
  nestedSaveError.value = null
}

async function saveNestedProcesses(targetId) {
  if (!targetId) return
  if (!hasBuilderSteps(builderPayload.value)) {
    nestedSaveWarnings.value = []
    nestedSaveError.value = null
    return
  }
  try {
    const payload = builderPayloadToNestedRequest(builderPayload.value)
    const response = await api.post(`/evaluations/${targetId}/processes/nested`, payload)
    nestedSaveWarnings.value = response.data?.data?.warnings || []
    nestedSaveError.value = null
    await refreshNestedPayload(targetId, null, { preserveWarnings: true })
  } catch (error) {
    nestedSaveError.value =
      'Failed to save nested processes. The raw payload was archived on the server.'
    console.error('Failed to save nested processes', error)
  }
}

const rules = computed(() => ({
  evaluation_type: [
    {
      required: true,
      message: t('validation.requiredField.type'),
      trigger: 'change',
    },
  ],
  product_name: [
    {
      required: true,
      message: t('validation.requiredField.productName'),
      trigger: 'blur',
    },
  ],
  part_number: [
    {
      required: true,
      message: t('validation.requiredField.partNumber'),
      trigger: 'blur',
    },
  ],
  start_date: [
    {
      required: true,
      message: t('validation.requiredField.startDate'),
      trigger: 'change',
    },
  ],
  process_step: [
    {
      trigger: 'change',
      validator: (_, value, callback) => {
        if (!value || value.length === 0) {
          callback(new Error(t('validation.requiredField.processStep')))
        } else {
          callback()
        }
      },
    },
  ],
  reason: [
    {
      required: true,
      message: t('validation.requiredField.reason'),
      trigger: 'change',
    },
  ],
  description: [
    {
      required: true,
      message: t('validation.requiredField.description'),
      trigger: 'blur',
    },
  ],
  scs_charger_name: [
    {
      required: false,
      message: t('validation.requiredField.scsCharger'),
      trigger: 'blur',
    },
  ],
  head_office_charger_name: [
    {
      required: false,
      message: t('validation.requiredField.headOfficeCharger'),
      trigger: 'blur',
    },
  ],
  end_date: [
    // Conditional validation: required only when finishing
    {
      validator: (rule, value, callback) => {
        if (finishing.value && !value) {
          callback(new Error(t('validation.requiredField.actualEndDate')))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}))

const handleTypeChange = () => {
  form.reason = '' // Reset reason when type changes
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm(t('evaluation.cancelConfirm'), t('common.confirmCancel'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })
    if (props.inDialog) emit('saved')
    else router.push('/evaluations')
  } catch {
    // User cancelled
  }
}

const buildPayload = () => ({
  evaluation_type: form.evaluation_type,
  product_name: form.product_name,
  part_number: form.part_number,
  start_date: form.start_date,
  end_date: form.end_date || null,
  reason: form.reason,
  process_step: serializeProcessSteps(form.process_step),
  evaluation_reason: form.reason, // Map reason to evaluation_reason for backend compatibility
  description: form.description,
  remarks: form.description, // Map description to remarks for backend compatibility
  pgm_version: form.pgm_version,
  pgm_test_time: form.pgm_test_time,
  scs_charger_name: form.scs_charger_name || null,
  head_office_charger_name: form.head_office_charger_name || null,
})

const handleSave = async (submit = false) => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    const loadingRef = submit ? submitting : saving
    loadingRef.value = true

    const payload = buildPayload()

    if (!isEditMode.value) {
      payload.status = submit ? 'in_progress' : 'draft'
    }

    let targetId = evaluationId.value
    if (isEditMode.value) {
      await api.put(`/evaluations/${targetId}`, payload)
      ElMessage.success(t('common.saveSuccess'))
    } else {
      const response = await api.post('/evaluations', payload)
      targetId = response.data?.data?.evaluation?.id
      if (!targetId) {
        console.error('Invalid response structure:', response.data)
        ElMessage.error(t('common.responseError'))
        return
      }
      ElMessage.success(submit ? t('evaluation.submitSuccess') : t('evaluation.saveSuccess'))
    }

    nestedSaveWarnings.value = []
    nestedSaveError.value = null
    await saveNestedProcesses(targetId)

    if (nestedSaveWarnings.value.length) {
      ElMessage.warning('Nested processes saved with warnings. Review details below.')
    } else if (hasBuilderSteps(builderPayload.value)) {
      ElMessage.success('Nested processes saved')
    }

    if (!isEditMode.value) {
      if (props.inDialog) emit('saved')
      else router.push(`/evaluations/${targetId}`)
    } else if (props.inDialog) {
      emit('saved')
    } else {
      router.push(`/evaluations/${targetId}`)
    }
  } catch (error) {
    if (error.name !== 'ValidationError') {
      ElMessage.error(
        isEditMode.value
          ? t('common.saveError')
          : submit
            ? t('evaluation.submitError')
            : t('evaluation.saveError'),
      )
      console.error('Save failed:', error)
    }
  } finally {
    saving.value = false
    submitting.value = false
  }
}

const handleFinish = async () => {
  if (!formRef.value) return
  finishing.value = true // To trigger validation

  try {
    await formRef.value.validate()

    await ElMessageBox.confirm(t('evaluation.finishConfirm'), t('common.confirmAction'), {
      type: 'info',
    })

    await api.put(`/evaluations/${evaluationId.value}/status`, {
      status: 'completed',
    })

    ElMessage.success(t('evaluation.finishSuccess'))
    if (props.inDialog) emit('saved')
    else router.push(`/evaluations/${evaluationId.value}`)
  } catch (error) {
    if (error && error.name !== 'ValidationError' && error !== 'cancel') {
      ElMessage.error(t('evaluation.finishError'))
      console.error('Finish failed:', error)
    }
  } finally {
    finishing.value = false
  }
}

const handleDelete = async () => {
  if (!isEditMode.value) return

  try {
    await ElMessageBox.confirm(t('evaluation.deleteConfirm'), t('common.confirmDelete'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })

    deleting.value = true
    await api.delete(`/evaluations/${evaluationId.value}`)

    ElMessage.success(t('evaluation.deleteSuccess'))
    if (props.inDialog) emit('saved')
    else router.push('/evaluations')
  } catch (error) {
    if (error && error !== 'cancel') {
      ElMessage.error(t('common.deleteError'))
      console.error('Delete failed:', error)
    }
  } finally {
    deleting.value = false
  }
}

// No user fetching in simplified mode

const fetchEvaluation = async () => {
  if (!isEditMode.value) return

  try {
    loading.value = true
    const response = await api.get(`/evaluations/${evaluationId.value}`)
    const evaluation = response.data.data.evaluation

    Object.assign(form, {
      evaluation_type: evaluation.evaluation_type || '',
      product_name: evaluation.product_name || '',
      part_number: evaluation.part_number || '',
      start_date: evaluation.start_date || '',
      end_date: evaluation.end_date || '',
      reason: evaluation.evaluation_reason || evaluation.reason || '',
      process_step: parseProcessSteps(evaluation.process_step),
      description: evaluation.remarks || evaluation.description || '',
      pgm_version: evaluation.pgm_version || '',
      pgm_test_time: evaluation.pgm_test_time || '',
      scs_charger_name: evaluation.scs_charger_name || '',
      head_office_charger_name: evaluation.head_office_charger_name || '',
    })
    const payload = evaluationToBuilderPayload(evaluation)
    builderPayload.value = normalizeBuilderPayload(payload)
    nestedSaveWarnings.value = []
    nestedSaveError.value = null
    processBuilderWarnings.value = []
    await refreshNestedPayload(evaluation.id, evaluation)
  } catch (error) {
    ElMessage.error(t('ui.fetchDataFailed'))
    console.error('Failed to fetch evaluation:', error)
    if (props.inDialog) emit('saved')
    else router.push('/evaluations')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchEvaluation()
})

// Expose methods for dialog footer controls in parent
const saveDraft = async () => {
  await handleSave(false)
}
const submitForm = async () => {
  await handleSave(true)
}
const save = async () => {
  await handleSave(false)
}
const finish = async () => {
  await handleFinish()
}
const deleteEval = async () => {
  await handleDelete()
}

defineExpose({ saveDraft, submitForm, save, finish, deleteEval })
</script>

<style scoped>
.new-evaluation-page {
  padding: 0;
  background: #f5f6f8;
  min-height: 100vh;
}

.page-container {
  max-width: 1200px; /* widen content to reduce side blanks */
  margin: 0 auto;
  padding: 12px 12px 28px; /* slightly tighter padding */
}

.page-header {
  margin-bottom: 32px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-description {
  color: #7f8c8d;
  margin: 0;
  font-size: 16px;
  opacity: 0.8;
}

.evaluation-form {
  max-width: 100%;
}

.form-section {
  margin-bottom: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  overflow: hidden;
}

.form-section:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.form-section :deep(.el-card__header) {
  background: #f7f8fa; /* Flattened, no gradient */
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.form-section :deep(.el-card__body) {
  padding: 32px;
}

.form-section :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.form-section :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.form-section :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.form-section :deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
}

.form-section :deep(.el-textarea__inner) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.form-section :deep(.el-textarea__inner:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.form-section :deep(.el-textarea__inner:focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.form-section :deep(.el-date-editor) {
  border-radius: 12px;
}

.form-section :deep(.el-radio) {
  margin-right: 24px;
  font-weight: 500;
}

.form-section :deep(.el-radio__input.is-checked .el-radio__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.form-section :deep(.el-checkbox) {
  font-weight: 500;
}

.form-section :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.process-selection {
  padding: 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.process-group h4 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-weight: 600;
  font-size: 16px;
}

.process-group .el-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.nested-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nested-process-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  background: #fdfdff;
}

.nested-process-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.nested-process-chain {
  font-size: 13px;
  color: #909399;
}

.nested-process-lots {
  margin: 0;
  padding-left: 18px;
  color: #606266;
  font-size: 13px;
}

.nested-lots-summary {
  margin-bottom: 12px;
}

.nested-lots-summary h4 {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.nested-lots-summary ul {
  margin: 0;
  padding-left: 16px;
  color: #606266;
  font-size: 13px;
}

.nested-summary-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  background: #f9fafc;
}

.nested-step-title {
  font-weight: 600;
  color: #303133;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.nested-step-meta {
  margin-top: 4px;
  color: #606266;
  font-size: 13px;
}

.nested-step-lots {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
}

.nested-failure-count {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
}

.nested-warning {
  margin-top: 12px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.form-actions .el-button {
  min-width: 140px;
  height: 48px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.form-actions .el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.form-actions .el-button--success {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border: none;
}

.form-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.form-actions .el-button--primary:hover {
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.form-actions .el-button--success:hover {
  box-shadow: 0 8px 24px rgba(67, 233, 123, 0.4);
}

.form-actions .el-button--danger {
  background: linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%);
  border-color: transparent;
  color: white;
}

.form-actions .el-button--danger:hover {
  box-shadow: 0 8px 24px rgba(255, 117, 140, 0.4);
}

/* Responsive design */
@media (max-width: 768px) {
  .evaluation-form {
    max-width: 100%;
  }

  .form-actions {
    flex-direction: column;
    align-items: center;
  }

  .form-actions .el-button {
    width: 200px;
  }
}
</style>
