<template>
  <div class="detail-header">
    <div class="header-left">
      <h1 class="page-title">
        <span>{{ evaluation.evaluation_number }}</span>
        <el-tag v-if="isSupportedStatus" :type="statusTagType" class="status-tag">
          {{ $t(`status.${evaluation.status}`) }}
        </el-tag>
      </h1>
      <p class="page-description">{{ evaluation.product_name }}</p>
    </div>
    <div class="header-right">
      <button class="detail-command secondary" type="button" @click="$emit('manage-nested')">
        {{ $t('evaluation.manageNestedProcesses') }}
      </button>
      <button v-if="canEdit" class="detail-command primary" type="button" @click="$emit('edit')">
        {{ $t('common.edit') }}
      </button>

      <el-dropdown v-if="canOperate" @command="$emit('operation', $event)">
        <button class="detail-command primary" type="button">
          {{ $t('common.operations') }}
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-if="canReopen" command="reopen">
              {{ $t('evaluation.reopen') }}
            </el-dropdown-item>
            <el-dropdown-item v-if="canCancel" command="cancel" divided>
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
  canReopen: Boolean,
  canCancel: Boolean,
})

defineEmits(['manage-nested', 'edit', 'operation'])

const supportedStatuses = ['in_progress', 'completed', 'cancelled']
const isSupportedStatus = computed(() => supportedStatuses.includes(props.evaluation.status))

const statusTagType = computed(() => {
  const typeMap = {
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'danger',
  }
  return typeMap[props.evaluation.status] || 'info'
})
</script>

<style scoped>
.detail-header {
  --console-line: #d8dee8;
  --console-ink: #1f2937;
  --console-muted: #667085;
  --console-blue: #155eef;
  --console-blue-dark: #0f48b8;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 14px;
  padding: 0;
}

.page-title {
  margin: 0 0 4px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--console-ink);
  font-size: 22px;
  font-weight: 750;
  line-height: 1.2;
  letter-spacing: 0;
}

.status-tag {
  font-size: 12px;
}

.page-description {
  margin: 0;
  color: var(--console-muted);
  font-size: 13px;
}

.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-command {
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.detail-command:hover {
  background: #f8fafc;
  border-color: #b9c3d3;
  color: #1f2937;
}

.detail-command.primary {
  background: var(--console-blue);
  border-color: var(--console-blue);
  color: #fff;
}

.detail-command.primary:hover {
  background: var(--console-blue-dark);
  border-color: var(--console-blue-dark);
  color: #fff;
}

.detail-command.secondary {
  background: #fff;
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
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
