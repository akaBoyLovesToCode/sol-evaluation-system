<template>
  <div class="evaluation-info-blocks">
    <!-- Basic Information -->
    <el-card class="detail-panel info-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('evaluation.basicInformation') }}</span>
          <div class="header-actions">
            <template v-if="!editing && canEdit">
              <el-button size="small" type="primary" class="detail-button" @click="startEdit">
                {{ $t('common.edit') }}
              </el-button>
            </template>
            <template v-else-if="editing">
              <el-button size="small" class="detail-button" @click="cancelEdit">
                {{ $t('common.cancel') }}
              </el-button>
              <el-button
                size="small"
                type="primary"
                class="detail-button"
                :loading="saving"
                @click="saveEdit"
              >
                {{ $t('common.save') }}
              </el-button>
            </template>
          </div>
        </div>
      </template>
      <el-descriptions :column="isMobile ? 1 : 2" border class="detail-descriptions">
        <el-descriptions-item :label="$t('common.status')">
          <template v-if="editing">
            <el-select v-model="editForm.status" style="width: 100%">
              <el-option
                v-for="status in statusOptions"
                :key="status"
                :label="$t(`status.${status}`)"
                :value="status"
              />
            </el-select>
          </template>
          <template v-else>
            <el-tag
              v-if="isSupportedStatus(evaluation.status)"
              :type="getStatusTagType(evaluation.status)"
            >
              {{ $t(`status.${evaluation.status}`) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.evaluationType')">
          <template v-if="editing">
            <el-select
              v-model="editForm.evaluation_type"
              style="width: 100%"
              @change="handleEvaluationTypeChange"
            >
              <el-option value="new_product" :label="$t('evaluation.type.new_product')" />
              <el-option value="mass_production" :label="$t('evaluation.type.mass_production')" />
            </el-select>
          </template>
          <template v-else>
            <el-tag :type="evaluation.evaluation_type === 'new_product' ? 'primary' : 'success'">
              {{ $t(`evaluation.type.${evaluation.evaluation_type}`) }}
            </el-tag>
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.evaluationName')">
          <template v-if="editing">
            <el-input v-model="editForm.evaluation_name" />
          </template>
          <template v-else>
            {{ evaluation.evaluation_name || '-' }}
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.productName')">
          <template v-if="editing">
            <el-input v-model="editForm.product_name" />
          </template>
          <template v-else>
            {{ evaluation.product_name }}
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.partNumber')">
          <template v-if="editing">
            <el-input v-model="editForm.part_number" />
          </template>
          <template v-else>
            {{ evaluation.part_number }}
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.scsCharger')">
          <template v-if="editing">
            <el-input v-model="editForm.scs_charger_name" />
          </template>
          <template v-else>
            {{ evaluation.scs_charger_name || '-' }}
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.headOfficeCharger')">
          <template v-if="editing">
            <el-input v-model="editForm.head_office_charger_name" />
          </template>
          <template v-else>
            {{ evaluation.head_office_charger_name || '-' }}
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.startDate')">
          <template v-if="editing">
            <el-date-picker
              v-model="editForm.start_date"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </template>
          <template v-else>
            {{ formatDate(evaluation.start_date) }}
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.actualEndDate')">
          <template v-if="editing">
            <el-date-picker
              v-model="editForm.end_date"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </template>
          <template v-else>
            {{ evaluation.actual_end_date ? formatDate(evaluation.actual_end_date) : '-' }}
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.processStep')">
          <template v-if="editing">
            <el-select v-model="editForm.process_step" multiple collapse-tags style="width: 100%">
              <el-option
                v-for="step in processStepChoices"
                :key="step"
                :label="step"
                :value="step"
              />
            </el-select>
          </template>
          <template v-else>
            {{ formatProcessSteps(evaluation.process_step) }}
          </template>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.reason')">
          <template v-if="editing">
            <el-select
              v-model="editForm.evaluation_reason"
              multiple
              collapse-tags
              style="width: 100%"
            >
              <el-option
                v-for="opt in reasonOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </template>
          <template v-else>
            {{ getReasonText(evaluation.evaluation_reason) }}
          </template>
        </el-descriptions-item>
      </el-descriptions>

      <div class="description-section">
        <h4 class="section-title">
          {{ $t('evaluation.evaluationDescription') }}
        </h4>
        <template v-if="editing">
          <el-input v-model="editForm.remarks" type="textarea" :rows="3" />
        </template>
        <template v-else>
          <p class="description-value">
            {{ evaluation.remarks || evaluation.description || '-' }}
          </p>
        </template>
      </div>
    </el-card>

    <!-- Technical Specifications -->
    <!-- Process Section -->
    <el-card class="detail-panel info-card">
      <template #header>
        <span>{{ $t('evaluation.processSection') }}</span>
      </template>
      <el-row :gutter="20" class="process-fields">
        <el-col :xs="24" :sm="12">
          <div class="process-field mb-4">
            <label class="process-label">{{ $t('evaluation.testProcess') }}</label>
            <template v-if="editing">
              <el-input
                v-model="editForm.test_process"
                type="textarea"
                :rows="3"
                :placeholder="$t('evaluation.placeholders.testProcess')"
              />
            </template>
            <template v-else>
              <div class="process-text">
                {{ evaluation.test_process || '-' }}
              </div>
            </template>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12">
          <div class="process-field mb-4">
            <label class="process-label">{{ $t('evaluation.vProcess') }}</label>
            <template v-if="editing">
              <el-input
                v-model="editForm.v_process"
                type="textarea"
                :rows="3"
                :placeholder="$t('evaluation.placeholders.vProcess')"
              />
            </template>
            <template v-else>
              <div class="process-text">
                {{ evaluation.v_process || '-' }}
              </div>
            </template>
          </div>
        </el-col>
      </el-row>

      <div class="process-field">
        <label class="process-label">{{ $t('evaluation.pgmLogin') }}</label>
        <template v-if="editing">
          <div class="pgm-login-block flex flex-col gap-2" @paste="handlePgmPaste">
            <el-input
              v-model="editForm.pgm_login_text"
              type="textarea"
              :rows="3"
              :placeholder="$t('evaluation.placeholders.pgmLoginText')"
            />
            <div class="pgm-upload-row flex items-center gap-3 mt-2 flex-wrap">
              <el-upload
                :show-file-list="false"
                :auto-upload="false"
                accept="image/*"
                :before-upload="handlePgmImageUpload"
              >
                <el-button>{{ $t('evaluation.upload') }}</el-button>
              </el-upload>
              <span class="text-gray-400 text-sm">{{ $t('evaluation.pgmLoginPasteHint') }}</span>
              <el-button v-if="editForm.pgm_login_image" text type="danger" @click="clearPgmImage">
                {{ $t('common.delete') }}
              </el-button>
            </div>
            <div
              v-if="editForm.pgm_login_image"
              class="pgm-image-preview mt-2 border border-dashed border-gray-300 rounded p-2 bg-gray-50 max-w-full"
            >
              <el-image
                :src="editForm.pgm_login_image"
                fit="contain"
                :preview-src-list="[editForm.pgm_login_image]"
                class="w-full h-auto max-h-[520px] block"
              />
            </div>
          </div>
        </template>
        <template v-else>
          <div class="process-text">
            {{ evaluation.pgm_login_text || '-' }}
          </div>
          <div
            v-if="evaluation.pgm_login_image"
            class="pgm-image-preview mt-2 border border-dashed border-gray-300 rounded p-2 bg-gray-50 max-w-full"
          >
            <el-image
              :src="evaluation.pgm_login_image"
              fit="contain"
              :preview-src-list="[evaluation.pgm_login_image]"
              class="w-full h-auto max-h-[520px] block"
            />
          </div>
        </template>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const props = defineProps({
  evaluation: { type: Object, required: true },
  canEdit: Boolean,
  processStepOptions: { type: Array, default: () => [] },
})

const emit = defineEmits(['update', 'save-start', 'save-end'])

const { t } = useI18n()
const editing = ref(false)
const saving = ref(false)

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)

const updateWidth = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', updateWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})

const editForm = reactive({
  evaluation_type: '',
  evaluation_name: '',
  product_name: '',
  part_number: '',
  evaluation_reason: [],
  process_step: [],
  scs_charger_name: '',
  head_office_charger_name: '',
  status: '',
  start_date: '',
  end_date: '',
  remarks: '',
  test_process: '',
  v_process: '',
  pgm_login_text: '',
  pgm_login_image: '',
})

const processStepChoices = computed(() => props.processStepOptions)
const supportedStatuses = ['in_progress', 'completed', 'cancelled']

const statusOptions = supportedStatuses
const selectedEvaluationType = computed(() =>
  editing.value ? editForm.evaluation_type : props.evaluation?.evaluation_type,
)

const reasonOptions = computed(() => {
  if (!selectedEvaluationType.value) return []
  if (selectedEvaluationType.value === 'new_product') {
    return [
      { label: t('evaluation.reasons.horizontal_expansion'), value: 'horizontal_expansion' },
      { label: t('evaluation.reasons.direct_development'), value: 'direct_development' },
    ]
  }
  return [
    { label: t('evaluation.reasons.pgm_improvement'), value: 'pgm_improvement' },
    { label: t('evaluation.reasons.firmware_change'), value: 'firmware_change' },
    { label: t('evaluation.reasons.bom_change'), value: 'bom_change' },
    { label: t('evaluation.reasons.pcb'), value: 'pcb' },
    { label: t('evaluation.reasons.customer_requirement'), value: 'customer_requirement' },
    { label: t('evaluation.reasons.nand'), value: 'nand' },
    { label: t('evaluation.reasons.nprr'), value: 'nprr' },
    { label: t('evaluation.reasons.repair'), value: 'repair' },
    { label: t('evaluation.reasons.facility'), value: 'facility' },
    { label: t('evaluation.reasons.other'), value: 'other' },
  ]
})

const parseProcessSteps = (value) => {
  if (!value) return []
  if (Array.isArray(value)) return value.filter(Boolean)
  return String(value)
    .split(/[|,]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const normalizeReasons = (reason) => {
  if (Array.isArray(reason)) return reason.filter(Boolean)
  if (!reason) return []
  return String(reason)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

const syncEditForm = () => {
  if (!props.evaluation) return
  Object.assign(editForm, {
    evaluation_type: props.evaluation.evaluation_type || '',
    evaluation_name: props.evaluation.evaluation_name || '',
    product_name: props.evaluation.product_name || '',
    part_number: props.evaluation.part_number || '',
    evaluation_reason: normalizeReasons(props.evaluation.evaluation_reason),
    process_step: parseProcessSteps(props.evaluation.process_step),
    scs_charger_name: props.evaluation.scs_charger_name || '',
    head_office_charger_name: props.evaluation.head_office_charger_name || '',
    status: props.evaluation.status || 'in_progress',
    start_date: props.evaluation.start_date || '',
    end_date: props.evaluation.actual_end_date || '',
    remarks: props.evaluation.remarks || props.evaluation.description || '',
    test_process: props.evaluation.test_process || '',
    v_process: props.evaluation.v_process || '',
    pgm_login_text: props.evaluation.pgm_login_text || '',
    pgm_login_image: props.evaluation.pgm_login_image || '',
  })
}

const startEdit = () => {
  syncEditForm()
  editing.value = true
}

const cancelEdit = () => {
  editing.value = false
}

const handleEvaluationTypeChange = () => {
  editForm.evaluation_reason = []
}

const saveEdit = async () => {
  emit('save-start')
  saving.value = true
  try {
    // Parent handles the actual API call
    emit('update', { ...editForm })
    editing.value = false
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
    emit('save-end')
  }
}

// Helpers
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

const formatProcessSteps = (value) => {
  const steps = parseProcessSteps(value)
  return steps.length > 0 ? steps.join(' / ') : '-'
}

const getReasonText = (reason) => {
  const reasons = normalizeReasons(reason)
  if (reasons.length === 0) return '-'
  const labels = reasons.map((r) => {
    const key = `evaluation.reasons.${r}`
    const translated = t(key)
    return translated === key ? r : translated
  })
  return labels.join(', ')
}

const getStatusTagType = (status) => {
  const typeMap = {
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'danger',
  }
  return typeMap[status] || 'info'
}

const isSupportedStatus = (status) => supportedStatuses.includes(status)

// Image handling
const fileToDataUrl = (file) =>
  new Promise((resolve, failFileRead) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = failFileRead
    reader.readAsDataURL(file)
  })

const handlePgmPaste = async (event) => {
  const items = event.clipboardData?.items
  if (!items || !items.length) return
  for (const item of items) {
    if (item.type && item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (!file) continue
      try {
        editForm.pgm_login_image = await fileToDataUrl(file)
        ElMessage.success(t('evaluation.operationSuccess'))
      } catch (error) {
        console.error('Paste image failed', error)
        ElMessage.error(t('evaluation.operationFailed'))
      }
      event.preventDefault()
      break
    }
  }
}

const handlePgmImageUpload = async (file) => {
  try {
    editForm.pgm_login_image = await fileToDataUrl(file)
    ElMessage.success(t('evaluation.operationSuccess'))
  } catch (error) {
    console.error('Upload image failed', error)
    ElMessage.error(t('evaluation.operationFailed'))
  }
  return false
}

const clearPgmImage = () => {
  editForm.pgm_login_image = ''
}

defineExpose({ startEdit, cancelEdit })
</script>

<style scoped>
.evaluation-info-blocks {
  --console-line: #d8dee8;
  --console-line-soft: #e8edf3;
  --console-ink: #1f2937;
  --console-muted: #667085;
  --console-blue: #155eef;
}

.detail-panel {
  margin-bottom: 0;
  border: 1px solid var(--console-line);
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
  overflow: hidden;
}

.detail-panel + .detail-panel {
  margin-top: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 750;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-button {
  height: 28px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
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

.detail-descriptions :deep(.el-descriptions__cell) {
  padding: 8px 10px;
}

.detail-descriptions :deep(.el-descriptions__label) {
  width: 132px;
  min-width: 132px;
  background: #f8fafc;
  color: var(--console-muted);
  font-size: 12px;
  font-weight: 650;
}

.detail-descriptions :deep(.el-descriptions__content) {
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 500;
}

.description-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--console-line-soft);
}

.section-title,
.process-label {
  display: block;
  margin: 0 0 6px;
  color: var(--console-muted);
  font-size: 12px;
  font-weight: 700;
}

.description-value,
.process-text {
  margin: 0;
  min-height: 48px;
  padding: 9px 10px;
  border: 1px solid var(--console-line-soft);
  border-radius: 6px;
  background: #f8fafc;
  color: var(--console-ink);
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.process-field {
  margin-bottom: 12px;
}

.process-fields {
  margin-bottom: 0;
}

.pgm-upload-row {
  color: var(--console-muted);
}

.pgm-image-preview {
  border-color: var(--console-line) !important;
  border-radius: 6px !important;
  background: #f8fafc !important;
}
</style>
