<template>
  <div class="evaluations-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t("evaluation.title") }}</h1>
        <p class="page-description">{{ $t("evaluation.description") }}</p>
      </div>
      <div class="header-right">
        <el-button
          type="primary"
          :icon="Plus"
          @click="$router.push('/evaluations/new')"
        >
          {{ $t("dashboard.newEvaluation") }}
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
              <el-option
                :label="$t('evaluation.type.new_product')"
                value="new_product"
              />
              <el-option
                :label="$t('evaluation.type.mass_production')"
                value="mass_production"
              />
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

          <el-form-item :label="$t('evaluation.evaluator')">
            <el-input
              v-model="searchForm.evaluator"
              :placeholder="$t('evaluation.placeholders.evaluator')"
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
            <el-button type="primary" :icon="Search" @click="handleSearch">
              {{ $t("evaluation.search") }}
            </el-button>
            <el-button :icon="Refresh" @click="handleReset">
              {{ $t("evaluation.reset") }}
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
            <span>{{ $t("evaluation.list") }}</span>
            <div class="table-actions">
              <el-button
                :icon="Download"
                @click="handleExport"
                :loading="exportLoading"
              >
                {{ $t("evaluation.export") }}
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
              <el-link
                type="primary"
                @click="$router.push(`/evaluations/${row.id}`)"
              >
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
              <el-tag
                :type="
                  row.evaluation_type === 'new_product' ? 'primary' : 'success'
                "
              >
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

          <el-table-column
            prop="part_number"
            :label="$t('evaluation.partNumber')"
            width="220"
          />

          <el-table-column
            prop="evaluator_name"
            :label="$t('evaluation.evaluator')"
            width="120"
            sortable="custom"
          />

          <el-table-column
            prop="status"
            :label="$t('common.status')"
            width="140"
            sortable="custom"
          >
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

          <el-table-column
            prop="actual_end_date"
            :label="$t('evaluation.endDate')"
            width="130"
          >
            <template #default="{ row }">
              {{ row.actual_end_date ? formatDate(row.actual_end_date) : "-" }}
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  Search,
  Refresh,
  Download,
  View,
  Edit,
  MoreFilled,
  Check,
  VideoPause,
  VideoPlay,
  Close,
} from "@element-plus/icons-vue";
import api from "../utils/api";
import { useAuthStore } from "../stores/auth";
import AnimatedContainer from "../components/AnimatedContainer.vue";

const router = useRouter();
const { t } = useI18n();
const authStore = useAuthStore();

const tableLoading = ref(false);
const exportLoading = ref(false);
const tableData = ref([]);
const selectedRows = ref([]);

const searchForm = reactive({
  evaluation_number: "",
  evaluation_type: "",
  status: "",
  product: "",
  evaluator: "",
  dateRange: null,
});

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
});

const sortParams = reactive({
  prop: "",
  order: "",
});

const statusOptions = computed(() => [
  { label: t("status.draft"), value: "draft" },
  { label: t("status.in_progress"), value: "in_progress" },
  { label: t("status.pending_approval"), value: "pending_approval" },
  { label: t("status.completed"), value: "completed" },
  { label: t("status.paused"), value: "paused" },
  { label: t("status.cancelled"), value: "cancelled" },
  { label: t("status.rejected"), value: "rejected" },
]);

const fetchEvaluations = async () => {
  try {
    tableLoading.value = true;

    const params = {
      page: pagination.page,
      per_page: pagination.size,
    };

    // 只添加非空的搜索参数
    if (searchForm.evaluation_number) {
      params.evaluation_number = searchForm.evaluation_number;
    }
    if (searchForm.evaluation_type) {
      params.evaluation_type = searchForm.evaluation_type;
    }
    if (searchForm.status) {
      params.status = searchForm.status;
    }
    if (searchForm.product) {
      params.product = searchForm.product;
    }
    if (searchForm.evaluator) {
      params.evaluator_id = searchForm.evaluator;
    }

    // 处理日期范围
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date_from = searchForm.dateRange[0];
      params.start_date_to = searchForm.dateRange[1];
    }

    // 处理排序
    if (sortParams.prop) {
      params.sort_by = sortParams.prop;
      params.sort_order = sortParams.order === "ascending" ? "asc" : "desc";
    }

    const response = await api.get("/evaluations", { params });
    const data = response.data.data;

    // 后端返回的数据结构是 { data: { evaluations: [...], pagination: {...} } }
    tableData.value = data.evaluations || [];
    pagination.total = data.total || 0;
  } catch (error) {
    ElMessage.error("获取评价列表失败");
    console.error("Failed to fetch evaluations:", error);
  } finally {
    tableLoading.value = false;
  }
};

const handleSearch = () => {
  pagination.page = 1;
  fetchEvaluations();
};

const handleReset = () => {
  Object.keys(searchForm).forEach((key) => {
    searchForm[key] = key === "dateRange" ? null : "";
  });
  pagination.page = 1;
  fetchEvaluations();
};

const handleSizeChange = (size) => {
  pagination.size = size;
  pagination.page = 1;
  fetchEvaluations();
};

const handleCurrentChange = (page) => {
  pagination.page = page;
  fetchEvaluations();
};

const handleSortChange = ({ prop, order }) => {
  sortParams.prop = prop;
  sortParams.order = order;
  fetchEvaluations();
};

const handleSelectionChange = (selection) => {
  selectedRows.value = selection;
};

const handleEdit = (row) => {
  router.push(`/evaluations/${row.id}/edit`);
};

const handleOperation = async (command, row) => {
  try {
    let message = "";
    let confirmText = "";

    switch (command) {
      case "approve":
        message = "确认审批通过此评价？";
        confirmText = "审批";
        break;
      case "pause":
        message = "确认暂停此评价？";
        confirmText = "暂停";
        break;
      case "resume":
        message = "确认恢复此评价？";
        confirmText = "恢复";
        break;
      case "cancel":
        message = "确认取消此评价？此操作不可撤销。";
        confirmText = "取消";
        break;
    }

    await ElMessageBox.confirm(message, "确认操作", {
      confirmButtonText: confirmText,
      cancelButtonText: "取消",
      type: "warning",
    });

    await api.put(`/evaluations/${row.id}/${command}`);
    ElMessage.success("操作成功");
    fetchEvaluations();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("操作失败");
      console.error("Operation failed:", error);
    }
  }
};

const handleExport = async () => {
  try {
    exportLoading.value = true;

    // Client-side export using current table data
    if (tableData.value.length === 0) {
      ElMessage.warning("没有数据可导出");
      return;
    }

    // Prepare CSV data
    const headers = [
      t("evaluation.evaluationNumber"),
      t("evaluation.evaluationType"),
      t("evaluation.product"),
      t("evaluation.partNumber"),
      t("evaluation.evaluator"),
      t("common.status"),
      t("evaluation.startDate"),
      t("evaluation.endDate"),
    ].join(",");

    const rows = tableData.value.map((row) =>
      [
        row.evaluation_number || "",
        t(`evaluation.type.${row.evaluation_type}`) || "",
        row.product_name || "",
        row.part_number || "",
        row.evaluator_name || "",
        t(`status.${row.status}`) || "",
        formatDate(row.start_date) || "",
        formatDate(row.actual_end_date) || "",
      ]
        .map((cell) => `"${cell}"`)
        .join(","),
    );

    const csvContent = [headers, ...rows].join("\n");

    // Create and download CSV file
    const blob = new Blob(["\uFEFF" + csvContent], {
      type: "text/csv;charset=utf-8;",
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `evaluations_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    ElMessage.success(t("evaluation.exportSuccess") || "导出成功");
  } catch (error) {
    ElMessage.error(t("evaluation.exportError") || "导出失败");
    console.error("Export failed:", error);
  } finally {
    exportLoading.value = false;
  }
};

// 权限检查函数
const canEdit = (row) => {
  return (
    row.status === "in_progress" &&
    (authStore.user.id === row.evaluator_id || authStore.isAdmin)
  );
};

const canOperate = (row) => {
  return authStore.canApprove || authStore.user.id === row.evaluator_id;
};

const canApprove = (row) => {
  return row.status === "pending_approval" && authStore.canApprove;
};

const canPause = (row) => {
  return row.status === "in_progress";
};

const canResume = (row) => {
  return row.status === "paused";
};

const canCancel = (row) => {
  return ["in_progress", "paused", "pending_approval"].includes(row.status);
};

const getStatusTagType = (status) => {
  const typeMap = {
    draft: "info",
    in_progress: "primary",
    pending_approval: "warning",
    completed: "success",
    paused: "info",
    cancelled: "danger",
    rejected: "danger",
  };
  return typeMap[status] || "info";
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleDateString();
};

onMounted(() => {
  fetchEvaluations();
});
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
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.1) 0%,
    rgba(118, 75, 162, 0.1) 100%
  );
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
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.05) 0%,
    rgba(118, 75, 162, 0.05) 100%
  );
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
