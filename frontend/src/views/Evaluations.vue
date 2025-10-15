<template>
  <div class="evaluations-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('evaluation.title') }}</h1>
        <p class="page-description">{{ $t('evaluation.description') }}</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="openNew()">
          <template #icon><Plus /></template>
          {{ $t('evaluation.new.title') }}
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <AnimatedContainer type="fadeInUp" delay="0.1s">
      <el-card class="filter-card">
        <el-form :model="searchForm" inline class="search-form">
          <el-form-item :label="$t('evaluation.evaluationNumber')">
            <el-input
              v-model="searchForm.evaluation_number"
              :placeholder="$t('evaluation.placeholders.evaluationNumber')"
              clearable
              style="width: 200px"
            />
          </el-form-item>

          <el-form-item :label="$t('evaluation.evaluationType')">
            <el-select
              v-model="searchForm.evaluation_type"
              :placeholder="$t('evaluation.placeholders.evaluationType')"
              clearable
              style="width: 150px"
            >
              <el-option :label="$t('evaluation.type.new_product')" value="new_product" />
              <el-option :label="$t('evaluation.type.mass_production')" value="mass_production" />
            </el-select>
          </el-form-item>

          <el-form-item :label="$t('common.status')">
            <el-select
              v-model="searchForm.status"
              :placeholder="$t('evaluation.placeholders.status')"
              clearable
              style="width: 150px"
            >
              <el-option
                v-for="status in statusOptions"
                :key="status.value"
                :label="status.label"
                :value="status.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="$t('evaluation.product')">
            <el-input
              v-model="searchForm.product"
              :placeholder="$t('evaluation.placeholders.product')"
              clearable
              style="width: 150px"
            />
          </el-form-item>

          <el-form-item :label="$t('evaluation.scsCharger')">
            <el-input
              v-model="searchForm.scs_charger"
              :placeholder="$t('evaluation.placeholders.scsCharger')"
              clearable
              style="width: 150px"
            />
          </el-form-item>

          <el-form-item :label="$t('evaluation.headOfficeCharger')">
            <el-input
              v-model="searchForm.head_office_charger"
              :placeholder="$t('evaluation.placeholders.headOfficeCharger')"
              clearable
              style="width: 150px"
            />
          </el-form-item>

          <el-form-item :label="$t('evaluation.dateRange')">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              :range-separator="$t('evaluation.placeholders.rangeSeparator')"
              :start-placeholder="$t('evaluation.placeholders.startDate')"
              :end-placeholder="$t('evaluation.placeholders.endDate')"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <template #icon><Search /></template>
              {{ $t('evaluation.search') }}
            </el-button>
            <el-button @click="handleReset">
              <template #icon><Refresh /></template>
              {{ $t('evaluation.reset') }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </AnimatedContainer>

    <!-- 数据表格 -->
    <AnimatedContainer type="fadeInUp" delay="0.3s">
      <el-card class="table-card">
        <template #header>
          <div class="table-header">
            <span>{{ $t('evaluation.list') }}</span>
            <div class="table-actions">
              <el-button :loading="exportLoading" @click="handleExport">
                <template #icon><Download /></template>
                {{ $t('evaluation.export') }}
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          v-loading="tableLoading"
          :data="tableData"
          stripe
          @selection-change="handleSelectionChange"
          @sort-change="handleSortChange"
        >
          <el-table-column type="selection" width="55" />

          <el-table-column
            prop="evaluation_number"
            :label="$t('evaluation.evaluationNumber')"
            width="180"
            sortable="custom"
          >
            <template #default="{ row }">
              <el-link type="primary" @click="openDetail(row.id)">
                {{ row.evaluation_number }}
              </el-link>
            </template>
          </el-table-column>

          <el-table-column
            prop="evaluation_type"
            :label="$t('evaluation.evaluationType')"
            width="120"
          >
            <template #default="{ row }">
              <el-tag :type="row.evaluation_type === 'new_product' ? 'primary' : 'success'">
                {{ $t(`evaluation.type.${row.evaluation_type}`) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            prop="product_name"
            :label="$t('evaluation.product')"
            width="150"
            sortable="custom"
          />

          <el-table-column prop="part_number" :label="$t('evaluation.partNumber')" width="220" />

          <el-table-column prop="evaluation_reason" :label="$t('evaluation.reason')" width="140">
            <template #default="{ row }">
              {{ row.evaluation_reason ? $t(`evaluation.reasons.${row.evaluation_reason}`) : '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="scs_charger_name"
            :label="$t('evaluation.scsCharger')"
            width="120"
            sortable="custom"
          />

          <el-table-column
            prop="head_office_charger_name"
            :label="$t('evaluation.headOfficeCharger')"
            width="120"
            sortable="custom"
          />

          <el-table-column prop="status" :label="$t('common.status')" width="140" sortable="custom">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">
                {{ $t(`status.${row.status}`) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            prop="start_date"
            :label="$t('evaluation.startDate')"
            width="130"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ formatDate(row.start_date) }}
            </template>
          </el-table-column>

          <el-table-column prop="actual_end_date" :label="$t('evaluation.endDate')" width="130">
            <template #default="{ row }">
              {{ row.actual_end_date ? formatDate(row.actual_end_date) : '-' }}
            </template>
          </el-table-column>

          <el-table-column :label="$t('evaluation.tat')" width="140">
            <template #default="{ row }">
              {{ formatTat(row) }}
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </AnimatedContainer>

    <!-- Popout dialogs -->
    <el-dialog
      v-model="showDetail"
      :title="$t('evaluation.title')"
      width="80%"
      destroy-on-close
      :close-on-click-modal="false"
      :close-on-press-escape="true"
    >
      <component
        :is="EvaluationDetail"
        :evaluation-id="selectedId"
        :in-dialog="true"
        :process-step-options="processStepOptions"
        @edit="onEdit"
      />
      <template #footer>
        <el-button @click="showDetail = false">{{ $t('common.cancel') }}</el-button>
      </template>
    </el-dialog>
    <el-dialog
      v-model="showNew"
      :title="isEditing ? $t('evaluation.edit.title') : $t('evaluation.new.title')"
      width="80%"
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
        <el-button @click="showNew = false">{{ $t('common.cancel') }}</el-button>
        <template v-if="!isEditing">
          <el-button type="primary" @click="newEvalRef?.saveDraft()">
            {{ $t('evaluation.saveDraft') }}
          </el-button>
          <el-button type="success" @click="newEvalRef?.submitForm()">
            {{ $t('evaluation.submit') }}
          </el-button>
        </template>
        <template v-else>
          <el-button type="danger" @click="newEvalRef?.deleteEval()">
            {{ $t('common.delete') }}
          </el-button>
          <el-button type="primary" @click="newEvalRef?.save()">
            {{ $t('common.save') }}
          </el-button>
          <el-button type="success" @click="newEvalRef?.finish()">
            {{ $t('evaluation.finish') }}
          </el-button>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../utils/api'
import AnimatedContainer from '../components/AnimatedContainer.vue'
const EvaluationDetail = defineAsyncComponent(() => import('./EvaluationDetail.vue'))
const NewEvaluation = defineAsyncComponent(() => import('./NewEvaluation.vue'))

const { t } = useI18n()

const tableLoading = ref(false)
const exportLoading = ref(false)
const showDetail = ref(false)
const showNew = ref(false)
const selectedId = ref(null)
const isEditing = computed(() => !!selectedId.value)
const newEvalRef = ref(null)
const tableData = ref([])
const selectedRows = ref([])
const processStepOptions = ['iARTS', 'Aging', 'LI', 'Repair']

const searchForm = reactive({
  evaluation_number: '',
  evaluation_type: '',
  status: '',
  product: '',
  scs_charger: '',
  head_office_charger: '',
  dateRange: null,
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

const sortParams = reactive({
  prop: '',
  order: '',
})

const statusOptions = computed(() => [
  { label: t('status.draft'), value: 'draft' },
  { label: t('status.in_progress'), value: 'in_progress' },
  { label: t('status.pending_approval'), value: 'pending_approval' },
  { label: t('status.completed'), value: 'completed' },
  { label: t('status.paused'), value: 'paused' },
  { label: t('status.cancelled'), value: 'cancelled' },
  { label: t('status.rejected'), value: 'rejected' },
])

const fetchEvaluations = async () => {
  try {
    tableLoading.value = true

    const params = {
      page: pagination.page,
      per_page: pagination.size,
    }

    // 只添加非空的搜索参数
    if (searchForm.evaluation_number) {
      params.evaluation_number = searchForm.evaluation_number
    }
    if (searchForm.evaluation_type) {
      params.evaluation_type = searchForm.evaluation_type
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    if (searchForm.product) {
      params.product = searchForm.product
    }
    if (searchForm.scs_charger) {
      params.scs_charger_name = searchForm.scs_charger
    }
    if (searchForm.head_office_charger) {
      params.head_office_charger_name = searchForm.head_office_charger
    }

    // 处理日期范围
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date_from = searchForm.dateRange[0]
      params.start_date_to = searchForm.dateRange[1]
    }

    // 处理排序
    if (sortParams.prop) {
      params.sort_by = sortParams.prop
      params.sort_order = sortParams.order === 'ascending' ? 'asc' : 'desc'
    }

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

const openDetail = (id) => {
  selectedId.value = id
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
  fetchEvaluations()
}

const handleSearch = () => {
  pagination.page = 1
  fetchEvaluations()
}

const handleReset = () => {
  Object.keys(searchForm).forEach((key) => {
    searchForm[key] = key === 'dateRange' ? null : ''
  })
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

const handleExport = async () => {
  try {
    exportLoading.value = true

    // Determine data to export: selected rows or all data
    const dataToExport = selectedRows.value.length > 0 ? selectedRows.value : tableData.value

    if (dataToExport.length === 0) {
      ElMessage.warning(t('ui.noDataToExport'))
      return
    }

    // Show message about what's being exported
    const exportMessage =
      selectedRows.value.length > 0
        ? `导出选中的 ${selectedRows.value.length} 条评价记录`
        : `导出全部 ${tableData.value.length} 条评价记录`
    console.log(exportMessage)

    // Prepare CSV data
    const headers = [
      t('evaluation.evaluationNumber'),
      t('evaluation.evaluationType'),
      t('evaluation.product'),
      t('evaluation.partNumber'),
      t('evaluation.reason'),
      t('evaluation.scsCharger'),
      t('evaluation.headOfficeCharger'),
      t('common.status'),
      t('evaluation.startDate'),
      t('evaluation.endDate'),
      t('evaluation.tat'),
    ].join(',')

    const rows = dataToExport.map((row) =>
      [
        row.evaluation_number || '',
        t(`evaluation.type.${row.evaluation_type}`) || '',
        row.product_name || '',
        row.part_number || '',
        row.evaluation_reason ? t(`evaluation.reasons.${row.evaluation_reason}`) : '',
        row.scs_charger_name || '',
        row.head_office_charger_name || '',
        t(`status.${row.status}`) || '',
        formatDate(row.start_date) || '',
        formatDate(row.actual_end_date) || '',
        formatTat(row) || '',
      ]
        .map((cell) => `"${cell}"`)
        .join(','),
    )

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
    completed: 'success',
    paused: 'info',
    cancelled: 'danger',
    rejected: 'danger',
  }
  return typeMap[status] || 'info'
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

onMounted(() => {
  fetchEvaluations()
})
</script>

<style scoped>
.evaluations-page {
  padding: 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.header-right .el-button {
  height: 48px;
  padding: 0 24px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.header-right .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.filter-card:hover {
  transform: none;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.search-form {
  margin: 0;
  padding: 8px;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.search-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.search-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.search-form :deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
}

.search-form :deep(.el-button) {
  border-radius: 12px;
  height: 40px;
  padding: 0 20px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.search-form :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.search-form :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.search-form :deep(.el-button:not(.el-button--primary):hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.table-card {
  margin-bottom: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.table-card:hover {
  transform: none;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #2c3e50;
}

.table-actions .el-button {
  border-radius: 12px;
  height: 40px;
  padding: 0 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.table-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.table-card :deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

.table-card :deep(.el-table th) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  font-weight: 600;
  color: #2c3e50;
  text-align: center; /* Center align all table headers */
}

.table-card :deep(.el-table th .cell) {
  text-align: center; /* Ensure header text is centered */
}

/* Center align all table data cells */
.table-card :deep(.el-table td) {
  text-align: center; /* Center align all table data */
}

.table-card :deep(.el-table td .cell) {
  text-align: center; /* Ensure cell content is centered */
  justify-content: center; /* Center flex content */
}

.table-card :deep(.el-table tr:hover > td) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.table-card :deep(.el-link) {
  font-weight: 500;
}

.table-card :deep(.el-tag) {
  border-radius: 8px;
  font-weight: 500;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  margin-left: 8px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 12px;
  padding: 16px 0;
}

.pagination-container :deep(.el-pagination) {
  --el-pagination-button-bg-color: transparent;
  --el-pagination-hover-color: #667eea;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 12px 20px;
  display: flex;
  align-items: center;
}

.pagination-container :deep(.el-pagination .btn-next),
.pagination-container :deep(.el-pagination .btn-prev) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.pagination-container :deep(.el-pagination .btn-next:hover),
.pagination-container :deep(.el-pagination .btn-prev:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* Fix all pagination text alignment */
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

/* Expand table width and improve column spacing */
.table-card :deep(.el-table) {
  width: 100%;
  min-width: 1200px; /* Ensure minimum width to prevent wrapping */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .search-form {
    display: block;
  }

  .search-form :deep(.el-form-item) {
    display: block;
    margin-bottom: 16px;
  }

  .search-form :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
