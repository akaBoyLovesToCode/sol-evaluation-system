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
        <el-button type="primary" plain @click="goToNestedEditor">
          <template #icon><Connection /></template>
          {{ $t('evaluation.manageNestedProcesses') }}
        </el-button>
        <el-button v-if="canEdit" type="primary" @click="handleEdit">
          <template #icon><Edit /></template>
          {{ $t('common.edit') }}
        </el-button>

        <el-dropdown v-if="canOperate" @command="handleOperation">
          <el-button type="primary">
            <template #icon><MoreFilled /></template>
            {{ $t('common.operations') }}
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <!-- Approvals removed in simplified mode -->
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
                      <el-button size="small" type="primary" @click="startEdit">
                        <template #icon><Edit /></template>
                        {{ $t('common.edit') }}
                      </el-button>
                    </template>
                    <template v-else-if="editing">
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
                    <el-select
                      v-model="editForm.evaluation_reason"
                      multiple
                      collapse-tags
                      style="width: 100%"
                    >
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
                  <el-button v-if="canEdit" size="small" @click="handleUploadFile">
                    <template #icon><Plus /></template>
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
                  <el-button
                    size="small"
                    aria-label="Download file"
                    title="Download file"
                    @click="handleDownloadFile(file)"
                  >
                    <template #icon><Download /></template>
                  </el-button>
                </div>
                <div v-if="!evaluation.files || evaluation.files.length === 0" class="empty-files">
                  {{ $t('evaluation.noRelatedFiles') }}
                </div>
              </div>
              <el-card v-if="legacyProcessNotes.length" class="legacy-card" shadow="never">
                <template #header>
                  <span>Legacy (view-only)</span>
                </template>
                <div
                  v-for="(note, index) in legacyProcessNotes"
                  :key="`legacy-note-${index}`"
                  class="legacy-note"
                >
                  <h4 class="legacy-title">{{ note.title }}</h4>
                  <pre class="legacy-content">{{ note.content }}</pre>
                </div>
              </el-card>
            </el-card>
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.technicalSpecifications')" name="specs">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span>{{ $t('evaluation.technicalSpecifications') }}</span>
                  <div class="header-actions">
                    <template v-if="!editing && canEdit">
                      <el-button size="small" type="primary" @click="startEdit">
                        <template #icon><Edit /></template>
                        {{ $t('common.edit') }}
                      </el-button>
                    </template>
                    <template v-else-if="editing">
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
              <el-descriptions :column="2" border class="technical-specs">
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
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.processSection')" name="process-meta">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span>{{ $t('evaluation.processSection') }}</span>
                  <div class="header-actions">
                    <template v-if="!editing && canEdit">
                      <el-button size="small" type="primary" @click="startEdit">
                        <template #icon><Edit /></template>
                        {{ $t('common.edit') }}
                      </el-button>
                    </template>
                    <template v-else-if="editing">
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

              <el-row :gutter="20" class="process-fields">
                <el-col :span="12">
                  <div class="process-field">
                    <label class="process-label">{{ $t('evaluation.testProcess') }}</label>
                    <template v-if="editing">
                      <el-input
                        v-model="editForm.test_process"
                        type="textarea"
                        :rows="3"
                        :placeholder="$t('evaluation.placeholders.testProcess')"
                      />
                    </template>
                    <template v-else>
                      <div class="process-text">
                        {{ evaluation.test_process || '-' }}
                      </div>
                    </template>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="process-field">
                    <label class="process-label">{{ $t('evaluation.vProcess') }}</label>
                    <template v-if="editing">
                      <el-input
                        v-model="editForm.v_process"
                        type="textarea"
                        :rows="3"
                        :placeholder="$t('evaluation.placeholders.vProcess')"
                      />
                    </template>
                    <template v-else>
                      <div class="process-text">
                        {{ evaluation.v_process || '-' }}
                      </div>
                    </template>
                  </div>
                </el-col>
              </el-row>

              <div class="process-field">
                <label class="process-label">{{ $t('evaluation.pgmLogin') }}</label>
                <template v-if="editing">
                  <div class="pgm-login-block" @paste="handlePgmPaste($event, editForm)">
                    <el-input
                      v-model="editForm.pgm_login_text"
                      type="textarea"
                      :rows="3"
                      :placeholder="$t('evaluation.placeholders.pgmLoginText')"
                    />
                    <div class="pgm-upload-row">
                      <el-upload
                        :show-file-list="false"
                        :auto-upload="false"
                        accept="image/*"
                        :before-upload="(file) => handlePgmImageUpload(file, editForm)"
                      >
                        <el-button>{{ $t('evaluation.upload') }}</el-button>
                      </el-upload>
                      <span class="pgm-paste-hint">{{ $t('evaluation.pgmLoginPasteHint') }}</span>
                      <el-button
                        v-if="editForm.pgm_login_image"
                        text
                        type="danger"
                        @click="clearPgmImage(editForm)"
                      >
                        {{ $t('common.delete') }}
                      </el-button>
                    </div>
                    <div v-if="editForm.pgm_login_image" class="pgm-image-preview">
                      <el-image :src="editForm.pgm_login_image" fit="contain" />
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="process-text">
                    {{ evaluation.pgm_login_text || '-' }}
                  </div>
                  <div v-if="evaluation.pgm_login_image" class="pgm-image-preview">
                    <el-image :src="evaluation.pgm_login_image" fit="contain" />
                  </div>
                </template>
              </div>
            </el-card>
          </el-tab-pane>

          <el-tab-pane :label="$t('evaluation.evaluationProcesses')" name="processes">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span>{{ $t('evaluation.evaluationProcesses') }}</span>
                  <el-button v-if="canEdit" size="small" type="primary" @click="openProcessDrawer">
                    <template #icon><Connection /></template>
                    {{ $t('evaluation.manageNestedProcesses') }}
                  </el-button>
                </div>
              </template>

              <el-empty v-if="!builderHasStepsSummary" :description="$t('nested.summary.empty')" />

              <div v-else class="nested-summary">
                <div
                  v-for="process in builderSummaryProcesses"
                  :key="process.key"
                  class="nested-process-summary"
                >
                  <div class="nested-process-header">
                    <strong>{{ process.name }}</strong>
                    <span class="nested-process-chain">
                      {{
                        process.steps
                          .map((step) => stepLabelForPath(step, $t('nested.newStep')))
                          .join(' → ')
                      }}
                    </span>
                  </div>
                  <ul v-if="process.lots.length" class="nested-process-lots">
                    <li v-for="lot in process.lots" :key="lot.client_id">{{ lot.label }}</li>
                  </ul>
                  <div
                    v-for="step in process.steps"
                    :key="`${process.key}-${step.order_index}`"
                    class="nested-summary-item"
                  >
                    <div class="nested-step-title">
                      <strong>{{ step.order_index }}. {{ step.step_code }}</strong>
                      <span v-if="step.step_label"> - {{ step.step_label }}</span>
                    </div>
                    <div class="nested-step-meta">
                      <template v-if="step.results_applicable === false">
                        {{ $t('nested.summary.noResults') }}
                      </template>
                      <template v-else-if="isReliabilityStepCode(step.step_code)">
                        {{ reliabilitySummaryFor(step) || totalsSummaryFor(step) }}
                      </template>
                      <template v-else>
                        {{ totalsSummaryFor(step) }}
                      </template>
                    </div>
                    <div class="nested-step-lots">
                      {{ $t('nested.summary.appliesTo') }}
                      {{ describeStepLots(process, step.lot_refs) }}
                    </div>
                    <div
                      v-if="Array.isArray(step.failures) && step.failures.length"
                      class="nested-failure-count"
                    >
                      {{ $t('nested.summary.failuresCount', { count: step.failures.length }) }}
                    </div>
                  </div>
                </div>
              </div>

              <el-alert
                v-if="nestedSaveWarnings.length"
                type="warning"
                show-icon
                class="nested-warning"
                @close="clearNestedWarnings"
              >
                <ul class="alert-list">
                  <li
                    v-for="(warning, index) in nestedSaveWarnings"
                    :key="`nested-warning-${index}`"
                  >
                    {{ warning }}
                  </li>
                </ul>
              </el-alert>
              <el-alert
                v-if="nestedSaveError"
                type="error"
                show-icon
                class="nested-warning"
                @close="clearNestedError"
              >
                {{ nestedSaveError }}
              </el-alert>
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
                    :color="getOperationColor(log.operation_type)"
                  >
                    <template #dot>
                      <el-icon
                        ><component :is="getOperationIconName(log.operation_type)"
                      /></el-icon>
                    </template>
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
                    <el-button size="small" type="primary" @click="startEdit">
                      <template #icon><Edit /></template>
                      {{ $t('common.edit') }}
                    </el-button>
                  </template>
                  <template v-else-if="editing">
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
                  <el-select
                    v-model="editForm.evaluation_reason"
                    multiple
                    collapse-tags
                    style="width: 100%"
                  >
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

          <el-card class="info-card">
            <template #header>
              <span>{{ $t('evaluation.processSection') }}</span>
            </template>
            <el-row :gutter="20" class="process-fields">
              <el-col :span="12">
                <div class="process-field">
                  <label class="process-label">{{ $t('evaluation.testProcess') }}</label>
                  <template v-if="editing">
                    <el-input
                      v-model="editForm.test_process"
                      type="textarea"
                      :rows="3"
                      :placeholder="$t('evaluation.placeholders.testProcess')"
                    />
                  </template>
                  <template v-else>
                    <div class="process-text">
                      {{ evaluation.test_process || '-' }}
                    </div>
                  </template>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="process-field">
                  <label class="process-label">{{ $t('evaluation.vProcess') }}</label>
                  <template v-if="editing">
                    <el-input
                      v-model="editForm.v_process"
                      type="textarea"
                      :rows="3"
                      :placeholder="$t('evaluation.placeholders.vProcess')"
                    />
                  </template>
                  <template v-else>
                    <div class="process-text">
                      {{ evaluation.v_process || '-' }}
                    </div>
                  </template>
                </div>
              </el-col>
            </el-row>

            <div class="process-field">
              <label class="process-label">{{ $t('evaluation.pgmLogin') }}</label>
              <template v-if="editing">
                <div class="pgm-login-block" @paste="handlePgmPaste($event, editForm)">
                  <el-input
                    v-model="editForm.pgm_login_text"
                    type="textarea"
                    :rows="3"
                    :placeholder="$t('evaluation.placeholders.pgmLoginText')"
                  />
                  <div class="pgm-upload-row">
                    <el-upload
                      :show-file-list="false"
                      :auto-upload="false"
                      accept="image/*"
                      :before-upload="(file) => handlePgmImageUpload(file, editForm)"
                    >
                      <el-button>{{ $t('evaluation.upload') }}</el-button>
                    </el-upload>
                    <span class="pgm-paste-hint">{{ $t('evaluation.pgmLoginPasteHint') }}</span>
                    <el-button
                      v-if="editForm.pgm_login_image"
                      text
                      type="danger"
                      @click="clearPgmImage(editForm)"
                    >
                      {{ $t('common.delete') }}
                    </el-button>
                  </div>
                  <div v-if="editForm.pgm_login_image" class="pgm-image-preview">
                    <el-image :src="editForm.pgm_login_image" fit="contain" />
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="process-text">
                  {{ evaluation.pgm_login_text || '-' }}
                </div>
                <div v-if="evaluation.pgm_login_image" class="pgm-image-preview">
                  <el-image :src="evaluation.pgm_login_image" fit="contain" />
                </div>
              </template>
            </div>
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

          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t('evaluation.evaluationProcesses') }}</span>
                <el-button v-if="canEdit" type="primary" plain @click="openProcessDrawer">
                  <template #icon><Connection /></template>
                  {{ $t('evaluation.manageNestedProcesses') }}
                </el-button>
              </div>
            </template>

            <el-empty v-if="!builderHasStepsSummary" :description="$t('nested.summary.empty')" />

            <div v-else class="nested-summary">
              <div
                v-for="process in builderSummaryProcesses"
                :key="process.key"
                class="nested-process-summary"
              >
                <div class="nested-process-header">
                  <strong>{{ process.name }}</strong>
                  <span class="nested-process-chain">
                    {{
                      process.steps
                        .map((step) => stepLabelForPath(step, $t('nested.newStep')))
                        .join(' → ')
                    }}
                  </span>
                </div>
                <ul v-if="process.lots.length" class="nested-process-lots">
                  <li v-for="lot in process.lots" :key="lot.client_id">{{ lot.label }}</li>
                </ul>
                <div
                  v-for="step in process.steps"
                  :key="`${process.key}-${step.order_index}`"
                  class="nested-summary-item"
                >
                  <div class="nested-step-title">
                    <strong>{{ step.order_index }}. {{ step.step_code }}</strong>
                    <span v-if="step.step_label"> - {{ step.step_label }}</span>
                  </div>
                  <div class="nested-step-meta">
                    <template v-if="step.results_applicable === false">
                      {{ $t('nested.summary.noResults') }}
                    </template>
                    <template v-else-if="isReliabilityStepCode(step.step_code)">
                      {{ reliabilitySummaryFor(step) || totalsSummaryFor(step) }}
                    </template>
                    <template v-else>
                      {{ totalsSummaryFor(step) }}
                    </template>
                  </div>
                  <div class="nested-step-lots">
                    {{ $t('nested.summary.appliesTo') }}
                    {{ describeStepLots(process, step.lot_refs) }}
                  </div>
                  <div
                    v-if="Array.isArray(step.failures) && step.failures.length"
                    class="nested-failure-count"
                  >
                    {{ $t('nested.summary.failuresCount', { count: step.failures.length }) }}
                  </div>
                </div>
              </div>
            </div>

            <el-alert
              v-if="nestedSaveWarnings.length"
              type="warning"
              show-icon
              class="nested-warning"
              @close="clearNestedWarnings"
            >
              <ul class="alert-list">
                <li v-for="(warning, index) in nestedSaveWarnings" :key="`nested-warning-${index}`">
                  {{ warning }}
                </li>
              </ul>
            </el-alert>
            <el-alert
              v-if="nestedSaveError"
              type="error"
              show-icon
              class="nested-warning"
              @close="clearNestedError"
            >
              {{ nestedSaveError }}
            </el-alert>
            <el-card v-if="legacyProcessNotes.length" class="legacy-card" shadow="never">
              <template #header>
                <span>Legacy (view-only)</span>
              </template>
              <div
                v-for="(note, index) in legacyProcessNotes"
                :key="`legacy-note-${index}`"
                class="legacy-note"
              >
                <h4 class="legacy-title">{{ note.title }}</h4>
                <pre class="legacy-content">{{ note.content }}</pre>
              </div>
            </el-card>
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
                <el-button v-if="canEdit" size="small" @click="handleUploadFile">
                  <template #icon><Plus /></template>
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
                <el-button
                  size="small"
                  aria-label="Download file"
                  title="Download file"
                  @click="handleDownloadFile(file)"
                >
                  <template #icon><Download /></template>
                </el-button>
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
                  :color="getOperationColor(log.operation_type)"
                >
                  <template #dot>
                    <el-icon><component :is="getOperationIconName(log.operation_type)" /></el-icon>
                  </template>
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
      <el-drawer
        v-model="processDrawerVisible"
        size="60%"
        :before-close="handleProcessDrawerBeforeClose"
        :title="$t('evaluation.manageNestedProcesses')"
      >
        <ProcessBuilder
          ref="processBuilderRef"
          :initial-payload="builderPayload"
          :server-warnings="processBuilderWarnings"
          :show-save-button="false"
          @dirty-change="handleBuilderDirtyChange"
        />
        <template #footer>
          <div class="drawer-footer">
            <el-button @click="handleDrawerCancel">{{ $t('common.close') }}</el-button>
            <el-button
              v-if="canCancel"
              type="danger"
              data-test-id="cancel-evaluation"
              @click="promptCancelEvaluation"
            >
              {{ $t('evaluation.cancel') }}
            </el-button>
            <el-button type="primary" @click="commitBuilderChanges">{{
              $t('common.save')
            }}</el-button>
          </div>
        </template>
      </el-drawer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, defineExpose } from 'vue'
import { useRoute } from 'vue-router'
const props = defineProps({
  inDialog: { type: Boolean, default: false },
  evaluationId: { type: [String, Number], default: null },
  processStepOptions: {
    type: Array,
    default: () => ['iARTs', 'Aging', 'LI', 'Repair'],
  },
})
// No emits used currently (inline editing in same view)
import { useI18n } from 'vue-i18n'
import api from '../utils/api'
import ProcessBuilder from '../components/ProcessBuilder.vue'
import {
  buildReliabilitySummary,
  buildTotalsSummary,
  stepLabelForPath,
  isReliabilityStep,
} from '../utils/reliability'
import {
  builderPayloadToNestedRequest,
  createEmptyBuilderPayload,
  evaluationToBuilderPayload,
  extractLegacyProcessNotes,
  hasBuilderSteps,
  normalizeBuilderPayload,
} from '../utils/processMapper'
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

const fileToDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })

const normalizeReasons = (reason) => {
  if (Array.isArray(reason)) return reason.filter(Boolean)
  if (!reason) return []
  return String(reason)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

const serializeReasons = (reasons) => normalizeReasons(reasons).join(',')

const handlePgmPaste = async (event, target = editForm) => {
  const items = event.clipboardData?.items
  if (!items || !items.length) return
  for (const item of items) {
    if (item.type && item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (!file) continue
      try {
        target.pgm_login_image = await fileToDataUrl(file)
        ElMessage.success(t('evaluation.operationSuccess'))
      } catch (error) {
        console.error('Paste image failed', error)
        ElMessage.error(t('evaluation.operationFailed'))
      }
      event.preventDefault()
      break
    }
  }
}

const handlePgmImageUpload = async (file, target = editForm) => {
  try {
    target.pgm_login_image = await fileToDataUrl(file)
    ElMessage.success(t('evaluation.operationSuccess'))
  } catch (error) {
    console.error('Upload image failed', error)
    ElMessage.error(t('evaluation.operationFailed'))
  }
  return false
}

const clearPgmImage = (target = editForm) => {
  target.pgm_login_image = ''
}

const formatProcessSteps = (value) => {
  const steps = parseProcessSteps(value)
  return steps.length > 0 ? steps.join(' / ') : '-'
}
const evaluation = ref(null)
const builderPayload = ref(normalizeBuilderPayload(createEmptyBuilderPayload()))
const processDrawerVisible = ref(false)
const processBuilderRef = ref(null)
const processBuilderWarnings = ref([])
const processBuilderDirty = ref(false)
const nestedSaveWarnings = ref([])
const nestedSaveError = ref(null)
const builderSummaryProcesses = computed(() => {
  const processes = Array.isArray(builderPayload.value.processes)
    ? builderPayload.value.processes
    : []

  return processes.map((process, processIndex) => {
    const lots = Array.isArray(process.lots) ? process.lots : []
    const lotLabels = lots.map((lot, lotIndex) => {
      const quantity = Number(lot.quantity) || 0
      const lotNumber = lot.lot_number || t('nested.summary.lotFallback', { index: lotIndex + 1 })
      const label = quantity ? `${lotNumber} (${quantity})` : lotNumber
      return {
        client_id: lot.client_id || lot.temp_id || `${process.key || 'proc'}-lot-${lotIndex}`,
        label,
      }
    })
    const lotLabelMap = new Map(lotLabels.map((lot) => [String(lot.client_id), lot.label]))

    return {
      key: process.key || `proc_${processIndex + 1}`,
      name: process.name || t('nested.defaultProcessName', { index: processIndex + 1 }),
      order_index: process.order_index || processIndex + 1,
      lots: lotLabels,
      lotLabelMap,
      steps: Array.isArray(process.steps) ? process.steps : [],
    }
  })
})

const builderHasStepsSummary = computed(() => hasBuilderSteps(builderPayload.value))

const describeStepLots = (process, lotRefs) => {
  if (!Array.isArray(lotRefs) || !lotRefs.length) {
    return t('nested.summary.allLots')
  }
  const labels = lotRefs
    .map((ref) => process.lotLabelMap.get(String(ref)) || process.lotLabelMap.get(ref))
    .filter(Boolean)
  if (!labels.length) {
    return t('nested.summary.allLots')
  }
  return labels.join(', ')
}

const reliabilitySummaryFor = (step) => buildReliabilitySummary(step, t)
const totalsSummaryFor = (step) => buildTotalsSummary(step, t)
const isReliabilityStepCode = (code) => isReliabilityStep(code)

async function refreshNestedPayload(targetId, evaluationContext = null, options = {}) {
  const { preserveWarnings = false } = options
  if (!targetId) {
    const fallback = evaluationContext
      ? evaluationToBuilderPayload(evaluationContext)
      : createEmptyBuilderPayload()
    builderPayload.value = normalizeBuilderPayload(fallback)
    if (!preserveWarnings) {
      nestedSaveWarnings.value = []
    }
    processBuilderWarnings.value = []
    return
  }

  try {
    const response = await api.get(`/evaluations/${targetId}/processes/nested`)
    const payload = response.data?.data?.payload
    const warnings = response.data?.data?.warnings || []

    if (payload) {
      builderPayload.value = normalizeBuilderPayload(payload)
    } else if (evaluationContext) {
      builderPayload.value = normalizeBuilderPayload(evaluationToBuilderPayload(evaluationContext))
    }

    if (!preserveWarnings) {
      nestedSaveWarnings.value = warnings
    }
    processBuilderWarnings.value = warnings
  } catch (error) {
    console.error('Failed to load nested process payload', error)
    if (evaluationContext) {
      builderPayload.value = normalizeBuilderPayload(evaluationToBuilderPayload(evaluationContext))
    }
    if (!preserveWarnings) {
      nestedSaveWarnings.value = []
    }
    processBuilderWarnings.value = []
  }
}

const legacyProcessNotes = computed(() => extractLegacyProcessNotes(evaluation.value) || [])
const editing = ref(false)
const saving = ref(false)

function handleBuilderDirtyChange(value) {
  processBuilderDirty.value = value
}

async function openProcessDrawer() {
  processBuilderWarnings.value = Array.isArray(nestedSaveWarnings.value)
    ? [...nestedSaveWarnings.value]
    : []
  processDrawerVisible.value = true
  await nextTick()
  processBuilderRef.value?.setPayload(builderPayload.value, { markClean: true })
  processBuilderDirty.value = false
}

async function handleProcessDrawerBeforeClose(done) {
  if (processBuilderDirty.value) {
    try {
      await ElMessageBox.confirm(t('nested.discardChanges'), t('common.confirmAction'), {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      })
      processBuilderRef.value?.markPristine()
      processBuilderDirty.value = false
    } catch {
      if (typeof done === 'function') {
        return
      }
      return
    }
  }
  processDrawerVisible.value = false
  if (typeof done === 'function') {
    done()
  }
}

function handleDrawerCancel() {
  handleProcessDrawerBeforeClose(() => {
    processDrawerVisible.value = false
  })
}

function clearNestedWarnings() {
  nestedSaveWarnings.value = []
  processBuilderWarnings.value = []
}

function clearNestedError() {
  nestedSaveError.value = null
}

async function commitBuilderChanges() {
  if (!processBuilderRef.value || !evaluation.value) return
  builderPayload.value = normalizeBuilderPayload(processBuilderRef.value.getPayload())
  processBuilderWarnings.value = []
  processBuilderRef.value.markPristine()
  processBuilderDirty.value = false
  processDrawerVisible.value = false
  nestedSaveWarnings.value = []
  nestedSaveError.value = null
  await saveNestedProcesses(evaluation.value.id)
}

const editForm = reactive({
  product_name: '',
  part_number: '',
  evaluation_reason: [],
  process_step: [],
  scs_charger_name: '',
  head_office_charger_name: '',
  status: '',
  start_date: '',
  end_date: '',
  remarks: '',
  test_process: '',
  v_process: '',
  pgm_login_text: '',
  pgm_login_image: '',
  pgm_version: '',
  pgm_test_time: '',
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
    evaluation_reason: normalizeReasons(evaluation.value.evaluation_reason),
    process_step: parseProcessSteps(evaluation.value.process_step),
    scs_charger_name: evaluation.value.scs_charger_name || '',
    head_office_charger_name: evaluation.value.head_office_charger_name || '',
    status: evaluation.value.status || 'draft',
    start_date: evaluation.value.start_date || '',
    end_date: evaluation.value.actual_end_date || '',
    remarks: evaluation.value.remarks || evaluation.value.description || '',
    test_process: evaluation.value.test_process || '',
    v_process: evaluation.value.v_process || '',
    pgm_login_text: evaluation.value.pgm_login_text || '',
    pgm_login_image: evaluation.value.pgm_login_image || '',
    pgm_version: evaluation.value.pgm_version || '',
    pgm_test_time: evaluation.value.pgm_test_time || '',
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
      evaluation_reason: serializeReasons(editForm.evaluation_reason),
      process_step: serializeProcessSteps(editForm.process_step),
      scs_charger_name: editForm.scs_charger_name,
      head_office_charger_name: editForm.head_office_charger_name,
      start_date: editForm.start_date || null,
      end_date: editForm.end_date || null,
      remarks: editForm.remarks,
      test_process: editForm.test_process,
      v_process: editForm.v_process,
      pgm_login_text: editForm.pgm_login_text,
      pgm_login_image: editForm.pgm_login_image,
      pgm_version: editForm.pgm_version,
      pgm_test_time: editForm.pgm_test_time,
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
  return !['completed', 'cancelled', 'rejected'].includes(evaluation.value.status)
})

const promptCancelEvaluation = async () => {
  if (!evaluation.value) return
  if (!canCancel.value) {
    ElMessage.warning(t('evaluation.cancelNotAllowed'))
    return
  }

  try {
    const { value } = await ElMessageBox.prompt(
      t('evaluation.cancelReasonPrompt'),
      t('evaluation.cancel'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.close'),
        inputPlaceholder: t('evaluation.cancelReasonPlaceholder'),
        inputType: 'textarea',
      },
    )

    await api.put(`/evaluations/${evaluation.value.id}/status`, {
      status: 'cancelled',
      cancel_reason: value || '',
    })

    ElMessage.success(t('evaluation.operationSuccess'))
    fetchEvaluation()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('evaluation.operationFailed'))
      console.error('Cancel operation failed:', error)
    }
  }
}
defineExpose({
  promptCancelEvaluation,
  canCancel,
})

// timeline steps removed; process list is source of truth

const filteredLogs = computed(() => {
  const logs = evaluation.value?.logs || []
  return logs
})

async function fetchEvaluation(options = {}) {
  const { preserveWarnings = false } = options
  try {
    loading.value = true
    const id = props.evaluationId || route.params.id
    const response = await api.get(`/evaluations/${id}`)
    evaluation.value = response.data.data.evaluation
    if (evaluation.value) {
      builderPayload.value = normalizeBuilderPayload(evaluationToBuilderPayload(evaluation.value))
      if (!preserveWarnings) {
        nestedSaveWarnings.value = []
      }
      processBuilderWarnings.value = []
      await refreshNestedPayload(evaluation.value.id, evaluation.value, { preserveWarnings })
    }
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

const goToNestedEditor = () => {
  if (!evaluation.value) return
  openProcessDrawer()
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
        await promptCancelEvaluation()
        return
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
  const reasons = normalizeReasons(reason)
  if (reasons.length === 0) return '-'
  const labels = reasons.map((r) => {
    const key = `evaluation.reasons.${r}`
    const translated = t(key)
    return translated === key ? r : translated
  })
  return labels.join(', ')
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

const getOperationIconName = (operationType) => {
  const iconMap = {
    create: 'CirclePlus',
    update: 'EditPen',
    delete: 'Delete',
    approve: 'CircleCheck',
    reject: 'CircleClose',
    view: 'View',
    login: 'User',
    logout: 'User',
    export: 'Download',
  }
  return iconMap[operationType] || 'EditPen'
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

async function saveNestedProcesses(targetId) {
  if (!targetId) return
  if (!hasBuilderSteps(builderPayload.value)) {
    nestedSaveWarnings.value = []
    nestedSaveError.value = null
    return
  }
  try {
    const payload = builderPayloadToNestedRequest(builderPayload.value)
    const response = await api.post(`/evaluations/${targetId}/processes/nested`, payload)
    nestedSaveWarnings.value = response.data?.data?.warnings || []
    nestedSaveError.value = null
    await fetchEvaluation({ preserveWarnings: true })
    if (nestedSaveWarnings.value.length) {
      ElMessage.warning('Nested processes saved with warnings. Review details below.')
    } else {
      ElMessage.success('Nested processes saved')
    }
  } catch (error) {
    nestedSaveError.value = 'Failed to save nested processes. Please retry.'
    console.error('Failed to save nested processes', error)
  }
}

onMounted(async () => {
  await fetchEvaluation()
})

// Dialog tabs
const activeTab = ref('details')
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
  white-space: pre-wrap;
  word-break: break-word;
}

.process-fields {
  margin-top: 8px;
}

.process-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.process-label {
  font-weight: 600;
  color: #2c3e50;
}

.process-text {
  min-height: 56px;
  padding: 10px 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
  white-space: pre-wrap;
  word-break: break-word;
}

.pgm-login-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pgm-upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.pgm-paste-hint {
  color: #909399;
  font-size: 13px;
}

.pgm-image-preview {
  margin-top: 8px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  padding: 8px;
  background: #fafafa;
  max-width: 360px;
}

.pgm-image-preview :deep(img) {
  max-height: 220px;
  width: auto;
  display: block;
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

/* Nested process summary */
.nested-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nested-process-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  background: #fdfdff;
}

.nested-process-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.nested-process-chain {
  font-size: 13px;
  color: #909399;
}

.nested-process-lots {
  margin: 0;
  padding-left: 18px;
  color: #606266;
  font-size: 13px;
}

.nested-lots-summary {
  margin-bottom: 12px;
}

.nested-lots-summary h4 {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.nested-lots-summary ul {
  margin: 0;
  padding-left: 16px;
  color: #606266;
  font-size: 13px;
}

.nested-summary-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  background: #f9fafc;
}

.nested-step-title {
  font-weight: 600;
  color: #303133;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.nested-step-meta {
  margin-top: 4px;
  color: #606266;
  font-size: 13px;
}

.nested-step-lots {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
}

.nested-failure-count {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
}

.nested-warning {
  margin-top: 12px;
}

.legacy-card {
  margin-top: 16px;
}

.legacy-note {
  margin-bottom: 12px;
}

.legacy-title {
  margin: 0 0 6px;
  font-size: 14px;
  color: #303133;
}

.legacy-content {
  margin: 0;
  background: #f4f4f5;
  border-radius: 4px;
  padding: 12px;
  white-space: pre-wrap;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.inline-label {
  display: inline-block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
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
