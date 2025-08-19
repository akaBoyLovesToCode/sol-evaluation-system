import api from '../utils/api'

export const userAPI = {
  // Get all users with filters
  getUsers: async (params = {}) => {
    const response = await api.get('/users', { params })
    return response.data
  },

  // Get single user by ID
  getUser: async (id) => {
    const response = await api.get(`/users/${id}`)
    return response.data
  },

  // Get current user profile
  getCurrentUser: async () => {
    const response = await api.get('/users/me')
    return response.data
  },

  // Update current user profile
  updateCurrentUser: async (data) => {
    const response = await api.put('/users/me', data)
    return response.data
  },

  // Create new user (admin only)
  createUser: async (data) => {
    const response = await api.post('/users', data)
    return response.data
  },

  // Update user (admin only)
  updateUser: async (id, data) => {
    const response = await api.put(`/users/${id}`, data)
    return response.data
  },

  // Delete user (admin only)
  deleteUser: async (id) => {
    const response = await api.delete(`/users/${id}`)
    return response.data
  },

  // Search users
  searchUsers: async (params = {}) => {
    const response = await api.get('/users/search', { params })
    return response.data
  },

  // Get users by role
  getUsersByRole: async (role) => {
    const response = await api.get('/users/by-role', {
      params: { role },
    })
    return response.data
  },

  // Get users by department
  getUsersByDepartment: async (department) => {
    const response = await api.get('/users/by-department', {
      params: { department },
    })
    return response.data
  },

  // Change user password
  changePassword: async (data) => {
    const response = await api.put('/users/me/password', data)
    return response.data
  },

  // Reset user password (admin only)
  resetPassword: async (userId, data) => {
    const response = await api.put(`/users/${userId}/reset-password`, data)
    return response.data
  },

  // Activate/deactivate user (admin only)
  toggleUserStatus: async (userId, isActive) => {
    const response = await api.put(`/users/${userId}/status`, {
      is_active: isActive,
    })
    return response.data
  },

  // Get user statistics (admin only)
  getUserStats: async () => {
    const response = await api.get('/users/stats')
    return response.data
  },

  // Get user activity log
  getUserActivity: async (userId, params = {}) => {
    const response = await api.get(`/users/${userId}/activity`, { params })
    return response.data
  },

  // Get current user activity
  getCurrentUserActivity: async (params = {}) => {
    const response = await api.get('/users/me/activity', { params })
    return response.data
  },

  // Get user permissions
  getUserPermissions: async (userId) => {
    const response = await api.get(`/users/${userId}/permissions`)
    return response.data
  },

  // Update user permissions (admin only)
  updateUserPermissions: async (userId, permissions) => {
    const response = await api.put(`/users/${userId}/permissions`, {
      permissions,
    })
    return response.data
  },

  // Get users for mention (returns users that can be mentioned)
  getUsersForMention: async (query = '') => {
    const response = await api.get('/users/mention', {
      params: { q: query },
    })
    return response.data
  },

  // Get head officers (users with admin, group_leader, or part_leader roles)
  getHeadOfficers: async (query = '') => {
    const response = await api.get('/users/head-officers', {
      params: { q: query },
    })
    return response.data
  },

  // Get SCS colleagues (users in SCS department)
  getSCSColleagues: async (query = '') => {
    const response = await api.get('/users/scs-colleagues', {
      params: { q: query },
    })
    return response.data
  },

  // Get user's evaluations
  getUserEvaluations: async (userId, params = {}) => {
    const response = await api.get(`/users/${userId}/evaluations`, { params })
    return response.data
  },

  // Get current user's evaluations
  getCurrentUserEvaluations: async (params = {}) => {
    const response = await api.get('/users/me/evaluations', { params })
    return response.data
  },

  // Get user's approvals
  getUserApprovals: async (userId, params = {}) => {
    const response = await api.get(`/users/${userId}/approvals`, { params })
    return response.data
  },

  // Get current user's approvals
  getCurrentUserApprovals: async (params = {}) => {
    const response = await api.get('/users/me/approvals', { params })
    return response.data
  },

  // Get user's messages/notifications
  getUserMessages: async (userId, params = {}) => {
    const response = await api.get(`/users/${userId}/messages`, { params })
    return response.data
  },

  // Get current user's messages/notifications
  getCurrentUserMessages: async (params = {}) => {
    const response = await api.get('/users/me/messages', { params })
    return response.data
  },

  // Update user profile picture
  updateProfilePicture: async (formData) => {
    const response = await api.put('/users/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Get departments list
  getDepartments: async () => {
    const response = await api.get('/users/departments')
    return response.data
  },

  // Get roles list
  getRoles: async () => {
    const response = await api.get('/users/roles')
    return response.data
  },

  // Bulk update users (admin only)
  bulkUpdateUsers: async (data) => {
    const response = await api.put('/users/bulk-update', data)
    return response.data
  },

  // Export users data (admin only)
  exportUsers: async (format = 'excel') => {
    const response = await api.get('/users/export', {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  },

  // Import users data (admin only)
  importUsers: async (formData) => {
    const response = await api.post('/users/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}
