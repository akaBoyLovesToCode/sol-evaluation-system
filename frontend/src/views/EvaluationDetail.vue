<template>
  <div class="evaluation-detail-page" v-loading="loading">
    <div class="page-header" v-if="evaluation">
      <div class="header-left">
        <h1 class="page-title">
          {{ evaluation.evaluation_number }}
          <el-tag
            :type="getStatusTagType(evaluation.status)"
            class="status-tag"
          >
            {{ $t(`status.${evaluation.status}`) }}
          </el-tag>
        </h1>
        <p class="page-description">{{ evaluation.product_name }}</p>
      </div>
      <div class="header-right">
        <el-button
          v-if="canEdit"
          type="primary"
          :icon="Edit"
          @click="$router.push(`/evaluations/${evaluation.id}/edit`)"
        >
          {{ $t("common.edit") }}
        </el-button>

        <el-dropdown v-if="canOperate" @command="handleOperation">
          <el-button type="primary" :icon="MoreFilled">
            {{ $t("common.operations") }}
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-if="canApprove"
                command="approve"
                :icon="Check"
              >
                {{ $t("evaluation.approve") }}
              </el-dropdown-item>
              <el-dropdown-item v-if="canReject" command="reject" :icon="Close">
                {{ $t("evaluation.reject") }}
              </el-dropdown-item>
              <el-dropdown-item
                v-if="canPause"
                command="pause"
                :icon="VideoPause"
              >
                {{ $t("evaluation.pause") }}
              </el-dropdown-item>
              <el-dropdown-item
                v-if="canResume"
                command="resume"
                :icon="VideoPlay"
              >
                {{ $t("evaluation.resume") }}
              </el-dropdown-item>
              <el-dropdown-item
                v-if="canCancel"
                command="cancel"
                :icon="Close"
                divided
              >
                {{ $t("evaluation.cancel") }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="detail-content" v-if="evaluation">
      <el-row :gutter="20">
        <!-- 左侧主要内容 -->
        <el-col :span="16">
          <!-- {{ $t('evaluation.basicInformation') }} -->
          <el-card class="info-card">
            <template #header>
              <span>{{ $t("evaluation.basicInformation") }}</span>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="$t('evaluation.evaluationNumber')">
                {{ evaluation.evaluation_number }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.evaluationType')">
                <el-tag
                  :type="
                    evaluation.evaluation_type === 'new_product'
                      ? 'primary'
                      : 'success'
                  "
                >
                  {{ $t(`evaluation.type.${evaluation.evaluation_type}`) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.productName')">
                {{ evaluation.product_name }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.partNumber')">
                {{ evaluation.part_number }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.evaluator')">
                {{ evaluation.evaluator_name }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.startDate')">
                {{ formatDate(evaluation.start_date) }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.expectedEndDate')">
                {{ formatDate(evaluation.expected_end_date) }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.actualEndDate')">
                {{
                  evaluation.actual_end_date ? formatDate(evaluation.actual_end_date) : "-"
                }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.reason')">
                {{ getReasonText(evaluation.evaluation_reason) }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.progress')">
                <el-progress
                  :percentage="evaluation.progress || 0"
                  :stroke-width="8"
                />
              </el-descriptions-item>
            </el-descriptions>

            <div class="description-section" v-if="evaluation.description">
              <h4>{{ $t("evaluation.evaluationDescription") }}</h4>
              <p>{{ evaluation.description }}</p>
            </div>
          </el-card>

          <!-- {{ $t('evaluation.technicalSpecifications') }} -->
          <el-card class="info-card">
            <template #header>
              <span>{{ $t("evaluation.technicalSpecifications") }}</span>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="$t('evaluation.pgmVersion')">
                {{ evaluation.pgm_version || "-" }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.materialInfo')">
                {{ evaluation.material_info || "-" }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.capacity')">
                {{ evaluation.capacity || "-" }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.interfaceType')">
                {{ evaluation.interface_type || "-" }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.formFactor')">
                {{ evaluation.form_factor || "-" }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.temperatureGrade')">
                {{ getTemperatureGradeText(evaluation.temperature_grade) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- {{ $t('evaluation.evaluationProcess') }} -->
          <el-card class="info-card">
            <template #header>
              <span>{{ $t("evaluation.evaluationProcess") }}</span>
            </template>
            <div class="process-timeline">
              <el-timeline>
                <el-timeline-item
                  v-for="process in processSteps"
                  :key="process.key"
                  :timestamp="process.timestamp"
                  :type="process.type"
                  :icon="process.icon"
                >
                  <div class="process-content">
                    <h4>{{ process.title }}</h4>
                    <p v-if="process.description">{{ process.description }}</p>
                    <div v-if="process.result" class="process-result">
                      <el-tag :type="process.result.type">
                        {{ process.result.text }}
                      </el-tag>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-card>

          <!-- {{ $t('evaluation.evaluationResults') }} -->
          <el-card
            class="info-card"
            v-if="evaluation.results && evaluation.results.length > 0"
          >
            <template #header>
              <span>{{ $t("evaluation.evaluationResults") }}</span>
            </template>
            <div class="results-section">
              <div
                v-for="result in evaluation.results"
                :key="result.id"
                class="result-item"
              >
                <div class="result-header">
                  <h4>{{ result.test_item }}</h4>
                  <el-tag
                    :type="result.result === 'pass' ? 'success' : 'danger'"
                  >
                    {{
                      result.result === "pass"
                        ? $t("evaluation.pass")
                        : $t("evaluation.fail")
                    }}
                  </el-tag>
                </div>
                <div class="result-content">
                  <p>
                    <strong>{{ $t("evaluation.testConditions") }}：</strong
                    >{{ result.test_conditions }}
                  </p>
                  <p>
                    <strong>{{ $t("evaluation.testResult") }}：</strong
                    >{{ result.test_result }}
                  </p>
                  <p v-if="result.remarks">
                    <strong>{{ $t("evaluation.remarks") }}：</strong
                    >{{ result.remarks }}
                  </p>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧边栏 -->
        <el-col :span="8">
          <!-- {{ $t('evaluation.statusInformation') }} -->
          <el-card class="sidebar-card">
            <template #header>
              <span>{{ $t("evaluation.statusInformation") }}</span>
            </template>
            <div class="status-info">
              <div class="status-item">
                <span class="label"
                  >{{ $t("evaluation.currentStatus") }}：</span
                >
                <el-tag :type="getStatusTagType(evaluation.status)">
                  {{ $t(`status.${evaluation.status}`) }}
                </el-tag>
              </div>
              <div class="status-item">
                <span class="label">{{ $t("evaluation.createdAt") }}：</span>
                <span>{{ formatDateTime(evaluation.created_at) }}</span>
              </div>
              <div class="status-item">
                <span class="label">{{ $t("evaluation.updatedAt") }}：</span>
                <span>{{ formatDateTime(evaluation.updated_at) }}</span>
              </div>
              <div class="status-item" v-if="evaluation.approved_by">
                <span class="label">{{ $t("evaluation.approvedBy") }}：</span>
                <span>{{ evaluation.approved_by }}</span>
              </div>
              <div class="status-item" v-if="evaluation.approved_at">
                <span class="label">{{ $t("evaluation.approvedAt") }}：</span>
                <span>{{ formatDateTime(evaluation.approved_at) }}</span>
              </div>
            </div>
          </el-card>

          <!-- {{ $t('evaluation.relatedFiles') }} -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t("evaluation.relatedFiles") }}</span>
                <el-button
                  v-if="canEdit"
                  size="small"
                  :icon="Plus"
                  @click="handleUploadFile"
                >
                  {{ $t("evaluation.upload") }}
                </el-button>
              </div>
            </template>
            <div class="files-list">
              <div
                v-for="file in evaluation.files"
                :key="file.id"
                class="file-item"
              >
                <el-icon class="file-icon"><Document /></el-icon>
                <div class="file-info">
                  <div class="file-name">{{ file.filename }}</div>
                  <div class="file-meta">
                    {{ formatFileSize(file.size) }} •
                    {{ formatDate(file.created_at) }}
                  </div>
                </div>
                <el-button
                  size="small"
                  :icon="Download"
                  @click="handleDownloadFile(file)"
                />
              </div>
              <div
                v-if="!evaluation.files || evaluation.files.length === 0"
                class="empty-files"
              >
                {{ $t("evaluation.noRelatedFiles") }}
              </div>
            </div>
          </el-card>

          <!-- {{ $t('evaluation.operationLogs') }} -->
          <el-card class="sidebar-card">
            <template #header>
              <span>{{ $t("evaluation.operationLogs") }}</span>
            </template>
            <div class="logs-list">
              <el-timeline>
                <el-timeline-item
                  v-for="log in evaluation.logs"
                  :key="log.id"
                  :timestamp="formatDateTime(log.created_at)"
                  size="small"
                >
                  <div class="log-content">
                    <span class="log-user">{{ log.user_name }}</span>
                    <span class="log-action">{{ log.description }}</span>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Edit,
  MoreFilled,
  Check,
  Close,
  VideoPause,
  VideoPlay,
  Plus,
  Document,
  Download,
} from "@element-plus/icons-vue";
import api from "../utils/api";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const authStore = useAuthStore();

const loading = ref(false);
const evaluation = ref(null);

const canEdit = computed(() => {
  if (!evaluation.value) return false;
  return (
    evaluation.value.status === "in_progress" &&
    (authStore.user.id === evaluation.value.evaluator_id || authStore.isAdmin)
  );
});

const canOperate = computed(() => {
  return (
    authStore.canApprove || authStore.user.id === evaluation.value?.evaluator_id
  );
});

const canApprove = computed(() => {
  return (
    evaluation.value?.status === "pending_approval" && authStore.canApprove
  );
});

const canReject = computed(() => {
  return (
    evaluation.value?.status === "pending_approval" && authStore.canApprove
  );
});

const canPause = computed(() => {
  if (!evaluation.value) return false;
  return (
    evaluation.value.status === "in_progress" &&
    (authStore.user.id === evaluation.value.evaluator_id || authStore.isAdmin)
  );
});

const canResume = computed(() => {
  if (!evaluation.value) return false;
  return (
    evaluation.value.status === "paused" &&
    (authStore.user.id === evaluation.value.evaluator_id || authStore.isAdmin)
  );
});

const canCancel = computed(() => {
  if (!evaluation.value) return false;
  return (
    ["in_progress", "paused", "pending_approval"].includes(
      evaluation.value.status,
    ) &&
    (authStore.user.id === evaluation.value.evaluator_id || authStore.isAdmin)
  );
});

const processSteps = computed(() => {
  if (!evaluation.value) return [];

  const steps = [];
  const processes = evaluation.value.processes || [];

  processes.forEach((process) => {
    steps.push({
      key: process,
      title: getProcessTitle(process),
      timestamp: formatDate(evaluation.value.start_date),
      type: "primary",
      description: getProcessDescription(process),
    });
  });

  return steps;
});

const fetchEvaluation = async () => {
  try {
    loading.value = true;
    const response = await api.get(`/evaluations/${route.params.id}`);
    evaluation.value = response.data.data.evaluation;
  } catch (error) {
    ElMessage.error(t("evaluation.getEvaluationDetailsFailed"));
    console.error("Failed to fetch evaluation:", error);
  } finally {
    loading.value = false;
  }
};

const handleOperation = async (command) => {
  try {
    let message = "";
    let confirmText = "";

    switch (command) {
      case "approve":
        message = t("evaluation.confirmApprove");
        confirmText = t("evaluation.approve");
        break;
      case "reject":
        message = t("evaluation.confirmReject");
        confirmText = t("evaluation.reject");
        break;
      case "pause":
        message = t("evaluation.confirmPause");
        confirmText = t("evaluation.pause");
        break;
      case "resume":
        message = t("evaluation.confirmResume");
        confirmText = t("evaluation.resume");
        break;
      case "cancel":
        message = t("evaluation.confirmCancel");
        confirmText = t("evaluation.cancel");
        break;
    }

    await ElMessageBox.confirm(message, t("common.confirmAction"), {
      confirmButtonText: confirmText,
      cancelButtonText: t("common.cancel"),
      type: "warning",
    });

    // Call appropriate API endpoint based on command
    if (command === "approve") {
      await api.post(`/evaluations/${evaluation.value.id}/approve`);
    } else if (command === "reject") {
      await api.post(`/evaluations/${evaluation.value.id}/reject`);
    } else if (command === "pause") {
      await api.put(`/evaluations/${evaluation.value.id}/status`, {
        status: "paused",
      });
    } else if (command === "resume") {
      await api.put(`/evaluations/${evaluation.value.id}/status`, {
        status: "in_progress",
      });
    } else if (command === "cancel") {
      await api.put(`/evaluations/${evaluation.value.id}/status`, {
        status: "cancelled",
      });
    }

    ElMessage.success(t("evaluation.operationSuccess"));
    fetchEvaluation();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(t("evaluation.operationFailed"));
      console.error("Operation failed:", error);
    }
  }
};

const handleUploadFile = () => {
  // TODO: 实现文件上传功能
  ElMessage.info(t("evaluation.fileUploadInDevelopment"));
};

const handleDownloadFile = (file) => {
  // TODO: 实现文件下载功能
  ElMessage.info(t("evaluation.fileDownloadInDevelopment"));
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

const getReasonText = (reason) => {
  if (reason && t(`evaluation.reasons.${reason}`)) {
    return t(`evaluation.reasons.${reason}`);
  }
  return reason || "-";
};

const getTemperatureGradeText = (grade) => {
  if (grade && t(`evaluation.temperatureGrades.${grade}`)) {
    return t(`evaluation.temperatureGrades.${grade}`);
  }
  return grade || "-";
};

const getProcessTitle = (process) => {
  if (process && t(`evaluation.processes.${process}`)) {
    return t(`evaluation.processes.${process}`);
  }
  return process;
};

const getProcessDescription = (process) => {
  // Process descriptions are technical and don't need i18n for now
  const descMap = {
    doe: "Design of Experiments - Optimize product parameters",
    ppq: "Production Part Qualification - Verify production process",
    prq: "Production Readiness Qualification - Ensure production readiness",
    production_test: "Production testing - Verify product quality",
    aql: "Acceptable Quality Level testing",
  };
  return descMap[process] || "";
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleDateString();
};

const formatDateTime = (dateString) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleString();
};

const formatFileSize = (bytes) => {
  if (!bytes) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

onMounted(async () => {
  // 首先确保用户信息已加载
  if (!authStore.user && authStore.token) {
    await authStore.checkAuth();
  }

  // 然后获取评估信息
  await fetchEvaluation();
});
</script>

<style scoped>
.evaluation-detail-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-tag {
  font-size: 12px;
}

.page-description {
  color: #7f8c8d;
  margin: 0;
}

.detail-content {
  margin-top: 20px;
}

.info-card {
  margin-bottom: 20px;
}

.info-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
}

.description-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.description-section h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-weight: 600;
}

.description-section p {
  margin: 0;
  line-height: 1.6;
  color: #606266;
}

.process-timeline {
  padding: 20px 0;
}

.process-content h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-weight: 600;
}

.process-content p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 14px;
}

.process-result {
  margin-top: 8px;
}

.results-section {
  padding: 20px 0;
}

.result-item {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.result-item:last-child {
  margin-bottom: 0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-header h4 {
  margin: 0;
  color: #2c3e50;
  font-weight: 600;
}

.result-content p {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
}

.sidebar-card {
  margin-bottom: 20px;
}

.sidebar-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-info {
  padding: 16px 0;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-item:last-child {
  margin-bottom: 0;
}

.status-item .label {
  color: #7f8c8d;
  font-size: 14px;
}

.files-list {
  padding: 16px 0;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.file-item:last-child {
  border-bottom: none;
}

.file-icon {
  color: #409eff;
  font-size: 20px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.file-meta {
  font-size: 12px;
  color: #7f8c8d;
}

.empty-files {
  text-align: center;
  color: #7f8c8d;
  font-size: 14px;
  padding: 20px 0;
}

.logs-list {
  padding: 16px 0;
  max-height: 300px;
  overflow-y: auto;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.log-user {
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.log-action {
  color: #7f8c8d;
  font-size: 13px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .detail-content .el-row {
    flex-direction: column;
  }

  .detail-content .el-col {
    width: 100% !important;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .page-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
