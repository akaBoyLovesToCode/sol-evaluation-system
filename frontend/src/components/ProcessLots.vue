<template>
  <el-card class="form-section">
    <template #header>
      <div class="card-header">
        <span>{{ t('nested.processLots') }}</span>
        <div class="header-actions">
          <el-button
            v-if="!readonly"
            size="small"
            @click.stop="() => emit('paste-lots', processIndex)"
          >
            <template #icon><DocumentCopy /></template>
            {{ t('nested.pasteList') }}
          </el-button>
          <el-button
            v-if="!readonly"
            type="primary"
            size="small"
            @click.stop="() => emit('add-lot', processIndex)"
          >
            <template #icon><Plus /></template>
            {{ t('nested.addLot') }}
          </el-button>
        </div>
      </div>
    </template>

    <el-table
      v-if="process.lots.length"
      :data="process.lots"
      border
      size="small"
      class="lots-table"
    >
      <el-table-column label="#" width="60">
        <template #default="{ $index }">{{ $index + 1 }}</template>
      </el-table-column>
      <el-table-column :label="t('nested.processLotName')" min-width="220">
        <template #default="{ row }">
          <el-input
            v-model="row.lot_number"
            :placeholder="t('nested.lotNumberPlaceholder')"
            :readonly="readonly"
          />
        </template>
      </el-table-column>
      <el-table-column :label="t('nested.quantity')" width="180">
        <template #default="{ row }">
          <el-input-number
            v-model="row.quantity"
            :min="0"
            :step="1"
            controls-position="right"
            :disabled="readonly"
          />
        </template>
      </el-table-column>
      <el-table-column :label="t('nested.lotId')" width="200">
        <template #default="{ row }">
          <el-tooltip :content="row.client_id" placement="top">
            <span class="lot-id">{{ row.client_id }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column v-if="!readonly" :label="t('nested.actions')" width="160" align="right">
        <template #default="{ $index }">
          <div class="lots-actions">
            <el-button size="small" @click.stop="() => emit('duplicate-lot', processIndex, $index)">
              <template #icon><DocumentCopy /></template>
              {{ t('nested.duplicate') }}
            </el-button>
            <el-button
              size="small"
              type="danger"
              aria-label="Remove lot"
              title="Remove lot"
              @click.stop="() => emit('remove-lot', processIndex, $index)"
            >
              <template #icon><Delete /></template>
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else :description="t('nested.emptyLotsDescription')" />
  </el-card>
</template>

<script setup>
const { processIndex, process, readonly, t } = defineProps({
  processIndex: {
    type: Number,
    required: true,
  },
  process: {
    type: Object,
    required: true,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  t: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits(['add-lot', 'duplicate-lot', 'remove-lot', 'paste-lots'])
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.lots-table {
  width: 100%;
}

.lots-actions {
  display: flex;
  gap: 8px;
}

.lot-id {
  font-size: 12px;
  color: #909399;
  cursor: default;
}
</style>
