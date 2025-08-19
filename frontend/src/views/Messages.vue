<template>
  <div class="messages-page">
    <div class="page-header">
      <h1>{{ $t('messages.title') }}</h1>
      <p>{{ $t('messages.description') }}</p>
    </div>

    <el-row :gutter="20">
      <!-- Message List Section -->
      <el-col :span="16">
        <el-card class="message-list-card">
          <!-- Filters and Actions -->
          <div class="message-filters">
            <el-row :gutter="20" align="middle">
              <el-col :span="8">
                <el-select
                  v-model="filters.type"
                  placeholder="All Types"
                  clearable
                  @change="fetchMessages"
                >
                  <el-option label="All Types" value="" />
                  <el-option label="Mentions" value="mention" />
                  <el-option label="Approval Requests" value="approval_request" />
                  <el-option label="Status Changes" value="status_change" />
                  <el-option label="System Announcements" value="system_announcement" />
                  <el-option label="Task Assignments" value="evaluation_assigned" />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-select
                  v-model="filters.status"
                  placeholder="All Status"
                  clearable
                  @change="fetchMessages"
                >
                  <el-option label="All Messages" value="" />
                  <el-option label="Unread" value="unread" />
                  <el-option label="Read" value="read" />
                </el-select>
              </el-col>
              <el-col :span="8" style="text-align: right">
                <el-button-group>
                  <el-button @click="markAllAsRead" :disabled="unreadCount === 0">
                    <el-icon><DocumentChecked /></el-icon>
                    Mark All Read
                  </el-button>
                  <el-button @click="refreshMessages">
                    <el-icon><Refresh /></el-icon>
                    Refresh
                  </el-button>
                </el-button-group>
              </el-col>
            </el-row>
          </div>

          <!-- Message List -->
          <div v-loading="loading" class="message-list">
            <template v-if="messages.length > 0">
              <div
                v-for="message in messages"
                :key="message.id"
                class="message-item"
                :class="{
                  unread: !message.is_read,
                  mention: message.message_type === 'mention',
                  approval: message.message_type === 'approval_request',
                }"
                @click="viewMessage(message)"
              >
                <div class="message-icon">
                  <el-icon v-if="message.message_type === 'mention'" color="#409EFF">
                    <ChatDotRound />
                  </el-icon>
                  <el-icon v-else-if="message.message_type === 'approval_request'" color="#E6A23C">
                    <DocumentChecked />
                  </el-icon>
                  <el-icon v-else-if="message.message_type === 'status_change'" color="#67C23A">
                    <Refresh />
                  </el-icon>
                  <el-icon v-else color="#909399">
                    <Message />
                  </el-icon>
                </div>

                <div class="message-content">
                  <div class="message-header">
                    <span class="message-title">{{ message.title }}</span>
                    <span class="message-time">{{ formatTime(message.created_at) }}</span>
                  </div>
                  <div class="message-body">
                    {{ truncateText(message.content, 100) }}
                  </div>
                  <div class="message-meta">
                    <el-tag size="small" :type="getMessageTypeTag(message.message_type)">
                      {{ formatMessageType(message.message_type) }}
                    </el-tag>
                    <span v-if="message.sender_name" class="message-sender">
                      From: {{ message.sender_name }}
                    </span>
                    <span v-if="message.evaluation_number" class="message-evaluation">
                      <el-icon><Document /></el-icon>
                      {{ message.evaluation_number }}
                    </span>
                  </div>
                </div>

                <div class="message-actions">
                  <el-button
                    v-if="!message.is_read"
                    link
                    type="primary"
                    @click.stop="markAsRead(message)"
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                  <el-button v-else link @click.stop="markAsUnread(message)">
                    <el-icon><Hide /></el-icon>
                  </el-button>
                  <el-button link type="danger" @click.stop="deleteMessage(message)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>

            <el-empty v-else description="No messages found" />
          </div>

          <!-- Pagination -->
          <div v-if="totalMessages > pageSize" class="message-pagination">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="totalMessages"
              layout="total, prev, pager, next"
              @current-change="fetchMessages"
            />
          </div>
        </el-card>
      </el-col>

      <!-- Statistics and Quick Actions -->
      <el-col :span="8">
        <!-- Statistics Card -->
        <el-card class="statistics-card">
          <template #header>
            <span>Message Statistics</span>
          </template>
          <div class="stat-item">
            <span class="stat-label">Unread Messages</span>
            <span class="stat-value unread-badge">{{ unreadCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Messages</span>
            <span class="stat-value">{{ totalMessages }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Pending Approvals</span>
            <span class="stat-value">{{ pendingApprovals }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Recent Mentions</span>
            <span class="stat-value">{{ recentMentions }}</span>
          </div>
        </el-card>

        <!-- Recent Notifications -->
        <el-card class="recent-notifications-card" style="margin-top: 20px">
          <template #header>
            <span>Recent Notifications</span>
          </template>
          <div v-if="recentNotifications.length > 0" class="recent-list">
            <div
              v-for="notification in recentNotifications"
              :key="notification.id"
              class="recent-item"
              @click="viewMessage(notification)"
            >
              <el-icon :color="getNotificationColor(notification.message_type)">
                <component :is="getNotificationIcon(notification.message_type)" />
              </el-icon>
              <div class="recent-content">
                <div class="recent-title">{{ notification.title }}</div>
                <div class="recent-time">{{ formatRelativeTime(notification.created_at) }}</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="No recent notifications" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Message Detail Dialog -->
    <el-dialog
      v-model="messageDialog"
      :title="selectedMessage?.title"
      width="600px"
      @closed="selectedMessage = null"
    >
      <div v-if="selectedMessage" class="message-detail">
        <div class="detail-header">
          <el-tag :type="getMessageTypeTag(selectedMessage.message_type)">
            {{ formatMessageType(selectedMessage.message_type) }}
          </el-tag>
          <span class="detail-time">{{ formatDateTime(selectedMessage.created_at) }}</span>
        </div>

        <div class="detail-meta">
          <div v-if="selectedMessage.sender_name" class="meta-item">
            <strong>From:</strong> {{ selectedMessage.sender_name }}
          </div>
          <div v-if="selectedMessage.evaluation_number" class="meta-item">
            <strong>Related Evaluation:</strong>
            <router-link
              :to="`/evaluations/${selectedMessage.evaluation_id}`"
              class="evaluation-link"
            >
              {{ selectedMessage.evaluation_number }}
            </router-link>
          </div>
        </div>

        <div class="detail-content">
          {{ selectedMessage.content }}
        </div>

        <div v-if="selectedMessage.message_type === 'approval_request'" class="detail-actions">
          <el-button type="primary" @click="goToEvaluation(selectedMessage.evaluation_id)">
            View Evaluation
          </el-button>
        </div>
      </div>

      <template #footer>
        <el-button @click="messageDialog = false">Close</el-button>
        <el-button
          v-if="selectedMessage && !selectedMessage.is_read"
          type="primary"
          @click="markAsRead(selectedMessage)"
        >
          Mark as Read
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Message,
  ChatDotRound,
  DocumentChecked,
  Refresh,
  View,
  Hide,
  Delete,
  Document,
} from '@element-plus/icons-vue'
import api from '@/utils/api'
// Using native JavaScript date formatting instead of date-fns

const router = useRouter()
const { t } = useI18n()

// State
const loading = ref(false)
const messages = ref([])
const totalMessages = ref(0)
const unreadCount = ref(0)
const pendingApprovals = ref(0)
const recentMentions = ref(0)
const recentNotifications = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const messageDialog = ref(false)
const selectedMessage = ref(null)
const refreshInterval = ref(null)

// Filters
const filters = reactive({
  type: '',
  status: '',
})

// Fetch messages
const fetchMessages = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
    }

    if (filters.type) {
      params.message_type = filters.type
    }

    if (filters.status) {
      params.status = filters.status
    }

    const response = await api.get('/notifications', { params })
    messages.value = response.data.notifications || []
    totalMessages.value = response.data.total || 0
    unreadCount.value = response.data.unread_count || 0

    // Calculate statistics
    pendingApprovals.value = messages.value.filter(
      (m) => m.message_type === 'approval_request' && !m.is_read,
    ).length
    recentMentions.value = messages.value.filter(
      (m) => m.message_type === 'mention' && !m.is_read,
    ).length

    // Get recent notifications
    recentNotifications.value = messages.value.filter((m) => !m.is_read).slice(0, 5)
  } catch (error) {
    console.error('Failed to fetch messages:', error)
    ElMessage.error('Failed to load messages')
  } finally {
    loading.value = false
  }
}

// Mark message as read
const markAsRead = async (message) => {
  try {
    await api.put(`/notifications/${message.id}/read`)
    message.is_read = true
    message.read_at = new Date().toISOString()
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    ElMessage.success('Message marked as read')

    if (messageDialog.value && selectedMessage.value?.id === message.id) {
      selectedMessage.value.is_read = true
      selectedMessage.value.read_at = message.read_at
    }
  } catch (error) {
    console.error('Failed to mark message as read:', error)
    ElMessage.error('Failed to mark message as read')
  }
}

// Mark message as unread
const markAsUnread = async (message) => {
  try {
    // Note: This endpoint might need to be implemented in the backend
    await api.put(`/notifications/${message.id}/unread`)
    message.is_read = false
    message.read_at = null
    unreadCount.value += 1
    ElMessage.success('Message marked as unread')
  } catch (error) {
    console.error('Failed to mark message as unread:', error)
    ElMessage.error('Failed to mark message as unread')
  }
}

// Mark all as read
const markAllAsRead = async () => {
  try {
    await ElMessageBox.confirm('Mark all messages as read?', 'Confirm', {
      confirmButtonText: 'Yes',
      cancelButtonText: 'No',
      type: 'info',
    })

    await api.put('/notifications/mark-all-read')
    messages.value.forEach((m) => {
      if (!m.is_read) {
        m.is_read = true
        m.read_at = new Date().toISOString()
      }
    })
    unreadCount.value = 0
    ElMessage.success('All messages marked as read')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to mark all as read:', error)
      ElMessage.error('Failed to mark all messages as read')
    }
  }
}

// Delete message
const deleteMessage = async (message) => {
  try {
    await ElMessageBox.confirm('Delete this message?', 'Confirm Delete', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning',
    })

    await api.delete(`/notifications/${message.id}`)
    const index = messages.value.findIndex((m) => m.id === message.id)
    if (index > -1) {
      if (!messages.value[index].is_read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      messages.value.splice(index, 1)
      totalMessages.value = Math.max(0, totalMessages.value - 1)
    }
    ElMessage.success('Message deleted')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete message:', error)
      ElMessage.error('Failed to delete message')
    }
  }
}

// View message details
const viewMessage = (message) => {
  selectedMessage.value = message
  messageDialog.value = true

  if (!message.is_read) {
    markAsRead(message)
  }
}

// Go to evaluation
const goToEvaluation = (evaluationId) => {
  messageDialog.value = false
  router.push(`/evaluations/${evaluationId}`)
}

// Refresh messages
const refreshMessages = () => {
  fetchMessages()
}

// Format functions using native JavaScript
const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  return 'just now'
}

const formatMessageType = (type) => {
  const types = {
    mention: 'Mention',
    approval_request: 'Approval Request',
    status_change: 'Status Change',
    system_announcement: 'System',
    evaluation_assigned: 'Assignment',
    evaluation_completed: 'Completed',
  }
  return types[type] || type
}

const getMessageTypeTag = (type) => {
  const tags = {
    mention: 'primary',
    approval_request: 'warning',
    status_change: 'success',
    system_announcement: 'info',
    evaluation_assigned: 'primary',
    evaluation_completed: 'success',
  }
  return tags[type] || 'info'
}

const getNotificationIcon = (type) => {
  const icons = {
    mention: 'ChatDotRound',
    approval_request: 'DocumentChecked',
    status_change: 'Refresh',
    system_announcement: 'Message',
    evaluation_assigned: 'Document',
    evaluation_completed: 'DocumentChecked',
  }
  return icons[type] || 'Message'
}

const getNotificationColor = (type) => {
  const colors = {
    mention: '#409EFF',
    approval_request: '#E6A23C',
    status_change: '#67C23A',
    system_announcement: '#909399',
    evaluation_assigned: '#409EFF',
    evaluation_completed: '#67C23A',
  }
  return colors[type] || '#909399'
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

// Lifecycle
onMounted(() => {
  fetchMessages()

  // Set up auto-refresh every 30 seconds
  refreshInterval.value = setInterval(() => {
    fetchMessages()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.messages-page {
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

.message-list-card {
  min-height: 600px;
}

.message-filters {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.message-list {
  min-height: 400px;
  padding: 16px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  margin-bottom: 12px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.message-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.message-item.unread {
  background: #f0f9ff;
  border-color: #409eff;
}

.message-item.mention {
  border-left: 4px solid #409eff;
}

.message-item.approval {
  border-left: 4px solid #e6a23c;
}

.message-icon {
  margin-right: 16px;
  font-size: 24px;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.message-time {
  color: #909399;
  font-size: 12px;
}

.message-body {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.message-sender,
.message-evaluation {
  display: flex;
  align-items: center;
  gap: 4px;
}

.message-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.message-pagination {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  text-align: center;
}

.statistics-card,
.recent-notifications-card {
  background: #fff;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  font-weight: 600;
  font-size: 18px;
  color: #303133;
}

.unread-badge {
  color: #f56c6c;
}

.recent-list {
  max-height: 300px;
  overflow-y: auto;
}

.recent-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.recent-item:hover {
  background: #f5f7fa;
}

.recent-content {
  margin-left: 12px;
  flex: 1;
}

.recent-title {
  font-size: 13px;
  color: #303133;
  margin-bottom: 4px;
}

.recent-time {
  font-size: 11px;
  color: #909399;
}

.message-detail {
  padding: 20px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-time {
  color: #909399;
  font-size: 13px;
}

.detail-meta {
  margin-bottom: 20px;
}

.meta-item {
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.meta-item strong {
  margin-right: 8px;
}

.evaluation-link {
  color: #409eff;
  text-decoration: none;
}

.evaluation-link:hover {
  text-decoration: underline;
}

.detail-content {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
}

.detail-actions {
  margin-top: 20px;
  text-align: center;
}
</style>
