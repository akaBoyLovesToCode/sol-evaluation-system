<template>
  <div v-loading="loading" :class="['evaluation-detail-page', inDialog ? 'dialog-mode' : '']">
    <div v-if="evaluation && !inDialog" class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          {{ evaluation.evaluation_number }}
          <el-tag :type="getStatusTagType(evaluation.status)" class="status-tag">
            {{ $t(`status.${evaluation.status}`) }}
          </el-tag>
        </h1>
        <p class="page-description">{{ evaluation.product_name }}</p>
      </div>
      <div class="header-right">
        <el-button v-if="canEdit" type="primary" :icon="Edit" @click="handleEdit">
          {{ $t('common.edit') }}
        </el-button>

        <el-dropdown v-if="canOperate" @command="handleOperation">
          <el-button type="primary" :icon="MoreFilled">
            {{ $t('common.operations') }}
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <!-- Approvals removed in simplified mode -->
              <el-dropdown-item v-if="canPause" command="pause" :icon="VideoPause">
                {{ $t('evaluation.pause') }}
              </el-dropdown-item>
              <el-dropdown-item v-if="canResume" command="resume" :icon="VideoPlay">
                {{ $t('evaluation.resume') }}
              </el-dropdown-item>
              <el-dropdown-item v-if="canCancel" command="cancel" :icon="Close" divided>
                {{ $t('evaluation.cancel') }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div v-if="evaluation" class="detail-content dialog-scroll">
      <!-- Dialog mode: Tabbed layout to reduce scrolling -->
      <template v-if="inDialog">
        <el-tabs v-model="activeTab" type="border-card" class="dialog-tabs">
          <el-tab-pane :label="$t('evaluation.basicInformation')" name="details">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span>{{ $t('evaluation.basicInformation') }}</span>
                  <div class="header-actions">
                    <template v-if="!editing && canEdit">
                      <el-button size="small" type="primary" :icon="Edit" @click="startEdit">
                        {{ $t('common.edit') }}
                      </el-button>
                    </template>
                    <template v-else-if="editing">
                      <el-button size="small" :icon="Close" @click="cancelEdit">
                        {{ $t('common.cancel') }}
                      </el-button>
                      <el-button
                        size="small"
                        type="primary"
                        :loading="saving"
                        :icon="Check"
                        @click="saveEdit"
                      >
                        {{ $t('common.save') }}
                      </el-button>
                    </template>
                  </div>
                </div>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item :label="$t('evaluation.evaluationNumber')">
                  {{ evaluation.evaluation_number }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.evaluationType')">
                  <el-tag
                    :type="evaluation.evaluation_type === 'new_product' ? 'primary' : 'success'"
                  >
                    {{ $t(`evaluation.type.${evaluation.evaluation_type}`) }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.productName')">
                  <template v-if="editing">
                    <el-input v-model="editForm.product_name" />
                  </template>
                  <template v-else>
                    {{ evaluation.product_name }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.partNumber')">
                  <template v-if="editing">
                    <el-input v-model="editForm.part_number" />
                  </template>
                  <template v-else>
                    {{ evaluation.part_number }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.scsCharger')">
                  <template v-if="editing">
                    <el-input v-model="editForm.scs_charger_name" />
                  </template>
                  <template v-else>
                    {{ evaluation.scs_charger_name || '-' }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.headOfficeCharger')">
                  <template v-if="editing">
                    <el-input v-model="editForm.head_office_charger_name" />
                  </template>
                  <template v-else>
                    {{ evaluation.head_office_charger_name || '-' }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.startDate')">
                  <template v-if="editing">
                    <el-date-picker
                      v-model="editForm.start_date"
                      type="date"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      style="width: 100%"
                    />
                  </template>
                  <template v-else>
                    {{ formatDate(evaluation.start_date) }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.actualEndDate')">
                  <template v-if="editing">
                    <el-date-picker
                      v-model="editForm.end_date"
                      type="date"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      style="width: 100%"
                    />
                  </template>
                  <template v-else>
                    {{ evaluation.actual_end_date ? formatDate(evaluation.actual_end_date) : '-' }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.processStep')">
                  <template v-if="editing">
                    <el-select
                      v-model="editForm.process_step"
                      multiple
                      collapse-tags
                      style="width: 100%"
                    >
                      <el-option
                        v-for="step in processStepChoices"
                        :key="step"
                        :label="step"
                        :value="step"
                      />
                    </el-select>
                  </template>
                  <template v-else>
                    {{ formatProcessSteps(evaluation.process_step) }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.reason')">
                  <template v-if="editing">
                    <el-select v-model="editForm.evaluation_reason" style="width: 100%">
                      <el-option
                        v-for="opt in reasonOptions"
                        :key="opt.value"
                        :label="opt.label"
                        :value="opt.value"
                      />
                    </el-select>
                  </template>
                  <template v-else>
                    {{ getReasonText(evaluation.evaluation_reason) }}
                  </template>
                </el-descriptions-item>
              </el-descriptions>

              <div class="description-section">
                <h4>{{ $t('evaluation.evaluationDescription') }}</h4>
                <template v-if="editing">
                  <el-input v-model="editForm.remarks" type="textarea" :rows="3" />
                </template>
                <template v-else>
                  <p>{{ evaluation.remarks || evaluation.description || '-' }}</p>
                </template>
              </div>
            </el-card>

            <el-card class="sidebar-card" style="margin-top: 12px">
              <template #header>
                <span>{{ $t('evaluation.statusInformation') }}</span>
              </template>
              <div class="status-info">
                <div class="status-item">
                  <span class="label">{{ $t('evaluation.currentStatus') }}：</span>
                  <template v-if="editing">
                    <el-select v-model="editForm.status" size="small" style="width: 180px">
                      <el-option
                        v-for="opt in statusOptions"
                        :key="opt.value"
                        :label="opt.label"
                        :value="opt.value"
                      />
                    </el-select>
                  </template>
                  <template v-else>
                    <el-tag :type="getStatusTagType(evaluation.status)">
                      {{ $t(`status.${evaluation.status}`) }}
                    </el-tag>
                  </template>
                </div>
                <div class="status-item">
                  <span class="label">{{ $t('evaluation.createdAt') }}：</span>
                  <span>{{ formatDateTime(evaluation.created_at) }}</span>
                </div>
                <div class="status-item">
                  <span class="label">{{ $t('evaluation.updatedAt') }}：</span>
                  <span>{{ formatDateTime(evaluation.updated_at) }}</span>
                </div>
              </div>
            </el-card>

            <el-card class="sidebar-card" style="margin-top: 12px">
              <template #header>
                <div class="card-header">
                  <span>{{ $t('evaluation.relatedFiles') }}</span>
                  <el-button v-if="canEdit" size="small" :icon="Plus" @click="handleUploadFile">
                    {{ $t('evaluation.upload') }}
                  </el-button>
                </div>
              </template>
              <div class="files-list">
                <div v-for="file in evaluation.files" :key="file.id" class="file-item">
                  <el-icon class="file-icon"><Document /></el-icon>
                  <div class="file-info">
                    <div class="file-name">{{ file.filename }}</div>
                    <div class="file-meta">
                      {{ formatFileSize(file.size) }} •
                      {{ formatDate(file.created_at) }}
                    </div>
                  </div>
                  <el-button size="small" :icon="Download" @click="handleDownloadFile(file)" />
                </div>
                <div v-if="!evaluation.files || evaluation.files.length === 0" class="empty-files">
                  {{ $t('evaluation.noRelatedFiles') }}
                </div>
              </div>
            </el-card>
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.technicalSpecifications')" name="specs">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span>{{ $t('evaluation.technicalSpecifications') }}</span>
                  <div class="header-actions">
                    <template v-if="!editing && canEdit">
                      <el-button size="small" type="primary" :icon="Edit" @click="startEdit">
                        {{ $t('common.edit') }}
                      </el-button>
                    </template>
                    <template v-else-if="editing">
                      <el-button size="small" :icon="Close" @click="cancelEdit">
                        {{ $t('common.cancel') }}
                      </el-button>
                      <el-button
                        size="small"
                        type="primary"
                        :loading="saving"
                        :icon="Check"
                        @click="saveEdit"
                      >
                        {{ $t('common.save') }}
                      </el-button>
                    </template>
                  </div>
                </div>
              </template>
              <el-descriptions :column="2" border class="technical-specs">
                <el-descriptions-item :label="$t('evaluation.pgmVersion')">
                  <template v-if="editing">
                    <el-input v-model="editForm.pgm_version" />
                  </template>
                  <template v-else>
                    {{ evaluation.pgm_version || '-' }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.capacity')">
                  <template v-if="editing">
                    <el-input v-model="editForm.capacity" />
                  </template>
                  <template v-else>
                    {{ evaluation.capacity || '-' }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.interfaceType')">
                  <template v-if="editing">
                    <el-select v-model="editForm.interface_type" style="width: 100%">
                      <el-option :label="$t('evaluation.interfaceTypes.sata')" value="SATA" />
                      <el-option :label="$t('evaluation.interfaceTypes.nvme')" value="NVMe" />
                      <el-option :label="$t('evaluation.interfaceTypes.pcie')" value="PCIe" />
                      <el-option :label="$t('common.other')" value="other" />
                    </el-select>
                  </template>
                  <template v-else>
                    {{ evaluation.interface_type || '-' }}
                  </template>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('evaluation.formFactor')">
                  <template v-if="editing">
                    <el-select v-model="editForm.form_factor" style="width: 100%">
                      <el-option :label="$t('evaluation.formFactors.2_5_inch')" value="2.5" />
                      <el-option :label="$t('evaluation.formFactors.m2_2280')" value="M.2_2280" />
                      <el-option :label="$t('evaluation.formFactors.m2_2242')" value="M.2_2242" />
                      <el-option :label="$t('common.other')" value="other" />
                    </el-select>
                  </template>
                  <template v-else>
                    {{ evaluation.form_factor || '-' }}
                  </template>
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.evaluationProcesses')" name="processes">
            <el-card
              v-if="evaluation.processes && evaluation.processes.length >= 0"
              class="info-card"
            >
              <template #header>
                <div class="card-header">
                  <span>{{ $t('evaluation.evaluationProcesses') }}</span>
                  <div v-if="canEdit" class="header-actions">
                    <template v-if="!isProcessEditing('new')">
                      <el-button size="small" type="primary" :icon="Plus" @click="startAddProcess">
                        {{ $t('evaluation.addProcess') }}
                      </el-button>
                    </template>
                    <template v-else>
                      <el-button size="small" :icon="Close" @click="cancelEditProcess('new')">
                        {{ $t('common.cancel') }}
                      </el-button>
                      <el-button
                        size="small"
                        type="primary"
                        :loading="processSaving['new']"
                        :icon="Check"
                        @click="saveProcess('new')"
                      >
                        {{ $t('common.save') }}
                      </el-button>
                    </template>
                  </div>
                </div>
              </template>
              <div class="processes-section">
                <!-- New process inline editor -->
                <div v-if="isProcessEditing('new')" class="process-item">
                  <div class="process-header">
                    <div class="title-with-edit">
                      <el-input
                        v-model="processEditState['new'].title"
                        size="small"
                        :placeholder="$t('evaluation.process') + ' 1'"
                        style="max-width: 240px"
                      />
                    </div>
                    <el-tag :type="getProcessStatusType(processEditState['new'].status)">
                      {{ $t(`evaluation.processStatus.${processEditState['new'].status}`) }}
                    </el-tag>
                  </div>
                  <div class="process-content">
                    <el-row :gutter="12" style="margin-bottom: 8px">
                      <el-col :span="8">
                        <label class="inline-label">{{ $t('evaluation.evalCode') }}</label>
                        <el-input v-model="processEditState['new'].eval_code" />
                      </el-col>
                      <el-col :span="8">
                        <label class="inline-label">{{ $t('evaluation.lotNumber') }}</label>
                        <el-input v-model="processEditState['new'].lot_number" />
                      </el-col>
                      <el-col :span="8">
                        <label class="inline-label">{{ $t('evaluation.quantity') }}</label>
                        <el-input-number
                          v-model="processEditState['new'].quantity"
                          :min="1"
                          style="width: 100%"
                        />
                      </el-col>
                    </el-row>
                    <el-row :gutter="12" style="margin-bottom: 8px">
                      <el-col :span="12">
                        <label class="inline-label">{{ $t('evaluation.processFlow') }}</label>
                        <el-input
                          v-model="processEditState['new'].process_description"
                          type="textarea"
                          :rows="2"
                        />
                      </el-col>
                      <el-col :span="12">
                        <label class="inline-label">{{ $t('evaluation.aqlResult') }}</label>
                        <el-input v-model="processEditState['new'].aql_result" />
                      </el-col>
                    </el-row>
                    <el-row :gutter="12" style="margin-bottom: 8px">
                      <el-col :span="12">
                        <label class="inline-label">{{
                          $t('evaluation.manufacturingTestResults')
                        }}</label>
                        <el-input
                          v-model="processEditState['new'].manufacturing_test_results"
                          type="textarea"
                          :rows="2"
                        />
                      </el-col>
                      <el-col :span="12">
                        <label class="inline-label">{{
                          $t('evaluation.defectAnalysisResults')
                        }}</label>
                        <el-input
                          v-model="processEditState['new'].defect_analysis_results"
                          type="textarea"
                          :rows="2"
                        />
                      </el-col>
                    </el-row>
                    <div>
                      <label class="inline-label">{{ $t('common.status') }}</label>
                      <el-select
                        v-model="processEditState['new'].status"
                        size="small"
                        style="width: 200px"
                      >
                        <el-option
                          v-for="opt in processStatusOptions"
                          :key="opt.value"
                          :label="opt.label"
                          :value="opt.value"
                        />
                      </el-select>
                    </div>
                  </div>
                </div>
                <div v-for="process in evaluation.processes" :key="process.id" class="process-item">
                  <div class="process-header">
                    <template v-if="isProcessEditing(process.id)">
                      <div class="title-with-edit">
                        <el-input
                          v-model="processEditState[process.id].title"
                          size="small"
                          :placeholder="$t('evaluation.process')"
                          style="max-width: 240px"
                        />
                      </div>
                    </template>
                    <template v-else>
                      <h4>{{ process.title || process.eval_code }} - {{ process.lot_number }}</h4>
                    </template>
                    <div class="header-actions">
                      <template v-if="!isProcessEditing(process.id) && canEdit">
                        <el-button
                          size="small"
                          text
                          :icon="Edit"
                          @click="startEditProcess(process)"
                        >
                          {{ $t('common.edit') }}
                        </el-button>
                        <el-button
                          size="small"
                          text
                          type="danger"
                          :icon="Delete"
                          @click="deleteProcess(process.id)"
                        >
                          {{ $t('common.delete') }}
                        </el-button>
                      </template>
                      <template v-else-if="isProcessEditing(process.id)">
                        <el-button
                          size="small"
                          text
                          :icon="Close"
                          @click="cancelEditProcess(process.id)"
                        >
                          {{ $t('common.cancel') }}
                        </el-button>
                        <el-button
                          size="small"
                          type="primary"
                          :loading="processSaving[process.id]"
                          :icon="Check"
                          @click="saveProcess(process.id)"
                        >
                          {{ $t('common.save') }}
                        </el-button>
                      </template>
                    </div>
                  </div>
                  <div class="process-content">
                    <template v-if="isProcessEditing(process.id)">
                      <el-row :gutter="12" style="margin-bottom: 8px">
                        <el-col :span="8">
                          <label class="inline-label">{{ $t('evaluation.evalCode') }}</label>
                          <el-input v-model="processEditState[process.id].eval_code" />
                        </el-col>
                        <el-col :span="8">
                          <label class="inline-label">{{ $t('evaluation.lotNumber') }}</label>
                          <el-input v-model="processEditState[process.id].lot_number" />
                        </el-col>
                        <el-col :span="8">
                          <label class="inline-label">{{ $t('evaluation.quantity') }}</label>
                          <el-input-number
                            v-model="processEditState[process.id].quantity"
                            :min="1"
                            style="width: 100%"
                          />
                        </el-col>
                      </el-row>
                      <el-row :gutter="12" style="margin-bottom: 8px">
                        <el-col :span="12">
                          <label class="inline-label">{{ $t('evaluation.processFlow') }}</label>
                          <el-input
                            v-model="processEditState[process.id].process_description"
                            type="textarea"
                            :rows="2"
                          />
                        </el-col>
                        <el-col :span="12">
                          <label class="inline-label">{{ $t('evaluation.aqlResult') }}</label>
                          <el-input v-model="processEditState[process.id].aql_result" />
                        </el-col>
                      </el-row>
                      <el-row :gutter="12" style="margin-bottom: 8px">
                        <el-col :span="12">
                          <label class="inline-label">{{
                            $t('evaluation.manufacturingTestResults')
                          }}</label>
                          <el-input
                            v-model="processEditState[process.id].manufacturing_test_results"
                            type="textarea"
                            :rows="2"
                          />
                        </el-col>
                        <el-col :span="12">
                          <label class="inline-label">{{
                            $t('evaluation.defectAnalysisResults')
                          }}</label>
                          <el-input
                            v-model="processEditState[process.id].defect_analysis_results"
                            type="textarea"
                            :rows="2"
                          />
                        </el-col>
                      </el-row>
                      <div>
                        <label class="inline-label">{{ $t('common.status') }}</label>
                        <el-select
                          v-model="processEditState[process.id].status"
                          size="small"
                          style="width: 200px"
                        >
                          <el-option
                            v-for="opt in processStatusOptions"
                            :key="opt.value"
                            :label="opt.label"
                            :value="opt.value"
                          />
                        </el-select>
                      </div>
                    </template>
                    <template v-else>
                      <p>
                        <strong>{{ $t('evaluation.quantity') }}：</strong>{{ process.quantity }}
                      </p>
                      <p>
                        <strong>{{ $t('evaluation.processFlow') }}：</strong
                        >{{ process.process_description }}
                      </p>
                      <p v-if="process.manufacturing_test_results">
                        <strong>{{ $t('evaluation.manufacturingTestResults') }}：</strong
                        >{{ process.manufacturing_test_results }}
                      </p>
                      <p v-if="process.defect_analysis_results">
                        <strong>{{ $t('evaluation.defectAnalysisResults') }}：</strong
                        >{{ process.defect_analysis_results }}
                      </p>
                      <p v-if="process.aql_result">
                        <strong>{{ $t('evaluation.aqlResult') }}：</strong>{{ process.aql_result }}
                      </p>
                      <p class="process-meta">
                        <small
                          >{{ $t('evaluation.createdAt') }}：{{
                            formatDateTime(process.created_at)
                          }}</small
                        >
                      </p>
                    </template>
                  </div>
                </div>
              </div>
            </el-card>
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.operationLogs')" name="logs">
            <el-card class="sidebar-card">
              <template #header>
                <div class="card-header">
                  <span>{{ $t('evaluation.operationLogs') }}</span>
                </div>
              </template>
              <div class="logs-list">
                <el-timeline>
                  <el-timeline-item
                    v-for="log in filteredLogs"
                    :key="log.id || log.created_at"
                    :icon="getOperationIcon(log.operation_type)"
                    :color="getOperationColor(log.operation_type)"
                  >
                    <div class="log-content">
                      <div class="log-time">{{ formatDateTime(log.created_at) }}</div>
                      <div class="log-user">
                        <el-tag size="small" type="info">{{
                          (log.request_method || 'GET').toUpperCase()
                        }}</el-tag>
                        <el-tag
                          size="small"
                          :type="log.success ? 'success' : 'danger'"
                          style="margin-left: 6px"
                          >{{ log.status_code || '-' }}</el-tag
                        >
                        <span style="margin-left: 8px">{{ log.request_path }}</span>
                      </div>
                      <div class="log-action">{{ getOperationDescription(log) }}</div>
                      <div class="log-meta">
                        <span>IP: {{ log.ip_address || '-' }}</span>
                        <span style="margin-left: 8px"
                          >UA: {{ (log.user_agent || '').slice(0, 80) }}</span
                        >
                      </div>
                      <div v-if="log.old_data || log.new_data" class="log-diff">
                        <el-button link type="primary" size="small" @click="toggleLog(log.id)">
                          {{
                            logExpanded[log.id]
                              ? $t('common.hide') || 'Hide'
                              : $t('common.details') || 'Details'
                          }}
                        </el-button>
                        <div v-show="logExpanded[log.id]">
                          <div v-if="getLogDiff(log).length > 0">
                            <div v-for="d in getLogDiff(log)" :key="d.key" class="diff-row">
                              <span class="diff-key">{{ d.key }}</span>
                              <span class="diff-from">{{ stringify(d.from) }}</span>
                              <span class="diff-arrow">→</span>
                              <span class="diff-to">{{ stringify(d.to) }}</span>
                            </div>
                          </div>
                          <div v-else>
                            <div v-if="log.new_data">
                              <strong>New:</strong> {{ stringify(parseJson(log.new_data)) }}
                            </div>
                            <div v-if="log.old_data">
                              <strong>Old:</strong> {{ stringify(parseJson(log.old_data)) }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </el-timeline-item>
                </el-timeline>
                <div v-if="filteredLogs.length === 0" class="empty-logs">
                  <el-empty :image-size="60" :description="$t('evaluation.noOperationLogs')" />
                </div>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </template>

      <!-- Full-page layout (non-dialog) -->
      <el-row v-else :gutter="20">
        <!-- 左侧主要内容 -->
        <el-col :span="16">
          <!-- {{ $t('evaluation.basicInformation') }} -->
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t('evaluation.basicInformation') }}</span>
                <div class="header-actions">
                  <template v-if="!editing && canEdit">
                    <el-button size="small" type="primary" :icon="Edit" @click="startEdit">
                      {{ $t('common.edit') }}
                    </el-button>
                  </template>
                  <template v-else-if="editing">
                    <el-button size="small" :icon="Close" @click="cancelEdit">
                      {{ $t('common.cancel') }}
                    </el-button>
                    <el-button
                      size="small"
                      type="primary"
                      :loading="saving"
                      :icon="Check"
                      @click="saveEdit"
                    >
                      {{ $t('common.save') }}
                    </el-button>
                  </template>
                </div>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="$t('evaluation.evaluationNumber')">
                {{ evaluation.evaluation_number }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.evaluationType')">
                <el-tag
                  :type="evaluation.evaluation_type === 'new_product' ? 'primary' : 'success'"
                >
                  {{ $t(`evaluation.type.${evaluation.evaluation_type}`) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.productName')">
                <template v-if="editing">
                  <el-input v-model="editForm.product_name" />
                </template>
                <template v-else>
                  {{ evaluation.product_name }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.partNumber')">
                <template v-if="editing">
                  <el-input v-model="editForm.part_number" />
                </template>
                <template v-else>
                  {{ evaluation.part_number }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.scsCharger')">
                <template v-if="editing">
                  <el-input v-model="editForm.scs_charger_name" />
                </template>
                <template v-else>
                  {{ evaluation.scs_charger_name || '-' }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.headOfficeCharger')">
                <template v-if="editing">
                  <el-input v-model="editForm.head_office_charger_name" />
                </template>
                <template v-else>
                  {{ evaluation.head_office_charger_name || '-' }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.startDate')">
                <template v-if="editing">
                  <el-date-picker
                    v-model="editForm.start_date"
                    type="date"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </template>
                <template v-else>
                  {{ formatDate(evaluation.start_date) }}
                </template>
              </el-descriptions-item>

              <el-descriptions-item :label="$t('evaluation.actualEndDate')">
                <template v-if="editing">
                  <el-date-picker
                    v-model="editForm.end_date"
                    type="date"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </template>
                <template v-else>
                  {{ evaluation.actual_end_date ? formatDate(evaluation.actual_end_date) : '-' }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.processStep')">
                <template v-if="editing">
                  <el-select
                    v-model="editForm.process_step"
                    multiple
                    collapse-tags
                    style="width: 100%"
                  >
                    <el-option
                      v-for="step in processStepChoices"
                      :key="step"
                      :label="step"
                      :value="step"
                    />
                  </el-select>
                </template>
                <template v-else>
                  {{ formatProcessSteps(evaluation.process_step) }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.reason')">
                <template v-if="editing">
                  <el-select v-model="editForm.evaluation_reason" style="width: 100%">
                    <el-option
                      v-for="opt in reasonOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </el-select>
                </template>
                <template v-else>
                  {{ getReasonText(evaluation.evaluation_reason) }}
                </template>
              </el-descriptions-item>
            </el-descriptions>

            <div class="description-section">
              <h4>{{ $t('evaluation.evaluationDescription') }}</h4>
              <template v-if="editing">
                <el-input v-model="editForm.remarks" type="textarea" :rows="3" />
              </template>
              <template v-else>
                <p>{{ evaluation.remarks || evaluation.description || '-' }}</p>
              </template>
            </div>
          </el-card>

          <!-- {{ $t('evaluation.technicalSpecifications') }} -->
          <el-card class="info-card">
            <template #header>
              <span>{{ $t('evaluation.technicalSpecifications') }}</span>
            </template>
            <el-descriptions :column="2" border class="technical-specs">
              <el-descriptions-item :label="$t('evaluation.pgmVersion')">
                <template v-if="editing">
                  <el-input v-model="editForm.pgm_version" />
                </template>
                <template v-else>
                  {{ evaluation.pgm_version || '-' }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.capacity')">
                <template v-if="editing">
                  <el-input v-model="editForm.capacity" />
                </template>
                <template v-else>
                  {{ evaluation.capacity || '-' }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.interfaceType')">
                <template v-if="editing">
                  <el-select v-model="editForm.interface_type" style="width: 100%">
                    <el-option :label="$t('evaluation.interfaceTypes.sata')" value="SATA" />
                    <el-option :label="$t('evaluation.interfaceTypes.nvme')" value="NVMe" />
                    <el-option :label="$t('evaluation.interfaceTypes.pcie')" value="PCIe" />
                    <el-option :label="$t('common.other')" value="other" />
                  </el-select>
                </template>
                <template v-else>
                  {{ evaluation.interface_type || '-' }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('evaluation.formFactor')">
                <template v-if="editing">
                  <el-select v-model="editForm.form_factor" style="width: 100%">
                    <el-option :label="$t('evaluation.formFactors.2_5_inch')" value="2.5" />
                    <el-option :label="$t('evaluation.formFactors.m2_2280')" value="M.2_2280" />
                    <el-option :label="$t('evaluation.formFactors.m2_2242')" value="M.2_2242" />
                    <el-option :label="$t('common.other')" value="other" />
                  </el-select>
                </template>
                <template v-else>
                  {{ evaluation.form_factor || '-' }}
                </template>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- Timeline view removed for clarity; list below is the source of truth -->

          <!-- {{ $t('evaluation.evaluationResults') }} -->
          <el-card v-if="evaluation.results && evaluation.results.length > 0" class="info-card">
            <template #header>
              <span>{{ $t('evaluation.evaluationResults') }}</span>
            </template>
            <div class="results-section">
              <div v-for="result in evaluation.results" :key="result.id" class="result-item">
                <div class="result-header">
                  <h4>{{ result.test_item }}</h4>
                  <el-tag :type="result.result === 'pass' ? 'success' : 'danger'">
                    {{ result.result === 'pass' ? $t('evaluation.pass') : $t('evaluation.fail') }}
                  </el-tag>
                </div>
                <div class="result-content">
                  <p>
                    <strong>{{ $t('evaluation.testConditions') }}：</strong
                    >{{ result.test_conditions }}
                  </p>
                  <p>
                    <strong>{{ $t('evaluation.testResult') }}：</strong>{{ result.test_result }}
                  </p>
                  <p v-if="result.remarks">
                    <strong>{{ $t('evaluation.remarks') }}：</strong>{{ result.remarks }}
                  </p>
                </div>
              </div>
            </div>
          </el-card>

          <el-card
            v-if="evaluation.processes && evaluation.processes.length >= 0"
            class="info-card"
          >
            <template #header>
              <div class="card-header">
                <span>{{ $t('evaluation.evaluationProcesses') }}</span>
                <div v-if="canEdit" class="header-actions">
                  <template v-if="!isProcessEditing('new')">
                    <el-button size="small" type="primary" :icon="Plus" @click="startAddProcess">
                      {{ $t('evaluation.addProcess') }}
                    </el-button>
                  </template>
                  <template v-else>
                    <el-button size="small" :icon="Close" @click="cancelEditProcess('new')">
                      {{ $t('common.cancel') }}
                    </el-button>
                    <el-button
                      size="small"
                      type="primary"
                      :loading="processSaving['new']"
                      :icon="Check"
                      @click="saveProcess('new')"
                    >
                      {{ $t('common.save') }}
                    </el-button>
                  </template>
                </div>
              </div>
            </template>
            <div class="processes-section">
              <div v-for="process in evaluation.processes" :key="process.id" class="process-item">
                <div class="process-header">
                  <h4>{{ process.title || process.eval_code }} - {{ process.lot_number }}</h4>
                  <el-tag :type="getProcessStatusType(process.status)">
                    {{ $t(`evaluation.processStatus.${process.status}`) }}
                  </el-tag>
                </div>
                <div class="process-content">
                  <p>
                    <strong>{{ $t('evaluation.quantity') }}：</strong>{{ process.quantity }}
                  </p>
                  <p>
                    <strong>{{ $t('evaluation.processFlow') }}：</strong
                    >{{ process.process_description }}
                  </p>
                  <p v-if="process.manufacturing_test_results">
                    <strong>{{ $t('evaluation.manufacturingTestResults') }}：</strong
                    >{{ process.manufacturing_test_results }}
                  </p>
                  <p v-if="process.defect_analysis_results">
                    <strong>{{ $t('evaluation.defectAnalysisResults') }}：</strong
                    >{{ process.defect_analysis_results }}
                  </p>
                  <p v-if="process.aql_result">
                    <strong>{{ $t('evaluation.aqlResult') }}：</strong>{{ process.aql_result }}
                  </p>
                  <p class="process-meta">
                    <small
                      >{{ $t('evaluation.createdAt') }}：{{
                        formatDateTime(process.created_at)
                      }}</small
                    >
                  </p>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧边栏 -->
        <el-col :span="8">
          <!-- {{ $t('evaluation.statusInformation') }} -->
          <el-card class="sidebar-card">
            <template #header>
              <span>{{ $t('evaluation.statusInformation') }}</span>
            </template>
            <div class="status-info">
              <div class="status-item">
                <span class="label">{{ $t('evaluation.currentStatus') }}：</span>
                <template v-if="editing">
                  <el-select v-model="editForm.status" size="small" style="width: 180px">
                    <el-option
                      v-for="opt in statusOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </el-select>
                </template>
                <template v-else>
                  <el-tag :type="getStatusTagType(evaluation.status)">
                    {{ $t(`status.${evaluation.status}`) }}
                  </el-tag>
                </template>
              </div>
              <div class="status-item">
                <span class="label">{{ $t('evaluation.createdAt') }}：</span>
                <span>{{ formatDateTime(evaluation.created_at) }}</span>
              </div>
              <div class="status-item">
                <span class="label">{{ $t('evaluation.updatedAt') }}：</span>
                <span>{{ formatDateTime(evaluation.updated_at) }}</span>
              </div>
              <div v-if="evaluation.approved_by" class="status-item">
                <span class="label">{{ $t('evaluation.approvedBy') }}：</span>
                <span>{{ evaluation.approved_by }}</span>
              </div>
              <div v-if="evaluation.approved_at" class="status-item">
                <span class="label">{{ $t('evaluation.approvedAt') }}：</span>
                <span>{{ formatDateTime(evaluation.approved_at) }}</span>
              </div>
            </div>
          </el-card>

          <!-- {{ $t('evaluation.relatedFiles') }} -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t('evaluation.relatedFiles') }}</span>
                <el-button v-if="canEdit" size="small" :icon="Plus" @click="handleUploadFile">
                  {{ $t('evaluation.upload') }}
                </el-button>
              </div>
            </template>
            <div class="files-list">
              <div v-for="file in evaluation.files" :key="file.id" class="file-item">
                <el-icon class="file-icon"><Document /></el-icon>
                <div class="file-info">
                  <div class="file-name">{{ file.filename }}</div>
                  <div class="file-meta">
                    {{ formatFileSize(file.size) }} •
                    {{ formatDate(file.created_at) }}
                  </div>
                </div>
                <el-button size="small" :icon="Download" @click="handleDownloadFile(file)" />
              </div>
              <div v-if="!evaluation.files || evaluation.files.length === 0" class="empty-files">
                {{ $t('evaluation.noRelatedFiles') }}
              </div>
            </div>
          </el-card>

          <!-- {{ $t('evaluation.operationLogs') }} -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t('evaluation.operationLogs') }}</span>
                <!-- Admin-only toggle removed -->
              </div>
            </template>
            <div class="logs-list">
              <el-timeline>
                <el-timeline-item
                  v-for="log in filteredLogs"
                  :key="log.id"
                  :icon="getOperationIcon(log.operation_type)"
                  :color="getOperationColor(log.operation_type)"
                >
                  <div class="log-content">
                    <div class="log-time">
                      {{ formatDateTime(log.created_at) }}
                    </div>
                    <div class="log-user">
                      {{ log.ip_address }} • {{ log.request_method }} {{ log.request_path }}
                    </div>
                    <div class="log-action">
                      {{ getOperationDescription(log) }}
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
              <div v-if="filteredLogs.length === 0" class="empty-logs">
                <el-empty :image-size="60" :description="$t('evaluation.noOperationLogs')" />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
const props = defineProps({
  inDialog: { type: Boolean, default: false },
  evaluationId: { type: [String, Number], default: null },
  processStepOptions: {
    type: Array,
    default: () => ['iARTS', 'Aging', 'LI', 'Repair'],
  },
})
// No emits used currently (inline editing in same view)
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit,
  MoreFilled,
  Check,
  Close,
  VideoPause,
  VideoPlay,
  Plus,
  Document,
  Download,
  View,
  CirclePlus,
  EditPen,
  Delete,
  CircleCheck,
  CircleClose,
  User,
  Download as DownloadIcon,
} from '@element-plus/icons-vue'
import api from '../utils/api'
// Auth removed

const route = useRoute()

const { t } = useI18n()
// Auth removed

const loading = ref(false)
const processStepChoices = computed(() => props.processStepOptions || [])

const parseProcessSteps = (value) => {
  if (!value) return []
  if (Array.isArray(value)) return value.filter(Boolean)
  return String(value)
    .split(/[|,]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const serializeProcessSteps = (steps) => {
  if (!Array.isArray(steps)) return steps ? String(steps) : ''
  return steps.filter(Boolean).join('|')
}

const formatProcessSteps = (value) => {
  const steps = parseProcessSteps(value)
  return steps.length > 0 ? steps.join(' / ') : '-'
}
const evaluation = ref(null)
// removed unused showAllLogs
const editing = ref(false)
const saving = ref(false)

const editForm = reactive({
  product_name: '',
  part_number: '',
  evaluation_reason: '',
  process_step: [],
  scs_charger_name: '',
  head_office_charger_name: '',
  status: '',
  start_date: '',
  end_date: '',
  remarks: '',
  pgm_version: '',
  capacity: '',
  interface_type: '',
  form_factor: '',
})

const reasonOptions = computed(() => {
  if (!evaluation.value) return []
  if (evaluation.value.evaluation_type === 'new_product') {
    return [
      { label: t('evaluation.reasons.horizontal_expansion'), value: 'horizontal_expansion' },
      { label: t('evaluation.reasons.direct_development'), value: 'direct_development' },
    ]
  }
  return [
    { label: t('evaluation.reasons.pgm_improvement'), value: 'pgm_improvement' },
    { label: t('evaluation.reasons.firmware_change'), value: 'firmware_change' },
    { label: t('evaluation.reasons.bom_change'), value: 'bom_change' },
    { label: t('evaluation.reasons.customer_requirement'), value: 'customer_requirement' },
    { label: t('evaluation.reasons.nand'), value: 'nand' },
    { label: t('evaluation.reasons.nprr'), value: 'nprr' },
    { label: t('evaluation.reasons.repair'), value: 'repair' },
    { label: t('evaluation.reasons.facility'), value: 'facility' },
    { label: t('evaluation.reasons.other'), value: 'other' },
  ]
})

const statusOptions = computed(() => [
  { label: t('status.draft'), value: 'draft' },
  { label: t('status.in_progress'), value: 'in_progress' },
  { label: t('status.paused'), value: 'paused' },
  { label: t('status.completed'), value: 'completed' },
  { label: t('status.cancelled'), value: 'cancelled' },
  { label: t('status.rejected'), value: 'rejected' },
])

const syncEditForm = () => {
  if (!evaluation.value) return
  Object.assign(editForm, {
    product_name: evaluation.value.product_name || '',
    part_number: evaluation.value.part_number || '',
    evaluation_reason: evaluation.value.evaluation_reason || '',
    process_step: parseProcessSteps(evaluation.value.process_step),
    scs_charger_name: evaluation.value.scs_charger_name || '',
    head_office_charger_name: evaluation.value.head_office_charger_name || '',
    status: evaluation.value.status || 'draft',
    start_date: evaluation.value.start_date || '',
    end_date: evaluation.value.actual_end_date || '',
    remarks: evaluation.value.remarks || evaluation.value.description || '',
    pgm_version: evaluation.value.pgm_version || '',
    capacity: evaluation.value.capacity || '',
    interface_type: evaluation.value.interface_type || '',
    form_factor: evaluation.value.form_factor || '',
  })
}

const startEdit = () => {
  syncEditForm()
  editing.value = true
}

const cancelEdit = () => {
  editing.value = false
}

const saveEdit = async () => {
  if (!evaluation.value) return
  try {
    saving.value = true
    const payload = {
      product_name: editForm.product_name,
      part_number: editForm.part_number,
      evaluation_reason: editForm.evaluation_reason,
      process_step: serializeProcessSteps(editForm.process_step),
      scs_charger_name: editForm.scs_charger_name,
      head_office_charger_name: editForm.head_office_charger_name,
      start_date: editForm.start_date || null,
      end_date: editForm.end_date || null,
      remarks: editForm.remarks,
      pgm_version: editForm.pgm_version,
      capacity: editForm.capacity,
      interface_type: editForm.interface_type,
      form_factor: editForm.form_factor,
    }
    await api.put(`/evaluations/${evaluation.value.id}`, payload)
    // Update status if changed
    if (editForm.status && editForm.status !== evaluation.value.status) {
      await api.put(`/evaluations/${evaluation.value.id}/status`, { status: editForm.status })
    }
    ElMessage.success(t('common.saveSuccess'))
    await fetchEvaluation()
    editing.value = false
  } catch (error) {
    ElMessage.error(t('common.saveError'))
    console.error('Save evaluation failed:', error)
  } finally {
    saving.value = false
  }
}

const canEdit = computed(() => {
  if (!evaluation.value) return false
  return ['draft', 'in_progress', 'paused'].includes(evaluation.value.status)
})

const canOperate = computed(() => canPause.value || canResume.value || canCancel.value)

// approval flow removed in simplified mode

const canPause = computed(() => {
  if (!evaluation.value) return false
  return evaluation.value.status === 'in_progress'
})

const canResume = computed(() => {
  if (!evaluation.value) return false
  return evaluation.value.status === 'paused'
})

const canCancel = computed(() => {
  if (!evaluation.value) return false
  return ['in_progress', 'paused', 'pending_approval'].includes(evaluation.value.status)
})

// timeline steps removed; process list is source of truth

const filteredLogs = computed(() => {
  const logs = evaluation.value?.logs || []
  return logs
})

const fetchEvaluation = async () => {
  try {
    loading.value = true
    const id = props.evaluationId || route.params.id
    const response = await api.get(`/evaluations/${id}`)
    evaluation.value = response.data.data.evaluation
    // Fetch combined logs (evaluation, status, processes)
    try {
      const logsResp = await api.get(`/evaluations/${id}/logs`)
      if (logsResp.data?.data?.logs) {
        evaluation.value.logs = logsResp.data.data.logs
      }
    } catch (e) {
      // Logs fetch is non-blocking
      console.warn('Failed to fetch combined logs', e)
    }
  } catch (error) {
    ElMessage.error(t('evaluation.getEvaluationDetailsFailed'))
    console.error('Failed to fetch evaluation:', error)
  } finally {
    loading.value = false
  }
}

const handleEdit = () => {
  // Switch to inline edit mode within the detail view
  startEdit()
}

const handleOperation = async (command) => {
  try {
    let message = ''
    let confirmText = ''

    switch (command) {
      case 'approve':
        message = t('evaluation.confirmApprove')
        confirmText = t('evaluation.approve')
        break
      case 'reject':
        message = t('evaluation.confirmReject')
        confirmText = t('evaluation.reject')
        break
      case 'pause':
        message = t('evaluation.confirmPause')
        confirmText = t('evaluation.pause')
        break
      case 'resume':
        message = t('evaluation.confirmResume')
        confirmText = t('evaluation.resume')
        break
      case 'cancel':
        message = t('evaluation.confirmCancel')
        confirmText = t('evaluation.cancel')
        break
    }

    await ElMessageBox.confirm(message, t('common.confirmAction'), {
      confirmButtonText: confirmText,
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })

    // Call appropriate API endpoint based on command
    if (command === 'pause') {
      await api.put(`/evaluations/${evaluation.value.id}/status`, {
        status: 'paused',
      })
    } else if (command === 'resume') {
      await api.put(`/evaluations/${evaluation.value.id}/status`, {
        status: 'in_progress',
      })
    } else if (command === 'cancel') {
      await api.put(`/evaluations/${evaluation.value.id}/status`, {
        status: 'cancelled',
      })
    }

    ElMessage.success(t('evaluation.operationSuccess'))
    fetchEvaluation()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('evaluation.operationFailed'))
      console.error('Operation failed:', error)
    }
  }
}

const handleUploadFile = () => {
  // TODO: 实现文件上传功能
  ElMessage.info(t('evaluation.fileUploadInDevelopment'))
}

const handleDownloadFile = () => {
  // TODO: 实现文件下载功能
  ElMessage.info(t('evaluation.fileDownloadInDevelopment'))
}

const getStatusTagType = (status) => {
  const typeMap = {
    draft: 'info',
    in_progress: 'primary',
    pending_approval: 'warning',
    completed: 'success',
    paused: 'info',
    cancelled: 'danger',
    rejected: 'danger',
  }
  return typeMap[status] || 'info'
}

const getReasonText = (reason) => {
  if (reason && t(`evaluation.reasons.${reason}`)) {
    return t(`evaluation.reasons.${reason}`)
  }
  return reason || '-'
}

// helpers for old timeline removed

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getOperationIcon = (operationType) => {
  const iconMap = {
    create: CirclePlus,
    update: EditPen,
    delete: Delete,
    approve: CircleCheck,
    reject: CircleClose,
    view: View,
    login: User,
    logout: User,
    export: DownloadIcon,
  }
  return iconMap[operationType] || EditPen
}

const getOperationColor = (operationType) => {
  const colorMap = {
    create: '#67C23A',
    update: '#E6A23C',
    delete: '#F56C6C',
    approve: '#67C23A',
    reject: '#F56C6C',
    view: '#909399',
    login: '#409EFF',
    logout: '#909399',
    export: '#409EFF',
  }
  return colorMap[operationType] || '#409EFF'
}

const getOperationDescription = (log) => {
  // First, try to use a more descriptive translation based on operation type and context
  if (log.operation_type === 'create') {
    return t('evaluation.operations.created')
  } else if (log.operation_type === 'update') {
    // Check if it's a status change
    if (log.operation_description && log.operation_description.toLowerCase().includes('status')) {
      return t('evaluation.operations.statusChanged')
    }
    return t('evaluation.operations.updated')
  } else if (log.operation_type === 'delete') {
    return t('evaluation.operations.deleted')
  } else if (log.operation_type === 'export') {
    return t('evaluation.operations.exported')
  } else if (log.operation_type === 'view') {
    return t('evaluation.operations.viewed')
  } else if (log.operation_type === 'login') {
    return t('evaluation.operations.loggedIn')
  } else if (log.operation_type === 'logout') {
    return t('evaluation.operations.loggedOut')
  }

  // Fallback to original description if available, or unknown
  return log.operation_description || t('evaluation.operations.unknown')
}

// Log details helpers
const parseJson = (v) => {
  try {
    if (!v) return null
    return typeof v === 'string' ? JSON.parse(v) : v
  } catch {
    return null
  }
}
const stringify = (v) => {
  if (v === null || v === undefined) return ''
  return typeof v === 'object' ? JSON.stringify(v) : String(v)
}
const getLogDiff = (log) => {
  const oldObj = parseJson(log.old_data)
  const newObj = parseJson(log.new_data)
  if (!oldObj || !newObj) return []
  const keys = new Set([...Object.keys(oldObj), ...Object.keys(newObj)])
  const diffs = []
  keys.forEach((k) => {
    const a = oldObj[k]
    const b = newObj[k]
    if (JSON.stringify(a) !== JSON.stringify(b)) {
      diffs.push({ key: k, from: a, to: b })
    }
  })
  return diffs
}
const logExpanded = reactive({})
const toggleLog = (id) => {
  logExpanded[id] = !logExpanded[id]
}

const getProcessStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    in_progress: 'primary',
    completed: 'success',
    failed: 'danger',
  }
  return typeMap[status] || 'info'
}

onMounted(async () => {
  await fetchEvaluation()
})

// Dialog tabs
const activeTab = ref('details')

// Inline edit for processes
const processEditState = reactive({})
const processSaving = reactive({})
const isProcessEditing = (id) => !!processEditState[id]
const startEditProcess = (process) => {
  processEditState[process.id] = {
    title: process.title || '',
    eval_code: process.eval_code || '',
    lot_number: process.lot_number || '',
    quantity: process.quantity || 1,
    process_description: process.process_description || '',
    manufacturing_test_results: process.manufacturing_test_results || '',
    defect_analysis_results: process.defect_analysis_results || '',
    aql_result: process.aql_result || '',
    status: process.status || 'pending',
  }
}
const cancelEditProcess = (id) => {
  delete processEditState[id]
}
const processStatusOptions = computed(() => [
  { label: t('evaluation.processStatus.pending'), value: 'pending' },
  { label: t('evaluation.processStatus.in_progress'), value: 'in_progress' },
  { label: t('evaluation.processStatus.completed'), value: 'completed' },
  { label: t('evaluation.processStatus.failed'), value: 'failed' },
])
const saveProcess = async (id) => {
  if (!evaluation.value || !processEditState[id]) return
  try {
    processSaving[id] = true
    const payload = { ...processEditState[id] }
    if (id === 'new') {
      // Create
      await api.post(`/evaluations/${evaluation.value.id}/processes`, payload)
    } else {
      // Update
      await api.put(`/evaluations/${evaluation.value.id}/processes/${id}`, payload)
    }
    ElMessage.success(t('common.saveSuccess'))
    await fetchEvaluation()
    delete processEditState[id]
  } catch (e) {
    ElMessage.error(t('common.saveError'))
    console.error('Save process failed:', e)
  } finally {
    processSaving[id] = false
  }
}

const startAddProcess = () => {
  processEditState['new'] = {
    title: '',
    eval_code: '',
    lot_number: '',
    quantity: 1,
    process_description: '',
    manufacturing_test_results: '',
    defect_analysis_results: '',
    aql_result: '',
    status: 'pending',
  }
}

const deleteProcess = async (id) => {
  if (!evaluation.value) return
  try {
    await ElMessageBox.confirm(
      t('evaluation.deleteConfirm') || '确认删除该工序？',
      t('common.confirmDelete') || '删除确认',
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      },
    )
    await api.delete(`/evaluations/${evaluation.value.id}/processes/${id}`)
    ElMessage.success(t('evaluation.deleteSuccess') || '删除成功')
    await fetchEvaluation()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(t('common.deleteError') || '删除失败')
      console.error('Delete process failed:', e)
    }
  }
}
</script>

<style scoped>
/* Header actions in info card */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-actions {
  display: flex;
  gap: 8px;
}
/* Dialog tab layout tweaks */
.dialog-tabs :deep(.el-card__header) {
  padding: 10px 14px;
}
.dialog-tabs :deep(.el-card__body) {
  padding: 12px 14px;
}
.evaluation-detail-page {
  padding: 0;
}
.dialog-mode .page-header {
  display: none;
}
.dialog-scroll {
  max-height: calc(80vh - 140px);
  overflow: auto;
  padding-right: 4px;
}

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

.detail-content {
  margin-top: 20px;
}

.info-card {
  margin-bottom: 20px;
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

.description-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.description-section h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-weight: 600;
}

.description-section p {
  margin: 0;
  line-height: 1.6;
  color: #606266;
}

.process-timeline {
  padding: 20px 0;
}

.process-content h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-weight: 600;
}

.process-content p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 14px;
}

.process-result {
  margin-top: 8px;
}

.results-section {
  padding: 20px 0;
}

.result-item {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.result-item:last-child {
  margin-bottom: 0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-header h4 {
  margin: 0;
  color: #2c3e50;
  font-weight: 600;
}

.result-content p {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
}

.sidebar-card {
  margin-bottom: 20px;
}

.sidebar-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-info {
  padding: 16px 0;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-item:last-child {
  margin-bottom: 0;
}

.status-item .label {
  color: #7f8c8d;
  font-size: 14px;
}

.files-list {
  padding: 16px 0;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.file-item:last-child {
  border-bottom: none;
}

.file-icon {
  color: #409eff;
  font-size: 20px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.file-meta {
  font-size: 12px;
  color: #7f8c8d;
}

.empty-files {
  text-align: center;
  color: #7f8c8d;
  font-size: 14px;
  padding: 20px 0;
}

.logs-list {
  padding: 16px 0;
  max-height: 300px;
  overflow-y: auto;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.log-time {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  margin-bottom: 4px;
}

.log-user {
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.log-action {
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
}

.empty-logs {
  padding: 20px 0;
  text-align: center;
}

.logs-list :deep(.el-timeline-item__node) {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 2px solid;
  background: white;
}

.logs-list :deep(.el-timeline-item__node .el-icon) {
  font-size: 10px;
}

/* 响应式设计 */
.processes-section {
  margin-top: 10px;
}

.process-item {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 16px;
  background-color: #fafafa;
}

.process-item:last-child {
  margin-bottom: 0;
}

.process-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}

.process-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.process-content p {
  margin: 8px 0;
  line-height: 1.5;
}

.process-content p:last-child {
  margin-bottom: 0;
}

.process-content strong {
  color: #606266;
  font-weight: 600;
}

.process-meta {
  margin-top: 12px !important;
  padding-top: 8px;
  border-top: 1px dashed #e8e8e8;
  color: #909399;
  font-size: 12px;
}

.inline-label {
  display: inline-block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}
.title-with-edit {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 1200px) {
  .detail-content .el-row {
    flex-direction: column;
  }

  .detail-content .el-col {
    width: 100% !important;
  }
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
}
</style>
