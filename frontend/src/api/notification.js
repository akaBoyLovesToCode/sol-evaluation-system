import api from '../utils/api'

export const notificationAPI = {
  // Get user notifications
  getUserNotifications: async (params = {}) => {
    const response = await api.get('/notifications', { params })
    return response.data
  },

  // Get unread notification count
  getUnreadCount: async () => {
    const response = await api.get('/notifications/unread-count')
    return response.data
  },

  // Mark notification as read
  markAsRead: async (messageId) => {
    const response = await api.put(`/notifications/${messageId}/read`)
    return response.data
  },

  // Mark all notifications as read
  markAllAsRead: async () => {
    const response = await api.put('/notifications/mark-all-read')
    return response.data
  },

  // Delete notification
  deleteNotification: async (messageId) => {
    const response = await api.delete(`/notifications/${messageId}`)
    return response.data
  },

  // Send notification to user
  sendNotification: async (data) => {
    const response = await api.post('/notifications/send', data)
    return response.data
  },

  // Send bulk notification
  sendBulkNotification: async (data) => {
    const response = await api.post('/notifications/send-bulk', data)
    return response.data
  },

  // Get notification statistics (admin only)
  getNotificationStatistics: async () => {
    const response = await api.get('/notifications/statistics')
    return response.data
  },

  // Clean up old notifications (admin only)
  cleanupOldNotifications: async (data = {}) => {
    const response = await api.post('/notifications/cleanup', data)
    return response.data
  },

  // Send reminder notifications (admin/group leader only)
  sendReminderNotifications: async () => {
    const response = await api.post('/notifications/send-reminders')
    return response.data
  },

  // Send daily digest to user (admin only)
  sendDailyDigest: async (userId) => {
    const response = await api.post(`/notifications/digest/${userId}`)
    return response.data
  },

  // Get notification preferences
  getNotificationPreferences: async () => {
    const response = await api.get('/notifications/preferences')
    return response.data
  },

  // Update notification preferences
  updateNotificationPreferences: async (data) => {
    const response = await api.put('/notifications/preferences', data)
    return response.data
  },

  // Get notification templates (admin only)
  getNotificationTemplates: async () => {
    const response = await api.get('/notifications/templates')
    return response.data
  },

  // Create notification template (admin only)
  createNotificationTemplate: async (data) => {
    const response = await api.post('/notifications/templates', data)
    return response.data
  },

  // Update notification template (admin only)
  updateNotificationTemplate: async (templateId, data) => {
    const response = await api.put(`/notifications/templates/${templateId}`, data)
    return response.data
  },

  // Delete notification template (admin only)
  deleteNotificationTemplate: async (templateId) => {
    const response = await api.delete(`/notifications/templates/${templateId}`)
    return response.data
  },

  // Send mention notification
  sendMention: async (data) => {
    const response = await api.post('/notifications/mention', data)
    return response.data
  },

  // Get mention notifications
  getMentionNotifications: async (params = {}) => {
    const response = await api.get('/notifications/mentions', { params })
    return response.data
  },

  // Send approval request notification
  sendApprovalRequest: async (data) => {
    const response = await api.post('/notifications/approval-request', data)
    return response.data
  },

  // Send status change notification
  sendStatusChange: async (data) => {
    const response = await api.post('/notifications/status-change', data)
    return response.data
  },

  // Send evaluation completion notification
  sendEvaluationCompletion: async (data) => {
    const response = await api.post('/notifications/evaluation-completion', data)
    return response.data
  },

  // Send system announcement
  sendSystemAnnouncement: async (data) => {
    const response = await api.post('/notifications/system-announcement', data)
    return response.data
  },

  // Get notification delivery status
  getNotificationDeliveryStatus: async (messageId) => {
    const response = await api.get(`/notifications/${messageId}/delivery-status`)
    return response.data
  },

  // Retry failed notification delivery
  retryNotificationDelivery: async (messageId) => {
    const response = await api.post(`/notifications/${messageId}/retry`)
    return response.data
  },

  // Search notifications
  searchNotifications: async (query, params = {}) => {
    const response = await api.get('/notifications/search', {
      params: { q: query, ...params },
    })
    return response.data
  },

  // Export notifications (admin only)
  exportNotifications: async (params = {}) => {
    const response = await api.get('/notifications/export', {
      params,
      responseType: 'blob',
    })
    return response.data
  },

  // Get notification channels
  getNotificationChannels: async () => {
    const response = await api.get('/notifications/channels')
    return response.data
  },

  // Update notification channels
  updateNotificationChannels: async (data) => {
    const response = await api.put('/notifications/channels', data)
    return response.data
  },

  // Test notification delivery
  testNotificationDelivery: async (data) => {
    const response = await api.post('/notifications/test', data)
    return response.data
  },
}
