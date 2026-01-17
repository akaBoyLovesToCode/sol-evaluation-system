<template>
  <div class="page-header">
    <div class="header-left">
      <h1 class="page-title">
        {{ evaluation.evaluation_number }}
        <el-tag :type="statusTagType" class="status-tag">
          {{ $t(`status.${evaluation.status}`) }}
        </el-tag>
      </h1>
      <p class="page-description">{{ evaluation.product_name }}</p>
    </div>
    <div class="header-right">
      <el-button type="primary" plain @click="$emit('manage-nested')">
        <template #icon><Connection /></template>
        {{ $t('evaluation.manageNestedProcesses') }}
      </el-button>
      <el-button v-if="canEdit" type="primary" @click="$emit('edit')">
        <template #icon><Edit /></template>
        {{ $t('common.edit') }}
      </el-button>

      <el-dropdown v-if="canOperate" @command="$emit('operation', $event)">
        <el-button type="primary">
          <template #icon><MoreFilled /></template>
          {{ $t('common.operations') }}
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-if="canPause" command="pause">
              <el-icon><VideoPause /></el-icon>
              {{ $t('evaluation.pause') }}
            </el-dropdown-item>
            <el-dropdown-item v-if="canResume" command="resume">
              <el-icon><VideoPlay /></el-icon>
              {{ $t('evaluation.resume') }}
            </el-dropdown-item>
            <el-dropdown-item v-if="canCancel" command="cancel" divided>
              <el-icon><Close /></el-icon>
              {{ $t('evaluation.cancel') }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  evaluation: {
    type: Object,
    required: true,
  },
  canEdit: Boolean,
  canOperate: Boolean,
  canPause: Boolean,
  canResume: Boolean,
  canCancel: Boolean,
})

defineEmits(['manage-nested', 'edit', 'operation'])

const statusTagType = computed(() => {
  const typeMap = {
    draft: 'info',
    in_progress: 'primary',
    pending_approval: 'warning',
    completed: 'success',
    paused: 'info',
    cancelled: 'danger',
    rejected: 'danger',
  }
  return typeMap[props.evaluation.status] || 'info'
})
</script>

<style scoped>
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

.header-right {
  display: flex;
  gap: 12px;
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

  .header-right {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
