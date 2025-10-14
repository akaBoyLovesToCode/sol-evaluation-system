<template>
  <el-card class="form-section step-card">
    <template #header>
      <div class="step-header">
        <div class="step-title">
          <el-tag type="info">{{ t('nested.stepTag') }} {{ stepIndex + 1 }}</el-tag>
          <span>{{ step.step_code || t('nested.newStep') }}</span>
          <span v-if="step.step_label" class="step-label">{{ step.step_label }}</span>
        </div>
        <div v-if="!readonly" class="step-actions">
          <el-button size="small" @click.stop="emit('add-step', processIndex, stepIndex)">
            <template #icon><Plus /></template>
            {{ t('nested.addAfter') }}
          </el-button>
          <el-button size="small" @click.stop="emit('duplicate-step', processIndex, stepIndex)">
            <template #icon><DocumentCopy /></template>
            {{ t('nested.duplicate') }}
          </el-button>
          <el-button
            size="small"
            type="danger"
            aria-label="Remove step"
            title="Remove step"
            @click.stop="emit('remove-step', processIndex, stepIndex)"
          >
            <template #icon><Delete /></template>
          </el-button>
        </div>
      </div>
    </template>

    <el-form label-position="top" class="step-form">
      <div class="step-header-row">
        <el-form-item :label="t('nested.stepCode')" required class="header-item code-item">
          <el-select
            v-model="localStep.step_code"
            :placeholder="t('nested.stepCode')"
            :disabled="readonly"
            @change="(value) => emit('code-change', processIndex, stepIndex, value)"
          >
            <el-option
              v-for="option in stepCodeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('nested.stepLabel')" class="header-item label-item">
          <el-input
            v-model="localStep.step_label"
            :placeholder="t('nested.stepLabelPlaceholder')"
            :readonly="readonly"
          />
          <el-link
            v-if="labelSuggestionAvailable"
            type="primary"
            class="suggestion-link"
            :underline="false"
            @click.prevent="emit('apply-suggestion', processIndex, stepIndex)"
          >
            {{ t('nested.applySuggestion', { suggestion: labelSuggestion }) }}
          </el-link>
        </el-form-item>
        <el-form-item :label="t('nested.evalCode')" class="header-item eval-item">
          <el-input
            v-model="localStep.eval_code"
            :placeholder="t('nested.evalCodePlaceholder')"
            :readonly="readonly"
          />
        </el-form-item>
        <el-form-item :label="t('nested.noTestResults')" class="header-item toggle-item">
          <el-switch
            v-model="localStep.results_applicable"
            :active-value="false"
            :inactive-value="true"
            :disabled="readonly"
            @change="(value) => emit('results-change', processIndex, stepIndex, value, true)"
          />
        </el-form-item>
      </div>

      <div class="step-header-row second-row">
        <el-form-item :label="t('nested.appliesToLots')" required class="header-item lots-item">
          <el-select
            v-model="localStep.lot_refs"
            multiple
            collapse-tags
            collapse-tags-tooltip
            :disabled="readonly || !lotOptions.length"
            :placeholder="t('nested.selectLots')"
            @change="(value) => emit('lot-change', processIndex, stepIndex, value)"
          >
            <el-option
              v-for="option in lotOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>

        <template v-if="localStep.results_applicable">
          <el-form-item :label="t('nested.totalUnits')" class="header-item number-item total-item">
            <div class="total-field">
              <el-input-number
                v-model="localStep.total_units"
                :min="0"
                :step="1"
                controls-position="right"
                :disabled="readonly"
                @change="() => emit('total-input', processIndex, stepIndex)"
              />
              <div class="field-hint">{{ autoHint }}</div>
            </div>
          </el-form-item>

          <el-form-item :label="t('nested.passUnits')" class="header-item number-item">
            <el-input-number
              v-model="localStep.pass_units"
              :min="0"
              :step="1"
              controls-position="right"
              disabled
            />
          </el-form-item>

          <el-form-item :label="t('nested.failUnits')" class="header-item number-item">
            <div class="fail-field">
              <el-input-number
                v-model="localStep.fail_units"
                :min="0"
                :step="1"
                controls-position="right"
                :disabled="readonly"
                @change="() => emit('fail-units-change', processIndex, stepIndex)"
              />
              <div v-if="resultsMismatch" class="field-hint warning-hint">
                {{ t('nested.rowsLabel', { count: step.failures.length }) }}
              </div>
              <el-button
                v-if="showAddFailurePrompt"
                class="add-failure-link"
                link
                size="small"
                type="primary"
                :disabled="readonly"
                @click="emit('add-failure', processIndex, stepIndex)"
              >
                {{ t('nested.addFailure') }}
              </el-button>
            </div>
          </el-form-item>
        </template>
      </div>

      <el-form-item :label="t('nested.notes')">
        <el-input
          v-model="localStep.notes"
          type="textarea"
          :rows="2"
          :placeholder="t('nested.notesPlaceholder')"
          :readonly="readonly"
        />
      </el-form-item>
    </el-form>

    <el-alert
      v-if="localStep.results_applicable && totalsMismatch"
      type="warning"
      class="compact-alert"
      show-icon
      :closable="false"
      :title="
        t('nested.inlineMismatch', {
          pass: localStep.pass_units ?? 0,
          fail: localStep.fail_units ?? 0,
          total: localStep.total_units ?? 0,
        })
      "
    />

    <div v-if="localStep.results_applicable && showFailureDetails" class="failure-block">
      <div class="failure-header">
        <h4>{{ t('nested.failureTitle') }}</h4>
        <el-button
          v-if="!readonly"
          size="small"
          @click="emit('add-failure', processIndex, stepIndex)"
        >
          <template #icon><Plus /></template>
          {{ t('nested.addFailure') }}
        </el-button>
      </div>

      <el-table
        :data="step.failures"
        border
        size="small"
        class="failure-table"
        :empty-text="t('nested.emptyFailures')"
      >
        <el-table-column label="#" width="50">
          <template #default="{ row }">
            <span>{{ row.sequence }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('nested.serialNumber')" min-width="160">
          <template #default="{ row }">
            <el-input
              v-model="row.serial_number"
              :placeholder="t('nested.serialNumberPlaceholder')"
              :readonly="readonly"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('nested.failCode')" min-width="120">
          <template #default="{ row, $index }">
            <el-autocomplete
              v-model="row.fail_code_text"
              class="code-input"
              :fetch-suggestions="(query, cb) => queryFailCodes(query, cb)"
              :trigger-on-focus="false"
              :placeholder="t('nested.failCodePlaceholder')"
              :disabled="readonly"
              @select="(item) => emit('assign-fail-code', processIndex, stepIndex, $index, item)"
              @blur="() => emit('normalize-fail-code', processIndex, stepIndex, $index)"
            >
              <template #suffix>
                <el-tooltip
                  v-if="!row.fail_code_id && row.fail_code_text"
                  :content="t('nested.notInDictionary')"
                  placement="top"
                >
                  <el-icon class="code-hint-icon"><WarningFilled /></el-icon>
                </el-tooltip>
              </template>
            </el-autocomplete>
          </template>
        </el-table-column>
        <el-table-column :label="t('nested.failName')" min-width="160">
          <template #default="{ row }">
            <el-input
              v-model="row.fail_code_name_snapshot"
              :placeholder="t('nested.failNamePlaceholder')"
              :readonly="readonly"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('nested.analysisResult')" min-width="260">
          <template #default="{ row }">
            <el-input
              v-model="row.analysis_result"
              type="textarea"
              :rows="2"
              :placeholder="t('nested.analysisPlaceholder')"
              :readonly="readonly"
            />
          </template>
        </el-table-column>
        <el-table-column v-if="!readonly" width="70" fixed="right">
          <template #default="{ $index }">
            <el-button
              type="danger"
              size="small"
              circle
              @click="emit('remove-failure', processIndex, stepIndex, $index)"
            >
              <template #icon><Delete /></template>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-card>
</template>

<script setup>
import { computed, toRefs } from 'vue'

const props = defineProps({
  processIndex: {
    type: Number,
    required: true,
  },
  stepIndex: {
    type: Number,
    required: true,
  },
  process: {
    type: Object,
    required: true,
  },
  step: {
    type: Object,
    required: true,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  dictionaryEntries: {
    type: Array,
    default: () => [],
  },
  labelSuggestions: {
    type: Object,
    default: () => ({}),
  },
  stepCodeOptions: {
    type: Array,
    default: () => [],
  },
  lotOptions: {
    type: Array,
    default: () => [],
  },
  t: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits([
  'add-step',
  'duplicate-step',
  'remove-step',
  'add-failure',
  'remove-failure',
  'assign-fail-code',
  'normalize-fail-code',
  'total-input',
  'lot-change',
  'code-change',
  'results-change',
  'fail-units-change',
  'apply-suggestion',
])

const { step } = toRefs(props)

const labelSuggestion = computed(() => props.labelSuggestions[props.step.step_code])

const labelSuggestionAvailable = computed(() => {
  const suggestion = labelSuggestion.value
  if (!suggestion) return false
  const current = (props.step.step_label || '').trim()
  return current !== suggestion
})

const autoHint = computed(() => {
  const values = props.step.lot_refs.map((ref) => {
    const option = props.process.lots.find((lot) => lot.client_id === ref)
    return Number(option?.quantity || 0)
  })
  if (!props.step.results_applicable || !values.length) {
    return props.t('nested.fromLotsNone')
  }
  const total = values.reduce((sum, value) => sum + value, 0)
  const formula = values.join(' + ')
  return props.t('nested.autoTotalHint', { total, formula })
})

const resultsMismatch = computed(() => {
  if (!props.step.results_applicable) return false
  const failUnits = Number(props.step.fail_units ?? 0)
  return failUnits !== props.step.failures.length
})

const totalsMismatch = computed(() => {
  if (!props.step.results_applicable) return false
  if (
    props.step.total_units === null ||
    props.step.total_units === undefined ||
    props.step.pass_units === null ||
    props.step.pass_units === undefined ||
    props.step.fail_units === null ||
    props.step.fail_units === undefined
  ) {
    return false
  }
  const total = Number(props.step.total_units)
  const passUnits = Number(props.step.pass_units)
  const failUnits = Number(props.step.fail_units)
  return total !== passUnits + failUnits
})

const showAddFailurePrompt = computed(() => {
  return (
    props.step.results_applicable &&
    Number(props.step.fail_units ?? 0) <= 0 &&
    !props.step.failures.length &&
    !props.readonly
  )
})

const showFailureDetails = computed(() => {
  if (!props.step.results_applicable) return false
  return Number(props.step.fail_units ?? 0) > 0 || props.step.failures.length > 0
})

const localStep = step

const queryFailCodes = (queryString, cb) => {
  const normalized = (queryString || '').trim().toUpperCase()
  let results = props.dictionaryEntries
  if (normalized) {
    results = results.filter(
      (entry) => entry.code.includes(normalized) || entry.name?.toUpperCase().includes(normalized),
    )
  }
  cb(results.map((entry) => ({ value: entry.code, ...entry })))
}
</script>

<style scoped>
.step-card {
  border-radius: 8px;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-label {
  font-size: 13px;
  color: #909399;
}

.step-actions {
  display: flex;
  gap: 8px;
}

.step-form {
  width: 100%;
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

.total-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-hint {
  font-size: 12px;
  color: #909399;
}

.warning-hint {
  color: #e6a23c;
}

.fail-field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.add-failure-link {
  padding: 0;
  margin-top: 4px;
}

.failure-block {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.failure-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.compact-alert {
  margin-top: 12px;
}

.code-hint-icon {
  color: #e6a23c;
}

.code-input {
  width: 100%;
}
</style>
