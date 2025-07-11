import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  
  const isAuthenticated = computed(() => !!token.value)
  
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
  
  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials)
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      localStorage.setItem('token', access_token)
      user.value = userData
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Login failed' 
      }
    }
  }
  
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }
  
  const checkAuth = async () => {
    if (!token.value) {
      return false
    }
    
    try {
      const response = await api.get('/auth/me')
      // Handle different response structures
      if (response.data.data) {
        user.value = response.data.data
      } else if (response.data.user) {
        user.value = response.data.user
      } else {
        user.value = response.data
      }
      return true
    } catch (error) {
      logout()
      return false
    }
  }
  
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
    login,
    logout,
    checkAuth,
    updateProfile,
    changePassword
  }
}) 