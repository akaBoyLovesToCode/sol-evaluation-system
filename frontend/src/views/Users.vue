<template>
  <div class="users-page">
    <div class="page-header">
      <h1>用户管理</h1>
      <p>管理系统用户和权限设置</p>
    </div>

    <el-card>
      <div class="coming-soon">
        <el-icon size="64"><User /></el-icon>
        <h2>用户管理功能开发中</h2>
        <p>用户管理功能正在开发中，敬请期待</p>
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