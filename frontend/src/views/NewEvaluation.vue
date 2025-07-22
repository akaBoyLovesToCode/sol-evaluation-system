<template>
  <div class="new-evaluation-page" v-loading="loading">
    <div class="page-header">
      <h1 class="page-title">
        {{ isEditMode ? "编辑评价" : $t("evaluation.new.title") }}
      </h1>
      <p class="page-description">
        {{ isEditMode ? "修改评价信息" : $t("evaluation.new.description") }}
      </p>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="evaluation-form"
    >
      <el-card class="form-section fade-in-up" style="animation-delay: 0.1s">
        <template #header>
          <span>{{ $t("evaluation.basicInfo") }}</span>
        </template>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item
              :label="$t('evaluation.typeLabel')"
              prop="evaluation_type"
            >
              <el-radio-group
                v-model="form.evaluation_type"
                @change="handleTypeChange"
              >
                <el-radio value="new_product">{{
                  $t("evaluation.type.new_product")
                }}</el-radio>
                <el-radio value="mass_production">{{
                  $t("evaluation.type.mass_production")
                }}</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              :label="$t('evaluation.productName')"
              prop="product_name"
            >
              <el-input
                v-model="form.product_name"
                :placeholder="$t('evaluation.placeholders.productName')"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="P/N" prop="part_number">
              <el-input
                v-model="form.part_number"
                :placeholder="$t('evaluation.placeholders.partNumber')"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('evaluation.startDate')" prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                :placeholder="$t('evaluation.placeholders.startDate')"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item
              :label="$t('evaluation.expectedEndDate')"
              prop="expected_end_date"
            >
              <el-date-picker
                v-model="form.expected_end_date"
                type="date"
                :placeholder="$t('evaluation.placeholders.expectedEndDate')"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="isEditMode">
            <el-form-item
              :label="$t('evaluation.actualEndDate')"
              prop="end_date"
            >
              <el-date-picker
                v-model="form.end_date"
                type="date"
                :placeholder="$t('evaluation.placeholders.actualEndDate')"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="$t('evaluation.reason')" prop="reason">
              <el-select
                v-model="form.reason"
                :placeholder="$t('evaluation.placeholders.reason')"
                style="width: 100%"
              >
                <el-option
                  :label="$t('evaluation.reasons.new_product_development')"
                  value="new_product_development"
                />
                <el-option
                  :label="$t('evaluation.reasons.quality_improvement')"
                  value="quality_improvement"
                />
                <el-option
                  :label="$t('evaluation.reasons.cost_optimization')"
                  value="cost_optimization"
                />
                <el-option
                  :label="$t('evaluation.reasons.customer_requirement')"
                  value="customer_requirement"
                />
                <el-option
                  :label="$t('evaluation.reasons.other')"
                  value="other"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              :label="$t('evaluation.processStep')"
              prop="process_step"
            >
              <el-input
                v-model="form.process_step"
                :placeholder="$t('evaluation.placeholders.processStep')"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item
          :label="$t('evaluation.descriptionLabel')"
          prop="description"
        >
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            :placeholder="$t('evaluation.placeholders.description')"
          />
        </el-form-item>
      </el-card>

      <el-card class="form-section fade-in-up" style="animation-delay: 0.3s">
        <template #header>
          <span>{{ $t("evaluation.technicalSpec") }}</span>
        </template>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item
              :label="$t('evaluation.pgmVersion')"
              prop="pgm_version"
            >
              <el-input
                v-model="form.pgm_version"
                :placeholder="$t('evaluation.placeholders.pgmVersion')"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              :label="$t('evaluation.materialInfo')"
              prop="material_info"
            >
              <el-input
                v-model="form.material_info"
                :placeholder="$t('evaluation.placeholders.materialInfo')"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('evaluation.capacity')" prop="capacity">
              <el-input
                v-model="form.capacity"
                :placeholder="$t('evaluation.placeholders.capacity')"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item
              :label="$t('evaluation.interfaceType')"
              prop="interface_type"
            >
              <el-select
                v-model="form.interface_type"
                :placeholder="$t('evaluation.placeholders.interfaceType')"
                style="width: 100%"
              >
                <el-option label="SATA" value="SATA" />
                <el-option label="NVMe" value="NVMe" />
                <el-option label="PCIe" value="PCIe" />
                <el-option :label="$t('common.other')" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              :label="$t('evaluation.formFactor')"
              prop="form_factor"
            >
              <el-select
                v-model="form.form_factor"
                :placeholder="$t('evaluation.placeholders.formFactor')"
                style="width: 100%"
              >
                <el-option
                  :label="$t('evaluation.formFactors.2_5_inch')"
                  value="2.5"
                />
                <el-option
                  :label="$t('evaluation.formFactors.m2_2280')"
                  value="M.2_2280"
                />
                <el-option
                  :label="$t('evaluation.formFactors.m2_2242')"
                  value="M.2_2242"
                />
                <el-option :label="$t('common.other')" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              :label="$t('evaluation.temperatureGrade')"
              prop="temperature_grade"
            >
              <el-select
                v-model="form.temperature_grade"
                :placeholder="$t('evaluation.placeholders.temperatureGrade')"
                style="width: 100%"
              >
                <el-option
                  :label="$t('evaluation.temperatureGrades.commercial')"
                  value="commercial"
                />
                <el-option
                  :label="$t('evaluation.temperatureGrades.industrial')"
                  value="industrial"
                />
                <el-option
                  :label="$t('evaluation.temperatureGrades.extended')"
                  value="extended"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <el-card
        class="form-section fade-in-up"
        v-if="form.evaluation_type"
        style="animation-delay: 0.5s"
      >
        <template #header>
          <span>{{ $t("evaluation.process") }}</span>
        </template>

        <div class="process-selection">
          <div
            v-if="form.evaluation_type === 'new_product'"
            class="process-group"
          >
            <h4>{{ $t("evaluation.newProductProcess") }}</h4>
            <el-checkbox-group v-model="form.processes">
              <el-checkbox value="doe">{{
                $t("evaluation.processes.doe")
              }}</el-checkbox>
              <el-checkbox value="ppq">{{
                $t("evaluation.processes.ppq")
              }}</el-checkbox>
              <el-checkbox value="prq">{{
                $t("evaluation.processes.prq")
              }}</el-checkbox>
            </el-checkbox-group>
            <p class="process-note">
              {{ $t("evaluation.newProductNote") }}
            </p>
          </div>

          <div
            v-else-if="form.evaluation_type === 'mass_production'"
            class="process-group"
          >
            <h4>{{ $t("evaluation.massProductionProcess") }}</h4>
            <el-checkbox-group v-model="form.processes">
              <el-checkbox value="production_test">{{
                $t("evaluation.processes.production_test")
              }}</el-checkbox>
              <el-checkbox value="aql">{{
                $t("evaluation.processes.aql")
              }}</el-checkbox>
            </el-checkbox-group>
            <p class="process-note">
              {{ $t("evaluation.massProductionNote") }}
            </p>
          </div>
        </div>
      </el-card>

      <div class="form-actions fade-in-up" style="animation-delay: 0.7s">
        <el-button @click="handleCancel">{{ $t("common.cancel") }}</el-button>

        <!-- Create Mode Buttons -->
        <template v-if="!isEditMode">
          <el-button
            type="primary"
            @click="handleSave(false)"
            :loading="saving"
          >
            {{ $t("evaluation.saveDraft") }}
          </el-button>
          <el-button
            type="success"
            @click="handleSave(true)"
            :loading="submitting"
          >
            {{ $t("evaluation.submit") }}
          </el-button>
        </template>

        <!-- Edit Mode Buttons -->
        <template v-if="isEditMode">
          <el-button type="danger" @click="handleDelete" :loading="deleting">
            {{ $t("common.delete") }}
          </el-button>
          <el-button
            type="primary"
            @click="handleSave(false)"
            :loading="saving"
          >
            {{ $t("common.save") }}
          </el-button>
          <el-button type="success" @click="handleFinish" :loading="finishing">
            {{ $t("evaluation.finish") }}
          </el-button>
        </template>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import { ElMessage, ElMessageBox } from "element-plus";
import api from "../utils/api";

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const formRef = ref();
const saving = ref(false);
const submitting = ref(false);
const loading = ref(false);
const deleting = ref(false);
const finishing = ref(false);

// 检测是否为编辑模式
const isEditMode = computed(
  () => route.name === "EditEvaluation" && route.params.id,
);
const evaluationId = computed(() => route.params.id);

const form = reactive({
  evaluation_type: "",
  product_name: "",
  part_number: "",
  start_date: "",
  expected_end_date: "",
  end_date: "", // Actual end date
  reason: "",
  process_step: "", // Process step identifier (e.g., M031)
  description: "",
  pgm_version: "",
  material_info: "",
  capacity: "",
  interface_type: "",
  form_factor: "",
  temperature_grade: "",
  processes: [],
});

const rules = computed(() => ({
  evaluation_type: [
    {
      required: true,
      message: t("validation.requiredField.type"),
      trigger: "change",
    },
  ],
  product_name: [
    {
      required: true,
      message: t("validation.requiredField.productName"),
      trigger: "blur",
    },
  ],
  part_number: [
    {
      required: true,
      message: t("validation.requiredField.partNumber"),
      trigger: "blur",
    },
  ],
  start_date: [
    {
      required: true,
      message: t("validation.requiredField.startDate"),
      trigger: "change",
    },
  ],
  expected_end_date: [
    {
      required: true,
      message: t("validation.requiredField.expectedEndDate"),
      trigger: "change",
    },
  ],
  process_step: [
    {
      required: true,
      message: t("validation.requiredField.processStep"),
      trigger: "blur",
    },
  ],
  reason: [
    {
      required: true,
      message: t("validation.requiredField.reason"),
      trigger: "change",
    },
  ],
  description: [
    {
      required: true,
      message: t("validation.requiredField.description"),
      trigger: "blur",
    },
  ],
  end_date: [
    // Conditional validation: required only when finishing
    {
      validator: (rule, value, callback) => {
        if (finishing.value && !value) {
          callback(new Error(t("validation.requiredField.actualEndDate")));
        } else {
          callback();
        }
      },
      trigger: "change",
    },
  ],
}));

const handleTypeChange = (type) => {
  form.processes = [];
  if (type === "new_product") {
    form.processes = ["doe", "ppq", "prq"];
  } else if (type === "mass_production") {
    form.processes = ["production_test", "aql"];
  }
};

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm(
      t("evaluation.cancelConfirm"),
      t("common.confirmCancel"),
      {
        confirmButtonText: t("common.confirm"),
        cancelButtonText: t("common.cancel"),
        type: "warning",
      },
    );
    router.push("/evaluations");
  } catch {
    // User cancelled
  }
};

const buildPayload = () => ({
  evaluation_type: form.evaluation_type,
  product_name: form.product_name,
  part_number: form.part_number,
  start_date: form.start_date,
  expected_end_date: form.expected_end_date,
  end_date: form.end_date || null,
  reason: form.reason,
  process_step: form.process_step,
  evaluation_reason: form.reason, // Map reason to evaluation_reason for backend compatibility
  description: form.description,
  remarks: form.description, // Map description to remarks for backend compatibility
  pgm_version: form.pgm_version,
  material_info: form.material_info,
  capacity: form.capacity,
  interface_type: form.interface_type,
  form_factor: form.form_factor,
  temperature_grade: form.temperature_grade,
  processes: form.processes,
});

const handleSave = async (submit = false) => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();

    const loadingRef = submit ? submitting : saving;
    loadingRef.value = true;

    const payload = buildPayload();

    // Determine status based on action
    if (isEditMode.value) {
      // In edit mode, "Save" keeps the current status, it doesn't revert to draft
      // The backend should handle preserving the status if not provided.
    } else {
      payload.status = submit ? "in_progress" : "draft";
    }

    let response;
    if (isEditMode.value) {
      response = await api.put(`/evaluations/${evaluationId.value}`, payload);
      ElMessage.success(t("common.saveSuccess"));
      // Stay on the page after saving in edit mode
    } else {
      response = await api.post("/evaluations", payload);
      ElMessage.success(
        submit ? t("evaluation.submitSuccess") : t("evaluation.saveSuccess"),
      );
      const targetId = response.data?.data?.evaluation?.id;
      if (targetId) {
        router.push(`/evaluations/${targetId}`);
      } else {
        console.error("Invalid response structure:", response.data);
        ElMessage.error(t("common.responseError"));
      }
    }
  } catch (error) {
    if (error.name !== "ValidationError") {
      ElMessage.error(
        isEditMode.value
          ? t("common.saveError")
          : submit
            ? t("evaluation.submitError")
            : t("evaluation.saveError"),
      );
      console.error("Save failed:", error);
    }
  } finally {
    saving.value = false;
    submitting.value = false;
  }
};

const handleFinish = async () => {
  if (!formRef.value) return;
  finishing.value = true; // To trigger validation

  try {
    await formRef.value.validate();

    await ElMessageBox.confirm(
      t("evaluation.finishConfirm"),
      t("common.confirmAction"),
      { type: "info" },
    );

    await api.put(`/evaluations/${evaluationId.value}/status`, {
      status: "completed",
    });

    ElMessage.success(t("evaluation.finishSuccess"));
    router.push(`/evaluations/${evaluationId.value}`);
  } catch (error) {
    if (error && error.name !== "ValidationError" && error !== "cancel") {
      ElMessage.error(t("evaluation.finishError"));
      console.error("Finish failed:", error);
    }
  } finally {
    finishing.value = false;
  }
};

const handleDelete = async () => {
  if (!isEditMode.value) return;

  try {
    await ElMessageBox.confirm(
      t("evaluation.deleteConfirm"),
      t("common.confirmDelete"),
      {
        confirmButtonText: t("common.confirm"),
        cancelButtonText: t("common.cancel"),
        type: "warning",
      },
    );

    deleting.value = true;
    await api.delete(`/evaluations/${evaluationId.value}`);

    ElMessage.success(t("evaluation.deleteSuccess"));
    router.push("/evaluations");
  } catch (error) {
    if (error && error !== "cancel") {
      ElMessage.error(t("common.deleteError"));
      console.error("Delete failed:", error);
    }
  } finally {
    deleting.value = false;
  }
};

const fetchEvaluation = async () => {
  if (!isEditMode.value) return;

  try {
    loading.value = true;
    const response = await api.get(`/evaluations/${evaluationId.value}`);
    const evaluation = response.data.data.evaluation;

    Object.assign(form, {
      evaluation_type: evaluation.evaluation_type || "",
      product_name: evaluation.product_name || "",
      part_number: evaluation.part_number || "",
      start_date: evaluation.start_date || "",
      expected_end_date: evaluation.expected_end_date || "",
      end_date: evaluation.end_date || "",
      reason: evaluation.evaluation_reason || evaluation.reason || "",
      process_step: evaluation.process_step || "",
      description: evaluation.remarks || evaluation.description || "",
      pgm_version: evaluation.pgm_version || "",
      material_info: evaluation.material_info || "",
      capacity: evaluation.capacity || "",
      interface_type: evaluation.interface_type || "",
      form_factor: evaluation.form_factor || "",
      temperature_grade: evaluation.temperature_grade || "",
      processes: evaluation.processes || [],
    });
  } catch (error) {
    ElMessage.error("获取评价数据失败");
    console.error("Failed to fetch evaluation:", error);
    router.push("/evaluations");
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchEvaluation();
});
</script>

<style scoped>
.new-evaluation-page {
  padding: 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.page-header {
  margin-bottom: 32px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-description {
  color: #7f8c8d;
  margin: 0;
  font-size: 16px;
  opacity: 0.8;
}

.evaluation-form {
  max-width: 1200px;
}

.form-section {
  margin-bottom: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  overflow: hidden;
}

.form-section:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.form-section :deep(.el-card__header) {
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.1) 0%,
    rgba(118, 75, 162, 0.1) 100%
  );
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.form-section :deep(.el-card__body) {
  padding: 32px;
}

.form-section :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.form-section :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.form-section :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.form-section :deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
}

.form-section :deep(.el-textarea__inner) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.form-section :deep(.el-textarea__inner:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.form-section :deep(.el-textarea__inner:focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.form-section :deep(.el-date-editor) {
  border-radius: 12px;
}

.form-section :deep(.el-radio) {
  margin-right: 24px;
  font-weight: 500;
}

.form-section :deep(.el-radio__input.is-checked .el-radio__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.form-section :deep(.el-checkbox) {
  font-weight: 500;
}

.form-section :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.process-selection {
  padding: 24px;
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.05) 0%,
    rgba(118, 75, 162, 0.05) 100%
  );
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.process-group h4 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-weight: 600;
  font-size: 16px;
}

.process-group .el-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.process-note {
  margin: 20px 0 0 0;
  padding: 16px 20px;
  background: linear-gradient(
    135deg,
    rgba(33, 150, 243, 0.1) 0%,
    rgba(25, 118, 210, 0.1) 100%
  );
  border-left: 4px solid #2196f3;
  color: #1976d2;
  font-size: 14px;
  border-radius: 12px;
  font-weight: 500;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.form-actions .el-button {
  min-width: 140px;
  height: 48px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.form-actions .el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.form-actions .el-button--success {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border: none;
}

.form-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.form-actions .el-button--primary:hover {
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.form-actions .el-button--success:hover {
  box-shadow: 0 8px 24px rgba(67, 233, 123, 0.4);
}

.form-actions .el-button--danger {
  background: linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%);
  border-color: transparent;
  color: white;
}

.form-actions .el-button--danger:hover {
  box-shadow: 0 8px 24px rgba(255, 117, 140, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .evaluation-form {
    max-width: 100%;
  }

  .form-actions {
    flex-direction: column;
    align-items: center;
  }

  .form-actions .el-button {
    width: 200px;
  }
}
</style>
