import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api' // api might still be used for profile/password updates

export const useAuthStore = defineStore('auth', () => {
  // Assume a default user is always logged in
  const user = ref({
    id: 'default-user-id', // Placeholder ID
    username: 'defaultuser',
    email: 'user@example.com',
    full_name: 'Default User',
    role: 'user', // Default role
    // Add any other essential user properties that the app might expect
    department: 'Default Department',
    phone: '000-000-0000',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_login: new Date().toISOString()
  })
  const token = ref('fake-token') // Assume a token is always present

  const isAuthenticated = computed(() => true) // Always authenticated
  
  const hasRole = (roles) => {
    if (!user.value) return false
    if (typeof roles === 'string') roles = [roles]
    return roles.includes(user.value.role)
  }
  
  const canApprove = computed(() => {
    return hasRole(['admin', 'group_leader', 'part_leader'])
  })
  
  const isAdmin = computed(() => hasRole('admin'))
  const isGroupLeader = computed(() => hasRole(['admin', 'group_leader']))
  const isPartLeader = computed(() => hasRole(['admin', 'group_leader', 'part_leader']))

  // login, logout, and checkAuth are no longer needed as user is always authenticated.
  // We can keep updateProfile and changePassword if they are meant to work
  // with a backend that allows these modifications for an assumed user.
  // If they strictly require prior real authentication, they should be removed or refactored.

  const updateProfile = async (profileData) => {
    try {
      const response = await api.put('/auth/profile', profileData)
      user.value = { ...user.value, ...response.data }
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Update failed' 
      }
    }
  }
  
  const changePassword = async (passwordData) => {
    try {
      await api.put('/auth/password', passwordData)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Password change failed' 
      }
    }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    hasRole,
    canApprove,
    isAdmin,
    isGroupLeader,
    isPartLeader,
    // login, logout, checkAuth removed
    updateProfile,
    changePassword
  }
}) 