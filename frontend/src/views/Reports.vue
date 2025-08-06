<template>
  <div class="reports-page">
    <div class="page-header">
      <h1>{{ $t("reports.title") }}</h1>
      <p>{{ $t("reports.description") }}</p>
    </div>

    <el-card>
      <div class="coming-soon">
        <el-icon size="64"><DataAnalysis /></el-icon>
        <h2>{{ $t("reports.comingSoon") }}</h2>
        <p>{{ $t("reports.comingSoonDesc") }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { DataAnalysis } from "@element-plus/icons-vue"
</script>

<style scoped>
.reports-page {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #2c3e50;
}

.page-header p {
  margin: 0;
  color: #7f8c8d;
}

.coming-soon {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.coming-soon h2 {
  margin: 20px 0 12px 0;
  color: #2c3e50;
}

.coming-soon p {
  margin: 0;
}
</style>
