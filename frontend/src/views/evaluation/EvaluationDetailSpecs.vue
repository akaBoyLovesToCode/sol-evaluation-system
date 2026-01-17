<template>
  <el-card class="info-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('evaluation.technicalSpecifications') }}</span>
        <div v-if="canEdit" class="header-actions">
          <template v-if="!editing">
            <el-button size="small" type="primary" @click="startEdit">
              <template #icon><Edit /></template>
              {{ $t('common.edit') }}
            </el-button>
          </template>
          <template v-else>
            <el-button size="small" @click="cancelEdit">
              <template #icon><Close /></template>
              {{ $t('common.cancel') }}
            </el-button>
            <el-button size="small" type="primary" :loading="saving" @click="saveEdit">
              <template #icon><Check /></template>
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
.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.technical-specs :deep(.el-descriptions__label) {
  width: 120px;
  min-width: 120px;
}

.technical-specs :deep(.el-descriptions__content) {
  width: auto;
  min-width: 180px;
}

.info-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>
