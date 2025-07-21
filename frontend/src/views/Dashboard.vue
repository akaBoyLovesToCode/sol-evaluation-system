<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <AnimatedContainer
        v-for="(stat, index) in stats"
        :key="stat.key"
        type="fadeInUp"
        :delay="`${index * 0.1}s`"
      >
        <div class="stat-card" :class="`stat-card-${index + 1}`">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="28">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ $t(stat.label) }}</div>
              <div
                class="stat-trend"
                :class="
                  stat.trend > 0
                    ? 'positive'
                    : stat.trend < 0
                      ? 'negative'
                      : 'neutral'
                "
              >
                <el-icon v-if="stat.trend !== 0" :size="14">
                  <ArrowUp v-if="stat.trend > 0" />
                  <ArrowDown v-else />
                </el-icon>
                <span v-if="stat.trend !== 0">{{ Math.abs(stat.trend) }}%</span>
                <span v-else>--</span>
              </div>
            </div>
            <div class="stat-decoration"></div>
          </div>
        </div>
      </AnimatedContainer>
    </div>

    <div class="dashboard-content">
      <!-- 左侧内容 -->
      <div class="left-content">
        <!-- 评价状态分布图表 -->
        <AnimatedContainer type="fadeInLeft" delay="0.4s">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t("dashboard.statusDistribution") }}</span>
                <el-button text @click="refreshCharts">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </template>
            <div ref="statusChartRef" class="chart-container"></div>
          </el-card>
        </AnimatedContainer>

        <!-- 月度评价趋势 -->
        <AnimatedContainer type="fadeInLeft" delay="0.6s">
          <el-card class="chart-card">
            <template #header>
              <span>{{ $t("dashboard.monthlyTrend") }}</span>
            </template>
            <div ref="trendChartRef" class="chart-container"></div>
          </el-card>
        </AnimatedContainer>
      </div>

      <!-- 右侧内容 -->
      <div class="right-content">
        <!-- 快速操作 -->
        <AnimatedContainer type="fadeInRight" delay="0.4s">
          <el-card class="quick-actions">
            <template #header>
              <span>{{ $t("dashboard.quickActions") }}</span>
            </template>
            <div class="actions-grid">
              <el-button
                type="primary"
                :icon="Plus"
                @click="$router.push('/evaluations/new')"
                class="action-button"
              >
                {{ $t("dashboard.newEvaluation") }}
              </el-button>
              <el-button
                :icon="Document"
                @click="$router.push('/evaluations')"
                class="action-button"
              >
                {{ $t("dashboard.viewEvaluations") }}
              </el-button>
              <el-button
                :icon="DataAnalysis"
                @click="$router.push('/reports')"
                class="action-button"
              >
                {{ $t("dashboard.viewReports") }}
              </el-button>
              <el-button
                :icon="Message"
                @click="$router.push('/messages')"
                class="action-button"
              >
                {{ $t("dashboard.viewMessages") }}
              </el-button>
            </div>
          </el-card>
        </AnimatedContainer>

        <!-- 待处理事项 -->
        <AnimatedContainer type="fadeInRight" delay="0.6s">
          <el-card class="pending-items">
            <template #header>
              <span>{{ $t("dashboard.pendingItems") }}</span>
            </template>
            <div class="pending-list" v-loading="pendingLoading">
              <div
                v-for="item in pendingItems"
                :key="item.id"
                class="pending-item"
                @click="handlePendingItemClick(item)"
              >
                <div class="item-info">
                  <div class="item-title">{{ item.title }}</div>
                  <div class="item-meta">
                    <el-tag :type="getStatusTagType(item.status)" size="small">
                      {{ $t(`status.${item.status}`) }}
                    </el-tag>
                    <span class="item-date">{{
                      formatDate(item.created_at)
                    }}</span>
                  </div>
                </div>
                <el-icon class="item-arrow"><ArrowRight /></el-icon>
              </div>
              <div v-if="pendingItems.length === 0" class="empty-state">
                <el-empty :description="$t('dashboard.noPendingItems')" />
              </div>
            </div>
          </el-card>
        </AnimatedContainer>

        <!-- 最近活动 -->
        <AnimatedContainer type="fadeInRight" delay="0.8s">
          <el-card class="recent-activities">
            <template #header>
              <span>{{ $t("dashboard.recentActivities") }}</span>
            </template>
            <el-timeline class="activity-timeline">
              <el-timeline-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :timestamp="formatDate(activity.created_at)"
                :type="getActivityType(activity.action)"
              >
                <div class="activity-content">
                  <div class="activity-title">{{ activity.description }}</div>
                  <div class="activity-user">{{ activity.user_name }}</div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </AnimatedContainer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, markRaw } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import {
  Document,
  DataAnalysis,
  User,
  CircleCheck,
  Plus,
  Message,
  Refresh,
  ArrowUp,
  ArrowDown,
  ArrowRight,
} from "@element-plus/icons-vue";
import {
  createPieChart,
  createLineChart,
  makeResponsive,
  disposeChart,
} from "../utils/charts";
import api from "../utils/api";
import { useAuthStore } from "../stores/auth";
import AnimatedContainer from "../components/AnimatedContainer.vue";

const router = useRouter();
const { t } = useI18n();
const authStore = useAuthStore();

const statusChartRef = ref();
const trendChartRef = ref();
const pendingLoading = ref(false);

const stats = ref([
  {
    key: "total",
    label: "dashboard.totalEvaluations",
    value: 0,
    icon: markRaw(Document),
    iconClass: "blue",
    trend: 0,
  },
  {
    key: "pending",
    label: "dashboard.pendingApprovals",
    value: 0,
    icon: markRaw(CircleCheck),
    iconClass: "orange",
    trend: 0,
  },
  {
    key: "completed",
    label: "dashboard.completedEvaluations",
    value: 0,
    icon: markRaw(CircleCheck),
    iconClass: "green",
    trend: 0,
  },
  {
    key: "users",
    label: "dashboard.activeUsers",
    value: 0,
    icon: markRaw(User),
    iconClass: "purple",
    trend: 0,
  },
]);

const pendingItems = ref([]);
const recentActivities = ref([]);

let statusChart = null;
let trendChart = null;
let statusChartCleanup = null;
let trendChartCleanup = null;

const fetchDashboardData = async () => {
  try {
    const response = await api.get("/dashboard/overview");
    const data = response.data.data;

    // 更新统计数据
    stats.value[0].value = data.total_evaluations || 0;
    stats.value[1].value = data.pending_approvals?.length || 0;
    stats.value[2].value = data.status_distribution?.completed || 0;
    stats.value[3].value = data.user_statistics?.active_users || 0;

    // 更新趋势数据 (暂时设为0，因为后端数据结构不同)
    stats.value[0].trend = 0;
    stats.value[1].trend = 0;
    stats.value[2].trend = 0;
    stats.value[3].trend = 0;

    return data;
  } catch (error) {
    ElMessage.error(t("dashboard.loadError"));
    console.error("Failed to fetch dashboard data:", error);
  }
};

const fetchPendingItems = async () => {
  if (!authStore.canApprove) return;

  try {
    pendingLoading.value = true;
    // 使用dashboard overview中的pending_approvals数据
    const response = await api.get("/dashboard/overview");
    pendingItems.value = response.data.data.pending_approvals || [];
  } catch (error) {
    console.error("Failed to fetch pending items:", error);
  } finally {
    pendingLoading.value = false;
  }
};

const fetchMonthlyTrend = async () => {
  try {
    // 获取更大的日期范围，包括未来数据（测试环境可能有未来日期）
    const endDate = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0]; // 未来一年
    const startDate = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0]; // 过去一年

    const response = await api.get(
      `/dashboard/statistics?start_date=${startDate}&end_date=${endDate}&group_by=month`,
    );
    return response.data.data;
  } catch (error) {
    console.error("Failed to fetch monthly trend:", error);
    return null;
  }
};

const fetchRecentActivities = async () => {
  try {
    // 使用dashboard overview中的recent_evaluations数据作为活动
    const response = await api.get("/dashboard/overview");
    recentActivities.value = (response.data.data.recent_evaluations || []).map(
      (evaluation) => ({
        id: evaluation.id,
        action: "create",
        user_name: evaluation.evaluator_name || "Unknown User",
        description: `评价 ${evaluation.evaluation_number} - ${evaluation.product_name || "Unknown Product"}`,
        created_at: evaluation.created_at,
      }),
    );
  } catch (error) {
    console.error("Failed to fetch recent activities:", error);
  }
};

const initStatusChart = (data) => {
  if (!statusChartRef.value) return;

  // Dispose existing chart and cleanup
  if (statusChart) {
    disposeChart(statusChart, statusChartCleanup);
  }

  const chartData = [
    {
      value: data.status_distribution?.in_progress || 0,
      name: t("status.in_progress"),
    },
    {
      value: data.status_distribution?.pending_approval || 0,
      name: t("status.pending_approval"),
    },
    {
      value: data.status_distribution?.completed || 0,
      name: t("status.completed"),
    },
    { value: data.status_distribution?.paused || 0, name: t("status.paused") },
    {
      value: data.status_distribution?.cancelled || 0,
      name: t("status.cancelled"),
    },
  ];

  statusChart = createPieChart(statusChartRef.value, chartData, {
    seriesName: t("dashboard.evaluationStatus"),
    customOptions: {
      legend: {
        orient: "vertical",
        left: "left",
      },
    },
  });

  // Make chart responsive
  statusChartCleanup = makeResponsive(statusChart, statusChartRef.value);
};

const initTrendChart = async () => {
  if (!trendChartRef.value) return;

  // Dispose existing chart and cleanup
  if (trendChart) {
    disposeChart(trendChart, trendChartCleanup);
  }

  // Get monthly trend data
  const trendData = await fetchMonthlyTrend();

  let periods = [];
  let newEvaluations = [];
  let completedEvaluations = [];

  if (trendData && trendData.evaluations_over_time) {
    periods = trendData.evaluations_over_time.map((item) => item.period);
    newEvaluations = trendData.evaluations_over_time.map((item) => item.count);

    // Calculate completed evaluations
    if (trendData.completion_rates) {
      completedEvaluations = trendData.completion_rates.map(
        (item) => item.completed || 0,
      );
    } else {
      completedEvaluations = new Array(periods.length).fill(0);
    }
  }

  const chartData = {
    xAxis: periods,
    series: [
      {
        name: t("dashboard.newEvaluations"),
        data: newEvaluations,
      },
      {
        name: t("dashboard.completedEvaluations"),
        data: completedEvaluations,
      },
    ],
  };

  trendChart = createLineChart(trendChartRef.value, chartData, {
    colors: ["#409EFF", "#67C23A"],
    showArea: false,
  });

  // Make chart responsive
  trendChartCleanup = makeResponsive(trendChart, trendChartRef.value);
};

const refreshCharts = async () => {
  const data = await fetchDashboardData();
  if (data) {
    initStatusChart(data);
    await initTrendChart();
  }
};

const handlePendingItemClick = (item) => {
  router.push(`/evaluations/${item.id}`);
};

const getStatusTagType = (status) => {
  const typeMap = {
    in_progress: "primary",
    pending_approval: "warning",
    completed: "success",
    paused: "info",
    cancelled: "danger",
    rejected: "danger",
  };
  return typeMap[status] || "info";
};

const getActivityType = (action) => {
  const typeMap = {
    create: "primary",
    update: "warning",
    approve: "success",
    reject: "danger",
    complete: "success",
  };
  return typeMap[action] || "primary";
};

const formatDate = (dateString) => {
  if (!dateString) return "--";

  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return "--";
    }
    return (
      date.toLocaleDateString() +
      " " +
      date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    );
  } catch (error) {
    console.error("Date formatting error:", error);
    return "--";
  }
};

onMounted(async () => {
  const data = await fetchDashboardData();

  await nextTick();

  if (data) {
    initStatusChart(data);
    await initTrendChart();
  }

  fetchPendingItems();
  fetchRecentActivities();
});

onUnmounted(() => {
  // Clean up charts and event listeners
  disposeChart(statusChart, statusChartCleanup);
  disposeChart(trendChart, trendChartCleanup);
});
</script>

<style scoped>
.dashboard {
  padding: 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  position: relative;
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.stat-card-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.stat-card-2 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
.stat-card-3 {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}
.stat-card-4 {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-card-1 .stat-value,
.stat-card-1 .stat-label,
.stat-card-1 .stat-trend,
.stat-card-1 .stat-icon {
  color: white;
}

.stat-card-2 .stat-value,
.stat-card-2 .stat-label,
.stat-card-2 .stat-trend,
.stat-card-2 .stat-icon {
  color: white;
}

.stat-card-3 .stat-value,
.stat-card-3 .stat-label,
.stat-card-3 .stat-trend,
.stat-card-3 .stat-icon {
  color: white;
}

.stat-card-4 .stat-value,
.stat-card-4 .stat-label,
.stat-card-4 .stat-trend,
.stat-card-4 .stat-icon {
  color: white;
}

.stat-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
  z-index: 2;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  margin-bottom: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 12px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.stat-trend.positive {
  background: rgba(103, 194, 58, 0.2);
}
.stat-trend.negative {
  background: rgba(245, 108, 108, 0.2);
}
.stat-trend.neutral {
  background: rgba(255, 255, 255, 0.2);
}

.stat-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  z-index: 1;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.left-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.right-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-card {
  min-height: 320px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #2c3e50;
}

.chart-container {
  height: 280px;
}

.quick-actions {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.quick-actions:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.quick-actions .actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.action-button {
  height: 52px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.pending-items {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.pending-items:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.pending-list {
  max-height: 320px;
  overflow-y: auto;
}

.pending-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 0 -8px;
  padding-left: 8px;
  padding-right: 8px;
}

.pending-item:hover {
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.1) 0%,
    rgba(118, 75, 162, 0.1) 100%
  );
  transform: translateX(4px);
}

.pending-item:last-child {
  border-bottom: none;
}

.item-info {
  flex: 1;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 4px;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-date {
  font-size: 12px;
  color: #7f8c8d;
}

.item-arrow {
  color: #c0c4cc;
}

.recent-activities {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.recent-activities:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.activity-timeline {
  max-height: 320px;
  overflow-y: auto;
}

.activity-content {
  margin-bottom: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.activity-content:hover {
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.05) 0%,
    rgba(118, 75, 162, 0.05) 100%
  );
}

.activity-title {
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
  font-weight: 500;
}

.activity-user {
  font-size: 12px;
  color: #7f8c8d;
  opacity: 0.8;
}

.empty-state {
  padding: 32px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
