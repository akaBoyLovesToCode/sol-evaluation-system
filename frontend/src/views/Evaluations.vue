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

    <section v-if="isNandView" v-loading="nandLoading" class="nand-shell">
      <div class="nand-toolbar">
        <div class="table-title">
          <span>{{ $t('evaluation.console.nand.title') }}</span>
          <span class="table-meta">
            {{
              $t('evaluation.console.nand.meta', {
                total: nandEvents.length,
                rows: nandRows.length,
              })
            }}
          </span>
        </div>
        <div class="nand-legend">
          <span v-for="item in nandLegendItems" :key="item.status" class="nand-legend-item">
            <span class="nand-legend-node" :class="`nand-node-${item.status}`"></span>
            {{ item.label }}
          </span>
        </div>
      </div>

      <el-alert
        v-if="nandIncompleteCount > 0"
        class="nand-incomplete-alert"
        type="warning"
        :closable="false"
        show-icon
        :title="$t('evaluation.console.nand.incompleteWarning', { count: nandIncompleteCount })"
      />

      <el-empty
        v-if="nandEvents.length === 0"
        class="nand-empty"
        :description="$t('evaluation.console.nand.emptyDescription')"
      />

      <div v-else class="nand-matrix-scroll">
        <div class="nand-matrix" :style="{ width: `${nandMatrixWidth}px` }">
          <div class="nand-left-head">
            <div>DR</div>
            <div>{{ $t('evaluation.console.nand.productColumn') }}</div>
          </div>
          <div class="nand-month-head" :style="{ width: `${nandTimelineWidth}px` }">
            <div
              v-for="month in nandMonths"
              :key="month.key"
              class="nand-month"
              :style="{ left: `${month.left}px`, width: `${month.width}px` }"
            >
              {{ month.label }}
            </div>
            <div
              v-if="nandTodayPosition !== null"
              class="nand-current-line head"
              :style="{ left: `${nandTodayPosition}px` }"
            >
              <span>{{ $t('evaluation.console.nand.currentLine') }}</span>
            </div>
          </div>

          <div class="nand-body" :style="{ width: `${nandMatrixWidth}px` }">
            <template v-for="group in nandGroupedRows" :key="group.dr">
              <div class="nand-dr-cell" :style="{ gridRow: `span ${group.rows.length}` }">
                {{ group.dr }}
              </div>
              <template v-for="row in group.rows" :key="row.key">
                <div class="nand-product-cell">{{ row.product }}</div>
                <div class="nand-timeline-cell" :style="{ width: `${nandTimelineWidth}px` }">
                  <div
                    v-for="month in nandMonths"
                    :key="`${row.key}-${month.key}`"
                    class="nand-month-gridline"
                    :style="{ left: `${month.left}px` }"
                  ></div>
                  <div
                    v-if="nandTodayPosition !== null"
                    class="nand-current-line body"
                    :style="{ left: `${nandTodayPosition}px` }"
                  ></div>
                  <button
                    v-for="event in row.events"
                    :key="event.key"
                    type="button"
                    class="nand-event"
                    :class="`nand-node-${event.status}`"
                    :style="{ left: `${event.left}px` }"
                    @click="openDetail(event.source)"
                  >
                    <span v-if="event.remarkTop" class="nand-event-note top">
                      {{ event.remarkTop }}
                    </span>
                    <span class="nand-event-node">{{ event.day }}</span>
                    <span v-if="event.remarkBottom" class="nand-event-note bottom">
                      {{ event.remarkBottom }}
                    </span>
                    <span class="nand-event-popover">
                      <strong>{{ event.evaluationNumber }}</strong>
                      <span>{{ event.evaluationItem || '-' }}</span>
                      <span>{{ event.appliedProducts || '-' }} · {{ event.fabLine || '-' }}</span>
                      <span>{{ event.grades || '-' }}</span>
                    </span>
                  </button>
                </div>
              </template>
            </template>
          </div>
        </div>
      </div>
    </section>

    <section v-else class="table-shell">
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
            width="198"
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
            prop="evaluation_name"
            :label="$t('evaluation.evaluationName')"
            width="220"
            sortable="custom"
            show-overflow-tooltip
            align="center"
          >
            <template #default="{ row }">
              {{ row.evaluation_name || '-' }}
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
            width="170"
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
                <el-tooltip
                  placement="top"
                  effect="dark"
                  popper-class="evaluation-description-tooltip"
                >
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
import { fetchAllEvaluationPages } from '../utils/evaluationExport'
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
const nandLoading = ref(false)
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
const nandEvaluations = ref([])
const selectedRows = ref([])
const activeOperationalView = ref('all_active')
const processStepOptions = ['iARTs', 'Aging', 'LI', 'Repair']
const DESCRIPTION_WORD_LIMIT = 16
const DESCRIPTION_CHAR_LIMIT = 80
const NAND_VIEW_VALUE = 'nand_view'
const NAND_LEFT_WIDTH = 190
const NAND_MONTH_WIDTH = 132
const DAY_MS = 24 * 60 * 60 * 1000

const kpiData = reactive({
  open_evaluations: 0,
  stale_open_evaluations: 0,
  open_over_10d: 0,
  median_open_age_days: 0,
  created_this_month: 0,
  total_evaluations: 0,
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
  { label: t('status.in_progress'), value: 'in_progress' },
  { label: t('status.completed'), value: 'completed' },
  { label: t('status.cancelled'), value: 'cancelled' },
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
    label: t('evaluation.console.savedViews.allEvaluations', {
      count: kpiData.total_evaluations,
    }),
    value: 'all',
  },
  {
    label: t('evaluation.console.savedViews.nandView'),
    value: NAND_VIEW_VALUE,
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
const isNandView = computed(() => activeOperationalView.value === NAND_VIEW_VALUE)

const detailDialogTitle = computed(() => selectedEvaluationNumber.value || t('evaluation.title'))
const terminalStatuses = ['completed', 'cancelled']
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

const parseDateOnly = (value) => {
  if (!value) return null
  const datePart = String(value).split('T')[0]
  const [year, month, day] = datePart.split('-').map(Number)
  if (!year || !month || !day) return null
  const date = new Date(year, month - 1, day)
  return Number.isNaN(date.getTime()) ? null : date
}

const startOfMonth = (date) => new Date(date.getFullYear(), date.getMonth(), 1)
const addMonths = (date, months) => new Date(date.getFullYear(), date.getMonth() + months, 1)
const daysBetween = (start, end) => Math.round((end.getTime() - start.getTime()) / DAY_MS)

const formatMonthLabel = (date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`

const nandProductOrder = new Map(
  [
    'V3_DW',
    'V3_DX',
    'V3_DA',
    'V4_FB',
    'V4_FP',
    'V4_FY',
    'V5_IX',
    'V5_IT',
    'V5_IL',
    'V6_BF',
    'V6_BU',
    'V6P_BH',
    'V7_GQ',
    'V7_GJ',
    'V8_CR',
    'V8_CU',
  ].map((key, index) => [key, index]),
)

const nandStatuses = ['approved', 'current_month_plan', 'follow_up_plan']

const normalizeNandStatus = (status) =>
  nandStatuses.includes(status) ? status : 'current_month_plan'

const isNandEvaluationRow = (row) => {
  if (row?.nand_info) return true
  return normalizeReasons(row?.evaluation_reason || row?.reason).some(
    (reason) => reason.toLowerCase() === 'nand',
  )
}

const nandLegendItems = computed(() => [
  {
    status: 'approved',
    label: t('evaluation.nand.status.approved'),
  },
  {
    status: 'current_month_plan',
    label: t('evaluation.nand.status.currentMonthPlan'),
  },
  {
    status: 'follow_up_plan',
    label: t('evaluation.nand.status.followUpPlan'),
  },
])

const nandBaseEvents = computed(() =>
  nandEvaluations.value
    .map((row) => {
      const info = row.nand_info
      const date = parseDateOnly(info?.milestone_date)
      if (!info || !date) return null
      const dr = info.dr_generation || '-'
      const product = info.product_code || '-'
      const rowKey = `${dr}_${product}`
      const appliedProducts = Array.isArray(info.applied_products)
        ? info.applied_products.join(', ')
        : ''
      const grades = Array.isArray(info.grades) ? info.grades.join(', ') : ''

      return {
        key: `${row.id}-${info.id || info.milestone_date}`,
        rowKey,
        dr,
        product,
        date,
        day: date.getDate(),
        status: normalizeNandStatus(info.milestone_status),
        evaluationNumber: row.evaluation_number || '-',
        evaluationItem: info.evaluation_item || '',
        fabLine: info.fab_line || '',
        appliedProducts,
        grades,
        remarkTop: info.remark_top || '',
        remarkBottom: info.remark_bottom || '',
        remark: info.remark || '',
        source: row,
      }
    })
    .filter(Boolean),
)

const nandTimelineRange = computed(() => {
  const rangeStart = parseDateOnly(searchForm.dateRange?.[0])
  const rangeEnd = parseDateOnly(searchForm.dateRange?.[1])
  if (rangeStart && rangeEnd) {
    return {
      start: startOfMonth(rangeStart),
      end: addMonths(startOfMonth(rangeEnd), 1),
    }
  }

  const dates = nandBaseEvents.value.map((event) => event.date)
  if (dates.length === 0) {
    const today = new Date()
    return {
      start: startOfMonth(today),
      end: addMonths(startOfMonth(today), 1),
    }
  }

  const minDate = new Date(Math.min(...dates.map((date) => date.getTime())))
  const maxDate = new Date(Math.max(...dates.map((date) => date.getTime())))
  return {
    start: startOfMonth(minDate),
    end: addMonths(startOfMonth(maxDate), 1),
  }
})

const nandMonthCount = computed(() => {
  const { start, end } = nandTimelineRange.value
  let count = 0
  let cursor = start
  while (cursor < end) {
    count += 1
    cursor = addMonths(cursor, 1)
  }
  return Math.max(1, count)
})

const nandTimelineWidth = computed(() => Math.max(760, nandMonthCount.value * NAND_MONTH_WIDTH))
const nandMatrixWidth = computed(() => NAND_LEFT_WIDTH + nandTimelineWidth.value)

const nandMonths = computed(() => {
  const months = []
  const { start, end } = nandTimelineRange.value
  const totalDays = Math.max(1, daysBetween(start, end))
  let cursor = start

  while (cursor < end) {
    const next = addMonths(cursor, 1)
    const boundedNext = next < end ? next : end
    months.push({
      key: formatMonthLabel(cursor),
      label: formatMonthLabel(cursor),
      left: (daysBetween(start, cursor) / totalDays) * nandTimelineWidth.value,
      width: (daysBetween(cursor, boundedNext) / totalDays) * nandTimelineWidth.value,
    })
    cursor = next
  }

  return months
})

const positionForNandDate = (date) => {
  const { start, end } = nandTimelineRange.value
  const totalDays = Math.max(1, daysBetween(start, end))
  const offsetDays = Math.min(Math.max(daysBetween(start, date), 0), totalDays)
  const rawPosition = (offsetDays / totalDays) * nandTimelineWidth.value
  return Math.min(Math.max(rawPosition, 18), nandTimelineWidth.value - 18)
}

const nandEvents = computed(() =>
  nandBaseEvents.value.map((event) => ({
    ...event,
    left: positionForNandDate(event.date),
  })),
)

const nandIncompleteCount = computed(() => nandEvaluations.value.length - nandEvents.value.length)

const nandTodayPosition = computed(() => {
  const today = new Date()
  const { start, end } = nandTimelineRange.value
  if (today < start || today > end) return null
  return positionForNandDate(today)
})

const nandRows = computed(() => {
  const rowMap = new Map()
  nandEvents.value.forEach((event) => {
    if (!rowMap.has(event.rowKey)) {
      rowMap.set(event.rowKey, {
        key: event.rowKey,
        dr: event.dr,
        product: event.product,
        events: [],
      })
    }
    rowMap.get(event.rowKey).events.push(event)
  })

  return Array.from(rowMap.values())
    .map((row) => ({
      ...row,
      order: nandProductOrder.get(row.key) ?? Number.MAX_SAFE_INTEGER,
      events: row.events.sort((a, b) => a.date - b.date),
    }))
    .sort((a, b) => {
      if (a.order !== b.order) return a.order - b.order
      return a.key.localeCompare(b.key)
    })
})

const nandGroupedRows = computed(() => {
  const groups = []
  nandRows.value.forEach((row) => {
    let group = groups.find((item) => item.dr === row.dr)
    if (!group) {
      group = { dr: row.dr, order: row.order, rows: [] }
      groups.push(group)
    }
    group.rows.push(row)
    group.order = Math.min(group.order, row.order)
  })
  return groups.sort((a, b) => a.order - b.order || a.dr.localeCompare(b.dr))
})

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

  if (includeOperationalView && activeOperationalView.value && !isNandView.value) {
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

    tableData.value = data.evaluations || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error(t('ui.fetchListFailed'))
    console.error('Failed to fetch evaluations:', error)
  } finally {
    tableLoading.value = false
  }
}

const fetchNandEvaluations = async () => {
  try {
    nandLoading.value = true
    const params = buildEvaluationParams({
      includePagination: false,
      includeOperationalView: false,
    })
    const rows = await fetchAllEvaluationPages(api, params)
    nandEvaluations.value = rows.filter(isNandEvaluationRow)
  } catch (error) {
    ElMessage.error(t('ui.fetchListFailed'))
    console.error('Failed to fetch NAND evaluations:', error)
  } finally {
    nandLoading.value = false
  }
}

const fetchPageData = async () => {
  await Promise.all([isNandView.value ? fetchNandEvaluations() : fetchEvaluations(), fetchKpis()])
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
  fetchPageData()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  if (!isNandView.value) {
    fetchEvaluations()
  }
}

const handleCurrentChange = (page) => {
  pagination.page = page
  if (!isNandView.value) {
    fetchEvaluations()
  }
}

const handleSortChange = ({ prop, order }) => {
  sortParams.prop = prop
  sortParams.order = order
  if (isNandView.value) {
    fetchNandEvaluations()
  } else {
    fetchEvaluations()
  }
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
      const params = buildEvaluationParams({
        includePagination: false,
        includeOperationalView: false,
      })
      dataToExport = await fetchAllEvaluationPages(api, params)
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
        ? `Export selected ${selectedRows.value.length} evaluations`
        : `Export all ${dataToExport.length} evaluations`
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
        header: t('evaluation.evaluationName'),
        value: (source) => source.evaluation_name || '',
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

    ElMessage.success(t('evaluation.exportSuccess'))
  } catch (error) {
    ElMessage.error(t('evaluation.exportError'))
    console.error('Export failed:', error)
  } finally {
    exportLoading.value = false
  }
}

const getStatusTagType = (status) => {
  const typeMap = {
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'danger',
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
  box-shadow:
    1px 0 0 var(--console-line-soft),
    12px 0 18px -18px rgba(16, 24, 40, 0.45);
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

.nand-shell {
  background: var(--console-panel);
  border: 1px solid var(--console-line);
  border-radius: 6px;
  box-shadow: var(--console-shadow);
  overflow: hidden;
}

.nand-toolbar {
  min-height: 44px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--console-line);
  background: #fff;
}

.nand-legend {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--console-muted);
  font-size: 12px;
  font-weight: 650;
}

.nand-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.nand-legend-node {
  width: 12px;
  height: 12px;
  border: 2px solid currentColor;
  border-radius: 50%;
  background: #fff;
}

.nand-incomplete-alert {
  margin: 10px 12px 0;
}

.nand-empty {
  padding: 48px 0;
}

.nand-matrix-scroll {
  width: 100%;
  overflow: auto;
  background: #fff;
}

.nand-matrix {
  min-width: 100%;
  display: grid;
  grid-template-columns: 82px 108px auto;
  grid-template-rows: 34px auto;
}

.nand-left-head {
  position: sticky;
  left: 0;
  z-index: 8;
  grid-column: 1 / 3;
  grid-row: 1;
  display: grid;
  grid-template-columns: 82px 108px;
  border-right: 1px solid var(--console-line);
  border-bottom: 1px solid var(--console-line);
  background: #f8fafc;
  color: #475467;
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.nand-left-head > div,
.nand-dr-cell,
.nand-product-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  border-right: 1px solid var(--console-line-soft);
}

.nand-month-head {
  position: relative;
  grid-column: 3;
  grid-row: 1;
  height: 34px;
  border-bottom: 1px solid var(--console-line);
  background: #f8fafc;
}

.nand-month {
  position: absolute;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  padding-left: 10px;
  border-left: 1px solid var(--console-line-soft);
  color: #475467;
  font-size: 11px;
  font-weight: 750;
  font-variant-numeric: tabular-nums;
}

.nand-body {
  grid-column: 1 / 4;
  grid-row: 2;
  display: grid;
  grid-template-columns: 82px 108px auto;
  align-items: stretch;
}

.nand-dr-cell {
  position: sticky;
  left: 0;
  z-index: 6;
  min-height: 78px;
  background: #f8fafc;
  border-bottom: 1px solid var(--console-line);
  color: #344054;
  font-size: 13px;
  font-weight: 800;
}

.nand-product-cell {
  position: sticky;
  left: 82px;
  z-index: 5;
  min-height: 78px;
  background: #fff;
  border-bottom: 1px solid var(--console-line);
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 750;
}

.nand-timeline-cell {
  position: relative;
  min-height: 78px;
  border-bottom: 1px solid var(--console-line);
  background: linear-gradient(to bottom, #fff 0, #fff 50%, #f2f5f9 50%, #f2f5f9 51%, #fff 51%);
}

.nand-month-gridline {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--console-line-soft);
}

.nand-current-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0;
  border-left: 1px dashed #b42318;
  z-index: 3;
  pointer-events: none;
}

.nand-current-line.head span {
  position: absolute;
  top: 4px;
  left: 6px;
  padding: 1px 5px;
  border-radius: 4px;
  background: #fff1f0;
  color: #b42318;
  font-size: 10px;
  font-weight: 750;
  white-space: nowrap;
}

.nand-event {
  position: absolute;
  top: 50%;
  width: 42px;
  height: 42px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--console-ink);
  cursor: pointer;
  transform: translate(-50%, -50%);
  z-index: 4;
}

.nand-event-node {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2px solid currentColor;
  border-radius: 50%;
  background: #fff;
  color: inherit;
  font-size: 12px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.nand-event:hover .nand-event-node {
  background: #f8fafc;
  box-shadow: 0 0 0 3px rgba(21, 94, 239, 0.08);
}

.nand-event-note {
  position: absolute;
  left: 50%;
  width: 92px;
  color: #344054;
  font-size: 10px;
  font-weight: 650;
  line-height: 1.15;
  text-align: center;
  white-space: normal;
  overflow-wrap: anywhere;
  transform: translateX(-50%);
}

.nand-event-note.top {
  bottom: 36px;
}

.nand-event-note.bottom {
  top: 36px;
}

.nand-event-popover {
  position: absolute;
  bottom: 46px;
  left: 50%;
  width: 190px;
  display: none;
  flex-direction: column;
  gap: 3px;
  padding: 8px 9px;
  border: 1px solid var(--console-line);
  border-radius: 6px;
  background: #fff;
  color: var(--console-ink);
  text-align: left;
  box-shadow: 0 8px 20px rgba(16, 24, 40, 0.12);
  transform: translateX(-50%);
  pointer-events: none;
}

.nand-event:hover .nand-event-popover {
  display: flex;
}

.nand-node-approved {
  color: #667085;
}

.nand-node-current_month_plan {
  color: #155eef;
}

.nand-node-follow_up_plan {
  color: #d99a00;
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
