<template>
  <div class="evaluations-page">
    <section class="page-head">
      <div class="page-title-block">
        <div>
          <h1 class="page-title">{{ $t('evaluation.console.title') }}</h1>
          <p class="page-description">
            {{ $t('evaluation.console.subtitle') }}
          </p>
        </div>
      </div>
      <div class="page-actions">
        <button class="console-command primary" type="button" @click="openNew()">
          {{ $t('evaluation.new.title') }}
        </button>
      </div>
    </section>

    <section v-loading="kpiLoading" class="kpi-strip">
      <div v-for="item in kpiCards" :key="item.key" class="kpi-card">
        <div class="kpi-label">
          <span>{{ item.label }}</span>
        </div>
        <div class="kpi-value">{{ item.value }}</div>
        <div class="kpi-hint">{{ item.hint }}</div>
      </div>
    </section>

    <section class="saved-views">
      <div class="view-tabs">
        <button
          v-for="view in savedViews"
          :key="view.value"
          type="button"
          class="view-tab"
          :class="{ active: activeOperationalView === view.value }"
          @click="handleSavedView(view.value)"
        >
          {{ view.label }}
        </button>
      </div>
    </section>

    <section class="filters">
      <div class="field">
        <label>{{ $t('evaluation.evaluationNumber') }}</label>
        <el-input
          v-model="searchForm.evaluation_number"
          :placeholder="$t('evaluation.placeholders.evaluationNumber')"
          clearable
        />
      </div>
      <div class="field">
        <label>{{ $t('evaluation.evaluationType') }}</label>
        <el-select
          v-model="searchForm.evaluation_type"
          :placeholder="$t('evaluation.placeholders.evaluationType')"
          clearable
        >
          <el-option :label="$t('evaluation.type.new_product')" value="new_product" />
          <el-option :label="$t('evaluation.type.mass_production')" value="mass_production" />
        </el-select>
      </div>
      <div class="field">
        <label>{{ $t('common.status') }}</label>
        <el-select
          v-model="searchForm.status"
          :placeholder="$t('evaluation.placeholders.status')"
          clearable
        >
          <el-option
            v-for="status in statusOptions"
            :key="status.value"
            :label="status.label"
            :value="status.value"
          />
        </el-select>
      </div>
      <div class="field">
        <label>{{ $t('evaluation.product') }}</label>
        <el-select
          v-model="searchForm.product"
          multiple
          filterable
          allow-create
          default-first-option
          collapse-tags
          collapse-tags-tooltip
          :reserve-keyword="false"
          :placeholder="$t('evaluation.placeholders.product')"
        />
      </div>
      <div class="field">
        <label>{{ $t('evaluation.scsCharger') }}</label>
        <el-select
          v-model="searchForm.scs_charger"
          multiple
          filterable
          allow-create
          default-first-option
          collapse-tags
          collapse-tags-tooltip
          :reserve-keyword="false"
          :placeholder="$t('evaluation.placeholders.scsCharger')"
        />
      </div>
      <div class="field">
        <label>{{ $t('evaluation.headOfficeCharger') }}</label>
        <el-select
          v-model="searchForm.head_office_charger"
          multiple
          filterable
          allow-create
          default-first-option
          collapse-tags
          collapse-tags-tooltip
          :reserve-keyword="false"
          :placeholder="$t('evaluation.placeholders.headOfficeCharger')"
        />
      </div>
      <div class="field date-field">
        <label>{{ $t('evaluation.dateRange') }}</label>
        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          :range-separator="$t('evaluation.placeholders.rangeSeparator')"
          :start-placeholder="$t('evaluation.placeholders.startDate')"
          :end-placeholder="$t('evaluation.placeholders.endDate')"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </div>
      <div class="filter-actions">
        <button
          class="console-command primary dense"
          type="button"
          :aria-label="$t('evaluation.search')"
          :title="$t('evaluation.search')"
          @click="handleSearch"
        >
          {{ $t('evaluation.search') }}
        </button>
        <button
          class="console-command secondary dense"
          type="button"
          :aria-label="$t('evaluation.reset')"
          :title="$t('evaluation.reset')"
          @click="handleReset"
        >
          {{ $t('evaluation.reset') }}
        </button>
      </div>
    </section>

    <section class="table-shell">
      <div class="table-toolbar">
        <div class="table-title">
          <span>{{ $t('evaluation.list') }}</span>
          <span class="table-meta">
            {{ $t('evaluation.console.tableMeta', { total: pagination.total, sort: sortLabel }) }}
          </span>
        </div>
        <div class="table-actions">
          <button
            class="console-command secondary"
            type="button"
            :disabled="exportLoading"
            @click="handleExport('current')"
          >
            {{ $t('evaluation.export') }}
          </button>
          <button
            class="console-command ghost"
            type="button"
            :disabled="exportLoading"
            @click="handleCommand('exportAll')"
          >
            {{ $t('evaluation.exportAll') }}
          </button>
        </div>
      </div>

      <div class="table-scroll">
        <el-table
          v-loading="tableLoading"
          :data="tableData"
          class="operations-table"
          size="small"
          border
          table-layout="fixed"
          @selection-change="handleSelectionChange"
          @sort-change="handleSortChange"
          @row-dblclick="openDetail"
        >
          <el-table-column type="selection" width="44" fixed="left" align="center" />

          <el-table-column
            prop="evaluation_number"
            :label="$t('evaluation.evaluationNumber')"
            width="168"
            fixed="left"
            sortable="custom"
            align="center"
          >
            <template #default="{ row }">
              <el-link type="primary" class="eval-link" @click="openDetail(row)">
                {{ row.evaluation_number }}
              </el-link>
            </template>
          </el-table-column>

          <el-table-column
            prop="evaluation_type"
            :label="$t('evaluation.evaluationType')"
            width="122"
            align="center"
          >
            <template #default="{ row }">
              <el-tag
                effect="plain"
                :type="row.evaluation_type === 'new_product' ? 'primary' : 'success'"
              >
                {{ formatEvaluationType(row.evaluation_type) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            prop="product_name"
            :label="$t('evaluation.product')"
            width="150"
            sortable="custom"
            show-overflow-tooltip
            align="center"
          />

          <el-table-column prop="status" :label="$t('common.status')" width="136" align="center">
            <template #default="{ row }">
              <el-tag effect="plain" :type="getStatusTagType(row.status)">
                {{ formatStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            prop="process_step"
            :label="$t('evaluation.processStep')"
            width="130"
            show-overflow-tooltip
            align="center"
          />

          <el-table-column
            prop="pgm_version"
            :label="$t('evaluation.pgmVersionColumn')"
            width="130"
            sortable="custom"
            show-overflow-tooltip
            align="center"
          >
            <template #default="{ row }">
              {{ row.pgm_version || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="part_number"
            :label="$t('evaluation.partNumber')"
            width="150"
            show-overflow-tooltip
            align="center"
          />

          <el-table-column
            prop="evaluation_reason"
            :label="$t('evaluation.reason')"
            width="150"
            show-overflow-tooltip
            align="center"
          >
            <template #default="{ row }">
              {{ formatReasons(row.evaluation_reason || row.reason) }}
            </template>
          </el-table-column>

          <el-table-column
            prop="remarks"
            :label="$t('evaluation.descriptionLabel')"
            width="240"
            header-align="center"
            align="left"
            class-name="description-column"
          >
            <template #default="{ row }">
              <template v-if="row.remarks">
                <el-tooltip placement="top" effect="dark" popper-class="evaluation-description-tooltip">
                  <template #content>
                    <div class="evaluation-description-tooltip-content">
                      {{ row.remarks }}
                    </div>
                  </template>
                  <span class="evaluation-description-cell">
                    {{ truncateDescription(row.remarks) }}
                  </span>
                </el-tooltip>
              </template>
              <span v-else class="evaluation-description-cell">-</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="scs_charger_name"
            :label="$t('evaluation.scsCharger')"
            width="120"
            show-overflow-tooltip
            align="center"
          />

          <el-table-column
            prop="head_office_charger_name"
            :label="$t('evaluation.headOfficeCharger')"
            width="120"
            show-overflow-tooltip
            align="center"
          />

          <el-table-column
            prop="start_date"
            :label="$t('evaluation.startDate')"
            width="122"
            sortable="custom"
            align="center"
          >
            <template #default="{ row }">
              {{ formatDate(row.start_date) }}
            </template>
          </el-table-column>

          <el-table-column
            prop="actual_end_date"
            :label="$t('evaluation.endDate')"
            width="122"
            align="center"
          >
            <template #default="{ row }">
              {{ row.actual_end_date ? formatDate(row.actual_end_date) : '-' }}
            </template>
          </el-table-column>

          <el-table-column :label="$t('evaluation.tat')" width="82" align="center">
            <template #default="{ row }">
              {{ formatTat(row) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-container">
        <span class="pagination-meta">
          {{
            $t('evaluation.console.paginationMeta', {
              start: pageStart,
              end: pageEnd,
              total: pagination.total,
              size: pagination.size,
            })
          }}
        </span>
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[8, 20, 50, 100]"
          :total="pagination.total"
          layout="sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </section>

    <!-- Popout dialogs -->
    <el-dialog
      v-model="showDetail"
      :title="detailDialogTitle"
      :width="dialogWidth"
      :fullscreen="isMobile"
      destroy-on-close
      :close-on-click-modal="false"
      :close-on-press-escape="true"
    >
      <component
        :is="EvaluationDetail"
        ref="detailRef"
        :evaluation-id="selectedId"
        :in-dialog="true"
        :process-step-options="processStepOptions"
        @edit="onEdit"
      />
      <template #footer>
        <div class="dialog-footer-actions">
          <button class="console-command secondary" type="button" @click="showDetail = false">
            {{ $t('common.close') }}
          </button>
          <button
            class="console-command"
            :class="detailPrimaryActionClass"
            type="button"
            @click="triggerDetailPrimaryAction"
          >
            {{ detailPrimaryActionLabel }}
          </button>
        </div>
      </template>
    </el-dialog>
    <el-dialog
      v-model="showNew"
      :title="isEditing ? $t('evaluation.edit.title') : $t('evaluation.new.title')"
      :width="dialogWidth"
      :fullscreen="isMobile"
      destroy-on-close
      :close-on-click-modal="false"
      :close-on-press-escape="true"
    >
      <component
        :is="NewEvaluation"
        ref="newEvalRef"
        :in-dialog="true"
        :evaluation-id="selectedId"
        :process-step-options="processStepOptions"
        @saved="handleSaved"
      />
      <template #footer>
        <div class="dialog-footer-actions">
          <button class="console-command secondary" type="button" @click="showNew = false">
            {{ $t('common.cancel') }}
          </button>
          <template v-if="!isEditing">
            <button
              class="console-command secondary"
              type="button"
              @click="newEvalRef?.saveDraft()"
            >
              {{ $t('evaluation.saveDraft') }}
            </button>
            <button class="console-command success" type="button" @click="newEvalRef?.submitForm()">
              {{ $t('evaluation.submit') }}
            </button>
          </template>
          <template v-else>
            <button class="console-command danger" type="button" @click="newEvalRef?.deleteEval()">
              {{ $t('common.delete') }}
            </button>
            <button class="console-command primary" type="button" @click="newEvalRef?.save()">
              {{ $t('common.save') }}
            </button>
            <button class="console-command success" type="button" @click="newEvalRef?.finish()">
              {{ $t('evaluation.finish') }}
            </button>
          </template>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, defineAsyncComponent, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../utils/api'
import { buildReliabilitySummary, isReliabilityStep } from '../utils/reliability'
const EvaluationDetail = defineAsyncComponent(() => import('./EvaluationDetail.vue'))
const NewEvaluation = defineAsyncComponent(() => import('./NewEvaluation.vue'))

const { t } = useI18n()

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)
const dialogWidth = computed(() => (isMobile.value ? '100%' : '80%'))

const updateWidth = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', updateWidth)
  fetchPageData()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})

const tableLoading = ref(false)
const kpiLoading = ref(false)
const exportLoading = ref(false)
const showDetail = ref(false)
const showNew = ref(false)
const selectedId = ref(null)
const selectedEvaluationNumber = ref('')
const selectedEvaluationStatus = ref('')
const isEditing = computed(() => !!selectedId.value)
const detailRef = ref(null)
const newEvalRef = ref(null)
const tableData = ref([])
const selectedRows = ref([])
const activeOperationalView = ref('all_active')
const processStepOptions = ['iARTs', 'Aging', 'LI', 'Repair']
const DESCRIPTION_WORD_LIMIT = 16
const DESCRIPTION_CHAR_LIMIT = 80

const kpiData = reactive({
  open_evaluations: 0,
  stale_open_evaluations: 0,
  open_over_10d: 0,
  median_open_age_days: 0,
  created_this_month: 0,
  reliability_failures: 0,
  completed_this_month: 0,
})

const searchForm = reactive({
  evaluation_number: '',
  evaluation_type: '',
  status: '',
  product: [],
  scs_charger: [],
  head_office_charger: [],
  dateRange: null,
})

const pagination = reactive({
  page: 1,
  size: 8,
  total: 0,
})

const sortParams = reactive({
  prop: '',
  order: '',
})

const statusOptions = computed(() => [
  { label: t('status.draft'), value: 'draft' },
  { label: t('status.in_progress'), value: 'in_progress' },
  { label: t('status.completed'), value: 'completed' },
  { label: t('status.paused'), value: 'paused' },
  { label: t('status.cancelled'), value: 'cancelled' },
  { label: t('status.rejected'), value: 'rejected' },
])

const savedViews = computed(() => [
  {
    label: t('evaluation.console.savedViews.allActive', { count: kpiData.open_evaluations }),
    value: 'all_active',
  },
  {
    label: t('evaluation.console.savedViews.noUpdate', {
      count: kpiData.stale_open_evaluations,
    }),
    value: 'no_update_48h',
  },
  {
    label: t('evaluation.console.savedViews.openOver10d', { count: kpiData.open_over_10d }),
    value: 'open_over_10d',
  },
  {
    label: t('evaluation.console.savedViews.reliabilityFailures', {
      count: kpiData.reliability_failures,
    }),
    value: 'has_failures',
  },
])

const formatKpiValue = (value, suffix = '') => {
  if (value === null || value === undefined || value === '') return `0${suffix}`
  return `${value}${suffix}`
}

const kpiCards = computed(() => [
  {
    key: 'open_evaluations',
    label: t('evaluation.console.kpis.openEvaluations.label'),
    value: formatKpiValue(kpiData.open_evaluations),
    hint: t('evaluation.console.kpis.openEvaluations.hint'),
  },
  {
    key: 'stale_open_evaluations',
    label: t('evaluation.console.kpis.staleOpenEvaluations.label'),
    value: formatKpiValue(kpiData.stale_open_evaluations),
    hint: t('evaluation.console.kpis.staleOpenEvaluations.hint'),
  },
  {
    key: 'open_over_10d',
    label: t('evaluation.console.kpis.openOver10d.label'),
    value: formatKpiValue(kpiData.open_over_10d),
    hint: t('evaluation.console.kpis.openOver10d.hint'),
  },
  {
    key: 'median_open_age_days',
    label: t('evaluation.console.kpis.medianOpenAge.label'),
    value: formatKpiValue(kpiData.median_open_age_days, t('evaluation.console.daySuffix')),
    hint: t('evaluation.console.kpis.medianOpenAge.hint'),
  },
  {
    key: 'created_this_month',
    label: t('evaluation.console.kpis.createdThisMonth.label'),
    value: formatKpiValue(kpiData.created_this_month),
    hint: t('evaluation.console.kpis.createdThisMonth.hint'),
  },
  {
    key: 'completed_this_month',
    label: t('evaluation.console.kpis.completedThisMonth.label'),
    value: formatKpiValue(kpiData.completed_this_month),
    hint: t('evaluation.console.kpis.completedThisMonth.hint'),
  },
])

const sortLabel = computed(() => {
  const directionKey = sortParams.order === 'ascending' ? 'asc' : 'desc'
  const direction = t(`evaluation.console.sort.${directionKey}`)
  if (!sortParams.prop) {
    return t('evaluation.console.sort.defaultCreatedDesc')
  }
  const fieldKey = `evaluation.console.sort.fields.${sortParams.prop}`
  const translatedField = t(fieldKey)
  const field = translatedField === fieldKey ? sortParams.prop : translatedField
  return t('evaluation.console.sort.sortedBy', { field, direction })
})

const pageStart = computed(() => {
  if (pagination.total === 0) return 0
  return (pagination.page - 1) * pagination.size + 1
})

const pageEnd = computed(() => Math.min(pagination.page * pagination.size, pagination.total))

const detailDialogTitle = computed(() => selectedEvaluationNumber.value || t('evaluation.title'))
const terminalStatuses = ['completed', 'cancelled', 'rejected']
const detailStatus = computed(
  () => detailRef.value?.evaluation?.status || selectedEvaluationStatus.value || '',
)
const detailPrimaryActionIsReopen = computed(() => terminalStatuses.includes(detailStatus.value))
const detailPrimaryActionLabel = computed(() =>
  detailPrimaryActionIsReopen.value ? t('evaluation.reopen') : t('evaluation.cancel'),
)
const detailPrimaryActionClass = computed(() =>
  detailPrimaryActionIsReopen.value ? 'primary' : 'danger',
)

const translateOrFallback = (key, fallback, params = {}) => {
  const translated = t(key, params)
  return translated === key ? fallback : translated
}

const normalizeMultiValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean)
  }
  if (!value) return []
  return String(value)
    .split(/[|,]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const toNumberSafe = (value) => {
  if (value === null || value === undefined || value === '') {
    return null
  }
  const normalized = typeof value === 'string' ? value.replace(/,/g, '') : value
  const num = Number(normalized)
  return Number.isFinite(num) ? num : null
}

const normalizeReasons = (value) => {
  if (Array.isArray(value)) return value.filter(Boolean)
  if (!value) return []
  return String(value)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

const formatReasons = (value) => {
  const reasons = normalizeReasons(value)
  if (reasons.length === 0) return '-'
  const labels = reasons.map((reason) => {
    const key = `evaluation.reasons.${reason}`
    const translated = t(key)
    return translated === key ? reason : translated
  })
  return labels.join(', ')
}

const truncateDescription = (text) => {
  if (!text) {
    return ''
  }
  const trimmed = text.trim()
  if (!trimmed) {
    return ''
  }
  const words = trimmed.split(/\s+/)
  if (words.length > DESCRIPTION_WORD_LIMIT) {
    return `${words.slice(0, DESCRIPTION_WORD_LIMIT).join(' ')}…`
  }
  if (trimmed.length > DESCRIPTION_CHAR_LIMIT) {
    return `${trimmed.slice(0, DESCRIPTION_CHAR_LIMIT)}…`
  }
  return trimmed
}

const buildResultSummary = (results) => {
  if (!Array.isArray(results) || results.length === 0) {
    return ''
  }

  const buildLegacyReliabilitySummary = (result) => {
    if (!result?.result_data || typeof result.result_data !== 'object') {
      return ''
    }

    const data = result.result_data
    const totalUnits =
      toNumberSafe(data.total_units) ??
      toNumberSafe(data.test_units) ??
      toNumberSafe(data.total) ??
      toNumberSafe(data.sample_size)
    const failUnits =
      toNumberSafe(data.fail_units) ??
      toNumberSafe(data.fail) ??
      toNumberSafe(data.fail_count) ??
      toNumberSafe(data.failures) ??
      0
    const passUnits = toNumberSafe(data.pass_units ?? data.pass)

    if (!Number.isFinite(totalUnits) || totalUnits <= 0) {
      return ''
    }

    const stepCodeCandidate = (data.step_code || result.result_type || '').toString().toUpperCase()
    if (!isReliabilityStep(stepCodeCandidate) && result.result_type !== 'aql') {
      return ''
    }
    const stepCode = isReliabilityStep(stepCodeCandidate) ? stepCodeCandidate : 'AQL'

    return buildReliabilitySummary(
      {
        step_code: stepCode,
        fail_units: failUnits,
        total_units: totalUnits,
        test_units: totalUnits,
        pass_units: passUnits ?? undefined,
        metrics: {
          ...data,
          fail: failUnits,
          total: totalUnits,
          test_units: totalUnits,
        },
      },
      t,
    )
  }

  return results
    .map((result, index) => {
      const parts = []
      const typeLabel = result.result_type
        ? t(`evaluation.processes.${result.result_type}`) || result.result_type
        : ''
      if (typeLabel) {
        parts.push(typeLabel)
      }
      if (result.result_status) {
        const statusLabel =
          t(`evaluation.resultStatus.${result.result_status}`) || result.result_status
        parts.push(`${t('common.status')}: ${statusLabel}`)
      }
      const testDate = formatDateForExport(result.test_date)
      if (testDate) {
        parts.push(`${t('evaluation.testDate')}: ${testDate}`)
      }
      if (result.comments) {
        parts.push(`${t('evaluation.resultNotesLabel')}: ${result.comments}`)
      }

      const reliabilitySummary = buildLegacyReliabilitySummary(result)
      if (reliabilitySummary) {
        parts.push(reliabilitySummary)
      } else if (result.result_data) {
        let dataString = ''
        if (typeof result.result_data === 'string') {
          dataString = result.result_data
        } else {
          try {
            dataString = JSON.stringify(result.result_data)
          } catch {
            dataString = String(result.result_data)
          }
        }
        parts.push(`${t('evaluation.resultDataLabel')}: ${dataString}`)
      }
      return `${index + 1}. ${parts.filter(Boolean).join(' | ')}`
    })
    .join(' ; ')
}

const fetchDetailedEvaluations = async (rows) => {
  const ids = Array.from(
    new Set(rows.map((row) => row.id).filter((id) => id !== undefined && id !== null)),
  )

  if (ids.length === 0) {
    return { detailMap: new Map(), failedIds: [] }
  }

  const detailMap = new Map()
  const failedIds = []

  await Promise.all(
    ids.map(async (id) => {
      try {
        const response = await api.get(`/evaluations/${id}`)
        const evaluation = response.data?.data?.evaluation
        if (evaluation) {
          detailMap.set(id, evaluation)
        } else {
          failedIds.push(id)
        }
      } catch (error) {
        console.error(`Failed to fetch evaluation ${id} for export`, error)
        failedIds.push(id)
      }
    }),
  )

  return { detailMap, failedIds }
}

const fetchNestedProcesses = async (rows) => {
  const ids = Array.from(
    new Set(rows.map((row) => row.id).filter((id) => id !== undefined && id !== null)),
  )

  if (ids.length === 0) {
    return { nestedMap: new Map() }
  }

  const nestedMap = new Map()

  await Promise.all(
    ids.map(async (id) => {
      try {
        const response = await api.get(`/evaluations/${id}/processes/nested`)
        const responseData = response.data?.data
        const payload = responseData?.payload
        if (payload) {
          nestedMap.set(id, payload.processes || [])
        }
      } catch (nestedError) {
        console.error(`Failed to fetch nested processes for evaluation ${id}`, nestedError)
      }
    }),
  )

  return { nestedMap }
}

const buildNestedResultSummary = (processes) => {
  const segments = []

  if (Array.isArray(processes)) {
    processes.forEach((process, processIndex) => {
      const processName =
        process?.name ||
        translateOrFallback('evaluation.defaultProcessName', `Process ${processIndex + 1}`, {
          index: processIndex + 1,
        })
      if (!Array.isArray(process?.steps)) {
        return
      }

      const stepSegments = []

      process.steps.forEach((step) => {
        const stepWord = translateOrFallback('nested.stepTag', 'Step')
        const stepName =
          step.step_label || step.step_code || `${stepWord} ${step.order_index || ''}`

        if (step.results_applicable === false) {
          stepSegments.push(
            `${stepName}: ${translateOrFallback(
              'nested.summary.noResults',
              'No test results recorded',
            )}`,
          )
          return
        }

        const reliabilitySummary = buildReliabilitySummary(step, t)
        if (reliabilitySummary) {
          stepSegments.push(`${stepName}: ${reliabilitySummary}`)
          return
        }

        const metrics = []
        if (step.total_units !== undefined && step.total_units !== null) {
          metrics.push(
            `${translateOrFallback('nested.totalUnitsLabel', 'Total')} ${step.total_units}`,
          )
        }
        if (step.pass_units !== undefined && step.pass_units !== null) {
          metrics.push(`${translateOrFallback('nested.passUnitsLabel', 'Pass')} ${step.pass_units}`)
        }
        if (step.fail_units !== undefined && step.fail_units !== null) {
          metrics.push(`${translateOrFallback('nested.failUnitsLabel', 'Fail')} ${step.fail_units}`)
        }
        if (Array.isArray(step.failures) && step.failures.length > 0) {
          const failureText = t('nested.summary.failuresCount', { count: step.failures.length })
          metrics.push(
            failureText !== 'nested.summary.failuresCount'
              ? failureText
              : `Failures: ${step.failures.length}`,
          )
        }
        if (metrics.length > 0) {
          stepSegments.push(`${stepName}: ${metrics.join(', ')}`)
        }
      })

      if (stepSegments.length > 0) {
        segments.push(`${processName}: ${stepSegments.join(' ; ')}`)
      }
    })
  }

  return segments.join(' ; ')
}

const buildEvaluationParams = ({
  page = pagination.page,
  perPage = pagination.size,
  includePagination = true,
  includeSort = true,
  includeOperationalView = true,
} = {}) => {
  const params = {}

  if (includePagination) {
    params.page = page
    params.per_page = perPage
  }

  if (includeOperationalView && activeOperationalView.value) {
    params.operational_view = activeOperationalView.value
  }
  if (searchForm.evaluation_number) {
    params.evaluation_number = searchForm.evaluation_number
  }
  if (searchForm.evaluation_type) {
    params.evaluation_type = searchForm.evaluation_type
  }
  if (searchForm.status) {
    params.status = searchForm.status
  }
  const products = normalizeMultiValue(searchForm.product)
  if (products.length > 0) {
    params.product = products.join(',')
  }
  const scsChargers = normalizeMultiValue(searchForm.scs_charger)
  if (scsChargers.length > 0) {
    params.scs_charger_name = scsChargers.join(',')
  }
  const headCharger = normalizeMultiValue(searchForm.head_office_charger)
  if (headCharger.length > 0) {
    params.head_office_charger_name = headCharger.join(',')
  }
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    params.start_date_from = searchForm.dateRange[0]
    params.start_date_to = searchForm.dateRange[1]
  }
  if (includeSort && sortParams.prop) {
    params.sort_by = sortParams.prop
    params.sort_order = sortParams.order === 'ascending' ? 'asc' : 'desc'
  }

  return params
}

const fetchKpis = async () => {
  try {
    kpiLoading.value = true
    const response = await api.get('/evaluations/kpis', {
      params: buildEvaluationParams({
        includePagination: false,
        includeSort: false,
        includeOperationalView: false,
      }),
    })
    Object.assign(kpiData, response.data?.data || {})
  } catch (error) {
    ElMessage.error(t('ui.fetchListFailed'))
    console.error('Failed to fetch evaluation KPIs:', error)
  } finally {
    kpiLoading.value = false
  }
}

const fetchEvaluations = async () => {
  try {
    tableLoading.value = true
    const params = buildEvaluationParams()
    const response = await api.get('/evaluations', { params })
    const data = response.data.data

    // 后端返回的数据结构是 { data: { evaluations: [...], pagination: {...} } }
    tableData.value = data.evaluations || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error(t('ui.fetchListFailed'))
    console.error('Failed to fetch evaluations:', error)
  } finally {
    tableLoading.value = false
  }
}

const fetchPageData = async () => {
  await Promise.all([fetchEvaluations(), fetchKpis()])
}

const openDetail = (rowOrId) => {
  const id = typeof rowOrId === 'object' ? rowOrId?.id : rowOrId
  selectedId.value = id
  if (typeof rowOrId === 'object' && rowOrId) {
    selectedEvaluationNumber.value = rowOrId.evaluation_number || ''
    selectedEvaluationStatus.value = rowOrId.status || ''
  } else {
    const match = tableData.value.find((row) => row.id === id)
    selectedEvaluationNumber.value = match?.evaluation_number || ''
    selectedEvaluationStatus.value = match?.status || ''
  }
  showDetail.value = true
}

const openNew = () => {
  selectedId.value = null
  showNew.value = true
}

const onEdit = (id) => {
  showDetail.value = false
  selectedId.value = id
  showNew.value = true
}

const handleSaved = () => {
  showNew.value = false
  fetchPageData()
}

const triggerDetailPrimaryAction = () => {
  if (detailPrimaryActionIsReopen.value) {
    detailRef.value?.promptReopenEvaluation?.()
    return
  }
  detailRef.value?.promptCancelEvaluation?.()
}

const handleSearch = () => {
  pagination.page = 1
  fetchPageData()
}

const handleReset = () => {
  searchForm.evaluation_number = ''
  searchForm.evaluation_type = ''
  searchForm.status = ''
  searchForm.product = []
  searchForm.scs_charger = []
  searchForm.head_office_charger = []
  searchForm.dateRange = null
  activeOperationalView.value = 'all_active'
  pagination.page = 1
  fetchPageData()
}

const handleSavedView = (view) => {
  activeOperationalView.value = view
  pagination.page = 1
  fetchEvaluations()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchEvaluations()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchEvaluations()
}

const handleSortChange = ({ prop, order }) => {
  sortParams.prop = prop
  sortParams.order = order
  fetchEvaluations()
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleCommand = (command) => {
  if (command === 'exportAll') {
    ElMessageBox.confirm(t('evaluation.exportAllConfirm'), t('common.confirm'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })
      .then(() => {
        handleExport('all')
      })
      .catch(() => {})
  }
}

const handleExport = async (type = 'current') => {
  try {
    exportLoading.value = true

    let dataToExport = []

    if (type === 'all') {
      const params = buildEvaluationParams({ page: 1, perPage: 100000 })

      const response = await api.get('/evaluations', { params })
      dataToExport = response.data.data.evaluations || []
    } else {
      // Determine data to export: selected rows or all data
      dataToExport = selectedRows.value.length > 0 ? selectedRows.value : tableData.value
    }

    if (dataToExport.length === 0) {
      ElMessage.warning(t('ui.noDataToExport'))
      return
    }

    const { detailMap, failedIds } = await fetchDetailedEvaluations(dataToExport)
    const { nestedMap } = await fetchNestedProcesses(dataToExport)
    if (failedIds.length > 0) {
      ElMessage.warning(
        t('evaluation.exportDetailWarning', {
          count: failedIds.length,
        }),
      )
    }

    // Show message about what's being exported
    const exportMessage =
      selectedRows.value.length > 0
        ? `导出选中的 ${selectedRows.value.length} 条评价记录`
        : `导出全部 ${tableData.value.length} 条评价记录`
    console.log(exportMessage)

    // Prepare CSV data
    const sanitizeCell = (value) => {
      if (value === null || value === undefined) {
        return '""'
      }
      const text = typeof value === 'string' ? value : String(value)
      const normalized = text.replace(/\r?\n|\r/g, ' ').trim()
      const csvValue = normalized.startsWith('-') ? `="${normalized}"` : normalized
      return `"${csvValue.replace(/"/g, '""')}"`
    }

    const resolveEvaluationType = (value) => {
      if (!value) return ''
      const key = `evaluation.type.${value}`
      const translated = t(key)
      return translated !== key ? translated : value
    }

    const resolveStatus = (value) => {
      if (!value) return ''
      const key = `status.${value}`
      const translated = t(key)
      return translated !== key ? translated : value
    }

    const formatReasonsForExport = (value) => {
      const reasons = normalizeReasons(value)
      if (reasons.length === 0) return ''
      return reasons
        .map((reason) => {
          const key = `evaluation.reasons.${reason}`
          const translated = t(key)
          return translated !== key ? translated : reason
        })
        .join(', ')
    }

    const exportFields = [
      {
        header: t('common.id'),
        value: (source) => source.id ?? '',
      },
      {
        header: t('evaluation.evaluationNumber'),
        value: (source) => source.evaluation_number || '',
      },
      {
        header: t('evaluation.evaluationType'),
        value: (source) => resolveEvaluationType(source.evaluation_type),
      },
      {
        header: t('evaluation.product'),
        value: (source) => source.product_name || '',
      },
      {
        header: t('evaluation.partNumber'),
        value: (source) => source.part_number || '',
      },
      {
        header: t('evaluation.reason'),
        value: (source) => formatReasonsForExport(source.evaluation_reason || source.reason),
      },
      {
        header: t('evaluation.descriptionLabel'),
        value: (source) => source.remarks || '',
      },
      {
        header: t('evaluation.testProcess'),
        value: (source, detailed) => detailed?.test_process || source.test_process || '',
      },
      {
        header: t('evaluation.processStep'),
        value: (source) => source.process_step || '',
      },
      {
        header: t('evaluation.pgmVersion'),
        value: (source) => source.pgm_version || '',
      },
      {
        header: t('evaluation.scsCharger'),
        value: (source) => source.scs_charger_name || '',
      },
      {
        header: t('evaluation.headOfficeCharger'),
        value: (source) => source.head_office_charger_name || '',
      },
      {
        header: t('common.status'),
        value: (source) => resolveStatus(source.status),
      },
      {
        header: t('evaluation.startDate'),
        value: (source) => formatDateForExport(source.start_date),
      },
      {
        header: t('evaluation.endDate'),
        value: (source) => formatDateForExport(source.actual_end_date),
      },
      {
        header: t('evaluation.tat'),
        value: (source) => formatTat(source) || '',
      },
      {
        header: t('evaluation.createdAt'),
        value: (source) => formatDateForExport(source.created_at),
      },
      {
        header: t('evaluation.updatedAt'),
        value: (source) => formatDateForExport(source.updated_at),
      },
      {
        header: t('evaluation.resultSummary'),
        value: (_source, detailed, nestedProcesses) => {
          const legacyResultSummary = buildResultSummary(detailed?.results ?? [])
          const nestedResultSummary = buildNestedResultSummary(nestedProcesses)
          return [legacyResultSummary, nestedResultSummary].filter(Boolean).join(' || ')
        },
      },
    ]

    const headers = exportFields.map((field) => sanitizeCell(field.header)).join(',')

    const rows = dataToExport.map((row) => {
      const detailed = detailMap.get(row.id)
      const nestedProcesses = nestedMap.get(row.id) || []
      const exportSource = detailed ? { ...row, ...detailed } : row

      const baseValues = exportFields.map((field) =>
        sanitizeCell(field.value(exportSource, detailed, nestedProcesses)),
      )

      return baseValues.join(',')
    })

    const csvContent = [headers, ...rows].join('\n')

    // Create and download CSV file
    const blob = new Blob(['\uFEFF' + csvContent], {
      type: 'text/csv;charset=utf-8;',
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const filename =
      selectedRows.value.length > 0
        ? `evaluations_selected_${new Date().toISOString().split('T')[0]}.csv`
        : `evaluations_all_${new Date().toISOString().split('T')[0]}.csv`
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success(t('evaluation.exportSuccess') || '导出成功')
  } catch (error) {
    ElMessage.error(t('evaluation.exportError') || '导出失败')
    console.error('Export failed:', error)
  } finally {
    exportLoading.value = false
  }
}

// 权限检查函数

const getStatusTagType = (status) => {
  const typeMap = {
    draft: 'info',
    in_progress: 'primary',
    pending_approval: 'warning',
    pending_part_approval: 'warning',
    pending_group_approval: 'warning',
    completed: 'success',
    paused: 'info',
    cancelled: 'danger',
    rejected: 'danger',
  }
  return typeMap[status] || 'info'
}

const formatEvaluationType = (value) => {
  if (!value) return '-'
  const key = `evaluation.type.${value}`
  const translated = t(key)
  return translated === key ? value : translated
}

const formatStatusLabel = (status) => {
  if (!status) return '-'
  const key = `status.${status}`
  const translated = t(key)
  if (translated !== key) return translated
  return status.replace(/_/g, ' ')
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

const formatTat = (row) => {
  if (!row) {
    return '-'
  }

  // Prefer the explicit evaluation start date; fall back to creation time if missing.
  const startDateSource = row.start_date || row.created_at

  if (!startDateSource || !row.actual_end_date) {
    return '-'
  }

  const start = new Date(startDateSource)
  const end = new Date(row.actual_end_date)

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    return '-'
  }

  // Normalize both dates to midnight UTC so we measure whole days only.
  const startUtcMidnight = Date.UTC(start.getUTCFullYear(), start.getUTCMonth(), start.getUTCDate())
  const endUtcMidnight = Date.UTC(end.getUTCFullYear(), end.getUTCMonth(), end.getUTCDate())

  const diffDays = Math.max(
    0,
    Math.round((endUtcMidnight - startUtcMidnight) / (1000 * 60 * 60 * 24)),
  )

  return `${diffDays}d`
}

const formatDateForExport = (value) => {
  if (value === null || value === undefined) {
    return ''
  }
  const date = value instanceof Date ? value : new Date(value)
  if (!Number.isNaN(date.getTime())) {
    return date.toISOString().split('T')[0]
  }
  return String(value)
}

</script>

<style scoped>
.evaluations-page {
  --console-bg: #f5f7fa;
  --console-panel: #ffffff;
  --console-line: #d8dee8;
  --console-line-soft: #e8edf3;
  --console-ink: #1f2937;
  --console-muted: #667085;
  --console-blue: #155eef;
  --console-blue-dark: #0f48b8;
  --console-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
  padding: 0;
  background: var(--console-bg);
  min-height: 100vh;
  color: var(--console-ink);
  font-size: 13px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.page-title-block {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  margin: 0 0 4px;
  color: var(--console-ink);
  font-size: 22px;
  font-weight: 750;
  line-height: 1.2;
  letter-spacing: 0;
}

.page-description {
  margin: 0;
  color: var(--console-muted);
  font-size: 13px;
}

.page-actions,
.table-actions,
.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.console-command {
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 0 11px;
  border: 1px solid var(--console-line);
  border-radius: 6px;
  background: #fff;
  color: #344054;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
  box-shadow: none;
}

.console-command:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #b9c3d3;
  color: #1f2937;
}

.console-command.primary {
  background: var(--console-blue);
  border-color: var(--console-blue);
  color: #fff;
}

.console-command.primary:hover:not(:disabled) {
  background: var(--console-blue-dark);
  border-color: var(--console-blue-dark);
  color: #fff;
}

.console-command.success {
  background: #14804a;
  border-color: #14804a;
  color: #fff;
}

.console-command.success:hover:not(:disabled) {
  background: #0f6b3d;
  border-color: #0f6b3d;
  color: #fff;
}

.console-command.danger {
  background: #b42318;
  border-color: #b42318;
  color: #fff;
}

.console-command.danger:hover:not(:disabled) {
  background: #912018;
  border-color: #912018;
  color: #fff;
}

.console-command.secondary {
  background: #fff;
}

.console-command.ghost {
  background: transparent;
  border-color: transparent;
}

.console-command.ghost:hover:not(:disabled) {
  background: #f2f5f9;
  border-color: #e1e7ef;
}

.console-command.dense {
  min-width: 82px;
}

.console-command:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.console-command .el-icon {
  font-size: 14px;
}

.console-icon-command {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: 1px solid var(--console-line);
  border-radius: 6px;
  background: #fff;
  color: #344054;
  cursor: pointer;
  font: inherit;
  box-shadow: none;
}

.console-icon-command:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #b9c3d3;
  color: #1f2937;
}

.console-icon-command.primary {
  background: var(--console-blue);
  border-color: var(--console-blue);
  color: #fff;
}

.console-icon-command.primary:hover:not(:disabled) {
  background: var(--console-blue-dark);
  border-color: var(--console-blue-dark);
  color: #fff;
}

.console-icon-command .el-icon {
  font-size: 15px;
}

.dialog-footer-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.kpi-strip {
  display: grid;
  grid-template-columns: repeat(6, minmax(140px, 1fr));
  gap: 8px;
  margin-bottom: 10px;
}

.kpi-card {
  min-height: 78px;
  padding: 10px 12px;
  background: var(--console-panel);
  border: 1px solid var(--console-line);
  border-radius: 6px;
}

.kpi-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
  color: var(--console-muted);
  font-size: 12px;
}

.kpi-value {
  color: var(--console-ink);
  font-size: 24px;
  font-weight: 750;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.kpi-hint {
  margin-top: 5px;
  color: var(--console-muted);
  font-size: 12px;
}

.saved-views,
.filters,
.table-shell {
  background: var(--console-panel);
  border: 1px solid var(--console-line);
  border-radius: 6px;
  box-shadow: var(--console-shadow);
}

.saved-views {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 9px 10px;
  margin-bottom: 8px;
}

.view-tabs {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.view-tab {
  height: 28px;
  padding: 0 10px;
  border: 1px solid transparent;
  border-radius: 5px;
  background: transparent;
  color: var(--console-muted);
  cursor: pointer;
  font: inherit;
  font-weight: 650;
}

.view-tab.active {
  background: #eef4ff;
  color: var(--console-blue-dark);
  border-color: #c7d7fe;
}

.filters {
  display: grid;
  grid-template-columns: 190px 132px 126px 160px 160px 160px 230px auto;
  gap: 8px;
  align-items: end;
  padding: 10px;
  margin-bottom: 10px;
}

.field label {
  display: block;
  margin-bottom: 4px;
  color: var(--console-muted);
  font-size: 11px;
  font-weight: 650;
}

.field :deep(.el-input__wrapper),
.field :deep(.el-select__wrapper) {
  min-height: 32px;
  border-radius: 6px;
  box-shadow: 0 0 0 1px var(--console-line) inset;
}

.field :deep(.el-input__wrapper:hover),
.field :deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #b9c3d3 inset;
}

.field :deep(.el-input__wrapper.is-focus),
.field :deep(.el-select__wrapper.is-focused) {
  box-shadow:
    0 0 0 1px #84adff inset,
    0 0 0 3px #eff4ff;
}

.date-field :deep(.el-date-editor) {
  width: 100%;
  height: 32px;
}

.filter-actions {
  align-self: end;
  white-space: nowrap;
}

.table-shell {
  overflow: hidden;
}

.table-toolbar {
  min-height: 44px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--console-line);
  background: #fff;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  color: var(--console-ink);
  font-weight: 750;
}

.table-meta,
.pagination-meta {
  color: var(--console-muted);
  font-size: 12px;
  font-weight: 500;
}

.table-scroll {
  width: 100%;
  overflow: hidden;
}

.operations-table {
  width: 100%;
}

.operations-table :deep(.el-table__inner-wrapper::before),
.operations-table :deep(.el-table__border-left-patch) {
  background: var(--console-line-soft);
}

.operations-table :deep(.el-table__header th) {
  height: 34px;
  background: #f8fafc;
  color: #475467;
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.operations-table :deep(.el-table__row .el-table__cell) {
  height: 40px;
  padding: 4px 0;
  color: var(--console-ink);
  background: #fff;
}

.operations-table :deep(.el-table__cell .cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 24px;
  line-height: 1.35;
}

.operations-table :deep(.description-column .cell) {
  justify-content: flex-start;
  text-align: left;
}

.operations-table :deep(.el-table__row:hover > .el-table__cell) {
  background: #f9fbff;
}

.operations-table :deep(.el-table-fixed-column--left),
.operations-table :deep(.el-table__cell.is-left) {
  background: #fff;
  background-clip: padding-box;
}

.operations-table :deep(th.el-table-fixed-column--left),
.operations-table :deep(th.el-table__cell.is-left) {
  background: #f8fafc;
  background-clip: padding-box;
}

.operations-table :deep(.el-table__row:hover > .el-table-fixed-column--left),
.operations-table :deep(.el-table__row:hover > .el-table__cell.is-left) {
  background: #f9fbff;
}

.operations-table :deep(.el-table-fixed-column--left:last-of-type) {
  box-shadow: 1px 0 0 var(--console-line-soft), 12px 0 18px -18px rgba(16, 24, 40, 0.45);
}

.eval-link {
  font-weight: 750;
}

.evaluation-description-cell {
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.evaluation-description-tooltip) {
  max-width: 420px;
  line-height: 1.4;
  white-space: normal;
  word-break: break-all;
  overflow-wrap: anywhere;
}

:deep(.evaluation-description-tooltip .el-tooltip__content) {
  max-width: 420px;
  white-space: normal;
  word-break: break-all;
  overflow-wrap: anywhere;
  text-align: left;
}

.evaluation-description-tooltip-content {
  max-width: 420px;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  line-height: 1.4;
  text-align: left;
}

.pagination-container {
  min-height: 46px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 12px;
  border-top: 1px solid var(--console-line);
  background: #fff;
}

.pagination-container :deep(.el-pagination .el-pager li),
.pagination-container :deep(.el-pagination .el-pagination__total),
.pagination-container :deep(.el-pagination .el-pagination__sizes),
.pagination-container :deep(.el-pagination .el-pagination__jump) {
  line-height: 1.2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-container :deep(.el-pagination .el-pagination__total),
.pagination-container :deep(.el-pagination .el-pagination__jump) {
  margin-top: 0;
  margin-bottom: 0;
}

@media (max-width: 1200px) {
  .kpi-strip {
    grid-template-columns: repeat(3, minmax(140px, 1fr));
  }

  .filters {
    grid-template-columns: repeat(4, minmax(150px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-head,
  .saved-views,
  .pagination-container,
  .table-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .kpi-strip,
  .filters {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    align-self: stretch;
  }

}
</style>
