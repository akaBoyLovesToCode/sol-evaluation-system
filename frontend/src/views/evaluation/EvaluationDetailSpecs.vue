<template>
  <el-card class="detail-panel info-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('evaluation.technicalSpecifications') }}</span>
        <div v-if="canEdit" class="header-actions">
          <template v-if="!editing">
            <el-button size="small" type="primary" class="detail-button" @click="startEdit">
              {{ $t('common.edit') }}
            </el-button>
          </template>
          <template v-else>
            <el-button size="small" class="detail-button" @click="cancelEdit">
              {{ $t('common.cancel') }}
            </el-button>
            <el-button
              size="small"
              type="primary"
              class="detail-button"
              :loading="saving"
              @click="saveEdit"
            >
              {{ $t('common.save') }}
            </el-button>
          </template>
        </div>
      </div>
    </template>

    <el-descriptions :column="isMobile ? 1 : 2" border class="technical-specs">
      <el-descriptions-item :label="$t('evaluation.pgmVersion')">
        <template v-if="editing">
          <el-input v-model="editForm.pgm_version" />
        </template>
        <template v-else>
          {{ evaluation.pgm_version || '-' }}
        </template>
      </el-descriptions-item>
      <el-descriptions-item :label="$t('evaluation.testTime')">
        <template v-if="editing">
          <el-input v-model="editForm.pgm_test_time" />
        </template>
        <template v-else>
          {{ evaluation.pgm_test_time || '-' }}
        </template>
      </el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  evaluation: { type: Object, required: true },
  canEdit: Boolean,
})

const emit = defineEmits(['update', 'save-start', 'save-end'])

useI18n()
const editing = ref(false)
const saving = ref(false)

const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1200)
const isMobile = computed(() => windowWidth.value < 768)

const updateWidth = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', updateWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})

const editForm = reactive({
  pgm_version: '',
  pgm_test_time: '',
  start_date: '',
  end_date: '',
})

const syncEditForm = () => {
  if (!props.evaluation) return
  editForm.pgm_version = props.evaluation.pgm_version || ''
  editForm.pgm_test_time = props.evaluation.pgm_test_time || ''
  editForm.start_date = props.evaluation.start_date || ''
  editForm.end_date = props.evaluation.actual_end_date || ''
}

watch(
  () => props.evaluation,
  () => syncEditForm(),
  { immediate: true, deep: true },
)

const startEdit = () => {
  syncEditForm()
  editing.value = true
}

const cancelEdit = () => {
  editing.value = false
}

const saveEdit = async () => {
  emit('save-start')
  saving.value = true
  try {
    emit('update', { ...editForm })
    editing.value = false
  } finally {
    saving.value = false
    emit('save-end')
  }
}

defineExpose({ startEdit, cancelEdit })
</script>

<style scoped>
.detail-panel {
  --console-line: #d8dee8;
  --console-ink: #1f2937;
  --console-muted: #667085;
  margin-bottom: 0;
  border: 1px solid var(--console-line);
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 750;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-button {
  height: 28px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
}

.technical-specs :deep(.el-descriptions__label) {
  width: 132px;
  min-width: 132px;
  background: #f8fafc;
  color: var(--console-muted);
  font-size: 12px;
  font-weight: 650;
}

.technical-specs :deep(.el-descriptions__content) {
  width: auto;
  min-width: 180px;
  color: var(--console-ink);
  font-size: 13px;
  font-weight: 500;
}

.technical-specs :deep(.el-descriptions__cell) {
  padding: 8px 10px;
}

.detail-panel :deep(.el-card__header) {
  min-height: 42px;
  padding: 6px 12px;
  background: #fff;
  border-bottom: 1px solid var(--console-line);
  font-weight: 750;
}

.detail-panel :deep(.el-card__body) {
  padding: 12px;
}
</style>
