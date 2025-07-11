<template>
  <div class="users-page">
    <div class="page-header">
      <h1>{{ $t('users.title') }}</h1>
      <p>{{ $t('users.description') }}</p>
    </div>

    <el-card>
      <div class="coming-soon">
        <el-icon size="64"><User /></el-icon>
        <h2>{{ $t('users.comingSoon') }}</h2>
        <p>{{ $t('users.comingSoonDesc') }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { User } from '@element-plus/icons-vue'
</script>

<style scoped>
.users-page {
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