<template>
  <div class="new-evaluation-page">
    <div class="page-header">
      <h1 class="page-title">新建评价</h1>
      <p class="page-description">创建新的SSD产品评价项目</p>
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
          <span>基本信息</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="评价类型" prop="evaluation_type">
              <el-radio-group v-model="form.evaluation_type" @change="handleTypeChange">
                <el-radio value="new_product">新产品</el-radio>
                <el-radio value="mass_production">量产</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SSD产品" prop="ssd_product">
              <el-input v-model="form.ssd_product" placeholder="请输入SSD产品名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="料号" prop="part_number">
              <el-input v-model="form.part_number" placeholder="请输入料号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="选择开始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预计结束日期" prop="expected_end_date">
              <el-date-picker
                v-model="form.expected_end_date"
                type="date"
                placeholder="选择预计结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评价原因" prop="reason">
              <el-select v-model="form.reason" placeholder="请选择评价原因" style="width: 100%">
                <el-option label="新产品开发" value="new_product_development" />
                <el-option label="质量改进" value="quality_improvement" />
                <el-option label="成本优化" value="cost_optimization" />
                <el-option label="客户要求" value="customer_requirement" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="评价描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入评价描述"
          />
        </el-form-item>
      </el-card>

      <el-card class="form-section fade-in-up" style="animation-delay: 0.3s">
        <template #header>
          <span>技术规格</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="PGM版本" prop="pgm_version">
              <el-input v-model="form.pgm_version" placeholder="请输入PGM版本" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="材料信息" prop="material_info">
              <el-input v-model="form.material_info" placeholder="请输入材料信息" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="容量" prop="capacity">
              <el-input v-model="form.capacity" placeholder="请输入容量" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="接口类型" prop="interface_type">
              <el-select v-model="form.interface_type" placeholder="请选择接口类型" style="width: 100%">
                <el-option label="SATA" value="SATA" />
                <el-option label="NVMe" value="NVMe" />
                <el-option label="PCIe" value="PCIe" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="外形规格" prop="form_factor">
              <el-select v-model="form.form_factor" placeholder="请选择外形规格" style="width: 100%">
                <el-option label="2.5寸" value="2.5" />
                <el-option label="M.2 2280" value="M.2_2280" />
                <el-option label="M.2 2242" value="M.2_2242" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="温度等级" prop="temperature_grade">
              <el-select v-model="form.temperature_grade" placeholder="请选择温度等级" style="width: 100%">
                <el-option label="商业级 (0°C ~ 70°C)" value="commercial" />
                <el-option label="工业级 (-40°C ~ 85°C)" value="industrial" />
                <el-option label="扩展级 (-40°C ~ 105°C)" value="extended" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <el-card class="form-section fade-in-up" v-if="form.evaluation_type" style="animation-delay: 0.5s">
        <template #header>
          <span>评价流程</span>
        </template>
        
        <div class="process-selection">
          <div v-if="form.evaluation_type === 'new_product'" class="process-group">
            <h4>新产品评价流程</h4>
            <el-checkbox-group v-model="form.processes">
              <el-checkbox value="doe">DOE (Design of Experiments)</el-checkbox>
              <el-checkbox value="ppq">PPQ (Production Part Qualification)</el-checkbox>
              <el-checkbox value="prq">PRQ (Production Readiness Qualification)</el-checkbox>
            </el-checkbox-group>
            <p class="process-note">
              注：新产品评价需要经过Part Leader和Group Leader两级审批
            </p>
          </div>
          
          <div v-else-if="form.evaluation_type === 'mass_production'" class="process-group">
            <h4>量产评价流程</h4>
            <el-checkbox-group v-model="form.processes">
              <el-checkbox value="production_test">生产测试</el-checkbox>
              <el-checkbox value="aql">AQL (Acceptable Quality Level)</el-checkbox>
            </el-checkbox-group>
            <p class="process-note">
              注：量产评价通过后无需审批，直接完成
            </p>
          </div>
        </div>
      </el-card>

      <div class="form-actions fade-in-up" style="animation-delay: 0.7s">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave(false)" :loading="saving">
          保存草稿
        </el-button>
        <el-button type="success" @click="handleSave(true)" :loading="submitting">
          提交评价
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'

const router = useRouter()
const formRef = ref()
const saving = ref(false)
const submitting = ref(false)

const form = reactive({
  evaluation_type: '',
  ssd_product: '',
  part_number: '',
  start_date: '',
  expected_end_date: '',
  reason: '',
  description: '',
  pgm_version: '',
  material_info: '',
  capacity: '',
  interface_type: '',
  form_factor: '',
  temperature_grade: '',
  processes: []
})

const rules = {
  evaluation_type: [
    { required: true, message: '请选择评价类型', trigger: 'change' }
  ],
  ssd_product: [
    { required: true, message: '请输入SSD产品名称', trigger: 'blur' }
  ],
  part_number: [
    { required: true, message: '请输入料号', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  expected_end_date: [
    { required: true, message: '请选择预计结束日期', trigger: 'change' }
  ],
  reason: [
    { required: true, message: '请选择评价原因', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入评价描述', trigger: 'blur' }
  ]
}

const handleTypeChange = (type) => {
  form.processes = []
  if (type === 'new_product') {
    form.processes = ['doe', 'ppq', 'prq']
  } else if (type === 'mass_production') {
    form.processes = ['production_test', 'aql']
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消吗？未保存的数据将丢失。',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    router.push('/evaluations')
  } catch {
    // 用户取消
  }
}

const handleSave = async (submit = false) => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    const loading = submit ? submitting : saving
    loading.value = true
    
    const data = {
      evaluation_type: form.evaluation_type,
      ssd_product: form.ssd_product,
      part_number: form.part_number,
      start_date: form.start_date,
      evaluation_reason: form.reason,
      remarks: form.description,
      status: submit ? 'in_progress' : 'draft'
    }
    
    const response = await api.post('/evaluations', data)
    
    ElMessage.success(submit ? '评价提交成功' : '保存成功')
    
    // 检查响应数据结构
    if (response.data && response.data.data && response.data.data.evaluation && response.data.data.evaluation.id) {
      router.push(`/evaluations/${response.data.data.evaluation.id}`)
    } else {
      console.error('Invalid response structure:', response.data)
      ElMessage.error('响应数据格式错误')
    }
    
  } catch (error) {
    if (error.name !== 'ValidationError') {
      ElMessage.error(submit ? '提交失败' : '保存失败')
      console.error('Save failed:', error)
    }
  } finally {
    saving.value = false
    submitting.value = false
  }
}
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
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
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
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
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
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(25, 118, 210, 0.1) 100%);
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