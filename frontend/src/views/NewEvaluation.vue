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

    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="evaluation-form">
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
              <el-input
                v-model="form.process_step"
                :placeholder="$t('evaluation.placeholders.processStep')"
              />
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
            <el-form-item :label="$t('evaluation.headOfficeCharger')" prop="head_office_charger_name">
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
            <el-form-item :label="$t('evaluation.capacity')" prop="capacity">
              <el-input
                v-model="form.capacity"
                :placeholder="$t('evaluation.placeholders.capacity')"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item :label="$t('evaluation.interfaceType')" prop="interface_type">
              <el-select
                v-model="form.interface_type"
                :placeholder="$t('evaluation.placeholders.interfaceType')"
                style="width: 100%"
              >
                <el-option :label="$t('evaluation.interfaceTypes.sata')" value="SATA" />
                <el-option :label="$t('evaluation.interfaceTypes.nvme')" value="NVMe" />
                <el-option :label="$t('evaluation.interfaceTypes.pcie')" value="PCIe" />
                <el-option :label="$t('common.other')" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('evaluation.formFactor')" prop="form_factor">
              <el-select
                v-model="form.form_factor"
                :placeholder="$t('evaluation.placeholders.formFactor')"
                style="width: 100%"
              >
                <el-option :label="$t('evaluation.formFactors.2_5_inch')" value="2.5" />
                <el-option :label="$t('evaluation.formFactors.m2_2280')" value="M.2_2280" />
                <el-option :label="$t('evaluation.formFactors.m2_2242')" value="M.2_2242" />
                <el-option :label="$t('common.other')" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <el-card class="form-section fade-in-up" style="animation-delay: 0.5s">
        <template #header>
          <span>{{ $t('evaluation.evaluationProcesses') }}</span>
        </template>

        <div class="processes-section">
          <div v-for="(process, index) in form.processes" :key="index" class="process-item">
            <div class="process-header">
              <div class="title-with-edit">
                <h4 v-if="!process.editingTitle">
                  {{ process.title || $t('evaluation.process') + ' ' + (index + 1) }}
                </h4>
                <el-input
                  v-else
                  v-model="process.editTitle"
                  size="small"
                  @blur="saveProcessTitle(index)"
                  @keyup.enter="saveProcessTitle(index)"
                  @keyup.escape="cancelProcessTitleEdit(index)"
                />
                <el-button
                  link
                  size="small"
                  :icon="Edit"
                  style="color: #909399; margin-left: 8px"
                  @click="startProcessTitleEdit(index)"
                />
              </div>
              <el-button
                v-if="form.processes.length > 1"
                type="danger"
                size="small"
                :icon="Delete"
                @click="removeProcess(index)"
              >
                {{ $t('evaluation.remove') }}
              </el-button>
            </div>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item
                  :label="$t('evaluation.evalCode')"
                  :prop="`processes.${index}.eval_code`"
                  :rules="[
                    {
                      required: true,
                      message: $t('validation.requiredField.evalCode'),
                      trigger: 'blur',
                    },
                  ]"
                >
                  <el-input
                    v-model="process.eval_code"
                    :placeholder="$t('evaluation.placeholders.evalCode')"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="8">
                <el-form-item
                  :label="$t('evaluation.lotNumber')"
                  :prop="`processes.${index}.lot_number`"
                  :rules="[
                    {
                      required: true,
                      message: $t('validation.requiredField.lotNumber'),
                      trigger: 'blur',
                    },
                  ]"
                >
                  <el-input
                    v-model="process.lot_number"
                    :placeholder="$t('evaluation.placeholders.lotNumber')"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="8">
                <el-form-item
                  :label="$t('evaluation.quantity')"
                  :prop="`processes.${index}.quantity`"
                  :rules="[
                    {
                      required: true,
                      message: $t('validation.requiredField.quantity'),
                      trigger: 'blur',
                    },
                  ]"
                >
                  <el-input-number
                    v-model="process.quantity"
                    :min="1"
                    :placeholder="$t('evaluation.placeholders.quantity')"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item
              :label="$t('evaluation.processFlow')"
              :prop="`processes.${index}.process_description`"
              :rules="[
                {
                  required: true,
                  message: $t('validation.requiredField.processFlow'),
                  trigger: 'blur',
                },
              ]"
            >
              <el-input
                v-model="process.process_description"
                type="textarea"
                :rows="2"
                :placeholder="$t('evaluation.placeholders.processFlow')"
              />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item :label="$t('evaluation.manufacturingTestResults')">
                  <el-input
                    v-model="process.manufacturing_test_results"
                    type="textarea"
                    :rows="2"
                    :placeholder="$t('evaluation.placeholders.manufacturingTestResults')"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item :label="$t('evaluation.defectAnalysisResults')">
                  <el-input
                    v-model="process.defect_analysis_results"
                    type="textarea"
                    :rows="2"
                    :placeholder="$t('evaluation.placeholders.defectAnalysisResults')"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item :label="$t('evaluation.aqlResult')">
              <el-input
                v-model="process.aql_result"
                :placeholder="$t('evaluation.placeholders.aqlResult')"
              />
            </el-form-item>
          </div>

          <el-button type="primary" :icon="Plus" @click="addProcess">
            {{ $t('evaluation.addProcess') }}
          </el-button>
        </div>
      </el-card>

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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const props = defineProps({
  inDialog: { type: Boolean, default: false },
  evaluationId: { type: [String, Number], default: null },
})
const emit = defineEmits(['saved'])
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { nextTick } from 'vue'
import { Plus, Delete, Edit } from '@element-plus/icons-vue'
import api from '../utils/api'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const formRef = ref()
const saving = ref(false)
const submitting = ref(false)
const loading = ref(false)
const deleting = ref(false)
const finishing = ref(false)
// Simplified app: no user directory; chargers are free-text

// Check if in edit mode
const isEditMode = computed(() => !!(props.evaluationId || (route.name === 'EditEvaluation' && route.params.id)))
const evaluationId = computed(() => props.evaluationId || route.params.id)

// Default process template
const defaultProcess = () => ({
  title: '',
  editingTitle: false,
  editTitle: '',
  eval_code: '',
  lot_number: '',
  quantity: 1,
  process_description: '',
  manufacturing_test_results: '',
  defect_analysis_results: '',
  aql_result: '',
  status: 'pending',
})

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
  process_step: '',
  description: '',
  pgm_version: '',
  capacity: '',
  interface_type: '',
  form_factor: '',
  // Start with no default process; user adds explicitly
  processes: [],
  scs_charger_name: '',
  head_office_charger_name: '',
})

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
      required: true,
      message: t('validation.requiredField.processStep'),
      trigger: 'blur',
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

const addProcess = () => {
  form.processes.push(defaultProcess())
}

const startProcessTitleEdit = (index) => {
  const process = form.processes[index]
  process.editingTitle = true
  process.editTitle = process.title || ''
  // Focus the input field after it's rendered
  nextTick(() => {
    const input = document.querySelector(`.process-item:nth-child(${index + 1}) .el-input__inner`)
    if (input) input.focus()
  })
}

const saveProcessTitle = (index) => {
  const process = form.processes[index]
  process.title = process.editTitle.trim()
  process.editingTitle = false
  process.editTitle = ''
}

const cancelProcessTitleEdit = (index) => {
  const process = form.processes[index]
  process.editingTitle = false
  process.editTitle = ''
}

const removeProcess = (index) => {
  if (form.processes.length > 1) {
    form.processes.splice(index, 1)
  }
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
  process_step: form.process_step,
  evaluation_reason: form.reason, // Map reason to evaluation_reason for backend compatibility
  description: form.description,
  remarks: form.description, // Map description to remarks for backend compatibility
  pgm_version: form.pgm_version,
  capacity: form.capacity,
  interface_type: form.interface_type,
  form_factor: form.form_factor,
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

    // Determine status based on action
    if (isEditMode.value) {
      // In edit mode, "Save" keeps the current status, it doesn't revert to draft
      // The backend should handle preserving the status if not provided.
    } else {
      payload.status = submit ? 'in_progress' : 'draft'
    }

    let response
    if (isEditMode.value) {
      response = await api.put(`/evaluations/${evaluationId.value}`, payload)
      ElMessage.success(t('common.saveSuccess'))
      // Redirect to detail view after successful save
      if (props.inDialog) emit('saved')
      else router.push(`/evaluations/${evaluationId.value}`)
    } else {
      response = await api.post('/evaluations', payload)
      ElMessage.success(submit ? t('evaluation.submitSuccess') : t('evaluation.saveSuccess'))
      const targetId = response.data?.data?.evaluation?.id

      // Create evaluation processes if evaluation was created successfully
      if (targetId) {
        const validProcesses = form.processes.filter(
          (process) => process.eval_code && process.lot_number && process.process_description,
        )

        for (const process of validProcesses) {
          try {
            // Create a clean process object without frontend-only fields
            const cleanProcess = {
              title: process.title,
              eval_code: process.eval_code,
              lot_number: process.lot_number,
              quantity: process.quantity,
              process_description: process.process_description,
              manufacturing_test_results: process.manufacturing_test_results,
              defect_analysis_results: process.defect_analysis_results,
              aql_result: process.aql_result,
              status: process.status,
            }
            await api.post(`/evaluations/${targetId}/processes`, cleanProcess)
          } catch (error) {
            console.error('Failed to create process:', error)
            // Continue with other processes even if one fails
          }
        }
      }

      if (targetId) {
        if (props.inDialog) emit('saved')
        else router.push(`/evaluations/${targetId}`)
      } else {
        console.error('Invalid response structure:', response.data)
        ElMessage.error(t('common.responseError'))
      }
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
      process_step: evaluation.process_step || '',
      description: evaluation.remarks || evaluation.description || '',
      pgm_version: evaluation.pgm_version || '',
      capacity: evaluation.capacity || '',
      interface_type: evaluation.interface_type || '',
      form_factor: evaluation.form_factor || '',
      processes: (evaluation.processes || []).map((process) => ({
        ...process,
        editingTitle: false,
        editTitle: '',
      })),
      scs_charger_name: evaluation.scs_charger_name || '',
      head_office_charger_name: evaluation.head_office_charger_name || '',
    })
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
  max-width: 980px;
  margin: 0 auto;
  padding: 16px 16px 40px;
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

.evaluation-form { max-width: 100%; }

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

.process-note {
  margin: 20px 0 0 0;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(25, 118, 210, 0.1) 100%);
  border-left: 4px solid #2196f3;
  color: #1976d2;
  font-size: 14px;
  border-radius: 12px;
  font-weight: 500;
}

.processes-section {
  margin-top: 10px;
}

.process-item {
  border: 1px solid #e6e6e6;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #fafafa;
}

.process-item:last-child {
  margin-bottom: 0;
}

.process-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8e8e8;
}

.process-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.process-content p {
  margin: 8px 0;
  line-height: 1.5;
}

.process-content strong {
  color: #606266;
  font-weight: 600;
}

.process-meta {
  margin-top: 12px !important;
  padding-top: 8px;
  border-top: 1px dashed #e8e8e8;
  color: #909399;
  font-size: 12px;
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

.title-with-edit {
  display: flex;
  align-items: center;
}

.title-with-edit h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.title-with-edit .el-input {
  width: 200px;
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

  .title-with-edit {
    display: flex;
    align-items: center;
  }

  .title-with-edit h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .title-with-edit .el-input {
    width: 200px;
  }
}
</style>
